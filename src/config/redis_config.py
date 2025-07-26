"""
Redis Configuration and Client
Handles caching, sessions, and rate limiting
"""

import os
import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta
import redis
from redis.sentinel import Sentinel
import pickle

logger = logging.getLogger(__name__)


class RedisConfig:
    """Redis configuration"""
    
    def __init__(self):
        self.url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', '6379'))
        self.password = os.getenv('REDIS_PASSWORD', '')
        self.db = int(os.getenv('REDIS_DB', '0'))
        self.ssl = os.getenv('REDIS_SSL', 'false').lower() == 'true'
        self.max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))
        self.socket_timeout = int(os.getenv('REDIS_SOCKET_TIMEOUT', '5'))
        self.socket_connect_timeout = int(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', '5'))
        self.decode_responses = True
        
        # Sentinel configuration (for HA)
        self.sentinel_hosts = os.getenv('REDIS_SENTINEL_HOSTS', '')
        self.sentinel_master = os.getenv('REDIS_SENTINEL_MASTER', 'mymaster')
        
        # Key prefixes
        self.prefix = os.getenv('REDIS_PREFIX', 'lane_mcp:')
        self.cache_prefix = f"{self.prefix}cache:"
        self.session_prefix = f"{self.prefix}session:"
        self.rate_limit_prefix = f"{self.prefix}rate_limit:"
        self.lock_prefix = f"{self.prefix}lock:"
        
        # TTL settings
        self.default_cache_ttl = int(os.getenv('REDIS_CACHE_TTL', '3600'))  # 1 hour
        self.session_ttl = int(os.getenv('REDIS_SESSION_TTL', '86400'))  # 24 hours
        self.rate_limit_ttl = int(os.getenv('REDIS_RATE_LIMIT_TTL', '60'))  # 1 minute


class RedisClient:
    """Redis client wrapper with common operations"""
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self._client = None
        self._sentinel = None
        
    @property
    def client(self) -> redis.Redis:
        """Get Redis client (lazy initialization)"""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self) -> redis.Redis:
        """Create Redis client"""
        try:
            if self.config.sentinel_hosts:
                # Use Sentinel for HA
                sentinel_hosts = [
                    tuple(host.strip().split(':'))
                    for host in self.config.sentinel_hosts.split(',')
                ]
                self._sentinel = Sentinel(
                    sentinel_hosts,
                    socket_timeout=self.config.socket_timeout,
                    password=self.config.password if self.config.password else None
                )
                return self._sentinel.master_for(
                    self.config.sentinel_master,
                    socket_timeout=self.config.socket_timeout,
                    password=self.config.password if self.config.password else None,
                    db=self.config.db
                )
            else:
                # Direct connection
                return redis.Redis(
                    host=self.config.host,
                    port=self.config.port,
                    password=self.config.password if self.config.password else None,
                    db=self.config.db,
                    ssl=self.config.ssl,
                    decode_responses=self.config.decode_responses,
                    max_connections=self.config.max_connections,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout
                )
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            raise
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    # Cache operations
    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            full_key = f"{self.config.cache_prefix}{key}"
            value = self.client.get(full_key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            full_key = f"{self.config.cache_prefix}{key}"
            ttl = ttl or self.config.default_cache_ttl
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            return self.client.setex(full_key, ttl, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def cache_delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            full_key = f"{self.config.cache_prefix}{key}"
            return bool(self.client.delete(full_key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def cache_clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        try:
            full_pattern = f"{self.config.cache_prefix}{pattern}"
            keys = list(self.client.scan_iter(match=full_pattern))
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    # Session operations
    def session_get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            full_key = f"{self.config.session_prefix}{session_id}"
            value = self.client.get(full_key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Session get error: {e}")
            return None
    
    def session_set(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Set session data"""
        try:
            full_key = f"{self.config.session_prefix}{session_id}"
            return self.client.setex(
                full_key,
                self.config.session_ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Session set error: {e}")
            return False
    
    def session_delete(self, session_id: str) -> bool:
        """Delete session"""
        try:
            full_key = f"{self.config.session_prefix}{session_id}"
            return bool(self.client.delete(full_key))
        except Exception as e:
            logger.error(f"Session delete error: {e}")
            return False
    
    def session_extend(self, session_id: str) -> bool:
        """Extend session TTL"""
        try:
            full_key = f"{self.config.session_prefix}{session_id}"
            return self.client.expire(full_key, self.config.session_ttl)
        except Exception as e:
            logger.error(f"Session extend error: {e}")
            return False
    
    # Rate limiting
    def rate_limit_check(self, identifier: str, limit: int, window: int = None) -> tuple[bool, int]:
        """
        Check rate limit
        Returns (allowed, remaining_requests)
        """
        try:
            window = window or self.config.rate_limit_ttl
            full_key = f"{self.config.rate_limit_prefix}{identifier}"
            
            pipe = self.client.pipeline()
            pipe.incr(full_key)
            pipe.expire(full_key, window)
            current, _ = pipe.execute()
            
            allowed = current <= limit
            remaining = max(0, limit - current)
            
            return allowed, remaining
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, limit  # Fail open
    
    # Distributed locking
    def acquire_lock(self, resource: str, timeout: int = 10) -> Optional[str]:
        """Acquire distributed lock"""
        try:
            full_key = f"{self.config.lock_prefix}{resource}"
            identifier = os.urandom(16).hex()
            
            acquired = self.client.set(
                full_key,
                identifier,
                nx=True,
                ex=timeout
            )
            
            return identifier if acquired else None
        except Exception as e:
            logger.error(f"Lock acquire error: {e}")
            return None
    
    def release_lock(self, resource: str, identifier: str) -> bool:
        """Release distributed lock"""
        try:
            full_key = f"{self.config.lock_prefix}{resource}"
            
            # Use Lua script for atomic check and delete
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            return bool(self.client.eval(lua_script, 1, full_key, identifier))
        except Exception as e:
            logger.error(f"Lock release error: {e}")
            return False
    
    # Pub/Sub operations
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            return self.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Publish error: {e}")
            return 0
    
    def subscribe(self, *channels):
        """Subscribe to channels"""
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            logger.error(f"Subscribe error: {e}")
            return None
    
    # Queue operations (for background jobs)
    def queue_push(self, queue: str, item: Any) -> int:
        """Push item to queue"""
        try:
            full_key = f"{self.config.prefix}queue:{queue}"
            if isinstance(item, (dict, list)):
                item = json.dumps(item)
            return self.client.rpush(full_key, item)
        except Exception as e:
            logger.error(f"Queue push error: {e}")
            return 0
    
    def queue_pop(self, queue: str, timeout: int = 0) -> Optional[Any]:
        """Pop item from queue (blocking)"""
        try:
            full_key = f"{self.config.prefix}queue:{queue}"
            result = self.client.blpop(full_key, timeout=timeout)
            if result:
                _, value = result
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Queue pop error: {e}")
            return None
    
    def queue_length(self, queue: str) -> int:
        """Get queue length"""
        try:
            full_key = f"{self.config.prefix}queue:{queue}"
            return self.client.llen(full_key)
        except Exception as e:
            logger.error(f"Queue length error: {e}")
            return 0


# Global Redis client instance
redis_config = RedisConfig()
redis_client = RedisClient(redis_config)


# Flask-Session configuration
def get_flask_session_config() -> dict:
    """Get Flask-Session configuration for Redis"""
    return {
        'SESSION_TYPE': 'redis',
        'SESSION_REDIS': redis_client.client,
        'SESSION_PERMANENT': False,
        'SESSION_USE_SIGNER': True,
        'SESSION_KEY_PREFIX': redis_config.session_prefix,
        'PERMANENT_SESSION_LIFETIME': timedelta(seconds=redis_config.session_ttl)
    }


# Cache decorator
def redis_cache(key_prefix: str, ttl: Optional[int] = None):
    """Decorator for caching function results in Redis"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(arg) for arg in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached = redis_client.cache_get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            redis_client.cache_set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator