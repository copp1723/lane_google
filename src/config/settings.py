"""
Application Settings and Configuration
Centralized configuration management with environment variable support
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', 'sqlite:///lane_mcp.db'))
    echo: bool = field(default_factory=lambda: os.getenv('DATABASE_ECHO', 'False').lower() == 'true')
    pool_size: int = field(default_factory=lambda: int(os.getenv('DATABASE_POOL_SIZE', '10')))
    max_overflow: int = field(default_factory=lambda: int(os.getenv('DATABASE_MAX_OVERFLOW', '20')))
    pool_timeout: int = field(default_factory=lambda: int(os.getenv('DATABASE_POOL_TIMEOUT', '30')))
    pool_recycle: int = field(default_factory=lambda: int(os.getenv('DATABASE_POOL_RECYCLE', '3600')))


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = field(default_factory=lambda: os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'))
    jwt_secret_key: str = field(default_factory=lambda: os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'))
    jwt_expiration_hours: int = field(default_factory=lambda: int(os.getenv('JWT_EXPIRATION_HOURS', '24')))
    password_salt_rounds: int = field(default_factory=lambda: int(os.getenv('PASSWORD_SALT_ROUNDS', '12')))
    cors_origins: list = field(default_factory=lambda: os.getenv('CORS_ORIGINS', '*').split(','))


@dataclass
class GoogleAdsConfig:
    """Google Ads API configuration"""
    client_id: Optional[str] = field(default_factory=lambda: os.getenv('GOOGLE_ADS_CLIENT_ID'))
    client_secret: Optional[str] = field(default_factory=lambda: os.getenv('GOOGLE_ADS_CLIENT_SECRET'))
    refresh_token: Optional[str] = field(default_factory=lambda: os.getenv('GOOGLE_ADS_REFRESH_TOKEN'))
    developer_token: Optional[str] = field(default_factory=lambda: os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'))
    login_customer_id: Optional[str] = field(default_factory=lambda: os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID'))
    use_proto_plus: bool = field(default_factory=lambda: os.getenv('GOOGLE_ADS_USE_PROTO_PLUS', 'True').lower() == 'true')


@dataclass
class OpenRouterConfig:
    """OpenRouter API configuration"""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv('OPENROUTER_API_KEY'))
    base_url: str = field(default_factory=lambda: os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'))
    model: str = field(default_factory=lambda: os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet'))
    max_tokens: int = field(default_factory=lambda: int(os.getenv('OPENROUTER_MAX_TOKENS', '4000')))
    temperature: float = field(default_factory=lambda: float(os.getenv('OPENROUTER_TEMPERATURE', '0.7'))))


@dataclass
class RedisConfig:
    """Redis configuration"""
    url: str = field(default_factory=lambda: os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    password: Optional[str] = field(default_factory=lambda: os.getenv('REDIS_PASSWORD'))
    db: int = field(default_factory=lambda: int(os.getenv('REDIS_DB', '0')))
    max_connections: int = field(default_factory=lambda: int(os.getenv('REDIS_MAX_CONNECTIONS', '10')))


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    format: str = field(default_factory=lambda: os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_path: Optional[str] = field(default_factory=lambda: os.getenv('LOG_FILE_PATH'))
    max_file_size: int = field(default_factory=lambda: int(os.getenv('LOG_MAX_FILE_SIZE', '10485760')))  # 10MB
    backup_count: int = field(default_factory=lambda: int(os.getenv('LOG_BACKUP_COUNT', '5')))


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = field(default_factory=lambda: os.getenv('HOST', '0.0.0.0'))
    port: int = field(default_factory=lambda: int(os.getenv('PORT', '5000')))
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    workers: int = field(default_factory=lambda: int(os.getenv('WORKERS', '4')))
    timeout: int = field(default_factory=lambda: int(os.getenv('TIMEOUT', '30')))


@dataclass
class FeatureFlags:
    """Feature flags configuration"""
    ai_chat_enabled: bool = field(default_factory=lambda: os.getenv('FEATURE_AI_CHAT', 'True').lower() == 'true')
    real_time_monitoring: bool = field(default_factory=lambda: os.getenv('FEATURE_REAL_TIME_MONITORING', 'True').lower() == 'true')
    auto_optimization: bool = field(default_factory=lambda: os.getenv('FEATURE_AUTO_OPTIMIZATION', 'True').lower() == 'true')
    workflow_approval: bool = field(default_factory=lambda: os.getenv('FEATURE_WORKFLOW_APPROVAL', 'True').lower() == 'true')
    performance_analytics: bool = field(default_factory=lambda: os.getenv('FEATURE_PERFORMANCE_ANALYTICS', 'True').lower() == 'true')


@dataclass
class ApplicationSettings:
    """Main application settings"""
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    app_name: str = field(default_factory=lambda: os.getenv('APP_NAME', 'Lane MCP'))
    app_version: str = field(default_factory=lambda: os.getenv('APP_VERSION', '1.0.0'))
    
    # Configuration sections
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    google_ads: GoogleAdsConfig = field(default_factory=GoogleAdsConfig)
    openrouter: OpenRouterConfig = field(default_factory=OpenRouterConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() in ['development', 'dev', 'local']
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() in ['production', 'prod']
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.environment.lower() in ['testing', 'test']
    
    def validate_required_settings(self) -> Dict[str, list]:
        """Validate that required settings are present"""
        errors = {}
        warnings = []
        
        # Check critical settings
        if self.is_production:
            if self.security.secret_key == 'dev-secret-key-change-in-production':
                errors.setdefault('security', []).append('SECRET_KEY must be set in production')
            
            if self.security.jwt_secret_key == 'jwt-secret-key-change-in-production':
                errors.setdefault('security', []).append('JWT_SECRET_KEY must be set in production')
        
        # Check Google Ads configuration
        if not self.google_ads.client_id:
            warnings.append('Google Ads client ID not configured - Google Ads features will be disabled')
        
        if not self.google_ads.developer_token:
            warnings.append('Google Ads developer token not configured - Google Ads features will be disabled')
        
        # Check OpenRouter configuration
        if not self.openrouter.api_key:
            warnings.append('OpenRouter API key not configured - AI features will be disabled')
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def get_database_url(self) -> str:
        """Get database URL with fallback logic"""
        if self.database.url.startswith('sqlite:'):
            # Ensure SQLite directory exists
            import os
            db_path = self.database.url.replace('sqlite:///', '').replace('sqlite://', '')
            if db_path and '/' in db_path:
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        return self.database.url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)"""
        return {
            'environment': self.environment,
            'app_name': self.app_name,
            'app_version': self.app_version,
            'is_development': self.is_development,
            'is_production': self.is_production,
            'features': {
                'ai_chat_enabled': self.features.ai_chat_enabled,
                'real_time_monitoring': self.features.real_time_monitoring,
                'auto_optimization': self.features.auto_optimization,
                'workflow_approval': self.features.workflow_approval,
                'performance_analytics': self.features.performance_analytics
            },
            'services': {
                'google_ads_configured': bool(self.google_ads.client_id and self.google_ads.developer_token),
                'openrouter_configured': bool(self.openrouter.api_key),
                'redis_configured': 'redis://' in self.redis.url
            }
        }


# Global settings instance
settings = ApplicationSettings()

# Validate settings on import
validation_result = settings.validate_required_settings()
if validation_result['errors']:
    import logging
    logger = logging.getLogger(__name__)
    for category, error_list in validation_result['errors'].items():
        for error in error_list:
            logger.error(f"Configuration error ({category}): {error}")

if validation_result['warnings']:
    import logging
    logger = logging.getLogger(__name__)
    for warning in validation_result['warnings']:
        logger.warning(f"Configuration warning: {warning}")


def get_settings() -> ApplicationSettings:
    """Get application settings"""
    return settings


def reload_settings():
    """Reload settings from environment"""
    global settings
    load_dotenv(override=True)
    settings = ApplicationSettings()
    return settings