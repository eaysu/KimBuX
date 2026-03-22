#!/usr/bin/env python3
"""
Admin CLI tool to refresh Twitter cookies.

Usage:
    python admin_refresh_cookies.py

This will:
1. Delete existing cookies.json
2. Login to Twitter with credentials from .env
3. Save new cookies.json
4. Display base64 encoded cookies for Render deployment
"""
import os
import json
import base64
import asyncio
from pathlib import Path
from src.twitter_client import TwitterClient
from src.config import COOKIES_PATH


async def main():
    print("=" * 70)
    print("TWITTER COOKIE REFRESH")
    print("=" * 70)
    print()
    
    # Check if cookies exist
    cookies_path = Path(COOKIES_PATH)
    if cookies_path.exists():
        print(f"⚠️  Existing cookies found at: {COOKIES_PATH}")
        choice = input("Delete and create new cookies? (y/n): ").strip().lower()
        if choice != 'y':
            print("Cancelled.")
            return 0
        cookies_path.unlink()
        print(f"✅ Deleted old cookies")
        print()
    
    # Login and create new cookies
    print("🔄 Logging in to Twitter...")
    print("   (This may take 10-30 seconds)")
    print()
    
    try:
        tc = TwitterClient()
        await tc.login()
        print("✅ Login successful!")
        print(f"✅ Cookies saved to: {COOKIES_PATH}")
        print()
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return 1
    
    # Read and encode cookies
    try:
        with open(COOKIES_PATH, 'r') as f:
            cookies_dict = json.load(f)
        
        cookies_json = json.dumps(cookies_dict)
        cookies_b64 = base64.b64encode(cookies_json.encode('utf-8')).decode('utf-8')
        
        # Save to file
        output_file = Path("cookies_base64.txt")
        with open(output_file, 'w') as f:
            f.write(cookies_b64)
        
        print("=" * 70)
        print("RENDER DEPLOYMENT")
        print("=" * 70)
        print()
        print("To use these cookies on Render:")
        print()
        print("1. Go to Render dashboard → Your service → Environment")
        print("2. Add or update environment variable:")
        print()
        print("   Key:   TWITTER_COOKIES_BASE64")
        print(f"   Value: {cookies_b64[:50]}...")
        print()
        print(f"3. Full value saved to: {output_file}")
        print("   (Copy from file if needed)")
        print()
        print("4. Save and redeploy")
        print()
        print("=" * 70)
        print()
        print("✅ Cookie refresh complete!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error encoding cookies: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
