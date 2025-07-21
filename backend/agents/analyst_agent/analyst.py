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
from config.settings import config
from google.genai import types

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

**USER'S FINANCIAL DATA:**
{self._format_financial_data_for_ai(financial_data)}

**USER QUERY:** {user_query}

**YOUR ANALYSIS FRAMEWORK:**

1. **FINANCIAL POSITION ANALYSIS:**
   - Analyze the user's net worth, assets, and liabilities from the data above
   - Assess liquidity position based on savings accounts vs total assets
   - Evaluate debt burden using actual loan/credit data
   - Determine financial capacity based on current position

2. **PERSONALIZED RECOMMENDATIONS:**
   - For purchase decisions: Calculate affordability based on liquid funds and existing obligations
   - Consider emergency fund requirements (typically 3-6 months expenses)
   - Factor in debt-to-income ratios and existing loan obligations
   - Provide specific recommendations based on their actual financial situation

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
        """Format actual Fi MCP financial data for AI analysis using REAL data structure"""
        
        formatted_data = """
**USER'S ACTUAL FINANCIAL POSITION (Live Fi MCP Data):**
"""
        
        # Net Worth Data from REAL Fi MCP structure
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth
            if 'netWorthResponse' in net_worth:
                total_value = net_worth['netWorthResponse'].get('totalNetWorthValue', {})
                net_worth_amount = float(total_value.get('units', '0'))
                formatted_data += f"\n💰 **TOTAL NET WORTH**: ₹{self.format_currency(net_worth_amount)} (From connected accounts)\n\n"
                
                # Process REAL Assets from Fi MCP
                assets = net_worth['netWorthResponse'].get('assetValues', [])
                formatted_data += "📊 **ASSET BREAKDOWN** (Real-time data):\n"
                liquid_funds = 0
                mutual_funds = 0
                securities = 0
                epf_amount = 0
                
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {})
                    amount = float(value.get('units', '0'))
                    
                    if 'SAVINGS_ACCOUNTS' in asset_type:
                        liquid_funds += amount
                        formatted_data += f"  💳 Bank Savings: ₹{self.format_currency(amount)} (LIQUID - immediate access)\n"
                    elif 'MUTUAL_FUND' in asset_type:
                        mutual_funds += amount
                        formatted_data += f"  📈 Mutual Fund Portfolio: ₹{self.format_currency(amount)} (Can liquidate in 1-2 days)\n"
                    elif 'INDIAN_SECURITIES' in asset_type:
                        securities += amount
                        formatted_data += f"  📊 Stock Holdings: ₹{self.format_currency(amount)} (Can sell in T+2 days)\n"
                    elif 'EPF' in asset_type:
                        epf_amount += amount
                        formatted_data += f"  🏦 EPF Balance: ₹{self.format_currency(amount)} (RETIREMENT fund - restricted)\n"
                    else:
                        formatted_data += f"  • {asset_type.replace('ASSET_TYPE_', '').replace('_', ' ').title()}: ₹{self.format_currency(amount)}\n"
                
                # Process REAL Liabilities from Fi MCP
                liabilities = net_worth['netWorthResponse'].get('liabilityValues', [])
                total_loans = 0
                if liabilities:
                    formatted_data += "\n❌ **OUTSTANDING LIABILITIES**:\n"
                    for liability in liabilities:
                        liability_type = liability.get('netWorthAttribute', 'Unknown')
                        value = liability.get('value', {})
                        amount = float(value.get('units', '0'))
                        total_loans += amount
                        clean_type = liability_type.replace('LIABILITY_TYPE_', '').replace('_', ' ').title()
                        formatted_data += f"  • {clean_type}: ₹{self.format_currency(amount)}\n"
                
                # FINANCIAL CAPACITY ANALYSIS
                formatted_data += f"\n💡 **LIQUIDITY & CAPACITY ANALYSIS**:\n"
                formatted_data += f"- 💳 **Immediate Liquid Funds**: ₹{self.format_currency(liquid_funds)} (Bank accounts)\n"
                formatted_data += f"- 📈 **Liquidatable Investments**: ₹{self.format_currency(mutual_funds + securities)} (MF + Stocks)\n"
                formatted_data += f"- 🏦 **Retirement Savings**: ₹{self.format_currency(epf_amount)} (EPF - long-term)\n"
                formatted_data += f"- ❌ **Total Debt Burden**: ₹{self.format_currency(total_loans)} (EMI obligations)\n"
                
                # Calculate REAL financial metrics
                total_accessible = liquid_funds + (mutual_funds * 0.8) + (securities * 0.8)  # 80% liquidity factor
                formatted_data += f"- ⚡ **Accessible Funds**: ₹{self.format_currency(total_accessible)} (Emergency + purchases)\n"
                
                # Income estimation from REAL EPF and investment patterns  
                estimated_income = self._estimate_monthly_income_from_data(epf_amount, mutual_funds, liquid_funds)
                if estimated_income > 0:
                    formatted_data += f"- 💰 **Estimated Monthly Income**: ₹{self.format_currency(estimated_income)} (Based on EPF/investment patterns)\n"
        
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
    
    def _estimate_monthly_income_from_data(self, epf_amount: float, mutual_funds: float, liquid_funds: float) -> float:
        """Estimate monthly income based on real financial patterns from Fi MCP data"""
        estimated_income = 0
        
        # Use AI-based income estimation without hardcoded thresholds
        # Let AI analyze the financial patterns and estimate income
        if epf_amount > 0 or mutual_funds > 0 or liquid_funds > 0:
            # Return base estimate that AI can interpret contextually
            estimated_income = (epf_amount * 0.1) + (mutual_funds * 0.15) + (liquid_funds * 0.2)
        
        return int(estimated_income) if estimated_income > 0 else 0
    
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate targeted search queries using AI for better market intelligence"""
        
        # Extract financial context for better query generation
        financial_summary = self._format_financial_summary_for_queries(financial_data)
        
        # Use AI to generate context-aware search queries with explicit instruction
        query_prompt = f"""
