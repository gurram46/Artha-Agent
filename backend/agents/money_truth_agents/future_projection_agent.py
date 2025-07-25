"""
Future Projection Agent - AI predicts financial future
"""

import json
from typing import Dict, Any
import logging
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class FutureProjectionAgent(BaseMoneyAgent):
    """AI agent specialized in predicting financial future based on current patterns"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Future Wealth Oracle"
        self.description = "AI predicts your financial future based on current patterns"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict financial future with AI-powered projections"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Calculate current investment trends
            total_mutual_fund_value = sum(fund.get('current_value', 0) for fund in mcp_data.get('mutual_funds', []))
            total_invested_amount = sum(fund.get('invested_amount', 0) for fund in mcp_data.get('mutual_funds', []))
            current_returns = ((total_mutual_fund_value - total_invested_amount) / total_invested_amount * 100) if total_invested_amount > 0 else 0
            
            system_prompt = f"""
            You are the FUTURE WEALTH ORACLE - an AI time-travel expert who sees financial futures.
            
            Your mission: Analyze current financial patterns and predict realistic future scenarios.
            
            Key Analysis Areas:
            1. Wealth growth trajectory based on current savings/investment patterns
            2. Impact of current investment performance on future wealth
            3. Timeline to achieve financial milestones
            4. Potential risks that could derail progress
            5. Opportunities for acceleration
            
            PREDICTION STYLE:
            - Use 🔮, ⏰, 💰 emojis
            - Be specific with projected numbers and timelines
            - Show multiple scenarios (best case, realistic, worst case)
            - Base predictions on actual data patterns
            - Include actionable acceleration strategies
            """
            
            prompt = f"""
            FINANCIAL FUTURE ANALYSIS
            Current Net Worth: ₹{net_worth:,.2f}
            Current MF Returns: {current_returns:.1f}%
            Total Investments: ₹{total_invested_amount:,.2f}
            
            {financial_data}
            
            Predict this person's financial future with 3 scenarios. What will their wealth look like in 5, 10, 20 years?
            
            Format as JSON:
            {{
                "projections": {{
                    "5_years": {{
                        "conservative": "₹X.XX lakhs",
                        "realistic": "₹X.XX lakhs", 
                        "optimistic": "₹X.XX lakhs"
                    }},
                    "10_years": {{
                        "conservative": "₹X.XX crores",
                        "realistic": "₹X.XX crores",
                        "optimistic": "₹X.XX crores"
                    }},
                    "20_years": {{
                        "conservative": "₹X.XX crores",
                        "realistic": "₹X.XX crores", 
                        "optimistic": "₹X.XX crores"
                    }}
                }},
                "key_insights": [
                    "Specific insight about wealth trajectory",
                    "Timeline to reach specific milestone",
                    "Major risk that could impact projections"
                ],
                "acceleration_opportunities": [
                    "Specific action to boost wealth growth",
                    "Investment optimization suggestion"
                ],
                "most_likely_scenario": "Detailed narrative of realistic future",
                "confidence_level": 0.80
            }}
            """
            
            ai_response = await self.call_ai(prompt, system_prompt)
            
            # Check if AI response is valid
            if not ai_response or "AI analysis failed" in ai_response:
                logger.error(f"❌ {self.name}: Invalid AI response: {ai_response}")
                raise Exception(f"AI returned invalid response: {ai_response}")
            
            # Try to parse JSON response
            try:
                result = json.loads(ai_response)
                
                # Add analysis metadata
                result.update({
                    "agent_name": self.name,
                    "analysis_type": "future_projection",
                    "timestamp": "2025-01-23T19:33:28+05:30",
                    "current_net_worth": net_worth,
                    "current_investment_returns": f"{current_returns:.1f}%",
                    "projection_methodology": "AI-powered scenario modeling based on current patterns"
                })
                
                return result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON from Future Projection AI response")
                return {
                    "projections": {
                        "5_years": {
                            "conservative": f"₹{net_worth * 1.3 / 100000:.1f} lakhs",
                            "realistic": f"₹{net_worth * 1.6 / 100000:.1f} lakhs",
                            "optimistic": f"₹{net_worth * 2.0 / 100000:.1f} lakhs"
                        }
                    },
                    "key_insights": [ai_response[:200] + "..." if len(ai_response) > 200 else ai_response],
                    "acceleration_opportunities": ["Detailed analysis available in full report"],
                    "most_likely_scenario": "AI projection completed - see detailed analysis",
                    "confidence_level": 0.75,
                    "agent_name": self.name,
                    "analysis_type": "future_projection",
                    "timestamp": "2025-01-23T19:33:28+05:30"
                }
                
        except Exception as e:
            logger.error(f"Future Projection analysis failed: {e}")
            return {
                "projections": {"5_years": {"realistic": "Analysis unavailable"}},
                "key_insights": [f"Projection analysis failed: {str(e)}"],
                "acceleration_opportunities": ["Please try again later"],
                "most_likely_scenario": "Analysis temporarily unavailable",
                "confidence_level": 0.0,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "future_projection",
                "timestamp": "2025-01-23T19:33:28+05:30"
            }