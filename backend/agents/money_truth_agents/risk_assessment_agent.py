"""
Risk Assessment Agent - AI-powered financial risk analysis and protection gaps
"""

import json
from typing import Dict, Any
import logging
from datetime import datetime
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class RiskAssessmentAgent(BaseMoneyAgent):
    """AI agent specialized in comprehensive financial risk analysis and protection planning"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Risk Assessment Guardian"
        self.description = "AI-powered risk analysis and financial protection gaps detection"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive financial risk assessment and protection gap analysis"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Calculate risk indicators
            loans = mcp_data.get('loans', [])
            mutual_funds = mcp_data.get('mutual_funds', [])
            accounts = mcp_data.get('accounts', [])
            
            total_debt = sum(loan.get('outstanding_amount', 0) for loan in loans)
            total_investments = sum(fund.get('current_value', 0) for fund in mutual_funds)
            emergency_fund = sum(acc.get('balance', 0) for acc in accounts)
            
            # Risk ratios
            debt_to_income_proxy = total_debt / (net_worth + 1)  # Proxy calculation
            investment_concentration_risk = len(mutual_funds) < 3
            emergency_fund_months = (emergency_fund / 50000) if emergency_fund > 0 else 0  # Rough estimate
            
            system_prompt = """
            You are a Risk Assessment Guardian 🛡️ - identify threats to wealth in simple, clear language.
            
            WRITING STYLE:
            - Use Indian Rupees (₹) NEVER dollars ($)
            - Be direct about risks and solutions
            - Use protection emojis: ⚠️ 🛡️ 🚨 🔒 ⚡
            - Include specific numbers and potential losses
            - Give clear protection steps
            
            FORMAT: Write in markdown with clear sections and bullet points.
            """
            
            prompt = f"""
            ## 🛡️ FINANCIAL RISK ASSESSMENT
            
            **Current Financial Position:**
            - Net Worth: ₹{net_worth:,.0f}
            - Total Debt: ₹{total_debt:,.0f}
            - Emergency Fund: ₹{emergency_fund:,.0f} (~{emergency_fund_months:.1f} months)
            - Investment Funds: {len(mutual_funds)}
            
            **Risk Indicators:**
            - Debt Load: {debt_to_income_proxy:.1%} of net worth
            - Emergency Coverage: {emergency_fund_months:.1f} months
            - Investment Diversity: {'⚠️ Low' if investment_concentration_risk else '✅ Adequate'}
            
            **Financial Data:**
            {financial_data}
            
            Provide a clear risk assessment with:
            1. **Risk Level** (High/Medium/Low)
            2. **Biggest Threats** (what could go wrong)
            3. **Protection Plan** (how to reduce risks)
            4. **Emergency Readiness** (are they prepared)
            
            Keep it simple, actionable, and use ₹ for all amounts.
            """
            
            ai_response = await self.call_ai(prompt, system_prompt)
            
            # Return simple response with analysis content
            return {
                "analysis": ai_response,
                "agent_name": self.name,
                "analysis_type": "risk_assessment",
                "timestamp": datetime.now().isoformat(),
                "risk_metrics": {
                    "debt_to_networth_ratio": f"{debt_to_income_proxy:.1%}",
                    "emergency_fund_months": f"{emergency_fund_months:.1f}",
                    "investment_diversity_score": len(mutual_funds),
                    "total_exposure": total_debt + total_investments
                }
            }
                
        except Exception as e:
            logger.error(f"Risk Assessment analysis failed: {e}")
            return {
                "analysis": f"🛡️ **Risk Assessment Failed**\n\nSorry, unable to complete your risk assessment at this time.\n\n**Error:** {str(e)}\n\n**Next Steps:**\n- Please try again in a few moments\n- Ensure your financial data is properly connected\n- Contact support if the issue persists",
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "risk_assessment",
                "timestamp": datetime.now().isoformat()
            }