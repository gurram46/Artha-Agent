"""
Research Strategist Agent - Revolutionary Market Intelligence Expert
"Let me find the best opportunities in today's market"
Specializes in market timing, investment strategies, and economic trend analysis
"""

import json
import os
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """
    Research Strategist Agent - The Market Intelligence Expert
    
    Core Identity: "The best strategy leverages current market conditions"
    
    Specializations:
    ✅ Market Opportunity Analysis (sector trends, timing)
    ✅ Investment Product Research (best funds, schemes, options)
    ✅ Strategic Financial Planning (goal-based investing)
    ✅ Economic Context Integration (interest rates, market cycles)
    ✅ Alternative Investment Exploration (REITs, bonds, etc.)
    """
    
    def __init__(self, data_loader):
        super().__init__(
            agent_id="research", 
            agent_name="Research Strategist", 
            specialization="Market Intelligence & Strategic Planning",
            data_loader=data_loader
        )
        
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Revolutionary Agent Personality
        self.agent_prompt = """
        You are the RESEARCH STRATEGIST AGENT - the market intelligence expert of the team.

        CORE IDENTITY:
        - You're plugged into current market trends and opportunities
        - You think strategically about timing and market conditions
        - You research the best financial products and strategies
        - You connect macro trends to personal financial decisions

        YOUR EXPERTISE:
        - Current market analysis and sector opportunities
        - Investment product research and recommendations
        - Strategic asset allocation based on market conditions
        - Economic trend analysis and impact on personal finance
        - Alternative investment opportunities

        COMMUNICATION STYLE:
        - Reference current market conditions and trends
        - Suggest specific investment products and strategies
        - Explain timing considerations for financial decisions
        - Connect macro economic factors to personal impact
        - Provide strategic context for recommendations

        COLLABORATION APPROACH:
        - Provide market context for data analyst's findings
        - Suggest strategic alternatives to risk manager's concerns
        - Research solutions that address other agents' requirements
        - Bring fresh perspectives on conventional wisdom

        SAMPLE RESPONSES:
        "Current interest rates favor debt consolidation - 8.5% car loans vs 18% credit card debt"
        "Market timing suggests equity SIPs over lump sum investments in current volatility"
        "Technology and healthcare sectors showing resilience - consider focused funds"

        Remember: Combine market intelligence with user's specific situation from other agents.
        """
    
    # ===== STAGE 1: INDEPENDENT ANALYSIS =====
    
    def analyze(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Stage 1: Independent market intelligence analysis
        The Research Strategist provides market-informed strategic recommendations
        """
        try:
            # Get financial context and market intelligence
            financial_data = self.data_loader.get_user_financial_data(user_id)
            market_context = self._get_enhanced_market_context()
            financial_summary = self._create_strategic_financial_summary(financial_data)
            
            # Revolutionary strategist prompt for hackathon-winning insights
            strategy_prompt = f"""
            {self.agent_prompt}
            
            USER QUERY: "{query}"
            FINANCIAL CONTEXT: {financial_summary}
            MARKET INTELLIGENCE: {market_context}
            
            MISSION: Deliver ONE GAME-CHANGING strategic insight with MARKET-INFORMED recommendations.
            
            WINNING STRATEGY REQUIREMENTS:
            1. Reference current market conditions and interest rates
            2. Suggest specific investment products with timing rationale
            3. Provide asset allocation strategies based on market cycles
            4. Connect economic trends to personal financial decisions
            5. Offer alternatives that leverage market opportunities
            
            COLLABORATION READINESS:
            - Prepare market context that other agents need to consider
            - Identify strategic alternatives to address risk concerns
            - Suggest timing considerations for data-driven decisions
            - Flag market opportunities that require risk assessment
            
            RESPONSE FORMAT:
            Lead with your breakthrough strategic insight based on current market conditions, then explain the methodology.
            """
            
            response = self.model.generate_content(strategy_prompt)
            analysis_text = response.text
            
            # Build comprehensive strategy response
            strategy_result = {
                'agent': self.agent_id,
                'agent_name': self.agent_name,
                'analysis': analysis_text,
                'key_insights': self._extract_strategic_insights(analysis_text),
                'confidence': self._calculate_market_confidence(financial_data),
                'financial_metrics': self.extract_financial_metrics(analysis_text),
                'collaboration_points': self._prepare_market_insights(query, market_context),
                'market_opportunities': self._identify_strategic_opportunities(financial_data),
                'strategic_recommendations': self._extract_actionable_recommendations(analysis_text),
                'timing_analysis': self._analyze_market_timing(query),
                'timestamp': datetime.now().isoformat()
            }
            
            return strategy_result
            
        except Exception as e:
            return self.handle_error(e, "performing strategic market analysis")
    
    # ===== STAGE 3: COLLABORATION METHODS =====
    
    def collaborate(self, peer_responses: Dict[str, Any], conflict_type: str) -> Dict[str, Any]:
        """
        Stage 3: Engage in collaborative discussion to resolve conflicts
        Provides market-informed strategic alternatives to resolve disagreements
        """
        try:
            collaboration_prompt = f"""
            As the RESEARCH STRATEGIST AGENT, you are in a collaborative discussion with Data Analyst and Risk agents.
            
            CONFLICT TYPE: {conflict_type}
            PEER RESPONSES: {json.dumps(peer_responses, indent=2)}
            
            YOUR MISSION: Use market intelligence to provide strategic alternatives that address the conflict.
            
            COLLABORATION RULES:
            1. Reference current market conditions and opportunities
            2. Suggest strategic alternatives that address concerns
            3. Provide timing and market context for decisions
            4. Bridge differences with market-informed compromises
            
            RESPONSE: Provide your strategic perspective on this conflict in 2-3 sentences.
            """
            
            response = self.model.generate_content(collaboration_prompt)
            
            return {
                'agent': self.agent_id,
                'agent_name': self.agent_name,
                'collaboration_message': response.text,
                'conflict_type': conflict_type,
                'stance': 'strategic_alternative',
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, f"collaborating on {conflict_type}")
    
    def defend_position(self, challenge: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 3: Defend position with market-informed arguments
        Uses market intelligence and strategic reasoning to support recommendations
        """
        try:
            defense_prompt = f"""
            As the RESEARCH STRATEGIST AGENT, another agent is challenging your recommendation:
            
            CHALLENGE: "{challenge}"
            EVIDENCE: {json.dumps(evidence, indent=2)}
            
            DEFEND WITH STRATEGY: Use market conditions, timing analysis, and strategic reasoning to defend your position.
            Show exactly why your market-informed strategy is optimal.
            
            Keep it strategic and market-focused.
            """
            
            response = self.model.generate_content(defense_prompt)
            
            return {
                'agent': self.agent_id,
                'defense_message': response.text,
                'challenge_addressed': challenge,
                'evidence_used': evidence,
                'confidence': 0.9,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, "defending strategic position")
    
    def seek_compromise(self, opposing_views: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Stage 3: Find strategic middle ground with other agents
        Proposes market-informed compromise solutions
        """
        try:
            compromise_prompt = f"""
            As the RESEARCH STRATEGIST AGENT, you need to find a strategic compromise between different recommendations:
            
            OPPOSING VIEWS: {json.dumps(opposing_views, indent=2)}
            
            FIND STRATEGIC COMPROMISE: Suggest a market-informed solution that:
            1. Leverages current market opportunities
            2. Addresses core concerns from other agents
            3. Provides optimal timing and strategic approach
            4. Remains strategically sound and actionable
            
            Propose a strategic compromise in 2-3 sentences.
            """
            
            response = self.model.generate_content(compromise_prompt)
            
            return {
                'agent': self.agent_id,
                'compromise_proposal': response.text,
                'opposing_views_considered': len(opposing_views),
                'approach': 'strategic_compromise',
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, "seeking strategic compromise")
    
    # ===== ENHANCED MARKET ANALYSIS METHODS =====
    
    def _get_enhanced_market_context(self) -> str:
        """Get comprehensive market intelligence for strategic analysis"""
        # In a production system, this would integrate with market data APIs
        return """
        CURRENT MARKET INTELLIGENCE (Q4 2024):
        
        INTEREST RATE ENVIRONMENT:
        - Repo Rate: 6.5% (stable after recent policy normalization)
        - Auto Loan Rates: 8.5-9.5% (favorable for financing)
        - Home Loan Rates: 8.5-9.0% (competitive financing window)
        - Credit Card Debt: 15-24% (high cost of borrowing)
        
        EQUITY MARKET CONDITIONS:
        - Indian markets showing resilience amid global uncertainty
        - Technology sector leadership with AI/digital transformation themes
        - Healthcare and pharma showing consistent growth
        - Infrastructure and manufacturing (Make in India) momentum
        - Banking sector recovery with credit growth normalization
        
        INVESTMENT OPPORTUNITIES:
        - SIP strategies favored over lump-sum in volatile markets
        - Diversified equity funds outperforming narrow themes
        - Debt funds attractive with rate stabilization
        - International diversification gaining importance
        - ESG and sustainable investing mainstream adoption
        
        ECONOMIC INDICATORS:
        - GDP growth: 6.5-7% (robust domestic consumption)
        - Inflation: 4-5% (within RBI comfort zone)
        - Corporate earnings growth: 12-15% (broad-based recovery)
        - Rural demand recovery supporting consumption themes
        """
    
    def _create_strategic_financial_summary(self, financial_data: dict) -> str:
        """Create financial summary optimized for strategic analysis"""
        summary = []
        
        try:
            # Net worth for strategy sizing
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                if net_worth_data.get('totalNetWorthValue'):
                    net_worth = net_worth_data['totalNetWorthValue'].get('units', '0')
                    summary.append(f"Net Worth: ₹{net_worth}")
                    
                    # Investment capacity analysis
                    net_worth_float = float(net_worth) if net_worth.replace(',', '').isdigit() else 0
                    if net_worth_float > 1000000:  # 10L+
                        summary.append("High investment capacity - suitable for diversified strategies")
                    elif net_worth_float > 500000:  # 5L+
                        summary.append("Moderate investment capacity - focused portfolio approach")
                    else:
                        summary.append("Building wealth phase - systematic investment recommended")
                    
                # Asset allocation for strategic insights
                assets = net_worth_data.get('assetValues', [])
                equity_exposure = 0
                debt_exposure = 0
                
                for asset in assets:
                    asset_type = asset.get('netWorthAttribute', '')
                    value = float(asset.get('value', {}).get('units', '0'))
                    if 'MUTUAL' in asset_type or 'SECURITIES' in asset_type:
                        equity_exposure += value
                    elif 'FIXED' in asset_type or 'BANK' in asset_type:
                        debt_exposure += value
                
                total_investments = equity_exposure + debt_exposure
                if total_investments > 0:
                    equity_pct = (equity_exposure / total_investments) * 100
                    summary.append(f"Current Asset Allocation: {equity_pct:.1f}% Equity, {100-equity_pct:.1f}% Debt")
            
            # Credit profile for leveraging strategies
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    score = credit_data.get('score', {}).get('bureauScore', 'N/A')
                    summary.append(f"Credit Score: {score}")
                    
                    if str(score).isdigit():
                        score_int = int(score)
                        if score_int >= 750:
                            summary.append("Excellent credit - qualified for best rates and leverage strategies")
                        elif score_int >= 700:
                            summary.append("Good credit - favorable terms available")
                        else:
                            summary.append("Credit improvement needed before leveraging strategies")
            
        except Exception as e:
            summary.append("Financial profile available for strategic analysis")
        
        return " | ".join(summary) if summary else "Basic financial profile for strategy development"
    
    def _extract_strategic_insights(self, analysis_text: str) -> List[str]:
        """Extract strategic insights enhanced for collaboration"""
        insights = []
        
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # Enhanced keyword detection for strategic insights
            if any(keyword in line.lower() for keyword in [
                'recommend', 'strategy', 'consider', 'opportunity', 'allocation', 
                'invest', 'portfolio', 'market', 'timing', 'leverage', 'diversify'
            ]):
                if len(line) > 20 and len(line) < 250:
                    insights.append(line)
        
        # Add market-specific insights
        if 'car' in analysis_text.lower() or 'loan' in analysis_text.lower():
            insights.append("Current interest rate environment favors strategic financing decisions")
        if 'sip' in analysis_text.lower() or 'investment' in analysis_text.lower():
            insights.append("Market volatility supports systematic investment approaches")
        
        return insights[:8]  # Top 8 strategic insights for better collaboration
    
    def _calculate_market_confidence(self, financial_data: Dict) -> float:
        """Calculate enhanced confidence in market-based strategy recommendations"""
        base_confidence = 0.75  # Higher base confidence for market strategies
        
        # Enhanced confidence calculation
        if financial_data.get('net_worth', {}).get('netWorthResponse'):
            base_confidence += 0.1
        if financial_data.get('net_worth', {}).get('mfSchemeAnalytics'):
            base_confidence += 0.1
        if financial_data.get('credit_report', {}).get('creditReports'):
            base_confidence += 0.05  # Credit context helps strategic decisions
        
        return min(base_confidence, 1.0)
    
    def _prepare_market_insights(self, query: str, market_context: str) -> List[str]:
        """Prepare market intelligence insights for collaboration"""
        insights = []
        
        # Query-specific market insights
        if 'car' in query.lower():
            insights.extend([
                "Auto loan rates at 8.5-9% are competitive vs credit card debt at 18%",
                "Current market conditions favor financing over liquidating investments"
            ])
        elif 'invest' in query.lower():
            insights.extend([
                "Market volatility favors SIP strategies over lump-sum investments",
                "Diversified equity funds showing resilience in current environment"
            ])
        elif 'portfolio' in query.lower():
            insights.extend([
                "Asset allocation opportunities exist across equity and debt segments",
                "International diversification gaining importance in portfolio construction"
            ])
        
        # General market insights
        insights.extend([
            "Interest rate stabilization creates strategic opportunities",
            "Technology and healthcare sectors showing structural growth",
            "ESG investing becoming mainstream consideration"
        ])
        
        return insights[:6]
    
    def _identify_strategic_opportunities(self, financial_data: dict) -> List[str]:
        """Identify strategic opportunities enhanced for collaboration"""
        opportunities = []
        
        try:
            # Asset allocation gap analysis
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                assets = net_worth_data.get('assetValues', [])
                
                equity_weight = 0
                debt_weight = 0
                total_value = 0
                
                for asset in assets:
                    value = float(asset.get('value', {}).get('units', '0'))
                    total_value += value
                    asset_type = asset.get('netWorthAttribute', '')
                    
                    if 'MUTUAL' in asset_type or 'SECURITIES' in asset_type:
                        equity_weight += value
                    elif 'FIXED' in asset_type or 'BANK' in asset_type:
                        debt_weight += value
                
                if total_value > 0:
                    equity_pct = (equity_weight / total_value) * 100
                    
                    if equity_pct < 50:
                        opportunities.append("Increase equity allocation for higher growth potential")
                    elif equity_pct > 80:
                        opportunities.append("Add debt component for portfolio stability")
                    
                    if equity_weight > 200000:  # 2L+ in equity
                        opportunities.append("Consider international diversification through global funds")
            
            # Credit-based opportunities
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    score = credit_data.get('score', {}).get('bureauScore', '0')
                    
                    if str(score).isdigit() and int(score) >= 750:
                        opportunities.append("Leverage excellent credit for strategic financing options")
            
            # Market-based opportunities
            opportunities.extend([
                "Systematic investment plans (SIPs) optimize market timing risk",
                "Tax-efficient investments (ELSS) provide dual benefits",
                "Emerging sectors (technology, healthcare) offer growth potential",
                "Goal-based investing for structured wealth creation"
            ])
            
        except Exception as e:
            opportunities.append("Regular market-based portfolio optimization")
        
        return opportunities[:7]
    
    def _extract_actionable_recommendations(self, analysis_text: str) -> List[str]:
        """Extract specific actionable recommendations for collaboration"""
        recommendations = []
        
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # Enhanced recommendation detection
            if any(starter in line.lower() for starter in [
                'consider', 'recommend', 'suggest', 'should', 'start',
                'increase', 'decrease', 'invest', 'allocate', 'diversify',
                'leverage', 'optimize', 'implement'
            ]):
                if len(line) > 15 and len(line) < 200:
                    recommendations.append(line)
        
        return recommendations[:6]
    
    def _analyze_market_timing(self, query: str) -> Dict[str, str]:
        """Analyze market timing considerations for strategic decisions"""
        timing_analysis = {
            'immediate_factors': 'Interest rates stabilized, market resilience observed',
            'short_term_outlook': '3-6 months favorable for strategic asset allocation',
            'long_term_view': '12+ months outlook positive for equity investments',
            'risk_factors': 'Global uncertainty, policy changes, market volatility'
        }
        
        # Query-specific timing insights
        if 'car' in query.lower():
            timing_analysis['recommendation'] = 'Current rates favor financing over liquidation'
        elif 'invest' in query.lower():
            timing_analysis['recommendation'] = 'Systematic approach preferred over lump-sum'
        else:
            timing_analysis['recommendation'] = 'Gradual implementation of strategic changes'
        
        return timing_analysis