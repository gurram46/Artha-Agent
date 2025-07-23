"""
Integrated Stock Analysis Agent - Simplified for main server integration
Provides stock research and recommendations directly in the main Artha AI backend.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from google import genai
from google.genai import types
from config.settings import config


class StockAnalysisAgent:
    """
    Integrated Stock Analysis Agent that combines research and recommendations.
    Designed to work within the main Artha AI backend system.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the Stock Analysis Agent."""
        self.api_key = api_key or config.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google AI API key is required for stock analysis")
            
        # Initialize Gemini client (using the same pattern as other agents)
        self.client = genai.Client(api_key=self.api_key)
        
        self.name = "Stock Analysis Specialist"
        self.personality = "analytical stock expert, data-driven, provides clear actionable insights"
        
        # Configure grounding tool for research
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        # Generation config for stock analysis
        self.research_config = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            temperature=0.3,
            max_output_tokens=3000
        )
        
        self.recommendation_config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2000
        )
    
    async def analyze_stock_full(self, symbol: str, company_name: str, user_profile: Dict, stock_data: Dict) -> Dict[str, Any]:
        """
        Perform complete stock analysis including research and personalized recommendation.
        
        Args:
            symbol: Stock symbol (e.g., 'TCS.NS')
            company_name: Company name for better research
            user_profile: User investment profile
            stock_data: Current stock data (price, market cap, etc.)
            
        Returns:
            Complete analysis with research and recommendation
        """
        print(f"🔍 Starting full stock analysis for {symbol}...")
        
        try:
            # Step 1: Research the stock
            research_data = await self._research_stock(symbol, company_name)
            
            # Step 2: Generate personalized recommendation
            recommendation = await self._generate_recommendation(
                symbol, company_name, research_data, user_profile, stock_data
            )
            
            return {
                "symbol": symbol,
                "company_name": company_name,
                "research": research_data,
                "recommendation": recommendation,
                "user_profile": user_profile,
                "analysis_timestamp": datetime.now().isoformat(),
                "summary": {
                    "score": recommendation.get("score", 50),
                    "sentiment": recommendation.get("sentiment", "Hold"),
                    "confidence": recommendation.get("confidence", 0.7),
                    "research_quality": {
                        "sources_count": len(research_data.get("sources", [])),
                        "analysis_depth": "comprehensive" if len(research_data.get("key_insights", [])) >= 5 else "basic"
                    }
                }
            }
            
        except Exception as e:
            print(f"❌ Error in full stock analysis: {e}")
            # Return fallback analysis
            return await self._generate_fallback_analysis(symbol, company_name, user_profile, stock_data)
    
    async def _research_stock(self, symbol: str, company_name: str) -> Dict[str, Any]:
        """Research stock using Google Grounding."""
        try:
            clean_symbol = symbol.replace('.NS', '').replace('.BSE', '')
            
            # Comprehensive research query
            research_query = f"""
            Research {company_name} ({clean_symbol}) stock for investment analysis. Provide:
            
            1. Recent financial performance and key metrics
            2. Current market sentiment and analyst opinions
            3. Technical analysis indicators and price trends
            4. Key business developments and growth prospects
            5. Major risks and challenges
            6. Competitive position in the industry
            7. Investment highlights and concerns
            
            Focus on recent data from 2024-2025 and provide specific numbers where available.
            """
            
            print(f"🔍 Researching {company_name}...")
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=research_query,
                config=self.research_config
            )
            
            research_text = response.text if hasattr(response, 'text') else str(response)
            
            # Extract sources and metadata
            sources = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    chunks = candidate.grounding_metadata.grounding_chunks or []
                    sources = [
                        {
                            "title": chunk.web.title if hasattr(chunk, 'web') else "Market Data",
                            "url": chunk.web.uri if hasattr(chunk, 'web') else "N/A"
                        }
                        for chunk in chunks
                    ]
            
            # Extract key insights
            key_insights = self._extract_key_insights(research_text)
            
            return {
                "analysis": research_text,
                "key_insights": key_insights,
                "sources": sources,
                "confidence": min(0.9, 0.5 + len(sources) * 0.1),
                "research_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Research failed: {e}")
            return {
                "analysis": f"Research unavailable: {str(e)}",
                "key_insights": [
                    "Unable to fetch current market data",
                    "Manual research recommended",
                    "Consider multiple sources for analysis"
                ],
                "sources": [],
                "confidence": 0.2,
                "research_timestamp": datetime.now().isoformat()
            }
    
    async def _generate_recommendation(self, symbol: str, company_name: str, research_data: Dict, 
                                     user_profile: Dict, stock_data: Dict) -> Dict[str, Any]:
        """Generate personalized investment recommendation."""
        try:
            # Prepare user profile context
            risk_tolerance = user_profile.get("riskTolerance", "moderate")
            investment_horizon = user_profile.get("investmentHorizon", "medium")
            investment_goal = user_profile.get("investmentGoal", "balanced")
            monthly_investment = user_profile.get("monthlyInvestment", 10000)
            
            current_price = stock_data.get("currentPrice", 0)
            
            recommendation_prompt = f"""
            As an expert investment advisor, analyze {company_name} ({symbol}) for a specific investor profile:
            
            STOCK RESEARCH:
            {research_data.get('analysis', 'No research available')[:1500]}
            
            Key Insights:
            {chr(10).join(['• ' + insight for insight in research_data.get('key_insights', [])])}
            
            CURRENT STOCK DATA:
            - Current Price: ₹{current_price}
            - Market Cap: {stock_data.get('marketCap', 'N/A')}
            - Sector: {stock_data.get('sector', 'Unknown')}
            
            USER INVESTMENT PROFILE:
            - Risk Tolerance: {risk_tolerance}
            - Investment Horizon: {investment_horizon}
            - Investment Goal: {investment_goal}
            - Monthly Investment Budget: ₹{monthly_investment:,}
            
            Provide a personalized investment recommendation with:
            
            1. RECOMMENDATION SCORE (0-100): Based on research quality and user suitability
            2. INVESTMENT SENTIMENT: Strong Buy/Buy/Hold/Sell/Strong Sell
            3. KEY STRENGTHS (3-5 points): Why this stock is good for this investor
            4. KEY CONCERNS (3-5 points): Risks and limitations for this investor
            5. INVESTMENT CONSIDERATIONS (3-5 points): Important factors to monitor
            6. CONFIDENCE LEVEL (0.0-1.0): How confident you are in this recommendation
            7. SUGGESTED ALLOCATION: How much to invest given their budget
            8. REASONING: 2-3 sentence explanation of the recommendation
            
            Consider the user's risk tolerance and investment horizon carefully in your analysis.
            """
            
            print(f"🎯 Generating recommendation for {company_name}...")
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=recommendation_prompt,
                config=self.recommendation_config
            )
            
            recommendation_text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse structured recommendation
            parsed_rec = self._parse_recommendation(recommendation_text)
            
            return {
                "score": parsed_rec.get("score", 50),
                "sentiment": parsed_rec.get("sentiment", "Hold"),
                "strengths": parsed_rec.get("strengths", []),
                "weaknesses": parsed_rec.get("concerns", []),
                "considerations": parsed_rec.get("considerations", []),
                "confidence": parsed_rec.get("confidence", 0.7),
                "suggested_allocation": parsed_rec.get("allocation", f"₹{min(monthly_investment, 5000):,}"),
                "reasoning": parsed_rec.get("reasoning", "Analysis based on available data and user profile."),
                "alignment_score": self._calculate_alignment_score(user_profile, parsed_rec.get("score", 50)),
                "action_plan": {
                    "primary_action": parsed_rec.get("sentiment", "Hold"),
                    "suggested_amount": min(monthly_investment, 10000),
                    "timeframe": investment_horizon,
                    "monitoring_points": parsed_rec.get("considerations", [])[:3]
                },
                "scoring_breakdown": {
                    "components": {
                        "technical_score": min(100, parsed_rec.get("score", 50) + 10),
                        "fundamental_score": parsed_rec.get("score", 50),
                        "market_sentiment_score": min(100, parsed_rec.get("score", 50) - 5),
                        "risk_alignment_score": self._calculate_alignment_score(user_profile, parsed_rec.get("score", 50))
                    }
                },
                "full_analysis": recommendation_text,
                "recommendation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Recommendation generation failed: {e}")
            return self._generate_basic_recommendation(symbol, user_profile, stock_data)
    
    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights from research text."""
        insights = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith(('•', '-', '*')) or 
                (len(line) > 15 and any(char.isdigit() for char in line[:3]) and '.' in line[:3])):
                cleaned = line.lstrip('•-*0123456789. ').strip()
                if len(cleaned) > 20:
                    insights.append(cleaned)
        
        # If no bullet points, extract meaningful sentences
        if not insights:
            sentences = text.split('.')
            for sentence in sentences[:8]:
                sentence = sentence.strip()
                if (len(sentence) > 25 and 
                    any(keyword in sentence.lower() for keyword in 
                        ['revenue', 'profit', 'growth', 'margin', 'debt', 'strong', 'weak', 'outlook', 'performance'])):
                    insights.append(sentence)
        
        return insights[:7]
    
    def _parse_recommendation(self, text: str) -> Dict[str, Any]:
        """Parse structured recommendation from AI response."""
        parsed = {
            "score": 50,
            "sentiment": "Hold",
            "strengths": [],
            "concerns": [],
            "considerations": [],
            "confidence": 0.7,
            "allocation": "₹5,000",
            "reasoning": ""
        }
        
        try:
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                line_lower = line.lower()
                
                # Extract score
                if 'score' in line_lower and any(char.isdigit() for char in line):
                    numbers = [int(s) for s in line.split() if s.isdigit()]
                    if numbers:
                        parsed["score"] = min(100, max(0, numbers[0]))
                
                # Extract sentiment
                if 'sentiment' in line_lower or 'recommendation' in line_lower:
                    if 'strong buy' in line_lower:
                        parsed["sentiment"] = "Strong Buy"
                    elif 'buy' in line_lower:
                        parsed["sentiment"] = "Buy" 
                    elif 'hold' in line_lower:
                        parsed["sentiment"] = "Hold"
                    elif 'sell' in line_lower:
                        parsed["sentiment"] = "Sell"
                    elif 'strong sell' in line_lower:
                        parsed["sentiment"] = "Strong Sell"
                
                # Extract confidence
                if 'confidence' in line_lower:
                    try:
                        # Look for decimal numbers
                        parts = line.replace(',', '.').split()
                        for part in parts:
                            if '.' in part:
                                num = float(part)
                                if 0 <= num <= 1:
                                    parsed["confidence"] = num
                                    break
                                elif 0 <= num <= 100:
                                    parsed["confidence"] = num / 100
                                    break
                    except:
                        pass
                
                # Identify sections
                if 'strengths' in line_lower or 'positives' in line_lower:
                    current_section = 'strengths'
                elif 'concerns' in line_lower or 'risks' in line_lower or 'weaknesses' in line_lower:
                    current_section = 'concerns'
                elif 'considerations' in line_lower or 'factors' in line_lower:
                    current_section = 'considerations'
                elif 'reasoning' in line_lower or 'explanation' in line_lower:
                    current_section = 'reasoning'
                elif current_section and line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                    # Add bullet point to current section
                    cleaned = line.lstrip('•-*0123456789. ').strip()
                    if len(cleaned) > 10 and current_section in ['strengths', 'concerns', 'considerations']:
                        parsed[current_section].append(cleaned)
                elif current_section == 'reasoning' and len(line) > 20:
                    parsed["reasoning"] += line + " "
            
            # Clean up reasoning
            parsed["reasoning"] = parsed["reasoning"].strip()
            if not parsed["reasoning"]:
                parsed["reasoning"] = f"Recommendation based on analysis of {parsed['score']}/100 score with {parsed['sentiment']} sentiment."
            
        except Exception as e:
            print(f"⚠️ Error parsing recommendation: {e}")
        
        return parsed
    
    def _calculate_alignment_score(self, user_profile: Dict, base_score: int) -> int:
        """Calculate how well the stock aligns with user profile."""
        risk_tolerance = user_profile.get("riskTolerance", "moderate")
        investment_horizon = user_profile.get("investmentHorizon", "medium")
        
        alignment = base_score
        
        # Adjust for risk tolerance
        if risk_tolerance == "conservative" and base_score > 70:
            alignment -= 10  # High scores may be too risky for conservative investors
        elif risk_tolerance == "aggressive" and base_score < 50:
            alignment += 10  # Low scores might be acceptable for aggressive investors
        
        # Adjust for investment horizon
        if investment_horizon == "long" and base_score >= 60:
            alignment += 5  # Long-term investors can handle more volatility
        elif investment_horizon == "short" and base_score > 80:
            alignment -= 10  # Short-term investors need more stability
        
        return min(100, max(0, alignment))
    
    def _generate_basic_recommendation(self, symbol: str, user_profile: Dict, stock_data: Dict) -> Dict[str, Any]:
        """Generate a basic recommendation when AI analysis fails."""
        base_score = 50
        sentiment = "Hold"
        
        # Simple rules based on user profile
        risk_tolerance = user_profile.get("riskTolerance", "moderate")
        
        if risk_tolerance == "conservative":
            base_score = 45
            sentiment = "Hold"
        elif risk_tolerance == "aggressive":
            base_score = 60
            sentiment = "Buy"
        
        return {
            "score": base_score,
            "sentiment": sentiment,
            "strengths": [
                "Established company in the market",
                "Part of major Indian stock indices"
            ],
            "weaknesses": [
                "Limited analysis available",
                "Requires manual research"
            ],
            "considerations": [
                "Monitor quarterly results",
                "Review sector trends",
                "Consider broader market conditions"
            ],
            "confidence": 0.4,
            "suggested_allocation": f"₹{min(user_profile.get('monthlyInvestment', 10000), 5000):,}",
            "reasoning": "Basic recommendation due to limited analysis capabilities.",
            "alignment_score": base_score,
            "action_plan": {
                "primary_action": sentiment,
                "suggested_amount": 5000,
                "timeframe": user_profile.get("investmentHorizon", "medium"),
                "monitoring_points": ["Quarterly results", "Sector performance", "Market conditions"]
            },
            "scoring_breakdown": {
                "components": {
                    "technical_score": base_score,
                    "fundamental_score": base_score,
                    "market_sentiment_score": base_score,
                    "risk_alignment_score": base_score
                }
            },
            "full_analysis": "Basic analysis - AI research unavailable",
            "recommendation_timestamp": datetime.now().isoformat()
        }
    
    async def _generate_fallback_analysis(self, symbol: str, company_name: str, 
                                        user_profile: Dict, stock_data: Dict) -> Dict[str, Any]:
        """Generate fallback analysis when everything fails."""
        basic_recommendation = self._generate_basic_recommendation(symbol, user_profile, stock_data)
        
        return {
            "symbol": symbol,
            "company_name": company_name,
            "research": {
                "analysis": "Research services temporarily unavailable",
                "key_insights": [
                    "Manual research recommended",
                    "Check multiple financial sources",
                    "Consider consulting with financial advisor"
                ],
                "sources": [],
                "confidence": 0.2,
                "research_timestamp": datetime.now().isoformat()
            },
            "recommendation": basic_recommendation,
            "user_profile": user_profile,
            "analysis_timestamp": datetime.now().isoformat(),
            "summary": {
                "score": basic_recommendation["score"],
                "sentiment": basic_recommendation["sentiment"],
                "confidence": 0.4,
                "research_quality": {
                    "sources_count": 0,
                    "analysis_depth": "basic"
                }
            }
        }


