"""
Stock Recommendation Agent - Personalized investment recommendations based on research and user profile

This agent takes comprehensive stock research and user investment profile to generate
personalized, actionable investment recommendations with scoring and reasoning.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from google import genai
from google.genai import types


class StockRecommendationAgent:
    """
    Specialized AI agent for generating personalized stock investment recommendations.
    
    This agent analyzes:
    - Comprehensive stock research data
    - User investment profile and preferences
    - Risk tolerance and investment horizon
    - Financial goals and constraints
    
    And provides:
    - Numerical recommendation score (0-100)
    - Investment sentiment (Strong Buy, Buy, Hold, Sell, Strong Sell)
    - Detailed reasoning and justification
    - Risk assessment and suitability analysis
    - Actionable recommendations
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the Stock Recommendation Agent."""
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API key is required")
            
        # Initialize Gemini client
        genai.configure(api_key=self.api_key)
        self.client = genai.Client()
        
        # Generation config for recommendations
        self.config = types.GenerateContentConfig(
            temperature=0.1,  # Very low temperature for consistent recommendations
            max_output_tokens=3000
        )
    
    async def generate_recommendation(
        self, 
        stock_research: Dict[str, Any], 
        user_profile: Dict[str, Any],
        stock_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive personalized investment recommendation.
        
        Args:
            stock_research: Research data from StockResearchAgent
            user_profile: User investment profile and preferences
            stock_data: Current stock price and market data
            
        Returns:
            Comprehensive recommendation with score, sentiment, and reasoning
        """
        print(f"🎯 Generating personalized recommendation for {stock_research.get('symbol', 'Unknown')}...")
        
        try:
            # Generate the recommendation
            recommendation = await self._analyze_and_recommend(stock_research, user_profile, stock_data)
            
            # Calculate detailed scoring breakdown
            scoring_breakdown = await self._calculate_scoring_breakdown(stock_research, user_profile, recommendation)
            
            # Generate investment action plan
            action_plan = await self._generate_action_plan(recommendation, user_profile, stock_data)
            
            return {
                "symbol": stock_research.get("symbol", "Unknown"),
                "company_name": stock_research.get("company_name", "Unknown"),
                "recommendation_timestamp": datetime.now().isoformat(),
                
                # Core recommendation
                "score": recommendation["score"],
                "sentiment": recommendation["sentiment"],
                "confidence": recommendation["confidence"],
                
                # Detailed analysis
                "strengths": recommendation["strengths"],
                "weaknesses": recommendation["weaknesses"],
                "considerations": recommendation["considerations"],
                
                # User-specific analysis
                "suitability_analysis": recommendation["suitability_analysis"],
                "risk_assessment": recommendation["risk_assessment"],
                "alignment_score": recommendation["alignment_score"],
                
                # Breakdown and scoring
                "scoring_breakdown": scoring_breakdown,
                "action_plan": action_plan,
                
                # Metadata
                "user_profile_summary": {
                    "risk_tolerance": user_profile.get("riskTolerance", "unknown"),
                    "investment_horizon": user_profile.get("investmentHorizon", "unknown"),
                    "investment_goal": user_profile.get("investmentGoal", "unknown"),
                    "monthly_investment": user_profile.get("monthlyInvestment", 0)
                },
                "research_quality": {
                    "total_sources": stock_research.get("metadata", {}).get("total_sources", 0),
                    "research_confidence": stock_research.get("metadata", {}).get("average_confidence", 0),
                    "research_areas_covered": len(stock_research.get("research_areas", {}))
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating recommendation: {e}")
            return self._generate_fallback_recommendation(stock_research, user_profile, str(e))
    
    async def _analyze_and_recommend(
        self, 
        stock_research: Dict[str, Any], 
        user_profile: Dict[str, Any],
        stock_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Core recommendation analysis using AI."""
        
        # Prepare comprehensive analysis prompt
        prompt = self._build_recommendation_prompt(stock_research, user_profile, stock_data)
        
        try:
            # Generate recommendation using Gemini
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=self.config
            )
            
            recommendation_text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse structured recommendation
            structured_rec = self._parse_recommendation_response(recommendation_text)
            
            return structured_rec
            
        except Exception as e:
            print(f"⚠️ Error in AI recommendation analysis: {e}")
            return self._generate_basic_recommendation(stock_research, user_profile)
    
    def _build_recommendation_prompt(
        self, 
        stock_research: Dict[str, Any], 
        user_profile: Dict[str, Any],
        stock_data: Dict[str, Any] = None
    ) -> str:
        """Build comprehensive prompt for recommendation generation."""
        
        # Extract key research insights
        research_summary = self._summarize_research(stock_research)
        
        # Extract user profile details
        risk_tolerance = user_profile.get("riskTolerance", "moderate")
        investment_horizon = user_profile.get("investmentHorizon", "medium")
        investment_goal = user_profile.get("investmentGoal", "balanced")
        monthly_investment = user_profile.get("monthlyInvestment", 10000)
        
        # Current market data
        current_price = stock_data.get("currentPrice", 0) if stock_data else 0
        market_cap = stock_data.get("marketCap", "Unknown") if stock_data else "Unknown"
        
        prompt = f"""
        As a senior investment advisor with 20+ years of experience, provide a comprehensive personalized investment recommendation.

        STOCK RESEARCH ANALYSIS:
        {research_summary}

        INVESTOR PROFILE:
        - Risk Tolerance: {risk_tolerance.title()} (Conservative = Low risk tolerance, Moderate = Balanced risk-return, Aggressive = High risk tolerance)
        - Investment Horizon: {investment_horizon.title()} (Short = <2 years, Medium = 2-5 years, Long = 5+ years)
        - Investment Goal: {investment_goal.title()} (Growth = Capital appreciation focus, Income = Dividend focus, Balanced = Both)
        - Monthly Investment Budget: ₹{monthly_investment:,}
        - Current Stock Price: ₹{current_price} (Market Cap: {market_cap})

        PROVIDE YOUR RECOMMENDATION IN THIS EXACT FORMAT:

        RECOMMENDATION SCORE: [0-100 numerical score]
        INVESTMENT SENTIMENT: [Strong Buy/Buy/Hold/Sell/Strong Sell]
        CONFIDENCE LEVEL: [0.0-1.0 confidence in recommendation]

        KEY STRENGTHS:
        • [Strength 1 specific to this investor profile]
        • [Strength 2 specific to this investor profile]
        • [Strength 3 specific to this investor profile]
        • [Strength 4 specific to this investor profile]
        • [Strength 5 specific to this investor profile]

        KEY WEAKNESSES:
        • [Weakness 1 relevant to this investor]
        • [Weakness 2 relevant to this investor]
        • [Weakness 3 relevant to this investor]
        • [Weakness 4 relevant to this investor]

        INVESTMENT CONSIDERATIONS:
        • [Consideration 1 for this investor profile]
        • [Consideration 2 for this investor profile]
        • [Consideration 3 for this investor profile]
        • [Consideration 4 for this investor profile]

        SUITABILITY ANALYSIS:
        [2-3 sentences explaining why this stock is/isn't suitable for this specific investor profile considering their risk tolerance, horizon, and goals]

        RISK ASSESSMENT:
        [2-3 sentences analyzing the key risks for this investor specifically, considering their profile and investment amount]

        ALIGNMENT SCORE: [0-100 score for how well this stock aligns with investor's profile]

        SCORING RATIONALE:
        [2-3 sentences explaining the numerical score, considering both stock fundamentals and investor suitability]

        Base your analysis on:
        1. Match between stock characteristics and investor profile
        2. Risk-return alignment with investor preferences
        3. Time horizon compatibility with stock outlook
        4. Investment amount suitability for this stock
        5. Goal alignment (growth vs income vs balanced)
        
        Be specific, actionable, and consider both the stock's merits and the investor's unique situation.
        """
        
        return prompt
    
    def _summarize_research(self, stock_research: Dict[str, Any]) -> str:
        """Summarize research findings for the recommendation prompt."""
        summary_parts = []
        
        # Company and synthesis overview
        if "synthesis" in stock_research:
            synthesis = stock_research["synthesis"]
            if "investment_thesis" in synthesis:
                summary_parts.append(f"Investment Thesis: {synthesis['investment_thesis']}")
            if "conviction_level" in synthesis:
                summary_parts.append(f"Research Conviction: {synthesis['conviction_level']}/10")
        
        # Research areas summary
        research_areas = stock_research.get("research_areas", {})
        for area, data in research_areas.items():
            confidence = data.get("confidence", 0)
            key_points = data.get("key_points", [])
            
            summary_parts.append(f"\n{area.replace('_', ' ').title()} (Confidence: {confidence:.1f}):")
            for point in key_points[:3]:  # Top 3 points per area
                summary_parts.append(f"  • {point[:150]}...")
        
        return "\n".join(summary_parts)
    
    def _parse_recommendation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured recommendation from AI response."""
        recommendation = {
            "score": 50,
            "sentiment": "Hold",
            "confidence": 0.5,
            "strengths": [],
            "weaknesses": [],
            "considerations": [],
            "suitability_analysis": "",
            "risk_assessment": "",
            "alignment_score": 50,
            "scoring_rationale": ""
        }
        
        try:
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                line_lower = line.lower()
                
                # Extract numerical values
                if 'recommendation score:' in line_lower:
                    score_match = [int(x) for x in line.split() if x.isdigit()]
                    if score_match:
                        recommendation["score"] = max(0, min(100, score_match[0]))
                
                elif 'investment sentiment:' in line_lower:
                    sentiment_text = line.split(':', 1)[1].strip()
                    recommendation["sentiment"] = sentiment_text
                
                elif 'confidence level:' in line_lower:
                    try:
                        conf_text = line.split(':', 1)[1].strip()
                        conf_value = float(conf_text)
                        recommendation["confidence"] = max(0.0, min(1.0, conf_value))
                    except:
                        pass
                
                elif 'alignment score:' in line_lower:
                    align_match = [int(x) for x in line.split() if x.isdigit()]
                    if align_match:
                        recommendation["alignment_score"] = max(0, min(100, align_match[0]))
                
                # Section headers
                elif 'key strengths:' in line_lower:
                    current_section = 'strengths'
                elif 'key weaknesses:' in line_lower:
                    current_section = 'weaknesses'
                elif 'investment considerations:' in line_lower:
                    current_section = 'considerations'
                elif 'suitability analysis:' in line_lower:
                    current_section = 'suitability_analysis'
                elif 'risk assessment:' in line_lower:
                    current_section = 'risk_assessment'
                elif 'scoring rationale:' in line_lower:
                    current_section = 'scoring_rationale'
                
                # Content extraction
                elif current_section:
                    if current_section in ['strengths', 'weaknesses', 'considerations']:
                        if line.startswith('•') or line.startswith('-'):
                            cleaned = line.lstrip('•- ').strip()
                            if len(cleaned) > 10:
                                recommendation[current_section].append(cleaned)
                    elif current_section in ['suitability_analysis', 'risk_assessment', 'scoring_rationale']:
                        if len(line) > 20:
                            recommendation[current_section] += line + " "
            
            # Clean up text fields
            for field in ['suitability_analysis', 'risk_assessment', 'scoring_rationale']:
                recommendation[field] = recommendation[field].strip()
        
        except Exception as e:
            print(f"⚠️ Error parsing recommendation response: {e}")
        
        return recommendation
    
    async def _calculate_scoring_breakdown(
        self, 
        stock_research: Dict[str, Any], 
        user_profile: Dict[str, Any], 
        recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate detailed scoring breakdown across different factors."""
        
        try:
            # Base component scores
            components = {
                "technical_score": 50,
                "fundamental_score": 50,
                "market_sentiment_score": 50,
                "risk_alignment_score": 50,
                "time_horizon_fit": 50,
                "goal_alignment": 50
            }
            
            # Extract research confidence levels
            research_areas = stock_research.get("research_areas", {})
            
            # Technical analysis score
            if "technical_analysis" in research_areas:
                tech_confidence = research_areas["technical_analysis"].get("confidence", 0.5)
                components["technical_score"] = int(tech_confidence * 100)
            
            # Fundamental analysis score  
            if "fundamental_analysis" in research_areas:
                fund_confidence = research_areas["fundamental_analysis"].get("confidence", 0.5)
                components["fundamental_score"] = int(fund_confidence * 100)
            
            # Market sentiment score
            if "market_sentiment" in research_areas:
                sentiment_confidence = research_areas["market_sentiment"].get("confidence", 0.5)
                components["market_sentiment_score"] = int(sentiment_confidence * 100)
            
            # Risk alignment based on user profile
            risk_tolerance = user_profile.get("riskTolerance", "moderate")
            if risk_tolerance == "conservative":
                # Lower scores for high-risk elements
                components["risk_alignment_score"] = max(30, min(70, recommendation.get("alignment_score", 50)))
            elif risk_tolerance == "aggressive":
                # Higher tolerance for risk
                components["risk_alignment_score"] = max(40, min(90, recommendation.get("alignment_score", 50) + 10))
            else:
                components["risk_alignment_score"] = recommendation.get("alignment_score", 50)
            
            # Time horizon fit
            horizon = user_profile.get("investmentHorizon", "medium")
            if horizon == "long":
                components["time_horizon_fit"] = 80  # Most stocks suit long-term
            elif horizon == "short":
                components["time_horizon_fit"] = 40  # Fewer stocks suit short-term
            else:
                components["time_horizon_fit"] = 60
            
            # Goal alignment
            goal = user_profile.get("investmentGoal", "balanced")
            synthesis = stock_research.get("synthesis", {})
            conviction = synthesis.get("conviction_level", 5)
            
            if goal == "growth":
                components["goal_alignment"] = min(90, conviction * 10 + 20)
            elif goal == "income":
                components["goal_alignment"] = 50  # Moderate for most stocks
            else:  # balanced
                components["goal_alignment"] = min(80, conviction * 8 + 20)
            
            # Calculate weighted overall score
            weights = {
                "technical_score": 0.15,
                "fundamental_score": 0.25,
                "market_sentiment_score": 0.20,
                "risk_alignment_score": 0.20,
                "time_horizon_fit": 0.10,
                "goal_alignment": 0.10
            }
            
            weighted_score = sum(components[comp] * weights[comp] for comp in components)
            
            return {
                "components": components,
                "weights": weights,
                "weighted_total": int(weighted_score),
                "methodology": "Multi-factor scoring based on research quality and user profile alignment"
            }
            
        except Exception as e:
            print(f"⚠️ Error calculating scoring breakdown: {e}")
            return {
                "components": {"error": "Calculation failed"},
                "weighted_total": recommendation.get("score", 50),
                "methodology": "Fallback scoring due to calculation error"
            }
    
    async def _generate_action_plan(
        self, 
        recommendation: Dict[str, Any], 
        user_profile: Dict[str, Any],
        stock_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate specific action plan for the investor."""
        
        score = recommendation.get("score", 50)
        sentiment = recommendation.get("sentiment", "Hold")
        monthly_budget = user_profile.get("monthlyInvestment", 10000)
        current_price = stock_data.get("currentPrice", 0) if stock_data else 0
        
        action_plan = {
            "primary_action": "",
            "investment_amount": "",
            "timing_strategy": "",
            "monitoring_plan": "",
            "exit_strategy": "",
            "next_review_date": ""
        }
        
        try:
            if score >= 80:
                action_plan["primary_action"] = "Strong Buy - Consider significant allocation"
                if current_price > 0:
                    suggested_allocation = min(monthly_budget * 2, monthly_budget * 0.3)  # Up to 30% or 2 months budget
                    shares = int(suggested_allocation / current_price)
                    action_plan["investment_amount"] = f"₹{suggested_allocation:,.0f} ({shares} shares)"
                else:
                    action_plan["investment_amount"] = f"₹{monthly_budget * 0.3:,.0f} (30% of monthly budget)"
                action_plan["timing_strategy"] = "Immediate purchase or systematic buying over 2-4 weeks"
                
            elif score >= 65:
                action_plan["primary_action"] = "Buy - Suitable for portfolio inclusion"
                if current_price > 0:
                    suggested_allocation = min(monthly_budget * 1.5, monthly_budget * 0.2)  # Up to 20% or 1.5 months budget
                    shares = int(suggested_allocation / current_price)
                    action_plan["investment_amount"] = f"₹{suggested_allocation:,.0f} ({shares} shares)"
                else:
                    action_plan["investment_amount"] = f"₹{monthly_budget * 0.2:,.0f} (20% of monthly budget)"
                action_plan["timing_strategy"] = "Buy on dips or systematic investment over 4-6 weeks"
                
            elif score >= 35:
                action_plan["primary_action"] = "Hold - Monitor closely if already invested"
                action_plan["investment_amount"] = "No new investment recommended"
                action_plan["timing_strategy"] = "Wait for better entry points or improved fundamentals"
                
            else:
                action_plan["primary_action"] = "Avoid - Not suitable for this investor profile"
                action_plan["investment_amount"] = "No investment recommended"
                action_plan["timing_strategy"] = "Look for alternative investments"
            
            # Common elements
            action_plan["monitoring_plan"] = "Review quarterly earnings, major news, and technical levels"
            action_plan["exit_strategy"] = f"Review if fundamentals deteriorate or score drops below {max(30, score - 20)}"
            
            # Next review date based on investment horizon
            horizon = user_profile.get("investmentHorizon", "medium")
            if horizon == "short":
                action_plan["next_review_date"] = "1 month"
            elif horizon == "long":
                action_plan["next_review_date"] = "6 months"
            else:
                action_plan["next_review_date"] = "3 months"
                
        except Exception as e:
            print(f"⚠️ Error generating action plan: {e}")
            action_plan["primary_action"] = "Manual review recommended due to calculation error"
        
        return action_plan
    
    def _generate_basic_recommendation(self, stock_research: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic recommendation when AI analysis fails."""
        
        # Basic scoring based on available data
        base_score = 50
        
        # Adjust based on research conviction if available
        synthesis = stock_research.get("synthesis", {})
        conviction = synthesis.get("conviction_level", 5)
        base_score = min(90, max(10, conviction * 10))
        
        # Adjust for risk tolerance
        risk_tolerance = user_profile.get("riskTolerance", "moderate")
        if risk_tolerance == "conservative":
            base_score = max(20, base_score - 15)
        elif risk_tolerance == "aggressive":
            base_score = min(85, base_score + 10)
        
        # Determine sentiment
        if base_score >= 75:
            sentiment = "Buy"
        elif base_score >= 55:
            sentiment = "Hold"
        else:
            sentiment = "Sell"
        
        return {
            "score": base_score,
            "sentiment": sentiment,
            "confidence": 0.4,  # Lower confidence for basic recommendation
            "strengths": ["Research data available", "Basic analysis completed"],
            "weaknesses": ["Limited AI analysis", "Manual review recommended"],
            "considerations": ["Detailed analysis requires manual review"],
            "suitability_analysis": "Basic suitability assessment - detailed review recommended",
            "risk_assessment": "Standard risk considerations apply",
            "alignment_score": base_score,
            "scoring_rationale": "Basic scoring due to analysis limitations"
        }
    
    def _generate_fallback_recommendation(self, stock_research: Dict[str, Any], user_profile: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Generate fallback recommendation when the main process fails."""
        return {
            "symbol": stock_research.get("symbol", "Unknown"),
            "company_name": stock_research.get("company_name", "Unknown"),
            "recommendation_timestamp": datetime.now().isoformat(),
            "score": 50,
            "sentiment": "Hold",
            "confidence": 0.2,
            "strengths": ["Research data available for manual review"],
            "weaknesses": ["Automated analysis failed", "Manual review required"],
            "considerations": ["System error occurred", "Consult financial advisor"],
            "suitability_analysis": "Unable to assess suitability due to system error",
            "risk_assessment": "Standard risk assessment unavailable",
            "alignment_score": 50,
            "scoring_breakdown": {"error": f"Analysis failed: {error}"},
            "action_plan": {"primary_action": "Manual analysis recommended"},
            "error": error
        }


# Example usage and testing
async def main():
    """Test the Stock Recommendation Agent"""
    try:
        # Initialize agent
        agent = StockRecommendationAgent()
        
        # Mock stock research data
        mock_research = {
            "symbol": "TCS.NS",
            "company_name": "Tata Consultancy Services",
            "synthesis": {
                "investment_thesis": "Strong IT services leader with consistent performance",
                "conviction_level": 8
            },
            "research_areas": {
                "technical_analysis": {"confidence": 0.8},
                "fundamental_analysis": {"confidence": 0.9},
                "market_sentiment": {"confidence": 0.7}
            },
            "metadata": {"total_sources": 15, "average_confidence": 0.8}
        }
        
        # Mock user profile
        mock_profile = {
            "riskTolerance": "moderate",
            "investmentHorizon": "long",
            "investmentGoal": "growth",
            "monthlyInvestment": 25000
        }
        
        # Mock stock data
        mock_stock_data = {
            "currentPrice": 3500,
            "marketCap": "13.5L Cr"
        }
        
        print("🚀 Testing Stock Recommendation Agent...")
        result = await agent.generate_recommendation(mock_research, mock_profile, mock_stock_data)
        
        print(f"\n📊 RECOMMENDATION RESULTS:")
        print(f"Score: {result['score']}/100")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Alignment Score: {result['alignment_score']}/100")
        
        print(f"\n🎯 ACTION PLAN:")
        print(f"Primary Action: {result['action_plan']['primary_action']}")
        print(f"Investment Amount: {result['action_plan']['investment_amount']}")
        
        print(f"\n✅ TOP STRENGTHS:")
        for strength in result['strengths'][:3]:
            print(f"  • {strength}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())