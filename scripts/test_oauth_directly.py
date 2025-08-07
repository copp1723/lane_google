#!/usr/bin/env python3
"""
Test OAuth credentials directly without Google Ads library
This helps isolate if the issue is with OAuth or with the Google Ads library
"""

import os
import requests
from dotenv import load_dotenv

def test_oauth_token():
    """Test OAuth token by making a direct API call"""
    
    print("=" * 60)
    print("TESTING OAUTH TOKEN DIRECTLY")
    print("=" * 60)
    
    load_dotenv()
    
    client_id = os.getenv('GOOGLE_ADS_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Missing OAuth credentials")
        return False
    
    print("\n1. Testing OAuth Token Refresh:")
    print("-" * 35)
    
    # Try to refresh the access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    try:
        print("Requesting new access token...")
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            print("✅ Successfully obtained access token!")
            print(f"   Token type: {token_info.get('token_type', 'Unknown')}")
            print(f"   Expires in: {token_info.get('expires_in', 'Unknown')} seconds")
            print(f"   Scope: {token_info.get('scope', 'Unknown')}")
            
            # Test the access token with Google Ads API
            print("\n2. Testing Access Token with Google Ads API:")
            print("-" * 45)
            
            return test_google_ads_api(access_token)
            
        else:
            print(f"❌ Failed to refresh token: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 400:
                error_info = response.json()
                error = error_info.get('error', 'unknown')
                
                if error == 'invalid_client':
                    print("\n🔍 DIAGNOSIS: Invalid Client")
                    print("Your client_id or client_secret is incorrect.")
                    print("💡 SOLUTION: Check your Google Cloud Console credentials")
                    
                elif error == 'invalid_grant':
                    print("\n🔍 DIAGNOSIS: Invalid Grant")
                    print("Your refresh_token is invalid or expired.")
                    print("💡 SOLUTION: Generate a new refresh token")
                    
            return False
            
    except Exception as e:
        print(f"❌ Error testing OAuth: {e}")
        return False

def test_google_ads_api(access_token):
    """Test Google Ads API with the access token"""
    
    developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
    
    if not developer_token:
        print("❌ Missing GOOGLE_ADS_DEVELOPER_TOKEN")
        return False
    
    # Try to make a simple API call using REST
    headers = {
        'Authorization': f'Bearer {access_token}',
        'developer-token': developer_token,
        'Content-Type': 'application/json'
    }
    
    if login_customer_id:
        headers['login-customer-id'] = login_customer_id
    
    # Test with accessible customers first (simpler endpoint)
    api_url = "https://googleads.googleapis.com/v14/customers:listAccessibleCustomers"

    # No query data needed for this endpoint
    query_data = {}
    
    try:
        print("Making REST API call to Google Ads...")
        response = requests.post(api_url, json=query_data, headers=headers)

        if response.status_code == 200:
            print("✅ Google Ads API call successful!")
            result = response.json()

            if 'resourceNames' in result and result['resourceNames']:
                print(f"   Found {len(result['resourceNames'])} accessible customers:")
                for i, resource_name in enumerate(result['resourceNames'][:3]):
                    customer_id = resource_name.split('/')[-1]
                    print(f"   {i+1}. Customer ID: {customer_id}")
            else:
                print("   No accessible customers found (but API call worked)")

            return True
            
        else:
            print(f"❌ Google Ads API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 401:
                print("\n🔍 DIAGNOSIS: Authentication Error")
                print("The access token or developer token is invalid.")
                
            elif response.status_code == 403:
                print("\n🔍 DIAGNOSIS: Permission Error")
                print("The account doesn't have permission to access this customer.")
                
            elif response.status_code == 400:
                print("\n🔍 DIAGNOSIS: Bad Request")
                print("The request format or parameters are incorrect.")
                
            return False
            
    except Exception as e:
        print(f"❌ Error calling Google Ads API: {e}")
        return False

if __name__ == "__main__":
    success = test_oauth_token()
    
    if success:
        print("\n🎉 OAUTH AND API TESTS PASSED!")
        print("Your credentials are working. The issue might be with the Python library.")
    else:
        print("\n❌ OAUTH OR API TESTS FAILED!")
        print("Please fix the credential issues first.")
        
    print("\n" + "=" * 60)