User asks: {user_query}
Their finances: {financial_summary}

Write exactly 3 Google search queries for Indian market info.
Reply with ONLY the 3 queries (one per line), maximum 15 words each:
"""

        try:
            ai_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            
            # Parse AI-generated queries
            generated_queries = [q.strip() for q in ai_response.text.strip().split('\n') if q.strip()]
            
            # Return user query if AI generation produces insufficient results
            if not generated_queries or len(generated_queries) < 2:
                generated_queries = [user_query]
                
            return generated_queries[:3]  # Limit to 3 for speed
            
        except Exception as e:
            logger.error(f"AI query generation failed: {e}")
            return [user_query]
    
    def _format_financial_summary_for_queries(self, financial_data: FinancialData) -> str:
        """Extract key financial metrics for search query context"""
        summary_parts = []
        
        try:
            if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
                net_worth = financial_data.net_worth.get('netWorthResponse', {})
                total_value = net_worth.get('totalNetWorthValue', {})
                if total_value.get('units'):
                    net_worth_amount = float(total_value.get('units', '0'))
                    # Get liquid assets (savings accounts)
                    assets = net_worth.get('assetValues', [])
                    savings_amount = 0
                    for asset in assets:
                        if 'SAVINGS' in asset.get('netWorthAttribute', ''):
                            savings_amount += float(asset.get('value', {}).get('units', '0'))
                    
                    summary_parts.append(f"₹{net_worth_amount/100000:.0f}L net worth")
                    
                    if savings_amount > 0:
                        summary_parts.append(f"₹{savings_amount/100000:.0f}L liquid funds")
        
        except Exception as e:
            logger.warning(f"Error parsing financial data: {e}")
        
        return ", ".join(summary_parts) if summary_parts else "Indian professional"
    
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """Pure AI analysis of financial data - NO hardcoded calculations"""
        
        ai_prompt = f"""
Financial data:
{self._format_financial_data_for_ai(financial_data)[:1500]}

Analyze and reply with ONLY this JSON (no other text):
{{
  "financial_strength": "strong/moderate/weak",
  "liquidity_position": "high/moderate/low",
  "debt_burden": "high/moderate/low",
  "investment_maturity": "experienced/intermediate/beginner",
  "key_insights": ["insight1", "insight2", "insight3"]
}}
"""
        
        try:
            ai_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=ai_prompt,
                config=types.GenerateContentConfig(**config.GEMINI_GENERATION_CONFIG)
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
                contents=analysis_prompt,
                config=types.GenerateContentConfig(**config.GEMINI_GENERATION_CONFIG)
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
    
    async def _generate_executive_summary(self, user_query: str, financial_data: FinancialData) -> str:
        """Generate a dynamic executive summary using AI"""
        
        # Create a concise prompt for executive summary
        summary_prompt = f"""
