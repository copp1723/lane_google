#!/usr/bin/env python3
"""
Simple Google Ads Refresh Token Generator
Using the official Google Ads approach
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("Google Ads API - Generate Refresh Token")
print("=" * 70)
print()
print("Since you're having OAuth issues, let's use Google's official tool:")
print()
print("1. Go to this URL:")
print("   https://developers.google.com/oauthplayground/")
print()
print("2. In the left panel, find and select:")
print("   'Google Ads API v17' > 'https://www.googleapis.com/auth/adwords'")
print()
print("3. Click the gear icon (⚙️) in the top right")
print()
print("4. Check ✓ 'Use your own OAuth credentials'")
print()
print("5. Enter your credentials from .env:")

# Get credentials from environment
client_id = os.getenv('GOOGLE_ADS_CLIENT_ID', '<Not found in .env>')
client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET', '<Not found in .env>')

print(f"   OAuth Client ID: {client_id}")
print(f"   OAuth Client secret: {client_secret}")
print()
print("6. Click 'Close', then click 'Authorize APIs'")
print()
print("7. Choose your Google Ads account and authorize")
print()
print("8. Click 'Exchange authorization code for tokens'")
print()
print("9. Copy the 'Refresh token' value")
print()
print("10. Add it to your .env file as:")
print("    GOOGLE_ADS_REFRESH_TOKEN=<your-refresh-token>")
print()
print("=" * 70)
print()
print("This method bypasses the OAuth configuration issues and uses")
print("Google's official OAuth playground for token generation.")
print()