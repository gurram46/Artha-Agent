"""System Monitoring and Health Metrics for Artha AI Backend

Provides comprehensive system monitoring including:
- System resource monitoring (CPU, memory, disk)
- Application performance metrics
- Health checks and status reporting
- Alert generation and notification
- Metrics collection and aggregation
"""

import os
import sys
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import logging
from pathlib import Path

# Import our logging configuration
try:
    from backend.config.logging_config import get_logger
    logger = get_logger('monitoring')
except ImportError:
    logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    load_average: List[float]

@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    timestamp: datetime
    active_connections: int
    request_count: int
    error_count: int
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    database_connections: int
    cache_hit_rate: float
    ai_requests_count: int
    websocket_connections: int

@dataclass
class HealthStatus:
    """Overall system health status"""
    timestamp: datetime
    status: str  # 'healthy', 'warning', 'critical'
    score: float  # 0-100
    components: Dict[str, Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    uptime_seconds: float

class MetricsCollector:
    """Collects and aggregates system and application metrics"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.metrics_history = deque(maxlen=1440)  # 24 hours of minute data
        self.app_metrics_history = deque(maxlen=1440)
        self.start_time = time.time()
        self.is_collecting = False
        self.collection_thread = None
        
        # Performance counters
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
        
        # Network baseline
        self.network_baseline = self._get_network_stats()
        
        logger.info("MetricsCollector initialized", extra={'collection_interval': collection_interval})
    
    def start_collection(self):
        """Start metrics collection in background thread"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
    
    def _collection_loop(self):
        """Main collection loop"""
        while self.is_collecting:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.metrics_history.append(system_metrics)
                
                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                self.app_metrics_history.append(app_metrics)
                
                # Log metrics periodically
                if len(self.metrics_history) % 5 == 0:  # Every 5 minutes
                    self._log_metrics_summary(system_metrics, app_metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}", exc_info=True)
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system resource metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = self._get_network_stats()
        
        # Process metrics
        process_count = len(psutil.pids())
        
        # Load average (Unix-like systems)
        try:
            load_avg = list(os.getloadavg())
        except (OSError, AttributeError):
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_percent=disk.percent,
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_free_gb=disk.free / (1024 * 1024 * 1024),
            network_bytes_sent=network['bytes_sent'] - self.network_baseline['bytes_sent'],
            network_bytes_recv=network['bytes_recv'] - self.network_baseline['bytes_recv'],
            process_count=process_count,
            load_average=load_avg
        )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific metrics"""
        # Calculate response time percentiles
        response_times = list(self.request_times)
        if response_times:
            response_times.sort()
            avg_time = sum(response_times) / len(response_times)
            p95_time = response_times[int(len(response_times) * 0.95)] if response_times else 0
            p99_time = response_times[int(len(response_times) * 0.99)] if response_times else 0
        else:
            avg_time = p95_time = p99_time = 0
        
        # Get total request and error counts
        total_requests = sum(stats['count'] for stats in self.endpoint_stats.values())
        total_errors = sum(self.error_counts.values())
        
        return ApplicationMetrics(
            timestamp=datetime.utcnow(),
            active_connections=0,  # Will be updated by connection manager
            request_count=total_requests,
            error_count=total_errors,
            response_time_avg=avg_time,
            response_time_p95=p95_time,
            response_time_p99=p99_time,
            database_connections=0,  # Will be updated by database manager
            cache_hit_rate=0.0,  # Will be updated by cache manager
            ai_requests_count=0,  # Will be updated by AI service
            websocket_connections=0  # Will be updated by WebSocket manager
        )
    
    def _get_network_stats(self) -> Dict[str, int]:
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception:
            return {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}
    
    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record API request metrics"""
        self.request_times.append(duration)
        
        endpoint_key = f"{method} {endpoint}"
        self.endpoint_stats[endpoint_key]['count'] += 1
        self.endpoint_stats[endpoint_key]['total_time'] += duration
        
        if status_code >= 400:
            self.endpoint_stats[endpoint_key]['errors'] += 1
            self.error_counts[str(status_code)] += 1
    
    def update_connection_count(self, count: int):
        """Update active connection count"""
        if self.app_metrics_history:
            self.app_metrics_history[-1].active_connections = count
    
    def update_database_connections(self, count: int):
        """Update database connection count"""
        if self.app_metrics_history:
            self.app_metrics_history[-1].database_connections = count
    
    def update_cache_hit_rate(self, rate: float):
        """Update cache hit rate"""
        if self.app_metrics_history:
            self.app_metrics_history[-1].cache_hit_rate = rate
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get the latest collected metrics"""
        system_metrics = self.metrics_history[-1] if self.metrics_history else None
        app_metrics = self.app_metrics_history[-1] if self.app_metrics_history else None
        
        return {
            'system': asdict(system_metrics) if system_metrics else None,
            'application': asdict(app_metrics) if app_metrics else None,
            'uptime_seconds': time.time() - self.start_time
        }
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter metrics by time
        recent_system = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        recent_app = [m for m in self.app_metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_system or not recent_app:
            return {'error': 'Insufficient data for summary'}
        
        # Calculate averages and peaks
        avg_cpu = sum(m.cpu_percent for m in recent_system) / len(recent_system)
        max_cpu = max(m.cpu_percent for m in recent_system)
        avg_memory = sum(m.memory_percent for m in recent_system) / len(recent_system)
        max_memory = max(m.memory_percent for m in recent_system)
        
        avg_response_time = sum(m.response_time_avg for m in recent_app) / len(recent_app)
        total_requests = sum(m.request_count for m in recent_app)
        total_errors = sum(m.error_count for m in recent_app)
        
        return {
            'period_hours': hours,
            'data_points': len(recent_system),
            'cpu': {'average': avg_cpu, 'peak': max_cpu},
            'memory': {'average': avg_memory, 'peak': max_memory},
            'requests': {'total': total_requests, 'errors': total_errors},
            'response_time_avg': avg_response_time,
            'error_rate': (total_errors / total_requests * 100) if total_requests > 0 else 0
        }
    
    def _log_metrics_summary(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Log periodic metrics summary"""
        logger.info(
            "System metrics summary",
            extra={
                'event_type': 'metrics_summary',
                'cpu_percent': system_metrics.cpu_percent,
                'memory_percent': system_metrics.memory_percent,
                'disk_percent': system_metrics.disk_percent,
                'request_count': app_metrics.request_count,
                'error_count': app_metrics.error_count,
                'response_time_avg': app_metrics.response_time_avg,
                'uptime_hours': (time.time() - self.start_time) / 3600
            }
        )

