import re
from datetime import datetime, timedelta, timezone
from src.config import RECENT_TOP_LIKED_DAYS
from src.text_processor import (
    get_word_frequencies, get_ngrams, detect_language, clean_tweet
)


def compute_stats(tweets: list[dict]) -> dict:
    """Compute all non-GPT analytics from tweet data."""
    if not tweets:
        return {"error": "No tweets to analyze"}

    original_count = sum(1 for t in tweets if not t["is_quote"])
    quote_count = sum(1 for t in tweets if t["is_quote"])
    total = len(tweets)

    cleaned_texts = [clean_tweet(t["text"]) for t in tweets]
    dominant_lang = detect_language(cleaned_texts)

    top_liked = _top_liked_tweets(tweets, top_n=10)
    recent_top_liked = _recent_top_liked_tweets(tweets, top_n=10)

    word_freq = get_word_frequencies(tweets, top_n=20)
    bigrams = get_ngrams(tweets, n=2, top_n=15)
    trigrams = get_ngrams(tweets, n=3, top_n=10)
    top_mentions = _top_mentions(tweets)

    return {
        "total_analyzed": total,
        "original_count": original_count,
        "quote_count": quote_count,
        "original_ratio": round(original_count / total, 2) if total else 0,
        "quote_ratio": round(quote_count / total, 2) if total else 0,
        "dominant_language": dominant_lang,
        "top_liked": top_liked,
        "recent_top_liked": recent_top_liked,
        "word_frequencies": word_freq,
        "bigrams": bigrams,
        "trigrams": trigrams,
        "top_mentions": top_mentions,
    }


def _top_liked_tweets(tweets: list[dict], top_n: int = 5) -> list[dict]:
    """Get top N most liked tweets overall."""
    sorted_tweets = sorted(tweets, key=lambda t: t["favorite_count"], reverse=True)
    return [
        {
            "id": t["id"],
            "text": t["text"][:280],
            "favorite_count": t["favorite_count"],
            "retweet_count": t["retweet_count"],
            "created_at": t["created_at"],
            "url": t.get("url", ""),
        }
        for t in sorted_tweets[:top_n]
    ]


def _recent_top_liked_tweets(tweets: list[dict], top_n: int = 10) -> list[dict]:
    """Get top N most liked tweets from the last RECENT_TOP_LIKED_DAYS days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_TOP_LIKED_DAYS)

    recent = []
    for t in tweets:
        created = t["created_at"]
        if isinstance(created, str):
            try:
                # Twitter format: "Mon Oct 10 20:19:24 +0000 2022"
                created = datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y")
            except (ValueError, TypeError):
                continue
        if created and created >= cutoff:
            recent.append(t)

    sorted_recent = sorted(recent, key=lambda t: t["favorite_count"], reverse=True)
    return [
        {
            "id": t["id"],
            "text": t["text"][:280],
            "favorite_count": t["favorite_count"],
            "retweet_count": t["retweet_count"],
            "created_at": t["created_at"],
            "url": t.get("url", ""),
        }
        for t in sorted_recent[:top_n]
    ]


def _top_mentions(tweets: list[dict], top_n: int = 10) -> list[dict]:
    """Extract most mentioned accounts from tweet texts (X bestfriend detection)."""
    mention_counts: dict[str, int] = {}
    for t in tweets:
        text = t.get("text", "")
        mentions = re.findall(r"@(\w+)", text)
        for m in mentions:
            m_lower = m.lower()
            mention_counts[m_lower] = mention_counts.get(m_lower, 0) + 1

    sorted_mentions = sorted(mention_counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {"username": username, "count": count}
        for username, count in sorted_mentions[:top_n]
    ]
