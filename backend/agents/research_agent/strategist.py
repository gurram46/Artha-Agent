"""
Pure AI-Powered Financial Strategic Research Agent 🧠
Leverages Gemini AI for comprehensive financial planning and strategic analysis
No hardcoded strategies - Pure AI reasoning with Fi MCP data + Google Search Intelligence
"""

import asyncio
import json
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseFinancialAgent, AgentResponse
from core.fi_mcp.client import FinancialData
from core.google_grounding.grounding_client import GroundingResult
from google.generativeai import types

logger = logging.getLogger(__name__)

class ResearchAgent(BaseFinancialAgent):
    """Pure AI-Powered Financial Strategic Research Agent - Zero hardcoded strategies, pure Gemini intelligence"""
    
    def __init__(self):
        super().__init__("research")
        logger.info("🧠 Pure AI Financial Strategic Research Agent initialized - Gemini powered strategic planning")
    
    def get_strategic_system_prompt(self, user_query: str, financial_data: FinancialData) -> str:
        """Generate comprehensive system prompt for Gemini AI strategic financial planning"""
        
        return f"""
You are an expert Indian Financial Strategic Research Agent powered by Gemini AI. Your role is to conduct comprehensive strategic planning and research using ONLY the actual financial data provided and current INDIAN market intelligence from Google Search.

**CORE PRINCIPLES:**
1. Conduct strategic planning ONLY based on actual financial data provided - no generic strategies
2. Use your AI reasoning to develop personalized financial strategies and plans
3. Leverage real market intelligence from search results for strategic opportunities
4. Create actionable, step-by-step plans based on the user's specific financial situation
5. NO hardcoded planning templates - use intelligent strategic reasoning

**USER'S ACTUAL FINANCIAL DATA:**
{self._format_financial_data_for_strategic_planning(financial_data)}

**USER QUERY:** {user_query}

**YOUR STRATEGIC ANALYSIS FRAMEWORK:**

1. **FINANCIAL POSITION STRATEGIC ASSESSMENT:**
   - Analyze the user's current financial position from actual data above
   - Identify strategic strengths and weaknesses in their financial profile
   - Assess strategic financial capacity for achieving their goals
   - Determine optimal resource allocation based on their actual situation

2. **GOAL-SPECIFIC STRATEGIC PLANNING:**
   - For purchase goals: Develop financing strategy based on actual liquidity and debt capacity
   - For career goals: Create transition strategy considering actual emergency funds and obligations
   - For investment goals: Design portfolio strategy based on current holdings and risk capacity
   - For housing goals: Plan rent vs buy strategy using actual financial position and market data
   - For travel/lifestyle goals: Create budget strategy without compromising financial stability

3. **MARKET INTELLIGENCE INTEGRATION:**
   - Use Google Search results to understand current market opportunities and risks
   - Factor in real-time pricing, interest rates, and market trends
   - Identify strategic timing opportunities based on market conditions
   - Incorporate market-specific strategies relevant to the user's goals

4. **STRATEGIC RECOMMENDATIONS:**
   - Develop step-by-step action plan based on actual financial capacity
   - Suggest specific financial products or strategies from market research
   - Create timeline for goal achievement using real financial constraints
   - Recommend optimization strategies based on current market opportunities

**OUTPUT FORMAT:**
- Start with strategic assessment of current financial position
- Develop goal-specific strategic plan with clear steps
- Include market-based opportunities and timing recommendations
- Provide concrete action items with specific amounts and timelines
- End with strategic risk mitigation and contingency planning

**REMEMBER:** Use only the actual financial data provided. Your AI strategic reasoning should develop personalized plans based on real data in context of current market intelligence from search results. No generic planning templates - pure intelligent strategic analysis.
"""
    
    def _format_financial_data_for_strategic_planning(self, financial_data: FinancialData) -> str:
        """Format actual financial data for AI strategic planning"""
        
        formatted_data = """
**STRATEGIC FINANCIAL POSITION:**
"""
        
        # Net Worth & Asset Analysis
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth
            if 'netWorthResponse' in net_worth:
                total_value = net_worth['netWorthResponse'].get('totalNetWorthValue', {})
                formatted_data += f"- Total Net Worth: {total_value.get('units', 'N/A')} {total_value.get('currencyCode', '')}\n"
                
                assets = net_worth['netWorthResponse'].get('assetValues', [])
                formatted_data += "- Strategic Asset Position:\n"
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {})
                    formatted_data += f"  • {asset_type}: {value.get('units', 'N/A')} {value.get('currencyCode', '')}\n"
        
        # Investment Portfolio Analysis
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth and 'mfSchemeAnalytics' in financial_data.net_worth:
            mf_data = financial_data.net_worth['mfSchemeAnalytics'].get('schemeAnalytics', [])
            if mf_data:
                formatted_data += "\n**INVESTMENT PORTFOLIO ANALYSIS:**\n"
                total_current_value = 0
                total_invested_value = 0
                
                for fund in mf_data:
                    scheme = fund.get('schemeDetail', {})
                    analytics = fund.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                    fund_name = scheme.get('nameData', {}).get('longName', 'Unknown Fund')
                    fund_category = scheme.get('categoryName', 'Unknown Category')
                    risk_level = scheme.get('fundhouseDefinedRiskLevel', 'Unknown Risk')
                    current_value = analytics.get('currentValue', {})
                    invested_value = analytics.get('investedValue', {})
                    xirr = analytics.get('XIRR', 'N/A')
                    
                    try:
                        current_val = float(current_value.get('units', '0'))
                        invested_val = float(invested_value.get('units', '0'))
                        total_current_value += current_val
                        total_invested_value += invested_val
                    except:
                        pass
                    
                    formatted_data += f"- {fund_name} ({fund_category}, {risk_level}):\n"
                    formatted_data += f"  • Current: ₹{current_value.get('units', 'N/A')}, Invested: ₹{invested_value.get('units', 'N/A')}, XIRR: {xirr}%\n"
                
                if total_current_value > 0 and total_invested_value > 0:
                    portfolio_return = ((total_current_value - total_invested_value) / total_invested_value) * 100
                    formatted_data += f"\n**PORTFOLIO PERFORMANCE:** Total Current: ₹{total_current_value:.0f}, Total Invested: ₹{total_invested_value:.0f}, Overall Return: {portfolio_return:.1f}%\n"
        
        # Credit Profile for Strategic Planning
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_data = financial_data.credit_report
            formatted_data += "\n**STRATEGIC CREDIT POSITION:**\n"
            
            if 'creditReports' in credit_data and credit_data['creditReports']:
                credit_report = credit_data['creditReports'][0].get('creditReportData', {})
                score = credit_report.get('score', {}).get('bureauScore', 'N/A')
                formatted_data += f"- Credit Score: {score} (Strategic borrowing capacity indicator)\n"
                
                # Outstanding debt analysis
                credit_summary = credit_report.get('creditAccount', {}).get('creditAccountSummary', {})
                if credit_summary:
                    total_balance = credit_summary.get('totalOutstandingBalance', {})
                    secured_debt = total_balance.get('outstandingBalanceSecured', 'N/A')
                    unsecured_debt = total_balance.get('outstandingBalanceUnSecured', 'N/A')
                    total_debt = total_balance.get('outstandingBalanceAll', 'N/A')
                    
                    formatted_data += f"- Strategic Debt Position: Total: ₹{total_debt}, Secured: ₹{secured_debt}, Unsecured: ₹{unsecured_debt}\n"
                
                # Credit utilization for strategic planning
                credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
                if credit_accounts:
                    formatted_data += "- Strategic Credit Capacity:\n"
                    for account in credit_accounts[:3]:
                        subscriber = account.get('subscriberName', 'Unknown')
                        current_balance = account.get('currentBalance', 'N/A')
                        credit_limit = account.get('creditLimitAmount', 'N/A')
                        if credit_limit != 'N/A' and credit_limit != '0':
                            formatted_data += f"  • {subscriber}: Used: ₹{current_balance}, Available: ₹{credit_limit}\n"
        
        # EPF for Long-term Strategic Planning
        if hasattr(financial_data, 'epf_details') and financial_data.epf_details:
            epf_data = financial_data.epf_details
            formatted_data += "\n**RETIREMENT STRATEGIC POSITION:**\n"
            
            if 'uanAccounts' in epf_data and epf_data['uanAccounts']:
                epf_account = epf_data['uanAccounts'][0].get('rawDetails', {})
                
                # Employment history for strategic planning
                est_details = epf_account.get('est_details', [])
                if est_details:
                    current_employer = est_details[-1]  # Most recent employer
                    employer_name = current_employer.get('est_name', 'Unknown')
                    doj = current_employer.get('doj_epf', 'Unknown')
                    formatted_data += f"- Current Employment: {employer_name} (Since: {doj})\n"
                
                overall_balance = epf_account.get('overall_pf_balance', {})
                current_balance = overall_balance.get('current_pf_balance', 'N/A')
                employee_share = overall_balance.get('employee_share_total', {}).get('balance', 'N/A')
                employer_share = overall_balance.get('employer_share_total', {}).get('balance', 'N/A')
                
                formatted_data += f"- Strategic Retirement Fund: Total: ₹{current_balance}\n"
                formatted_data += f"- Contribution Breakdown: Employee: ₹{employee_share}, Employer: ₹{employer_share}\n"
        
        # Liquidity Analysis from Bank Accounts
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth and 'accountDetailsBulkResponse' in financial_data.net_worth:
            accounts = financial_data.net_worth['accountDetailsBulkResponse'].get('accountDetailsMap', {})
            if accounts:
                formatted_data += "\n**STRATEGIC LIQUIDITY POSITION:**\n"
                total_liquid = 0
                
                for account_id, account_info in accounts.items():
                    deposit_summary = account_info.get('depositSummary', {})
                    balance = deposit_summary.get('currentBalance', {})
                    account_details = account_info.get('accountDetails', {})
                    bank_name = account_details.get('fipMeta', {}).get('displayName', 'Unknown Bank')
                    account_type = deposit_summary.get('depositAccountType', 'Unknown Type')
                    
                    if balance and balance.get('units'):
                        try:
                            balance_amount = float(balance.get('units', '0'))
                            total_liquid += balance_amount
                            formatted_data += f"- {bank_name} ({account_type}): ₹{balance.get('units', 'N/A')}\n"
                        except:
                            pass
                
                if total_liquid > 0:
                    formatted_data += f"\n**TOTAL STRATEGIC LIQUIDITY: ₹{total_liquid:.0f}**\n"
        
        return formatted_data
    
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate strategic search queries using Gemini AI - Optimized for Speed"""
        
        financial_summary = self._format_financial_data_for_strategic_planning(financial_data)
        
        prompt = f"""
