#!/usr/bin/env python3
"""
Admin CLI tool to clear database cache.

Usage:
    python admin_clear_cache.py [--all|--negative|--analyses|--username USERNAME]

Options:
    --all              Clear everything (analyses + negative cache)
    --negative         Clear only negative cache (failed user lookups)
    --analyses         Clear only analysis cache
    --username USER    Clear cache for specific username only
    (no args)          Interactive mode - ask what to clear
"""
import asyncio
import sys
from src.database import init_db, get_pool


async def clear_negative_cache():
    """Clear negative cache (failed lookups, rate limits, etc.)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute('DELETE FROM negative_cache')
        count = int(result.split()[-1]) if result else 0
        print(f"✅ Cleared {count} negative cache entries")
        return count


async def clear_analyses():
    """Clear all cached analyses"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute('DELETE FROM analyses')
        count = int(result.split()[-1]) if result else 0
        print(f"✅ Cleared {count} cached analyses")
        return count


async def clear_username_cache(username: str):
    """Clear cache for specific username"""
    username = username.lstrip('@').strip().lower()
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Clear from analyses
        result_analyses = await conn.execute(
            'DELETE FROM analyses WHERE username = $1', username
        )
        count_analyses = int(result_analyses.split()[-1]) if result_analyses else 0
        
        # Clear from negative cache
        result_negative = await conn.execute(
            'DELETE FROM negative_cache WHERE username = $1', username
        )
        count_negative = int(result_negative.split()[-1]) if result_negative else 0
        
        total = count_analyses + count_negative
        if total > 0:
            print(f"✅ Cleared cache for @{username}:")
            if count_analyses > 0:
                print(f"   - {count_analyses} analysis cache entry/entries")
            if count_negative > 0:
                print(f"   - {count_negative} negative cache entry/entries")
        else:
            print(f"ℹ️  No cache found for @{username}")
        
        return total


async def list_cached_usernames():
    """List all cached usernames"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Get from analyses
        analyses = await conn.fetch(
            'SELECT username, created_at FROM analyses ORDER BY created_at DESC'
        )
        # Get from negative cache
        negative = await conn.fetch(
            'SELECT username, cached_at FROM negative_cache ORDER BY cached_at DESC'
        )
        
        return analyses, negative


async def get_stats():
    """Get current cache statistics"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        analyses_count = await conn.fetchval('SELECT COUNT(*) FROM analyses')
        negative_count = await conn.fetchval('SELECT COUNT(*) FROM negative_cache')
        return analyses_count, negative_count


async def main():
    await init_db()
    
    # Get current stats
    analyses_count, negative_count = await get_stats()
    
    print("=" * 70)
    print("CACHE STATISTICS")
    print("=" * 70)
    print(f"Cached analyses:      {analyses_count}")
    print(f"Negative cache:       {negative_count}")
    print("=" * 70)
    print()
    
    # Parse arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == '--all':
            print("Clearing ALL cache...")
            await clear_negative_cache()
            await clear_analyses()
        elif arg == '--negative':
            print("Clearing negative cache...")
            await clear_negative_cache()
        elif arg == '--analyses':
            print("Clearing analyses cache...")
            await clear_analyses()
        elif arg == '--username':
            if len(sys.argv) < 3:
                print("❌ Error: --username requires a username argument")
                print("Usage: python admin_clear_cache.py --username USERNAME")
                return 1
            username = sys.argv[2]
            print(f"Clearing cache for @{username.lstrip('@')}...")
            await clear_username_cache(username)
        else:
            print(f"❌ Unknown option: {arg}")
            print("Usage: python admin_clear_cache.py [--all|--negative|--analyses|--username USERNAME]")
            return 1
    else:
        # Interactive mode
        print("What would you like to clear?")
        print("1. Negative cache only (failed lookups, rate limits)")
        print("2. Analyses cache only (successful analyses)")
        print("3. Everything (both)")
        print("4. Specific username")
        print("5. Cancel")
        print()
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            await clear_negative_cache()
        elif choice == '2':
            await clear_analyses()
        elif choice == '3':
            await clear_negative_cache()
            await clear_analyses()
        elif choice == '4':
            # Show cached usernames
            analyses, negative = await list_cached_usernames()
            if not analyses and not negative:
                print("\nℹ️  No cached usernames found.")
                return 0
            
            print("\n📋 Cached usernames:")
            print("-" * 70)
            
            all_usernames = set()
            if analyses:
                print("\nAnalysis cache:")
                for i, row in enumerate(analyses, 1):
                    print(f"  {i}. @{row['username']}")
                    all_usernames.add(row['username'])
            
            if negative:
                print("\nNegative cache (failed):")
                for row in negative:
                    if row['username'] not in all_usernames:
                        print(f"  • @{row['username']}")
                    all_usernames.add(row['username'])
            
            print("-" * 70)
            username = input("\nEnter username to clear (or 'cancel'): ").strip()
            if username.lower() == 'cancel':
                print("Cancelled.")
                return 0
            await clear_username_cache(username)
        elif choice == '5':
            print("Cancelled.")
            return 0
        else:
            print("❌ Invalid choice")
            return 1
    
    # Show new stats
    print()
    analyses_count, negative_count = await get_stats()
    print("=" * 70)
    print("NEW CACHE STATISTICS")
    print("=" * 70)
    print(f"Cached analyses:      {analyses_count}")
    print(f"Negative cache:       {negative_count}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