class HealthChecker:
    """System health monitoring and alerting"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_thresholds = {
            'cpu_critical': float(os.getenv('ALERT_CPU_CRITICAL', '90')),
            'cpu_warning': float(os.getenv('ALERT_CPU_WARNING', '75')),
            'memory_critical': float(os.getenv('ALERT_MEMORY_CRITICAL', '90')),
            'memory_warning': float(os.getenv('ALERT_MEMORY_WARNING', '80')),
            'disk_critical': float(os.getenv('ALERT_DISK_CRITICAL', '95')),
            'disk_warning': float(os.getenv('ALERT_DISK_WARNING', '85')),
            'response_time_critical': float(os.getenv('ALERT_RESPONSE_TIME_CRITICAL', '5.0')),
            'response_time_warning': float(os.getenv('ALERT_RESPONSE_TIME_WARNING', '2.0')),
            'error_rate_critical': float(os.getenv('ALERT_ERROR_RATE_CRITICAL', '10')),
            'error_rate_warning': float(os.getenv('ALERT_ERROR_RATE_WARNING', '5'))
        }
        
        self.alert_callbacks: List[Callable] = []
        logger.info("HealthChecker initialized", extra={'thresholds': self.alert_thresholds})
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def check_health(self) -> HealthStatus:
        """Perform comprehensive health check"""
        latest_metrics = self.metrics_collector.get_latest_metrics()
        
        if not latest_metrics['system'] or not latest_metrics['application']:
            return HealthStatus(
                timestamp=datetime.utcnow(),
                status='unknown',
                score=0,
                components={},
                alerts=[{'type': 'error', 'message': 'Insufficient metrics data'}],
                uptime_seconds=latest_metrics['uptime_seconds']
            )
        
        system = latest_metrics['system']
        app = latest_metrics['application']
        
        # Check individual components
        components = {
            'cpu': self._check_cpu(system['cpu_percent']),
            'memory': self._check_memory(system['memory_percent']),
            'disk': self._check_disk(system['disk_percent']),
            'response_time': self._check_response_time(app['response_time_avg']),
            'error_rate': self._check_error_rate(app['request_count'], app['error_count'])
        }
        
        # Calculate overall health score and status
        scores = [comp['score'] for comp in components.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Determine overall status
        if overall_score >= 80:
            status = 'healthy'
        elif overall_score >= 60:
            status = 'warning'
        else:
            status = 'critical'
        
        # Collect alerts
        alerts = []
        for comp_name, comp_data in components.items():
            if comp_data['alerts']:
                alerts.extend(comp_data['alerts'])
        
        # Send alerts if any
        if alerts:
            self._send_alerts(alerts)
        
        health_status = HealthStatus(
            timestamp=datetime.utcnow(),
            status=status,
            score=overall_score,
            components=components,
            alerts=alerts,
            uptime_seconds=latest_metrics['uptime_seconds']
        )
        
        # Log health status
        logger.info(
            f"Health check completed: {status}",
            extra={
                'event_type': 'health_check',
                'status': status,
                'score': overall_score,
                'alert_count': len(alerts)
            }
        )
        
        return health_status
    
    def _check_cpu(self, cpu_percent: float) -> Dict[str, Any]:
        """Check CPU usage"""
        alerts = []
        if cpu_percent >= self.alert_thresholds['cpu_critical']:
            status = 'critical'
            score = 0
            alerts.append({'type': 'critical', 'component': 'cpu', 'message': f'CPU usage critical: {cpu_percent:.1f}%'})
        elif cpu_percent >= self.alert_thresholds['cpu_warning']:
            status = 'warning'
            score = 50
            alerts.append({'type': 'warning', 'component': 'cpu', 'message': f'CPU usage high: {cpu_percent:.1f}%'})
        else:
            status = 'healthy'
            score = 100 - cpu_percent
        
        return {
            'status': status,
            'score': score,
            'value': cpu_percent,
            'unit': '%',
            'alerts': alerts
        }
    
    def _check_memory(self, memory_percent: float) -> Dict[str, Any]:
        """Check memory usage"""
        alerts = []
        if memory_percent >= self.alert_thresholds['memory_critical']:
            status = 'critical'
            score = 0
            alerts.append({'type': 'critical', 'component': 'memory', 'message': f'Memory usage critical: {memory_percent:.1f}%'})
        elif memory_percent >= self.alert_thresholds['memory_warning']:
            status = 'warning'
            score = 50
            alerts.append({'type': 'warning', 'component': 'memory', 'message': f'Memory usage high: {memory_percent:.1f}%'})
        else:
            status = 'healthy'
            score = 100 - memory_percent
        
        return {
            'status': status,
            'score': score,
            'value': memory_percent,
            'unit': '%',
            'alerts': alerts
        }
    
    def _check_disk(self, disk_percent: float) -> Dict[str, Any]:
        """Check disk usage"""
        alerts = []
        if disk_percent >= self.alert_thresholds['disk_critical']:
            status = 'critical'
            score = 0
            alerts.append({'type': 'critical', 'component': 'disk', 'message': f'Disk usage critical: {disk_percent:.1f}%'})
        elif disk_percent >= self.alert_thresholds['disk_warning']:
            status = 'warning'
            score = 50
            alerts.append({'type': 'warning', 'component': 'disk', 'message': f'Disk usage high: {disk_percent:.1f}%'})
        else:
            status = 'healthy'
            score = 100 - disk_percent
        
        return {
            'status': status,
            'score': score,
            'value': disk_percent,
            'unit': '%',
            'alerts': alerts
        }
    
    def _check_response_time(self, avg_response_time: float) -> Dict[str, Any]:
        """Check average response time"""
        alerts = []
        if avg_response_time >= self.alert_thresholds['response_time_critical']:
            status = 'critical'
            score = 0
            alerts.append({'type': 'critical', 'component': 'response_time', 'message': f'Response time critical: {avg_response_time:.2f}s'})
        elif avg_response_time >= self.alert_thresholds['response_time_warning']:
            status = 'warning'
            score = 50
            alerts.append({'type': 'warning', 'component': 'response_time', 'message': f'Response time high: {avg_response_time:.2f}s'})
        else:
            status = 'healthy'
            score = max(0, 100 - (avg_response_time * 20))  # Scale response time to score
        
        return {
            'status': status,
            'score': score,
            'value': avg_response_time,
            'unit': 'seconds',
            'alerts': alerts
        }
    
    def _check_error_rate(self, request_count: int, error_count: int) -> Dict[str, Any]:
        """Check error rate"""
        error_rate = (error_count / request_count * 100) if request_count > 0 else 0
        alerts = []
        
        if error_rate >= self.alert_thresholds['error_rate_critical']:
            status = 'critical'
            score = 0
            alerts.append({'type': 'critical', 'component': 'error_rate', 'message': f'Error rate critical: {error_rate:.1f}%'})
        elif error_rate >= self.alert_thresholds['error_rate_warning']:
            status = 'warning'
            score = 50
            alerts.append({'type': 'warning', 'component': 'error_rate', 'message': f'Error rate high: {error_rate:.1f}%'})
        else:
            status = 'healthy'
            score = max(0, 100 - (error_rate * 10))  # Scale error rate to score
        
        return {
            'status': status,
            'score': score,
            'value': error_rate,
            'unit': '%',
            'alerts': alerts
        }
    
    def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send alerts through registered callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alerts)
            except Exception as e:
                logger.error(f"Error sending alert: {e}", exc_info=True)

# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker(metrics_collector)

def start_monitoring():
    """Start the monitoring system"""
    metrics_collector.start_collection()
    logger.info("System monitoring started")

def stop_monitoring():
    """Stop the monitoring system"""
    metrics_collector.stop_collection()
    logger.info("System monitoring stopped")

def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    health_status = health_checker.check_health()
    return asdict(health_status)

def get_metrics_dashboard() -> Dict[str, Any]:
    """Get comprehensive metrics for dashboard"""
    latest_metrics = metrics_collector.get_latest_metrics()
    summary_1h = metrics_collector.get_metrics_summary(hours=1)
    summary_24h = metrics_collector.get_metrics_summary(hours=24)
    health_status = health_checker.check_health()
    
    return {
        'current': latest_metrics,
        'summary_1h': summary_1h,
        'summary_24h': summary_24h,
        'health': asdict(health_status),
        'timestamp': datetime.utcnow().isoformat()
    }

# Export main components
__all__ = [
    'SystemMetrics',
    'ApplicationMetrics',
    'HealthStatus',
    'MetricsCollector',
    'HealthChecker',
    'metrics_collector',
    'health_checker',
    'start_monitoring',
    'stop_monitoring',
    'get_system_status',
    'get_metrics_dashboard'
]