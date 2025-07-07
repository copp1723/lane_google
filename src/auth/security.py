"""
Security Configuration Utilities
Centralized security settings and validation
"""

import os
import secrets
from typing import List, Optional


class SecurityConfig:
    """Security configuration management"""

    @staticmethod
    def get_secret_key() -> str:
        """Get or generate secret key"""
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            # Generate a secure random key for development
            secret_key = secrets.token_urlsafe(32)
        return secret_key

    @staticmethod
    def get_jwt_secret() -> str:
        """Get JWT secret key"""
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret:
            # Use the same secret as Flask for development
            jwt_secret = SecurityConfig.get_secret_key()
        return jwt_secret

    @staticmethod
    def get_allowed_origins() -> List[str]:
        """Get allowed CORS origins"""
        origins_str = os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
        )
        return [origin.strip() for origin in origins_str.split(",")]

    @staticmethod
    def get_rate_limit_config() -> dict:
        """Get rate limiting configuration"""
        return {
            "default": os.getenv("RATE_LIMIT_DEFAULT", "100 per hour"),
            "auth": os.getenv("RATE_LIMIT_AUTH", "10 per minute"),
            "api": os.getenv("RATE_LIMIT_API", "1000 per hour"),
        }

    @staticmethod
    def is_https_required() -> bool:
        """Check if HTTPS is required"""
        return os.getenv("FORCE_HTTPS", "false").lower() == "true"

    @staticmethod
    def get_session_config() -> dict:
        """Get session configuration"""
        return {
            "lifetime_hours": int(os.getenv("SESSION_LIFETIME_HOURS", "24")),
            "secure": SecurityConfig.is_https_required(),
            "httponly": True,
            "samesite": "Lax",
        }


class APIKeyManager:
    """API key management utilities"""

    @staticmethod
    def get_openrouter_key() -> Optional[str]:
        """Get OpenRouter API key"""
        return os.getenv("OPENROUTER_API_KEY")

    @staticmethod
    def get_google_ads_config() -> dict:
        """Get Google Ads API configuration"""
        return {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        }

    @staticmethod
    def validate_required_keys() -> List[str]:
        """Validate that required API keys are present"""
        missing_keys = []

        if not APIKeyManager.get_openrouter_key():
            missing_keys.append("OPENROUTER_API_KEY")

        google_config = APIKeyManager.get_google_ads_config()
        required_google_keys = ["developer_token", "client_id", "client_secret"]

        for key in required_google_keys:
            if not google_config.get(key):
                missing_keys.append(f"GOOGLE_ADS_{key.upper()}")

        return missing_keys
