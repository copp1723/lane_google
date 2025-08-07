#!/usr/bin/env python3
"""
Google Ads API Refresh Token Generator
Run this script to generate a refresh token for the Google Ads API
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
    
    # Run the OAuth flow
    print("Opening browser for Google Ads API authorization...")
    print("Please log in with the Google account that has access to Google Ads.")
    print()
    
    # Force account selection by adding prompt parameter
    flow.authorization_url_params = {
        'prompt': 'select_account',  # Forces account selection
        'access_type': 'offline',     # Ensures we get a refresh token
        'include_granted_scopes': 'true'
    }
    
    credentials = flow.run_local_server(
        port=0,
        authorization_prompt_message='Please visit this URL to authorize this application: {url}',
        success_message='The authentication flow has completed. You may close this window.',
        open_browser=True
    )
    
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