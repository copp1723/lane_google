#!/usr/bin/env python3
"""
Test Google Ads API Credentials
This script tests if your Google Ads API credentials are working
"""

import os
import sys
from dotenv import load_dotenv

def test_credentials():
    """Test Google Ads API credentials"""
    
    print("=" * 60)
    print("TESTING GOOGLE ADS API CREDENTIALS")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    client_id = os.getenv('GOOGLE_ADS_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_ADS_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
    developer_token = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    login_customer_id = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
    
    print("\n1. Environment Variables Check:")
    print("-" * 30)
    print(f"✅ GOOGLE_ADS_CLIENT_ID: {'SET' if client_id else '❌ NOT SET'}")
    print(f"✅ GOOGLE_ADS_CLIENT_SECRET: {'SET' if client_secret else '❌ NOT SET'}")
    print(f"✅ GOOGLE_ADS_REFRESH_TOKEN: {'SET' if refresh_token else '❌ NOT SET'}")
    print(f"✅ GOOGLE_ADS_DEVELOPER_TOKEN: {'SET' if developer_token else '❌ NOT SET'}")
    print(f"✅ GOOGLE_ADS_LOGIN_CUSTOMER_ID: {'SET' if login_customer_id else '❌ NOT SET'}")
    
    if not all([client_id, client_secret, refresh_token, developer_token]):
        print("\n❌ Missing required environment variables!")
        return False
    
    print(f"\nClient ID: {client_id}")
    
    # Test Google Ads client initialization
    print("\n2. Google Ads Client Initialization:")
    print("-" * 40)
    
    try:
        from google.ads.googleads.client import GoogleAdsClient
        from google.ads.googleads.errors import GoogleAdsException
        
        # Create configuration with REST transport (fallback for gRPC issues)
        config = {
            "use_proto_plus": True,
            "developer_token": developer_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "transport": "rest"  # Use REST instead of gRPC
        }

        if login_customer_id:
            config["login_customer_id"] = login_customer_id
        
        print("Initializing Google Ads client...")
        client = GoogleAdsClient.load_from_dict(config)
        print("✅ Google Ads client initialized successfully!")
        
        # Test API connection
        print("\n3. API Connection Test:")
        print("-" * 25)
        
        try:
            # Try different API versions and methods
            print("Testing with different API approaches...")

            # Method 1: Try with explicit version
            try:
                customer_service = client.get_service("CustomerService", version="v16")
                print("✅ Customer service (v16) obtained")
                accessible_customers = customer_service.list_accessible_customers()
                print("✅ API call with v16 successful!")
            except Exception as e1:
                print(f"❌ v16 failed: {e1}")

                # Method 2: Try with default version
                try:
                    customer_service = client.get_service("CustomerService")
                    print("✅ Customer service (default) obtained")
                    accessible_customers = customer_service.list_accessible_customers()
                    print("✅ API call with default version successful!")
                except Exception as e2:
                    print(f"❌ Default version failed: {e2}")

                    # Method 3: Try a simple query instead
                    try:
                        print("Trying GoogleAdsService query instead...")
                        ga_service = client.get_service("GoogleAdsService")

                        # Simple query to test connection
                        if login_customer_id:
                            query = "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"
                            response = ga_service.search(customer_id=login_customer_id, query=query)

                            for row in response:
                                print(f"✅ Query successful! Customer: {row.customer.descriptive_name} (ID: {row.customer.id})")
                                return True
                        else:
                            print("❌ No login_customer_id set, cannot test query")
                            return False

                    except Exception as e3:
                        print(f"❌ Query method failed: {e3}")
                        raise e3

            # If we get here, one of the methods worked
            if 'accessible_customers' in locals():
                if accessible_customers.resource_names:
                    print(f"✅ Found {len(accessible_customers.resource_names)} accessible customers:")
                    for i, customer_resource in enumerate(accessible_customers.resource_names[:5]):  # Show first 5
                        customer_id = customer_resource.split('/')[-1]
                        print(f"   {i+1}. Customer ID: {customer_id}")

                    if len(accessible_customers.resource_names) > 5:
                        print(f"   ... and {len(accessible_customers.resource_names) - 5} more")

                    return True
                else:
                    print("⚠️  API call successful but no accessible customers found")
                    print("   This might mean:")
                    print("   - Your Google account doesn't have access to any Google Ads accounts")
                    print("   - The developer token is not approved")
                    print("   - The refresh token was generated for a different account")
                    return False
                
        except GoogleAdsException as ex:
            print(f"❌ Google Ads API error: {ex}")
            print(f"   Error details: {ex.error}")
            return False
            
    except ImportError:
        print("❌ Google Ads Python client not installed!")
        print("   Run: pip install google-ads")
        return False
    except Exception as e:
        print(f"❌ Error initializing client: {str(e)}")
        
        # Check if it's an OAuth error
        if "invalid_client" in str(e):
            print("\n🔍 DIAGNOSIS: Invalid Client Error")
            print("This error means Google doesn't recognize your client_id.")
            print("Possible causes:")
            print("1. The client_id is incorrect or typo")
            print("2. The OAuth client was deleted from Google Cloud Console")
            print("3. The client_id is from a different Google Cloud project")
            print("4. The OAuth client is not configured for 'Desktop application'")
            print("\n💡 SOLUTION:")
            print("1. Go to Google Cloud Console > APIs & Services > Credentials")
            print("2. Check if your OAuth client exists")
            print("3. If not, create a new one (Desktop application type)")
            print("4. Update your GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET")
            print("5. Generate a new refresh token with the new credentials")
            
        elif "invalid_grant" in str(e):
            print("\n🔍 DIAGNOSIS: Invalid Grant Error")
            print("This error means your refresh token is invalid or expired.")
            print("💡 SOLUTION:")
            print("1. Generate a new refresh token using: python generate_refresh_token.py")
            print("2. Make sure to use the same Google account that has Google Ads access")
            
        return False

if __name__ == "__main__":
    success = test_credentials()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your Google Ads API credentials are working correctly.")
    else:
        print("\n❌ TESTS FAILED!")
        print("Please fix the issues above and try again.")
        
    print("\n" + "=" * 60)
