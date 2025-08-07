#!/usr/bin/env python3
"""
Google OAuth Client Setup Guide
This script provides instructions for setting up a proper Google OAuth Client ID
"""

import os
import sys

def print_setup_instructions():
    """Print detailed instructions for setting up Google OAuth Client"""
    
    print("=" * 80)
    print("GOOGLE OAUTH CLIENT SETUP INSTRUCTIONS")
    print("=" * 80)
    print()
    
    print("🔍 ISSUE DETECTED:")
    print("Your current Google Client ID appears to be invalid or malformed.")
    print()
    
    print("📋 STEPS TO GET A VALID GOOGLE OAUTH CLIENT ID:")
    print()
    
    print("1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    
    print("2. Select or create a project:")
    print("   - Click on the project dropdown at the top")
    print("   - Select an existing project or create a new one")
    print()
    
    print("3. Enable the Google Ads API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Ads API'")
    print("   - Click on it and press 'Enable'")
    print()
    
    print("4. Create OAuth 2.0 Credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("   - Choose 'Desktop application' as the application type")
    print("   - Give it a name (e.g., 'Lane Google Ads Client')")
    print("   - Click 'Create'")
    print()
    
    print("5. Download the credentials:")
    print("   - After creation, click the download button (⬇️)")
    print("   - Save the JSON file as 'client_secret.json' in your project root")
    print()
    
    print("6. Extract the Client ID and Secret:")
    print("   - Open the downloaded JSON file")
    print("   - Find 'client_id' and 'client_secret' values")
    print("   - The client_id should look like:")
    print("     123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com")
    print()
    
    print("7. Update your environment variables:")
    print("   - Replace GOOGLE_ADS_CLIENT_ID with the new client_id")
    print("   - Replace GOOGLE_ADS_CLIENT_SECRET with the new client_secret")
    print()
    
    print("8. Generate a new refresh token:")
    print("   - Run: python generate_refresh_token.py")
    print("   - Follow the authorization flow")
    print("   - Update GOOGLE_ADS_REFRESH_TOKEN with the new token")
    print()
    
    print("🔧 CURRENT ENVIRONMENT CHECK:")
    print("-" * 40)
    
    # Check current environment variables
    client_id = os.getenv('GOOGLE_ADS_CLIENT_ID', 'NOT SET')
    client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET', 'NOT SET')
    refresh_token = os.getenv('GOOGLE_ADS_REFRESH_TOKEN', 'NOT SET')
    developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', 'NOT SET')
    
    print(f"GOOGLE_ADS_CLIENT_ID: {client_id[:20]}..." if len(client_id) > 20 else f"GOOGLE_ADS_CLIENT_ID: {client_id}")
    print(f"GOOGLE_ADS_CLIENT_SECRET: {'SET' if client_secret != 'NOT SET' else 'NOT SET'}")
    print(f"GOOGLE_ADS_REFRESH_TOKEN: {'SET' if refresh_token != 'NOT SET' else 'NOT SET'}")
    print(f"GOOGLE_ADS_DEVELOPER_TOKEN: {'SET' if developer_token != 'NOT SET' else 'NOT SET'}")
    print()
    
    # Validate client ID format
    if client_id != 'NOT SET':
        if '.apps.googleusercontent.com' in client_id and '-' in client_id:
            parts = client_id.split('-')
            if len(parts) >= 2 and parts[0].isdigit() and len(parts[0]) == 12:
                print("✅ Client ID format appears valid")
            else:
                print("❌ Client ID format appears invalid")
        else:
            print("❌ Client ID format is definitely invalid")
    
    print()
    print("📚 ADDITIONAL RESOURCES:")
    print("- Google Ads API Documentation: https://developers.google.com/google-ads/api/docs/first-call/overview")
    print("- OAuth 2.0 Setup: https://developers.google.com/google-ads/api/docs/oauth/cloud-project")
    print()

def check_client_secret_file():
    """Check if client_secret.json exists and is valid"""
    
    if os.path.exists('client_secret.json'):
        print("✅ Found client_secret.json file")
        try:
            import json
            with open('client_secret.json', 'r') as f:
                data = json.load(f)
                
            if 'installed' in data:
                client_info = data['installed']
                client_id = client_info.get('client_id', '')
                client_secret = client_info.get('client_secret', '')
                
                print(f"   Client ID: {client_id}")
                print(f"   Client Secret: {'*' * len(client_secret) if client_secret else 'NOT FOUND'}")
                
                print("\n📝 To use these credentials, update your .env file:")
                print(f"GOOGLE_ADS_CLIENT_ID={client_id}")
                print(f"GOOGLE_ADS_CLIENT_SECRET={client_secret}")
                
            else:
                print("❌ Invalid client_secret.json format")
                
        except Exception as e:
            print(f"❌ Error reading client_secret.json: {e}")
    else:
        print("❌ client_secret.json not found")
        print("   Download it from Google Cloud Console after creating OAuth credentials")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print_setup_instructions()
    print()
    check_client_secret_file()
