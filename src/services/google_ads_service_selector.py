"""
Google Ads Service Selector
Intelligently selects between real and mock Google Ads service based on configuration
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_service_instance = None

def get_google_ads_service():
    """
    Get the appropriate Google Ads service instance.
    Returns real service if credentials are available, otherwise returns mock service.
    """
    global _service_instance
    
    if _service_instance is not None:
        return _service_instance
    
    # Check if we have all required credentials
    required_credentials = [
        'GOOGLE_ADS_DEVELOPER_TOKEN',
        'GOOGLE_ADS_CLIENT_ID',
        'GOOGLE_ADS_CLIENT_SECRET',
        'GOOGLE_ADS_REFRESH_TOKEN'
    ]
    
    has_all_credentials = all(
        os.getenv(var) and os.getenv(var) != f"your-{var.lower().replace('google_ads_', '').replace('_', '-')}"
        for var in required_credentials
    )
    
    # Check if we should force mock mode
    use_mock = os.getenv('GOOGLE_ADS_USE_MOCK', 'false').lower() == 'true'
    
    if has_all_credentials and not use_mock:
        try:
            # Try to import and initialize real service
            from .real_google_ads import RealGoogleAdsService
            
            logger.info("Attempting to initialize real Google Ads service...")
            service = RealGoogleAdsService()
            
            # Verify the client was initialized successfully
            if service.client:
                logger.info("✅ Using REAL Google Ads API service")
                _service_instance = service
                return _service_instance
            else:
                logger.warning("Real Google Ads client initialization failed, falling back to mock service")
                
        except ImportError as e:
            logger.warning(f"Could not import real Google Ads service: {e}")
            logger.info("Make sure to install: pip install google-ads")
        except Exception as e:
            logger.error(f"Error initializing real Google Ads service: {e}")
            logger.info("Falling back to mock service")
    else:
        if not has_all_credentials:
            missing = [var for var in required_credentials if not os.getenv(var) or 
                      os.getenv(var) == f"your-{var.lower().replace('google_ads_', '').replace('_', '-')}"]
            logger.info(f"Missing or invalid Google Ads credentials: {missing}")
            logger.info("To use real Google Ads API:")
            logger.info("1. Run: python scripts/generate_google_ads_credentials.py")
            logger.info("2. Add credentials to your .env file")
            logger.info("3. Get a developer token from https://ads.google.com/aw/apicenter")
    
    # Fall back to mock service
    from .google_ads import GoogleAdsService
    logger.info("🔄 Using MOCK Google Ads service")
    logger.info("Set GOOGLE_ADS_USE_MOCK=false to attempt real API connection")
    _service_instance = GoogleAdsService()
    return _service_instance

def reset_service():
    """Reset the service instance (useful for testing)"""
    global _service_instance
    _service_instance = None

def is_using_real_service() -> bool:
    """Check if we're using the real Google Ads service"""
    service = get_google_ads_service()
    return hasattr(service, '__class__') and 'Real' in service.__class__.__name__

def get_service_status() -> dict:
    """Get detailed status of the Google Ads service"""
    service = get_google_ads_service()
    is_real = is_using_real_service()
    
    status = {
        'service_type': 'real' if is_real else 'mock',
        'credentials_present': {
            'developer_token': bool(os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')),
            'client_id': bool(os.getenv('GOOGLE_ADS_CLIENT_ID')),
            'client_secret': bool(os.getenv('GOOGLE_ADS_CLIENT_SECRET')),
            'refresh_token': bool(os.getenv('GOOGLE_ADS_REFRESH_TOKEN'))
        },
        'force_mock': os.getenv('GOOGLE_ADS_USE_MOCK', 'false').lower() == 'true'
    }
    
    if is_real:
        status['client_initialized'] = hasattr(service, 'client') and service.client is not None
    
    return status