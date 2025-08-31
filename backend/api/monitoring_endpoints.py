"""Monitoring and Health Check API Endpoints for Artha AI Backend

Provides REST API endpoints for:
- System health status
- Performance metrics
- Resource monitoring
- Alert management
- Diagnostic information
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

# Import monitoring components
try:
    from backend.monitoring.system_monitor import (
        metrics_collector,
        health_checker,
        get_system_status,
        get_metrics_dashboard,
        start_monitoring,
        stop_monitoring
    )
    from backend.config.logging_config import get_logger, performance_logger, security_logger
    from backend.services.chat_service import ChatService
    logger = get_logger('api.monitoring')
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import monitoring components: {e}")

# Initialize chat service for monitoring
try:
    chat_service = ChatService()
except Exception as e:
    chat_service = None
    logger.warning(f"Chat service not available for monitoring: {e}")

# Pydantic models for API responses
class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Overall health status: healthy, warning, critical")
    score: float = Field(..., description="Health score from 0-100")
    timestamp: datetime = Field(..., description="Timestamp of health check")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    components: Dict[str, Any] = Field(..., description="Individual component health status")
    alerts: List[Dict[str, Any]] = Field(..., description="Active alerts")

class MetricsResponse(BaseModel):
    """Metrics response model"""
    timestamp: datetime = Field(..., description="Timestamp of metrics collection")
    system: Dict[str, Any] = Field(..., description="System resource metrics")
    application: Dict[str, Any] = Field(..., description="Application performance metrics")
    uptime_seconds: float = Field(..., description="System uptime in seconds")

class MetricsSummaryResponse(BaseModel):
    """Metrics summary response model"""
    period_hours: int = Field(..., description="Time period for summary in hours")
    data_points: int = Field(..., description="Number of data points in summary")
    cpu: Dict[str, float] = Field(..., description="CPU usage statistics")
    memory: Dict[str, float] = Field(..., description="Memory usage statistics")
    requests: Dict[str, int] = Field(..., description="Request statistics")
    response_time_avg: float = Field(..., description="Average response time")
    error_rate: float = Field(..., description="Error rate percentage")

class DashboardResponse(BaseModel):
    """Dashboard data response model"""
    current: Dict[str, Any] = Field(..., description="Current metrics")
    summary_1h: Dict[str, Any] = Field(..., description="1-hour summary")
    summary_24h: Dict[str, Any] = Field(..., description="24-hour summary")
    health: Dict[str, Any] = Field(..., description="Health status")
    timestamp: str = Field(..., description="Response timestamp")

class AlertResponse(BaseModel):
    """Alert response model"""
    alerts: List[Dict[str, Any]] = Field(..., description="List of active alerts")
    count: int = Field(..., description="Total number of alerts")
    critical_count: int = Field(..., description="Number of critical alerts")
    warning_count: int = Field(..., description="Number of warning alerts")

# Create router
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Dependency for API key authentication (optional)
def verify_monitoring_access(api_key: Optional[str] = Query(None, alias="api_key")):
    """Verify access to monitoring endpoints"""
    monitoring_api_key = os.getenv('MONITORING_API_KEY')
    
    # If no API key is configured, allow access
    if not monitoring_api_key:
        return True
    
    # If API key is configured, require it
    if not api_key or api_key != monitoring_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing monitoring API key"
        )
    
    return True

@monitoring_router.get("/health", response_model=HealthResponse)
async def get_health_status(authorized: bool = Depends(verify_monitoring_access)):
    """Get comprehensive system health status
    
    Returns overall system health including:
    - System resource status (CPU, memory, disk)
    - Application performance metrics
    - Component-level health checks
    - Active alerts and warnings
    """
    try:
        start_time = time.time()
        health_status = get_system_status()
        duration = time.time() - start_time
        
        # Log performance
        performance_logger.log_request_time(
            endpoint="/monitoring/health",
            method="GET",
            duration=duration,
            status_code=200
        )
        
        return HealthResponse(**health_status)
        
    except Exception as e:
        logger.error(f"Error getting health status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve health status: {str(e)}"
        )

@monitoring_router.get("/health/simple")
async def get_simple_health():
    """Simple health check endpoint for load balancers
    
    Returns basic OK/ERROR status without detailed metrics
    """
    try:
        health_status = health_checker.check_health()
        
        if health_status.status in ['healthy', 'warning']:
            return {"status": "OK", "timestamp": datetime.utcnow().isoformat()}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "ERROR", "timestamp": datetime.utcnow().isoformat()}
            )
            
    except Exception as e:
        logger.error(f"Error in simple health check: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={"status": "ERROR", "error": str(e), "timestamp": datetime.utcnow().isoformat()}
        )

@monitoring_router.get("/metrics", response_model=MetricsResponse)
async def get_current_metrics(authorized: bool = Depends(verify_monitoring_access)):
    """Get current system and application metrics
    
    Returns real-time metrics including:
    - System resource usage (CPU, memory, disk, network)
    - Application performance (response times, request counts)
    - Database and cache statistics
    """
    try:
        start_time = time.time()
        metrics = metrics_collector.get_latest_metrics()
        duration = time.time() - start_time
        
        if not metrics['system'] or not metrics['application']:
            raise HTTPException(
                status_code=503,
                detail="Metrics collection not available or insufficient data"
            )
        
        # Log performance
        performance_logger.log_request_time(
            endpoint="/monitoring/metrics",
            method="GET",
            duration=duration,
            status_code=200
        )
        
        return MetricsResponse(
            timestamp=datetime.utcnow(),
            system=metrics['system'],
            application=metrics['application'],
            uptime_seconds=metrics['uptime_seconds']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )

@monitoring_router.get("/metrics/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary(
    hours: int = Query(1, ge=1, le=24, description="Time period in hours (1-24)"),
    authorized: bool = Depends(verify_monitoring_access)
):
    """Get metrics summary for specified time period
    
    Returns aggregated metrics including:
    - Average and peak resource usage
    - Request and error statistics
    - Performance trends
    """
    try:
        start_time = time.time()
        summary = metrics_collector.get_metrics_summary(hours=hours)
        duration = time.time() - start_time
        
        if 'error' in summary:
            raise HTTPException(
                status_code=503,
                detail=summary['error']
            )
        
        # Log performance
        performance_logger.log_request_time(
            endpoint="/monitoring/metrics/summary",
            method="GET",
            duration=duration,
            status_code=200
        )
        
        return MetricsSummaryResponse(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics summary: {str(e)}"
        )

@monitoring_router.get("/dashboard", response_model=DashboardResponse)
async def get_monitoring_dashboard(authorized: bool = Depends(verify_monitoring_access)):
    """Get comprehensive monitoring dashboard data
    
    Returns complete monitoring data including:
    - Current metrics and health status
    - Short-term and long-term summaries
    - Trend analysis and alerts
    """
    try:
        start_time = time.time()
        dashboard_data = get_metrics_dashboard()
        duration = time.time() - start_time
        
        # Log performance
        performance_logger.log_request_time(
            endpoint="/monitoring/dashboard",
            method="GET",
            duration=duration,
            status_code=200
        )
        
        return DashboardResponse(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )

@monitoring_router.get("/alerts", response_model=AlertResponse)
async def get_active_alerts(authorized: bool = Depends(verify_monitoring_access)):
    """Get current active alerts
    
    Returns all active system alerts including:
    - Critical alerts requiring immediate attention
    - Warning alerts for monitoring
    - Alert counts and summaries
    """
    try:
        start_time = time.time()
        health_status = health_checker.check_health()
        alerts = health_status.alerts
        duration = time.time() - start_time
        
        # Count alerts by type
        critical_count = sum(1 for alert in alerts if alert.get('type') == 'critical')
        warning_count = sum(1 for alert in alerts if alert.get('type') == 'warning')
        
        # Log performance
        performance_logger.log_request_time(
            endpoint="/monitoring/alerts",
            method="GET",
            duration=duration,
            status_code=200
        )
        
        return AlertResponse(
            alerts=alerts,
            count=len(alerts),
            critical_count=critical_count,
            warning_count=warning_count
        )
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )

@monitoring_router.get("/system-info")
async def get_system_info(authorized: bool = Depends(verify_monitoring_access)):
    """Get system information and configuration
    
    Returns system details including:
    - Python version and platform
    - Environment configuration
    - Process information
    - Startup time and uptime
    """
    try:
        import platform
        import psutil
        
        start_time = time.time()
        
        # Get system information
        system_info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': sys.version,
                'python_executable': sys.executable
            },
            'process': {
                'pid': os.getpid(),
                'parent_pid': os.getppid(),
                'working_directory': os.getcwd(),
                'command_line': ' '.join(sys.argv)
            },
            'environment': {
                'node_env': os.getenv('NODE_ENV', 'development'),
                'debug_mode': os.getenv('DEBUG', 'false').lower() == 'true',
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'monitoring_enabled': True
            },
            'uptime': {
                'seconds': metrics_collector.start_time and (time.time() - metrics_collector.start_time) or 0,
                'started_at': datetime.fromtimestamp(metrics_collector.start_time).isoformat() if metrics_collector.start_time else None
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        duration = time.time() - start_time
        
        # Log performance
        performance_logger.log_request_time(
            endpoint="/monitoring/system-info",
            method="GET",
            duration=duration,
            status_code=200
        )
        
        return system_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system information: {str(e)}"
        )

@monitoring_router.post("/control/start")
async def start_monitoring_collection(
    background_tasks: BackgroundTasks,
    authorized: bool = Depends(verify_monitoring_access)
):
    """Start metrics collection
    
    Starts the background metrics collection process
    """
    try:
        if metrics_collector.is_collecting:
            return {"message": "Monitoring is already running", "status": "running"}
        
        background_tasks.add_task(start_monitoring)
        
        logger.info("Monitoring collection started via API")
        return {"message": "Monitoring collection started", "status": "started"}
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start monitoring: {str(e)}"
        )

@monitoring_router.post("/control/stop")
async def stop_monitoring_collection(
    background_tasks: BackgroundTasks,
    authorized: bool = Depends(verify_monitoring_access)
):
    """Stop metrics collection
    
    Stops the background metrics collection process
    """
    try:
        if not metrics_collector.is_collecting:
            return {"message": "Monitoring is not running", "status": "stopped"}
        
        background_tasks.add_task(stop_monitoring)
        
        logger.info("Monitoring collection stopped via API")
        return {"message": "Monitoring collection stopped", "status": "stopped"}
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop monitoring: {str(e)}"
        )

@monitoring_router.get("/control/status")
async def get_monitoring_status(authorized: bool = Depends(verify_monitoring_access)):
    """Get monitoring system status
    
    Returns the current status of the monitoring system
    """
    try:
        return {
            'monitoring_active': metrics_collector.is_collecting,
            'collection_interval': metrics_collector.collection_interval,
            'metrics_history_size': len(metrics_collector.metrics_history),
            'app_metrics_history_size': len(metrics_collector.app_metrics_history),
            'uptime_seconds': time.time() - metrics_collector.start_time if metrics_collector.start_time else 0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve monitoring status: {str(e)}"
        )

# Error handlers
# Note: APIRouter doesn't support exception_handler decorator
# @monitoring_router.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     """Handle HTTP exceptions for monitoring endpoints"""
#     logger.warning(
#         f"HTTP exception in monitoring endpoint: {exc.status_code} - {exc.detail}",
#         extra={
#             'event_type': 'http_error',
#             'status_code': exc.status_code,
#             'endpoint': str(request.url),
#             'method': request.method
#         }
#     )
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             'error': exc.detail,
#             'status_code': exc.status_code,
#             'timestamp': datetime.utcnow().isoformat()
#         }
#     )

@monitoring_router.get("/chat-service/stats", response_model=Dict[str, Any])
async def get_chat_service_stats():
    """Get chat service performance and cache statistics"""
    try:
        if not chat_service:
            raise HTTPException(
                status_code=503,
                detail="Chat service not available"
            )
        
        # Get cache statistics
        cache_stats = chat_service.get_cache_stats()
        
        # Get database connection info
        db_stats = {
            'pool_size': chat_service.engine.pool.size(),
            'checked_in': chat_service.engine.pool.checkedin(),
            'checked_out': chat_service.engine.pool.checkedout(),
            'overflow': chat_service.engine.pool.overflow(),
            'invalid': chat_service.engine.pool.invalid()
        }
        
        # Clear expired cache entries
        chat_service.clear_expired_cache()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'cache': cache_stats,
            'database_pool': db_stats,
            'performance': {
                'cache_hit_potential': 'high' if cache_stats['conversation_cache_size'] > 0 else 'low',
                'memory_usage': 'optimized'
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat service stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat service statistics: {str(e)}"
        )

@monitoring_router.post("/chat-service/cache/clear")
async def clear_chat_cache():
    """Clear chat service cache manually"""
    try:
        if not chat_service:
            raise HTTPException(
                status_code=503,
                detail="Chat service not available"
            )
        
        # Get stats before clearing
        before_stats = chat_service.get_cache_stats()
        
        # Clear all cache
        chat_service._conversation_cache.clear()
        chat_service._user_conversations_cache.clear()
        
        # Get stats after clearing
        after_stats = chat_service.get_cache_stats()
        
        logger.info("Chat service cache cleared manually")
        
        return {
            'status': 'success',
            'message': 'Chat service cache cleared',
            'timestamp': datetime.utcnow().isoformat(),
            'before': before_stats,
            'after': after_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to clear chat cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat service cache: {str(e)}"
        )

# Initialize monitoring on module import
try:
    if not metrics_collector.is_collecting:
        start_monitoring()
        logger.info("Monitoring system auto-started")
except Exception as e:
    logger.error(f"Failed to auto-start monitoring: {e}", exc_info=True)

# Export router
__all__ = ['monitoring_router']