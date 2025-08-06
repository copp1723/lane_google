#!/usr/bin/env python3
"""
Test Google Ads API Integration
Demonstrates proper usage of the Google Ads API with Lane MCP
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.services.real_google_ads import RealGoogleAdsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_google_ads_connection():
    """Test basic Google Ads API connection"""
    print("\n" + "="*60)
    print("Testing Google Ads API Connection")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize service
    service = RealGoogleAdsService()
    
    if not service.client:
        print("\n❌ Failed to initialize Google Ads client")
        print("\nPlease ensure you have:")
        print("1. Valid OAuth2 credentials in your .env file")
        print("2. Run: python scripts/generate_google_ads_credentials.py")
        print("3. Google Ads Python client installed: pip install google-ads")
        return False
    
    print("\n✅ Google Ads client initialized successfully!")
    
    # Test: Get accessible customers
    try:
        print("\n📋 Fetching accessible Google Ads accounts...")
        customers = service.get_accessible_customers()
        
        if not customers:
            print("\n⚠️  No accessible Google Ads accounts found.")
            print("Make sure your refresh token has access to Google Ads accounts.")
            return False
            
        print(f"\n✅ Found {len(customers)} accessible account(s):")
        for customer in customers:
            print(f"\n   Customer ID: {customer['id']}")
            print(f"   Name: {customer['name']}")
            print(f"   Currency: {customer['currency_code']}")
            print(f"   Time Zone: {customer['time_zone']}")
            print(f"   Is Test Account: {customer['is_test_account']}")
            print(f"   Is Manager Account: {customer['is_manager_account']}")
            
        return customers
        
    except Exception as e:
        print(f"\n❌ Error accessing Google Ads accounts: {str(e)}")
        return False

def test_campaign_operations(customer_id: str):
    """Test campaign operations"""
    print("\n" + "="*60)
    print(f"Testing Campaign Operations for Customer: {customer_id}")
    print("="*60)
    
    service = RealGoogleAdsService()
    
    # Test 1: List existing campaigns
    try:
        print("\n📋 Fetching existing campaigns...")
        campaigns = service.get_campaigns(customer_id)
        
        if campaigns:
            print(f"\n✅ Found {len(campaigns)} campaign(s):")
            for campaign in campaigns[:5]:  # Show first 5
                print(f"\n   Campaign: {campaign['name']}")
                print(f"   ID: {campaign['id']}")
                print(f"   Status: {campaign['status']}")
                print(f"   Type: {campaign['channel_type']}")
                print(f"   Budget: ${campaign['budget_amount']:.2f}")
                print(f"   Performance: {campaign['performance']['impressions']} impressions, "
                      f"{campaign['performance']['clicks']} clicks")
        else:
            print("\n   No campaigns found.")
            
    except Exception as e:
        print(f"\n❌ Error fetching campaigns: {str(e)}")
    
    # Test 2: Create a test campaign (only if in test account)
    try:
        print("\n📋 Creating a test campaign...")
        print("⚠️  Note: This will only work in a test account!")
        
        campaign_data = {
            'name': f'Lane MCP Test Campaign - {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'channel_type': 'SEARCH',
            'budget_amount': 10.0,  # $10 daily budget
            'bidding_strategy': 'MAXIMIZE_CLICKS',
            'start_date': datetime.now().strftime('%Y%m%d'),
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y%m%d')
        }
        
        result = service.create_campaign(customer_id, campaign_data)
        print(f"\n✅ Campaign created successfully!")
        print(f"   Campaign ID: {result['campaign_id']}")
        print(f"   Status: {result['status']}")
        
    except Exception as e:
        print(f"\n⚠️  Could not create campaign: {str(e)}")
        print("   This is normal if you're not using a test account.")
    
    # Test 3: Get performance metrics
    try:
        print("\n📋 Fetching performance metrics (last 7 days)...")
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        metrics = service.get_performance_metrics(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        total = metrics['total_metrics']
        print(f"\n✅ Performance Summary ({start_date} to {end_date}):")
        print(f"   Impressions: {total['impressions']:,}")
        print(f"   Clicks: {total['clicks']:,}")
        print(f"   Cost: ${total['cost']:.2f}")
        print(f"   CTR: {total['ctr']:.2f}%")
        print(f"   Avg CPC: ${total['cpc']:.2f}")
        print(f"   Conversions: {total['conversions']:.2f}")
        
    except Exception as e:
        print(f"\n❌ Error fetching metrics: {str(e)}")

def main():
    """Main test function"""
    print("\n🚀 Lane MCP - Google Ads API Integration Test")
    print("   This script tests your Google Ads API setup")
    
    # Test connection and get customers
    customers = test_google_ads_connection()
    
    if not customers:
        print("\n❌ Testing aborted. Please fix the connection issues first.")
        return
    
    # If we have customers, test operations on the first one
    if customers and isinstance(customers, list) and len(customers) > 0:
        # Prefer test accounts for testing
        test_account = next((c for c in customers if c['is_test_account']), None)
        
        if test_account:
            print(f"\n✅ Using test account: {test_account['name']} ({test_account['id']})")
            customer_id = test_account['id']
        else:
            # Use first account
            customer_id = customers[0]['id']
            print(f"\n⚠️  No test account found. Using: {customers[0]['name']} ({customer_id})")
            print("   Note: Campaign creation will be skipped for non-test accounts.")
        
        # Test campaign operations
        test_campaign_operations(customer_id)
    
    print("\n" + "="*60)
    print("✅ Testing complete!")
    print("="*60)

if __name__ == "__main__":
    main()