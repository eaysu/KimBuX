#!/usr/bin/env python3
"""
Admin CLI tool to reset rate limit for a specific IP address.

Usage:
    python admin_reset_rate_limit.py [IP_ADDRESS]
    python admin_reset_rate_limit.py --my-ip
    python admin_reset_rate_limit.py --all

Examples:
    python admin_reset_rate_limit.py 123.45.67.89
    python admin_reset_rate_limit.py --my-ip  # Reset your own IP
    python admin_reset_rate_limit.py --all    # Reset all IPs
"""
import asyncio
import sys
import requests
from src.database import init_db, get_pool


async def get_my_ip():
    """Get current public IP address."""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Failed to get IP: {e}")
        return None


async def reset_ip_rate_limit(ip_address: str):
    """Reset rate limit for a specific IP."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            DELETE FROM rate_limits
            WHERE ip_address = $1
            """,
            ip_address
        )
        # Extract count from result like "DELETE 1"
        count = int(result.split()[-1]) if result and result.split() else 0
        return count


async def reset_all_rate_limits():
    """Reset all rate limits."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM rate_limits")
        count = int(result.split()[-1]) if result and result.split() else 0
        return count


async def get_rate_limit_info(ip_address: str):
    """Get current rate limit info for an IP."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT request_count, last_request_at, reset_at
            FROM rate_limits
            WHERE ip_address = $1
            """,
            ip_address
        )
        return row


async def list_all_rate_limits():
    """List all current rate limits."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT ip_address, request_count, last_request_at, reset_at
            FROM rate_limits
            ORDER BY last_request_at DESC
            """
        )
        return rows


async def main():
    await init_db()
    
    print("=" * 70)
    print("RATE LIMIT RESET TOOL")
    print("=" * 70)
    print()
    
    # Parse arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--my-ip':
            # Reset current IP
            my_ip = await get_my_ip()
            if not my_ip:
                return 1
            
            print(f"Your IP: {my_ip}\n")
            
            # Show current status
            info = await get_rate_limit_info(my_ip)
            if info:
                print(f"Current status:")
                print(f"  Requests today: {info['request_count']}")
                print(f"  Last request: {info['last_request_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Resets at: {info['reset_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print()
            else:
                print("No rate limit record found for your IP.\n")
            
            # Reset
            count = await reset_ip_rate_limit(my_ip)
            if count > 0:
                print(f"✅ Rate limit reset for {my_ip}")
            else:
                print(f"ℹ️  No rate limit to reset for {my_ip}")
        
        elif arg == '--all':
            # List all first
            print("Current rate limits:\n")
            rows = await list_all_rate_limits()
            if rows:
                print(f"{'IP Address':<20} {'Requests':<10} {'Last Request':<20}")
                print("-" * 70)
                for row in rows:
                    print(f"{row['ip_address']:<20} {row['request_count']:<10} {row['last_request_at'].strftime('%Y-%m-%d %H:%M'):<20}")
                print()
            else:
                print("No rate limits found.\n")
            
            # Confirm
            choice = input(f"Reset ALL {len(rows)} rate limits? (y/n): ").strip().lower()
            if choice == 'y':
                count = await reset_all_rate_limits()
                print(f"\n✅ Reset {count} rate limit(s)")
            else:
                print("\nCancelled.")
        
        elif arg.startswith('--'):
            print(f"❌ Unknown option: {arg}")
            print("\nUsage:")
            print("  python admin_reset_rate_limit.py [IP_ADDRESS]")
            print("  python admin_reset_rate_limit.py --my-ip")
            print("  python admin_reset_rate_limit.py --all")
            return 1
        
        else:
            # Reset specific IP
            ip_address = arg
            
            # Show current status
            info = await get_rate_limit_info(ip_address)
            if info:
                print(f"Current status for {ip_address}:")
                print(f"  Requests today: {info['request_count']}")
                print(f"  Last request: {info['last_request_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Resets at: {info['reset_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print()
            else:
                print(f"No rate limit record found for {ip_address}.\n")
            
            # Reset
            count = await reset_ip_rate_limit(ip_address)
            if count > 0:
                print(f"✅ Rate limit reset for {ip_address}")
            else:
                print(f"ℹ️  No rate limit to reset for {ip_address}")
    
    else:
        # Interactive mode
        print("What would you like to do?")
        print("1. Reset my IP")
        print("2. Reset specific IP")
        print("3. Reset all IPs")
        print("4. List all rate limits")
        print("5. Cancel")
        print()
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            my_ip = await get_my_ip()
            if my_ip:
                count = await reset_ip_rate_limit(my_ip)
                print(f"\n✅ Rate limit reset for {my_ip}")
        
        elif choice == '2':
            ip = input("Enter IP address: ").strip()
            if ip:
                count = await reset_ip_rate_limit(ip)
                print(f"\n✅ Rate limit reset for {ip}")
        
        elif choice == '3':
            count = await reset_all_rate_limits()
            print(f"\n✅ Reset {count} rate limit(s)")
        
        elif choice == '4':
            rows = await list_all_rate_limits()
            if rows:
                print()
                print(f"{'IP Address':<20} {'Requests':<10} {'Last Request':<20}")
                print("-" * 70)
                for row in rows:
                    print(f"{row['ip_address']:<20} {row['request_count']:<10} {row['last_request_at'].strftime('%Y-%m-%d %H:%M'):<20}")
            else:
                print("\nNo rate limits found.")
        
        elif choice == '5':
            print("Cancelled.")
            return 0
        
        else:
            print("❌ Invalid choice")
            return 1
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
