import json
import asyncio
from datetime import datetime, timezone, timedelta
import asyncpg
from src.config import (
    DATABASE_URL, ACTIVE_ACCOUNT_DAILY_TWEETS,
    ACTIVE_ACCOUNT_TTL_DAYS, INACTIVE_ACCOUNT_TTL_DAYS,
    ANALYSIS_VERSION
)


_pool: asyncpg.Pool | None = None
_locks: dict[str, asyncio.Lock] = {}


async def get_pool() -> asyncpg.Pool:
    """Get or create connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def close_pool():
    """Close connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    """Create tables if they don't exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                scope INT NOT NULL,
                analysis_version TEXT NOT NULL,
                profile_data JSONB,
                tweets_data JSONB,
                stats_data JSONB,
                gpt_analysis JSONB,
                analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                tweet_count INT,
                is_active_account BOOLEAN DEFAULT FALSE,
                ttl_expires_at TIMESTAMPTZ NOT NULL,
                UNIQUE(username, scope, analysis_version)
            );

            CREATE TABLE IF NOT EXISTS negative_cache (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT,
                cached_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                expires_at TIMESTAMPTZ NOT NULL,
                UNIQUE(username, error_type)
            );

            CREATE INDEX IF NOT EXISTS idx_analyses_username ON analyses(username);
            CREATE INDEX IF NOT EXISTS idx_negative_cache_username ON negative_cache(username);
        """)


def get_analysis_lock(username: str) -> asyncio.Lock:
    """Get or create a lock for a specific username to prevent concurrent analysis."""
    if username not in _locks:
        _locks[username] = asyncio.Lock()
    return _locks[username]


async def get_cached_analysis(username: str, scope: int) -> dict | None:
    """
    Check if a valid (non-expired) analysis exists.
    Returns the cached result or None.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT profile_data, tweets_data, stats_data, gpt_analysis,
                   analyzed_at, tweet_count, is_active_account, ttl_expires_at
            FROM analyses
            WHERE username = $1 AND scope = $2 AND analysis_version = $3
              AND ttl_expires_at > NOW()
            ORDER BY analyzed_at DESC
            LIMIT 1
            """,
            username.lower(), scope, ANALYSIS_VERSION,
        )
        if row is None:
            return None
        return {
            "profile": json.loads(row["profile_data"]),
            "tweets": json.loads(row["tweets_data"]),
            "stats": json.loads(row["stats_data"]),
            "gpt_analysis": json.loads(row["gpt_analysis"]),
            "analyzed_at": row["analyzed_at"].isoformat(),
            "tweet_count": row["tweet_count"],
            "is_active_account": row["is_active_account"],
            "from_cache": True,
        }


async def save_analysis(
    username: str,
    scope: int,
    profile: dict,
    tweets: list[dict],
    stats: dict,
    gpt_analysis: dict,
):
    """Save analysis results to DB with appropriate TTL."""
    pool = await get_pool()
    now = datetime.now(timezone.utc)

    # Determine if active account
    total_tweets = profile.get("tweet_count", 0)
    account_age_days = 1  # fallback
    created_at = profile.get("created_at")
    if created_at:
        try:
            if isinstance(created_at, str):
                created_dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            else:
                created_dt = created_at
            account_age_days = max((now - created_dt).days, 1)
        except (ValueError, TypeError):
            pass

    daily_avg = total_tweets / account_age_days
    is_active = daily_avg >= ACTIVE_ACCOUNT_DAILY_TWEETS
    ttl_days = ACTIVE_ACCOUNT_TTL_DAYS if is_active else INACTIVE_ACCOUNT_TTL_DAYS
    ttl_expires = now + timedelta(days=ttl_days)

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO analyses
                (username, scope, analysis_version, profile_data, tweets_data,
                 stats_data, gpt_analysis, analyzed_at, tweet_count,
                 is_active_account, ttl_expires_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (username, scope, analysis_version)
            DO UPDATE SET
                profile_data = EXCLUDED.profile_data,
                tweets_data = EXCLUDED.tweets_data,
                stats_data = EXCLUDED.stats_data,
                gpt_analysis = EXCLUDED.gpt_analysis,
                analyzed_at = EXCLUDED.analyzed_at,
                tweet_count = EXCLUDED.tweet_count,
                is_active_account = EXCLUDED.is_active_account,
                ttl_expires_at = EXCLUDED.ttl_expires_at
            """,
            username.lower(), scope, ANALYSIS_VERSION,
            json.dumps(profile, default=str),
            json.dumps(tweets, default=str),
            json.dumps(stats, default=str),
            json.dumps(gpt_analysis, default=str),
            now, len(tweets), is_active, ttl_expires,
        )


async def get_negative_cache(username: str) -> dict | None:
    """Check if there's a valid negative cache entry for this username."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT error_type, error_message, cached_at, expires_at
            FROM negative_cache
            WHERE username = $1 AND expires_at > NOW()
            ORDER BY cached_at DESC LIMIT 1
            """,
            username.lower(),
        )
        if row is None:
            return None
        return {
            "error_type": row["error_type"],
            "error_message": row["error_message"],
            "cached_at": row["cached_at"].isoformat(),
        }


async def save_negative_cache(username: str, error_type: str, error_message: str):
    """
    Save a negative cache entry.
    - user_not_found: 24h TTL
    - rate_limit: 15min TTL
    - other errors: 5min TTL
    """
    ttl_map = {
        "user_not_found": timedelta(hours=24),
        "protected_account": timedelta(hours=24),
        "rate_limit": timedelta(minutes=15),
    }
    ttl = ttl_map.get(error_type, timedelta(minutes=5))
    expires = datetime.now(timezone.utc) + ttl

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO negative_cache (username, error_type, error_message, expires_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (username, error_type)
            DO UPDATE SET
                error_message = EXCLUDED.error_message,
                cached_at = NOW(),
                expires_at = EXCLUDED.expires_at
            """,
            username.lower(), error_type, error_message, expires,
        )