Generate 3 targeted Google search queries for Indian strategic financial planning:

User Query: {user_query}
Financial Context: {financial_summary}

Focus on CURRENT Indian market:
1. Strategic opportunities and market timing
2. Tax optimization and wealth building strategies  
3. Specific financial products and expert recommendations

Return ONLY search queries, one per line.
"""
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            
            queries = [q.strip() for q in response.text.strip().split('\n') if q.strip()]
            logger.info(f"Generated {len(queries)} strategic queries")
            return queries[:3]  # Reduced to 3 for speed
            
        except Exception as e:
            logger.error(f"Strategic query generation failed: {e}")
            return [
                f"{user_query} strategic financial planning India 2025",
                "wealth building strategies India tax optimization 2025",
                "investment opportunities India market timing 2025"
            ]
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """Pure AI strategic analysis of financial data - NO hardcoded calculations"""
        
        ai_prompt = f"""
Analyze this user's financial data for strategic planning and provide a comprehensive strategic assessment:

{self._format_financial_data_for_strategic_planning(financial_data)}

Provide strategic analysis in JSON format with these keys:
- strategic_position: (strong/moderate/weak)
- asset_diversification: (excellent/good/limited)
- growth_potential: (high/moderate/low)
- liquidity_flexibility: (high/moderate/low)
- debt_optimization_scope: (high/moderate/low)
- investment_sophistication: (advanced/intermediate/beginner)
- strategic_opportunities: [list of 3-5 key strategic opportunities]
- priority_focus_areas: [list of 3-5 priority areas to focus on]

