"""
Enhanced Market Research Agent - Pure AI-driven market analysis and opportunity detection
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
from .base_agent import BaseFinancialAgent
from core.fi_mcp.client import FinancialData

logger = logging.getLogger(__name__)


class EnhancedResearchAgent(BaseFinancialAgent):
    """Enhanced Research Agent with specialized AI-driven market analysis methods"""
    
    def __init__(self):
        super().__init__("research")
    
    async def research_market_opportunities(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI identifies market opportunities based on current portfolio and trends"""
        try:
            portfolio_json = json.dumps(portfolio_data, indent=2)
            
            prompt = f"""
You are an AI Market Research Expert. Analyze this portfolio and identify current market opportunities.

CURRENT PORTFOLIO:
{portfolio_json}

IDENTIFY MARKET OPPORTUNITIES:

1. MISSING SECTORS/THEMES:
   - High-growth sectors not represented in portfolio
   - Emerging themes and trends they should consider
   - Geographic/market cap diversification opportunities
   
2. FUND UPGRADE OPPORTUNITIES:
   - Better performing alternatives to current fund holdings
   - Lower cost alternatives with similar/better performance
   - New fund launches in their investment categories
   
3. MARKET TIMING INSIGHTS:
   - Current market valuations and opportunities
   - Sectors that are undervalued/overvalued
   - Optimal entry points based on market cycles
   
4. STRATEGIC OPPORTUNITIES:
   - International diversification options
   - Alternative investment classes (REITs, InvITs, etc.)
   - Tax optimization opportunities
   
5. SPECIFIC RECOMMENDATIONS:
   - Exact funds/investments to consider
   - Allocation percentages for new investments
   - Timeline for implementing changes
   - Expected returns from opportunities

Use current market analysis and their portfolio context to provide specific, actionable opportunities.
Return as structured JSON with research-backed recommendations.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI Market Research Expert specializing in investment opportunities",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"market_opportunities": response}
                
        except Exception as e:
            logger.error(f"Market opportunity research failed: {e}")
            return {"error": str(e)}
    
    async def analyze_fund_performance(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI analyzes individual fund performance and suggests improvements"""
        try:
            financial_json = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
You are an AI Fund Performance Analyst. Analyze each fund in this portfolio for performance and improvement opportunities.

COMPLETE PORTFOLIO DATA:
{financial_json}

FUND-BY-FUND ANALYSIS:

For each mutual fund holding, analyze:

1. PERFORMANCE METRICS:
   - Current XIRR vs category average
   - Risk-adjusted returns
   - Consistency of performance
   - Benchmark comparison
   
2. FUND QUALITY ASSESSMENT:
   - Expense ratio competitiveness  
   - Fund manager track record
   - Portfolio quality and holdings
   - Fund house reputation
   
3. SPECIFIC RECOMMENDATIONS:
   - CONTINUE: Funds performing well and worth holding
   - SWITCH: Underperforming funds with better alternatives
   - INCREASE: Good funds that deserve higher allocation
   - EXIT: Funds that should be sold immediately
   
4. ALTERNATIVE SUGGESTIONS:
   - For each underperforming fund, suggest 2-3 better alternatives
   - Provide expected improvement in returns
   - Consider exit loads and tax implications
   
5. PORTFOLIO REBALANCING:
   - Optimal allocation across remaining funds
   - New fund additions to fill gaps
   - Expected overall portfolio improvement

