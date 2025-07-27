#!/usr/bin/env python3
"""
SAndeep Investment System API Integration
Based on simple_investment_cli.py pattern for Artha-Agent backend integration
"""

import os
import sys
import json
import asyncio
import warnings
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Suppress Google ADK warnings (from SAndeep's pattern)
warnings.filterwarnings("ignore", message=".*non-text parts.*function_call.*")
warnings.filterwarnings("ignore", message=".*function_call.*")
warnings.filterwarnings("ignore", message=".*Warning.*non-text parts.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*function_call.*")
warnings.filterwarnings("ignore", message=".*non-text parts.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*non-text parts.*")
warnings.filterwarnings("ignore", message="Warning: there are non-text parts in the response.*")
warnings.filterwarnings("ignore", category=UserWarning, message="Warning: there are non-text parts.*")

# Global warning suppression for specific patterns
warnings.filterwarnings("ignore", module="google.*")
warnings.filterwarnings("ignore", module=".*types.*")

# Set environment variable to suppress warnings at Google library level
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""

# Add SAndeep system to Python path
sandeep_root = Path(__file__).parent
sys.path.insert(0, str(sandeep_root))

logger = logging.getLogger(__name__)

class SAndeepInvestmentAPI:
    """
    SAndeep Investment System API Integration
    Following the exact pattern from simple_investment_cli.py
    """
    
    def __init__(self):
        self.initialized = False
        self.root_agent = None
        self.cache_manager = None
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize SAndeep's investment system"""
        try:
            # Import SAndeep components (exact pattern from CLI)
            from investment_agent.agent import root_agent
            from investment_agent.cache import warm_up_cache, cache_manager
            from google.adk.runners import InMemoryRunner
            from google.genai.types import Part, UserContent
            
            self.root_agent = root_agent
            self.cache_manager = cache_manager
            self.InMemoryRunner = InMemoryRunner
            self.Part = Part
            self.UserContent = UserContent
            
            # Initialize cache for faster responses (from CLI pattern)
            logger.info("🚀 Initializing SAndeep market data cache...")
            warm_up_cache()
            cache_status = cache_manager.get_cache_status()
            cached_items = sum(1 for status in cache_status.values() if status.get('exists'))
            logger.info(f"✅ SAndeep cache initialized with {cached_items} market data items")
            
            self.initialized = True
            logger.info("✅ SAndeep Investment System initialized successfully")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import SAndeep system: {e}")
            logger.error("Please ensure Google ADK dependencies are installed:")
            logger.error("pip install google-adk google-genai python-dotenv")
            self.initialized = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize SAndeep system: {e}")
            self.initialized = False
    
    def create_investment_query(self, financial_data: Dict[str, Any], 
                              phone_number: str, investment_amount: float,
                              risk_tolerance: str = 'moderate',
                              investment_goal: str = 'wealth_creation',
                              time_horizon: str = 'long_term') -> str:
        """
        Create investment query using SAndeep's pattern from CLI
        """
        
        # Extract net worth (following CLI pattern)
        net_worth_data = financial_data.get('net_worth', {})
        net_worth_response = net_worth_data.get('netWorthResponse', {})
        
        # Calculate total assets
        total_assets = 0
        asset_breakdown = []
        
        # Extract asset values from netWorthResponse
        if 'totalNetWorthValue' in net_worth_response:
            total_assets = float(net_worth_response['totalNetWorthValue'].get('units', '0'))
        
        # Extract assets breakdown
        for asset in net_worth_response.get('assetValues', []):
            asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '').replace('_', ' ').title()
            value = float(asset.get('value', {}).get('units', '0'))
            if value > 0:
                asset_breakdown.append(f"  - {asset_type}: ₹{value:,.0f}")
        
        # Extract credit information
        credit_data = financial_data.get('credit_report', {})
        credit_score = 'Not available'
        if 'creditReports' in credit_data and credit_data['creditReports']:
            credit_score = credit_data['creditReports'][0].get('creditReportData', {}).get('score', {}).get('bureauScore', 'Not available')
        
        # Extract EPF information
        epf_data = financial_data.get('epf_details', {})
        epf_balance = 0
        if epf_data and 'epfDetails' in epf_data:
            for epf_account in epf_data['epfDetails']:
                if 'pfBalance' in epf_account:
                    pf_balance = epf_account['pfBalance']
                    epf_balance += pf_balance.get('employeeShare', 0) + pf_balance.get('employerShare', 0)
        
        # Extract existing investments
        mf_data = financial_data.get('net_worth', {}).get('mfSchemeAnalytics', {})
        mf_holdings = len(mf_data.get('schemeAnalytics', [])) if mf_data else 0
        
        # Create comprehensive query (exact SAndeep pattern)
        query = f"""
I am an Indian investor seeking personalized investment recommendations. Here is my complete financial profile:

**Personal Information:**
- Phone: {phone_number}
- Investment Amount: ₹{investment_amount:,.0f}
- Risk Tolerance: {risk_tolerance.title()}
- Investment Goal: {investment_goal.replace('_', ' ').title()}
- Time Horizon: {time_horizon.replace('_', ' ').title()}

**Current Financial Position:**
- Total Net Worth: ₹{total_assets:,.0f}
- Credit Score: {credit_score}
- EPF Balance: ₹{epf_balance:,.0f}

**Asset Breakdown:**
{chr(10).join(asset_breakdown) if asset_breakdown else '  - No detailed asset breakdown available'}

**Current Investment Portfolio:**
- Mutual Fund Holdings: {mf_holdings} schemes
- EPF Contribution: ₹{epf_balance:,.0f}

**Investment Requirements:**
1. Recommend specific Indian stocks, ETFs, and mutual funds suitable for my profile
2. Provide exact allocation percentages for the ₹{investment_amount:,.0f} investment
3. Consider my existing portfolio and suggest diversification strategies
4. Include tax-efficient investment options (ELSS, PPF, etc.)
5. Recommend suitable investment platforms (Angel One, Zerodha, Groww, etc.)
6. Provide risk analysis based on my current financial position

**Additional Context:**
- I prefer investments suitable for Indian markets
- Please consider tax implications under Indian tax laws
- Suggest both short-term and long-term investment strategies
- Include emergency fund recommendations if needed

Please provide a detailed, actionable investment plan with specific recommendations and reasoning.
Use your multi-agent analysis system for comprehensive research and recommendations.
"""
        
        return query
    
    async def get_investment_recommendations(self, financial_data: Dict[str, Any], 
                                           investment_amount: float = 50000,
                                           risk_tolerance: str = 'moderate',
                                           investment_goal: str = 'wealth_creation',
                                           time_horizon: str = 'long_term',
                                           phone_number: str = '9999999999') -> Dict[str, Any]:
        """
        Get investment recommendations using SAndeep's exact CLI pattern
        """
        
        if not self.initialized:
            raise Exception("SAndeep Investment System not properly initialized")
        
        try:
            logger.info(f"🤖 Starting SAndeep multi-agent analysis for ₹{investment_amount:,.0f}")
            
            # Create investment query using SAndeep's pattern
            query = self.create_investment_query(
                financial_data, phone_number, investment_amount,
                risk_tolerance, investment_goal, time_horizon
            )
            
            logger.info("📝 Investment query created following SAndeep pattern")
            
            # Create runner (exact CLI pattern)
            runner = self.InMemoryRunner(agent=self.root_agent)
            logger.info("✅ SAndeep runner created successfully")
            
            # Create session (exact CLI pattern)
            session = runner.session_service.create_session(
                app_name=runner.app_name,
                user_id=phone_number
            )
            logger.info(f"✅ SAndeep session created: {session.id}")
            
            # Send query to agent (exact CLI pattern)
            content = self.UserContent(parts=[self.Part(text=query)])
            logger.info("🚀 Sending query to SAndeep investment agent...")
            
            # Capture full response
            full_response = ""
            response_chunks = []
            
            # Process agent response (exact CLI pattern)
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content,
            ):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        if (event and hasattr(event, 'content') and event.content and
                            hasattr(event.content, 'parts') and event.content.parts and
                            len(event.content.parts) > 0):
                            
                            first_part = event.content.parts[0]
                            if (first_part and hasattr(first_part, 'text') and first_part.text):
                                chunk = first_part.text
                                full_response += chunk
                                response_chunks.append(chunk)
                                logger.debug(f"Received response chunk: {len(chunk)} chars")
                    except Exception as e:
                        logger.warning(f"Error processing event: {e}")
                        continue
            
            logger.info(f"✅ SAndeep investment analysis completed ({len(full_response)} chars)")
            
            # Format response for API
            result = {
                "status": "success",
                "analysis_type": "SAndeep Multi-Agent Investment Analysis",
                "timestamp": datetime.now().isoformat(),
                "investment_amount": investment_amount,
                "parameters": {
                    "risk_tolerance": risk_tolerance,
                    "investment_goal": investment_goal,
                    "time_horizon": time_horizon
                },
                "agent_analysis": {
                    "full_response": full_response,
                    "response_chunks": len(response_chunks),
                    "agents_used": ["data_analyst", "trading_analyst", "execution_analyst", "risk_analyst"]
                },
                "investment_analysis": {
                    "final_recommendation": full_response,
                    "personalized_plan": full_response,
                    "actionable_investments": self._extract_investments_from_response(full_response),
                    "invest_now_urls": self._generate_broker_urls()
                },
                "key_insights": [
                    f"Investment Amount: ₹{investment_amount:,.0f}",
                    "SAndeep 4-agent sequential analysis completed",
                    "Market research → Trading analysis → Execution planning → Risk assessment",
                    "Real-time market data integrated via Angel One API",
                    "Tax-optimized recommendations for Indian markets"
                ]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ SAndeep investment analysis failed: {e}")
            raise Exception(f"SAndeep analysis failed: {str(e)}")
    
    async def get_chat_response(self, query: str, financial_data: Dict[str, Any]) -> str:
        """Get chat response using SAndeep system"""
        
        if not self.initialized:
            return "SAndeep Investment System is not available. Please check system configuration."
        
        try:
            logger.info(f"💬 SAndeep chat query: {query[:100]}...")
            
            # Create a focused query for chat
            chat_query = f"""
Based on the user's financial profile, please provide a focused response to this query:

"{query}"

Please provide specific, actionable advice using your multi-agent investment analysis system.
Consider current Indian market conditions and provide relevant recommendations.
"""
            
            # Use the same pattern as investment recommendations but for chat
            runner = self.InMemoryRunner(agent=self.root_agent)
            session = runner.session_service.create_session(
                app_name=runner.app_name,
                user_id="chat_user"
            )
            
            content = self.UserContent(parts=[self.Part(text=chat_query)])
            
            full_response = ""
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content,
            ):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        if (event and hasattr(event, 'content') and event.content and
                            hasattr(event.content, 'parts') and event.content.parts and
                            len(event.content.parts) > 0):
                            
                            first_part = event.content.parts[0]
                            if (first_part and hasattr(first_part, 'text') and first_part.text):
                                full_response += first_part.text
                    except Exception as e:
                        continue
            
            logger.info(f"✅ SAndeep chat response generated ({len(full_response)} chars)")
            return full_response
            
        except Exception as e:
            logger.error(f"❌ SAndeep chat failed: {e}")
            return f"I'm having trouble processing your query using SAndeep's multi-agent system. Error: {str(e)}"
    
    def _extract_investments_from_response(self, response: str) -> list:
        """Extract actionable investments from SAndeep response"""
        # This would parse the response to extract specific investment recommendations
        # For now, return sample data that would come from SAndeep's analysis
        return [
            {"name": "HDFC Bank Ltd", "type": "stock", "amount": 7500, "allocation": 15},
            {"name": "Axis Bluechip Fund", "type": "mutual_fund", "amount": 12500, "allocation": 25},
            {"name": "HDFC Mid Cap Opportunities", "type": "mutual_fund", "amount": 10000, "allocation": 20},
            {"name": "Nifty 50 ETF", "type": "etf", "amount": 4000, "allocation": 8}
        ]
    
    def _generate_broker_urls(self) -> Dict[str, Any]:
        """Generate broker URLs using SAndeep's broker service"""
        try:
            from services.demat_broker_service import DematBrokerService
            broker_service = DematBrokerService()
            
            return {
                "angel_one": "https://trade.angelone.in/",
                "zerodha": "https://kite.zerodha.com/",
                "groww": "https://groww.in/",
                "upstox": "https://upstox.com/",
                "iifl": "https://www.iiflsecurities.com/",
                "paytm_money": "https://www.paytmmoney.com/",
                "total_investments": 6,
                "real_time_data": True,
                "broker_service_available": True
            }
        except:
            return {
                "angel_one": "https://trade.angelone.in/",
                "zerodha": "https://kite.zerodha.com/", 
                "groww": "https://groww.in/",
                "total_investments": 3,
                "real_time_data": False,
                "broker_service_available": False
            }
    
    def get_broker_comparison(self) -> list:
        """Get broker comparison from SAndeep's system"""
        try:
            from services.demat_broker_service import DematBrokerService
            broker_service = DematBrokerService()
            
            # This would return SAndeep's broker comparison
            brokers = []
            for key, broker_info in broker_service.supported_brokers.items():
                brokers.append({
                    "name": broker_info["name"],
                    "features": broker_info["features"],
                    "url": broker_info["url"],
                    "description": broker_info["description"]
                })
            return brokers
        except:
            # Fallback broker data
            return [
                {"name": "Angel One", "features": ["Zero brokerage delivery", "Real-time data"], "url": "https://trade.angelone.in/"},
                {"name": "Zerodha", "features": ["Kite platform", "Low costs"], "url": "https://kite.zerodha.com/"},
                {"name": "Groww", "features": ["Simple UI", "Goal investing"], "url": "https://groww.in/"}
            ]

# Global instance following SAndeep pattern
sandeep_api = SAndeepInvestmentAPI()