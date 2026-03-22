#!/usr/bin/env python3
"""
Admin CLI tool to view cached analyses.

Usage:
    python admin_view_cache.py [--detailed]

Options:
    --detailed    Show full analysis details for each cached user
    (no args)     Show summary list of cached users
"""
import asyncio
import sys
from datetime import datetime
from src.database import init_db, get_pool


async def get_cached_analyses(detailed=False):
    """Get all cached analyses with details"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        if detailed:
            query = """
                SELECT username, scope, tweet_count, analyzed_at, 
                       profile_data, stats_data, gpt_analysis
                FROM analyses
                ORDER BY analyzed_at DESC
            """
        else:
            query = """
                SELECT username, scope, tweet_count, analyzed_at
                FROM analyses
                ORDER BY analyzed_at DESC
            """
        rows = await conn.fetch(query)
        return rows


async def get_negative_cache():
    """Get negative cache entries"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        query = """
            SELECT username, error_type, cached_at
            FROM negative_cache
            ORDER BY cached_at DESC
        """
        rows = await conn.fetch(query)
        return rows


def format_time_ago(dt):
    """Format datetime as 'X hours/days ago'"""
    now = datetime.now(dt.tzinfo)
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "just now"


async def main():
    await init_db()
    
    detailed = '--detailed' in sys.argv
    
    print("=" * 70)
    print("CACHED ANALYSES")
    print("=" * 70)
    print()
    
    # Get cached analyses
    analyses = await get_cached_analyses(detailed)
    
    if not analyses:
        print("No cached analyses found.")
    else:
        print(f"Total: {len(analyses)} cached analyses\n")
        
        if detailed:
            # Detailed view
            for i, row in enumerate(analyses, 1):
                username = row['username']
                scope = row['scope']
                tweet_count = row['tweet_count'] or 0
                analyzed = row['analyzed_at']
                
                print(f"{i}. @{username}")
                print(f"   Scope: {scope} tweets (analyzed: {tweet_count} tweets)")
                print(f"   Cached: {format_time_ago(analyzed)} ({analyzed.strftime('%Y-%m-%d %H:%M')})")
                
                # Parse stats
                if row['stats_data']:
                    import json
                    stats = json.loads(row['stats_data'])
                    print(f"   Total tweets: {stats.get('total_tweets', 'N/A')}")
                    print(f"   Avg likes: {stats.get('avg_likes', 'N/A')}")
                    print(f"   Avg retweets: {stats.get('avg_retweets', 'N/A')}")
                
                # Parse GPT analysis
                if row['gpt_analysis']:
                    import json
                    gpt = json.loads(row['gpt_analysis'])
                    print(f"   Character: {gpt.get('character', 'N/A')}")
                    print(f"   Tone: {gpt.get('tone', 'N/A')}")
                
                print()
        else:
            # Summary view
            print(f"{'#':<4} {'Username':<20} {'Scope':<8} {'Analyzed':<10} {'Cached':<15}")
            print("-" * 70)
            
            for i, row in enumerate(analyses, 1):
                username = row['username']
                scope = row['scope']
                tweet_count = row['tweet_count'] or 0
                analyzed = row['analyzed_at']
                time_ago = format_time_ago(analyzed)
                
                print(f"{i:<4} @{username:<19} {scope:<8} {tweet_count:<10} {time_ago:<15}")
    
    # Get negative cache
    print()
    print("=" * 70)
    print("NEGATIVE CACHE (Failed Lookups)")
    print("=" * 70)
    print()
    
    negative = await get_negative_cache()
    
    if not negative:
        print("No negative cache entries.")
    else:
        print(f"Total: {len(negative)} failed lookups\n")
        print(f"{'#':<4} {'Username':<20} {'Error Type':<20} {'Cached':<15}")
        print("-" * 70)
        
        for i, row in enumerate(negative, 1):
            username = row['username']
            error_type = row['error_type']
            cached = row['cached_at']
            time_ago = format_time_ago(cached)
            
            print(f"{i:<4} @{username:<19} {error_type:<20} {time_ago:<15}")
    
    print()
    print("=" * 70)
    print()
    print("Usage:")
    print("  python admin_view_cache.py           # Summary view")
    print("  python admin_view_cache.py --detailed # Detailed view")
    print("  python admin_clear_cache.py --all    # Clear all cache")
    print()
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
