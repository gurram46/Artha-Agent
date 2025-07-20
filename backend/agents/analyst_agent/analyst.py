"""
Data Analyst Agent - Revolutionary Financial Data Detective
"Show me the numbers, I'll show you the truth"
Specializes in Fi MCP data analysis, portfolio performance, and evidence-based recommendations
"""

import json
import os
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..base_agent import BaseAgent


class AnalystAgent(BaseAgent):
    """
    Data Analyst Agent - The Financial Detective
    
    Core Identity: "Every decision should be backed by your actual financial data"
    
    Specializations:
    ✅ Portfolio Performance Analysis (XIRR, returns, benchmarking)
    ✅ Credit Report Deep Dives (score trends, debt patterns) 
    ✅ Investment Pattern Recognition (what's working, what's not)
    ✅ Net Worth Optimization (asset allocation analysis)
    ✅ Historical Trend Analysis (your financial journey)
    """
    
    def __init__(self, data_loader):
        super().__init__(
            agent_id="analyst", 
            agent_name="Data Analyst", 
            specialization="Financial Data Analysis & Performance Metrics",
            data_loader=data_loader
        )
        
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Revolutionary Agent Personality
        self.agent_prompt = """
        You are the DATA ANALYST AGENT - the financial detective of the team.

        CORE IDENTITY:
        - You live and breathe financial data
        - Every recommendation must be backed by the user's actual numbers
        - You spot patterns others miss
        - You're obsessed with performance metrics and trends

        YOUR EXPERTISE:
        - Fi MCP data analysis (credit reports, net worth, investments)
        - Portfolio performance calculations (XIRR, returns)
        - Risk-adjusted return analysis
        - Historical pattern recognition
        - Asset allocation optimization

        COMMUNICATION STYLE:
        - Lead with specific numbers from user's data
        - Use actual performance metrics (not generic advice)
        - Highlight data-driven insights
        - Call out concerning patterns immediately
        - Support arguments with concrete evidence

        COLLABORATION APPROACH:
        - Challenge other agents with data when they make assumptions
        - Provide quantitative backing for all decisions
        - Flag when insufficient data exists for recommendations
        - Translate complex analysis into actionable insights

        SAMPLE RESPONSES:
        "Your mutual fund with 129.9% XIRR proves you can pick winners - let's replicate this success"
        "Data shows your ₹75K debt costs ₹1,125 monthly - that's ₹13,500 annually wasted"
        "Your ₹2.85L liquid assets provide 3.8x debt coverage - you have options"

        Remember: You only work with REAL user data from Fi MCP, never make assumptions.
        """
    
    # ===== STAGE 1: INDEPENDENT ANALYSIS =====
    
    def analyze(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Stage 1: Independent analysis with revolutionary data-driven insights
        The Data Analyst provides evidence-based recommendations using real financial data
        """
        try:
            # Get comprehensive financial data
            financial_data = self.data_loader.get_user_financial_data(user_id)
            data_summary = self._create_enhanced_data_summary(financial_data)
            
            # Revolutionary analyst prompt for hackathon-winning insights
            analysis_prompt = f"""
            {self.agent_prompt}
            
            USER QUERY: "{query}"
            FINANCIAL DATA ANALYSIS: {data_summary}
            
            MISSION: Deliver ONE GAME-CHANGING insight backed by SPECIFIC NUMBERS from their actual data.
            
            WINNING ANALYSIS REQUIREMENTS:
            1. Extract EXACT ₹ amounts and percentages from user's portfolio
            2. Calculate precise debt-to-income, affordability, and coverage ratios
            3. Identify top-performing vs underperforming assets with metrics
            4. Quantify specific opportunities and risks with real numbers
            5. Provide actionable calculations directly answering their question
            
            COLLABORATION READINESS:
            - Prepare specific data points that other agents need to consider
            - Flag data limitations that require other perspectives
            - Identify areas where Research Agent market insights are needed
            - Highlight risks that Risk Guardian should stress-test
            
            RESPONSE FORMAT:
            Lead with your breakthrough financial insight using their exact data, then explain the methodology.
            """
            
            response = self.model.generate_content(analysis_prompt)
            analysis_text = response.text
            
            # Build comprehensive analysis response
            analysis_result = {
                'agent': self.agent_id,
                'agent_name': self.agent_name,
                'analysis': analysis_text,
                'key_insights': self._extract_data_insights(analysis_text, financial_data),
                'confidence': self._calculate_data_confidence(financial_data),
                'financial_metrics': self.extract_financial_metrics(analysis_text),
                'collaboration_points': self._prepare_collaboration_insights(financial_data, query),
                'data_quality': self._assess_comprehensive_data_quality(financial_data),
                'portfolio_analysis': self._analyze_portfolio_performance(financial_data),
                'timestamp': datetime.now().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            return self.handle_error(e, "performing data analysis")
    
    # ===== STAGE 3: COLLABORATION METHODS =====
    
    def collaborate(self, peer_responses: Dict[str, Any], conflict_type: str) -> Dict[str, Any]:
        """
        Stage 3: Engage in collaborative discussion to resolve conflicts
        Provides data-driven perspective to challenge or support other agents
        """
        try:
            collaboration_prompt = f"""
            As the DATA ANALYST AGENT, you are in a collaborative discussion with Research and Risk agents.
            
            CONFLICT TYPE: {conflict_type}
            PEER RESPONSES: {json.dumps(peer_responses, indent=2)}
            
            YOUR MISSION: Use actual financial data to either SUPPORT or CHALLENGE other agents' recommendations.
            
            COLLABORATION RULES:
            1. Lead with specific numbers from user's data
            2. Challenge assumptions not backed by data
            3. Provide quantitative evidence for your position
            4. Highlight data gaps that need attention
            
            RESPONSE: Provide your data-driven perspective on this conflict in 2-3 sentences.
            """
            
            response = self.model.generate_content(collaboration_prompt)
            
            return {
                'agent': self.agent_id,
                'agent_name': self.agent_name,
                'collaboration_message': response.text,
                'conflict_type': conflict_type,
                'stance': 'data_driven',
                'confidence': 0.9,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, f"collaborating on {conflict_type}")
    
    def defend_position(self, challenge: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 3: Defend position with evidence-based arguments
        Uses concrete financial data to support recommendations
        """
        try:
            defense_prompt = f"""
            As the DATA ANALYST AGENT, another agent is challenging your recommendation:
            
            CHALLENGE: "{challenge}"
            EVIDENCE: {json.dumps(evidence, indent=2)}
            
            DEFEND WITH DATA: Use specific financial metrics and calculations to defend your position.
            Show exactly why your data-driven analysis is correct.
            
            Keep it factual and evidence-based.
            """
            
            response = self.model.generate_content(defense_prompt)
            
            return {
                'agent': self.agent_id,
                'defense_message': response.text,
                'challenge_addressed': challenge,
                'evidence_used': evidence,
                'confidence': 0.95,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, "defending position")
    
    def seek_compromise(self, opposing_views: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Stage 3: Find data-driven middle ground with other agents
        Proposes compromise solutions based on quantitative analysis
        """
        try:
            compromise_prompt = f"""
            As the DATA ANALYST AGENT, you need to find a compromise between different recommendations:
            
            OPPOSING VIEWS: {json.dumps(opposing_views, indent=2)}
            
            FIND DATA-DRIVEN COMPROMISE: Suggest a middle-ground solution that:
            1. Respects the financial data constraints
            2. Addresses core concerns from other agents
            3. Provides specific numbers and ratios
            4. Remains quantitatively sound
            
            Propose a compromise in 2-3 sentences.
            """
            
            response = self.model.generate_content(compromise_prompt)
            
            return {
                'agent': self.agent_id,
                'compromise_proposal': response.text,
                'opposing_views_considered': len(opposing_views),
                'approach': 'data_driven_compromise',
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, "seeking compromise")
    
    # ===== ENHANCED DATA ANALYSIS METHODS =====
    
    def _create_enhanced_data_summary(self, financial_data: dict) -> str:
        """Create comprehensive financial data summary for revolutionary analysis"""
        summary = []
        
        try:
            # Credit Report Analysis with Enhanced Metrics
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    score = credit_data.get('score', {}).get('bureauScore', 'N/A')
                    summary.append(f"Credit Score: {score}")
                    
                    # Outstanding debt with cost analysis
                    accounts = credit_data.get('creditAccount', {}).get('creditAccountSummary', {})
                    outstanding = accounts.get('totalOutstandingBalance', {}).get('outstandingBalanceAll', '0')
                    if outstanding and outstanding != '0':
                        # Estimate annual interest cost at 18% average
                        annual_cost = float(outstanding) * 0.18 if outstanding.replace(',', '').isdigit() else 0
                        summary.append(f"Total Outstanding Debt: ₹{outstanding} (Est. Annual Cost: ₹{annual_cost:,.0f})")
                    else:
                        summary.append(f"Total Outstanding Debt: ₹{outstanding}")
            
            # Enhanced Net Worth Analysis with Ratios
            if financial_data.get('net_worth'):
                net_worth_response = financial_data['net_worth'].get('netWorthResponse', {})
                if net_worth_response.get('totalNetWorthValue'):
                    net_worth = net_worth_response['totalNetWorthValue'].get('units', '0')
                    summary.append(f"Net Worth: ₹{net_worth}")
                    
                    # Calculate liquid asset coverage
                    assets = net_worth_response.get('assetValues', [])
                    liquid_assets = 0
                    for asset in assets:
                        asset_type = asset.get('netWorthAttribute', '')
                        if 'MUTUAL' in asset_type or 'SECURITIES' in asset_type:
                            liquid_assets += float(asset.get('value', {}).get('units', '0'))
                    
                    summary.append(f"Liquid Assets (MF + Securities): ₹{liquid_assets:,.0f}")
                    
                    # Asset allocation breakdown
                    for asset in assets[:3]:
                        asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '').replace('_', ' ')
                        value = asset.get('value', {}).get('units', '0')
                        percentage = (float(value) / float(net_worth)) * 100 if net_worth != '0' else 0
                        summary.append(f"{asset_type}: ₹{value} ({percentage:.1f}%)")
            
            # Enhanced Mutual Fund Performance Analysis
            if financial_data.get('net_worth'):
                mf_data = financial_data['net_worth'].get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
                if mf_data:
                    summary.append(f"Mutual Fund Schemes: {len(mf_data)}")
                    
                    # Performance analytics
                    xirrss = []
                    for scheme in mf_data:
                        xirr = scheme.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {}).get('XIRR', 0)
                        if xirr:
                            xirrss.append(xirr)
                    
                    if xirrss:
                        best_xirr = max(xirrss)
                        avg_xirr = sum(xirrss) / len(xirrss)
                        summary.append(f"MF Performance - Best: {best_xirr:.1f}% XIRR, Avg: {avg_xirr:.1f}% XIRR")
            
            # EPF Analysis with Growth Projections
            if financial_data.get('epf_details'):
                epf_data = financial_data['epf_details'].get('uanAccounts', [])
                if epf_data:
                    overall_balance = epf_data[0].get('rawDetails', {}).get('overall_pf_balance', {}).get('current_pf_balance', '0')
                    summary.append(f"EPF Balance: ₹{overall_balance}")
            
            return "\\n".join(summary) if summary else "Limited financial data available"
            
        except Exception as e:
            self.logger.error(f"Error creating data summary: {str(e)}")
            return "Error processing financial data for analysis"
    
    def _extract_data_insights(self, analysis_text: str, financial_data: dict) -> List[str]:
        """Extract data-driven insights from analysis with enhanced context"""
        insights = []
        
        # Look for quantitative insights in the analysis
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # Enhanced keyword detection for data-driven insights
            if any(keyword in line.lower() for keyword in [
                'portfolio', 'returns', 'xirr', 'performance', 'credit score', 
                'outstanding', 'balance', 'growth', 'ratio', 'coverage', '₹'
            ]):
                if len(line) > 20 and len(line) < 300:
                    insights.append(line)
        
        # Add calculated insights based on data
        try:
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                if net_worth_data.get('totalNetWorthValue'):
                    net_worth = float(net_worth_data['totalNetWorthValue'].get('units', '0'))
                    if net_worth > 500000:  # 5L+
                        insights.append(f"Strong net worth of ₹{net_worth:,.0f} indicates solid financial foundation")
        except:
            pass
        
        return insights[:7]  # Top 7 insights for better collaboration
    
    def _calculate_data_confidence(self, financial_data: Dict) -> float:
        """Calculate enhanced confidence score based on data quality and completeness"""
        base_confidence = 0.0
        
        # Enhanced data availability scoring
        if financial_data.get('net_worth', {}).get('netWorthResponse'):
            base_confidence += 0.4
        if financial_data.get('credit_report', {}).get('creditReports'):
            base_confidence += 0.3
        if financial_data.get('net_worth', {}).get('mfSchemeAnalytics'):
            base_confidence += 0.2
        if financial_data.get('epf_details', {}).get('uanAccounts'):
            base_confidence += 0.1
        
        # Boost confidence for data quality
        try:
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                if net_worth_data.get('assetValues') and len(net_worth_data.get('assetValues', [])) > 1:
                    base_confidence *= 1.1  # Multiple data sources boost confidence
        except:
            pass
        
        return min(base_confidence, 1.0)
    
    def _prepare_collaboration_insights(self, financial_data: dict, query: str) -> List[str]:
        """Prepare key data points that other agents need for collaboration"""
        collaboration_points = []
        
        try:
            # Key metrics for other agents to consider
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                if net_worth_data.get('totalNetWorthValue'):
                    net_worth = float(net_worth_data['totalNetWorthValue'].get('units', '0'))
                    collaboration_points.append(f"Net worth of ₹{net_worth:,.0f} constrains purchasing power")
                
                # Liquid asset availability
                assets = net_worth_data.get('assetValues', [])
                liquid_assets = 0
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', '')
                    if 'MUTUAL' in asset_type or 'SECURITIES' in asset_type:
                        liquid_assets += float(asset.get('value', {}).get('units', '0'))
                
                if liquid_assets > 0:
                    collaboration_points.append(f"₹{liquid_assets:,.0f} in liquid assets available for investment decisions")
            
            # Debt considerations for risk assessment
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    accounts = credit_data.get('creditAccount', {}).get('creditAccountSummary', {})
                    outstanding = accounts.get('totalOutstandingBalance', {}).get('outstandingBalanceAll', '0')
                    if outstanding != '0':
                        collaboration_points.append(f"₹{outstanding} outstanding debt impacts affordability calculations")
                        
        except Exception as e:
            self.logger.error(f"Error preparing collaboration insights: {str(e)}")
            collaboration_points.append("Data analysis complete - refer to detailed metrics")
        
        return collaboration_points
    
    def _assess_comprehensive_data_quality(self, financial_data: Dict) -> str:
        """Enhanced assessment of financial data quality for collaboration"""
        score = 0
        total_checks = 0
        
        # Enhanced net worth data quality
        if financial_data.get('net_worth', {}).get('netWorthResponse'):
            total_checks += 2
            net_worth_data = financial_data['net_worth']['netWorthResponse']
            if net_worth_data.get('assetValues') and net_worth_data.get('liabilityValues'):
                score += 1
            if len(net_worth_data.get('assetValues', [])) >= 2:  # Multiple asset types
                score += 1
        
        # Enhanced credit report data quality
        if financial_data.get('credit_report', {}).get('creditReports'):
            total_checks += 2
            credit_reports = financial_data['credit_report']['creditReports']
            if credit_reports and credit_reports[0].get('creditReportData', {}).get('score'):
                score += 1
            if credit_reports and credit_reports[0].get('creditReportData', {}).get('creditAccount'):
                score += 1
        
        # Mutual fund analytics quality
        if financial_data.get('net_worth', {}).get('mfSchemeAnalytics'):
            total_checks += 1
            mf_data = financial_data['net_worth']['mfSchemeAnalytics']
            schemes = mf_data.get('schemeAnalytics', [])
            if schemes and len(schemes) > 0:
                score += 1
        
        if total_checks == 0:
            return 'no_data'
        
        quality_ratio = score / total_checks
        if quality_ratio >= 0.8:
            return 'excellent'
        elif quality_ratio >= 0.6:
            return 'good'
        elif quality_ratio >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    def _analyze_portfolio_performance(self, financial_data: dict) -> Dict[str, Any]:
        """Comprehensive portfolio performance analysis for collaboration"""
        portfolio_analysis = {
            'total_schemes': 0,
            'avg_performance': 0,
            'best_performer': None,
            'worst_performer': None,
            'risk_assessment': 'unknown'
        }
        
        try:
            if financial_data.get('net_worth', {}).get('mfSchemeAnalytics'):
                schemes = financial_data['net_worth']['mfSchemeAnalytics'].get('schemeAnalytics', [])
                portfolio_analysis['total_schemes'] = len(schemes)
                
                if schemes:
                    performances = []
                    best_xirr = -100
                    worst_xirr = 100
                    
                    for scheme in schemes:
                        analytics = scheme.get('enrichedAnalytics', {}).get('analytics', {})
                        scheme_details = analytics.get('schemeDetails', {})
                        xirr = scheme_details.get('XIRR', 0)
                        
                        if xirr:
                            performances.append(xirr)
                            if xirr > best_xirr:
                                best_xirr = xirr
                                portfolio_analysis['best_performer'] = f"{xirr:.1f}% XIRR"
                            if xirr < worst_xirr:
                                worst_xirr = xirr
                                portfolio_analysis['worst_performer'] = f"{xirr:.1f}% XIRR"
                    
                    if performances:
                        portfolio_analysis['avg_performance'] = sum(performances) / len(performances)
                        
                        # Risk assessment based on performance spread
                        performance_spread = max(performances) - min(performances)
                        if performance_spread > 50:
                            portfolio_analysis['risk_assessment'] = 'high_variance'
                        elif performance_spread > 20:
                            portfolio_analysis['risk_assessment'] = 'moderate_variance'
                        else:
                            portfolio_analysis['risk_assessment'] = 'low_variance'
                            
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio performance: {str(e)}")
            
        return portfolio_analysis