#!/usr/bin/env python3
"""
Admin CLI tool to clear database cache.

Usage:
    python admin_clear_cache.py [--all|--negative|--analyses]

Options:
    --all         Clear everything (analyses + negative cache)
    --negative    Clear only negative cache (failed user lookups)
    --analyses    Clear only analysis cache
    (no args)     Interactive mode - ask what to clear
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
        else:
            print(f"❌ Unknown option: {arg}")
            print("Usage: python admin_clear_cache.py [--all|--negative|--analyses]")
            return 1
    else:
        # Interactive mode
        print("What would you like to clear?")
        print("1. Negative cache only (failed lookups, rate limits)")
        print("2. Analyses cache only (successful analyses)")
        print("3. Everything (both)")
        print("4. Cancel")
        print()
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            await clear_negative_cache()
        elif choice == '2':
            await clear_analyses()
        elif choice == '3':
            await clear_negative_cache()
            await clear_analyses()
        elif choice == '4':
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
