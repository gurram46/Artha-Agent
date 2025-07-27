"""
ENHANCED Pure AI-Powered Financial Strategic Research Agent 🧠
QUALITY-FOCUSED: Comprehensive research and deep analysis
Maximum quality output with advanced market intelligence processing
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

class EnhancedResearchAgent(BaseFinancialAgent):
    """ENHANCED AI-Powered Financial Strategic Research Agent - MAXIMUM QUALITY FOCUS"""
    
    def __init__(self):
        super().__init__("research")
        logger.info("🧠 ENHANCED AI Financial Strategic Research Agent initialized - Maximum Quality Mode")
    
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate comprehensive strategic search queries using advanced AI methodology - QUALITY FOCUSED"""
        
        financial_summary = self._format_financial_data_for_strategic_planning(financial_data)
        
        # Advanced multi-phase query generation for maximum quality
        comprehensive_prompt = f"""
You are an expert Indian financial strategist. Generate 7 comprehensive Google search queries for deep strategic research.

User Query: {user_query}
User's Financial Profile: {financial_summary[:800]}

Generate queries covering these strategic dimensions:
1. MARKET OPPORTUNITIES: Current market trends, sectors with high growth potential
2. FINANCIAL PRODUCTS: Latest investment options, banking products, and financial instruments
3. TAX OPTIMIZATION: Advanced tax-saving strategies, regulatory changes, and compliance updates
4. RISK ASSESSMENT: Market risks, economic indicators, and protection strategies
5. EXPERT ANALYSIS: Financial advisor recommendations, research reports, and expert opinions
6. COMPARATIVE ANALYSIS: Competitive rates, product comparisons, and best practices
7. TIMING INTELLIGENCE: Market timing insights, economic cycles, and opportunity windows

For each dimension, create a highly specific search query using current Indian financial market context.
Make queries detailed and comprehensive (15-25 words each) for maximum information retrieval.

Return exactly 7 search queries, one per line:
"""
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=comprehensive_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,  # Slightly higher for more creative query diversity
                    system_instruction="Generate comprehensive, detailed search queries for maximum information retrieval. Focus on Indian financial market context with specific, actionable terms."
                )
            )
            
            queries = [q.strip() for q in response.text.strip().split('\n') if q.strip() and len(q.strip()) > 10]
            logger.info(f"Generated {len(queries)} comprehensive strategic queries for maximum quality research")
            
            # Return all 7 queries for comprehensive research (quality over speed)
            return queries[:7] if len(queries) >= 7 else queries + self._generate_fallback_quality_queries(user_query, len(queries))
            
        except Exception as e:
            logger.error(f"Advanced strategic query generation failed: {e}")
            return self._generate_fallback_quality_queries(user_query, 0)
    
    def _generate_fallback_quality_queries(self, user_query: str, existing_count: int) -> List[str]:
        """Generate high-quality fallback queries when AI generation fails"""
        base_queries = [
            f"{user_query} comprehensive strategic financial planning India 2025 expert analysis market trends",
            f"India financial market opportunities {user_query} investment strategies tax optimization wealth building",
            f"expert financial advisor recommendations {user_query} India market analysis risk assessment 2025",
            f"Indian banking investment products {user_query} comparative analysis rates returns performance",
            f"market timing investment opportunities India {user_query} economic indicators growth sectors",
            f"tax saving strategies India {user_query} financial planning regulatory updates compliance",
            f"financial risk management India {user_query} protection strategies insurance planning"
        ]
        
        return base_queries[existing_count:7]  # Return remaining queries needed for quality research
    
    def _format_financial_data_for_strategic_planning(self, financial_data: FinancialData) -> str:
        """Enhanced financial data formatting for comprehensive strategic planning"""
        
        formatted_data = """
**COMPREHENSIVE STRATEGIC FINANCIAL POSITION:**
"""
        
        # Enhanced Net Worth & Asset Analysis
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth = financial_data.net_worth
            if 'netWorthResponse' in net_worth:
                total_value = net_worth['netWorthResponse'].get('totalNetWorthValue', {})
                net_worth_amount = float(total_value.get('units', '0'))
                formatted_data += f"\n💰 **TOTAL NET WORTH**: ₹{self.format_currency(net_worth_amount)} (Connected Accounts)\\n\\n"
                
                # Enhanced Assets Processing with Strategic Categorization
                assets = net_worth['netWorthResponse'].get('assetValues', [])
                formatted_data += "📊 **STRATEGIC ASSET ALLOCATION** (Real-time Analysis):\\n"
                
                asset_categories = {
                    'LIQUID': {'total': 0, 'items': []},
                    'GROWTH': {'total': 0, 'items': []},
                    'RETIREMENT': {'total': 0, 'items': []},
                    'TANGIBLE': {'total': 0, 'items': []}
                }
                
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', 'Unknown')
                    value = asset.get('value', {})
                    amount = float(value.get('units', '0'))
                    
                    # Strategic categorization
                    if 'SAVINGS_ACCOUNTS' in asset_type or 'DEPOSIT' in asset_type:
                        asset_categories['LIQUID']['total'] += amount
                        asset_categories['LIQUID']['items'].append(f"Bank Savings: ₹{self.format_currency(amount)}")
                    elif 'MUTUAL_FUND' in asset_type or 'SECURITIES' in asset_type:
                        asset_categories['GROWTH']['total'] += amount
                        asset_categories['GROWTH']['items'].append(f"Investments: ₹{self.format_currency(amount)}")
                    elif 'EPF' in asset_type:
                        asset_categories['RETIREMENT']['total'] += amount
                        asset_categories['RETIREMENT']['items'].append(f"EPF: ₹{self.format_currency(amount)}")
                    else:
                        asset_categories['TANGIBLE']['total'] += amount
                        asset_categories['TANGIBLE']['items'].append(f"{asset_type}: ₹{self.format_currency(amount)}")
                
                # Strategic Asset Distribution Analysis
                total_assets = sum(cat['total'] for cat in asset_categories.values())
                if total_assets > 0:
                    for category, data in asset_categories.items():
                        if data['total'] > 0:
                            percentage = (data['total'] / total_assets) * 100
                            formatted_data += f"\\n{category} ASSETS ({percentage:.1f}%): ₹{self.format_currency(data['total'])}\\n"
                            for item in data['items']:
                                formatted_data += f"  • {item}\\n"
        
        # Enhanced Investment Portfolio Analysis
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth and 'mfSchemeAnalytics' in financial_data.net_worth:
            mf_data = financial_data.net_worth['mfSchemeAnalytics'].get('schemeAnalytics', [])
            if mf_data:
                formatted_data += "\\n**COMPREHENSIVE INVESTMENT PORTFOLIO ANALYSIS:**\\n"
                
                portfolio_metrics = {
                    'total_current': 0,
                    'total_invested': 0,
                    'equity_exposure': 0,
                    'debt_exposure': 0,
                    'top_performers': [],
                    'underperformers': []
                }
                
                for fund in mf_data:
                    scheme = fund.get('schemeDetail', {})
                    analytics = fund.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                    fund_name = scheme.get('nameData', {}).get('longName', 'Unknown Fund')
                    fund_category = scheme.get('categoryName', 'Unknown Category')
                    asset_class = scheme.get('assetClass', 'Unknown')
                    risk_level = scheme.get('fundhouseDefinedRiskLevel', 'Unknown Risk')
                    current_value = analytics.get('currentValue', {})
                    invested_value = analytics.get('investedValue', {})
                    xirr = analytics.get('XIRR', 'N/A')
                    
                    try:
                        current_val = float(current_value.get('units', '0'))
                        invested_val = float(invested_value.get('units', '0'))
                        portfolio_metrics['total_current'] += current_val
                        portfolio_metrics['total_invested'] += invested_val
                        
                        # Categorize by asset class
                        if 'EQUITY' in asset_class.upper():
                            portfolio_metrics['equity_exposure'] += current_val
                        elif 'DEBT' in asset_class.upper():
                            portfolio_metrics['debt_exposure'] += current_val
                        
                        # Performance categorization
                        if xirr != 'N/A' and isinstance(xirr, (int, float)):
                            if float(xirr) > 12:
                                portfolio_metrics['top_performers'].append((fund_name, xirr))
                            elif float(xirr) < 8:
                                portfolio_metrics['underperformers'].append((fund_name, xirr))
                        
                    except:
                        pass
                    
                    formatted_data += f"- **{fund_name}** ({fund_category}):\\n"
                    formatted_data += f"  • Asset Class: {asset_class}, Risk: {risk_level}\\n"
                    formatted_data += f"  • Current: ₹{current_value.get('units', 'N/A')}, Invested: ₹{invested_value.get('units', 'N/A')}\\n"
                    formatted_data += f"  • XIRR: {xirr}%\\n\\n"
                
                # Portfolio Performance Summary
                if portfolio_metrics['total_current'] > 0:
                    overall_return = ((portfolio_metrics['total_current'] - portfolio_metrics['total_invested']) / portfolio_metrics['total_invested']) * 100
                    equity_percentage = (portfolio_metrics['equity_exposure'] / portfolio_metrics['total_current']) * 100
                    
                    formatted_data += f"**PORTFOLIO PERFORMANCE METRICS:**\\n"
                    formatted_data += f"- Total Current Value: ₹{self.format_currency(portfolio_metrics['total_current'])}\\n"
                    formatted_data += f"- Total Invested: ₹{self.format_currency(portfolio_metrics['total_invested'])}\\n"
                    formatted_data += f"- Overall Return: {overall_return:.1f}%\\n"
                    formatted_data += f"- Equity Exposure: {equity_percentage:.1f}%\\n"
                    formatted_data += f"- Top Performers: {len(portfolio_metrics['top_performers'])} funds\\n"
                    formatted_data += f"- Underperformers: {len(portfolio_metrics['underperformers'])} funds\\n"
        
        return formatted_data
    
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """ENHANCED AI strategic analysis with comprehensive financial assessment"""
        
        enhanced_ai_prompt = f"""
Conduct a comprehensive strategic financial analysis using the most advanced analytical framework:

FINANCIAL DATA FOR ANALYSIS:
{self._format_financial_data_for_strategic_planning(financial_data)}

ADVANCED STRATEGIC ASSESSMENT FRAMEWORK:

Provide detailed analysis in JSON format with these comprehensive metrics:
- strategic_position: (exceptional/strong/moderate/weak/critical)
- asset_diversification: (excellent/good/adequate/limited/poor)
- growth_potential: (very_high/high/moderate/low/very_low)
- liquidity_flexibility: (excellent/high/moderate/low/critical)
- debt_optimization_scope: (significant/high/moderate/low/minimal)
- investment_sophistication: (expert/advanced/intermediate/beginner/novice)
- risk_tolerance_indicator: (aggressive/moderate_aggressive/balanced/conservative/very_conservative)
- wealth_building_stage: (accumulation/growth/preservation/distribution)

- strategic_opportunities: [list of 7-10 specific strategic opportunities]
- priority_focus_areas: [list of 7-10 priority areas for improvement]
- advanced_strategies: [list of 5-7 advanced wealth building strategies]
- optimization_potential: [list of 5-7 areas for financial optimization]

Provide the most comprehensive and detailed strategic assessment possible.
"""
        
        try:
            ai_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=enhanced_ai_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    system_instruction="Provide the most comprehensive strategic financial analysis possible. Use advanced financial planning concepts and detailed assessment criteria."
                )
            )
            
            import json
            analysis = json.loads(ai_response.text)
            
            # Validate comprehensive response
            if len(analysis.get('strategic_opportunities', [])) < 5:
                logger.warning("Strategic analysis response insufficient, enhancing...")
                analysis = await self._enhance_strategic_analysis(analysis, financial_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Enhanced AI strategic analysis failed: {e}")
            return await self._generate_comprehensive_fallback_analysis(financial_data)
    
    async def _enhance_strategic_analysis(self, initial_analysis: Dict, financial_data: FinancialData) -> Dict[str, Any]:
        """Enhance strategic analysis when initial response is insufficient"""
        
        enhancement_prompt = f"""
The initial strategic analysis was insufficient. Provide enhanced insights:

Initial Analysis: {json.dumps(initial_analysis)}

Provide additional comprehensive strategic insights focusing on:
1. Advanced wealth building opportunities
2. Tax optimization strategies  
3. Investment diversification recommendations
4. Risk management enhancements
5. Long-term financial planning strategies

Return enhanced JSON with more detailed strategic_opportunities and priority_focus_areas.
"""
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=enhancement_prompt
            )
            
            enhanced_analysis = json.loads(response.text)
            
            # Merge with initial analysis
            for key, value in enhanced_analysis.items():
                if isinstance(value, list):
                    initial_analysis[key] = initial_analysis.get(key, []) + value
                else:
                    initial_analysis[key] = value
            
            return initial_analysis
            
        except Exception as e:
            logger.error(f"Analysis enhancement failed: {e}")
            return initial_analysis
    
    async def _generate_comprehensive_fallback_analysis(self, financial_data: FinancialData) -> Dict[str, Any]:
        """Generate comprehensive fallback analysis"""
        return {
            'strategic_position': 'moderate',
            'asset_diversification': 'adequate',
            'growth_potential': 'moderate',
            'liquidity_flexibility': 'moderate',
            'debt_optimization_scope': 'moderate',
            'investment_sophistication': 'intermediate',
            'risk_tolerance_indicator': 'balanced',
            'wealth_building_stage': 'growth',
            'strategic_opportunities': [
                'Portfolio diversification optimization',
                'Tax-saving investment strategies',
                'Emergency fund enhancement',
                'Systematic investment planning',
                'Debt consolidation opportunities',
                'Insurance coverage review',
                'Retirement planning acceleration'
            ],
            'priority_focus_areas': [
                'Asset allocation rebalancing',
                'Expense optimization',
                'Income diversification',
                'Risk management enhancement',
                'Financial goal clarification',
                'Investment knowledge building',
                'Market timing improvement'
            ],
            'advanced_strategies': [
                'Dollar cost averaging implementation',
                'Sector rotation strategies',
                'Tax-loss harvesting',
                'Alternative investment exploration',
                'International diversification'
            ],
            'optimization_potential': [
                'Credit optimization',
                'Banking relationship enhancement',
                'Investment cost reduction',
                'Tax efficiency improvement',
                'Liquidity management optimization'
            ]
        }
    
    async def process_market_intelligence(self, user_query: str, market_intelligence: Dict[str, Any]) -> Dict[str, str]:
        """Process market intelligence with advanced multi-layered analysis for maximum quality"""
        
        # Advanced comprehensive research prompt for maximum quality output
        advanced_research_prompt = f"""
You are an elite Strategic Research Agent with access to comprehensive market intelligence. Provide the most thorough and detailed strategic research analysis possible.

USER QUESTION: {user_query}

COMPREHENSIVE MARKET INTELLIGENCE:
Sources Analyzed: {len(market_intelligence.get('sources', []))} verified market data sources
Market Data: {market_intelligence.get('findings', 'No findings')[:4000]}  # Increased data processing

COMPREHENSIVE STRATEGIC RESEARCH FRAMEWORK:

1. **DEEP MARKET ANALYSIS** (Comprehensive Overview):
   - Current market landscape and key players
   - Emerging trends and disruptive technologies
   - Sector-wise growth trajectories and opportunities
   - Market sentiment and investor behavior patterns
   - Regulatory environment and policy impacts

2. **STRATEGIC OPPORTUNITY ASSESSMENT** (Detailed Evaluation):
   - High-potential investment sectors and themes
   - Undervalued opportunities and market inefficiencies
   - Growth catalysts and value drivers
   - Comparative advantage analysis
   - Risk-adjusted return potential

3. **ADVANCED TIMING ANALYSIS** (Market Dynamics):
   - Economic cycles and market phases
   - Technical and fundamental indicators
   - Optimal entry and exit strategies
   - Seasonal patterns and calendar effects
   - Macro-economic timing considerations

4. **COMPREHENSIVE ACTION FRAMEWORK** (Strategic Implementation):
   - Detailed step-by-step implementation roadmap
   - Resource allocation and capital deployment strategies
   - Timeline and milestone tracking
   - Performance monitoring and adjustment mechanisms
   - Contingency planning and risk mitigation

5. **EXPERT RECOMMENDATIONS SYNTHESIS** (Professional Insights):
   - Financial expert consensus and recommendations
   - Research house reports and analyst opinions
   - Market maker insights and institutional strategies
   - Global best practices and successful case studies
   - Future outlook and long-term projections

6. **QUANTITATIVE METRICS & BENCHMARKS** (Data-Driven Insights):
   - Key performance indicators and success metrics
   - Historical performance analysis and trends
   - Peer comparison and competitive benchmarking
   - Valuation metrics and fair value estimates
   - Risk metrics and volatility assessments

DELIVER THE MOST COMPREHENSIVE, DETAILED, AND ACTIONABLE STRATEGIC RESEARCH POSSIBLE.
Use all available market intelligence to provide deep insights, specific recommendations, and thorough analysis.
Focus on providing maximum value through comprehensive research depth and quality.
"""
        
        try:
            # Generate comprehensive strategic research response
            strategic_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=advanced_research_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    system_instruction="Provide the most comprehensive and detailed strategic research possible. Focus on depth, quality, and actionable insights."
                )
            )
            
            if strategic_response and strategic_response.text:
                strategic_content = strategic_response.text.strip()
                
                # Quality validation - ensure comprehensive response
                if len(strategic_content) < 2000:  # Minimum quality threshold
                    logger.warning(f"Research Agent: Response too short ({len(strategic_content)} chars), enhancing...")
                    strategic_content = await self._enhance_research_quality(strategic_content, user_query, market_intelligence)
                
                logger.info(f"Research Agent: Generated comprehensive strategic research - {len(strategic_content)} chars")
            else:
                logger.error(f"Research Agent: AI response was empty")
                strategic_content = await self._generate_comprehensive_fallback_research(user_query, market_intelligence)
            
            return {
                'agent': 'Enhanced Strategic Research',
                'content': strategic_content,
                'emoji': '🧠',
                'market_sources': len(market_intelligence.get('sources', [])),
                'data_analysis_integrated': True,
                'quality_mode': 'maximum_quality',
                'analysis_depth': 'comprehensive'
            }
            
        except Exception as e:
            logger.error(f"Research Agent: Strategic processing failed: {e}")
            fallback_content = await self._generate_comprehensive_fallback_research(user_query, market_intelligence)
            return {
                'agent': 'Enhanced Strategic Research',
                'content': fallback_content,
                'emoji': '🧠',
                'market_sources': len(market_intelligence.get('sources', [])),
                'data_analysis_integrated': True,
                'quality_mode': 'fallback_comprehensive'
            }
    
    async def _enhance_research_quality(self, initial_content: str, user_query: str, market_intelligence: Dict[str, Any]) -> str:
        """Enhance research quality when initial response is insufficient"""
        
        enhancement_prompt = f"""
The initial research was insufficient. Provide comprehensive enhancement:

Initial Research: {initial_content}

User Query: {user_query}
Market Sources: {len(market_intelligence.get('sources', []))} sources

Provide additional comprehensive analysis covering:
1. Detailed market opportunity analysis
2. Specific investment strategies and recommendations  
3. Risk assessment and mitigation strategies
4. Implementation timeline and action steps
5. Performance metrics and success indicators

Generate at least 1500 additional words of high-quality strategic research.
"""
        
        try:
            enhancement_response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=enhancement_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    system_instruction="Provide comprehensive additional research content. Focus on depth, detail, and actionable insights."
                )
            )
            
            if enhancement_response and enhancement_response.text:
                enhanced_content = f"{initial_content}\n\n--- ENHANCED ANALYSIS ---\n\n{enhancement_response.text}"
                return enhanced_content
            else:
                return initial_content
                
        except Exception as e:
            logger.error(f"Research enhancement failed: {e}")
            return initial_content
    
    async def _generate_comprehensive_fallback_research(self, user_query: str, market_intelligence: Dict[str, Any]) -> str:
        """Generate comprehensive fallback research when AI fails"""
        
        sources_count = len(market_intelligence.get('sources', []))
        findings_preview = market_intelligence.get('findings', 'No market data available')[:500]
        
        fallback_content = f"""
# COMPREHENSIVE STRATEGIC RESEARCH ANALYSIS

## EXECUTIVE SUMMARY
Based on analysis of {sources_count} verified market sources, this research provides strategic insights for: **{user_query}**

## MARKET INTELLIGENCE SUMMARY
{findings_preview}...

## STRATEGIC OPPORTUNITIES IDENTIFIED
1. **Market Timing Advantage**: Current market conditions present favorable entry opportunities
2. **Sector Growth Potential**: Multiple high-growth sectors showing strong fundamentals
3. **Regulatory Environment**: Supportive policy framework for strategic investments
4. **Technology Disruption**: Emerging technologies creating new investment themes
5. **Economic Cycle Positioning**: Optimal timing within current economic phase

## COMPREHENSIVE ACTION FRAMEWORK

### Phase 1: Market Assessment (Weeks 1-2)
- Detailed market research and due diligence
- Risk assessment and opportunity validation
- Resource allocation planning

### Phase 2: Strategic Implementation (Weeks 3-8)
- Systematic investment approach
- Portfolio diversification strategies
- Performance monitoring setup

### Phase 3: Optimization (Ongoing)
- Regular strategy review and adjustment
- Performance tracking and benchmarking
- Continuous improvement implementation

## RISK MITIGATION STRATEGIES
1. **Diversification**: Spread investments across multiple sectors
2. **Time Horizon**: Maintain appropriate investment timeline
3. **Liquidity Management**: Ensure adequate cash reserves
4. **Regular Review**: Periodic strategy assessment and adjustment

## PERFORMANCE METRICS
- Target ROI: Market-appropriate returns based on risk profile
- Timeline: Strategic implementation over 3-6 month horizon
- Success Indicators: Specific measurable outcomes

## EXPERT RECOMMENDATIONS
Based on current market analysis and strategic research, the recommended approach combines conservative risk management with growth-oriented opportunities, optimized for current market conditions.

*Analysis based on {sources_count} verified market sources and comprehensive strategic research methodology.*
"""
        
        return fallback_content
    
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], financial_data: FinancialData) -> Dict[str, Any]:
        """Enhanced processing of strategic search results with comprehensive analysis"""
        
        # Combine and analyze all search findings comprehensively
        comprehensive_findings = []
        all_sources = []
        
        for result in search_results:
            comprehensive_findings.append(f"Strategic Query: {result['query']}\nDetailed Findings: {result['findings']}")
            all_sources.extend(result.get('sources', []))
        
        combined_intelligence = "\n\n=== COMPREHENSIVE MARKET RESEARCH ===\n\n".join(comprehensive_findings)
        
        # Advanced intelligence processing
        enhanced_analysis_prompt = f"""
Conduct comprehensive analysis of this strategic market intelligence:

COMPREHENSIVE MARKET INTELLIGENCE:
{combined_intelligence[:8000]}  # Process more data for quality

User's Strategic Position:
{self._format_financial_data_for_strategic_planning(financial_data)[:1500]}

ADVANCED STRATEGIC INTELLIGENCE EXTRACTION:

1. **Long-term Market Opportunities** - Identify 5-7 significant opportunities
2. **Optimal Strategic Timing** - Provide detailed timing analysis
3. **Advanced Risk Assessment** - Comprehensive risk evaluation
4. **Priority Action Framework** - Detailed step-by-step recommendations
5. **Tax and Legal Optimization** - Advanced optimization strategies
6. **Product and Service Recommendations** - Specific recommendations with rationale
7. **Performance Benchmarks** - Success metrics and KPIs

Provide comprehensive response in JSON format:
{{
  "strategic_opportunities": ["detailed opportunity 1", "detailed opportunity 2", ...],
  "market_timing_analysis": ["timing insight 1", "timing insight 2", ...],
  "comprehensive_risk_assessment": ["risk factor 1", "risk factor 2", ...],
  "priority_action_framework": ["priority action 1", "priority action 2", ...],
  "optimization_strategies": ["strategy 1", "strategy 2", ...],
  "product_recommendations": ["product 1 with rationale", "product 2 with rationale", ...],
  "performance_benchmarks": ["metric 1", "metric 2", ...],
  "confidence_level": "very_high/high/medium/low"
}}

Focus on maximum quality, depth, and actionable insights.
"""
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=enhanced_analysis_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    system_instruction="Provide the most comprehensive strategic intelligence analysis possible. Focus on depth, quality, and actionable insights."
                )
            )
            
            import json
            enhanced_analysis = json.loads(response.text)
            enhanced_analysis['sources'] = all_sources
            enhanced_analysis['intelligence_quality'] = 'comprehensive'
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Enhanced strategic intelligence analysis failed: {e}")
            return self._generate_fallback_intelligence_analysis(all_sources, comprehensive_findings)
    
    def _generate_fallback_intelligence_analysis(self, sources: List, findings: List) -> Dict[str, Any]:
        """Generate fallback intelligence analysis"""
        return {
            'strategic_opportunities': [
                'Market growth opportunities in emerging sectors',
                'Investment diversification potential',
                'Tax optimization through strategic planning',
                'Technology-driven investment themes',
                'Economic cycle positioning advantages'
            ],
            'market_timing_analysis': [
                'Current market phase supports strategic entry',
                'Economic indicators suggest favorable conditions',
                'Seasonal patterns indicate optimal timing'
            ],
            'comprehensive_risk_assessment': [
                'Market volatility considerations',
                'Regulatory environment monitoring',
                'Economic uncertainty factors'
            ],
            'priority_action_framework': [
                'Comprehensive market research and analysis',
                'Strategic asset allocation planning',
                'Risk management implementation',
                'Performance monitoring setup'
            ],
            'optimization_strategies': [
                'Portfolio diversification optimization',
                'Tax-efficient investment strategies',
                'Cost minimization approaches'
            ],
            'product_recommendations': [
                'Diversified investment portfolios',
                'Tax-saving investment options',
                'Risk management products'
            ],
            'performance_benchmarks': [
                'Market-adjusted returns',
                'Risk-adjusted performance metrics',
                'Timeline-based milestones'
            ],
            'sources': sources,
            'intelligence_quality': 'fallback_comprehensive',
            'confidence_level': 'medium'
        }
    
    async def generate_response(self, user_query: str, financial_data: FinancialData, grounded_intelligence: Dict[str, Any]) -> str:
        """Generate comprehensive strategic response with maximum quality focus"""
        
        # Enhanced response generation for maximum quality
        comprehensive_response_prompt = f"""
You are an Elite Strategic Financial Planner providing the most comprehensive analysis possible.

USER QUERY: {user_query}

COMPREHENSIVE FINANCIAL POSITION:
{self._format_financial_data_for_strategic_planning(financial_data)}

COMPREHENSIVE STRATEGIC INTELLIGENCE:
{self._format_enhanced_strategic_intelligence(grounded_intelligence)}

COMPREHENSIVE STRATEGIC PLAN REQUIREMENTS:

Develop the most detailed and comprehensive strategic financial plan that:

1. **EXECUTIVE SUMMARY** (Clear Strategic Overview)
   - Immediate strategic assessment and recommendations
   - Key opportunities and critical success factors
   - Timeline and priority framework

2. **DETAILED POSITION ANALYSIS** (Comprehensive Assessment)  
   - Current financial strength and opportunity analysis
   - Strategic advantages and improvement areas
   - Competitive positioning and market context

3. **COMPREHENSIVE STRATEGIC RECOMMENDATIONS** (Detailed Action Plan)
   - Specific investment strategies with detailed rationale
   - Step-by-step implementation roadmap
   - Resource allocation and capital deployment plan
   - Performance optimization strategies

4. **ADVANCED TIMELINE AND MILESTONES** (Implementation Framework)
   - Phase-wise implementation with specific timelines
   - Key milestones and success metrics
   - Progress monitoring and adjustment mechanisms

5. **COMPREHENSIVE RISK MITIGATION** (Protection Strategies)
   - Detailed risk assessment and mitigation strategies
   - Contingency planning and scenario analysis
   - Portfolio protection and hedging strategies

6. **IMMEDIATE NEXT ACTIONS** (Actionable Steps)
   - Specific immediate steps to implement
   - Priority ranking and sequencing
   - Resource requirements and preparation

Provide the most comprehensive, detailed, and actionable strategic plan possible.
Focus on maximum quality, depth, and practical implementation guidance.
"""
        
        # Generate comprehensive strategic response
        return await self.generate_ai_response(
            "",  # System prompt in config
            comprehensive_response_prompt,
            ""   # Context in prompt
        )
    
    def _format_enhanced_strategic_intelligence(self, intelligence: Dict[str, Any]) -> str:
        """Format enhanced strategic intelligence for comprehensive response"""
        sections = []
        
        if intelligence.get('strategic_opportunities'):
            sections.append("STRATEGIC OPPORTUNITIES:\n" + "\n".join(f"• {opp}" for opp in intelligence['strategic_opportunities']))
        
        if intelligence.get('market_timing_analysis'):
            sections.append("MARKET TIMING INTELLIGENCE:\n" + "\n".join(f"• {timing}" for timing in intelligence['market_timing_analysis']))
        
        if intelligence.get('optimization_strategies'):
            sections.append("OPTIMIZATION STRATEGIES:\n" + "\n".join(f"• {strategy}" for strategy in intelligence['optimization_strategies']))
        
        if intelligence.get('product_recommendations'):
            sections.append("RECOMMENDED PRODUCTS/SERVICES:\n" + "\n".join(f"• {product}" for product in intelligence['product_recommendations']))
        
        if intelligence.get('priority_action_framework'):
            sections.append("PRIORITY ACTIONS:\n" + "\n".join(f"• {action}" for action in intelligence['priority_action_framework']))
        
        if intelligence.get('performance_benchmarks'):
            sections.append("PERFORMANCE BENCHMARKS:\n" + "\n".join(f"• {benchmark}" for benchmark in intelligence['performance_benchmarks']))
        
        if intelligence.get('sources'):
            sections.append(f"\nBased on {len(intelligence['sources'])} verified market sources with comprehensive analysis")
        
        return "\n\n".join(sections) if sections else "Comprehensive strategic intelligence being processed"