Return only valid JSON.
"""
        
        try:
            ai_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=ai_prompt
            )
            
            import json
            return json.loads(ai_response.text)
            
        except Exception as e:
            logger.error(f"AI strategic analysis failed: {e}")
            return {
                'strategic_position': 'moderate',
                'asset_diversification': 'good',
                'growth_potential': 'moderate',
                'liquidity_flexibility': 'moderate',
                'debt_optimization_scope': 'moderate',
                'investment_sophistication': 'intermediate',
                'strategic_opportunities': ['Strategic analysis in progress'],
                'priority_focus_areas': ['Analysis being generated']
            }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], financial_data: FinancialData) -> Dict[str, Any]:
        """Process strategic search results using AI"""
        
        # Combine search findings
        strategic_findings = []
        all_sources = []
        
        for result in search_results:
            strategic_findings.append(f"Strategic Query: {result['query']}\nFindings: {result['findings']}")
            all_sources.extend(result.get('sources', []))
        
        combined_findings = "\n\n---\n\n".join(strategic_findings)
        
        # Analyze for strategic insights
        analysis_prompt = f"""
Analyze these strategic market intelligence findings:

{combined_findings}

User's Financial Position:
{self._format_financial_data_for_strategic_planning(financial_data)[:1000]}

Extract strategic insights:
1. Long-term opportunities based on market trends
2. Optimal timing for major financial decisions
3. Strategic risks to mitigate
4. Priority actions for wealth building
5. Tax and optimization strategies found
6. Specific products/services recommendations