Analyze each fund using their actual performance data. Provide specific fund names and actionable switches.
Return as structured JSON with fund-specific recommendations.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI Fund Performance Analyst",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"fund_analysis": response}
                
        except Exception as e:
            logger.error(f"Fund performance analysis failed: {e}")
            return {"error": str(e)}
    
    async def research_investment_themes(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI researches current investment themes and trend opportunities"""
        try:
            financial_json = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
You are an AI Investment Theme Researcher. Based on this user's portfolio and current market trends, identify relevant investment themes.

USER'S CURRENT PORTFOLIO:
{financial_json}

RESEARCH INVESTMENT THEMES:

1. CURRENT HOT THEMES:
   - Technology trends (AI, EV, renewable energy, etc.)
   - Demographic trends (aging population, urbanization)
   - Economic trends (digitization, consumption patterns)
   - Policy-driven themes (infrastructure, manufacturing)
   
2. PORTFOLIO THEME ANALYSIS:
   - Which themes are already represented in their portfolio
   - Theme concentration and gaps
   - Overexposure vs underexposure to key themes
   
3. EMERGING OPPORTUNITIES:
   - New themes gaining momentum
   - Undervalued themes ready for upturn
   - Geographic themes (China+1, US-India ties, etc.)
   - ESG and sustainability themes
   
4. IMPLEMENTATION STRATEGIES:
   - Specific funds/stocks for each theme
   - Allocation recommendations for theme exposure
   - Risk management within themes
   - Timeline for theme investments
   
5. THEME-BASED PORTFOLIO REBALANCING:
   - How to incorporate new themes
   - Expected returns from theme investing
   - Risk assessment of theme concentration

Provide research-backed theme analysis with specific investment options.
Focus on themes relevant to Indian markets and their portfolio size.
Return as structured JSON with actionable theme strategies.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI Investment Theme Research Expert",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"theme_research": response}
                
        except Exception as e:
            logger.error(f"Investment theme research failed: {e}")
            return {"error": str(e)}
    
    # Base class required methods - enhanced with AI
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate AI-powered market research queries"""
        try:
            financial_context = self._format_financial_summary(financial_data)
            
            prompt = f"""
Generate 3 specific market research queries to find current opportunities and trends for this user.

USER QUERY: {user_query}
USER'S FINANCIAL CONTEXT: {financial_context}

Create search queries that will find:
1. Current market opportunities and trends relevant to their portfolio
2. Specific investment strategies and themes gaining momentum
3. Expert market outlook and recommendations for similar investors

Focus on Indian markets, mutual funds, and investment opportunities.
Return only the search queries, one per line.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI market research query generator",
                user_context=prompt
            )
            
            # Extract queries from response
            queries = [q.strip() for q in response.split('\n') if q.strip()][:3]
            return queries if queries else [f"{user_query} India market opportunities 2024"]
            
        except Exception as e:
            logger.error(f"Research query generation failed: {e}")
            return [f"{user_query} investment opportunities India"]
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """AI-driven market perspective analysis of financial data"""
        try:
            data_dict = {
                "net_worth": getattr(financial_data, 'net_worth', {}),
                "credit_report": getattr(financial_data, 'credit_report', {}),
                "epf_details": getattr(financial_data, 'epf_details', {})
            }
            
            financial_json = json.dumps(data_dict, indent=2)
            
            prompt = f"""
Analyze this portfolio from a Market Research perspective:

FINANCIAL DATA:
{financial_json}

Provide market-focused analysis covering:

1. MARKET POSITIONING:
   - How their portfolio aligns with current market trends
   - Opportunities they're missing in current markets
   - Overexposure to declining sectors/themes
   
2. COMPETITIVE ANALYSIS:
   - How their funds compare to category leaders
   - Better alternatives available in the market
   - Emerging options they should consider
   
3. STRATEGIC OPPORTUNITIES:
   - Market segments underrepresented in their portfolio
   - Timing opportunities based on market cycles
   - Geographic/thematic diversification gaps
   
4. MARKET OUTLOOK IMPLICATIONS:
   - How current market trends affect their holdings
   - Recommended strategic shifts based on market direction
   - Risk factors from market perspective

Focus on market-driven insights and opportunities.
Return as structured market analysis.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a market research analyst reviewing investment portfolios",
                user_context=prompt
            )
            
            return {"market_analysis": response}
            
        except Exception as e:
            logger.error(f"Market-focused financial data analysis failed: {e}")
            return {"error": str(e)}
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], 
                                         financial_data: FinancialData) -> Dict[str, Any]:
        """Process market intelligence for investment opportunities"""
        try:
            # Combine all market research findings
            market_intelligence = ""
            for result in search_results:
                market_intelligence += f"\n{result.get('findings', '')}"
            
            financial_context = self._format_financial_summary(financial_data)
            
            prompt = f"""
Process this market intelligence to identify specific investment opportunities for the user:

MARKET INTELLIGENCE:
{market_intelligence}

USER'S FINANCIAL CONTEXT:
{financial_context}

Extract actionable market opportunities:

1. IMMEDIATE OPPORTUNITIES: Market opportunities they can act on now
2. STRATEGIC OPPORTUNITIES: Longer-term market trends to position for
3. THREAT MITIGATION: Market risks they should protect against
4. COMPETITIVE INSIGHTS: How to outperform in current market conditions

Focus on specific, implementable opportunities based on current market conditions.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a market intelligence processor for investment opportunities",
                user_context=prompt
            )
            
            return {
                "market_opportunities": response,
                "research_sources": len(search_results),
                "opportunities": []  # Will be extracted from AI response
            }
            
        except Exception as e:
            logger.error(f"Market intelligence processing failed: {e}")
            return {"error": str(e)}
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, 
                              grounded_intelligence: Dict[str, Any]) -> str:
        """Generate final research response with market insights"""
        try:
            financial_context = self._format_financial_summary(financial_data)
            market_context = grounded_intelligence.get('market_opportunities', '')
            
            prompt = f"""
As a Market Research Expert AI, provide comprehensive market-focused advice for the user's question.

USER QUESTION: {user_query}

USER'S FINANCIAL SITUATION:
{financial_context}

CURRENT MARKET OPPORTUNITIES:
{market_context}

Provide market research-driven response that includes:

1. Market-informed answer to their specific question
2. Current market opportunities relevant to their situation
3. Strategic recommendations based on market trends and analysis
4. Specific investment opportunities with market rationale
5. Market timing and implementation strategies

Be specific about market opportunities and provide actionable investment strategies.
"""

            return await self.generate_ai_response(
                system_prompt="You are a Market Research Expert providing investment strategy advice",
                user_context=prompt,
                market_context=market_context
            )
            
        except Exception as e:
            logger.error(f"Research response generation failed: {e}")
            return f"I encountered an error researching market opportunities: {str(e)}"