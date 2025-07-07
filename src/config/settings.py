"""
Environment Configuration Management
Handles all environment variables and configuration settings
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class RedisConfig:
    """Redis configuration"""
    url: str
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    decode_responses: bool = True


@dataclass
class GoogleAdsConfig:
    """Google Ads API configuration"""
    client_id: str
    client_secret: str
    refresh_token: str
    developer_token: str
    customer_id: Optional[str] = None
    login_customer_id: Optional[str] = None


@dataclass
class EmailConfig:
    """Email service configuration"""
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    from_email: str
    use_tls: bool = True


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str
    jwt_secret_key: str
    password_salt: str
    session_lifetime_hours: int = 24
    rate_limit_per_minute: int = 60


@dataclass
class AppConfig:
    """Main application configuration"""
    environment: str
    debug: bool
    host: str = "0.0.0.0"
    port: int = 5000
    log_level: str = "INFO"
    cors_origins: str = "*"


class Settings:
    """Application settings manager"""
    
    def __init__(self):
        self.environment = os.getenv('FLASK_ENV', 'development')
        self.debug = self.environment == 'development'
        
        # Load environment-specific settings
        self._load_env_file()
        
        # Initialize configurations
        self.app = self._load_app_config()
        self.database = self._load_database_config()
        self.redis = self._load_redis_config()
        self.google_ads = self._load_google_ads_config()
        self.email = self._load_email_config()
        self.security = self._load_security_config()
        
        # Validate critical settings
        self._validate_settings()
    
    def _load_env_file(self):
        """Load environment-specific .env file"""
        env_files = [
            f'.env.{self.environment}',
            '.env.local',
            '.env'
        ]
        
        for env_file in env_files:
            if os.path.exists(env_file):
                self._load_dotenv(env_file)
                logger.info(f"Loaded environment file: {env_file}")
                break
    
    def _load_dotenv(self, file_path: str):
        """Load variables from .env file"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
        except Exception as e:
            logger.warning(f"Could not load {file_path}: {str(e)}")
    
    def _load_app_config(self) -> AppConfig:
        """Load application configuration"""
        return AppConfig(
            environment=self.environment,
            debug=self.debug,
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', 5000)),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            cors_origins=os.getenv('CORS_ORIGINS', '*')
        )
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        # Default to PostgreSQL in production, SQLite in development
        if self.environment == 'production':
            default_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/lane_mcp')
        else:
            default_url = f"sqlite:///{Path(__file__).parent.parent.parent}/database/app.db"
        
        return DatabaseConfig(
            url=os.getenv('DATABASE_URL', default_url),
            echo=os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
            pool_size=int(os.getenv('DATABASE_POOL_SIZE', 10)),
            max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', 20)),
            pool_timeout=int(os.getenv('DATABASE_POOL_TIMEOUT', 30)),
            pool_recycle=int(os.getenv('DATABASE_POOL_RECYCLE', 3600))
        )
    
    def _load_redis_config(self) -> Optional[RedisConfig]:
        """Load Redis configuration"""
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            # Try individual components
            redis_host = os.getenv('REDIS_HOST')
            if not redis_host:
                return None
            
            redis_url = f"redis://{redis_host}:{os.getenv('REDIS_PORT', 6379)}"
        
        return RedisConfig(
            url=redis_url,
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
    
    def _load_google_ads_config(self) -> Optional[GoogleAdsConfig]:
        """Load Google Ads API configuration"""
        client_id = os.getenv('GOOGLE_ADS_CLIENT_ID')
        if not client_id:
            return None
        
        return GoogleAdsConfig(
            client_id=client_id,
            client_secret=os.getenv('GOOGLE_ADS_CLIENT_SECRET', ''),
            refresh_token=os.getenv('GOOGLE_ADS_REFRESH_TOKEN', ''),
            developer_token=os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', ''),
            customer_id=os.getenv('GOOGLE_ADS_CUSTOMER_ID'),
            login_customer_id=os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
        )
    
    def _load_email_config(self) -> Optional[EmailConfig]:
        """Load email configuration"""
        smtp_host = os.getenv('SMTP_HOST')
        if not smtp_host:
            return None
        
        return EmailConfig(
            smtp_host=smtp_host,
            smtp_port=int(os.getenv('SMTP_PORT', 587)),
            smtp_user=os.getenv('SMTP_USER', ''),
            smtp_password=os.getenv('SMTP_PASSWORD', ''),
            from_email=os.getenv('FROM_EMAIL', ''),
            use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        return SecurityConfig(
            secret_key=os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
            jwt_secret_key=os.getenv('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production'),
            password_salt=os.getenv('PASSWORD_SALT', 'salt-change-in-production'),
            session_lifetime_hours=int(os.getenv('SESSION_LIFETIME_HOURS', 24)),
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
        )
    
    def _validate_settings(self):
        """Validate critical settings"""
        errors = []
        
        # Production validations
        if self.environment == 'production':
            if self.security.secret_key == 'dev-key-change-in-production':
                errors.append("SECRET_KEY must be changed in production")
            
            if not self.database.url.startswith(('postgresql://', 'mysql://')):
                errors.append("Production requires PostgreSQL or MySQL database")
            
            if not self.google_ads:
                errors.append("Google Ads configuration required in production")
            elif not all([
                self.google_ads.client_id,
                self.google_ads.client_secret,
                self.google_ads.refresh_token,
                self.google_ads.developer_token
            ]):
                errors.append("Incomplete Google Ads configuration")
        
        # General validations
        if not self.security.secret_key:
            errors.append("SECRET_KEY is required")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        logger.info(f"Configuration validated for {self.environment} environment")
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        return self.database.url
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL"""
        return self.redis.url if self.redis else None
    
    def is_google_ads_configured(self) -> bool:
        """Check if Google Ads is properly configured"""
        return (self.google_ads is not None and 
                all([
                    self.google_ads.client_id,
                    self.google_ads.client_secret,
                    self.google_ads.refresh_token,
                    self.google_ads.developer_token
                ]))
    
    def get_google_ads_config_dict(self) -> Dict[str, str]:
        """Get Google Ads config as dictionary for API client"""
        if not self.google_ads:
            raise ValueError("Google Ads not configured")
        
        config = {
            'client_id': self.google_ads.client_id,
            'client_secret': self.google_ads.client_secret,
            'refresh_token': self.google_ads.refresh_token,
            'developer_token': self.google_ads.developer_token,
        }
        
        if self.google_ads.customer_id:
            config['customer_id'] = self.google_ads.customer_id
        if self.google_ads.login_customer_id:
            config['login_customer_id'] = self.google_ads.login_customer_id
        
        return config
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask configuration dictionary"""
        config = {
            'SECRET_KEY': self.security.secret_key,
            'DEBUG': self.debug,
            'SQLALCHEMY_DATABASE_URI': self.database.url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
                'pool_timeout': self.database.pool_timeout,
                'pool_recycle': self.database.pool_recycle,
                'echo': self.database.echo
            }
        }
        
        # Redis configuration
        if self.redis:
            config['REDIS_URL'] = self.redis.url
            config['SESSION_TYPE'] = 'redis'
            config['SESSION_REDIS'] = self.redis.url
        
        # Security settings
        config['JWT_SECRET_KEY'] = self.security.jwt_secret_key
        config['JWT_ACCESS_TOKEN_EXPIRES'] = self.security.session_lifetime_hours * 3600
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (safe for logging)"""
        return {
            'environment': self.environment,
            'debug': self.debug,
            'app': {
                'host': self.app.host,
                'port': self.app.port,
                'log_level': self.app.log_level
            },
            'database': {
                'url': self.database.url.split('@')[-1] if '@' in self.database.url else 'sqlite',
                'pool_size': self.database.pool_size
            },
            'redis_configured': self.redis is not None,
            'google_ads_configured': self.is_google_ads_configured(),
            'email_configured': self.email is not None,
            'security': {
                'session_lifetime_hours': self.security.session_lifetime_hours,
                'rate_limit_per_minute': self.security.rate_limit_per_minute
            }
        }
    
    def is_redis_configured(self) -> bool:
        """Check if Redis is properly configured"""
        return self.redis is not None


# Global settings instance
settings = Settings()