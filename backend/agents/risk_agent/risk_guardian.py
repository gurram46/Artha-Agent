"""
Pure AI-Powered Financial Risk Intelligence Agent 🛡️
Leverages Gemini AI for comprehensive risk assessment and protection planning
No hardcoded risk models - Pure AI reasoning with Fi MCP data + Google Search Intelligence
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseFinancialAgent, AgentResponse
from core.fi_mcp.client import FinancialData
from core.google_grounding.grounding_client import GroundingResult
from google.genai import types

logger = logging.getLogger(__name__)

class RiskAgent(BaseFinancialAgent):
    """Pure AI-Powered Financial Risk Intelligence Agent - Zero hardcoded risk models, pure Gemini intelligence"""
    
    def __init__(self):
        super().__init__("risk")
        logger.info("🛡️ Pure AI Financial Risk Intelligence Agent initialized - Gemini powered risk assessment")
    
    def get_risk_assessment_system_prompt(self, user_query: str, financial_data: FinancialData) -> str:
        """Generate comprehensive system prompt for Gemini AI risk assessment"""
        
        return f"""
You are an expert Indian Financial Risk Intelligence Agent powered by Gemini AI. Your role is to conduct comprehensive risk assessment and protection planning using ONLY the actual financial data provided and current INDIAN market intelligence from Google Search.

**CORE PRINCIPLES:**
1. Assess risks ONLY based on actual financial data provided - no generic risk models
2. Use your AI reasoning to identify personalized risks and protection needs
3. Leverage real market intelligence from search results for risk mitigation strategies
4. Provide specific, actionable risk management recommendations based on the user's actual situation
5. NO hardcoded risk formulas - use intelligent risk reasoning

**USER'S ACTUAL FINANCIAL DATA:**
{self._format_financial_data_for_risk_assessment(financial_data)}

**USER QUERY:** {user_query}

**YOUR RISK ANALYSIS FRAMEWORK:**

1. **FINANCIAL POSITION RISK ASSESSMENT:**
   - Analyze the user's actual financial vulnerabilities from data above
   - Identify liquidity risks based on actual cash flow and emergency fund status
   - Evaluate debt-related risks using actual credit and loan obligations
   - Assess investment concentration risks from current portfolio

2. **QUERY-SPECIFIC RISK ANALYSIS:**
   - For purchase decisions: Analyze affordability risk, financing risk, and opportunity cost risk
   - For career decisions: Assess income disruption risk, emergency fund adequacy, and transition risks
   - For investment decisions: Evaluate market risk, concentration risk, and liquidity risk
   - For housing decisions: Analyze market timing risk, financing risk, and mobility risk
   - For travel/lifestyle decisions: Assess discretionary spending risk and emergency impact

3. **MARKET-BASED RISK INTELLIGENCE:**
   - Use Google Search results to understand current market risks and trends
   - Factor in economic conditions and their impact on the user's specific situation
   - Identify emerging risks relevant to the user's financial decisions
   - Consider market-specific protection strategies and timing

4. **RISK MITIGATION RECOMMENDATIONS:**
   - Develop specific risk management strategies based on actual financial capacity
   - Suggest appropriate insurance coverage based on current assets and obligations
   - Recommend emergency fund optimization using real income and expense patterns
   - Provide market-timing risk mitigation based on search intelligence

**OUTPUT FORMAT:**
- Start with comprehensive risk assessment of current financial position
- Identify specific risks related to the user's query with severity levels
- Provide concrete risk mitigation strategies with specific amounts and actions
- Include market-based risk alerts and protection opportunities
- End with emergency contingency planning and protection recommendations

**REMEMBER:** Use only the actual financial data provided. Your AI risk reasoning should identify real vulnerabilities and provide personalized risk management based on current market conditions from search results. No generic risk percentages - pure intelligent risk analysis.
"""
    
    def _format_financial_data_for_risk_assessment(self, financial_data: FinancialData) -> str:
        """Format actual financial data for AI risk assessment"""
        
        formatted_data = """
