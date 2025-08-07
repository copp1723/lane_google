#!/usr/bin/env python3
"""
Google Ads API Credentials Generator
Helps generate the OAuth2 refresh token for Google Ads API access
"""

import os
import sys
import json
import webbrowser
from urllib.parse import urlencode
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configuration
CLIENT_ID = None  # Will be set from command line or user input
REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
SCOPES = ["https://www.googleapis.com/auth/adwords"]

print("=" * 60)
print("Google Ads API OAuth2 Setup")
print("=" * 60)

# Check if client ID and secret are provided via command line
if len(sys.argv) > 2:
    CLIENT_ID = sys.argv[1]
    CLIENT_SECRET = sys.argv[2]
else:
    print("\n⚠️  IMPORTANT: You need OAuth2 credentials from Google Cloud Console")
    print("\nSteps to get OAuth2 credentials:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select your project (or create a new one)")
    print("3. Enable the Google Ads API:")
    print("   - Go to: APIs & Services → Library")
    print("   - Search for 'Google Ads API'")
    print("   - Click on it and press 'Enable'")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Go to: APIs & Services → Credentials")
    print("   - Click '+ CREATE CREDENTIALS' → 'OAuth client ID'")
    print("   - Application type: 'Web application'")
    print("   - Name: 'Lane MCP Google Ads Integration' (or any name)")
    print(f"   - Authorized redirect URIs: Add 'http://localhost:{REDIRECT_PORT}'")
    print("   - Click 'CREATE'")
    print("5. Copy the Client ID and Client Secret\n")
    
    if not CLIENT_ID:
        print("The Client ID should look like: XXXXXXXXXX.apps.googleusercontent.com")
        CLIENT_ID = input("Enter your OAuth2 Client ID: ").strip()
    
    if not CLIENT_ID:
        print("❌ Client ID is required!")
        sys.exit(1)

# Check if client secret is provided
if 'CLIENT_SECRET' not in locals():
    print("\n⚠️  IMPORTANT: You need to get your Client Secret from Google Cloud Console")
    print("\nSteps to get Client Secret:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select your project (or create a new one)")
    print("3. Go to: APIs & Services → Credentials")
    print("4. Create OAuth 2.0 Client ID (Web application type)")
    print(f"5. Add redirect URI: http://localhost:{REDIRECT_PORT}")
    print("6. Download the credentials JSON and find 'client_secret'\n")
    
    CLIENT_SECRET = input("Enter your Client Secret: ").strip()

if not CLIENT_SECRET:
    print("❌ Client Secret is required!")
    sys.exit(1)

# Global variable to store the authorization code
auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback"""
    def do_GET(self):
        global auth_code
        
        # Parse the authorization code from the callback
        if "?code=" in self.path:
            auth_code = self.path.split("?code=")[1].split("&")[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #4CAF50;">✅ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>window.setTimeout(function(){window.close();}, 3000);</script>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = """
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #f44336;">❌ Authorization Failed!</h1>
                <p>No authorization code received. Please try again.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

def start_callback_server():
    """Start a local server to handle the OAuth callback"""
    server = HTTPServer(('localhost', REDIRECT_PORT), CallbackHandler)
    server.handle_request()

# Step 1: Generate authorization URL
auth_params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': ' '.join(SCOPES),
    'access_type': 'offline',
    'prompt': 'consent'
}

auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

print(f"\n📋 Starting OAuth2 flow...")
print(f"   Client ID: {CLIENT_ID[:30]}..." if len(CLIENT_ID) > 30 else f"   Client ID: {CLIENT_ID}")
print(f"   Redirect URI: {REDIRECT_URI}")

# Start the callback server in a separate thread
print(f"\n🌐 Starting local server on port {REDIRECT_PORT}...")
server_thread = threading.Thread(target=start_callback_server)
server_thread.daemon = True
server_thread.start()

# Open the authorization URL in the browser
print("\n🔗 Opening authorization URL in your browser...")
print("   If the browser doesn't open automatically, visit:")
print(f"   {auth_url}\n")

webbrowser.open(auth_url)

# Wait for the callback
print("⏳ Waiting for authorization...")
server_thread.join(timeout=300)  # 5 minute timeout

if not auth_code:
    print("\n❌ No authorization code received. Please try again.")
    sys.exit(1)

print(f"\n✅ Authorization code received!")

# Step 2: Exchange authorization code for tokens
print("\n🔄 Exchanging code for tokens...")

token_params = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': auth_code,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code'
}

try:
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data=token_params
    )
    response.raise_for_status()
    
    tokens = response.json()
    refresh_token = tokens.get('refresh_token')
    
    if not refresh_token:
        print("\n❌ No refresh token received. Make sure you:")
        print("   1. Are using the correct scopes")
        print("   2. Set 'access_type' to 'offline'")
        print("   3. Include 'prompt=consent' in the auth URL")
        sys.exit(1)
    
    print("\n🎉 SUCCESS! Here are your credentials:")
    print("=" * 60)
    print(f"GOOGLE_ADS_CLIENT_SECRET={CLIENT_SECRET}")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
    print("=" * 60)
    
    # Save to a file for reference
    credentials_file = "google_ads_credentials.txt"
    with open(credentials_file, 'w') as f:
        f.write("# Google Ads API Credentials\n")
        f.write("# Add these to your .env file or Render environment variables\n\n")
        f.write("# Get your developer token from: https://ads.google.com/aw/apicenter\n")
        f.write("GOOGLE_ADS_DEVELOPER_TOKEN=<your-developer-token>\n\n")
        f.write("# OAuth2 credentials from Google Cloud Console\n")
        f.write(f"GOOGLE_ADS_CLIENT_ID={CLIENT_ID}\n")
        f.write(f"GOOGLE_ADS_CLIENT_SECRET={CLIENT_SECRET}\n")
        f.write(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n\n")
        f.write("# Optional: Your Google Ads Manager Account Customer ID (without hyphens)\n")
        f.write("# GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890\n")
    
    print(f"\n📄 Credentials also saved to: {credentials_file}")
    print("\n⚠️  IMPORTANT:")
    print("   1. Add these to your .env file")
    print("   2. Never commit credentials to version control")
    print("   3. Set these as environment variables in Render Dashboard")
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ Error exchanging code for tokens: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
    sys.exit(1)

print("\n✅ Setup complete! You can now use the Google Ads API.")