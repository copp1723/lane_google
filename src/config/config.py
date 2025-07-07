"""
Enterprise Configuration Management
Centralized configuration handling for the Lane MCP platform
"""

import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

from src.utils.security import APIKeyManager, SecurityConfig

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings"""

    url: str
    track_modifications: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class OpenRouterConfig:
    """OpenRouter API configuration"""

    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-3.5-sonnet"
    timeout: int = 30
    max_retries: int = 3


@dataclass
class GoogleAdsConfig:
    """Google Ads API configuration"""

    developer_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    login_customer_id: Optional[str] = None
    use_proto_plus: bool = True


@dataclass
class RedisConfig:
    """Redis configuration"""

    url: str
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 10


@dataclass
class CeleryConfig:
    """Celery configuration"""

    broker_url: str
    result_backend: str
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = None
    timezone: str = "UTC"


@dataclass
class JWTConfig:
    """JWT configuration"""

    secret_key: str
    access_token_expires: int = 3600
    refresh_token_expires: int = 2592000
    algorithm: str = "HS256"


@dataclass
class SecurityConfig:
    """Security configuration"""

    cors_origins: List[str]
    secure_headers_enabled: bool = True
    csrf_protection_enabled: bool = True
    rate_limit_storage_url: str = "memory://"
    default_rate_limit: str = "100 per hour"


@dataclass
class FeatureFlags:
    """Feature flags configuration"""

    budget_pacing_enabled: bool = True
    automated_optimization_enabled: bool = True
    real_time_monitoring_enabled: bool = True
    advanced_analytics_enabled: bool = True
    prometheus_metrics_enabled: bool = True
    health_check_enabled: bool = True


class Config:
    """Main configuration class"""

    def __init__(self):
        self.app = self._load_app_config()
        self.database = self._load_database_config()
        self.openrouter = self._load_openrouter_config()
        self.google_ads = self._load_google_ads_config()
        self.redis = self._load_redis_config()
        self.celery = self._load_celery_config()
        self.jwt = self._load_jwt_config()
        self.security = self._load_security_config()
        self.features = self._load_feature_flags()

    def _load_app_config(self) -> dict:
        """Load application configuration"""
        return {
            "SECRET_KEY": os.getenv("SECRET_KEY", "dev-secret-key"),
            "DEBUG": os.getenv("DEBUG", "False").lower() == "true",
            "FLASK_ENV": os.getenv("FLASK_ENV", "development"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "LOG_FORMAT": os.getenv(
                "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
        }

    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///lane_mcp_dev.db"),
            track_modifications=os.getenv(
                "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
            ).lower()
            == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
        )

    def _load_openrouter_config(self) -> OpenRouterConfig:
        """Load OpenRouter configuration"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        return OpenRouterConfig(
            api_key=api_key,
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            default_model=os.getenv(
                "OPENROUTER_DEFAULT_MODEL", "anthropic/claude-3.5-sonnet"
            ),
            timeout=int(os.getenv("OPENROUTER_TIMEOUT", "30")),
            max_retries=int(os.getenv("OPENROUTER_MAX_RETRIES", "3")),
        )

    def _load_google_ads_config(self) -> GoogleAdsConfig:
        """Load Google Ads configuration"""
        return GoogleAdsConfig(
            developer_token=os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
            client_id=os.getenv("GOOGLE_ADS_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_ADS_CLIENT_SECRET", ""),
            refresh_token=os.getenv("GOOGLE_ADS_REFRESH_TOKEN", ""),
            login_customer_id=os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            use_proto_plus=os.getenv("GOOGLE_ADS_USE_PROTO_PLUS", "True").lower()
            == "true",
        )

    def _load_redis_config(self) -> RedisConfig:
        """Load Redis configuration"""
        return RedisConfig(
            url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
        )

    def _load_celery_config(self) -> CeleryConfig:
        """Load Celery configuration"""
        return CeleryConfig(
            broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
            result_backend=os.getenv(
                "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
            ),
            task_serializer=os.getenv("CELERY_TASK_SERIALIZER", "json"),
            result_serializer=os.getenv("CELERY_RESULT_SERIALIZER", "json"),
            accept_content=os.getenv("CELERY_ACCEPT_CONTENT", "json").split(","),
            timezone=os.getenv("CELERY_TIMEZONE", "UTC"),
        )

    def _load_jwt_config(self) -> JWTConfig:
        """Load JWT configuration"""
        return JWTConfig(
            secret_key=os.getenv("JWT_SECRET_KEY", "jwt-secret-key"),
            access_token_expires=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")),
            refresh_token_expires=int(
                os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")
            ),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        )

    def _load_security_config(self) -> dict:
        """Load security configuration"""
        # Security settings
        from src.utils.security import SecurityConfig as SecurityUtils
        
        secret_key = SecurityUtils.get_secret_key()
        jwt_secret = SecurityUtils.get_jwt_secret()
        cors_origins = SecurityUtils.get_allowed_origins()
        
        return {
            'secret_key': secret_key,
            'jwt_secret': jwt_secret,
            'cors_origins': cors_origins,
            'secure_headers_enabled': os.getenv("SECURE_HEADERS_ENABLED", "True").lower() == "true",
            'csrf_protection_enabled': os.getenv("CSRF_PROTECTION_ENABLED", "True").lower() == "true",
            'rate_limiting_enabled': os.getenv("RATE_LIMITING_ENABLED", "True").lower() == "true",
            'rate_limit_storage_url': os.getenv("RATELIMIT_STORAGE_URL", "memory://"),
            'default_rate_limit': os.getenv("RATELIMIT_DEFAULT", "100 per hour"),
        }

    def _load_feature_flags(self) -> FeatureFlags:
        """Load feature flags"""
        return FeatureFlags(
            budget_pacing_enabled=os.getenv("BUDGET_PACING_ENABLED", "True").lower()
            == "true",
            automated_optimization_enabled=os.getenv(
                "AUTOMATED_OPTIMIZATION_ENABLED", "True"
            ).lower()
            == "true",
            real_time_monitoring_enabled=os.getenv(
                "REAL_TIME_MONITORING_ENABLED", "True"
            ).lower()
            == "true",
            advanced_analytics_enabled=os.getenv(
                "ADVANCED_ANALYTICS_ENABLED", "True"
            ).lower()
            == "true",
            prometheus_metrics_enabled=os.getenv(
                "PROMETHEUS_METRICS_ENABLED", "True"
            ).lower()
            == "true",
            health_check_enabled=os.getenv("HEALTH_CHECK_ENABLED", "True").lower()
            == "true",
        )

    def validate(self) -> bool:
        """Validate configuration"""
        errors = []

        # Validate required OpenRouter configuration
        if not self.openrouter.api_key:
            errors.append("OPENROUTER_API_KEY is required")

        # Validate Google Ads configuration if features are enabled
        if self.features.automated_optimization_enabled:
            if not self.google_ads.developer_token:
                errors.append(
                    "GOOGLE_ADS_DEVELOPER_TOKEN is required for automated optimization"
                )
            if not self.google_ads.client_id:
                errors.append(
                    "GOOGLE_ADS_CLIENT_ID is required for automated optimization"
                )
            if not self.google_ads.client_secret:
                errors.append(
                    "GOOGLE_ADS_CLIENT_SECRET is required for automated optimization"
                )

        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

        return True


# Global configuration instance
config = Config()

# Validate configuration on import
config.validate()
