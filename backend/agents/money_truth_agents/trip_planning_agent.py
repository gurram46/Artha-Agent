"""
Trip Planning Agent - Financial-aware AI travel planning with budget optimization
"""

import json
from typing import Dict, Any
import logging
from datetime import datetime
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class TripPlanningAgent(BaseMoneyAgent):
    """AI agent specialized in financially-aware trip planning and budget optimization"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Smart Trip Planner"
        self.description = "AI-powered travel planning with personalized budget analysis"
    
    def _create_welcome_message(self, available_for_travel: float, recommended_budget: float) -> str:
        """Create welcome message without f-string backslashes"""
        if available_for_travel <= 0:
            status_msg = "🚨 Focus on savings first - very limited travel budget"
        elif available_for_travel <= 1000:
            status_msg = "⚠️ Limited budget - consider local day trips"
        elif available_for_travel <= 5000:
            status_msg = "💡 Budget travel options - local weekend getaways recommended"
        elif available_for_travel <= 15000:
            status_msg = "🎯 Moderate budget - good for short trips and budget vacations"
        else:
            status_msg = "✅ Ready for travel adventures!"
        
        return f"""🧳 **Welcome to Smart Trip Planner!**

I'm your AI travel advisor who knows your finances inside out! 

**Your Travel Budget Summary:**
- Available for Travel: ₹{available_for_travel:,.0f}
- Recommended Budget: ₹{recommended_budget:,.0f}
- Financial Status: {status_msg}

**Let's plan your perfect trip! Tell me:**
- Where would you like to go? 🗺️
- When are you planning to travel? 📅
- How many people will be traveling? 👥
- What type of experience are you looking for? (Adventure, Relaxation, Culture, etc.) 🎯

