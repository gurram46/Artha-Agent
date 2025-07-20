"""
Risk Guardian Agent - Revolutionary Financial Protection Specialist
"I protect you from financial disasters"
Specializes in risk assessment, scenario planning, and financial protection strategies
"""

import json
import os
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..base_agent import BaseAgent


class RiskManagementAgent(BaseAgent):
    """
    Risk Guardian Agent - The Financial Protection Specialist
    
    Core Identity: "Better safe than sorry - let's stress-test every decision"
    
    Specializations:
    ✅ Risk Assessment & Scenario Planning (what could go wrong)
    ✅ Debt Management & Credit Protection (safeguarding credit health)
    ✅ Emergency Fund Optimization (financial safety nets)
    ✅ Insurance Gap Analysis (protection planning)
    ✅ Stress Testing Financial Decisions (worst-case scenarios)
    """
    
    def __init__(self, data_loader):
        super().__init__(
            agent_id="risk_management", 
            agent_name="Risk Guardian", 
            specialization="Risk Assessment & Financial Protection",
            data_loader=data_loader
        )
        
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Dynamic Agent Personality (NO HARDCODED SAMPLES)
        self.agent_prompt = """
        You are a RISK GUARDIAN - a financial expert focused on identifying and protecting against financial risks.
        
        Your role: Assess risks and provide protective guidance related to the user's specific question.

        Guidelines:
        - Write naturally and conversationally
        - Vary your opening sentences and approach each time
        - Focus on the specific risks related to what the user asked
        - Provide practical risk mitigation advice
        - Consider worst-case scenarios when relevant
        - Suggest protective measures and safeguards
        - Write as if protecting a friend from financial mistakes
        
        Important:
        - Be natural and conversational
        - Start responses differently each time  
        - Don't use repetitive warning phrases or templates
        - Address the specific question asked
        - Balance caution with practical advice
        """
    
    # ===== STAGE 1: INDEPENDENT ANALYSIS =====
    
    def analyze(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Stage 1: Independent risk assessment and financial protection analysis
        The Risk Guardian provides comprehensive protection strategies and risk warnings
        """
        try:
            # Get financial data for comprehensive risk analysis
            financial_data = self.data_loader.get_user_financial_data(user_id)
            risk_profile = self._create_comprehensive_risk_profile(financial_data)
            scenario_analysis = self._perform_scenario_analysis(query, financial_data)
            
            # Natural, risk-focused prompt (NO TEMPLATES)
            risk_prompt = f"""
            {self.agent_prompt}
            
            The user is asking: "{query}"
            
            Their risk profile:
            {risk_profile}
            
            Scenario analysis:
            {scenario_analysis}
            
            Please assess the risks related to their specific question and provide protective guidance. 
            Write naturally and conversationally - start your response in a unique way that fits their 
            particular situation.
            
            Focus on:
            - Risks specific to what they asked about
            - Practical protective measures they should consider
            - Realistic scenarios they should be aware of
            - Natural, conversational language (not warning templates)
            
            Write as if you're a careful friend who wants to help them avoid financial mistakes.
            """
            
            response = self.model.generate_content(risk_prompt)
            analysis_text = response.text
            
            # Calculate comprehensive risk metrics
            risk_score = self._calculate_enhanced_risk_score(financial_data)
            
            # Build comprehensive risk response
            risk_result = {
                'agent': self.agent_id,
                'agent_name': self.agent_name,
                'analysis': analysis_text,
                'key_insights': self._extract_protective_insights(analysis_text),
                'confidence': self._calculate_protection_confidence(financial_data),
                'financial_metrics': self.extract_financial_metrics(analysis_text),
                'collaboration_points': self._prepare_risk_warnings(query, financial_data),
                'risk_score': risk_score,
                'risk_level': self._get_enhanced_risk_level(risk_score),
                'critical_warnings': self._identify_comprehensive_risks(financial_data),
                'stress_test_results': self._perform_stress_tests(financial_data, query),
                'protective_strategies': self._extract_protection_strategies(analysis_text),
                'timestamp': datetime.now().isoformat()
            }
            
            return risk_result
            
        except Exception as e:
            return self.handle_error(e, "performing risk assessment and protection analysis")
    
    # ===== STAGE 3: COLLABORATION METHODS =====
    
    def collaborate(self, peer_responses: Dict[str, Any], conflict_type: str) -> Dict[str, Any]:
        """
        Stage 3: Engage in collaborative discussion to resolve conflicts
        Provides protective perspective to challenge or validate other agents' recommendations
        """
        try:
            collaboration_prompt = f"""
            As the RISK GUARDIAN AGENT, you are in a collaborative discussion with Data Analyst and Research agents.
            
            CONFLICT TYPE: {conflict_type}
            PEER RESPONSES: {json.dumps(peer_responses, indent=2)}
            
            YOUR MISSION: Use risk analysis to either VALIDATE or CHALLENGE other agents' recommendations for safety.
            
            COLLABORATION RULES:
            1. Lead with specific risk warnings and protective measures
            2. Challenge aggressive recommendations with scenario analysis
            3. Provide safety-first alternatives and risk mitigation
            4. Quantify potential downsides and protective margins needed
            
            RESPONSE: Provide your protective perspective on this conflict in 2-3 sentences.
            """
            
            response = self.model.generate_content(collaboration_prompt)
            
            return {
                'agent': self.agent_id,
                'agent_name': self.agent_name,
                'collaboration_message': response.text,
                'conflict_type': conflict_type,
                'stance': 'protective_caution',
                'confidence': 0.95,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, f"collaborating on {conflict_type}")
    
    def defend_position(self, challenge: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 3: Defend position with risk-based arguments
        Uses comprehensive risk analysis and scenario planning to support protective recommendations
        """
        try:
            defense_prompt = f"""
            As the RISK GUARDIAN AGENT, another agent is challenging your protective recommendation:
            
            CHALLENGE: "{challenge}"
            EVIDENCE: {json.dumps(evidence, indent=2)}
            
            DEFEND WITH PROTECTION: Use risk scenarios, stress testing, and protective analysis to defend your position.
            Show exactly why your safety-first approach protects their financial future.
            
            Keep it protective and evidence-based.
            """
            
            response = self.model.generate_content(defense_prompt)
            
            return {
                'agent': self.agent_id,
                'defense_message': response.text,
                'challenge_addressed': challenge,
                'evidence_used': evidence,
                'confidence': 0.98,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, "defending protective position")
    
    def seek_compromise(self, opposing_views: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Stage 3: Find protective middle ground with other agents
        Proposes compromise solutions that maintain adequate safety margins
        """
        try:
            compromise_prompt = f"""
            As the RISK GUARDIAN AGENT, you need to find a protective compromise between different recommendations:
            
            OPPOSING VIEWS: {json.dumps(opposing_views, indent=2)}
            
            FIND PROTECTIVE COMPROMISE: Suggest a safety-focused solution that:
            1. Maintains adequate emergency fund and liquidity
            2. Addresses core growth aspirations with protective measures
            3. Provides specific risk mitigation and safety margins
            4. Remains financially responsible and sustainable
            
            Propose a protective compromise in 2-3 sentences.
            """
            
            response = self.model.generate_content(compromise_prompt)
            
            return {
                'agent': self.agent_id,
                'compromise_proposal': response.text,
                'opposing_views_considered': len(opposing_views),
                'approach': 'protective_compromise',
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self.handle_error(e, "seeking protective compromise")
    
    # ===== ENHANCED RISK ANALYSIS METHODS =====
    
    def _create_comprehensive_risk_profile(self, financial_data: dict) -> str:
        """Create comprehensive risk profile for enhanced analysis"""
        profile = []
        
        try:
            # Enhanced debt analysis
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    accounts = credit_data.get('creditAccount', {}).get('creditAccountSummary', {})
                    outstanding = accounts.get('totalOutstandingBalance', {}).get('outstandingBalanceAll', '0')
                    
                    if outstanding != '0':
                        annual_cost = float(outstanding.replace(',', '')) * 0.18 if outstanding.replace(',', '').isdigit() else 0
                        profile.append(f"Debt Burden: ₹{outstanding} (Annual Cost: ₹{annual_cost:,.0f})")
                    
                    score = credit_data.get('score', {}).get('bureauScore', 'N/A')
                    profile.append(f"Credit Score: {score}")
            
            # Liquidity analysis
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                assets = net_worth_data.get('assetValues', [])
                
                liquid_assets = 0
                total_assets = 0
                for asset in assets:
                    value = float(asset.get('value', {}).get('units', '0'))
                    total_assets += value
                    asset_type = asset.get('netWorthAttribute', '')
                    if 'MUTUAL' in asset_type or 'SECURITIES' in asset_type or 'SAVINGS' in asset_type:
                        liquid_assets += value
                
                profile.append(f"Liquid Assets: ₹{liquid_assets:,.0f} of ₹{total_assets:,.0f}")
                
                # Emergency fund adequacy (assuming ₹50K monthly expenses)
                emergency_months = liquid_assets / 50000 if liquid_assets > 0 else 0
                profile.append(f"Emergency Coverage: {emergency_months:.1f} months")
                
        except Exception as e:
            profile.append("Risk profile data available for analysis")
        
        return " | ".join(profile) if profile else "Standard risk assessment"
    
    def _perform_scenario_analysis(self, query: str, financial_data: dict) -> str:
        """Perform scenario analysis for risk assessment"""
        scenarios = []
        
        # Job loss scenario
        scenarios.append("Job Loss: 6-month income disruption test")
        
        # Market crash scenario
        scenarios.append("Market Crash: 30% portfolio decline stress test")
        
        # Query-specific scenarios
        if 'car' in query.lower():
            scenarios.append("Car Purchase: Added EMI impact on cash flow")
        elif 'invest' in query.lower():
            scenarios.append("Investment Loss: Principal erosion risk assessment")
        
        scenarios.append("Interest Rate Rise: 2% increase impact on borrowing costs")
        
        return " | ".join(scenarios)
    
    def _calculate_enhanced_risk_score(self, financial_data: Dict) -> float:
        """Enhanced risk score calculation for collaboration framework"""
        risk_score = 0.0
        
        try:
            # Debt service ratio risk
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    accounts = credit_data.get('creditAccount', {}).get('creditAccountSummary', {})
                    outstanding = accounts.get('totalOutstandingBalance', {}).get('outstandingBalanceAll', '0')
                    
                    if outstanding != '0':
                        debt_amount = float(outstanding.replace(',', ''))
                        # Assume monthly income of ₹1L for risk calculation
                        debt_ratio = (debt_amount * 0.18 / 12) / 100000  # Monthly interest / assumed income
                        if debt_ratio > 0.4:  # >40% debt service ratio
                            risk_score += 30
                        elif debt_ratio > 0.2:
                            risk_score += 15
            
            # Liquidity risk
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                assets = net_worth_data.get('assetValues', [])
                
                liquid_ratio = 0
                if assets:
                    total_assets = sum(float(asset.get('value', {}).get('units', '0')) for asset in assets)
                    liquid_assets = sum(float(asset.get('value', {}).get('units', '0')) for asset in assets 
                                      if 'SAVINGS' in asset.get('netWorthAttribute', '') or 'MUTUAL' in asset.get('netWorthAttribute', ''))
                    
                    liquid_ratio = liquid_assets / total_assets if total_assets > 0 else 0
                    
                    if liquid_ratio < 0.2:  # <20% liquid assets
                        risk_score += 25
                    elif liquid_ratio < 0.4:
                        risk_score += 10
            
            # Credit score risk
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    score = credit_data.get('score', {}).get('bureauScore', '750')
                    
                    if str(score).isdigit():
                        score_int = int(score)
                        if score_int < 650:
                            risk_score += 25
                        elif score_int < 700:
                            risk_score += 15
                        elif score_int < 750:
                            risk_score += 5
            
        except Exception:
            risk_score = 50.0  # Default medium risk
        
        return min(risk_score, 100.0)
    
    def _get_enhanced_risk_level(self, risk_score: float) -> str:
        """Enhanced risk level classification"""
        if risk_score >= 75:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH" 
        elif risk_score >= 40:
            return "MODERATE"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _extract_protective_insights(self, analysis_text: str) -> List[str]:
        """Extract protective insights enhanced for collaboration"""
        insights = []
        
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # Enhanced keyword detection for protective insights
            if any(keyword in line.lower() for keyword in [
                'risk', 'warning', 'danger', 'caution', 'protect', 'safe',
                'emergency', 'debt', 'stress', 'vulnerable', 'secure'
            ]):
                if len(line) > 20 and len(line) < 300:
                    insights.append(line)
        
        # Add calculated protective insights
        if 'debt' in analysis_text.lower():
            insights.append("High-interest debt elimination should precede aggressive investments")
        if 'emergency' in analysis_text.lower():
            insights.append("Emergency fund adequacy is critical for financial stability")
        
        return insights[:8]  # Top 8 protective insights
    
    def _calculate_protection_confidence(self, financial_data: Dict) -> float:
        """Calculate confidence in protective recommendations"""
        base_confidence = 0.8  # High base confidence for protective advice
        
        # Enhanced confidence based on data completeness
        if financial_data.get('credit_report', {}).get('creditReports'):
            base_confidence += 0.1
        if financial_data.get('net_worth', {}).get('netWorthResponse'):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _prepare_risk_warnings(self, query: str, financial_data: dict) -> List[str]:
        """Prepare risk warnings for collaboration"""
        warnings = []
        
        # Query-specific warnings
        if 'car' in query.lower():
            warnings.extend([
                "Additional EMI burden must be stress-tested against income volatility",
                "Existing debt should be prioritized before new borrowing"
            ])
        elif 'invest' in query.lower():
            warnings.extend([
                "Emergency fund adequacy must be verified before aggressive investing",
                "Market volatility could force premature liquidation of investments"
            ])
        
        # General risk warnings
        try:
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    accounts = credit_data.get('creditAccount', {}).get('creditAccountSummary', {})
                    outstanding = accounts.get('totalOutstandingBalance', {}).get('outstandingBalanceAll', '0')
                    
                    if outstanding != '0':
                        warnings.append(f"₹{outstanding} outstanding debt creates financial vulnerability")
        except:
            pass
        
        warnings.extend([
            "Diversification across asset classes reduces concentration risk",
            "Adequate insurance coverage protects against unforeseen events"
        ])
        
        return warnings[:6]
    
    def _identify_comprehensive_risks(self, financial_data: dict) -> List[str]:
        """Identify comprehensive risks for enhanced protection"""
        risks = []
        
        try:
            # Enhanced debt risk analysis
            if financial_data.get('credit_report'):
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    accounts = credit_data.get('creditAccount', {}).get('creditAccountSummary', {})
                    outstanding = accounts.get('totalOutstandingBalance', {}).get('outstandingBalanceAll', '0')
                    
                    if outstanding != '0':
                        debt_amount = float(outstanding.replace(',', ''))
                        annual_cost = debt_amount * 0.18
                        risks.append(f"URGENT: ₹{outstanding} debt costs ₹{annual_cost:,.0f} annually - prioritize elimination")
            
            # Liquidity risk
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                assets = net_worth_data.get('assetValues', [])
                
                if assets:
                    cash_assets = sum(float(asset.get('value', {}).get('units', '0')) for asset in assets 
                                    if 'SAVINGS' in asset.get('netWorthAttribute', ''))
                    # Assuming ₹50K monthly expenses
                    emergency_months = cash_assets / 50000 if cash_assets > 0 else 0
                    
                    if emergency_months < 3:
                        risks.append(f"WARNING: Emergency fund covers only {emergency_months:.1f} months - inadequate safety buffer")
                    elif emergency_months < 6:
                        risks.append(f"CAUTION: Emergency fund covers {emergency_months:.1f} months - consider building to 6 months")
        
        except Exception:
            risks.append("Comprehensive risk assessment requires data review")
        
        return risks[:5]
    
    def _perform_stress_tests(self, financial_data: dict, query: str) -> Dict[str, str]:
        """Perform stress tests for collaboration insights"""
        stress_results = {}
        
        try:
            # Job loss stress test
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                assets = net_worth_data.get('assetValues', [])
                liquid_assets = sum(float(asset.get('value', {}).get('units', '0')) for asset in assets 
                                  if 'SAVINGS' in asset.get('netWorthAttribute', '') or 'MUTUAL' in asset.get('netWorthAttribute', ''))
                
                survival_months = liquid_assets / 50000 if liquid_assets > 0 else 0
                stress_results['job_loss'] = f"Can survive {survival_months:.1f} months without income"
            
            # Market crash stress test
            if financial_data.get('net_worth'):
                net_worth_data = financial_data['net_worth'].get('netWorthResponse', {})
                net_worth = float(net_worth_data.get('totalNetWorthValue', {}).get('units', '0'))
                post_crash_worth = net_worth * 0.7  # 30% decline
                stress_results['market_crash'] = f"30% market decline: Net worth drops to ₹{post_crash_worth:,.0f}"
            
            # Query-specific stress test
            if 'car' in query.lower():
                stress_results['car_purchase'] = "Additional EMI reduces available liquidity for emergencies"
            elif 'invest' in query.lower():
                stress_results['investment'] = "Investment losses could impact emergency fund adequacy"
        
        except Exception:
            stress_results['general'] = "Stress testing requires comprehensive data analysis"
        
        return stress_results
    
    def _extract_protection_strategies(self, analysis_text: str) -> List[str]:
        """Extract protection strategies for collaboration"""
        strategies = []
        
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # Enhanced detection for protection strategies
            if any(keyword in line.lower() for keyword in [
                'protect', 'secure', 'mitigate', 'hedge', 'insure',
                'emergency', 'diversify', 'reduce', 'eliminate', 'build'
            ]):
                if len(line) > 15 and len(line) < 200:
                    strategies.append(line)
        
        return strategies[:6]