"""
Enhanced Financial Analyst Agent - Pure AI-driven analysis with specialized methods
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
from .base_agent import BaseFinancialAgent
from core.fi_mcp.client import FinancialData

logger = logging.getLogger(__name__)


class EnhancedAnalystAgent(BaseFinancialAgent):
    """Enhanced Analyst Agent with specialized AI-driven portfolio analysis methods"""
    
    def __init__(self):
        super().__init__("analyst")
    
    async def analyze_portfolio_health(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered comprehensive portfolio health analysis"""
        try:
            portfolio_json = json.dumps(portfolio_data, indent=2)
            
            prompt = f"""
Analyze this portfolio in exactly 3 lines:

DATA: {portfolio_json}

Format:
1. Health Score: [0-100]/100 - [5 words why]
2. Top Problem: [10 words max] - Loss ₹[amount]
3. Quick Fix: [10 words max] - Gain ₹[amount]

TOTAL: Maximum 30 words. Be specific with amounts.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a concise financial analyst. Give short, specific answers only.",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"technical_analysis": response}
                
        except Exception as e:
            logger.error(f"Enhanced Analyst portfolio health analysis failed: {e}")
            return {"error": str(e)}
    
    async def detect_money_leaks(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI detects all money leaks from actual financial data"""
        try:
            financial_json = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
Money leak scanner:

DATA: {financial_json}

Find leaks:
1. WORST FUND: [Fund name] - Losing ₹[amount]/year
2. IDLE CASH: ₹[amount] earning nothing - Move to [where]
3. HIGH FEES: [Bank/Fund] charging ₹[amount]/year - Switch to [alternative]

Max 15 words per leak. Show exact ₹ losses only.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a concise money leak detector. Give short, specific answers only.",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"money_leaks": response}
                
        except Exception as e:
            logger.error(f"Money leak detection failed: {e}")
            return {"error": str(e)}
    
    async def calculate_optimization_impact(self, mcp_data: Dict[str, Any], 
                                          proposed_changes: List[Dict]) -> Dict[str, Any]:
        """AI calculates the impact of proposed portfolio optimizations"""
        try:
            financial_json = json.dumps(mcp_data, indent=2)
            changes_json = json.dumps(proposed_changes, indent=2)
            
            prompt = f"""
You are an AI Impact Calculator. Calculate the financial impact of proposed portfolio changes.

CURRENT PORTFOLIO:
{financial_json}

PROPOSED CHANGES:
{changes_json}

CALCULATE OPTIMIZATION IMPACT:

1. RETURN IMPROVEMENT:
   - Current portfolio weighted average return
   - Expected return after changes
   - Additional annual return in ₹
   - 10-year and 20-year wealth difference

2. RISK CHANGES:
   - Current portfolio risk level
   - Risk after optimization
   - Risk-adjusted return improvement
   
3. COST ANALYSIS:
   - Exit loads/taxes for switches
   - One-time implementation costs
   - Net benefit after costs
   
4. TIME-BASED PROJECTIONS:
   - Month 1: Immediate impact
   - Year 1: Annual improvement
   - Year 5: Medium-term wealth gain
   - Year 20: Long-term wealth difference
   
5. SCENARIO ANALYSIS:
   - Best case outcome
   - Most likely outcome  
   - Conservative outcome

Use actual current returns and fund data to calculate realistic projections.
Return detailed calculations as JSON with specific ₹ amounts and timelines.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI Investment Impact Calculator",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"optimization_impact": response}
                
        except Exception as e:
            logger.error(f"Optimization impact calculation failed: {e}")
            return {"error": str(e)}
    
    # Base class required methods - enhanced with AI
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate AI-powered search queries for market intelligence"""
        try:
            financial_context = self._format_financial_summary(financial_data)
            
            prompt = f"""
Generate 3 search queries for: {user_query}
Context: {financial_context}

1. [Query about current market trends]
2. [Query about specific opportunities/risks]
3. [Query about expert recommendations]

India-focused. One line each.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI search query generator for financial research",
                user_context=prompt
            )
            
            # Extract queries from response
            queries = [q.strip() for q in response.split('\n') if q.strip()][:3]
            return queries if queries else [f"{user_query} India financial analysis 2024"]
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return [f"{user_query} financial advice India"]
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """AI-driven comprehensive financial data analysis"""
        try:
            data_dict = {
                "net_worth": getattr(financial_data, 'net_worth', {}),
                "credit_report": getattr(financial_data, 'credit_report', {}),
                "epf_details": getattr(financial_data, 'epf_details', {})
            }
            
            financial_json = json.dumps(data_dict, indent=2)
            
            prompt = f"""
