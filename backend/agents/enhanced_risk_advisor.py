"""
Enhanced Risk Advisor Agent - Pure AI-driven comprehensive risk assessment and protection planning
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
from .base_agent import BaseFinancialAgent
from core.fi_mcp.client import FinancialData

logger = logging.getLogger(__name__)


class EnhancedRiskAdvisorAgent(BaseFinancialAgent):
    """Enhanced Risk Advisor Agent with specialized AI-driven risk assessment methods"""
    
    def __init__(self):
        super().__init__("risk")
    
    async def assess_portfolio_risks(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI performs comprehensive portfolio risk assessment"""
        try:
            portfolio_json = json.dumps(portfolio_data, indent=2)
            
            prompt = f"""
Risk check in 3 lines:

DATA: {portfolio_json}

Format:
1. Risk Level: [LOW/MEDIUM/HIGH] - [5 words why]
2. Biggest Risk: [10 words max] - Could lose ₹[amount]
3. Protection Fix: [10 words max] - Save ₹[amount]

Maximum 30 words total.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a concise risk advisor. Give short, specific answers only.",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"portfolio_risk_assessment": response}
                
        except Exception as e:
            logger.error(f"Portfolio risk assessment failed: {e}")
            return {"error": str(e)}
    
    async def analyze_protection_gaps(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI identifies critical protection gaps in financial planning"""
        try:
            financial_json = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
You are an AI Protection Gap Analyst. Identify critical protection gaps in this user's financial plan.

COMPLETE FINANCIAL DATA:
{financial_json}

PROTECTION GAP ANALYSIS:

1. LIFE INSURANCE GAP:
   - Calculate human capital value
   - Assess existing coverage adequacy
   - Identify protection shortfall in ₹
   - Recommend appropriate coverage amounts
   
2. HEALTH INSURANCE GAP:
   - Analyze current health coverage
   - Assess family protection needs
   - Calculate potential medical expense risks
   - Recommend additional coverage needed
   
3. EMERGENCY FUND GAP:
   - Calculate required emergency fund (6-12 months expenses)
   - Assess current liquid funds adequacy
   - Identify shortfall amount
   - Recommend emergency fund building strategy
   
4. DISABILITY PROTECTION GAP:
   - Assess income replacement needs
   - Evaluate existing disability coverage
   - Calculate protection gap for disability scenarios
   - Recommend disability insurance solutions
   
5. CRITICAL ILLNESS PROTECTION:
   - Analyze critical illness coverage needs
   - Assess impact of major illness on finances
   - Calculate required coverage amounts
   - Recommend critical illness planning
   
6. ESTATE PLANNING GAPS:
   - Will and nomination status analysis
   - Asset transmission planning needs
   - Tax implications for beneficiaries
   - Legal documentation requirements

For each protection area:
- Calculate exact ₹ gap amount
- Assess urgency level (CRITICAL/HIGH/MEDIUM/LOW)
- Provide specific product recommendations
- Estimate premium costs and budget impact
- Create implementation timeline

Use their actual financial data to calculate realistic protection needs.
Return as structured JSON with prioritized protection plan.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI Financial Protection Gap Analyst",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"protection_gaps": response}
                
        except Exception as e:
            logger.error(f"Protection gap analysis failed: {e}")
            return {"error": str(e)}
    
    async def stress_test_portfolio(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI performs stress testing on portfolio under various scenarios"""
        try:
            financial_json = json.dumps(mcp_data, indent=2)
            
            prompt = f"""
You are an AI Stress Testing Expert. Perform comprehensive stress tests on this portfolio.

COMPLETE PORTFOLIO DATA:
{financial_json}

STRESS TEST SCENARIOS:

1. MARKET CRASH S
CENARIO:
   - 30-50% market decline impact
   - Portfolio value during crash
   - Recovery timeline analysis
   - Behavioural risk during crash
   
2. ECONOMIC RECESSION SCENARIO:
   - Impact on different asset classes
   - Sector-specific risks in recession
   - Employment/income risk scenarios
   - Liquidity stress during recession
   
3. INTEREST RATE SHOCK:
   - Rising interest rate impact on portfolio
   - Debt servicing stress with higher rates
   - Fixed deposit vs equity trade-offs
   - Refinancing opportunities/risks
   
4. INFLATION STRESS TEST:
   - High inflation impact on returns
   - Real return erosion analysis
   - Asset class protection against inflation
   - Purchasing power preservation strategies
   
5. PERSONAL CRISIS SCENARIOS:
   - Job loss impact and survival analysis
   - Medical emergency financial impact
   - Family emergency fund requirements
   - Forced liquidation scenarios
   
6. SEQUENCE OF RETURNS RISK:
   - Poor returns in early retirement impact
   - SWP sustainability analysis
   - Goal achievement under poor sequence
   - Recovery strategies for poor timing

For each stress test:
- Calculate specific portfolio impact in ₹
- Assess survival/recovery timeline
- Identify most vulnerable areas
- Recommend stress mitigation strategies
- Provide contingency planning steps

Use actual portfolio composition and returns for realistic stress analysis.
Return as structured JSON with stress test results and mitigation plans.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI Portfolio Stress Testing Expert",
                user_context=prompt
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"stress_test_results": response}
                
        except Exception as e:
            logger.error(f"Portfolio stress testing failed: {e}")
            return {"error": str(e)}
    
    # Base class required methods - enhanced with AI
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate AI-powered risk research queries"""
        try:
            financial_context = self._format_financial_summary(financial_data)
            
            prompt = f"""
