"""
Pure AI-Powered Financial Intelligence Analyst 🤖
Leverages Gemini AI reasoning with real financial data for comprehensive analysis
No hardcoded calculations - Pure AI intelligence with Fi MCP data + Google Search Grounding
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

logger = logging.getLogger(__name__)

class AnalystAgent(BaseFinancialAgent):
    """Pure AI-Powered Financial Intelligence Analyst - Zero hardcoded calculations, pure Gemini reasoning"""
    
    def __init__(self):
        super().__init__("analyst")
        logger.info("🤖 Pure AI Financial Intelligence Analyst initialized - Gemini powered with Fi MCP data")
    
    def get_system_prompt(self, user_query: str, financial_data: FinancialData) -> str:
        """Generate comprehensive system prompt for Gemini AI to analyze financial data"""
        
        return f"""
You are an expert Indian Financial Intelligence Analyst powered by Gemini AI. Your role is to provide comprehensive financial analysis using ONLY the actual financial data provided and current Indian market intelligence from Google Search.

**CORE PRINCIPLES:**
1. ALL financial analysis is for INDIAN CONTEXT - use Indian Rupees (₹), Indian financial products, Indian market conditions
2. Analyze ONLY based on actual financial data provided - no assumptions or generic calculations
3. Use your AI reasoning to understand financial health, affordability, and opportunities in Indian context
4. Consider real Indian market conditions from search results for contextual advice
5. Provide personalized insights based on the user's specific Indian financial situation
6. NO hardcoded formulas - use intelligent reasoning about Indian financial relationships
7. Focus on practical, realistic advice for Indian middle-class and upper-middle-class scenarios

**USER'S ACTUAL FINANCIAL DATA:**
{self._format_financial_data_for_ai(financial_data)}

**USER QUERY:** {user_query}

**YOUR ANALYSIS FRAMEWORK:**

1. **FINANCIAL POSITION ANALYSIS:**
   - Analyze the user's actual net worth, assets, liabilities from the data above
   - Assess liquidity position based on savings accounts vs total assets
   - Evaluate debt burden using actual loan/credit card data
   - Determine monthly cash flow capacity based on asset patterns and EPF contributions

2. **QUERY-SPECIFIC REASONING:**
   - For purchase decisions: Reason about affordability based on actual liquidity, monthly capacity, and debt situation
   - For career decisions: Consider emergency fund adequacy, debt obligations, and financial flexibility
   - For investment decisions: Analyze current portfolio, risk capacity, and surplus availability
   - For housing decisions: Evaluate rent vs buy based on actual financial position and market data
   - For travel/lifestyle: Assess discretionary spending capacity without compromising financial health

3. **MARKET CONTEXT INTEGRATION:**
   - Use Google Search results to understand current market prices, interest rates, and trends
   - Factor in real-world costs and opportunities relevant to the user's query
   - Consider economic conditions affecting the user's specific financial decision

4. **INTELLIGENT RECOMMENDATIONS:**
   - Provide specific, actionable advice based on the user's actual financial situation
   - Suggest optimization strategies considering real market opportunities
   - Highlight risks and opportunities using current market intelligence
   - Recommend specific financial products or strategies based on search results

**OUTPUT FORMAT:**
- Start with a clear assessment of the user's financial position
- Address the specific query with reasoned analysis
- Provide concrete recommendations with specific amounts/strategies
- Include market context from search results
- End with actionable next steps

**REMEMBER:** Use only the actual financial data provided. Your AI reasoning should interpret this real data in context of current market conditions from search results. No generic percentages or hardcoded formulas - pure intelligent analysis.
"""
    
    def _format_financial_data_for_ai(self, financial_data: FinancialData) -> str:
        """Format actual financial data for AI analysis"""
        
        formatted_data = """
