"""
Risk Assessment Agent - AI-powered financial risk analysis and protection gaps
"""

import json
from typing import Dict, Any
import logging
from .base_money_agent import BaseMoneyAgent

logger = logging.getLogger(__name__)


class RiskAssessmentAgent(BaseMoneyAgent):
    """AI agent specialized in comprehensive financial risk analysis and protection planning"""
    
    def __init__(self, gemini_client):
        super().__init__(gemini_client)
        self.name = "Risk Assessment Guardian"
        self.description = "AI-powered risk analysis and financial protection gaps detection"
    
    async def _perform_analysis(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive financial risk assessment and protection gap analysis"""
        try:
            financial_data = self.format_financial_data(mcp_data)
            net_worth = self.calculate_net_worth(mcp_data)
            
            # Calculate risk indicators
            loans = mcp_data.get('loans', [])
            mutual_funds = mcp_data.get('mutual_funds', [])
            accounts = mcp_data.get('accounts', [])
            
            total_debt = sum(loan.get('outstanding_amount', 0) for loan in loans)
            total_investments = sum(fund.get('current_value', 0) for fund in mutual_funds)
            emergency_fund = sum(acc.get('balance', 0) for acc in accounts)
            
            # Risk ratios
            debt_to_income_proxy = total_debt / (net_worth + 1)  # Proxy calculation
            investment_concentration_risk = len(mutual_funds) < 3
            emergency_fund_months = (emergency_fund / 50000) if emergency_fund > 0 else 0  # Rough estimate
            
            system_prompt = f"""
            You are the RISK ASSESSMENT GUARDIAN - a financial security expert who identifies threats to wealth.
            
            Your mission: Comprehensive risk analysis and protection gap identification.
            
            Risk Analysis Framework:
            1. Immediate Financial Threats (debt, cash flow)
            2. Investment Risk Exposure (concentration, volatility)
            3. Protection Gaps (insurance, emergency funds)
            4. Market and Economic Risks
            5. Life Event Risk Preparedness
            
            RISK STYLE:
            - Use security and protection terminology
            - Use ⚠️, 🛡️, 🚨 emojis
            - Quantify risk levels and potential impacts
            - Provide specific protection strategies
            - Prioritize by urgency and impact
            """
            
            prompt = f"""
            COMPREHENSIVE RISK ASSESSMENT
            Net Worth: ₹{net_worth:,.2f}
            Total Debt: ₹{total_debt:,.2f}
            Emergency Fund: ₹{emergency_fund:,.2f} (~{emergency_fund_months:.1f} months)
            Investment Concentration: {len(mutual_funds)} funds
            
            RISK INDICATORS:
            - Debt Ratio: {debt_to_income_proxy:.1%}
            - Investment Diversity: {'Low' if investment_concentration_risk else 'Adequate'}
            - Emergency Coverage: {emergency_fund_months:.1f} months
            
            {financial_data}
            
            Conduct a comprehensive risk assessment. What threats could destroy this person's wealth? What protection gaps exist?
            
            Format as JSON:
            {{
                "overall_risk_level": "High/Medium/Low",
                "risk_score": 75,
                "critical_risks": [
                    {{
                        "risk_type": "Specific financial threat",
                        "severity": "Critical/High/Medium/Low",
                        "potential_impact": "₹XX,XXX loss potential",
                        "probability": "High/Medium/Low",
                        "time_horizon": "Immediate/6 months/1 year",
                        "mitigation_strategy": "Specific protection action"
                    }}
                ],
                "protection_gaps": [
                    {{
                        "gap_type": "Missing protection area",
                        "exposure_amount": "₹XX,XXX at risk",
                        "urgency": "Critical/High/Medium",
                        "solution": "Specific protection product/strategy",
                        "estimated_cost": "₹X,XXX annually"
                    }}
                ],
                "risk_mitigation_plan": [
                    "Immediate action item 1",
                    "Short-term protection step 2",
                    "Long-term security measure 3"
                ],
                "emergency_preparedness": {{
                    "current_months_covered": 3.5,
                    "recommended_months": 6,
                    "gap_amount": "₹XX,XXX needed"
                }},
                "insurance_assessment": {{
                    "life_insurance_need": "₹XX lakhs",
                    "health_coverage_adequacy": "Adequate/Insufficient",
                    "asset_protection_gaps": ["Specific gap"]
                }},
                "stress_test_results": {{
                    "market_crash_impact": "₹XX,XXX loss",
                    "job_loss_survival": "X months",
                    "medical_emergency_impact": "₹XX,XXX exposure"
                }},
                "confidence_level": 0.80
            }}
            """
            
            ai_response = await self.call_ai(prompt, system_prompt)
            
            # Try to parse JSON response
            try:
                result = json.loads(ai_response)
                
                # Add analysis metadata
                result.update({
                    "agent_name": self.name,
                    "analysis_type": "risk_assessment",
                    "timestamp": "2025-01-23T19:33:28+05:30",
                    "risk_metrics": {
                        "debt_to_networth_ratio": f"{debt_to_income_proxy:.1%}",
                        "emergency_fund_months": f"{emergency_fund_months:.1f}",
                        "investment_diversity_score": len(mutual_funds),
                        "total_exposure": total_debt + total_investments
                    }
                })
                
                return result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON from Risk Assessment AI response")
                
                # Calculate basic risk level
                risk_factors = 0
                if debt_to_income_proxy > 0.3: risk_factors += 1
                if emergency_fund_months < 3: risk_factors += 1
                if investment_concentration_risk: risk_factors += 1
                
                risk_level = "High" if risk_factors >= 2 else "Medium" if risk_factors == 1 else "Low"
                
                return {
                    "overall_risk_level": risk_level,
                    "risk_score": max(0, 100 - (risk_factors * 25)),
                    "critical_risks": [{
                        "risk_type": "Financial vulnerability detected",
                        "severity": "Medium",
                        "potential_impact": f"₹{total_debt:,.0f}",
                        "probability": "Medium",
                        "time_horizon": "6 months",
                        "mitigation_strategy": "Comprehensive risk analysis available"
                    }],
                    "protection_gaps": [{
                        "gap_type": "Emergency fund adequacy",
                        "exposure_amount": f"₹{max(0, 300000 - emergency_fund):,.0f}",
                        "urgency": "High" if emergency_fund_months < 3 else "Medium",
                        "solution": "Build emergency fund to 6 months expenses",
                        "estimated_cost": "₹10,000 monthly"
                    }],
                    "risk_mitigation_plan": [
                        ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                        "Build adequate emergency fund",
                        "Review insurance coverage"
                    ],
                    "emergency_preparedness": {
                        "current_months_covered": emergency_fund_months,
                        "recommended_months": 6,
                        "gap_amount": f"₹{max(0, 300000 - emergency_fund):,.0f}"
                    },
                    "insurance_assessment": {
                        "life_insurance_need": f"₹{net_worth * 0.1 / 100000:.0f} lakhs",
                        "health_coverage_adequacy": "Assessment needed",
                        "asset_protection_gaps": ["Detailed analysis required"]
                    },
                    "stress_test_results": {
                        "market_crash_impact": f"₹{total_investments * 0.3:,.0f}",
                        "job_loss_survival": f"{emergency_fund_months:.1f} months",
                        "medical_emergency_impact": "₹5,00,000 potential"
                    },
                    "confidence_level": 0.75,
                    "agent_name": self.name,
                    "analysis_type": "risk_assessment",
                    "timestamp": "2025-01-23T19:33:28+05:30"
                }
                
        except Exception as e:
            logger.error(f"Risk Assessment analysis failed: {e}")
            return {
                "overall_risk_level": "Unknown",
                "risk_score": 0,
                "critical_risks": [{
                    "risk_type": "Analysis unavailable",
                    "severity": "Critical",
                    "potential_impact": f"Assessment failed: {str(e)}",
                    "probability": "Unknown",
                    "time_horizon": "Unknown",
                    "mitigation_strategy": "Retry analysis"
                }],
                "protection_gaps": [{
                    "gap_type": "System unavailable",
                    "exposure_amount": "Cannot calculate",
                    "urgency": "Critical",
                    "solution": "Please try again later",
                    "estimated_cost": "Unknown"
                }],
                "risk_mitigation_plan": ["Retry risk assessment when system is available"],
                "emergency_preparedness": {
                    "current_months_covered": 0,
                    "recommended_months": 6,
                    "gap_amount": "Cannot calculate"
                },
                "insurance_assessment": {
                    "life_insurance_need": "Assessment needed",
                    "health_coverage_adequacy": "Cannot assess",
                    "asset_protection_gaps": ["Analysis unavailable"]
                },
                "stress_test_results": {
                    "market_crash_impact": "Cannot calculate",
                    "job_loss_survival": "Cannot assess",
                    "medical_emergency_impact": "Assessment needed"
                },
                "confidence_level": 0.0,
                "error": str(e),
                "agent_name": self.name,
                "analysis_type": "risk_assessment",
                "timestamp": "2025-01-23T19:33:28+05:30"
            }