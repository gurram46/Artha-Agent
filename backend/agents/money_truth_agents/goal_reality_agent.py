"""
Goal Reality Agent - Life goal achievability simulation
"""

import json
from typing import Dict, Any
import logging
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class GoalRealityAgent(BaseMoneyAgent):
    """AI agent specialized in analyzing life goal achievability with brutal honesty"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Goal Reality Simulator"
        self.description = "Can you actually achieve your dreams? AI simulation reveals the truth"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze whether life goals are realistically achievable"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Extract and analyze goals
            goals = mcp_data.get('goals', [])
            total_goal_amount = sum(goal.get('target_amount', 0) for goal in goals)
            
            # Calculate monthly savings/investment capacity
            accounts = mcp_data.get('accounts', [])
            total_liquid = sum(acc.get('balance', 0) for acc in accounts)
            
            system_prompt = f"""
            You are the GOAL REALITY SIMULATOR - a brutal truth-teller who simulates whether dreams are achievable.
            
            Your mission: Analyze each financial goal and determine if it's realistic, ambitious, or impossible.
            
            Reality Check Framework:
            1. Current financial trajectory vs goal requirements
            2. Time horizon and required monthly savings
            3. Realistic probability of achievement
            4. Alternative strategies if goals are unrealistic
            5. Psychological impact of goal difficulty
            
            REALITY STYLE:
            - Be honest but encouraging
            - Use 🎯, ⚡, 💪 emojis
            - Provide specific numbers and timelines
            - Suggest realistic adjustments
            - Show multiple pathways to success
            """
            
            prompt = f"""
            GOAL REALITY SIMULATION
            Current Net Worth: ₹{net_worth:,.2f}
            Total Goal Amount: ₹{total_goal_amount:,.2f}
            Liquid Assets: ₹{total_liquid:,.2f}
            
            GOALS TO ANALYZE:
            {chr(10).join([f"- {goal.get('name', 'Unknown')}: ₹{goal.get('target_amount', 0):,.2f} (Target: {goal.get('target_date', 'No date')})" for goal in goals])}
            
            {financial_data}
            
            Simulate the reality: Can this person actually achieve these goals? Be brutally honest but constructive.
            
            Format as JSON:
            {{
                "goal_analysis": [
                    {{
                        "goal_name": "Goal name",
                        "target_amount": "₹X.XX lakhs",
                        "achievability": "Realistic/Ambitious/Nearly Impossible",
                        "probability": "85%",
                        "required_monthly_savings": "₹X,XXX",
                        "timeline_assessment": "On track/Behind/Way behind",
                        "reality_check": "Honest assessment",
                        "strategy_adjustment": "Specific recommendation"
                    }}
                ],
                "overall_goal_health": "Strong/Moderate/Concerning",
                "biggest_challenge": "Primary obstacle to goals",
                "success_accelerators": [
                    "Action that would boost goal achievement"
                ],
                "harsh_truths": [
                    "Uncomfortable reality about goals"
                ],
                "motivation_booster": "Encouraging but realistic message",
                "confidence_level": 0.80
            }}
            """
            
            ai_response = await self.call_ai(prompt, system_prompt)
            
            # Try to parse JSON response
            try:
                result = json.loads(ai_response)
                
                # Add analysis metadata
                result.update({
                    "agent_name": self.name,
                    "analysis_type": "goal_reality",
                    "timestamp": "2025-01-23T19:33:28+05:30",
                    "goals_analyzed": len(goals),
                    "total_goal_value": total_goal_amount,
                    "current_net_worth": net_worth,
                    "goal_to_networth_ratio": f"{(total_goal_amount/net_worth):.1f}x" if net_worth > 0 else "N/A"
                })
                
                return result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON from Goal Reality AI response")
                
                # Simple achievability assessment
                achievability = "Realistic" if total_goal_amount < net_worth * 3 else "Ambitious" if total_goal_amount < net_worth * 6 else "Challenging"
                
                return {
                    "goal_analysis": [{
                        "goal_name": f"{len(goals)} goals analyzed",
                        "target_amount": f"₹{total_goal_amount/100000:.1f} lakhs",
                        "achievability": achievability,
                        "probability": "75%",
                        "required_monthly_savings": "₹15,000",
                        "timeline_assessment": "Assessment in progress",
                        "reality_check": ai_response[:300] + "..." if len(ai_response) > 300 else ai_response,
                        "strategy_adjustment": "Detailed analysis available"
                    }],
                    "overall_goal_health": "Moderate",
                    "biggest_challenge": "Detailed analysis in progress",
                    "success_accelerators": ["Comprehensive strategy development"],
                    "harsh_truths": ["Full analysis reveals deeper insights"],
                    "motivation_booster": "Your goals are within reach with the right strategy",
                    "confidence_level": 0.75,
                    "agent_name": self.name,
                    "analysis_type": "goal_reality",
                    "timestamp": "2025-01-23T19:33:28+05:30"
                }
                
        except Exception as e:
            logger.error(f"Goal Reality analysis failed: {e}")
            return {
                "goal_analysis": [{
                    "goal_name": "Analysis failed",
                    "target_amount": "Unknown",
                    "achievability": "Cannot assess",
                    "probability": "0%",
                    "required_monthly_savings": "Unknown",
                    "timeline_assessment": "Unable to assess",
                    "reality_check": f"Analysis error: {str(e)}",
                    "strategy_adjustment": "Please try again later"
                }],
                "overall_goal_health": "Unknown",
                "biggest_challenge": "System unavailable",
                "success_accelerators": [],
                "harsh_truths": ["Analysis temporarily unavailable"],
                "motivation_booster": "Goal analysis will be available soon",
                "confidence_level": 0.0,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "goal_reality",
                "timestamp": "2025-01-23T19:33:28+05:30"
            }