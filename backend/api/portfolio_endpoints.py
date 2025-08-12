"""
Portfolio Analytics and Export API Endpoints for Artha AI
========================================================

Advanced portfolio management with historical tracking, analytics, and export functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, date
import json
import io

from services.portfolio_service import get_portfolio_service, PortfolioService
from api.auth_endpoints import get_current_user

logger = logging.getLogger(__name__)

# Initialize services
portfolio_service = get_portfolio_service()
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Pydantic models for request/response
class PortfolioSnapshotRequest(BaseModel):
    portfolio_data: Dict[str, Any] = Field(..., description="Portfolio data to store")
    data_source: Optional[str] = Field("fi_mcp", description="Data source identifier")

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/snapshot", response_model=StandardResponse)
async def store_portfolio_snapshot(
    request: PortfolioSnapshotRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Store daily portfolio snapshot for historical tracking
    """
    try:
        logger.info(f"📊 Storing portfolio snapshot for user: {current_user['id']}")
        
        result = portfolio_service.store_portfolio_snapshot(
            current_user['id'], 
            request.portfolio_data, 
            request.data_source
        )
        
        if result['success']:
            return StandardResponse(
                success=True,
                message=result['message']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Store snapshot endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store portfolio snapshot"
        )

@router.get("/history")
async def get_portfolio_history(
    days: int = Query(30, ge=1, le=730, description="Number of days of history to retrieve"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get portfolio history for specified number of days with summary statistics
    """
    try:
        logger.info(f"📈 Getting {days} days portfolio history for user: {current_user['id']}")
        
        result = portfolio_service.get_portfolio_history(current_user['id'], days)
        
        if result['success']:
            return {
                "success": True,
                "history": result['history'],
                "summary": result.get('summary', {}),
                "period_days": days
            }
        else:
            return {
                "success": False,
                "message": result['message'],
                "history": [],
                "summary": {}
            }
            
    except Exception as e:
        logger.error(f"❌ Get history endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio history"
        )

@router.get("/analytics")
async def get_portfolio_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive portfolio analytics with risk metrics, trends, and insights
    """
    try:
        logger.info(f"🔍 Getting portfolio analytics for user: {current_user['id']}")
        
        result = portfolio_service.get_detailed_analytics(current_user['id'])
        
        if result['success']:
            return {
                "success": True,
                "analytics": result['analytics'],
                "insights": result['insights'],
                "data_period": result['data_period'],
                "total_snapshots": result['total_snapshots']
            }
        else:
            return {
                "success": False,
                "message": result['message'],
                "analytics": {},
                "insights": []
            }
            
    except Exception as e:
        logger.error(f"❌ Get analytics endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio analytics"
        )

@router.get("/insights")
async def get_portfolio_insights(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get personalized portfolio insights and recommendations
    """
    try:
        logger.info(f"💡 Getting portfolio insights for user: {current_user['id']}")
        
        result = portfolio_service.get_detailed_analytics(current_user['id'])
        
        if result['success']:
            insights = result.get('insights', [])
            
            # Categorize insights
            categorized = {
                'high_priority': [i for i in insights if i.get('priority') == 'high'],
                'medium_priority': [i for i in insights if i.get('priority') == 'medium'],
                'low_priority': [i for i in insights if i.get('priority') == 'low'],
                'by_category': {}
            }
            
            # Group by category
            for insight in insights:
                category = insight.get('category', 'general')
                if category not in categorized['by_category']:
                    categorized['by_category'][category] = []
                categorized['by_category'][category].append(insight)
            
            return {
                "success": True,
                "insights": categorized,
                "total_insights": len(insights),
                "last_updated": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "message": result['message'],
                "insights": {
                    'high_priority': [],
                    'medium_priority': [],
                    'low_priority': [],
                    'by_category': {}
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Get insights endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio insights"
        )

@router.get("/performance")
async def get_portfolio_performance(
    period: str = Query("30d", description="Performance period: 7d, 30d, 90d, 1y"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get portfolio performance metrics for specified period
    """
    try:
        logger.info(f"📊 Getting portfolio performance for user: {current_user['id']} - Period: {period}")
        
        # Map period to days
        period_days = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }
        
        days = period_days.get(period, 30)
        
        # Get history and analytics
        history_result = portfolio_service.get_portfolio_history(current_user['id'], days)
        analytics_result = portfolio_service.get_detailed_analytics(current_user['id'])
        
        performance_data = {
            "period": period,
            "period_days": days
        }
        
        if history_result['success']:
            performance_data.update(history_result.get('summary', {}))
        
        if analytics_result['success']:
            analytics = analytics_result.get('analytics', {})
            
            # Extract key performance metrics
            if 'growth' in analytics:
                performance_data['growth_metrics'] = analytics['growth']
            
            if 'risk' in analytics:
                performance_data['risk_metrics'] = analytics['risk']
            
            if 'benchmarks' in analytics:
                performance_data['benchmarks'] = analytics['benchmarks']
            
            if 'trends' in analytics:
                performance_data['trends'] = analytics['trends']
        
        return {
            "success": True,
            "performance": performance_data
        }
            
    except Exception as e:
        logger.error(f"❌ Get performance endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio performance"
        )

@router.get("/export")
async def export_portfolio_data(
    format: str = Query("json", description="Export format: json, csv, pdf"),
    days: int = Query(365, ge=30, le=1095, description="Number of days to export"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export comprehensive portfolio data in specified format
    """
    try:
        logger.info(f"📤 Exporting portfolio data for user: {current_user['id']} - Format: {format}, Days: {days}")
        
        result = portfolio_service.export_portfolio_data(current_user['id'], format, days)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
        
        export_data = result['data']
        export_format = result['format']
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_export_{timestamp}.{export_format}"
        
        if export_format == 'csv':
            # Return CSV as streaming response
            def generate_csv():
                yield export_data.encode('utf-8')
            
            return StreamingResponse(
                generate_csv(),
                media_type='text/csv',
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        elif export_format == 'pdf':
            # Generate PDF report
            from services.pdf_service import get_pdf_service
            
            pdf_service = get_pdf_service()
            
            # Get additional data for PDF
            history_result = portfolio_service.get_portfolio_history(current_user['id'], days)
            analytics_result = portfolio_service.get_detailed_analytics(current_user['id'])
            
            # Prepare data for PDF generation
            portfolio_data = export_data
            analytics_data = analytics_result.get('analytics', {}) if analytics_result['success'] else {}
            user_data = {'name': current_user.get('email', 'User')}
            
            # Generate PDF
            pdf_bytes = pdf_service.generate_portfolio_report(user_data, portfolio_data, analytics_data)
            
            def generate_pdf():
                yield pdf_bytes
            
            return StreamingResponse(
                generate_pdf(),
                media_type='application/pdf',
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            # Return JSON
            json_content = json.dumps(export_data, indent=2)
            
            def generate_json():
                yield json_content.encode('utf-8')
            
            return StreamingResponse(
                generate_json(),
                media_type='application/json',
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Export data endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export portfolio data"
        )

@router.get("/summary")
async def get_portfolio_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get portfolio summary with key metrics and recent performance
    """
    try:
        logger.info(f"📋 Getting portfolio summary for user: {current_user['id']}")
        
        # Get recent history (last 30 days)
        history_result = portfolio_service.get_portfolio_history(current_user['id'], 30)
        
        if not history_result['success'] or not history_result.get('history'):
            return {
                "success": False,
                "message": "No portfolio data available",
                "summary": {}
            }
        
        # Get latest snapshot
        latest_snapshot = history_result['history'][0]  # Sorted DESC, so first is latest
        summary_stats = history_result.get('summary', {})
        
        # Get basic analytics
        analytics_result = portfolio_service.get_detailed_analytics(current_user['id'])
        
        summary = {
            "current_values": {
                "net_worth": latest_snapshot.get('net_worth', 0),
                "total_assets": latest_snapshot.get('total_assets', 0),
                "total_liabilities": latest_snapshot.get('total_liabilities', 0),
                "mutual_funds": latest_snapshot.get('mutual_funds_value', 0),
                "savings_accounts": latest_snapshot.get('savings_accounts', 0),
                "epf": latest_snapshot.get('epf_value', 0)
            },
            "recent_performance": {
                "30_day_change": summary_stats.get('absolute_change', 0),
                "30_day_change_percent": summary_stats.get('percentage_change', 0),
                "highest_value": summary_stats.get('highest_net_worth', 0),
                "lowest_value": summary_stats.get('lowest_net_worth', 0)
            },
            "data_info": {
                "last_updated": latest_snapshot.get('created_at'),
                "data_source": latest_snapshot.get('data_source', 'fi_mcp'),
                "snapshots_available": summary_stats.get('data_points', 0)
            }
        }
        
        # Add allocation if analytics available
        if analytics_result.get('success'):
            analytics = analytics_result.get('analytics', {})
            if 'allocation' in analytics:
                summary['asset_allocation'] = analytics['allocation']
        
        return {
            "success": True,
            "summary": summary
        }
            
    except Exception as e:
        logger.error(f"❌ Get summary endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio summary"
        )

@router.get("/status")
async def portfolio_service_status():
    """
    Get portfolio service status and capabilities
    """
    try:
        return {
            "status": "active",
            "service": "Artha AI Portfolio Analytics Service",
            "features": [
                "Historical portfolio tracking",
                "Advanced analytics and insights",
                "Risk metrics calculation",
                "Performance benchmarking",
                "Data export (JSON/CSV)",
                "Personalized recommendations",
                "Trend analysis",
                "Asset allocation optimization"
            ],
            "supported_formats": ["json", "csv"],
            "max_history_days": 1095,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Portfolio status endpoint error: {e}")
        return {
            "status": "error",
            "message": "Service status check failed"
        }