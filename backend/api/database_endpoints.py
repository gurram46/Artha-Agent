"""Database Health Monitoring API Endpoints for Artha AI
======================================================

FastAPI endpoints for monitoring database health, connection pool status, and performance metrics.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from database.connection_manager import get_connection_manager
from database.health_monitor import DatabaseHealthMonitor
from api.auth_endpoints import get_current_user

logger = logging.getLogger(__name__)

# Initialize services
connection_manager = get_connection_manager()
health_monitor = DatabaseHealthMonitor()
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/database", tags=["database-health"])

# Pydantic models for response
class DatabaseHealthResponse(BaseModel):
    """Database health status response"""
    status: str
    health_score: float
    timestamp: datetime
    connection_pool: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]

class ConnectionPoolResponse(BaseModel):
    """Connection pool status response"""
    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    invalid: int
    utilization_percent: float
    status: str

class PerformanceMetricsResponse(BaseModel):
    """Database performance metrics response"""
    avg_response_time_ms: float
    total_queries: int
    successful_queries: int
    failed_queries: int
    success_rate_percent: float
    error_rate_percent: float
    uptime_hours: float

@router.get("/health", response_model=DatabaseHealthResponse)
async def get_database_health(
    include_recommendations: bool = True,
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """
    Get comprehensive database health status
    
    Returns:
        DatabaseHealthResponse: Complete health status with metrics and recommendations
    """
    try:
        health_data = await health_monitor.get_health_status()
        
        response_data = {
            "status": health_data["status"],
            "health_score": health_data["health_score"],
            "timestamp": datetime.now(),
            "connection_pool": health_data["connection_pool"],
            "performance_metrics": health_data["performance_metrics"],
            "recommendations": health_data.get("recommendations", []) if include_recommendations else []
        }
        
        logger.info(f"Database health check completed - Score: {health_data['health_score']:.2f}")
        return DatabaseHealthResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Failed to get database health status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve database health status: {str(e)}"
        )

@router.get("/connection-pool", response_model=ConnectionPoolResponse)
async def get_connection_pool_status(
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """
    Get current connection pool status
    
    Returns:
        ConnectionPoolResponse: Connection pool utilization and status
    """
    try:
        pool_stats = connection_manager.get_pool_stats()
        
        # Calculate utilization percentage
        total_connections = pool_stats["pool_size"] + pool_stats["overflow"]
        active_connections = pool_stats["checked_out"]
        utilization = (active_connections / total_connections * 100) if total_connections > 0 else 0
        
        # Determine status based on utilization
        if utilization < 50:
            pool_status = "healthy"
        elif utilization < 80:
            pool_status = "moderate"
        else:
            pool_status = "high_utilization"
        
        response_data = {
            "pool_size": pool_stats["pool_size"],
            "checked_in": pool_stats["checked_in"],
            "checked_out": pool_stats["checked_out"],
            "overflow": pool_stats["overflow"],
            "invalid": pool_stats["invalid"],
            "utilization_percent": round(utilization, 2),
            "status": pool_status
        }
        
        logger.info(f"Connection pool status: {utilization:.1f}% utilization")
        return ConnectionPoolResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Failed to get connection pool status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve connection pool status: {str(e)}"
        )

@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """
    Get database performance metrics
    
    Returns:
        PerformanceMetricsResponse: Performance statistics and metrics
    """
    try:
        metrics = health_monitor.get_performance_metrics()
        
        # Calculate derived metrics
        total_queries = metrics["successful_queries"] + metrics["failed_queries"]
        success_rate = (metrics["successful_queries"] / total_queries * 100) if total_queries > 0 else 100
        error_rate = (metrics["failed_queries"] / total_queries * 100) if total_queries > 0 else 0
        
        response_data = {
            "avg_response_time_ms": round(metrics["avg_response_time"] * 1000, 2),
            "total_queries": total_queries,
            "successful_queries": metrics["successful_queries"],
            "failed_queries": metrics["failed_queries"],
            "success_rate_percent": round(success_rate, 2),
            "error_rate_percent": round(error_rate, 2),
            "uptime_hours": round(metrics["uptime_seconds"] / 3600, 2)
        }
        
        logger.info(f"Performance metrics: {success_rate:.1f}% success rate, {metrics['avg_response_time']*1000:.1f}ms avg response")
        return PerformanceMetricsResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance metrics: {str(e)}"
        )

@router.post("/maintenance/cleanup-cache")
async def cleanup_expired_cache(
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """
    Trigger cleanup of expired cache entries
    
    Returns:
        Dict: Cleanup results and statistics
    """
    try:
        result = await health_monitor.cleanup_expired_cache()
        
        logger.info(f"Cache cleanup completed: {result['deleted_count']} entries removed")
        return {
            "status": "success",
            "message": "Cache cleanup completed successfully",
            "deleted_count": result["deleted_count"],
            "cleanup_time_ms": round(result["cleanup_time"] * 1000, 2),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup expired cache: {str(e)}"
        )

@router.get("/status")
async def get_database_status():
    """
    Simple database connectivity check (no authentication required)
    
    Returns:
        Dict: Basic database status
    """
    try:
        # Test basic connectivity
        is_connected = await connection_manager.test_connection()
        
        if is_connected:
            return {
                "status": "connected",
                "message": "Database is accessible",
                "timestamp": datetime.now()
            }
        else:
            return {
                "status": "disconnected",
                "message": "Database connection failed",
                "timestamp": datetime.now()
            }
            
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return {
            "status": "error",
            "message": f"Database status check failed: {str(e)}",
            "timestamp": datetime.now()
        }