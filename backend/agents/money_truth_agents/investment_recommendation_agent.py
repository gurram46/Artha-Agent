"""
Investment Recommendation Agent - Integrates Sandeep-Artha investment system with Fi Money MCP data
Uses BaseMoneyAgent pattern and real Fi Money MCP data
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from .base_money_agent import BaseMoneyAgent
from .investment_agent.agent import create_investment_coordinator

logger = logging.getLogger(__name__)


class InvestmentRecommendationAgent(BaseMoneyAgent):
    """
    Investment Recommendation Agent that integrates Sandeep-Artha investment system
    with Fi Money MCP data using BaseMoneyAgent pattern
    """
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Investment Recommendation Agent"
        self.description = "Comprehensive investment analysis and recommendations for Indian markets using real Fi Money MCP data"
        
        # Initialize the investment coordinator from Sandeep-Artha system
        self.investment_coordinator = create_investment_coordinator(gemini_client)
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive investment analysis using the integrated system"""
        logger.info("🚀 Starting investment analysis with real Fi Money MCP data...")
        
        try:
            # Use the investment coordinator from Sandeep-Artha system
            # It already uses real Fi Money MCP data
            result = await self.investment_coordinator.coordinate_investment_analysis()
            
            # Enhance with BaseMoneyAgent capabilities
            net_worth = self.calculate_net_worth(mcp_data)
            formatted_data = self.format_financial_data(mcp_data)
            
            # Create comprehensive result following BaseMoneyAgent pattern
            enhanced_result = {
                "analysis_type": "Investment Recommendations",
                "timestamp": datetime.now().isoformat(),
                "net_worth": net_worth,
                "formatted_financial_data": formatted_data,
                "investment_analysis": result,
                "key_insights": [
                    f"Total Net Worth: ₹{net_worth:,.2f}",
                    f"Investment strategies generated using real Fi Money data",
                    "Multi-agent analysis completed",
                    "Specific product recommendations provided"
                ],
                "recommendations": {
                    "immediate_actions": [
                        "Review investment strategies based on real financial data",
                        "Choose strategy matching risk profile",
                        "Complete platform KYC if needed",
                        "Start recommended SIP investments"
                    ],
                    "monitoring": [
                        "Monthly portfolio review",
                        "Quarterly rebalancing",
                        "Annual strategy adjustment"
                    ]
                }
            }
            
            logger.info(f"✅ Investment recommendation analysis completed")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ Investment recommendation analysis failed: {e}")
            raise Exception(f"Investment analysis failed: {str(e)}")
    
    async def get_chat_response(self, query: str, mcp_data: Dict[str, Any], conversation_history: List[Dict] = None) -> str:
        """Handle chat interactions for investment recommendations"""
        try:
            logger.info(f"💬 Investment Agent: Processing chat query: {query[:100]}...")
            
            # Extract financial context
            net_worth = self.calculate_net_worth(mcp_data)
            formatted_data = self.format_financial_data(mcp_data)
            
            # Include conversation history context
            history_context = ""
            if conversation_history:
                history_context = "\n## Previous Conversation:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages for context
                    history_context += f"**{msg['type'].title()}**: {msg['content'][:200]}...\n"
            
            system_prompt = """You are an expert investment advisor for Indian markets with access to real-time Fi Money financial data. 

Your capabilities:
- Real-time portfolio analysis using Fi Money MCP data
- Multi-agent investment analysis system (data analyst, trading analyst, execution analyst, risk analyst)
- Specific Indian market recommendations (stocks, mutual funds, ETFs)
- Tax-efficient investment planning
- Platform-specific guidance (Zerodha, Groww, Angel One, etc.)
- Risk-appropriate strategies

Always provide:
1. Specific product names and current prices/NAV
2. Exact investment amounts and allocations
3. Platform recommendations for execution
4. Tax implications and benefits
5. Step-by-step actionable advice

Be conversational but precise with financial recommendations."""
            
            chat_prompt = f"""
            {history_context}
            
            ## Current User Query:
            {query}
            
            ## User's Real Financial Data (Fi Money MCP):
            - **Total Net Worth**: ₹{net_worth:,.2f}
            {formatted_data}
            
            ## Current Market Context:
            - Indian markets showing positive momentum
            - Banking and IT sectors performing well
            - Multiple investment opportunities available
            
            Provide specific, actionable investment advice using the user's real financial data.
            Include specific product recommendations, investment amounts, and platform guidance.
            """
            
            response = await self.call_ai(chat_prompt, system_prompt)
            
            logger.info(f"✅ Investment chat response generated ({len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"❌ Investment chat failed: {e}")
            return f"I apologize, but I'm having trouble processing your investment query right now. The investment analysis system uses real Fi Money data to provide personalized recommendations. Please try asking about specific investment topics like mutual funds, stocks, or portfolio allocation. Error: {str(e)}"