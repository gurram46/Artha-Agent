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
    
    async def analyze_stock_full(self, symbol: str, company_name: str, user_profile: Dict, stock_data: Dict, log_callback=None) -> Dict[str, Any]:
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
        
        # Real-time logging function
        async def log(message):
            if log_callback:
                await log_callback(message)
        
        try:
            # Step 1: Research the stock
            await log(f"📊 Researching {company_name} fundamentals...")
            research_data = await self._research_stock(symbol, company_name, log_callback)
            
            # Step 2: Generate personalized recommendation  
            await log(f"🧠 Generating personalized investment recommendation...")
            recommendation = await self._generate_recommendation(
                symbol, company_name, research_data, user_profile, stock_data, log_callback
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
            import traceback
            print("Full traceback:")
            traceback.print_exc()
            # Return a proper error response instead of raising
            return {
                "symbol": symbol,
                "company_name": company_name,
                "research": {
                    "analysis": f"Analysis failed: {str(e)}",
                    "key_insights": [],
                    "sources": [],
                    "confidence": 0.0,
                    "research_timestamp": datetime.now().isoformat()
                },
                "recommendation": {
                    "score": 0,
                    "sentiment": "Error",
                    "strengths": [],
                    "weaknesses": [],
                    "considerations": [],
                    "confidence": 0.0,
                    "reasoning": f"Analysis failed: {str(e)}",
                    "full_analysis": f"Error: {str(e)}",
                    "recommendation_timestamp": datetime.now().isoformat()
                },
                "user_profile": user_profile,
                "analysis_timestamp": datetime.now().isoformat(),
                "summary": {
                    "score": 0,
                    "sentiment": "Error",
                    "confidence": 0.0,
                    "research_quality": {
                        "sources_count": 0,
                        "analysis_depth": "failed"
                    }
                }
            }
    
    async def _research_stock(self, symbol: str, company_name: str, log_callback=None) -> Dict[str, Any]:
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
            
            # Real-time logging function
            async def log(message):
                if log_callback:
                    await log_callback(message)
            
            await log(f"🔍 Analyzing market data for {company_name}...")
            
            # Use higher token limit to avoid truncation
            simple_research_config = types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=4000
            )
            
            await log(f"🤖 Querying Gemini AI for research insights...")
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=research_query,
                config=simple_research_config
            )
            
            # Extract text from response
            research_text = None
            if hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts and len(candidate.content.parts) > 0:
                        research_text = candidate.content.parts[0].text
            
            # Fallback methods
            if not research_text and hasattr(response, 'text') and response.text:
                research_text = response.text
                
            if not research_text:
                research_text = f"Research failed: Unable to extract response text"
                print(f"⚠️ Failed to extract research text from response: {type(response)}")
            
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
            
            await log(f"📈 Extracting key insights from research data...")
            
            # Extract key insights
            key_insights = self._extract_key_insights(research_text)
            
            await log(f"✅ Research completed - found {len(key_insights)} key insights")
            
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
                                     user_profile: Dict, stock_data: Dict, log_callback=None) -> Dict[str, Any]:
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
            
            CRITICAL: Format your response EXACTLY as follows (use these exact headers and markdown formatting):
            
            RECOMMENDATION SCORE: [number 0-100]
            
            INVESTMENT SENTIMENT: [Strong Buy/Buy/Hold/Sell/Strong Sell]
            
            KEY STRENGTHS:
            • **[Strength Title]:** [detailed explanation with specific data and metrics]
            • **[Strength Title]:** [detailed explanation with specific data and metrics]
            • **[Strength Title]:** [detailed explanation with specific data and metrics]
            • **[Strength Title]:** [detailed explanation with specific data and metrics]
            
            KEY CONCERNS:
            • **[Concern Title]:** [detailed explanation with specific risks and challenges]
            • **[Concern Title]:** [detailed explanation with specific risks and challenges]
            • **[Concern Title]:** [detailed explanation with specific risks and challenges]
            • **[Concern Title]:** [detailed explanation with specific risks and challenges]
            
            INVESTMENT CONSIDERATIONS:
            • **[Consideration Title]:** [detailed actionable advice with specific recommendations]
            • **[Consideration Title]:** [detailed actionable advice with specific recommendations]
            • **[Consideration Title]:** [detailed actionable advice with specific recommendations]
            
            CONFIDENCE LEVEL: [0.0-1.0]
            
            REASONING: [2-3 sentence explanation]
            
            IMPORTANT: Use **bold** markdown formatting for titles in each bullet point. Be specific and detailed in your strengths, concerns, and considerations. Each point should be actionable and relevant to this specific stock and investor profile.
            """
            
            print(f"🎯 Generating recommendation for {company_name}...")
            
            # Real-time logging function
            async def log(message):
                if log_callback:
                    await log_callback(message)
            
            await log(f"⚖️ Analyzing investment risks and opportunities...")
            await log(f"🎯 Matching analysis with your {risk_tolerance} risk profile...")
            
            # Use higher token limit to avoid truncation
            simple_config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=4000
            )
            
            await log(f"🤖 Generating AI recommendation with Gemini 2.5...")
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=recommendation_prompt,
                config=simple_config
            )
            
            # DEBUG: Check for safety issues or other problems
            print(f"🔍 Full response: {response}")
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    print(f"🔍 Finish reason: {candidate.finish_reason}")
                if hasattr(candidate, 'safety_ratings'):
                    print(f"🔍 Safety ratings: {candidate.safety_ratings}")
                if hasattr(candidate, 'content') and candidate.content:
                    print(f"🔍 Content parts: {candidate.content.parts}")
            
            # Extract text from response 
            recommendation_text = None
            if hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                    if len(candidate.content.parts) > 0 and hasattr(candidate.content.parts[0], 'text'):
                        recommendation_text = candidate.content.parts[0].text
            
            # Fallback methods
            if not recommendation_text and hasattr(response, 'text') and response.text:
                recommendation_text = response.text
                
            if not recommendation_text:
                # Try to understand why the response is empty
                error_msg = f"AI response is empty. "
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        error_msg += f"Finish reason: {candidate.finish_reason}. "
                    if hasattr(candidate, 'safety_ratings'):
                        error_msg += f"Safety ratings: {candidate.safety_ratings}. "
                error_msg += f"Response type: {type(response)}"
                raise Exception(error_msg)
            
            # DEBUG: Log the extracted text
            print(f"🤖 Raw AI response for {company_name}:")
            print("="*80)
            print(recommendation_text)
            print("="*80)
            
            await log(f"📊 Parsing AI recommendation structure...")
            
            # Parse structured recommendation
            parsed_rec = self._parse_recommendation(recommendation_text)
            
            await log(f"✅ Analysis complete! Generated {parsed_rec.get('sentiment', 'Hold')} recommendation with {parsed_rec.get('score', 50)}/100 score")
            
            # DEBUG: Log the parsed results
            print(f"📊 Parsed recommendation for {company_name}:")
            print(f"   Score: {parsed_rec.get('score', 'N/A')}")
            print(f"   Sentiment: {parsed_rec.get('sentiment', 'N/A')}")
            print(f"   Strengths ({len(parsed_rec.get('strengths', []))}): {parsed_rec.get('strengths', [])}")
            print(f"   Concerns ({len(parsed_rec.get('concerns', []))}): {parsed_rec.get('concerns', [])}")
            print(f"   Considerations ({len(parsed_rec.get('considerations', []))}): {parsed_rec.get('considerations', [])}")
            print("="*80)
            
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
            import traceback
            print("Full traceback for recommendation generation:")
            traceback.print_exc()
            
            # Return error instead of basic recommendation
            return {
                "score": 0,
                "sentiment": "Error",
                "strengths": [],
                "weaknesses": [],
                "considerations": [],
                "confidence": 0.0,
                "reasoning": f"Recommendation generation failed: {str(e)}",
                "full_analysis": f"Error in recommendation: {str(e)}",
                "recommendation_timestamp": datetime.now().isoformat()
            }
    
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
                if line_lower.startswith('recommendation score:'):
                    numbers = [int(s) for s in line.split() if s.isdigit()]
                    if numbers:
                        parsed["score"] = min(100, max(0, numbers[0]))
                
                # Extract sentiment
                elif line_lower.startswith('investment sentiment:'):
                    if 'strong buy' in line_lower:
                        parsed["sentiment"] = "Strong Buy"
                    elif 'strong sell' in line_lower:
                        parsed["sentiment"] = "Strong Sell"
                    elif 'buy' in line_lower:
                        parsed["sentiment"] = "Buy"
                    elif 'sell' in line_lower:
                        parsed["sentiment"] = "Sell"
                    elif 'hold' in line_lower:
                        parsed["sentiment"] = "Hold"
                
                # Extract confidence
                elif line_lower.startswith('confidence level:'):
                    try:
                        # Look for decimal numbers
                        parts = line.replace(',', '.').split()
                        for part in parts:
                            try:
                                num = float(part)
                                if 0 <= num <= 1:
                                    parsed["confidence"] = num
                                    break
                                elif 0 <= num <= 100:
                                    parsed["confidence"] = num / 100
                                    break
                            except ValueError:
                                continue
                    except:
                        pass
                
                # Handle section headers
                elif line_lower.startswith('key strengths:'):
                    current_section = 'strengths'
                elif line_lower.startswith('key concerns:'):
                    current_section = 'concerns'
                elif line_lower.startswith('investment considerations:'):
                    current_section = 'considerations'
                elif line_lower.startswith('reasoning:'):
                    current_section = 'reasoning'
                    # Also capture the reasoning on the same line
                    reasoning_text = line[len('reasoning:'):].strip()
                    if reasoning_text:
                        parsed["reasoning"] = reasoning_text
                
                # Handle bullet points
                elif current_section and line.startswith('•'):
                    cleaned = line.lstrip('• ').strip()
                    if len(cleaned) > 5 and current_section in ['strengths', 'concerns', 'considerations']:
                        parsed[current_section].append(cleaned)
                
                # Handle multi-line reasoning
                elif current_section == 'reasoning' and len(line) > 10 and not line.lower().startswith(('key ', 'investment ', 'recommendation ', 'confidence ')):
                    if parsed["reasoning"]:
                        parsed["reasoning"] += " " + line
                    else:
                        parsed["reasoning"] = line
            
            # Clean up reasoning
            parsed["reasoning"] = parsed["reasoning"].strip()
            if not parsed["reasoning"]:
                parsed["reasoning"] = f"Recommendation based on analysis with {parsed['score']}/100 score and {parsed['sentiment']} sentiment."
            
            # Debug output
            print(f"🔍 Parsing results:")
            print(f"   - Score: {parsed['score']}")
            print(f"   - Sentiment: {parsed['sentiment']}")
            print(f"   - Strengths found: {len(parsed['strengths'])}")  
            print(f"   - Concerns found: {len(parsed['concerns'])}")
            print(f"   - Considerations found: {len(parsed['considerations'])}")
            print(f"   - Confidence: {parsed['confidence']}")
            
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
        """Generate a basic recommendation when AI analysis fails - should be avoided."""
        print("⚠️ WARNING: Using basic recommendation - AI analysis failed!")
        
        return {
            "score": 50,
            "sentiment": "Hold",
            "strengths": [],  # No hardcoded data
            "weaknesses": [],  # No hardcoded data
            "considerations": [],  # No hardcoded data
            "confidence": 0.3,
            "suggested_allocation": "₹0",
            "reasoning": "AI analysis failed - please try again later.",
            "alignment_score": 50,
            "action_plan": {
                "primary_action": "Hold",
                "suggested_amount": 0,
                "timeframe": user_profile.get("investmentHorizon", "medium"),
                "monitoring_points": []
            },
            "scoring_breakdown": {
                "components": {
                    "technical_score": 50,
                    "fundamental_score": 50,
                    "market_sentiment_score": 50,
                    "risk_alignment_score": 50
                }
            },
            "full_analysis": "AI analysis unavailable",
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


# Disabled to prevent interference with main server
# if __name__ == "__main__":
#     asyncio.run(test_stock_agent())