**FINANCIAL RISK PROFILE:**
"""
        
        # Liquidity Risk Analysis
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth
            if 'netWorthResponse' in net_worth:
                total_value = net_worth['netWorthResponse'].get('totalNetWorthValue', {})
                formatted_data += f"- Total Net Worth: {total_value.get('units', 'N/A')} {total_value.get('currencyCode', '')}\n"
                
                assets = net_worth['netWorthResponse'].get('assetValues', [])
                formatted_data += "- Asset Risk Distribution:\n"
                
                liquid_assets = 0
                illiquid_assets = 0
                
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {})
                    asset_value = value.get('units', 'N/A')
                    
                    # Categorize by liquidity risk
                    if 'SAVINGS' in asset_type or 'DEPOSIT' in asset_type:
                        risk_category = "Low Liquidity Risk"
                        try:
                            liquid_assets += float(asset_value) if asset_value != 'N/A' else 0
                        except:
                            pass
                    elif 'MUTUAL_FUND' in asset_type:
                        risk_category = "Medium Liquidity Risk (1-3 days)"
                    elif 'SECURITIES' in asset_type:
                        risk_category = "Medium-High Liquidity Risk (market dependent)"
                    elif 'EPF' in asset_type:
                        risk_category = "High Liquidity Risk (locked until retirement)"
                        try:
                            illiquid_assets += float(asset_value) if asset_value != 'N/A' else 0
                        except:
                            pass
                    else:
                        risk_category = "Unknown Liquidity Risk"
                    
                    formatted_data += f"  • {asset_type}: ₹{asset_value} ({risk_category})\n"
                
                # Liquidity risk ratio
                total_assets = liquid_assets + illiquid_assets
                if total_assets > 0:
                    liquidity_ratio = (liquid_assets / total_assets) * 100
                    formatted_data += f"\n**LIQUIDITY RISK ASSESSMENT:** {liquidity_ratio:.1f}% in liquid assets\n"
        
        # Credit and Debt Risk Analysis
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_data = financial_data.credit_report
            formatted_data += "\n**CREDIT & DEBT RISK PROFILE:**\n"
            
            if 'creditReports' in credit_data and credit_data['creditReports']:
                credit_report = credit_data['creditReports'][0].get('creditReportData', {})
                score = credit_report.get('score', {}).get('bureauScore', 'N/A')
                
                # Credit score risk assessment
                if score != 'N/A':
                    try:
                        credit_score = int(score)
                        if credit_score >= 750:
                            credit_risk = "Low Credit Risk (Excellent Score)"
                        elif credit_score >= 700:
                            credit_risk = "Low-Medium Credit Risk (Good Score)"
                        elif credit_score >= 650:
                            credit_risk = "Medium Credit Risk (Fair Score)"
                        else:
                            credit_risk = "High Credit Risk (Poor Score)"
                    except:
                        credit_risk = "Unknown Credit Risk"
                else:
                    credit_risk = "No Credit History Risk"
                
                formatted_data += f"- Credit Score: {score} ({credit_risk})\n"
                
                # Debt obligations risk
                credit_summary = credit_report.get('creditAccount', {}).get('creditAccountSummary', {})
                if credit_summary:
                    total_balance = credit_summary.get('totalOutstandingBalance', {})
                    secured_debt = total_balance.get('outstandingBalanceSecured', 'N/A')
                    unsecured_debt = total_balance.get('outstandingBalanceUnSecured', 'N/A')
                    total_debt = total_balance.get('outstandingBalanceAll', 'N/A')
                    
                    formatted_data += f"- Debt Risk Exposure: Total: ₹{total_debt}, Secured: ₹{secured_debt}, Unsecured: ₹{unsecured_debt}\n"
                    
                    # High-risk unsecured debt analysis
                    try:
                        if unsecured_debt != 'N/A' and float(unsecured_debt) > 0:
                            formatted_data += f"- High-Risk Unsecured Debt: ₹{unsecured_debt} (requires immediate attention)\n"
                    except:
                        pass
                
                # Credit utilization risk
                credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
                if credit_accounts:
                    formatted_data += "- Credit Utilization Risk Analysis:\n"
                    for account in credit_accounts[:3]:
                        subscriber = account.get('subscriberName', 'Unknown')
                        current_balance = account.get('currentBalance', 'N/A')
                        credit_limit = account.get('creditLimitAmount', 'N/A')
                        
                        if credit_limit != 'N/A' and credit_limit != '0' and current_balance != 'N/A':
                            try:
                                utilization = (float(current_balance) / float(credit_limit)) * 100
                                if utilization > 80:
                                    util_risk = "Very High Utilization Risk"
                                elif utilization > 60:
                                    util_risk = "High Utilization Risk"
                                elif utilization > 30:
                                    util_risk = "Medium Utilization Risk"
                                else:
                                    util_risk = "Low Utilization Risk"
                                formatted_data += f"  • {subscriber}: {utilization:.1f}% utilization ({util_risk})\n"
                            except:
                                formatted_data += f"  • {subscriber}: Unable to calculate utilization risk\n"
        
        # Investment Risk Analysis
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth and 'mfSchemeAnalytics' in financial_data.net_worth:
            mf_data = financial_data.net_worth['mfSchemeAnalytics'].get('schemeAnalytics', [])
            if mf_data:
                formatted_data += "\n**INVESTMENT PORTFOLIO RISK ANALYSIS:**\n"
                
                risk_distribution = {
                    'VERY_HIGH_RISK': 0,
                    'HIGH_RISK': 0,
                    'MODERATE_RISK': 0,
                    'LOW_RISK': 0,
                    'UNKNOWN_RISK': 0
                }
                
                total_portfolio_value = 0
                
                for fund in mf_data:
                    scheme = fund.get('schemeDetail', {})
                    analytics = fund.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                    fund_name = scheme.get('nameData', {}).get('longName', 'Unknown Fund')
                    fund_category = scheme.get('categoryName', 'Unknown Category')
                    risk_level = scheme.get('fundhouseDefinedRiskLevel', 'UNKNOWN_RISK')
                    asset_class = scheme.get('assetClass', 'Unknown')
                    current_value = analytics.get('currentValue', {})
                    xirr = analytics.get('XIRR', 'N/A')
                    
                    try:
                        fund_value = float(current_value.get('units', '0'))
                        total_portfolio_value += fund_value
                        
                        if risk_level in risk_distribution:
                            risk_distribution[risk_level] += fund_value
                        else:
                            risk_distribution['UNKNOWN_RISK'] += fund_value
                    except:
                        pass
                    
                    # Individual fund risk assessment
                    if 'EQUITY' in asset_class.upper():
                        market_risk = "High Market Risk (Equity exposure)"
                    elif 'DEBT' in asset_class.upper():
                        market_risk = "Low-Medium Market Risk (Debt exposure)"
                    else:
                        market_risk = "Unknown Market Risk"
                    
                    formatted_data += f"- {fund_name}: ₹{current_value.get('units', 'N/A')} ({risk_level}, {market_risk})\n"
                
                # Portfolio risk concentration analysis
                if total_portfolio_value > 0:
                    formatted_data += "\n**PORTFOLIO RISK CONCENTRATION:**\n"
                    for risk_level, value in risk_distribution.items():
                        if value > 0:
                            percentage = (value / total_portfolio_value) * 100
                            formatted_data += f"- {risk_level.replace('_', ' ').title()}: {percentage:.1f}% (₹{value:.0f})\n"
        
        # Employment and Income Risk Analysis
        if hasattr(financial_data, 'epf_details') and financial_data.epf_details:
            epf_data = financial_data.epf_details
            formatted_data += "\n**EMPLOYMENT & INCOME RISK ANALYSIS:**\n"
            
            if 'uanAccounts' in epf_data and epf_data['uanAccounts']:
                epf_account = epf_data['uanAccounts'][0].get('rawDetails', {})
                
                # Employment stability risk
                est_details = epf_account.get('est_details', [])
                if est_details:
                    current_employer = est_details[-1]
                    employer_name = current_employer.get('est_name', 'Unknown')
                    doj = current_employer.get('doj_epf', 'Unknown')
                    doe = current_employer.get('doe_epf', 'Unknown')
                    
                    # Calculate employment tenure risk
                    if doj != 'Unknown':
                        try:
                            from datetime import datetime
                            start_date = datetime.strptime(doj, '%d-%m-%Y')
                            current_date = datetime.now()
                            tenure_years = (current_date - start_date).days / 365.25
                            
                            if tenure_years < 1:
                                employment_risk = "High Employment Risk (Short tenure)"
                            elif tenure_years < 3:
                                employment_risk = "Medium Employment Risk (Moderate tenure)"
                            else:
                                employment_risk = "Low Employment Risk (Stable tenure)"
                        except:
                            employment_risk = "Unknown Employment Risk"
                    else:
                        employment_risk = "Unknown Employment Risk"
                    
                    formatted_data += f"- Current Employment: {employer_name} (Since: {doj}) - {employment_risk}\n"
                    
                    # Job change frequency risk
                    if len(est_details) > 3:
                        formatted_data += f"- Job Change Pattern: {len(est_details)} employers (High mobility risk)\n"
                    elif len(est_details) > 1:
                        formatted_data += f"- Job Change Pattern: {len(est_details)} employers (Moderate mobility risk)\n"
                    else:
                        formatted_data += f"- Job Change Pattern: Single employer (Low mobility risk)\n"
                
                # Retirement security risk
                overall_balance = epf_account.get('overall_pf_balance', {})
                current_balance = overall_balance.get('current_pf_balance', 'N/A')
                
                if current_balance != 'N/A':
                    try:
                        epf_balance = float(current_balance)
                        formatted_data += f"- Retirement Security: ₹{current_balance} EPF\n"
                    except:
                        formatted_data += f"- Retirement Security: Unable to assess risk\n"
        
        # Emergency Fund Risk Analysis
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth and 'accountDetailsBulkResponse' in financial_data.net_worth:
            accounts = financial_data.net_worth['accountDetailsBulkResponse'].get('accountDetailsMap', {})
            if accounts:
                formatted_data += "\n**EMERGENCY FUND RISK ANALYSIS:**\n"
                total_emergency_funds = 0
                
                for account_id, account_info in accounts.items():
                    deposit_summary = account_info.get('depositSummary', {})
                    balance = deposit_summary.get('currentBalance', {})
                    account_details = account_info.get('accountDetails', {})
                    bank_name = account_details.get('fipMeta', {}).get('displayName', 'Unknown Bank')
                    account_type = deposit_summary.get('depositAccountType', 'Unknown Type')
                    
                    if balance and balance.get('units'):
                        try:
                            balance_amount = float(balance.get('units', '0'))
                            total_emergency_funds += balance_amount
                            formatted_data += f"- {bank_name} ({account_type}): ₹{balance.get('units', 'N/A')}\n"
                        except:
                            pass
                
                # Overall emergency fund total
                if total_emergency_funds > 0:
                    formatted_data += f"\n**TOTAL LIQUID EMERGENCY FUNDS: ₹{total_emergency_funds:.0f}**\n"
        
        return formatted_data
    
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Pure AI-powered risk query generation using Gemini AI - NO hardcoded functions"""
        
        # Use AI to generate risk intelligence queries - Optimized for Speed
        ai_prompt = f"""
Generate 3 targeted Google search queries for Indian financial risk assessment:

User Query: {user_query}
Financial Context: {self._format_financial_summary_for_queries(financial_data)}

Focus on CURRENT Indian market risks:
1. Insurance and protection strategies
2. Market risks and emergency planning
3. Regulatory compliance and safeguards

Return ONLY search queries, one per line.
"""
        
        try:
            ai_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=ai_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            
            # Parse AI response into query list
            queries = [line.strip() for line in ai_response.text.strip().split('\n') if line.strip()]
            return queries[:3]  # Reduced to 3 for speed
            
        except Exception as e:
            logger.error(f"AI risk query generation failed: {e}")
            return [
                f"{user_query} insurance protection India 2025",
                "financial risk management India emergency fund",
                "investment protection strategies India market risk 2025"
            ]
    
    def _format_financial_summary_for_queries(self, financial_data: FinancialData) -> str:
        """Extract key financial metrics for risk assessment query context"""
        summary_parts = []
        
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth.get('netWorthResponse', {})
            total_value = net_worth.get('totalNetWorthValue', {})
            if total_value.get('units'):
                net_worth_amount = float(total_value.get('units', '0'))
                summary_parts.append(f"Net worth ₹{self.format_currency(net_worth_amount)}")
        
        return ", ".join(summary_parts) if summary_parts else "General user"
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """Pure AI risk analysis of financial data - NO hardcoded calculations"""
        
        ai_prompt = f"""
Analyze this user's financial data for risk assessment and provide a comprehensive risk evaluation:

{self._format_financial_data_for_risk_assessment(financial_data)}

Provide risk analysis in JSON format with these keys:
- overall_risk_level: (critical/high/medium/low)
- liquidity_risk: (critical/high/medium/low)
- credit_risk: (critical/high/medium/low)
- investment_risk: (critical/high/medium/low)
- employment_risk: (critical/high/medium/low)
- emergency_preparedness: (excellent/good/fair/poor)
- key_vulnerabilities: [list of 3-5 key financial vulnerabilities]
- protection_priorities: [list of 3-5 protection priorities]

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
            logger.error(f"AI risk analysis failed: {e}")
            return {
                'overall_risk_level': 'medium',
                'liquidity_risk': 'medium',
                'credit_risk': 'medium',
                'investment_risk': 'medium',
                'employment_risk': 'medium',
                'emergency_preparedness': 'fair',
                'key_vulnerabilities': ['Risk analysis in progress'],
                'protection_priorities': ['Protection assessment being generated']
            }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], financial_data: FinancialData) -> Dict[str, Any]:
        """Process risk-focused search results using AI"""
        
        # Combine search findings
        risk_findings = []
        all_sources = []
        
        for result in search_results:
            risk_findings.append(f"Risk Query: {result['query']}\nFindings: {result['findings']}")
            all_sources.extend(result.get('sources', []))
        
        combined_findings = "\n\n---\n\n".join(risk_findings)
        
        # Analyze for risk insights
        analysis_prompt = f"""
