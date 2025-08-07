#!/usr/bin/env python3
"""
Test script to verify Google Ads configuration fixes
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Test if required environment variables are set"""
    logger.info("=== Testing Environment Variables ===")
    
    required_vars = [
        'GOOGLE_ADS_DEVELOPER_TOKEN',
        'GOOGLE_ADS_CLIENT_ID',
        'GOOGLE_ADS_CLIENT_SECRET',
        'GOOGLE_ADS_REFRESH_TOKEN'
    ]
    
    optional_vars = [
        'GOOGLE_ADS_LOGIN_CUSTOMER_ID',
        'GOOGLE_ADS_USE_PROTO_PLUS',
        'GOOGLE_ADS_USE_MOCK'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {'*' * min(10, len(value))}...")
        else:
            logger.error(f"❌ {var}: Not set")
            all_set = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"ℹ️  {var}: {value}")
        else:
            logger.info(f"ℹ️  {var}: Not set (using default)")
    
    return all_set

def test_yaml_config():
    """Test google-ads.yaml configuration"""
    logger.info("\n=== Testing YAML Configuration ===")
    
    yaml_path = Path('google-ads.yaml')
    if not yaml_path.exists():
        logger.error("❌ google-ads.yaml file not found")
        return False
    
    try:
        import yaml
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        
        logger.info("✅ YAML file loads successfully")
        
        # Check use_proto_plus setting
        use_proto_plus = config.get('use_proto_plus')
        if use_proto_plus is True:
            logger.info("✅ use_proto_plus is correctly set to True")
        elif use_proto_plus is False:
            logger.info("✅ use_proto_plus is correctly set to False")
        else:
            logger.warning(f"⚠️  use_proto_plus has unexpected value: {use_proto_plus}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading YAML: {e}")
        return False

def test_service_imports():
    """Test if services can be imported without errors"""
    logger.info("\n=== Testing Service Imports ===")
    
    try:
        from src.services.google_ads import GoogleAdsService
        logger.info("✅ GoogleAdsService imported successfully")
        
        # Test mock service
        mock_service = GoogleAdsService()
        test_result = mock_service.test_connection()
        logger.info(f"✅ Mock service test_connection: {test_result['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error importing GoogleAdsService: {e}")
        return False
    
    try:
        from src.services.real_google_ads import RealGoogleAdsService
        logger.info("✅ RealGoogleAdsService imported successfully")
        
        # Test real service (without initializing client)
        real_service = RealGoogleAdsService()
        test_result = real_service.test_connection()
        logger.info(f"✅ Real service test_connection: {test_result['status']}")
        
    except Exception as e:
        logger.error(f"❌ Error importing RealGoogleAdsService: {e}")
        return False
    
    try:
        from src.services.google_ads_service_selector import get_google_ads_service
        logger.info("✅ Service selector imported successfully")
        
        service = get_google_ads_service()
        logger.info(f"✅ Service selector returned: {type(service).__name__}")
        
    except Exception as e:
        logger.error(f"❌ Error with service selector: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    logger.info("Google Ads Configuration Fix Test")
    logger.info("=" * 50)
    
    env_ok = test_environment_variables()
    yaml_ok = test_yaml_config()
    imports_ok = test_service_imports()
    
    logger.info("\n=== Summary ===")
    if env_ok and yaml_ok and imports_ok:
        logger.info("🎉 All tests passed! Google Ads configuration should work.")
    else:
        logger.error("❌ Some tests failed. Check the issues above.")
        
        if not env_ok:
            logger.info("💡 To fix environment variables:")
            logger.info("   1. Create a .env file in the project root")
            logger.info("   2. Add your Google Ads API credentials")
            logger.info("   3. Run: python scripts/generate_google_ads_credentials.py (if it exists)")

if __name__ == "__main__":
    main()
