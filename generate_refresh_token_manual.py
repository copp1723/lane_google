#!/usr/bin/env python3
"""
Google Ads API Refresh Token Generator - Manual Version
This version gives you a URL to open manually, allowing you to choose which account to use
"""

import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# The AdWords API OAuth2 scope
SCOPE = ['https://www.googleapis.com/auth/adwords']

def main():
    # Create credentials config from environment variables
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    client_config = {
        "installed": {
            "client_id": os.getenv('GOOGLE_ADS_CLIENT_ID', 'YOUR_CLIENT_ID'),
            "client_secret": os.getenv('GOOGLE_ADS_CLIENT_SECRET', 'YOUR_CLIENT_SECRET'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }

    # Create the flow using the client config
    flow = InstalledAppFlow.from_client_config(client_config, SCOPE)
    
    # Get authorization URL with account selection forced
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='select_account',  # This forces account selection
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Manual copy/paste flow
    )
    
    print("=" * 70)
    print("Google Ads API Authorization")
    print("=" * 70)
    print()
    print("1. Open this URL in a browser where you're NOT logged in,")
    print("   or use an incognito/private window:")
    print()
    print(auth_url)
    print()
    print("2. Choose or sign in with the Google account that has")
    print("   access to your Google Ads account")
    print()
    print("3. After authorizing, you'll see a code.")
    print("   Copy and paste that code here:")
    print()
    
    code = input("Enter the authorization code: ").strip()
    
    # Exchange code for token
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Print the refresh token
    print()
    print("=" * 50)
    print("SUCCESS! Your refresh token is:")
    print("=" * 50)
    print(credentials.refresh_token)
    print("=" * 50)
    print()
    print("Add this to your .env file as:")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}")
    print()

if __name__ == '__main__':
    main()