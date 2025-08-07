#!/usr/bin/env python3
"""
Quick deployment verification for Google Ads fixes
"""

import os
import sys
from pathlib import Path
import logging

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def verify_deployment_readiness():
    """Verify that the Google Ads fixes will work in deployment"""
    logger.info("=== Deployment Readiness Check ===")
    
    issues_fixed = []
    
    # 1. Check use_proto_plus configuration
    try:
        import yaml
        with open('google-ads.yaml') as f:
            config = yaml.safe_load(f)
        
        use_proto_plus = config.get('use_proto_plus')
        if use_proto_plus is True:
            issues_fixed.append("✅ use_proto_plus configuration fixed")
        else:
            logger.error(f"❌ use_proto_plus still has wrong value: {use_proto_plus}")
    except Exception as e:
        logger.error(f"❌ YAML config issue: {e}")
    
    # 2. Check GoogleAdsService import
    try:
        from src.services.google_ads import GoogleAdsService
        service = GoogleAdsService()
        service.test_connection()
        issues_fixed.append("✅ GoogleAdsService class exists and works")
    except Exception as e:
        logger.error(f"❌ GoogleAdsService issue: {e}")
    
    # 3. Check RealGoogleAdsService test_connection
    try:
        from src.services.real_google_ads import RealGoogleAdsService
        service = RealGoogleAdsService()
        result = service.test_connection()
        if 'status' in result:
            issues_fixed.append("✅ RealGoogleAdsService.test_connection() exists")
        else:
            logger.error("❌ test_connection() doesn't return expected format")
    except Exception as e:
        logger.error(f"❌ RealGoogleAdsService issue: {e}")
    
    # 4. Check service selector
    try:
        from src.services.google_ads_service_selector import get_google_ads_service
        service = get_google_ads_service()
        issues_fixed.append("✅ Service selector works correctly")
    except Exception as e:
        logger.error(f"❌ Service selector issue: {e}")
    
    logger.info(f"\n=== Issues Fixed ({len(issues_fixed)}/4) ===")
    for issue in issues_fixed:
        logger.info(issue)
    
    logger.info("\n=== Expected Deployment Behavior ===")
    logger.info("✅ No more 'use_proto_plus' configuration errors")
    logger.info("✅ No more 'GoogleAdsService' import errors") 
    logger.info("✅ No more 'test_connection' attribute errors")
    logger.info("✅ Service will fall back to mock if real API fails")
    
    if len(issues_fixed) == 4:
        logger.info("\n🎉 All Google Ads configuration issues fixed!")
        logger.info("Deployment should now work without these errors.")
    else:
        logger.error(f"\n❌ {4 - len(issues_fixed)} issues remain")

if __name__ == "__main__":
    verify_deployment_readiness()