Analyze these risk intelligence findings:

{combined_findings}

User's Risk Profile:
{self._format_financial_data_for_risk_assessment(financial_data)[:1000]}

Extract risk insights:
1. Critical risks that need immediate attention
2. Protection gaps in current financial position
3. Specific insurance products recommended
4. Emergency fund requirements based on situation
5. Risk mitigation strategies with concrete steps
6. Cost estimates for protection measures

Provide response in JSON format:
{{
  "critical_risks": ["risk1", "risk2", ...],
  "protection_gaps": ["gap1", "gap2", ...],
  "insurance_recommendations": [
    {{"type": "insurance_type", "coverage": "amount", "premium_estimate": "amount"}}
  ],
  "emergency_fund_target": "specific amount based on analysis",
  "mitigation_strategies": ["strategy1", "strategy2", ...],
  "protection_costs": {{"insurance": "estimate", "emergency_fund": "monthly_saving_needed"}},
  "risk_score": "high/medium/low"
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
            logger.error(f"Risk analysis failed: {e}")
            return {
                'critical_risks': ['Risk assessment pending'],
                'protection_gaps': ['Gap analysis in progress'],
                'insurance_recommendations': [],
                'emergency_fund_target': 'Calculating...',
                'mitigation_strategies': ['Strategy development ongoing'],
                'protection_costs': {},
                'sources': all_sources,
                'risk_score': 'medium'
            }
    
    
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, grounded_intelligence: Dict[str, Any]) -> str:
        """Generate AI-powered risk assessment response using system prompt and market intelligence"""
        
        # Create risk assessment system prompt for Gemini AI
        system_prompt = self.get_risk_assessment_system_prompt(user_query, financial_data)
        
        # Format risk intelligence and financial data
        risk_context = self._format_risk_intelligence(grounded_intelligence)
        financial_context = self._format_financial_data_for_risk_assessment(financial_data)
        
        # Create risk assessment prompt
        response_prompt = f"""
You are a Risk Management Expert. Provide a comprehensive risk assessment using real market data.

USER QUERY: {user_query}

USER'S RISK PROFILE:
{financial_context}

CURRENT RISK INTELLIGENCE (from Google Search):
{risk_context}

Provide a detailed risk assessment that:
1. Identifies and quantifies specific risks related to their query
2. Uses actual insurance products and costs from search results
3. Recommends specific protection measures with costs
4. Calculates appropriate emergency fund based on their situation
5. Provides step-by-step risk mitigation plan
6. Includes both immediate actions and long-term protection strategies

Structure your response with:
- Risk Assessment Summary (with risk score)
- Critical Risks Identified (with severity levels)
- Protection Recommendations (specific products & costs)
- Emergency Fund Analysis (target amount & timeline)
- Risk Mitigation Action Plan (prioritized steps)
- Cost-Benefit Analysis of Protection Measures
"""
        
        # Generate risk assessment response
        return await self.generate_ai_response(
            "",  # System prompt in config
            response_prompt,
            ""   # Context in prompt
        )
    
    def _format_risk_intelligence(self, intelligence: Dict[str, Any]) -> str:
        """Format risk intelligence for response"""
        sections = []
        
        if intelligence.get('critical_risks'):
            sections.append("Critical Risks Identified:\n" + "\n".join(f"• {risk}" for risk in intelligence['critical_risks']))
        
        if intelligence.get('protection_gaps'):
            sections.append("Protection Gaps:\n" + "\n".join(f"• {gap}" for gap in intelligence['protection_gaps']))
        
        if intelligence.get('insurance_recommendations'):
            insurance_text = "Insurance Recommendations:\n"
            for rec in intelligence['insurance_recommendations']:
                if isinstance(rec, dict):
                    insurance_text += f"• {rec.get('type', 'Insurance')}: Coverage ₹{rec.get('coverage', 'TBD')}, Premium ~₹{rec.get('premium_estimate', 'TBD')}\n"
                else:
                    insurance_text += f"• {rec}\n"
            sections.append(insurance_text.rstrip())
        
        if intelligence.get('emergency_fund_target'):
            sections.append(f"Emergency Fund Target: {intelligence['emergency_fund_target']}")
        
        if intelligence.get('mitigation_strategies'):
            sections.append("Risk Mitigation Strategies:\n" + "\n".join(f"• {strategy}" for strategy in intelligence['mitigation_strategies']))
        
        if intelligence.get('risk_score'):
            sections.append(f"\nOverall Risk Level: {intelligence['risk_score'].upper()}")
        
        if intelligence.get('sources'):
            sections.append(f"\nBased on {len(intelligence['sources'])} verified sources")
        
        return "\n\n".join(sections) if sections else "Risk intelligence being processed"
    
    async def assess_comprehensive_risks(self, user_query: str, research_response: Dict[str, Any], market_intelligence: Dict[str, Any]) -> Dict[str, str]:
        """Assess comprehensive risks based on data analysis, research findings, and market intelligence"""
        
        # Pure risk analysis prompt - NO user financial data
        research_summary = research_response.get('content', 'No research available')[:1500] + "..." if len(research_response.get('content', '')) > 1500 else research_response.get('content', 'No research available')
        
        risk_prompt = f"""
You are the Risk Assessment Agent. Provide comprehensive risk analysis for this investment/financial decision.

USER QUESTION: {user_query}

STRATEGIC RESEARCH ANALYSIS:
{research_summary}

LIVE MARKET DATA: {len(market_intelligence.get('sources', []))} sources analyzed

Provide comprehensive risk analysis covering:
1. **Market & Investment Risks** - Specific risks related to this opportunity
2. **Timing & Volatility Risks** - Market timing and volatility considerations
3. **Risk Mitigation Strategies** - General strategies to minimize risks
4. **Protection Measures** - Recommended safeguards and best practices
5. **Timeline Considerations** - Risk management over time

Focus on investment/decision-specific risks and general risk management strategies. Do NOT provide personalized financial advice - that will be handled separately.
Be thorough and analytical using the research and market data provided."""
        
        try:
            logger.info(f"🛡️ Risk Agent: Processing prompt of {len(risk_prompt)} characters")
            
            # Generate comprehensive risk assessment
            risk_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=risk_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3  # Lower temperature for more conservative risk assessment
                    # Removed max_output_tokens to fix Gemini API bug
                )
            )
            
            logger.info(f"🛡️ Risk Agent: API response received, type: {type(risk_response)}")
            
            if risk_response and hasattr(risk_response, 'text') and risk_response.text and risk_response.text.strip():
                risk_content = risk_response.text.strip()
                logger.info(f"✅ Risk Agent: Generated comprehensive risk assessment ({len(risk_content)} chars)")
            else:
                logger.error(f"❌ Risk Agent: AI response failed")
                if hasattr(risk_response, 'text'):
                    logger.error(f"Response text: '{risk_response.text}'")
                if hasattr(risk_response, 'candidates') and risk_response.candidates:
                    logger.error(f"Candidates: {risk_response.candidates}")
                    if hasattr(risk_response.candidates[0], 'finish_reason'):
                        logger.error(f"Finish reason: {risk_response.candidates[0].finish_reason}")
                logger.error(f"❌ CRITICAL: Risk Agent failed - returning fallback response")
                # Return a fallback response instead of crashing the server
                return {
                    'agent': 'Comprehensive Risk Assessment',
                    'content': 'Risk assessment temporarily unavailable. Please consider general investment risks: market volatility, economic uncertainty, and portfolio diversification needs.',
                    'emoji': '🛡️',
                    'market_sources': len(market_intelligence.get('sources', [])),
                    'data_analysis_integrated': True,
                    'status': 'fallback'
                }
            
            return {
                'agent': 'Comprehensive Risk Assessment',
                'content': risk_content,
                'emoji': '🛡️',
                'market_sources': len(market_intelligence.get('sources', [])),
                'data_analysis_integrated': True,
                'research_integrated': True
            }
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR: Risk Agent comprehensive risk assessment failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"❌ SYSTEM FAILURE: Cannot proceed without risk assessment")
            import sys
            sys.exit(1)
    
