"""
Money Leaks Agent - Detective for finding hidden money drains
"""

import json
from typing import Dict, Any
import logging
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class MoneyLeaksAgent(BaseMoneyAgent):
    """AI agent specialized in detecting hidden money leaks and inefficiencies"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Money Leak Detective"
        self.description = "Where you're losing money secretly - AI forensic analysis"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect hidden money leaks and inefficiencies"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Analyze potential leak sources
            accounts = mcp_data.get('accounts', [])
            mutual_funds = mcp_data.get('mutual_funds', [])
            loans = mcp_data.get('loans', [])
            
            # Calculate inefficiency indicators
            total_cash = sum(acc.get('balance', 0) for acc in accounts)
            total_investments = sum(fund.get('current_value', 0) for fund in mutual_funds)
            idle_cash_ratio = total_cash / (total_cash + total_investments) if (total_cash + total_investments) > 0 else 0
            
            # Find underperforming investments
            underperforming_funds = []
            for fund in mutual_funds:
                invested = fund.get('invested_amount', 0)
                current = fund.get('current_value', 0)
                if invested > 0:
                    returns = ((current - invested) / invested) * 100
                    if returns < -5:  # More than 5% loss
                        underperforming_funds.append({
                            'name': fund.get('name', 'Unknown'),
                            'loss': current - invested,
                            'loss_percentage': returns
                        })
            
            system_prompt = f"""
            You are the MONEY LEAK DETECTIVE - a financial forensics expert who finds hidden money drains.
            
            Your mission: Identify all the ways money is being wasted, lost, or inefficiently used.
            
            Leak Detection Framework:
            1. Idle cash not earning returns
            2. Underperforming investments dragging down portfolio
            3. High-fee financial products
            4. Debt inefficiencies and missed opportunities
            5. Behavioral leaks (emotional decisions, timing errors)
            
            DETECTIVE STYLE:
            - Use investigative language and terminology
            - Use 🔍, 💸, 🚨 emojis
            - Quantify exact money amounts being lost
            - Provide immediate plugging strategies
            - Rate urgency of each leak
            """
            
            prompt = f"""
            MONEY LEAK INVESTIGATION
            Total Cash: ₹{total_cash:,.2f}
            Total Investments: ₹{total_investments:,.2f}
            Idle Cash Ratio: {idle_cash_ratio:.1%}
            Underperforming Funds: {len(underperforming_funds)}
            
            LEAK SUSPECTS:
            {chr(10).join([f"- {fund['name']}: ₹{fund['loss']:,.2f} loss ({fund['loss_percentage']:.1f}%)" for fund in underperforming_funds[:3]])}
            
            {financial_data}
            
            Investigate and find all money leaks. Where is money being wasted or lost? How much exactly?
            
            Format as JSON:
            {{
                "money_leaks": [
                    {{
                        "leak_type": "Type of money drain",
                        "leak_source": "Specific source/account/fund",
                        "money_lost_annually": "₹X,XXX per year",
                        "total_impact": "₹X,XXX total",
                        "urgency": "High/Medium/Low",
                        "plug_strategy": "Specific action to stop leak",
                        "recovery_potential": "₹X,XXX recoverable"
                    }}
                ],
                "total_leaks_identified": 5,
                "annual_leakage": "₹XX,XXX per year",
                "biggest_leak": {{
                    "source": "Primary drain source",
                    "impact": "₹XX,XXX",
                    "fix": "Immediate solution"
                }},
                "quick_wins": [
                    "Immediate action for fast savings"
                ],
                "leak_severity": "High/Medium/Low",
                "money_saved_if_fixed": "₹XX,XXX annually",
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
                    "analysis_type": "money_leaks",
                    "timestamp": "2025-01-23T19:33:28+05:30",
                    "leak_indicators": {
                        "idle_cash_amount": total_cash,
                        "idle_cash_percentage": f"{idle_cash_ratio:.1%}",
                        "underperforming_investments": len(underperforming_funds),
                        "potential_annual_loss": sum(abs(fund['loss']) for fund in underperforming_funds)
                    }
                })
                
                return result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON from Money Leaks AI response")
                
                # Calculate basic leak estimation
                estimated_idle_loss = total_cash * 0.04  # 4% opportunity cost
                estimated_underperformance_loss = sum(abs(fund['loss']) for fund in underperforming_funds)
                
                return {
                    "money_leaks": [{
                        "leak_type": "Idle Cash Opportunity Cost",
                        "leak_source": f"₹{total_cash:,.2f} in low-yield accounts",
                        "money_lost_annually": f"₹{estimated_idle_loss:,.0f} per year",
                        "total_impact": f"₹{estimated_idle_loss:,.0f}",
                        "urgency": "Medium",
                        "plug_strategy": "Move to higher-yield instruments",
                        "recovery_potential": f"₹{estimated_idle_loss:,.0f}"
                    }],
                    "total_leaks_identified": 1 + len(underperforming_funds),
                    "annual_leakage": f"₹{estimated_idle_loss + estimated_underperformance_loss:,.0f} per year",
                    "biggest_leak": {
                        "source": "Idle cash and underperforming investments",
                        "impact": f"₹{max(estimated_idle_loss, estimated_underperformance_loss):,.0f}",
                        "fix": "Optimize asset allocation"
                    },
                    "quick_wins": [ai_response[:200] + "..." if len(ai_response) > 200 else ai_response],
                    "leak_severity": "Medium",
                    "money_saved_if_fixed": f"₹{estimated_idle_loss + estimated_underperformance_loss:,.0f} annually",
                    "confidence_level": 0.75,
                    "agent_name": self.name,
                    "analysis_type": "money_leaks",
                    "timestamp": "2025-01-23T19:33:28+05:30"
                }
                
        except Exception as e:
            logger.error(f"Money Leaks analysis failed: {e}")
            return {
                "money_leaks": [{
                    "leak_type": "Analysis Error",
                    "leak_source": "System unavailable",
                    "money_lost_annually": "Unknown",
                    "total_impact": f"Analysis failed: {str(e)}",
                    "urgency": "High",
                    "plug_strategy": "Retry analysis",
                    "recovery_potential": "Unknown"
                }],
                "total_leaks_identified": 0,
                "annual_leakage": "Unknown",
                "biggest_leak": {
                    "source": "System error",
                    "impact": "Cannot calculate",
                    "fix": "Please try again later"
                },
                "quick_wins": ["Retry when system is available"],
                "leak_severity": "Unknown",
                "money_saved_if_fixed": "Unknown",
                "confidence_level": 0.0,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "money_leaks",
                "timestamp": "2025-01-23T19:33:28+05:30"
            }