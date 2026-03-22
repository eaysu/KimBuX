import re
import asyncio
from collections import Counter
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.config import TWEET_LIMITS
from src.twitter_client import TwitterClient
from src.analyzer import compute_stats
from src.gpt_analyzer import generate_profile_analysis
from src.database import (
    init_db, get_cached_analysis, save_analysis,
    get_negative_cache, save_negative_cache,
    get_analysis_lock, close_pool,
)

app = FastAPI(title="KimBuX API")

# Global semaphore: max 2 concurrent Twitter analyses to avoid rate limits
_analysis_semaphore = asyncio.Semaphore(2)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    username: str
    limit: int = 100
    order: str = "latest"  # "latest" (yeniden eskiye) or "oldest" (eskiden yeniye)


@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await close_pool()


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    username = req.username.lstrip("@").strip().lower()
    limit = req.limit
    order = req.order

    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty.")

    if limit not in TWEET_LIMITS:
        raise HTTPException(status_code=400, detail=f"Invalid limit. Choose from: {TWEET_LIMITS}")

    # Check negative cache
    neg = await get_negative_cache(username)
    if neg:
        raise HTTPException(status_code=404, detail=neg["error_message"])

    # Check positive cache (order is part of key via scope encoding)
    cache_scope = limit if order == "latest" else limit + 10000
    cached = await get_cached_analysis(username, cache_scope)
    if cached:
        return {
            "from_cache": True,
            "profile": cached["profile"],
            "stats": cached["stats"],
            "gpt_analysis": cached["gpt_analysis"],
            "analyzed_at": cached["analyzed_at"],
            "tweet_count": cached["tweet_count"],
        }

    # Acquire per-user lock
    lock = get_analysis_lock(username)
    if lock.locked():
        raise HTTPException(status_code=409, detail="Bu hesap zaten analiz ediliyor. Lütfen bekleyin.")

    # Semaphore: max 2 concurrent analyses globally
    if _analysis_semaphore._value == 0:
        raise HTTPException(status_code=429, detail="Sunucu yoğun. Lütfen bir dakika sonra tekrar deneyin.")

    async with _analysis_semaphore:
        async with lock:
            try:
                tc = TwitterClient()
                await tc.login()
                profile = await tc.get_profile(username)

                if profile.get("protected"):
                    await save_negative_cache(username, "protected_account", "This account is protected.")
                    raise HTTPException(status_code=403, detail="Protected account.")

                tweets = await tc.get_tweets(username, limit=limit)
                if not tweets:
                    raise HTTPException(status_code=404, detail="No eligible tweets found.")

                # Reverse order if "oldest" (ilk tweetlerden başla)
                if order == "oldest":
                    tweets = list(reversed(tweets))

                # Fetch replies for bestfriend detection (best effort, don't fail)
                bestfriend = None
                try:
                    replies = await tc.get_replies(username, max_tweets=150)
                    reply_counts = Counter()
                    if replies:
                        reply_counts.update(r["reply_to"] for r in replies)
                    # Also add mentions from normal tweets
                    for t in tweets:
                        for m in re.findall(r"@(\w+)", t.get("text", "")):
                            if m.lower() != username:
                                reply_counts[m.lower()] += 1
                    if reply_counts:
                        top = reply_counts.most_common(5)
                        bestfriend = [
                            {"username": u, "count": c} for u, c in top
                        ]
                except Exception:
                    pass

                stats = compute_stats(tweets)
                if bestfriend:
                    stats["x_bestfriend"] = bestfriend

                gpt_analysis = await generate_profile_analysis(profile, stats, tweets)

                await save_analysis(username, cache_scope, profile, tweets, stats, gpt_analysis)

                # Build data warnings
                data_warning = None
                tweet_count = len(tweets)
                total_account = profile.get("tweet_count", 0)
                if tweet_count < limit and tweet_count < total_account:
                    data_warning = f"İstenen {limit} tweet yerine yalnızca {tweet_count} tweet çekilebildi. Hesapta toplam {total_account:,} tweet var. Rate limit veya API kısıtlaması nedeniyle tüm tweetler alınamadı."
                elif tweet_count < limit and tweet_count >= total_account:
                    data_warning = f"İstenen {limit} tweet yerine {tweet_count} tweet analiz edildi. Bu hesap toplamda {total_account:,} uygun tweete sahip."
                elif tweet_count < 50:
                    data_warning = f"Bu hesaptan yalnızca {tweet_count} tweet analiz edilebildi. Analiz için yeterli veri olmayabilir, sonuçlar düşük güvenilirlikte olabilir."
                elif total_account and total_account > 10000:
                    data_warning = f"Bu hesapta toplam {total_account:,} tweet bulunuyor ancak yalnızca {tweet_count} tanesi analiz edildi. Çok fazla veri olduğundan analiz, hesabın tamamını temsil etmeyebilir."

                return {
                    "from_cache": False,
                    "profile": profile,
                    "stats": stats,
                    "gpt_analysis": gpt_analysis,
                    "analyzed_at": "just now",
                    "tweet_count": tweet_count,
                    "data_warning": data_warning,
                }

            except HTTPException:
                raise
            except Exception as e:
                error_str = str(e).lower()
                if "not found" in error_str:
                    await save_negative_cache(username, "user_not_found", str(e))
                    raise HTTPException(status_code=404, detail=f"@{username} adında bir kullanıcı bulunamadı.")
                elif "rate limit" in error_str or "429" in error_str:
                    raise HTTPException(status_code=429, detail="Twitter rate limit. Lütfen birkaç dakika sonra tekrar deneyin.")
                else:
                    raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    return {"status": "ok"}
