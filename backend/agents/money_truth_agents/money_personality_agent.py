"""
Money Personality Agent - Deep psychological analysis of financial behavior
"""

import json
from typing import Dict, Any
import logging
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class MoneyPersonalityAgent(BaseMoneyAgent):
    """AI agent specialized in analyzing money personality and financial psychology"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Money Psychology Expert"
        self.description = "What your financial behavior reveals about your wealth potential"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze money personality and psychological patterns"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Analyze behavioral patterns
            accounts = mcp_data.get('accounts', [])
            mutual_funds = mcp_data.get('mutual_funds', [])
            stocks = mcp_data.get('stocks', [])
            loans = mcp_data.get('loans', [])
            
            # Calculate behavior indicators
            cash_to_investment_ratio = sum(acc.get('balance', 0) for acc in accounts) / (sum(fund.get('current_value', 0) for fund in mutual_funds) + 1)
            investment_diversity = len(mutual_funds) + len(stocks)
            debt_to_asset_ratio = sum(loan.get('outstanding_amount', 0) for loan in loans) / (net_worth + 1)
            
            system_prompt = f"""
            You are the MONEY PSYCHOLOGY EXPERT - a financial therapist who reads personalities through money patterns.
            
            Your mission: Analyze financial behavior patterns to reveal deep personality insights about money.
            
            Personality Framework:
            1. Money Archetype (Saver, Spender, Investor, Risk-taker, etc.)
            2. Deep psychological drivers and fears
            3. Wealth creation potential based on personality
            4. Behavioral strengths and blind spots
            5. Personalized growth strategies
            
            PSYCHOLOGY STYLE:
            - Use psychological insights and terminology
            - Use 🧠, 💭, 🎭 emojis
            - Be specific about behavioral patterns
            - Connect patterns to wealth potential
            - Provide personality-based recommendations
            """
            
            prompt = f"""
            MONEY PERSONALITY ANALYSIS
            Net Worth: ₹{net_worth:,.2f}
            Cash/Investment Ratio: {cash_to_investment_ratio:.1f}
            Investment Diversity: {investment_diversity} different instruments
            Debt/Asset Ratio: {debt_to_asset_ratio:.2f}
            
            BEHAVIORAL PATTERNS:
            - Account Balances: {len(accounts)} accounts
            - Investment Portfolio: {len(mutual_funds)} MFs, {len(stocks)} stocks
            - Debt Profile: {len(loans)} loans
            
            {financial_data}
            
            What does this financial behavior reveal about their money personality? What's their wealth creation potential?
            
            Format as JSON:
            {{
                "money_archetype": "Primary personality type",
                "archetype_confidence": 0.85,
                "personality_profile": {{
                    "core_traits": [
                        "Key personality trait related to money"
                    ],
                    "money_fears": [
                        "Deep fear or anxiety about money"
                    ],
                    "wealth_drivers": [
                        "What motivates their financial decisions"
                    ],
                    "blind_spots": [
                        "Areas where personality limits growth"
                    ]
                }},
                "behavioral_patterns": [
                    {{
                        "pattern": "Specific behavior observed",
                        "psychological_meaning": "What this reveals about mindset",
                        "wealth_impact": "How this affects wealth building"
                    }}
                ],
                "wealth_potential": {{
                    "natural_strengths": ["Personality-based advantages"],
                    "growth_limiters": ["Psychological barriers"],
                    "potential_rating": "High/Medium/Low",
                    "timeline_to_optimize": "X months to overcome barriers"
                }},
                "personalized_strategy": [
                    "Personality-specific recommendation"
                ],
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
                    "analysis_type": "money_personality",
                    "timestamp": "2025-01-23T19:33:28+05:30",
                    "behavioral_indicators": {
                        "cash_investment_ratio": f"{cash_to_investment_ratio:.1f}",
                        "investment_diversity_score": investment_diversity,
                        "debt_ratio": f"{debt_to_asset_ratio:.2f}",
                        "financial_complexity": len(accounts) + len(mutual_funds) + len(stocks) + len(loans)
                    }
                })
                
                return result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON from Money Personality AI response")
                
                # Simple archetype determination
                if cash_to_investment_ratio > 2:
                    archetype = "Conservative Saver"
                elif investment_diversity > 5:
                    archetype = "Diversified Investor"
                elif debt_to_asset_ratio > 0.3:
                    archetype = "Leveraged Risk-Taker"
                else:
                    archetype = "Balanced Builder"
                
                return {
                    "money_archetype": archetype,
                    "archetype_confidence": 0.75,
                    "personality_profile": {
                        "core_traits": ["Detailed analysis in progress"],
                        "money_fears": ["Assessment underway"],
                        "wealth_drivers": ["Pattern recognition active"],
                        "blind_spots": ["Behavioral analysis ongoing"]
                    },
                    "behavioral_patterns": [{
                        "pattern": "Financial behavior patterns detected",
                        "psychological_meaning": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                        "wealth_impact": "Impact assessment in progress"
                    }],
                    "wealth_potential": {
                        "natural_strengths": ["Comprehensive analysis available"],
                        "growth_limiters": ["Detailed insights provided"],
                        "potential_rating": "Medium",
                        "timeline_to_optimize": "3-6 months"
                    },
                    "personalized_strategy": ["Strategy development in progress"],
                    "confidence_level": 0.75,
                    "agent_name": self.name,
                    "analysis_type": "money_personality",
                    "timestamp": "2025-01-23T19:33:28+05:30"
                }
                
        except Exception as e:
            logger.error(f"Money Personality analysis failed: {e}")
            return {
                "money_archetype": "Analysis unavailable",
                "archetype_confidence": 0.0,
                "personality_profile": {
                    "core_traits": [f"Analysis failed: {str(e)}"],
                    "money_fears": ["System unavailable"],
                    "wealth_drivers": ["Please try again later"],
                    "blind_spots": ["Analysis pending"]
                },
                "behavioral_patterns": [{
                    "pattern": "Unable to analyze patterns",
                    "psychological_meaning": "System error occurred",
                    "wealth_impact": "Cannot assess currently"
                }],
                "wealth_potential": {
                    "natural_strengths": [],
                    "growth_limiters": ["Analysis unavailable"],
                    "potential_rating": "Unknown",
                    "timeline_to_optimize": "Unknown"
                },
                "personalized_strategy": ["Please retry analysis"],
                "confidence_level": 0.0,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "money_personality",
                "timestamp": "2025-01-23T19:33:28+05:30"
            }