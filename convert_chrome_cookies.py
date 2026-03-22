#!/usr/bin/env python3
"""
Convert Chrome extension JSON cookies to Twikit format.
"""

import json

# Read Chrome format cookies
with open('cookies.txt', 'r') as f:
    chrome_cookies = json.load(f)

# Convert to simple key-value format for Twikit
twikit_cookies = {}
for cookie in chrome_cookies:
    name = cookie.get('name')
    value = cookie.get('value')
    if name and value:
        twikit_cookies[name] = value

# Save as cookies.json
with open('cookies.json', 'w') as f:
    json.dump(twikit_cookies, f, indent=2)

print(f"✅ Converted {len(twikit_cookies)} cookies to cookies.json")
print("\nKey cookies found:")
for key in ['auth_token', 'ct0', 'auth_multi']:
    if key in twikit_cookies:
        print(f"  ✓ {key}")
    else:
        print(f"  ✗ {key} (missing)")

print("\nYou can now run: python main.py elonmusk 100")
