#!/usr/bin/env python3
"""
Admin CLI tool to import Twitter cookies to database for production use.

Usage:
    python admin_cookie_import.py

This will:
1. Read cookies.json from local filesystem
2. Encode to base64
3. Display the base64 string for Render environment variable
"""
import json
import base64
import os
from pathlib import Path


def main():
    cookies_path = Path("cookies.json")
    
    if not cookies_path.exists():
        print("❌ Error: cookies.json not found in current directory")
        print("\nMake sure you have a valid cookies.json file.")
        print("You can generate it by running the app locally first.")
        return 1
    
    try:
        # Read cookies
        with open(cookies_path, 'r') as f:
            cookies_dict = json.load(f)
        
        # Validate cookies
        if not isinstance(cookies_dict, dict):
            print("❌ Error: cookies.json is not a valid JSON object")
            return 1
        
        # Encode to base64
        cookies_json = json.dumps(cookies_dict)
        cookies_b64 = base64.b64encode(cookies_json.encode('utf-8')).decode('utf-8')
        
        # Display results
        print("✅ Cookies successfully encoded!\n")
        print("=" * 70)
        print("RENDER ENVIRONMENT VARIABLE")
        print("=" * 70)
        print("\nKey:   TWITTER_COOKIES_BASE64")
        print(f"Value: {cookies_b64}\n")
        print("=" * 70)
        print("\nInstructions:")
        print("1. Go to Render dashboard → Your service → Environment")
        print("2. Click 'Add Environment Variable'")
        print("3. Key: TWITTER_COOKIES_BASE64")
        print("4. Value: Copy the base64 string above")
        print("5. Save and redeploy")
        print("\nNote: This will allow Render to use your local cookies")
        print("      without needing to login on every restart.")
        print("=" * 70)
        
        # Save to file for easy copy
        output_file = Path("cookies_base64.txt")
        with open(output_file, 'w') as f:
            f.write(cookies_b64)
        
        print(f"\n✅ Base64 string also saved to: {output_file}")
        print("   You can copy it from there if needed.\n")
        
        return 0
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in cookies.json: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