Generate 3 specific risk research queries to identify current financial risks and protection strategies.

USER QUERY: {user_query}
USER'S FINANCIAL CONTEXT: {financial_context}

Create search queries that will find:
1. Current market risks and volatility factors affecting their portfolio
2. Protection and insurance strategies for their life situation
3. Risk management and diversification expert recommendations

Focus on risk assessment, protection planning, and safety strategies.
Return only the search queries, one per line.
"""

            response = await self.generate_ai_response(
                system_prompt="You are an AI risk research query generator",
                user_context=prompt
            )
            
            # Extract queries from response
            queries = [q.strip() for q in response.split('\n') if q.strip()][:3]
            return queries if queries else [f"{user_query} financial risk management India 2024"]
            
        except Exception as e:
            logger.error(f"Risk query generation failed: {e}")
            return [f"{user_query} financial protection strategies India"]
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """AI-driven risk-focused analysis of financial data"""
        try:
            data_dict = {
                "net_worth": getattr(financial_data, 'net_worth', {}),
                "credit_report": getattr(financial_data, 'credit_report', {}),
                "epf_details": getattr(financial_data, 'epf_details', {})
            }
            
            financial_json = json.dumps(data_dict, indent=2)
            
            prompt = f"""
Analyze this portfolio from a Risk Management perspective:

FINANCIAL DATA:
{financial_json}

Provide risk-focused analysis covering:

1. IMMEDIATE RISK ALERTS:
   - High-priority risks requiring urgent attention
   - Critical protection gaps that could cause financial ruin
   - Concentration risks that threaten portfolio stability
   
2. RISK PROFILE ASSESSMENT:
   - Current portfolio risk level vs appropriate risk for their situation
   - Risk-return balance analysis
   - Volatility and downside risk evaluation
   
3. PROTECTION ADEQUACY:
   - Emergency fund sufficiency
   - Insurance coverage gaps
   - Credit risk assessment
   
4. STRATEGIC RISK RECOMMENDATIONS:
   - Risk diversification opportunities
   - Portfolio protection strategies
   - Crisis preparation recommendations

Focus on risk identification, quantification, and mitigation strategies.
Return as structured risk analysis with actionable protection plans.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a comprehensive financial risk analyst",
                user_context=prompt
            )
            
            return {"risk_analysis": response}
            
        except Exception as e:
            logger.error(f"Risk-focused financial data analysis failed: {e}")
            return {"error": str(e)}
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], 
                                         financial_data: FinancialData) -> Dict[str, Any]:
        """Process risk intelligence for protection strategies"""
        try:
            # Combine all risk research findings
            risk_intelligence = ""
            for result in search_results:
                risk_intelligence += f"\n{result.get('findings', '')}"
            
            financial_context = self._format_financial_summary(financial_data)
            
            prompt = f"""
Process this risk intelligence to identify specific protection strategies for the user:

RISK INTELLIGENCE:
{risk_intelligence}

USER'S FINANCIAL CONTEXT:
{financial_context}

Extract actionable risk management insights:

1. IMMEDIATE RISKS: Current risks they need to address urgently
2. PROTECTION STRATEGIES: Specific protection products and strategies relevant to current conditions
3. RISK MITIGATION: Concrete steps to reduce portfolio and financial risks
4. CRISIS PREPARATION: How to prepare for potential financial crises based on current risk environment

Focus on specific, implementable risk management strategies.
"""

            response = await self.generate_ai_response(
                system_prompt="You are a risk intelligence processor for financial protection planning",
                user_context=prompt
            )
            
            return {
                "risk_insights": response,
                "protection_sources": len(search_results),
                "risks": []  # Will be extracted from AI response
            }
            
        except Exception as e:
            logger.error(f"Risk intelligence processing failed: {e}")
            return {"error": str(e)}
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, 
                              grounded_intelligence: Dict[str, Any]) -> str:
        """Generate final risk advisor response with protection strategies"""
        try:
            financial_context = self._format_financial_summary(financial_data)
            risk_context = grounded_intelligence.get('risk_insights', '')
            
            prompt = f"""
As a Risk Management Expert AI, provide comprehensive risk-focused advice for the user's question.

USER QUESTION: {user_query}

USER'S FINANCIAL SITUATION:
{financial_context}

CURRENT RISK ENVIRONMENT:
{risk_context}

Provide risk management-focused response that includes:

1. Risk assessment specific to their question and portfolio
2. Current risk environment impact on their financial situation
3. Specific protection strategies and risk mitigation recommendations
4. Crisis preparation and contingency planning advice
5. Implementation priorities for risk management

Be specific about risks and provide actionable protection strategies with quantified benefits.
"""

            return await self.generate_ai_response(
                system_prompt="You are a Risk Management Expert providing comprehensive financial protection advice",
                user_context=prompt,
                market_context=risk_context
            )
            
        except Exception as e:
            logger.error(f"Risk advisor response generation failed: {e}")
            return f"I encountered an error assessing financial risks: {str(e)}"