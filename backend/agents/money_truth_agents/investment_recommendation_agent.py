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
from .investment_agent.agent import root_agent
from services.broker_integration import broker_service

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
        self.investment_coordinator = root_agent
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive investment analysis using the 4-agent sequential flow"""
        logger.info("🚀 Starting investment analysis with real Fi Money MCP data...")
        
        try:
            # Prepare financial context from MCP data
            financial_context = {
                "user_financial_profile": mcp_data,
                "investment_amount": 50000,  # Default amount, can be customized
                "investment_goals": "Long-term wealth creation with balanced risk approach"
            }
            
            # STEP 1: Data Analyst Agent
            logger.info("📊 Step 1: Running Data Analyst Agent...")
            from .investment_agent.sub_agents.data_analyst.prompt import DATA_ANALYST_PROMPT
            data_analyst_prompt = f"""
            {DATA_ANALYST_PROMPT}
            
            User Financial Data (Real Fi Money MCP):
            {json.dumps(financial_context, indent=2, default=str)}
            
            Analyze current market conditions and provide comprehensive market research.
            """
            data_analyst_output = await self.call_ai(data_analyst_prompt)
            logger.info(f"✅ Data Analyst completed ({len(data_analyst_output)} chars)")
            
            # STEP 2: Execution Analyst Agent  
            logger.info("⚙️ Step 2: Running Execution Analyst Agent...")
            from .investment_agent.sub_agents.execution_analyst.prompt import EXECUTION_ANALYST_PROMPT
            execution_analyst_prompt = f"""
            {EXECUTION_ANALYST_PROMPT}
            
            Data Analyst Output:
            {data_analyst_output}
            
            User Financial Data:
            {json.dumps(financial_context, indent=2, default=str)}
            
            Create detailed execution strategies based on the market analysis.
            """
            execution_analyst_output = await self.call_ai(execution_analyst_prompt)
            logger.info(f"✅ Execution Analyst completed ({len(execution_analyst_output)} chars)")
            
            # STEP 3: Risk Analyst Agent
            logger.info("🛡️ Step 3: Running Risk Analyst Agent...")
            from .investment_agent.sub_agents.risk_analyst.prompt import RISK_ANALYST_PROMPT
            risk_analyst_prompt = f"""
            {RISK_ANALYST_PROMPT}
            
            Data Analyst Output:
            {data_analyst_output}
            
            Execution Analyst Output:
            {execution_analyst_output}
            
            User Financial Data:
            {json.dumps(financial_context, indent=2, default=str)}
            
            Assess risks and validate the proposed strategies.
            """
            risk_analyst_output = await self.call_ai(risk_analyst_prompt)
            logger.info(f"✅ Risk Analyst completed ({len(risk_analyst_output)} chars)")
            
            # STEP 4: Trading Analyst Agent (Final Recommendations)
            logger.info("📈 Step 4: Running Trading Analyst Agent...")
            from .investment_agent.sub_agents.trading_analyst.prompt import TRADING_ANALYST_PROMPT
            trading_analyst_prompt = f"""
            {TRADING_ANALYST_PROMPT}
            
            Data Analyst Output:
            {data_analyst_output}
            
            Execution Analyst Output:
            {execution_analyst_output}
            
            Risk Analyst Output:
            {risk_analyst_output}
            
            User Financial Data:
            {json.dumps(financial_context, indent=2, default=str)}
            
            Generate final comprehensive investment recommendations based on all previous analyses.
            """
            trading_analyst_output = await self.call_ai(trading_analyst_prompt)
            logger.info(f"✅ Trading Analyst completed ({len(trading_analyst_output)} chars)")
            
            # Parse investment recommendations for Invest Now feature
            parsed_investments = broker_service.parse_investment_recommendations(trading_analyst_output)
            logger.info(f"📊 Parsed {len(parsed_investments)} actionable investments")
            
            # Generate broker URLs for immediate execution
            broker_urls = None
            if parsed_investments:
                broker_urls = broker_service.generate_broker_urls(parsed_investments, "groww")
                logger.info(f"🔗 Generated investment URLs for {broker_urls.get('total_investments', 0)} investments")
            
            # Enhance with BaseMoneyAgent capabilities
            net_worth = self.calculate_net_worth(mcp_data)
            formatted_data = self.format_financial_data(mcp_data)
            
            # Create comprehensive result following BaseMoneyAgent pattern
            enhanced_result = {
                "analysis_type": "Investment Recommendations (4-Agent Flow)",
                "timestamp": datetime.now().isoformat(),
                "net_worth": net_worth,
                "formatted_financial_data": formatted_data,
                "agent_outputs": {
                    "data_analyst": data_analyst_output,
                    "execution_analyst": execution_analyst_output,
                    "risk_analyst": risk_analyst_output,
                    "trading_analyst": trading_analyst_output
                },
                "investment_analysis": {
                    "final_recommendation": trading_analyst_output,
                    "personalized_plan": trading_analyst_output,  # For frontend compatibility
                    "actionable_investments": parsed_investments,
                    "invest_now_urls": broker_urls
                },
                "key_insights": [
                    f"Total Net Worth: ₹{net_worth:,.2f}",
                    f"4-agent sequential analysis completed",
                    "Market research → Execution planning → Risk assessment → Final recommendations",
                    "Comprehensive analysis with Sandeep-Artha prompt engineering"
                ],
                "recommendations": {
                    "immediate_actions": [
                        "Review investment strategies based on real financial data",
                        "Choose strategy matching risk profile",
                        "Use 'Invest Now' feature for immediate execution",
                        "Complete platform KYC if needed",
                        "Start recommended SIP investments"
                    ],
                    "monitoring": [
                        "Monthly portfolio review", 
                        "Quarterly rebalancing",
                        "Annual strategy adjustment"
                    ],
                    "invest_now_available": broker_urls is not None,
                    "supported_brokers": ["Groww", "Zerodha", "Angel One", "Upstox", "IIFL", "Paytm Money"]
                }
            }
            
            logger.info(f"✅ 4-agent investment analysis completed")
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
    
    async def get_broker_execution_plan(self, recommendation_text: str, preferred_broker: str = "groww") -> Dict[str, Any]:
        """Generate broker-specific execution plan for immediate investment"""
        try:
            logger.info(f"🚀 Generating broker execution plan for {preferred_broker}")
            
            # Parse investments from recommendation
            parsed_investments = broker_service.parse_investment_recommendations(recommendation_text)
            
            if not parsed_investments:
                return {
                    "error": "No actionable investments found in recommendations",
                    "suggestion": "Please ensure the recommendation includes specific fund names and amounts"
                }
            
            # Generate broker URLs and execution plan
            broker_plan = broker_service.generate_broker_urls(parsed_investments, preferred_broker)
            
            # Add broker comparison
            broker_comparison = broker_service.get_broker_comparison()
            
            return {
                "execution_plan": broker_plan,
                "broker_comparison": broker_comparison,
                "total_investments": len(parsed_investments),
                "investment_summary": [
                    f"{inv['name']}: ₹{inv['amount']:,}" 
                    for inv in parsed_investments
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate broker execution plan: {e}")
            return {"error": f"Failed to generate execution plan: {str(e)}"}
    
    async def execute_investments(self, broker_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute investments by launching broker platforms"""
        try:
            if "investment_urls" not in broker_plan:
                return {"error": "No investment URLs available"}
            
            # Launch broker platform
            success = broker_service.launch_investment_platform(broker_plan)
            
            return {
                "success": success,
                "message": "Investment platforms opened in browser" if success else "Failed to open platforms",
                "next_steps": broker_plan.get("next_steps", []),
                "total_investments": broker_plan.get("total_investments", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to execute investments: {e}")
            return {"error": f"Failed to execute investments: {str(e)}"}