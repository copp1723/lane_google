"""
Health check API endpoints.
Merged from health.py and health_api.py
"""

from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import psutil
import redis
import logging

from ..config.database import get_db, engine
from ..config.settings import settings
from ..auth.authentication import get_current_user, get_admin_user
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])

# Redis client
redis_client = redis.from_url(settings.redis.url, decode_responses=True)


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, Dict[str, Any]]
    system: Dict[str, Any]


class ServiceHealth(BaseModel):
    """Individual service health."""
    name: str
    status: str
    latency_ms: float
    details: Dict[str, Any] = {}


@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    Basic health check endpoint.
    Returns the overall system health status.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.app_version,
        "services": {},
        "system": {}
    }
    
    # Check database
    db_health = await check_database_health()
    health_status["services"]["database"] = db_health
    
    # Check Redis
    redis_health = await check_redis_health()
    health_status["services"]["redis"] = redis_health
    
    # Check system resources
    system_health = await check_system_health()
    health_status["system"] = system_health
    
    # Determine overall status
    if any(service["status"] == "unhealthy" for service in health_status["services"].values()):
        health_status["status"] = "unhealthy"
    elif any(service["status"] == "degraded" for service in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/detailed", response_model=HealthStatus)
async def detailed_health_check(current_user: User = Depends(get_admin_user)):
    """
    Detailed health check endpoint (admin only).
    Returns comprehensive system health information.
    """
    health_status = await health_check()
    
    # Add additional detailed information
    health_status["services"]["google_ads"] = await check_google_ads_health()
    health_status["services"]["ai_service"] = await check_ai_service_health()
    
    # Add more system metrics
    health_status["system"]["connections"] = get_connection_stats()
    health_status["system"]["performance"] = get_performance_metrics()
    
    return health_status


async def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    start_time = datetime.utcnow()
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").scalar()
            
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Get connection pool stats
        pool_stats = {
            "size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "overflow": engine.pool.overflow(),
            "total": engine.pool.checkedout()
        }
        
        return {
            "status": "healthy" if latency_ms < 100 else "degraded",
            "latency_ms": round(latency_ms, 2),
            "details": {
                "pool_stats": pool_stats,
                "database": settings.get_database_url().split("@")[-1].split("/")[0] if "@" in settings.get_database_url() else "sqlite"
            }
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "latency_ms": -1,
            "error": str(e)
        }


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity and performance."""
    start_time = datetime.utcnow()
    
    try:
        # Test connection
        redis_client.ping()
        
        # Get Redis info
        info = redis_client.info()
        
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "status": "healthy" if latency_ms < 50 else "degraded",
            "latency_ms": round(latency_ms, 2),
            "details": {
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "uptime_days": info.get("uptime_in_days")
            }
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "latency_ms": -1,
            "error": str(e)
        }


async def check_system_health() -> Dict[str, Any]:
    """Check system resources."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage("/")
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "cores": psutil.cpu_count()
            },
            "memory": {
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024 ** 3), 2),
                "total_gb": round(memory.total / (1024 ** 3), 2)
            },
            "disk": {
                "usage_percent": disk.percent,
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "total_gb": round(disk.total / (1024 ** 3), 2)
            }
        }
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        return {"error": str(e)}


async def check_google_ads_health() -> Dict[str, Any]:
    """Check Google Ads API connectivity."""
    # TODO: Implement actual Google Ads API health check
    return {
        "status": "healthy",
        "latency_ms": 0,
        "details": {
            "api_version": "v14",
            "authenticated": True
        }
    }


async def check_ai_service_health() -> Dict[str, Any]:
    """Check AI service connectivity."""
    # TODO: Implement actual AI service health check
    return {
        "status": "healthy",
        "latency_ms": 0,
        "details": {
            "model": "gpt-4",
            "available": True
        }
    }


def get_connection_stats() -> Dict[str, Any]:
    """Get network connection statistics."""
    try:
        connections = psutil.net_connections()
        
        status_counts = {}
        for conn in connections:
            status = conn.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total": len(connections),
            "by_status": status_counts
        }
    except Exception as e:
        return {"error": str(e)}


def get_performance_metrics() -> Dict[str, Any]:
    """Get application performance metrics."""
    # TODO: Implement actual performance metrics collection
    return {
        "avg_response_time_ms": 50,
        "requests_per_second": 100,
        "error_rate": 0.01
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint for uptime monitoring."""
    return {"status": "pong", "timestamp": datetime.utcnow()}


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if the service is ready to accept traffic.
    """
    # Check critical services
    db_health = await check_database_health()
    redis_health = await check_redis_health()
    
    if db_health["status"] == "unhealthy" or redis_health["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if the service is alive.
    """
    return {"status": "alive"}
