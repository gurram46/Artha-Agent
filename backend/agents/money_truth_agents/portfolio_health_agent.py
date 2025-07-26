"""
Portfolio Health Agent - Comprehensive investment health diagnosis
"""

import json
from typing import Dict, Any
import logging
from datetime import datetime
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
            
            system_prompt = """
            You are a Portfolio Health Doctor 🏥 - diagnose financial health in simple, clear language.
            
            WRITING STYLE:
            - Use Indian Rupees (₹) NEVER dollars ($)
            - Be direct and actionable
            - Use medical emojis: 🏥 💊 🩺 ⚡ 🚨
            - Include specific numbers and percentages
            - Give clear treatment steps
            
            FORMAT: Write in markdown with clear sections and bullet points.
            """
            
            prompt = f"""
            ## 🏥 PORTFOLIO HEALTH CHECKUP
            
            **Financial Vitals:**
            - Total Investment: ₹{total_invested:,.0f}
            - Current Value: ₹{total_current:,.0f}
            - Gain/Loss: ₹{total_gain_loss:,.0f}
            - Performance: {((total_gain_loss/total_invested*100) if total_invested > 0 else 0):.1f}%
            
            **Fund Performance:**
            - Best Fund: {best_fund.get('name', 'No funds') if best_fund else 'No funds'} ({best_performance:.1f}%)
            - Worst Fund: {worst_fund.get('name', 'No funds') if worst_fund else 'No funds'} ({worst_performance:.1f}%)
            - Total Funds: {len(mutual_funds)}
            
            **Patient Data:**
            {financial_data}
            
            Provide a clear portfolio health diagnosis with:
            1. **Health Score** (X/100)
            2. **Main Issues** (what's wrong)
            3. **Treatment Plan** (what to do)
            4. **Prognosis** (expected outcome)
            
            Keep it simple, actionable, and use ₹ for all amounts.
            """
            
            ai_response = await self.call_ai(prompt, system_prompt)
            
            # Return simple response with analysis content
            return {
                "analysis": ai_response,
                "agent_name": self.name,
                "analysis_type": "portfolio_health",
                "timestamp": datetime.now().isoformat(),
                "portfolio_metrics": {
                    "total_invested": total_invested,
                    "current_value": total_current,
                    "total_gain_loss": total_gain_loss,
                    "return_percentage": f"{(total_gain_loss/total_invested*100):.1f}%" if total_invested > 0 else "0%",
                    "funds_analyzed": len(mutual_funds)
                }
            }
                
        except Exception as e:
            logger.error(f"Portfolio Health analysis failed: {e}")
            return {
                "analysis": f"🏥 **Portfolio Health Analysis Failed**\n\nSorry, unable to complete your portfolio health checkup at this time.\n\n**Error:** {str(e)}\n\n**Next Steps:**\n- Please try again in a few moments\n- Ensure your financial data is properly connected\n- Contact support if the issue persists",
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "portfolio_health",
                "timestamp": datetime.now().isoformat()
            }