Analyze this user's complete financial portfolio as a Technical Financial Analyst:

FINANCIAL DATA:
{financial_json}

Provide comprehensive analysis covering:

1. PORTFOLIO SNAPSHOT:
   - Current net worth breakdown
   - Asset allocation analysis
   - Liquidity position
   
2. PERFORMANCE ASSESSMENT:
   - Investment returns analysis (using XIRR data)
   - Best and worst performing investments
   - Benchmark comparison
   
3. RISK PROFILE:
   - Current risk level assessment
   - Diversification analysis
   - Concentration risks
   
4. IMMEDIATE OBSERVATIONS:
   - Key strengths of the portfolio
   - Major concerns or red flags
   - Quick wins available

Focus on actionable insights with specific numbers from their data.
Return as structured analysis.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a comprehensive financial portfolio analyzer",
                user_context=prompt
            )
            
            return {"comprehensive_analysis": response}
            
        except Exception as e:
            logger.error(f"Financial data analysis failed: {e}")
            return {"error": str(e)}
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], 
                                         financial_data: FinancialData) -> Dict[str, Any]:
        """Process market intelligence with user's financial context"""
        try:
            # Combine all search findings
            market_intelligence = ""
            for result in search_results:
                market_intelligence += f"\n{result.get('findings', '')}"
            
            financial_context = self._format_financial_summary(financial_data)
            
            prompt = f"""
Process this market intelligence in the context of the user's financial situation:

MARKET INTELLIGENCE:
{market_intelligence}

USER'S FINANCIAL CONTEXT:
{financial_context}

Extract key insights that are specifically relevant to this user:

1. RELEVANT OPPORTUNITIES: Market opportunities that match their risk profile and goals
2. RELEVANT RISKS: Market risks that could impact their portfolio
3. ACTIONABLE INSIGHTS: Specific actions they should consider based on current market conditions
4. RECOMMENDATIONS: Prioritized recommendations based on market data and their situation

Focus on insights that are directly actionable for their specific portfolio.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a market intelligence processor for personalized financial advice",
                user_context=prompt
            )
            
            return {
                "processed_intelligence": response,
                "market_sources": len(search_results),
                "recommendations": []  # Will be extracted from AI response
            }
            
        except Exception as e:
            logger.error(f"Intelligence processing failed: {e}")
            return {"error": str(e)}
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, 
                              grounded_intelligence: Dict[str, Any]) -> str:
        """Generate final analyst response with grounding"""
        try:
            financial_context = self._format_financial_summary(financial_data)
            market_context = grounded_intelligence.get('processed_intelligence', '')
            
            prompt = f"""
As a Technical Financial Analyst AI, provide a comprehensive response to the user's question.

USER QUESTION: {user_query}

USER'S FINANCIAL SITUATION:
{financial_context}

CURRENT MARKET INTELLIGENCE:
{market_context}

Provide a detailed technical analysis that includes:

1. Direct answer to their question using their actual financial data
2. Technical assessment based on their portfolio metrics
3. Market-informed recommendations using current intelligence
4. Specific action steps with quantified impacts
5. Risk assessment and mitigation strategies

Be specific, data-driven, and actionable. Use their actual numbers and current market conditions.
"""

            return await self.generate_ai_response(
                system_prompt="You are a Technical Financial Analyst providing expert advice",
                user_context=prompt,
                market_context=market_context
            )
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"I encountered an error analyzing your portfolio: {str(e)}"