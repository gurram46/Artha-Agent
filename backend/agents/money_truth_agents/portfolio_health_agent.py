"""
Portfolio Health Agent - Comprehensive investment health diagnosis
"""

import json
from typing import Dict, Any
import logging
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class PortfolioHealthAgent(BaseMoneyAgent):
    """AI agent specialized in diagnosing portfolio health and investment performance"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Portfolio Health Doctor"
        self.description = "Comprehensive AI diagnosis of your investment health"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive portfolio health diagnosis"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Calculate portfolio metrics
            mutual_funds = mcp_data.get('mutual_funds', [])
            total_invested = sum(fund.get('invested_amount', 0) for fund in mutual_funds)
            total_current = sum(fund.get('current_value', 0) for fund in mutual_funds)
            total_gain_loss = total_current - total_invested
            
            # Find best and worst performing funds
            best_fund = None
            worst_fund = None
            best_performance = float('-inf')
            worst_performance = float('inf')
            
            for fund in mutual_funds:
                invested = fund.get('invested_amount', 0)
                current = fund.get('current_value', 0)
                if invested > 0:
                    performance = ((current - invested) / invested) * 100
                    if performance > best_performance:
                        best_performance = performance
                        best_fund = fund
                    if performance < worst_performance:
                        worst_performance = performance
                        worst_fund = fund
            
            system_prompt = f"""
            You are the PORTFOLIO HEALTH DOCTOR - a medical expert for investments who diagnoses financial health.
            
            Your mission: Provide a comprehensive health diagnosis of the investment portfolio.
            
            Analysis Framework:
            1. Overall Health Score (0-100)
            2. Critical Issues requiring immediate attention
            3. Healthy aspects to maintain
            4. Treatment recommendations for sick investments
            5. Preventive measures for portfolio protection
            
            DIAGNOSTIC STYLE:
            - Use medical terminology: "diagnosis", "symptoms", "treatment"
            - Use 🏥, 💊, 🩺 emojis
            - Be specific with numbers and percentages
            - Provide clear action items
            - Rate urgency levels
            """
            
            prompt = f"""
            PORTFOLIO HEALTH EXAMINATION
            Total Investment: ₹{total_invested:,.2f}
            Current Value: ₹{total_current:,.2f}
            Overall Gain/Loss: ₹{total_gain_loss:,.2f}
            
            Best Performer: {best_fund.get('name', 'N/A') if best_fund else 'N/A'} ({best_performance:.1f}%)
            Worst Performer: {worst_fund.get('name', 'N/A') if worst_fund else 'N/A'} ({worst_performance:.1f}%)
            
            {financial_data}
            
            Diagnose this portfolio's health. What's sick? What's healthy? What needs immediate treatment?
            
            Format as JSON:
            {{
                "health_score": 75,
                "overall_diagnosis": "Brief medical-style diagnosis",
                "critical_issues": [
                    {{
                        "problem": "Specific issue detected",
                        "severity": "High/Medium/Low",
                        "financial_impact": "₹X loss or risk",
                        "treatment": "Specific action needed"
                    }}
                ],
                "healthy_aspects": [
                    "What's working well in the portfolio"
                ],
                "prescription": [
                    "Immediate action item 1",
                    "Immediate action item 2"
                ],
                "risk_level": "High/Medium/Low",
                "prognosis": "Expected outcome if treated",
                "confidence_level": 0.85
            }}
            """
            
            ai_response = await self.call_ai(prompt, system_prompt)
            
            # Try to parse JSON response
            try:
                result = json.loads(ai_response)
                
                # Add analysis metadata
                result.update({
                    "agent_name": self.name,
                    "analysis_type": "portfolio_health",
                    "timestamp": "2025-01-23T19:33:28+05:30",
                    "portfolio_metrics": {
                        "total_invested": total_invested,
                        "current_value": total_current,
                        "total_gain_loss": total_gain_loss,
                        "return_percentage": f"{(total_gain_loss/total_invested*100):.1f}%" if total_invested > 0 else "0%",
                        "funds_analyzed": len(mutual_funds)
                    }
                })
                
                return result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON from Portfolio Health AI response")
                
                # Generate basic health score based on performance
                health_score = max(0, min(100, 50 + (total_gain_loss / total_invested * 100) if total_invested > 0 else 50))
                
                return {
                    "health_score": int(health_score),
                    "overall_diagnosis": "Portfolio analysis completed",
                    "critical_issues": [{
                        "problem": "Detailed analysis in progress",
                        "severity": "Medium",
                        "financial_impact": f"₹{abs(total_gain_loss):,.2f}",
                        "treatment": "Review full AI analysis"
                    }],
                    "healthy_aspects": ["Investment discipline maintained"],
                    "prescription": [ai_response[:200] + "..." if len(ai_response) > 200 else ai_response],
                    "risk_level": "Medium",
                    "prognosis": "Positive with proper management",
                    "confidence_level": 0.75,
                    "agent_name": self.name,
                    "analysis_type": "portfolio_health",
                    "timestamp": "2025-01-23T19:33:28+05:30"
                }
                
        except Exception as e:
            logger.error(f"Portfolio Health analysis failed: {e}")
            return {
                "health_score": 0,
                "overall_diagnosis": f"Analysis failed: {str(e)}",
                "critical_issues": [{
                    "problem": "Unable to complete health check",
                    "severity": "High",
                    "financial_impact": "Unknown",
                    "treatment": "Please try again later"
                }],
                "healthy_aspects": [],
                "prescription": ["Retry analysis when system is available"],
                "risk_level": "Unknown",
                "prognosis": "Analysis needed",
                "confidence_level": 0.0,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "portfolio_health",
                "timestamp": "2025-01-23T19:33:28+05:30"
            }