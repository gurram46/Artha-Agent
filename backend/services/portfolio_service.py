"""
Portfolio Analytics Service with Historical Tracking
==================================================

Advanced portfolio management with historical data, analytics, and insights.
"""

import os
import sys
import uuid
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
import json
import statistics
from collections import defaultdict

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_database_url
from utils.encryption import EncryptionHelper

logger = logging.getLogger(__name__)

class PortfolioService:
    """
    Advanced portfolio analytics and historical tracking service
    """
    
    def __init__(self):
        self.database_url = get_database_url()
        self.encryption = EncryptionHelper()
    
    def _get_db_connection(self):
        """Get database connection with proper error handling"""
        try:
            # Parse database URL
            import re
            match = re.match(r'postgresql://([^:]+):?([^@]*)@([^:]+):(\d+)/(.+)', self.database_url)
            if not match:
                match = re.match(r'postgresql://([^@]+)@([^:]+):(\d+)/(.+)', self.database_url)
                if match:
                    user, host, port, database = match.groups()
                    password = ''
                else:
                    raise ValueError(f"Invalid database URL format: {self.database_url}")
            else:
                user, password, host, port, database = match.groups()
            
            conn = psycopg2.connect(
                host=host,
                port=int(port),
                database=database,
                user=user,
                password=password,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise Exception("Database connection failed")
    
    def store_portfolio_snapshot(self, user_id: str, portfolio_data: Dict[str, Any], 
                                data_source: str = 'fi_mcp') -> Dict[str, Any]:
        """
        Store daily portfolio snapshot for historical tracking
        """
        try:
            today = date.today()
            
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if snapshot already exists for today
                    cursor.execute("""
                        SELECT id FROM portfolio_snapshots 
                        WHERE user_id = %s AND snapshot_date = %s
                    """, (user_id, today))
                    
                    existing = cursor.fetchone()
                    
                    # Extract key metrics from portfolio data
                    summary = portfolio_data.get('summary', {})
                    net_worth = summary.get('total_net_worth', 0)
                    total_assets = summary.get('total_assets', 0)
                    total_liabilities = summary.get('total_liabilities', 0)
                    mutual_funds = summary.get('mutual_funds', 0)
                    liquid_funds = summary.get('liquid_funds', 0)
                    epf = summary.get('epf', 0)
                    
                    # Encrypt complete portfolio data
                    portfolio_enc = self.encryption.encrypt_data(json.dumps(portfolio_data))
                    
                    if existing:
                        # Update existing snapshot
                        cursor.execute("""
                            UPDATE portfolio_snapshots SET
                                net_worth = %s, total_assets = %s, total_liabilities = %s,
                                mutual_funds_value = %s, savings_accounts = %s, epf_value = %s,
                                portfolio_data_encrypted = %s, portfolio_data_nonce = %s, 
                                portfolio_data_auth_tag = %s, data_source = %s
                            WHERE user_id = %s AND snapshot_date = %s
                        """, (
                            Decimal(str(net_worth)), Decimal(str(total_assets)), Decimal(str(total_liabilities)),
                            Decimal(str(mutual_funds)), Decimal(str(liquid_funds)), Decimal(str(epf)),
                            portfolio_enc['encrypted_data'], portfolio_enc['nonce'], portfolio_enc['auth_tag'],
                            data_source, user_id, today
                        ))
                        action = "updated"
                    else:
                        # Create new snapshot
                        snapshot_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO portfolio_snapshots (
                                id, user_id, snapshot_date, net_worth, total_assets, total_liabilities,
                                mutual_funds_value, savings_accounts, epf_value,
                                portfolio_data_encrypted, portfolio_data_nonce, portfolio_data_auth_tag,
                                data_source
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            snapshot_id, user_id, today,
                            Decimal(str(net_worth)), Decimal(str(total_assets)), Decimal(str(total_liabilities)),
                            Decimal(str(mutual_funds)), Decimal(str(liquid_funds)), Decimal(str(epf)),
                            portfolio_enc['encrypted_data'], portfolio_enc['nonce'], portfolio_enc['auth_tag'],
                            data_source
                        ))
                        action = "created"
                    
                    conn.commit()
                    
                    logger.info(f"✅ Portfolio snapshot {action} for user: {user_id} on {today}")
                    return {"success": True, "message": f"Portfolio snapshot {action} successfully"}
                    
        except Exception as e:
            logger.error(f"Store portfolio snapshot failed: {e}")
            return {"success": False, "message": "Failed to store portfolio snapshot"}
    
    def get_portfolio_history(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get portfolio history for specified number of days
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT snapshot_date, net_worth, total_assets, total_liabilities,
                               mutual_funds_value, savings_accounts, epf_value, data_source, created_at
                        FROM portfolio_snapshots 
                        WHERE user_id = %s AND snapshot_date >= %s 
                        ORDER BY snapshot_date DESC
                    """, (user_id, start_date))
                    
                    snapshots = cursor.fetchall()
                    
                    if not snapshots:
                        return {"success": True, "history": [], "message": "No portfolio history found"}
                    
                    history = []
                    for snapshot in snapshots:
                        snapshot_dict = dict(snapshot)
                        
                        # Convert Decimals to floats
                        for key in ['net_worth', 'total_assets', 'total_liabilities', 
                                   'mutual_funds_value', 'savings_accounts', 'epf_value']:
                            if snapshot_dict[key]:
                                snapshot_dict[key] = float(snapshot_dict[key])
                        
                        # Format dates
                        snapshot_dict['snapshot_date'] = snapshot_dict['snapshot_date'].isoformat()
                        snapshot_dict['created_at'] = snapshot_dict['created_at'].isoformat()
                        
                        history.append(snapshot_dict)
                    
                    # Calculate summary statistics
                    net_worths = [s['net_worth'] for s in history if s['net_worth']]
                    
                    summary_stats = {}
                    if net_worths:
                        current_value = net_worths[0]  # Latest value (DESC order)
                        oldest_value = net_worths[-1]  # Oldest value
                        
                        summary_stats = {
                            "current_net_worth": current_value,
                            "period_start_net_worth": oldest_value,
                            "absolute_change": current_value - oldest_value,
                            "percentage_change": ((current_value - oldest_value) / oldest_value * 100) if oldest_value != 0 else 0,
                            "highest_net_worth": max(net_worths),
                            "lowest_net_worth": min(net_worths),
                            "average_net_worth": statistics.mean(net_worths),
                            "volatility": statistics.stdev(net_worths) if len(net_worths) > 1 else 0,
                            "data_points": len(history),
                            "period_days": days
                        }
                    
                    return {
                        "success": True,
                        "history": history,
                        "summary": summary_stats
                    }
                    
        except Exception as e:
            logger.error(f"Get portfolio history failed: {e}")
            return {"success": False, "message": "Failed to get portfolio history"}
    
    def get_detailed_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed portfolio analytics with insights
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get last 90 days of data for detailed analysis
                    end_date = date.today()
                    start_date = end_date - timedelta(days=90)
                    
                    cursor.execute("""
                        SELECT snapshot_date, net_worth, total_assets, total_liabilities,
                               mutual_funds_value, savings_accounts, epf_value,
                               portfolio_data_encrypted, portfolio_data_nonce, portfolio_data_auth_tag
                        FROM portfolio_snapshots 
                        WHERE user_id = %s AND snapshot_date >= %s 
                        ORDER BY snapshot_date ASC
                    """, (user_id, start_date))
                    
                    snapshots = cursor.fetchall()
                    
                    if not snapshots:
                        return {"success": False, "message": "Insufficient data for analytics"}
                    
                    # Process snapshots
                    analytics_data = []
                    for snapshot in snapshots:
                        snapshot_dict = dict(snapshot)
                        
                        # Convert Decimals to floats
                        for key in ['net_worth', 'total_assets', 'total_liabilities', 
                                   'mutual_funds_value', 'savings_accounts', 'epf_value']:
                            if snapshot_dict[key]:
                                snapshot_dict[key] = float(snapshot_dict[key])
                        
                        analytics_data.append(snapshot_dict)
                    
                    # Calculate comprehensive analytics
                    analytics = self._calculate_comprehensive_analytics(analytics_data)
                    
                    # Get user investment preferences for contextualized insights
                    cursor.execute("""
                        SELECT risk_tolerance, investment_horizon, investment_goals,
                               monthly_investment_amount, emergency_fund_months
                        FROM investment_preferences WHERE user_id = %s
                    """, (user_id,))
                    
                    prefs = cursor.fetchone()
                    preferences = dict(prefs) if prefs else {}
                    
                    # Generate personalized insights
                    insights = self._generate_insights(analytics, preferences)
                    
                    return {
                        "success": True,
                        "analytics": analytics,
                        "insights": insights,
                        "data_period": f"{start_date.isoformat()} to {end_date.isoformat()}",
                        "total_snapshots": len(analytics_data)
                    }
                    
        except Exception as e:
            logger.error(f"Get detailed analytics failed: {e}")
            return {"success": False, "message": "Failed to get portfolio analytics"}
    
    def _calculate_comprehensive_analytics(self, snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive analytics from snapshot data
        """
        if not snapshots:
            return {}
        
        # Extract time series data
        dates = [s['snapshot_date'] for s in snapshots]
        net_worths = [s['net_worth'] for s in snapshots if s['net_worth']]
        assets = [s['total_assets'] for s in snapshots if s['total_assets']]
        liabilities = [s['total_liabilities'] for s in snapshots if s['total_liabilities']]
        mf_values = [s['mutual_funds_value'] for s in snapshots if s['mutual_funds_value']]
        liquid_values = [s['savings_accounts'] for s in snapshots if s['savings_accounts']]
        epf_values = [s['epf_value'] for s in snapshots if s['epf_value']]
        
        analytics = {}
        
        if net_worths and len(net_worths) > 1:
            current_nw = net_worths[-1]
            previous_nw = net_worths[0]
            
            # Growth metrics
            analytics['growth'] = {
                "current_net_worth": current_nw,
                "starting_net_worth": previous_nw,
                "absolute_growth": current_nw - previous_nw,
                "percentage_growth": ((current_nw - previous_nw) / previous_nw * 100) if previous_nw != 0 else 0,
                "avg_daily_growth": (current_nw - previous_nw) / len(net_worths) if len(net_worths) > 0 else 0
            }
            
            # Risk metrics
            if len(net_worths) > 2:
                daily_returns = [(net_worths[i] - net_worths[i-1]) / net_worths[i-1] * 100 
                               for i in range(1, len(net_worths)) if net_worths[i-1] != 0]
                
                if daily_returns:
                    analytics['risk'] = {
                        "volatility": statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0,
                        "max_drawdown": self._calculate_max_drawdown(net_worths),
                        "best_day_return": max(daily_returns) if daily_returns else 0,
                        "worst_day_return": min(daily_returns) if daily_returns else 0,
                        "positive_days": len([r for r in daily_returns if r > 0]),
                        "negative_days": len([r for r in daily_returns if r < 0]),
                        "win_rate": len([r for r in daily_returns if r > 0]) / len(daily_returns) * 100 if daily_returns else 0
                    }
        
        # Asset allocation analysis
        if assets and mf_values and liquid_values and epf_values:
            latest_assets = assets[-1]
            latest_mf = mf_values[-1] if mf_values else 0
            latest_liquid = liquid_values[-1] if liquid_values else 0
            latest_epf = epf_values[-1] if epf_values else 0
            
            analytics['allocation'] = {
                "mutual_funds_percentage": (latest_mf / latest_assets * 100) if latest_assets > 0 else 0,
                "liquid_funds_percentage": (latest_liquid / latest_assets * 100) if latest_assets > 0 else 0,
                "epf_percentage": (latest_epf / latest_assets * 100) if latest_assets > 0 else 0,
                "diversification_score": self._calculate_diversification_score([latest_mf, latest_liquid, latest_epf])
            }
        
        # Trend analysis
        if len(net_worths) >= 7:
            recent_trend = self._calculate_trend(net_worths[-7:])  # Last 7 days
            overall_trend = self._calculate_trend(net_worths)      # Overall trend
            
            analytics['trends'] = {
                "recent_trend": recent_trend,
                "overall_trend": overall_trend,
                "momentum": "positive" if recent_trend > overall_trend else "negative" if recent_trend < overall_trend else "neutral"
            }
        
        # Performance benchmarks
        analytics['benchmarks'] = {
            "nifty_50_comparison": "Not available",  # Would need market data integration
            "fd_comparison": self._calculate_fd_comparison(analytics.get('growth', {}).get('percentage_growth', 0)),
            "inflation_adjusted": "Not available"     # Would need inflation data
        }
        
        return analytics
    
    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """
        Calculate maximum drawdown from peak
        """
        if not values or len(values) < 2:
            return 0
        
        peak = values[0]
        max_drawdown = 0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak * 100
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_diversification_score(self, asset_values: List[float]) -> float:
        """
        Calculate diversification score based on asset allocation
        """
        total = sum(asset_values)
        if total == 0:
            return 0
        
        # Calculate Herfindahl-Hirschman Index (lower is better diversified)
        proportions = [value / total for value in asset_values if value > 0]
        hhi = sum(p ** 2 for p in proportions)
        
        # Convert to score (0-100, higher is better)
        max_hhi = 1.0  # Worst case (all in one asset)
        min_hhi = 1 / len([v for v in asset_values if v > 0])  # Best case (equal allocation)
        
        if max_hhi == min_hhi:
            return 100
        
        score = (1 - (hhi - min_hhi) / (max_hhi - min_hhi)) * 100
        return max(0, min(100, score))
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculate trend using simple linear regression slope
        """
        if not values or len(values) < 2:
            return 0
        
        n = len(values)
        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_vals[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        return slope
    
    def _calculate_fd_comparison(self, portfolio_return: float) -> Dict[str, Any]:
        """
        Compare portfolio performance with fixed deposit returns
        """
        # Assume average FD rate of 6.5% annually
        fd_annual_rate = 6.5
        
        # Annualize portfolio return (rough estimate)
        annualized_return = portfolio_return * 4  # Assuming quarterly measurement
        
        return {
            "portfolio_return": portfolio_return,
            "annualized_portfolio_return": annualized_return,
            "fd_return": fd_annual_rate,
            "excess_return": annualized_return - fd_annual_rate,
            "outperforming": annualized_return > fd_annual_rate
        }
    
    def _generate_insights(self, analytics: Dict[str, Any], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized insights based on analytics and user preferences
        """
        insights = []
        
        # Growth insights
        growth = analytics.get('growth', {})
        if growth:
            percentage_growth = growth.get('percentage_growth', 0)
            if percentage_growth > 10:
                insights.append({
                    "type": "positive",
                    "category": "growth",
                    "title": "Strong Portfolio Growth",
                    "message": f"Your portfolio has grown by {percentage_growth:.1f}% in the analyzed period. Keep up the good work!",
                    "priority": "high"
                })
            elif percentage_growth < -5:
                insights.append({
                    "type": "warning",
                    "category": "growth",
                    "title": "Portfolio Decline",
                    "message": f"Your portfolio has declined by {abs(percentage_growth):.1f}%. Consider reviewing your investment strategy.",
                    "priority": "high"
                })
        
        # Risk insights
        risk = analytics.get('risk', {})
        if risk:
            volatility = risk.get('volatility', 0)
            max_drawdown = risk.get('max_drawdown', 0)
            
            if volatility > 5:
                risk_tolerance = preferences.get('risk_tolerance', 'moderate')
                if risk_tolerance in ['conservative']:
                    insights.append({
                        "type": "warning",
                        "category": "risk",
                        "title": "High Volatility Detected",
                        "message": f"Your portfolio shows {volatility:.1f}% volatility, which may be high for your conservative risk profile.",
                        "priority": "medium"
                    })
            
            if max_drawdown > 15:
                insights.append({
                    "type": "caution",
                    "category": "risk",
                    "title": "Significant Drawdown",
                    "message": f"Your portfolio experienced a maximum drawdown of {max_drawdown:.1f}%. Consider risk management strategies.",
                    "priority": "medium"
                })
        
        # Allocation insights
        allocation = analytics.get('allocation', {})
        if allocation:
            mf_percentage = allocation.get('mutual_funds_percentage', 0)
            liquid_percentage = allocation.get('liquid_funds_percentage', 0)
            diversification = allocation.get('diversification_score', 0)
            
            if liquid_percentage > 50:
                insights.append({
                    "type": "suggestion",
                    "category": "allocation",
                    "title": "High Liquid Fund Allocation",
                    "message": f"{liquid_percentage:.1f}% of your portfolio is in liquid funds. Consider diversifying for better returns.",
                    "priority": "low"
                })
            
            if diversification < 60:
                insights.append({
                    "type": "suggestion",
                    "category": "allocation",
                    "title": "Improve Diversification",
                    "message": f"Your diversification score is {diversification:.1f}/100. Consider spreading investments across more asset classes.",
                    "priority": "medium"
                })
        
        # Trend insights
        trends = analytics.get('trends', {})
        if trends:
            momentum = trends.get('momentum', 'neutral')
            if momentum == 'negative':
                insights.append({
                    "type": "caution",
                    "category": "trends",
                    "title": "Negative Momentum",
                    "message": "Your portfolio shows negative momentum recently. Monitor closely and consider rebalancing.",
                    "priority": "medium"
                })
            elif momentum == 'positive':
                insights.append({
                    "type": "positive",
                    "category": "trends",
                    "title": "Positive Momentum",
                    "message": "Your portfolio shows positive momentum. Good time to review and optimize allocation.",
                    "priority": "low"
                })
        
        # Monthly investment insights
        monthly_investment = preferences.get('monthly_investment_amount')
        if monthly_investment and growth:
            current_nw = growth.get('current_net_worth', 0)
            if current_nw > 0 and monthly_investment > 0:
                months_to_double = (current_nw / monthly_investment) if monthly_investment > 0 else 0
                if months_to_double < 12:
                    insights.append({
                        "type": "positive",
                        "category": "planning",
                        "title": "Strong Savings Rate",
                        "message": f"At your current savings rate, you could double your portfolio in {months_to_double:.1f} months!",
                        "priority": "low"
                    })
        
        return sorted(insights, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    def export_portfolio_data(self, user_id: str, format: str = 'json', days: int = 365) -> Dict[str, Any]:
        """
        Export user portfolio data in specified format
        """
        try:
            # Get portfolio history
            history_result = self.get_portfolio_history(user_id, days)
            if not history_result['success']:
                return history_result
            
            # Get analytics
            analytics_result = self.get_detailed_analytics(user_id)
            
            export_data = {
                "export_info": {
                    "user_id": user_id,
                    "export_date": datetime.utcnow().isoformat(),
                    "format": format,
                    "period_days": days,
                    "data_points": len(history_result.get('history', []))
                },
                "portfolio_history": history_result.get('history', []),
                "summary_statistics": history_result.get('summary', {}),
                "analytics": analytics_result.get('analytics', {}) if analytics_result.get('success') else {},
                "insights": analytics_result.get('insights', []) if analytics_result.get('success') else []
            }
            
            if format.lower() == 'csv':
                # Convert to CSV format (simplified)
                csv_data = self._convert_to_csv(export_data)
                return {"success": True, "data": csv_data, "format": "csv"}
            elif format.lower() == 'pdf':
                # Return data for PDF generation (processed by endpoint)
                return {"success": True, "data": export_data, "format": "pdf"}
            else:
                # Return as JSON
                return {"success": True, "data": export_data, "format": "json"}
                
        except Exception as e:
            logger.error(f"Export portfolio data failed: {e}")
            return {"success": False, "message": "Failed to export portfolio data"}
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """
        Convert portfolio data to CSV format
        """
        import io
        import csv
        
        output = io.StringIO()
        
        # Write portfolio history
        if data.get('portfolio_history'):
            writer = csv.DictWriter(output, fieldnames=[
                'snapshot_date', 'net_worth', 'total_assets', 'total_liabilities',
                'mutual_funds_value', 'savings_accounts', 'epf_value', 'data_source'
            ])
            writer.writeheader()
            writer.writerows(data['portfolio_history'])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content


# Global portfolio service instance
_portfolio_service: Optional[PortfolioService] = None

def get_portfolio_service() -> PortfolioService:
    """Get or create global portfolio service instance"""
    global _portfolio_service
    if _portfolio_service is None:
        _portfolio_service = PortfolioService()
    return _portfolio_service