# Initialize the stock analysis agent when module is imported
stock_analyst = None

def get_stock_analyst() -> StockAnalysisAgent:
    """Get or create the stock analysis agent instance."""
    global stock_analyst
    if stock_analyst is None:
        try:
            stock_analyst = StockAnalysisAgent()
            print("📈 Stock Analysis Agent initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize Stock Analysis Agent: {e}")
            print("💡 Set GOOGLE_API_KEY environment variable to enable stock analysis")
            stock_analyst = None
    return stock_analyst


# Test function
async def test_stock_agent():
    """Test the stock analysis agent."""
    try:
        agent = get_stock_analyst()
        if not agent:
            print("❌ Stock agent not available")
            return
        
        # Test analysis
        result = await agent.analyze_stock_full(
            symbol="TCS.NS",
            company_name="Tata Consultancy Services",
            user_profile={
                "riskTolerance": "moderate",
                "investmentHorizon": "long",
                "investmentGoal": "growth",
                "monthlyInvestment": 25000
            },
            stock_data={
                "currentPrice": 3500,
                "marketCap": "13.5L Cr",
                "sector": "Information Technology"
            }
        )
        
        print("✅ Stock analysis test completed")
        print(f"Score: {result['summary']['score']}")
        print(f"Sentiment: {result['summary']['sentiment']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_stock_agent())