I'll create a personalized itinerary that fits your budget perfectly! ✈️"""
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize chatbot context for interactive trip planning"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Calculate financial capacity for travel
            accounts = mcp_data.get('accounts', [])
            mutual_funds = mcp_data.get('mutual_funds', [])
            loans = mcp_data.get('loans', [])
            
            liquid_funds = sum(acc.get('balance', 0) for acc in accounts)
            total_investments = sum(fund.get('current_value', 0) for fund in mutual_funds)
            total_debt = sum(loan.get('outstanding_amount', 0) for loan in loans)
            
            # Debug logging
            logger.info(f"🔍 Trip Planning Agent - Liquid funds calculated: ₹{liquid_funds}")
            logger.info(f"🔍 Trip Planning Agent - Accounts data: {accounts}")
            logger.info(f"🔍 Trip Planning Agent - MCP accounts count: {len(accounts)}")
            
            # Realistic travel budget calculation based on actual liquid funds
            # Keep some emergency reserve but be practical about it
            if liquid_funds <= 1000:
                emergency_reserve = liquid_funds * 0.9  # Keep 90% for emergency if very low
                available_for_travel = liquid_funds * 0.1
                recommended_budget = 0
            elif liquid_funds <= 5000:
                emergency_reserve = 1000  # Keep ₹1K emergency if funds are low
                available_for_travel = liquid_funds - emergency_reserve
                recommended_budget = max(0, available_for_travel * 0.3)  # 30% of available for budget trips
            elif liquid_funds <= 15000:
                emergency_reserve = 2000  # Keep ₹2K emergency for moderate funds
                available_for_travel = liquid_funds - emergency_reserve
                recommended_budget = max(0, available_for_travel * 0.5)  # 50% of available
            else:
                emergency_reserve = 5000  # Keep ₹5K emergency for higher funds
                available_for_travel = liquid_funds - emergency_reserve
                recommended_budget = min(
                    max(available_for_travel * 0.7, 5000),  # 70% of available or min ₹5K
                    50000  # Maximum ₹50K for conservative planning
                )
            
            # Financial health indicators
            debt_to_asset_ratio = total_debt / (net_worth + 1) if net_worth > 0 else 1
            liquidity_ratio = liquid_funds / (total_investments + 1) if total_investments > 0 else 0
            
            # Return chatbot initialization data
            return {
                "chatbot_mode": True,
                "agent_name": self.name,
                "analysis_type": "trip_planning_chat",
                "timestamp": datetime.now().isoformat(),
                "financial_context": {
                    "net_worth": net_worth,
                    "liquid_funds": liquid_funds,
                    "available_for_travel": available_for_travel,
                    "recommended_budget": recommended_budget,
                    "emergency_reserve": emergency_reserve,
                    "debt_ratio": debt_to_asset_ratio,
                    "liquidity_ratio": liquidity_ratio,
                    "financial_readiness": "ready" if available_for_travel > 15000 else "moderate" if available_for_travel > 1000 else "limited",
                    "formatted_data": financial_data
                },
                "welcome_message": self._create_welcome_message(available_for_travel, recommended_budget)
            }
                
        except Exception as e:
            logger.error(f"Trip Planning chatbot initialization failed: {e}")
            return {
                "chatbot_mode": True,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "trip_planning_chat",
                "timestamp": datetime.now().isoformat(),
                "welcome_message": f"🧳 **Trip Planning Assistant**\n\nI'm having trouble accessing your financial data right now.\n\n**Error:** {str(e)}\n\nPlease ensure you're authenticated with Fi Money to get personalized budget recommendations. Without your financial data, I cannot provide accurate travel budget advice."
            }
    
    async def chat_response(self, user_message: str, financial_context: Dict[str, Any], conversation_history: list = None) -> str:
        """Handle interactive chat for trip planning with conversation memory"""
        try:
            system_prompt = """
            You are a Smart Trip Planner 🧳 - an interactive AI travel advisor with access to the user's financial data.
            
            PERSONALITY:
            - Friendly, enthusiastic, and budget-conscious
            - Use travel emojis frequently: 🧳 ✈️ 🏨 🚗 🎯 💡 🗺️ 📅 👥
            - Always consider the user's financial capacity
            - Provide practical, actionable advice
            - REMEMBER previous conversation context and build upon it
            
            FINANCIAL AWARENESS:
            - Always use Indian Rupees (₹) NEVER dollars ($)
            - Keep recommendations within the user's recommended budget
            - Suggest cost-saving tips and alternatives
            - Break down costs clearly: Transport, Stay, Food, Activities
            
            CONVERSATION STYLE:
            - Remember what the user has already told you
            - Build upon previous information instead of asking for it again
            - Provide specific recommendations with costs when you have enough details
            - Offer multiple options (budget/mid-range/premium)
            - Be encouraging and helpful
            
            TRIP PLANNING APPROACH:
            1. Build on previous conversation details
            2. Ask for missing information only
            3. Suggest detailed itinerary when you have: destination, dates, group size
            4. Provide cost breakdowns
            5. Offer money-saving tips and booking strategies
            """
            
            # Include financial context in the prompt
            available_budget = financial_context.get('available_for_travel', 0)
            recommended_budget = financial_context.get('recommended_budget', 0)
            financial_status = financial_context.get('financial_readiness', 'moderate')
            
            # Build conversation context
            conversation_context = ""
            if conversation_history:
                conversation_context = "**Previous Conversation:**\n"
                for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                    role = "User" if msg.get('type') == 'user' else "Assistant"
                    conversation_context += f"{role}: {msg.get('content', '')}\n"
                conversation_context += "\n"
            
            prompt = f"""
            **User's Financial Context:**
            - Available for Travel: ₹{available_budget:,.0f}
            - Recommended Safe Budget: ₹{recommended_budget:,.0f}
            - Financial Readiness: {financial_status}
            
            {conversation_context}**Current User Message:** {user_message}
            
            Based on the conversation history above, respond as a friendly trip planning assistant who remembers what the user has already shared. Build upon the previous information and provide specific recommendations when you have enough details. Don't ask for information the user has already provided!
            """
            
            ai_response = await self.call_ai(prompt, system_prompt)
            return ai_response
            
        except Exception as e:
            logger.error(f"Trip planning chat response failed: {e}")
            return "🧳 Sorry, I'm having a bit of trouble right now! But I'm still here to help with your trip planning. Could you tell me more about where you would like to go? ✈️"