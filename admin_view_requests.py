#!/usr/bin/env python3
"""
Admin CLI tool to view analysis request logs.

Usage:
    python admin_view_requests.py [options]

Options:
    --today          Show only today's requests
    --last-hour      Show requests from last hour
    --ip <IP>        Filter by IP address
    --username <UN>  Filter by username
    --limit <N>      Limit results (default: 50)
    --failures       Show only failed requests
    --successes      Show only successful requests
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from src.database import init_db, get_pool


async def get_request_logs(
    hours_ago: int = None,
    ip_filter: str = None,
    username_filter: str = None,
    only_failures: bool = False,
    only_successes: bool = False,
    limit: int = 50
):
    """Get request logs with optional filters."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        conditions = []
        params = []
        param_count = 0
        
        if hours_ago is not None:
            param_count += 1
            conditions.append(f"requested_at >= NOW() - INTERVAL '{hours_ago} hours'")
        
        if ip_filter:
            param_count += 1
            conditions.append(f"ip_address = ${param_count}")
            params.append(ip_filter)
        
        if username_filter:
            param_count += 1
            conditions.append(f"username = ${param_count}")
            params.append(username_filter.lower())
        
        if only_failures:
            conditions.append("success = FALSE")
        elif only_successes:
            conditions.append("success = TRUE")
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        query = f"""
            SELECT ip_address, username, tweet_limit, order_type, 
                   from_cache, success, error_message, requested_at
            FROM request_logs
            WHERE {where_clause}
            ORDER BY requested_at DESC
            LIMIT {limit}
        """
        
        rows = await conn.fetch(query, *params)
        return rows


async def get_stats(hours_ago: int = None):
    """Get request statistics."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        time_filter = f"WHERE requested_at >= NOW() - INTERVAL '{hours_ago} hours'" if hours_ago else ""
        
        # Total requests
        total = await conn.fetchval(f"SELECT COUNT(*) FROM request_logs {time_filter}")
        
        # Success/failure counts
        success_count = await conn.fetchval(
            f"SELECT COUNT(*) FROM request_logs {time_filter} {'AND' if time_filter else 'WHERE'} success = TRUE"
        )
        failure_count = total - success_count
        
        # Cache hit rate
        cache_hits = await conn.fetchval(
            f"SELECT COUNT(*) FROM request_logs {time_filter} {'AND' if time_filter else 'WHERE'} from_cache = TRUE"
        )
        cache_rate = (cache_hits / total * 100) if total > 0 else 0
        
        # Top requested usernames
        top_usernames = await conn.fetch(f"""
            SELECT username, COUNT(*) as count
            FROM request_logs
            {time_filter}
            GROUP BY username
            ORDER BY count DESC
            LIMIT 10
        """)
        
        # Top IPs
        top_ips = await conn.fetch(f"""
            SELECT ip_address, COUNT(*) as count
            FROM request_logs
            {time_filter}
            GROUP BY ip_address
            ORDER BY count DESC
            LIMIT 10
        """)
        
        return {
            'total': total,
            'success': success_count,
            'failure': failure_count,
            'cache_rate': cache_rate,
            'top_usernames': top_usernames,
            'top_ips': top_ips
        }


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
    
    # Parse arguments
    hours_ago = None
    ip_filter = None
    username_filter = None
    only_failures = False
    only_successes = False
    limit = 50
    show_stats = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--today':
            hours_ago = 24
        elif arg == '--last-hour':
            hours_ago = 1
        elif arg == '--ip' and i + 1 < len(sys.argv):
            ip_filter = sys.argv[i + 1]
            i += 1
        elif arg == '--username' and i + 1 < len(sys.argv):
            username_filter = sys.argv[i + 1]
            i += 1
        elif arg == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 1
        elif arg == '--failures':
            only_failures = True
        elif arg == '--successes':
            only_successes = True
        elif arg == '--stats':
            show_stats = True
        
        i += 1
    
    print("=" * 100)
    print("ADMIN REQUEST LOGS")
    print("=" * 100)
    print()
    
    # Show statistics
    if show_stats or (not ip_filter and not username_filter):
        stats = await get_stats(hours_ago)
        
        time_desc = f"Last {hours_ago} hours" if hours_ago else "All time"
        print(f"📊 STATISTICS ({time_desc})")
        print("-" * 100)
        print(f"Total requests:      {stats['total']}")
        print(f"  ✅ Successful:      {stats['success']} ({stats['success']/stats['total']*100:.1f}%)" if stats['total'] > 0 else "  ✅ Successful:      0")
        print(f"  ❌ Failed:          {stats['failure']} ({stats['failure']/stats['total']*100:.1f}%)" if stats['total'] > 0 else "  ❌ Failed:          0")
        print(f"Cache hit rate:      {stats['cache_rate']:.1f}%")
        print()
        
        if stats['top_usernames']:
            print("Top requested accounts:")
            for idx, row in enumerate(stats['top_usernames'][:5], 1):
                print(f"  {idx}. @{row['username']:<20} {row['count']:>4}×")
        print()
        
        if stats['top_ips']:
            print("Top IP addresses:")
            for idx, row in enumerate(stats['top_ips'][:5], 1):
                print(f"  {idx}. {row['ip_address']:<20} {row['count']:>4} requests")
        print()
    
    # Show request logs
    logs = await get_request_logs(
        hours_ago=hours_ago,
        ip_filter=ip_filter,
        username_filter=username_filter,
        only_failures=only_failures,
        only_successes=only_successes,
        limit=limit
    )
    
    if not logs:
        print("No requests found with the specified filters.")
    else:
        filters = []
        if hours_ago: filters.append(f"last {hours_ago}h")
        if ip_filter: filters.append(f"IP={ip_filter}")
        if username_filter: filters.append(f"user=@{username_filter}")
        if only_failures: filters.append("failures only")
        if only_successes: filters.append("successes only")
        
        filter_text = f" ({', '.join(filters)})" if filters else ""
        print(f"📋 REQUEST LOG{filter_text}")
        print("-" * 100)
        print(f"{'#':<4} {'IP Address':<18} {'Username':<20} {'Limit':<6} {'Cache':<6} {'Status':<8} {'Time':<15}")
        print("-" * 100)
        
        for idx, row in enumerate(logs, 1):
            ip = row['ip_address']
            username = f"@{row['username']}"
            limit_val = row['tweet_limit']
            cache = "✓" if row['from_cache'] else "✗"
            status = "✅ OK" if row['success'] else "❌ FAIL"
            time_ago = format_time_ago(row['requested_at'])
            
            print(f"{idx:<4} {ip:<18} {username:<20} {limit_val:<6} {cache:<6} {status:<8} {time_ago:<15}")
            
            if not row['success'] and row['error_message']:
                error = row['error_message'][:60] + "..." if len(row['error_message']) > 60 else row['error_message']
                print(f"     └─ Error: {error}")
    
    print()
    print("=" * 100)
    print()
    print("Usage examples:")
    print("  python admin_view_requests.py --stats                # Show statistics")
    print("  python admin_view_requests.py --today                # Today's requests")
    print("  python admin_view_requests.py --last-hour            # Last hour")
    print("  python admin_view_requests.py --ip 123.45.67.89      # Filter by IP")
    print("  python admin_view_requests.py --username nasa        # Filter by username")
    print("  python admin_view_requests.py --failures             # Show only failures")
    print("  python admin_view_requests.py --limit 100            # Show more results")
    print()
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
