import re
import os
import time
import asyncio
from collections import Counter
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.config import TWEET_LIMITS
from src.twitter_client import TwitterClient
from src.analyzer import compute_stats
from src.gpt_analyzer import generate_profile_analysis
from src.database import (
    init_db, get_cached_analysis, save_analysis,
    get_negative_cache, save_negative_cache,
    get_analysis_lock, close_pool, check_rate_limit,
    log_request,
)

app = FastAPI(title="KimBuX API")

# Global semaphore: max 1 concurrent Twitter analysis - queue other requests
_analysis_semaphore = asyncio.Semaphore(1)

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
async def analyze(req: AnalyzeRequest, request: Request):
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    admin_ips = os.getenv("ADMIN_IPS", "").split(",") if os.getenv("ADMIN_IPS") else []
    
    is_allowed, remaining = await check_rate_limit(client_ip, max_requests=10, admin_ips=admin_ips)
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "Günlük analiz limitinize ulaştınız. Yarın tekrar deneyin.",
                "limit": 10,
                "remaining": 0,
                "reset_at": "midnight UTC"
            }
        )
    
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
        # Log cache hit
        await log_request(client_ip, username, limit, order, from_cache=True, success=True)
        
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

    # Semaphore: max 1 concurrent analysis globally - others wait in queue
    if _analysis_semaphore._value == 0:
        raise HTTPException(status_code=429, detail="Sırada bekleyin. Başka bir analiz devam ediyor.")

    async with _analysis_semaphore:
        async with lock:
            try:
                # Performance timing
                timings = {}
                start_total = time.time()
                
                # Login
                start = time.time()
                tc = TwitterClient()
                await tc.login()
                timings["login"] = round(time.time() - start, 2)
                
                # Profile fetch
                start = time.time()
                profile = await tc.get_profile(username)
                timings["profile_fetch"] = round(time.time() - start, 2)

                if profile.get("protected"):
                    await save_negative_cache(username, "protected_account", "This account is protected.")
                    raise HTTPException(status_code=403, detail="Protected account.")

                # Tweet scraping
                start = time.time()
                tweets = await tc.get_tweets(username, limit=limit)
                timings["tweet_scrape"] = round(time.time() - start, 2)
                
                if not tweets:
                    raise HTTPException(status_code=404, detail="No eligible tweets found.")

                # Reverse order if "oldest" (ilk tweetlerden başla)
                if order == "oldest":
                    tweets = list(reversed(tweets))

                # Stats computation
                start = time.time()
                stats = compute_stats(tweets)
                timings["stats_compute"] = round(time.time() - start, 2)

                # GPT analysis
                start = time.time()
                gpt_analysis = await generate_profile_analysis(profile, stats, tweets)
                timings["gpt_analysis"] = round(time.time() - start, 2)

                # Database save
                start = time.time()
                await save_analysis(username, cache_scope, profile, tweets, stats, gpt_analysis)
                timings["db_save"] = round(time.time() - start, 2)
                
                # Total time
                timings["total"] = round(time.time() - start_total, 2)

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

                # Log performance metrics
                print(f"\n{'='*70}")
                print(f"PERFORMANCE METRICS - @{username} ({limit} tweets)")
                print(f"{'='*70}")
                print(f"Login:           {timings['login']}s")
                print(f"Profile fetch:   {timings['profile_fetch']}s")
                print(f"Tweet scrape:    {timings['tweet_scrape']}s")
                print(f"Stats compute:   {timings['stats_compute']}s")
                print(f"GPT analysis:    {timings['gpt_analysis']}s")
                print(f"DB save:         {timings['db_save']}s")
                print(f"{'='*70}")
                print(f"TOTAL:           {timings['total']}s")
                print(f"{'='*70}\n")

                # Log successful request
                await log_request(client_ip, username, limit, order, from_cache=False, success=True)

                return {
                    "from_cache": False,
                    "profile": profile,
                    "stats": stats,
                    "gpt_analysis": gpt_analysis,
                    "analyzed_at": "just now",
                    "tweet_count": tweet_count,
                    "data_warning": data_warning,
                    "performance": timings,
                }

            except HTTPException as http_exc:
                # Log failed request
                await log_request(client_ip, username, limit, order, from_cache=False, success=False, error_message=str(http_exc.detail))
                raise
            except Exception as e:
                error_str = str(e).lower()
                # Log failed request
                await log_request(client_ip, username, limit, order, from_cache=False, success=False, error_message=str(e))
                
                if "not found" in error_str:
                    await save_negative_cache(username, "user_not_found", str(e))
                    raise HTTPException(status_code=404, detail=f"@{username} adında bir kullanıcı bulunamadı.")
                elif "rate limit" in error_str or "429" in error_str:
                    raise HTTPException(status_code=429, detail="Twitter rate limit. Lütfen birkaç dakika sonra tekrar deneyin.")
                else:
                    raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/preview/{username}")
async def preview_tweets(username: str):
    """
    Quick preview of user's tweets for loading animation.
    Returns first 10-15 tweets without full analysis.
    """
    username = username.lstrip("@").strip().lower()
    
    try:
        tc = TwitterClient()
        await tc.login()
        
        # Just get first 15 tweets quickly
        tweets = await tc.get_tweets(username, limit=15)
        
        if not tweets:
            return {"tweets": []}
        
        # Return just the text
        preview_tweets = [{"text": t.get("text", "")} for t in tweets[:15] if t.get("text")]
        
        return {"tweets": preview_tweets}
    except Exception:
        # If preview fails, return empty - don't block main analysis
        return {"tweets": []}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
