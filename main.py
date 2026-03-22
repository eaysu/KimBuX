import asyncio
import sys
from src.config import TWEET_LIMITS
from src.twitter_client import TwitterClient
from src.analyzer import compute_stats
from src.gpt_analyzer import generate_profile_analysis
from src.database import (
    init_db, get_cached_analysis, save_analysis,
    get_negative_cache, save_negative_cache,
    get_analysis_lock, close_pool,
)
from src.display import (
    console, display_results, display_status,
    display_error, display_cached_warning,
)


async def run_analysis(username: str, limit: int):
    """Main analysis pipeline."""
    username = username.lstrip("@").strip().lower()

    if not username:
        display_error("Username cannot be empty.")
        return

    if limit not in TWEET_LIMITS:
        display_error(f"Invalid limit. Choose from: {TWEET_LIMITS}")
        return

    display_status("Initializing database")
    await init_db()

    # Check negative cache
    neg = await get_negative_cache(username)
    if neg:
        display_cached_warning(neg["error_type"], neg["error_message"])
        return

    # Check positive cache
    display_status("Checking cache")
    cached = await get_cached_analysis(username, limit)
    if cached:
        console.print("  [green]✓ Found cached analysis[/]")
        display_results(
            profile=cached["profile"],
            stats=cached["stats"],
            gpt_analysis=cached["gpt_analysis"],
            meta={
                "from_cache": True,
                "analyzed_at": cached["analyzed_at"],
            },
        )
        return

    # Acquire lock to prevent concurrent analysis of same user
    lock = get_analysis_lock(username)
    if lock.locked():
        display_error(f"Analysis for @{username} is already in progress. Please wait.")
        return

    async with lock:
        try:
            # Fetch profile
            display_status(f"Fetching profile for @{username}")
            tc = TwitterClient()
            await tc.login()
            profile = await tc.get_profile(username)

            if profile.get("protected"):
                await save_negative_cache(username, "protected_account", "This account is protected.")
                display_error(f"@{username} is a protected account. Cannot analyze.")
                return

            # Fetch tweets
            display_status(f"Fetching last {limit} tweets (original + quote only)")
            tweets = await tc.get_tweets(username, limit=limit)

            if not tweets:
                display_error(f"No eligible tweets found for @{username}.")
                return

            console.print(f"  [green]✓ Fetched {len(tweets)} eligible tweets[/]")

            # Compute stats
            display_status("Computing statistics")
            stats = compute_stats(tweets)

            # GPT analysis
            display_status("Running GPT analysis (this may take a moment)")
            gpt_analysis = await generate_profile_analysis(profile, stats, tweets)

            # Save to DB
            display_status("Saving results to database")
            await save_analysis(username, limit, profile, tweets, stats, gpt_analysis)

            # Display
            display_results(
                profile=profile,
                stats=stats,
                gpt_analysis=gpt_analysis,
                meta={
                    "from_cache": False,
                    "analyzed_at": "just now",
                },
            )

        except Exception as e:
            error_str = str(e).lower()

            if "not found" in error_str or "user" in error_str and "exist" in error_str:
                await save_negative_cache(username, "user_not_found", str(e))
                display_error(f"User @{username} not found.")
            elif "rate limit" in error_str or "429" in error_str:
                await save_negative_cache(username, "rate_limit", str(e))
                display_error("Rate limited by Twitter. Please try again later.")
            elif "login" in error_str or "auth" in error_str or "session" in error_str:
                display_error(f"Authentication error: {e}\nCheck your .env credentials or delete cookies.json and retry.")
            else:
                display_error(f"Unexpected error: {e}")


async def main():
    """CLI entry point."""
    console.print("\n[bold cyan]╔══════════════════════════════╗[/]")
    console.print("[bold cyan]║        KimBuX Analyzer       ║[/]")
    console.print("[bold cyan]╚══════════════════════════════╝[/]\n")

    # Get username
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = console.input("[bold]Enter Twitter/X username:[/] @")

    # Get limit
    if len(sys.argv) > 2 and sys.argv[2].isdigit() and int(sys.argv[2]) in TWEET_LIMITS:
        limit = int(sys.argv[2])
    else:
        console.print(f"\n[bold]Select tweet analysis limit:[/]")
        for i, opt in enumerate(TWEET_LIMITS, 1):
            console.print(f"  {i}. Last {opt} tweets")

        choice = console.input("\n[bold]Choice (1/2/3):[/] ").strip()
        choice_map = {"1": TWEET_LIMITS[0], "2": TWEET_LIMITS[1], "3": TWEET_LIMITS[2]}
        limit = choice_map.get(choice, TWEET_LIMITS[0])

    console.print(f"\n  Analyzing [cyan]@{username}[/] — last [cyan]{limit}[/] tweets\n")

    try:
        await run_analysis(username, limit)
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