Provide response in JSON format:
{{
  "strategic_opportunities": ["opportunity1", "opportunity2", ...],
  "market_timing": ["timing insight1", "timing insight2", ...],
  "strategic_risks": ["risk1", "risk2", ...],
  "action_priorities": ["priority1", "priority2", ...],
  "optimization_strategies": ["strategy1", "strategy2", ...],
  "product_recommendations": ["product1", "product2", ...],
  "confidence": "high/medium/low"
}}
"""
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt
            )
            
            import json
            analysis = json.loads(response.text)
            analysis['sources'] = all_sources
            return analysis
            
        except Exception as e:
            logger.error(f"Strategic analysis failed: {e}")
            return {
                'strategic_opportunities': ['Analysis pending'],
                'market_timing': ['Timing assessment in progress'],
                'strategic_risks': ['Risk evaluation ongoing'],
                'action_priorities': ['Prioritization in progress'],
                'optimization_strategies': ['Strategy development ongoing'],
                'product_recommendations': ['Product analysis pending'],
                'sources': all_sources,
                'confidence': 'low'
            }
    
    
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, grounded_intelligence: Dict[str, Any]) -> str:
        """Generate strategic response using Gemini with market intelligence"""
        
        # Format intelligence and financial data
        strategic_context = self._format_strategic_intelligence(grounded_intelligence)
        financial_context = self._format_financial_data_for_strategic_planning(financial_data)
        
        # Create strategic planning prompt
        response_prompt = f"""
You are a Strategic Financial Planner. Create a comprehensive strategic plan using real market intelligence.

USER QUERY: {user_query}

USER'S FINANCIAL POSITION:
{financial_context}

STRATEGIC MARKET INTELLIGENCE (from Google Search):
{strategic_context}

Develop a strategic financial plan that:
1. Provides a clear roadmap to achieve their financial goals
2. Uses specific market data and opportunities from search results
3. Includes concrete timelines and milestones
4. Suggests specific financial products or strategies found in searches
5. Addresses risks and provides contingency plans
6. Optimizes for tax efficiency and wealth building

