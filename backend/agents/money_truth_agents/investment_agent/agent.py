# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Investment coordinator: provide personalized investment recommendations for Indian markets"""

import asyncio
import json
from typing import Dict, Any, Optional
import logging
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from google.adk import Agent
from google import genai
from google.genai import types
from core.fi_mcp.production_client import get_user_financial_data

# Import sub-agents
from .sub_agents.data_analyst.agent import data_analyst_agent
from .sub_agents.trading_analyst.agent import trading_analyst_agent
from .sub_agents.execution_analyst.agent import execution_analyst_agent
from .sub_agents.risk_analyst.agent import risk_analyst_agent

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


class InvestmentCoordinator:
    """Investment coordinator using real Fi Money MCP data and direct Gemini API calls"""
    
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.name = "investment_coordinator"
        self.description = (
            "provide personalized investment recommendations for Indian markets "
            "by orchestrating a series of expert subagents. analyze user's "
            "financial data from Fi Money MCP, assess risk profile, research "
            "investment opportunities, and propose tailored investment plans."
        )
        
        # AI configuration
        self.config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=3000,
            top_p=0.8,
            top_k=40
        )
    
    async def call_ai(self, prompt: str, system_prompt: str = "") -> str:
        """Call Gemini AI with proper error handling"""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model=MODEL,
                contents=full_prompt,
                config=self.config
            )
            
            # Extract text from response
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        return candidate.content.parts[0].text
            
            return "AI analysis failed: No response generated"
            
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return f"AI analysis failed: {str(e)}"
    
    async def get_fi_money_data(self) -> Dict[str, Any]:
        """Get real-time Fi Money MCP data"""
        try:
            financial_data = await get_user_financial_data()
            
            # Structure data for investment analysis
            return {
                "net_worth": financial_data.net_worth,
                "credit_report": financial_data.credit_report,
                "epf_details": financial_data.epf_details,
                "mf_transactions": financial_data.mf_transactions,
                "bank_transactions": financial_data.bank_transactions,
                "total_net_worth": financial_data.get_total_net_worth(),
                "assets_breakdown": financial_data.get_assets_breakdown(),
                "liabilities_breakdown": financial_data.get_liabilities_breakdown()
            }
        except Exception as e:
            logger.error(f"Failed to get Fi Money data: {e}")
            raise
    
    async def analyze_user_portfolio(self, fi_data: Dict[str, Any]) -> str:
        """Data analyst agent functionality using real Fi Money data"""
        from .sub_agents.data_analyst.prompt import DATA_ANALYST_PROMPT
        
        prompt = f"""
        {DATA_ANALYST_PROMPT}
        
        Real Fi Money User Data:
        {json.dumps(fi_data, indent=2, default=str)}
        
        Analyze this user's financial data and provide investment insights.
        """
        
        return await self.call_ai(prompt)
    
    async def generate_investment_strategies(self, fi_data: Dict[str, Any], market_analysis: str) -> str:
        """Trading analyst agent functionality"""
        from .sub_agents.trading_analyst.prompt import TRADING_ANALYST_PROMPT
        
        prompt = f"""
        {TRADING_ANALYST_PROMPT}
        
        User Financial Data:
        {json.dumps(fi_data, indent=2, default=str)}
        
        Market Analysis:
        {market_analysis}
        
        Generate specific investment strategies for this user.
        """
        
        return await self.call_ai(prompt)
    
    async def create_execution_plan(self, strategies: str, fi_data: Dict[str, Any]) -> str:
        """Execution analyst agent functionality"""
        from .sub_agents.execution_analyst.prompt import EXECUTION_ANALYST_PROMPT
        
        prompt = f"""
        {EXECUTION_ANALYST_PROMPT}
        
        Investment Strategies:
        {strategies}
        
        User Financial Data:
        {json.dumps(fi_data, indent=2, default=str)}
        
        Create detailed execution plan.
        """
        
        return await self.call_ai(prompt)
    
    async def assess_risks(self, strategies: str, execution_plan: str, fi_data: Dict[str, Any]) -> str:
        """Risk analyst agent functionality"""
        from .sub_agents.risk_analyst.prompt import RISK_ANALYST_PROMPT
        
        prompt = f"""
        {RISK_ANALYST_PROMPT}
        
        Investment Strategies:
        {strategies}
        
        Execution Plan:
        {execution_plan}
        
        User Financial Data:
        {json.dumps(fi_data, indent=2, default=str)}
        
        Provide comprehensive risk assessment.
        """
        
        return await self.call_ai(prompt)
    
    async def coordinate_investment_analysis(self) -> Dict[str, Any]:
        """Main coordination function using real Fi Money MCP data"""
        try:
            logger.info("🚀 Starting investment analysis with real Fi Money MCP data")
            
            # Get real Fi Money data
            fi_data = await self.get_fi_money_data()
            logger.info(f"📊 Fi Money data retrieved: Net Worth ₹{fi_data['total_net_worth']:,.2f}")
            
            # Run sub-agents in sequence (as per original design)
            logger.info("🔍 Running data analyst...")
            market_analysis = await self.analyze_user_portfolio(fi_data)
            
            logger.info("📈 Running trading analyst...")
            investment_strategies = await self.generate_investment_strategies(fi_data, market_analysis)
            
            logger.info("⚡ Running execution analyst...")
            execution_plan = await self.create_execution_plan(investment_strategies, fi_data)
            
            logger.info("⚠️ Running risk analyst...")
            risk_assessment = await self.assess_risks(investment_strategies, execution_plan, fi_data)
            
            # Final coordination
            from .prompt import INVESTMENT_COORDINATOR_PROMPT
            
            final_prompt = f"""
            {INVESTMENT_COORDINATOR_PROMPT}
            
            User Financial Data (Real Fi Money MCP):
            {json.dumps(fi_data, indent=2, default=str)}
            
            Market Analysis:
            {market_analysis}
            
            Investment Strategies:
            {investment_strategies}
            
            Execution Plan:
            {execution_plan}
            
            Risk Assessment:
            {risk_assessment}
            
            Provide final investment recommendation coordinating all agent outputs.
            """
            
            final_recommendation = await self.call_ai(final_prompt)
            
            result = {
                "user_data": fi_data,
                "analyses": {
                    "market_analysis": market_analysis,
                    "investment_strategies": investment_strategies,
                    "execution_plan": execution_plan,
                    "risk_assessment": risk_assessment
                },
                "final_recommendation": final_recommendation,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            logger.info("✅ Investment analysis coordination completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Investment coordination failed: {e}")
            raise


# Create the coordinator instance
def create_investment_coordinator(gemini_client):
    return InvestmentCoordinator(gemini_client)

# Load the main coordinator prompt
from . import prompt

# Create Google ADK root agent for compatibility with original structure
root_agent = Agent(
    model=MODEL,
    name="investment_coordinator",
    instruction=prompt.INVESTMENT_COORDINATOR_PROMPT,
    output_key="investment_recommendation_output",
    sub_agents=[
        data_analyst_agent,
        trading_analyst_agent, 
        execution_analyst_agent,
        risk_analyst_agent
    ]
)