**NET WORTH & ASSETS:**
"""
        
        # Net Worth Data
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth
            if 'netWorthResponse' in net_worth:
                total_value = net_worth['netWorthResponse'].get('totalNetWorthValue', {})
                formatted_data += f"- Total Net Worth: {total_value.get('units', 'N/A')} {total_value.get('currencyCode', '')}\n"
                
                assets = net_worth['netWorthResponse'].get('assetValues', [])
                formatted_data += "- Asset Breakdown:\n"
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {})
                    formatted_data += f"  • {asset_type}: {value.get('units', 'N/A')} {value.get('currencyCode', '')}\n"
        
        # Mutual Fund Holdings
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth and 'mfSchemeAnalytics' in financial_data.net_worth:
            mf_data = financial_data.net_worth['mfSchemeAnalytics'].get('schemeAnalytics', [])
            if mf_data:
                formatted_data += "\n**MUTUAL FUND PORTFOLIO:**\n"
                for fund in mf_data[:5]:  # Top 5 funds
                    scheme = fund.get('schemeDetail', {})
                    analytics = fund.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                    fund_name = scheme.get('nameData', {}).get('longName', 'Unknown Fund')
                    current_value = analytics.get('currentValue', {})
                    invested_value = analytics.get('investedValue', {})
                    xirr = analytics.get('XIRR', 'N/A')
                    
                    formatted_data += f"- {fund_name}:\n"
                    formatted_data += f"  • Current Value: {current_value.get('units', 'N/A')} {current_value.get('currencyCode', '')}\n"
                    formatted_data += f"  • Invested Value: {invested_value.get('units', 'N/A')} {invested_value.get('currencyCode', '')}\n"
                    formatted_data += f"  • XIRR: {xirr}%\n"
        
        # Credit Report Data
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_data = financial_data.credit_report
            formatted_data += "\n**CREDIT PROFILE:**\n"
            
            if 'creditReports' in credit_data and credit_data['creditReports']:
                credit_report = credit_data['creditReports'][0].get('creditReportData', {})
                score = credit_report.get('score', {}).get('bureauScore', 'N/A')
                formatted_data += f"- Credit Score: {score}\n"
                
                # Credit Accounts
                credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
                if credit_accounts:
                    formatted_data += "- Active Credit Accounts:\n"
                    for account in credit_accounts[:3]:  # Top 3 accounts
                        subscriber = account.get('subscriberName', 'Unknown')
                        account_type = account.get('accountType', 'N/A')
                        current_balance = account.get('currentBalance', 'N/A')
                        credit_limit = account.get('creditLimitAmount', 'N/A')
                        formatted_data += f"  • {subscriber} (Type: {account_type}): Balance: {current_balance}, Limit: {credit_limit}\n"
        
        # EPF Data
        if hasattr(financial_data, 'epf_details') and financial_data.epf_details:
            epf_data = financial_data.epf_details
            formatted_data += "\n**EPF DETAILS:**\n"
            
            if 'uanAccounts' in epf_data and epf_data['uanAccounts']:
                epf_account = epf_data['uanAccounts'][0].get('rawDetails', {})
                overall_balance = epf_account.get('overall_pf_balance', {})
                current_balance = overall_balance.get('current_pf_balance', 'N/A')
                employee_share = overall_balance.get('employee_share_total', {}).get('balance', 'N/A')
                employer_share = overall_balance.get('employer_share_total', {}).get('balance', 'N/A')
                
                formatted_data += f"- Total EPF Balance: ₹{current_balance}\n"
                formatted_data += f"- Employee Contribution: ₹{employee_share}\n"
                formatted_data += f"- Employer Contribution: ₹{employer_share}\n"
        
        # Bank Account Summary from account details
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth and 'accountDetailsBulkResponse' in financial_data.net_worth:
            accounts = financial_data.net_worth['accountDetailsBulkResponse'].get('accountDetailsMap', {})
            if accounts:
                formatted_data += "\n**BANK ACCOUNTS:**\n"
                for account_id, account_info in list(accounts.items())[:3]:  # Top 3 accounts
                    deposit_summary = account_info.get('depositSummary', {})
                    balance = deposit_summary.get('currentBalance', {})
                    account_details = account_info.get('accountDetails', {})
                    bank_name = account_details.get('fipMeta', {}).get('displayName', 'Unknown Bank')
                    
                    if balance:
                        formatted_data += f"- {bank_name}: ₹{balance.get('units', 'N/A')}\n"
        
        return formatted_data
    
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate search queries using Gemini AI based on user query and financial data"""
        
        # Format financial summary for context
        financial_summary = self._format_financial_data_for_ai(financial_data)
        
        # Use Gemini to generate search queries
        prompt = f"""
Analyze this financial query and generate specific Google search queries to find current market data:

User Query: {user_query}

User's Financial Data:
{financial_summary}

Generate 5 specific search queries focused on INDIAN financial context that will help answer their question with:
1. Current Indian market prices and rates (in INR)
2. Indian financial product comparisons (banks, mutual funds, loans)
3. Indian market trends and forecasts
4. Expert recommendations for Indian consumers
5. India-specific information and regulations

IMPORTANT: All searches should focus on INDIAN market, INDIAN products, prices in RUPEES, and be relevant to Indian consumers.
Return ONLY the queries, one per line.
"""
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # Parse queries from response
            queries = [q.strip() for q in response.text.strip().split('\n') if q.strip()]
            logger.info(f"Generated {len(queries)} search queries for analysis")
            return queries[:5]
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            # Basic fallback query
            return [f"{user_query} India 2024 current market analysis"]
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """Pure AI analysis of financial data - NO hardcoded calculations"""
        
        ai_prompt = f"""
Analyze this user's financial data and provide a comprehensive assessment:

{self._format_financial_data_for_ai(financial_data)}

Provide analysis in JSON format with these keys:
- financial_strength: (strong/moderate/weak)
- liquidity_position: (high/moderate/low) 
- debt_burden: (high/moderate/low)
- investment_maturity: (experienced/intermediate/beginner)
- key_insights: [list of 3-5 key insights]

Return only valid JSON.
"""
        
        try:
            ai_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=ai_prompt
            )
            
            # Clean and parse JSON response
            response_text = ai_response.text.strip()
            
            # Find JSON in response (might have extra text)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
            else:
                json_text = response_text
            
            import json
            return json.loads(json_text)
            
        except Exception as e:
            logger.error(f"AI financial analysis failed: {e}")
            logger.error(f"Response was: {ai_response.text if 'ai_response' in locals() else 'No response'}")
            return {
                'financial_strength': 'moderate',
                'liquidity_position': 'moderate',
                'debt_burden': 'moderate',
                'investment_maturity': 'intermediate',
                'key_insights': ['AI analysis temporarily unavailable']
            }
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], financial_data: FinancialData) -> Dict[str, Any]:
        """Process search results from Gemini Google Search using AI"""
        
        # Combine search findings
        search_findings = []
        all_sources = []
        
        for result in search_results:
            search_findings.append(f"Query: {result['query']}\nFindings: {result['findings']}")
            all_sources.extend(result.get('sources', []))
        
        combined_findings = "\n\n---\n\n".join(search_findings)
        
        # Use AI to analyze the search results
        analysis_prompt = f"""
Analyze these Google search results for financial insights:

{combined_findings}

User's Financial Context:
{self._format_financial_data_for_ai(financial_data)[:1000]}

Extract and provide:
1. Current market trends relevant to the user
2. Specific opportunities based on their financial position
3. Potential risks to consider
4. Actionable recommendations with specific numbers/rates found
5. Key data points (prices, rates, percentages) from the search

Provide response in JSON format:
{{
  "market_trends": ["trend1", "trend2", ...],
  "opportunities": ["opportunity1", "opportunity2", ...],
  "risks": ["risk1", "risk2", ...],
  "recommendations": ["recommendation1", "recommendation2", ...],
  "key_data_points": {{
    "prices": [],
    "rates": [],
    "other": []
  }},
  "confidence": "high/medium/low"
}}

IMPORTANT: Return ONLY valid JSON, no additional text or explanations.
"""
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt
            )
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            
            # Find JSON in response (might have extra text)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
            else:
                json_text = response_text
            
            import json
            analysis = json.loads(json_text)
            analysis['sources'] = all_sources
            return analysis
            
        except Exception as e:
            logger.error(f"Search result analysis failed: {e}")
            return {
                'market_trends': [finding[:100] + "..." for finding in search_findings[:2]],
                'opportunities': ['Analysis in progress'],
                'risks': ['Assessment pending'],
                'recommendations': ['Generating recommendations'],
                'key_data_points': {'prices': [], 'rates': [], 'other': []},
                'sources': all_sources,
                'confidence': 'low'
            }
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, grounded_intelligence: Dict[str, Any]) -> str:
        """Generate response using Gemini with Google Search grounding"""
        
        # Prepare comprehensive context
        market_context = self._format_market_intelligence(grounded_intelligence)
        financial_context = self._format_financial_data_for_ai(financial_data)
        
        # Create comprehensive prompt for final response
        response_prompt = f"""
You are an Indian Financial Intelligence Analyst. Using the user's Indian financial data and fresh Indian market intelligence from Google Search, provide a comprehensive analysis.

USER QUERY: {user_query}

USER'S INDIAN FINANCIAL DATA:
{financial_context}

CURRENT INDIAN MARKET INTELLIGENCE (from Google Search):
{market_context}

Provide a detailed, personalized Indian financial analysis that:
1. Directly answers their question with specific INR amounts and realistic recommendations for Indian consumers
2. Uses actual Indian market data from search results (cite specific Indian rates, prices, trends)
3. Considers their personal Indian financial situation and Indian market context
4. Provides actionable next steps relevant to Indian financial systems
5. Includes any relevant warnings or opportunities specific to Indian market
6. Be practical and realistic - avoid overly complex or unrealistic scenarios
7. Focus on middle-class to upper-middle-class Indian financial decisions

IMPORTANT: All amounts in INR, all advice relevant to Indian consumers, realistic scenarios only.
"""
        
        # Generate final response with grounding
        return await self.generate_ai_response(
            "",  # System prompt is in config
            response_prompt,
            ""   # Market context already in prompt
        )
    
    def _format_market_intelligence(self, intelligence: Dict[str, Any]) -> str:
        """Format market intelligence for response generation"""
        sections = []
        
        if intelligence.get('market_trends'):
            sections.append("Market Trends:\n" + "\n".join(f"• {trend}" for trend in intelligence['market_trends']))
        
        if intelligence.get('key_data_points'):
            data_points = intelligence['key_data_points']
            if data_points.get('prices'):
                sections.append("Current Prices:\n" + "\n".join(f"• {price}" for price in data_points['prices']))
            if data_points.get('rates'):
                sections.append("Current Rates:\n" + "\n".join(f"• {rate}" for rate in data_points['rates']))
        
        if intelligence.get('opportunities'):
            sections.append("Opportunities:\n" + "\n".join(f"• {opp}" for opp in intelligence['opportunities']))
        
        if intelligence.get('risks'):
            sections.append("Risks to Consider:\n" + "\n".join(f"• {risk}" for risk in intelligence['risks']))
        
        if intelligence.get('sources'):
            sections.append("\nSources: " + str(len(intelligence['sources'])) + " verified sources from Google Search")
        
        return "\n\n".join(sections) if sections else "No market intelligence available"
    