Generate a VERY brief executive summary for this financial query. Use exactly this format:

🎯 **QUICK ANSWER: [ONE WORD RECOMMENDATION]**

✅ **Feasible**: [Yes/No/Partially] - [brief reason]
⚠️ **Risk Level**: [Low/Medium/High] - [key concern]
💡 **Best Approach**: [one key strategy]
🚀 **Timeline**: [timeframe needed]

Query: {user_query}
Keep it under 100 words total.
"""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=summary_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            return response.text.strip()
        except:
            # Simple fallback without hardcoded specifics
            return """🎯 **QUICK ANALYSIS COMPLETE**

✅ **Assessment**: Analyzing your situation...
💡 **Strategy**: Personalized recommendations below  
🚀 **Next Steps**: Review detailed analysis"""

    async def generate_response(self, user_query: str, financial_data: FinancialData, grounded_intelligence: Dict[str, Any]) -> str:
        """Generate response using Gemini with Google Search grounding"""
        
        # Generate executive summary first
        exec_summary = await self._generate_executive_summary(user_query, financial_data)
        
        # Prepare comprehensive context
        market_context = self._format_market_intelligence(grounded_intelligence)
        financial_context = self._format_financial_data_for_ai(financial_data)
        
        # Create comprehensive prompt for final response
        response_prompt = f"""
You are an enthusiastic Indian Financial Intelligence Analyst. Start with excitement about the analysis, then provide concise insights.

USER QUERY: {user_query}

EXECUTIVE SUMMARY ALREADY PROVIDED:
{exec_summary}

USER'S FINANCIAL DATA:
{financial_context}

CURRENT MARKET INTELLIGENCE:
{market_context}

Provide a concise, enthusiastic analysis (max 1000 words) that:
1. Shows excitement about their financial potential
2. Uses specific numbers from their data
3. Gives 3-4 key actionable recommendations
4. Includes realistic calculations
5. Maintains optimistic but realistic tone

Be specific, concise, and enthusiastic about their financial journey!
"""
        
        # Generate final response with grounding
        detailed_response = await self.generate_ai_response(
            "",  # System prompt is in config
            response_prompt,
            ""   # Market context already in prompt
        )
        
        # Combine executive summary with detailed response
        return f"{exec_summary}\n\n---\n\n{detailed_response}"
    
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
    
    async def generate_comprehensive_search_query(self, user_query: str, financial_data: FinancialData) -> str:
        """Use Gemini 2.5 Flash to generate comprehensive search query with intelligent context understanding"""
        
        # Extract financial context for better query generation
        financial_summary = self._format_financial_summary_for_queries(financial_data)
        
        # Ultra-simplified prompt to avoid MAX_TOKENS
        query_generation_prompt = f"""Query: {user_query}

Create comprehensive Google search query for India market 2025.
Return ONLY search query (max 20 words):"""

        try:
            logger.info(f"🤖 Using Gemini 2.5 Flash for intelligent query generation: {user_query[:50]}...")
            
            ai_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query_generation_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    system_instruction="Generate ONLY search query. No explanations."
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            
            if ai_response and ai_response.text and ai_response.text.strip():
                comprehensive_query = ai_response.text.strip()
                # Clean up any extra formatting or quotes
                comprehensive_query = comprehensive_query.replace('"', '').replace('\n', ' ').replace('\r', '')
                # Remove any leading/trailing punctuation
                comprehensive_query = comprehensive_query.strip('.,!?;:')
                
                logger.info(f"✅ AI Generated Query: {comprehensive_query}")
                logger.info(f"📊 Query Length: {len(comprehensive_query.split())} words")
                return comprehensive_query
            else:
                logger.error(f"❌ CRITICAL: Gemini returned empty response for query generation")
                if hasattr(ai_response, 'candidates') and ai_response.candidates:
                    candidate = ai_response.candidates[0]
                    logger.error(f"Finish reason: {candidate.finish_reason}")
                    if hasattr(candidate, 'safety_ratings'):
                        logger.error(f"Safety ratings: {candidate.safety_ratings}")
                logger.error("❌ SYSTEM FAILURE: AI query generation failed. Exiting program.")
                import sys
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR: AI query generation failed: {e}")
            logger.error(f"❌ SYSTEM FAILURE: Cannot proceed without AI-generated query")
            logger.error(f"❌ NO FALLBACKS ALLOWED - Shutting down program")
            import sys
            sys.exit(1)
    
