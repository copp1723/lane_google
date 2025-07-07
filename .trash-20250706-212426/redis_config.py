"""Redis configuration and client management for lane_google"""

import os
import redis
from typing import Optional, Union
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)


class RedisManager:
    """Manages Redis connection with fallback to in-memory storage"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.is_connected = False
        self.connection_attempted = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Redis client if URL is provided"""
        redis_url = os.getenv('REDIS_URL')
        
        if not redis_url or self.connection_attempted:
            return
        
        self.connection_attempted = True
        
        try:
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=5,
                retry_on_timeout=True,
                retry_on_error=[ConnectionError, TimeoutError],
                health_check_interval=30
            )
            
            # Test connection
            self.client.ping()
            self.is_connected = True
            logger.info("Redis connected successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {str(e)}")
            self.client = None
            self.is_connected = False
    
    def get_client(self) -> Optional[redis.Redis]:
        """Get Redis client if available"""
        if not self.client:
            return None
        
        try:
            # Test connection
            self.client.ping()
            return self.client
        except Exception as e:
            logger.warning(f"Redis connection lost: {str(e)}")
            self.is_connected = False
            return None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        client = self.get_client()
        return client is not None
    
    def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.warning(f"Error disconnecting from Redis: {str(e)}")
            finally:
                self.client = None
                self.is_connected = False


# Singleton instance
redis_manager = RedisManager()


# Decorator for Redis operations with fallback
def with_redis_fallback(fallback_value=None):
    """Decorator to handle Redis operations with fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                client = redis_manager.get_client()
                if client:
                    return func(*args, **kwargs, redis_client=client)
                else:
                    logger.debug(f"Redis not available for {func.__name__}, returning fallback")
                    return fallback_value
            except Exception as e:
                logger.warning(f"Redis operation failed in {func.__name__}: {str(e)}")
                return fallback_value
        return wrapper
    return decorator


# Rate limiting utilities
class RateLimiter:
    """Rate limiter using Redis with in-memory fallback"""
    
    def __init__(self, key_prefix: str = "rate_limit"):
        self.key_prefix = key_prefix
        self._memory_store = {}  # Fallback for when Redis is unavailable
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed within rate limit"""
        client = redis_manager.get_client()
        
        if client:
            return self._check_redis(client, key, limit, window)
        else:
            return self._check_memory(key, limit, window)
    
    def _check_redis(self, client: redis.Redis, key: str, limit: int, window: int) -> bool:
        """Check rate limit using Redis"""
        full_key = f"{self.key_prefix}:{key}"
        
        try:
            current = client.incr(full_key)
            if current == 1:
                client.expire(full_key, window)
            
            return current <= limit
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {str(e)}")
            return True  # Allow on error
    
    def _check_memory(self, key: str, limit: int, window: int) -> bool:
        """Check rate limit using in-memory storage"""
        now = time.time()
        full_key = f"{self.key_prefix}:{key}"
        
        # Clean old entries
        self._memory_store = {
            k: v for k, v in self._memory_store.items()
            if now - v['first_request'] < window
        }
        
        if full_key not in self._memory_store:
            self._memory_store[full_key] = {
                'count': 1,
                'first_request': now
            }
            return True
        
        entry = self._memory_store[full_key]
        if now - entry['first_request'] >= window:
            # Window expired, reset
            entry['count'] = 1
            entry['first_request'] = now
            return True
        
        entry['count'] += 1
        return entry['count'] <= limit


# Cache utilities
class CacheManager:
    """Cache manager using Redis with in-memory fallback"""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._memory_cache = {}  # Fallback cache
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        client = redis_manager.get_client()
        
        if client:
            try:
                return client.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed: {str(e)}")
        
        # Fallback to memory cache
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if time.time() < entry['expires']:
                return entry['value']
            else:
                del self._memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Union[str, int, float], ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        client = redis_manager.get_client()
        
        if client:
            try:
                client.setex(key, ttl, str(value))
                return True
            except Exception as e:
                logger.warning(f"Redis set failed: {str(e)}")
        
        # Fallback to memory cache
        self._memory_cache[key] = {
            'value': str(value),
            'expires': time.time() + ttl
        }
        return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        client = redis_manager.get_client()
        
        if client:
            try:
                client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {str(e)}")
        
        # Also delete from memory cache
        if key in self._memory_cache:
            del self._memory_cache[key]
        
        return True
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        count = 0
        client = redis_manager.get_client()
        
        if client:
            try:
                for key in client.scan_iter(match=pattern):
                    client.delete(key)
                    count += 1
            except Exception as e:
                logger.warning(f"Redis clear pattern failed: {str(e)}")
        
        # Clear from memory cache
        keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
        for key in keys_to_delete:
            del self._memory_cache[key]
            count += 1
        
        return count


# Initialize global instances
rate_limiter = RateLimiter()
cache_manager = CacheManager()