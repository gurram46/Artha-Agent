"""Database Health Monitoring Module

Provides comprehensive database health monitoring and metrics collection
for the Artha AI backend system.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from .connection_manager import get_connection_manager
from .config import get_cache_stats, cleanup_expired_cache

logger = logging.getLogger(__name__)

@dataclass
class DatabaseMetrics:
    """Database performance and health metrics"""
    timestamp: str
    connection_pool: Dict[str, Any]
    cache_stats: Dict[str, Any]
    health_score: float
    response_time_ms: float
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]

class DatabaseHealthMonitor:
    """Comprehensive database health monitoring system"""
    
    def __init__(self):
        self.connection_manager = get_connection_manager()
        self.metrics_history: List[DatabaseMetrics] = []
        self.max_history_size = 100
        self.alert_thresholds = {
            'response_time_ms': 1000,  # 1 second
            'failed_connections_ratio': 0.1,  # 10%
            'pool_utilization': 0.8,  # 80%
            'retry_attempts_per_hour': 50
        }
    
    async def collect_metrics(self) -> DatabaseMetrics:
        """Collect comprehensive database metrics"""
        start_time = datetime.utcnow()
        errors = []
        warnings = []
        recommendations = []
        
        try:
            # Test connection and measure response time
            connection_start = datetime.utcnow()
            connection_healthy = self.connection_manager.test_connection()
            response_time = (datetime.utcnow() - connection_start).total_seconds() * 1000
            
            # Get connection pool status
            pool_status = self.connection_manager.get_pool_status()
            
            # Get cache statistics
            cache_stats = get_cache_stats()
            
            # Analyze metrics and generate insights
            health_score = self._calculate_health_score(
                connection_healthy, response_time, pool_status, cache_stats
            )
            
            # Generate warnings and recommendations
            warnings, recommendations = self._analyze_metrics(
                response_time, pool_status, cache_stats
            )
            
            if not connection_healthy:
                errors.append("Database connection test failed")
            
        except Exception as e:
            errors.append(f"Metrics collection failed: {str(e)}")
            logger.error(f"❌ Database metrics collection failed: {e}")
            
            # Fallback values
            response_time = 0
            pool_status = {}
            cache_stats = {}
            health_score = 0.0
        
        metrics = DatabaseMetrics(
            timestamp=start_time.isoformat(),
            connection_pool=pool_status,
            cache_stats=cache_stats,
            health_score=health_score,
            response_time_ms=response_time,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations
        )
        
        # Store in history
        self._store_metrics(metrics)
        
        return metrics
    
    def _calculate_health_score(self, connection_healthy: bool, response_time: float, 
                              pool_status: Dict, cache_stats: Dict) -> float:
        """Calculate overall database health score (0-100)"""
        score = 0.0
        
        # Connection health (40 points)
        if connection_healthy:
            score += 40
        
        # Response time (20 points)
        if response_time < self.alert_thresholds['response_time_ms']:
            score += 20
        elif response_time < self.alert_thresholds['response_time_ms'] * 2:
            score += 10
        
        # Pool utilization (20 points)
        if isinstance(pool_status, dict) and 'pool_size' in pool_status:
            pool_size = pool_status.get('pool_size', 1)
            checked_out = pool_status.get('checked_out', 0)
            if pool_size > 0:
                utilization = checked_out / pool_size
                if utilization < self.alert_thresholds['pool_utilization']:
                    score += 20
                elif utilization < self.alert_thresholds['pool_utilization'] * 1.2:
                    score += 10
        else:
            score += 15  # Partial score if pool info unavailable
        
        # Error rate (20 points)
        if isinstance(pool_status, dict):
            total_connections = pool_status.get('total_connections', 1)
            failed_connections = pool_status.get('failed_connections', 0)
            if total_connections > 0:
                error_rate = failed_connections / total_connections
                if error_rate < self.alert_thresholds['failed_connections_ratio']:
                    score += 20
                elif error_rate < self.alert_thresholds['failed_connections_ratio'] * 2:
                    score += 10
        else:
            score += 15  # Partial score if error info unavailable
        
        return min(100.0, max(0.0, score))
    
    def _analyze_metrics(self, response_time: float, pool_status: Dict, 
                        cache_stats: Dict) -> tuple[List[str], List[str]]:
        """Analyze metrics and generate warnings and recommendations"""
        warnings = []
        recommendations = []
        
        # Response time analysis
        if response_time > self.alert_thresholds['response_time_ms']:
            warnings.append(f"High database response time: {response_time:.2f}ms")
            recommendations.append("Consider optimizing database queries or increasing connection pool size")
        
        # Pool utilization analysis
        if isinstance(pool_status, dict) and 'pool_size' in pool_status:
            pool_size = pool_status.get('pool_size', 1)
            checked_out = pool_status.get('checked_out', 0)
            overflow = pool_status.get('overflow', 0)
            
            if pool_size > 0:
                utilization = checked_out / pool_size
                if utilization > self.alert_thresholds['pool_utilization']:
                    warnings.append(f"High connection pool utilization: {utilization:.1%}")
                    recommendations.append("Consider increasing connection pool size")
            
            if overflow > 0:
                warnings.append(f"Connection pool overflow detected: {overflow} connections")
                recommendations.append("Increase max_overflow setting or optimize connection usage")
        
        # Error rate analysis
        if isinstance(pool_status, dict):
            failed_connections = pool_status.get('failed_connections', 0)
            retry_attempts = pool_status.get('retry_attempts', 0)
            
            if failed_connections > 10:
                warnings.append(f"High number of failed connections: {failed_connections}")
                recommendations.append("Check database server health and network connectivity")
            
            if retry_attempts > self.alert_thresholds['retry_attempts_per_hour']:
                warnings.append(f"High number of retry attempts: {retry_attempts}")
                recommendations.append("Investigate database performance issues")
        
        # Cache analysis
        if isinstance(cache_stats, dict):
            expired_users = cache_stats.get('expired_users', 0)
            total_users = cache_stats.get('total_users', 0)
            
            if total_users > 0 and expired_users / total_users > 0.5:
                warnings.append(f"High cache expiration rate: {expired_users}/{total_users}")
                recommendations.append("Consider running cache cleanup more frequently")
        
        return warnings, recommendations
    
    def _store_metrics(self, metrics: DatabaseMetrics):
        """Store metrics in history with size limit"""
        self.metrics_history.append(metrics)
        
        # Maintain history size limit
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def get_metrics_history(self, hours: int = 24) -> List[DatabaseMetrics]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics.timestamp.replace('Z', '+00:00')) > cutoff_time
        ]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        if not self.metrics_history:
            return {
                'status': 'unknown',
                'message': 'No metrics available',
                'last_check': None
            }
        
        latest_metrics = self.metrics_history[-1]
        recent_metrics = self.get_metrics_history(1)  # Last hour
        
        # Calculate average health score
        if recent_metrics:
            avg_health_score = sum(m.health_score for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
        else:
            avg_health_score = latest_metrics.health_score
            avg_response_time = latest_metrics.response_time_ms
        
        # Determine overall status
        if avg_health_score >= 80:
            status = 'healthy'
            status_color = '🟢'
        elif avg_health_score >= 60:
            status = 'warning'
            status_color = '🟡'
        else:
            status = 'critical'
            status_color = '🔴'
        
        return {
            'status': status,
            'status_icon': status_color,
            'health_score': avg_health_score,
            'avg_response_time_ms': avg_response_time,
            'last_check': latest_metrics.timestamp,
            'active_warnings': len(latest_metrics.warnings),
            'active_errors': len(latest_metrics.errors),
            'recommendations_count': len(latest_metrics.recommendations),
            'metrics_collected': len(self.metrics_history),
            'connection_pool': latest_metrics.connection_pool,
            'cache_stats': latest_metrics.cache_stats
        }
    
    async def run_maintenance(self) -> Dict[str, Any]:
        """Run database maintenance tasks"""
        maintenance_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'tasks_completed': [],
            'errors': []
        }
        
        try:
            # Clean up expired cache entries
            cleaned_count = cleanup_expired_cache()
            maintenance_results['tasks_completed'].append(
                f"Cache cleanup: {cleaned_count} expired entries removed"
            )
        except Exception as e:
            maintenance_results['errors'].append(f"Cache cleanup failed: {str(e)}")
        
        try:
            # Test connection health
            connection_healthy = self.connection_manager.test_connection()
            if connection_healthy:
                maintenance_results['tasks_completed'].append("Connection health check: PASSED")
            else:
                maintenance_results['errors'].append("Connection health check: FAILED")
        except Exception as e:
            maintenance_results['errors'].append(f"Connection health check failed: {str(e)}")
        
        return maintenance_results

# Global health monitor instance
_health_monitor: Optional[DatabaseHealthMonitor] = None

def get_health_monitor() -> DatabaseHealthMonitor:
    """Get or create global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = DatabaseHealthMonitor()
    return _health_monitor

# Convenience functions
async def get_database_health() -> Dict[str, Any]:
    """Get current database health status"""
    monitor = get_health_monitor()
    metrics = await monitor.collect_metrics()
    return asdict(metrics)

async def get_database_summary() -> Dict[str, Any]:
    """Get database health summary"""
    monitor = get_health_monitor()
    await monitor.collect_metrics()  # Ensure we have recent data
    return monitor.get_health_summary()

async def run_database_maintenance() -> Dict[str, Any]:
    """Run database maintenance tasks"""
    monitor = get_health_monitor()
    return await monitor.run_maintenance()