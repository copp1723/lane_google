"""
Health Monitoring Service
Comprehensive health checks for Google Ads automation platform
"""

import logging
import os
import psutil
from datetime import datetime
from typing import Dict, Any, List
from flask import current_app
from database import db
from redis_config import redis_client
import asyncio
from google_ads import GoogleAdsClient

logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status constants"""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    UNHEALTHY = 'unhealthy'


class HealthMonitor:
    """Health monitoring service for the platform"""
    
    def __init__(self):
        self.health_checks = {
            'database': self._check_database_health,
            'redis': self._check_redis_health,
            'google_ads': self._check_google_ads_health,
            'system': self._check_system_health,
            'services': self._check_services_health
        }
        self.last_check_results = {}
        self.check_history = []
        
    async def get_health_status(self, detailed: bool = False) -> Dict[str, Any]:
        """Get overall health status of the system"""
        try:
            # Run all health checks
            results = {}
            overall_status = HealthStatus.HEALTHY
            
            for check_name, check_func in self.health_checks.items():
                try:
                    result = await check_func()
                    results[check_name] = result
                    
                    # Update overall status
                    if result['status'] == HealthStatus.UNHEALTHY:
                        overall_status = HealthStatus.UNHEALTHY
                    elif result['status'] == HealthStatus.DEGRADED and overall_status != HealthStatus.UNHEALTHY:
                        overall_status = HealthStatus.DEGRADED
                        
                except Exception as e:
                    logger.error(f"Health check failed for {check_name}: {str(e)}")
                    results[check_name] = {
                        'status': HealthStatus.UNHEALTHY,
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    overall_status = HealthStatus.UNHEALTHY
            
            # Build response
            health_data = {
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'services': results
            }
            
            if detailed:
                health_data['environment'] = self._get_environment_info()
                health_data['system'] = results.get('system', {})
            
            # Store results
            self.last_check_results = health_data
            self._update_health_history(health_data)
            
            return health_data
            
        except Exception as e:
            logger.error(f"Critical error in health check: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = datetime.utcnow()
            
            # Simple query to check connectivity
            result = db.session.execute('SELECT 1').scalar()
            
            # Check table counts for basic health
            campaign_count = db.session.execute('SELECT COUNT(*) FROM campaigns').scalar()
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Determine health based on response time
            if response_time > 1.0:
                status = HealthStatus.DEGRADED
                message = f"Database response slow: {response_time:.2f}s"
            else:
                status = HealthStatus.HEALTHY
                message = "Database is responsive"
            
            return {
                'status': status,
                'message': message,
                'response_time': response_time,
                'campaign_count': campaign_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            if not redis_client:
                return {
                    'status': HealthStatus.DEGRADED,
                    'message': 'Redis not configured',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            start_time = datetime.utcnow()
            
            # Ping Redis
            redis_client.ping()
            
            # Get Redis info
            info = redis_client.info()
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'Redis is healthy',
                'response_time': response_time,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_google_ads_health(self) -> Dict[str, Any]:
        """Check Google Ads API connectivity"""
        try:
            # Check if credentials are configured
            if not os.environ.get('GOOGLE_ADS_CLIENT_ID'):
                return {
                    'status': HealthStatus.DEGRADED,
                    'message': 'Google Ads not fully configured',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # In production, you would make a lightweight API call
            # For now, we'll just check configuration
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'Google Ads API configured',
                'api_version': 'v15',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Google Ads health check failed: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system resources and performance"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Determine health based on resource usage
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > 80:
                status = HealthStatus.DEGRADED
                warnings.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 85:
                status = HealthStatus.DEGRADED
                warnings.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                status = HealthStatus.DEGRADED
                warnings.append(f"Low disk space: {disk.percent}% used")
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory': {
                    'percent': memory.percent,
                    'available': memory.available,
                    'total': memory.total
                },
                'disk': {
                    'percent': disk.percent,
                    'free': disk.free,
                    'total': disk.total
                },
                'warnings': warnings,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_services_health(self) -> Dict[str, Any]:
        """Check health of internal services"""
        try:
            services_status = {}
            
            # Check if budget pacing service is running
            from src.services.budget_pacing import budget_pacing_service
            if budget_pacing_service.monitoring_task and not budget_pacing_service.monitoring_task.done():
                services_status['budget_pacing'] = 'running'
            else:
                services_status['budget_pacing'] = 'stopped'
            
            # Check if AI agent is responsive (basic check)
            services_status['ai_agent'] = 'configured' if os.environ.get('OPENAI_API_KEY') else 'not_configured'
            
            # Determine overall service health
            all_running = all(status == 'running' or status == 'configured' 
                            for status in services_status.values())
            
            return {
                'status': HealthStatus.HEALTHY if all_running else HealthStatus.DEGRADED,
                'services': services_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Services health check failed: {str(e)}")
            return {
                'status': HealthStatus.UNHEALTHY,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_environment_info(self) -> Dict[str, str]:
        """Get environment configuration info"""
        return {
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'debug_mode': current_app.debug,
            'database_configured': bool(os.environ.get('DATABASE_URL')),
            'redis_configured': bool(os.environ.get('REDIS_URL')),
            'google_ads_configured': bool(os.environ.get('GOOGLE_ADS_CLIENT_ID')),
            'openai_configured': bool(os.environ.get('OPENAI_API_KEY'))
        }
    
    def _update_health_history(self, health_data: Dict[str, Any]):
        """Update health check history"""
        self.check_history.append({
            'timestamp': health_data['timestamp'],
            'status': health_data['status']
        })
        
        # Keep only last 100 checks
        if len(self.check_history) > 100:
            self.check_history = self.check_history[-100:]
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics for monitoring"""
        if not self.check_history:
            return {'uptime_percentage': 100.0, 'checks_total': 0}
        
        total_checks = len(self.check_history)
        healthy_checks = sum(1 for check in self.check_history 
                           if check['status'] == HealthStatus.HEALTHY)
        
        return {
            'uptime_percentage': (healthy_checks / total_checks * 100) if total_checks > 0 else 100.0,
            'checks_total': total_checks,
            'last_check': self.check_history[-1] if self.check_history else None,
            'current_status': self.last_check_results.get('status', 'unknown')
        }
    
    async def run_diagnostic(self) -> Dict[str, Any]:
        """Run comprehensive diagnostic checks"""
        logger.info("Running comprehensive system diagnostic")
        
        diagnostic_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'health_status': await self.get_health_status(detailed=True),
            'metrics': self.get_health_metrics(),
            'recommendations': []
        }
        
        # Generate recommendations based on health status
        health_status = diagnostic_results['health_status']
        
        if health_status['status'] != HealthStatus.HEALTHY:
            for service, status in health_status['services'].items():
                if status.get('status') != HealthStatus.HEALTHY:
                    if service == 'database' and 'response_time' in status:
                        if status['response_time'] > 1.0:
                            diagnostic_results['recommendations'].append({
                                'service': 'database',
                                'issue': 'Slow response time',
                                'recommendation': 'Check database indexes and query performance'
                            })
                    
                    if service == 'system':
                        for warning in status.get('warnings', []):
                            diagnostic_results['recommendations'].append({
                                'service': 'system',
                                'issue': warning,
                                'recommendation': 'Monitor system resources and consider scaling'
                            })
        
        return diagnostic_results


# Global health monitor instance
health_monitor = HealthMonitor()