Structure your response with:
- Executive Summary
- Current Position Analysis  
- Strategic Recommendations (with specific steps)
- Timeline and Milestones
- Risk Mitigation Strategies
- Next Immediate Actions
"""
        
        # Generate strategic response
        return await self.generate_ai_response(
            "",  # System prompt in config
            response_prompt,
            ""   # Context in prompt
        )
    
    def _format_strategic_intelligence(self, intelligence: Dict[str, Any]) -> str:
        """Format strategic intelligence for response"""
        sections = []
        
        if intelligence.get('strategic_opportunities'):
            sections.append("Strategic Opportunities:\n" + "\n".join(f"• {opp}" for opp in intelligence['strategic_opportunities']))
        
        if intelligence.get('market_timing'):
            sections.append("Market Timing Insights:\n" + "\n".join(f"• {timing}" for timing in intelligence['market_timing']))
        
        if intelligence.get('optimization_strategies'):
            sections.append("Optimization Strategies:\n" + "\n".join(f"• {strategy}" for strategy in intelligence['optimization_strategies']))
        
        if intelligence.get('product_recommendations'):
            sections.append("Recommended Products/Services:\n" + "\n".join(f"• {product}" for product in intelligence['product_recommendations']))
        
        if intelligence.get('action_priorities'):
            sections.append("Priority Actions:\n" + "\n".join(f"• {action}" for action in intelligence['action_priorities']))
        
        if intelligence.get('sources'):
            sections.append(f"\nBased on {len(intelligence['sources'])} verified sources")
        
        return "\n\n".join(sections) if sections else "Strategic intelligence being processed"
    
    async def process_market_intelligence(self, user_query: str, market_intelligence: Dict[str, Any]) -> Dict[str, str]:
        """Process market intelligence and data analysis to produce strategic research"""
        
        # Pure market research prompt - NO user financial data
        strategic_prompt = f"""
You are the Strategic Research Agent. Provide comprehensive market research and investment opportunities analysis.

USER QUESTION: {user_query}

LIVE MARKET INTELLIGENCE ({len(market_intelligence.get('sources', []))} sources):
{market_intelligence.get('findings', 'No findings')[:2000]}

SEARCH SOURCES: {len(market_intelligence.get('sources', []))} live market data sources

Provide comprehensive research covering:
1. **Market Opportunities** - Current opportunities and growth potential
2. **Strategic Timing** - Best timing for entry and market conditions  
3. **Action Plan** - Step-by-step approach for taking advantage
4. **Specific Recommendations** - Concrete actionable recommendations

Focus on market research, trends, and opportunities. Do NOT make personalized financial advice - that will be handled separately.
Be thorough and data-driven using the live market intelligence provided.
"""
        
        try:
            # Generate strategic research response
            strategic_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=strategic_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            
            if strategic_response and strategic_response.text:
                strategic_content = strategic_response.text.strip()
                logger.info(f"Research Agent: Generated strategic research - {len(strategic_content)} chars")
            else:
                logger.error(f"Research Agent: AI response was empty. Response object: {strategic_response}")
                if hasattr(strategic_response, 'candidates') and strategic_response.candidates:
                    logger.error(f"Candidate[0]: {strategic_response.candidates[0]}")
                    if hasattr(strategic_response.candidates[0], 'finish_reason'):
                        logger.error(f"Finish reason: {strategic_response.candidates[0].finish_reason}")
                if hasattr(strategic_response, 'usage_metadata'):
                    logger.error(f"Usage metadata: {strategic_response.usage_metadata}")
                strategic_content = f"ERROR: Strategic analysis failed - AI returned empty response. Query: {user_query}"
            
            return {
                'agent': 'Strategic Research',
                'content': strategic_content,
                'emoji': '🎯',
                'market_sources': len(market_intelligence.get('sources', [])),
                'data_analysis_integrated': True
            }
            
        except Exception as e:
            logger.error(f"Research Agent: Strategic processing failed: {e}")
            return {
                'agent': 'Strategic Research',
                'content': f"Strategic analysis failed: {str(e)}",
                'emoji': '🎯',
                'market_sources': len(market_intelligence.get('sources', [])),
                'data_analysis_integrated': False
            }
    
