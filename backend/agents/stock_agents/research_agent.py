"""
Stock Research Agent - Comprehensive market intelligence gathering using Google Grounding

This agent specializes in collecting comprehensive research data about individual stocks
using Google Search Grounding to access real-time market information, news, and analysis.
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from google import genai
from google.genai import types
from core.google_grounding.grounding_client import GroundingClient


class StockResearchAgent:
    """
    Specialized AI agent for comprehensive stock research using Google Grounding.
    
    This agent performs deep market intelligence gathering including:
    - Technical analysis signals and patterns
    - Fundamental metrics and financial health
    - Market sentiment and news analysis  
    - Sector trends and competitive positioning
    - Management quality and governance
    - Future growth prospects and catalysts
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the Stock Research Agent with Google Grounding capabilities."""
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API key is required")
            
        # Initialize Gemini client
        genai.configure(api_key=self.api_key)
        self.client = genai.Client()
        
        # Initialize grounding client
        self.grounding_client = GroundingClient(api_key=self.api_key)
        
        # Configure grounding tool
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        # Generation config for research
        self.config = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            temperature=0.3,  # Lower temperature for more factual research
            max_output_tokens=4000
        )
        
    async def research_stock_comprehensive(self, symbol: str, company_name: str = None) -> Dict[str, Any]:
        """
        Perform comprehensive stock research using multiple specialized search queries.
        
        Args:
            symbol: Stock symbol (e.g., 'TCS.NS', 'RELIANCE.NS')
            company_name: Optional company name for better search results
            
        Returns:
            Comprehensive research report with all analysis areas
        """
        print(f"🔍 Starting comprehensive research for {symbol}...")
        
        # Extract clean symbol and company info
        clean_symbol = symbol.replace('.NS', '').replace('.BSE', '')
        if not company_name:
            company_name = self._get_company_name(clean_symbol)
        
        # Define specialized research queries
        research_queries = [
            {
                "area": "technical_analysis",
                "query": f"{company_name} {clean_symbol} stock technical analysis chart patterns RSI MACD moving averages support resistance levels 2024 2025",
                "focus": "Technical indicators, chart patterns, price action analysis"
            },
            {
                "area": "fundamental_analysis", 
                "query": f"{company_name} {clean_symbol} financial results Q3 2024 Q4 2024 revenue profit margin PE ratio debt equity ROE earnings growth",
                "focus": "Financial metrics, valuation ratios, earnings quality"
            },
            {
                "area": "market_sentiment",
                "query": f"{company_name} {clean_symbol} stock news analyst ratings buy sell hold recommendations price targets recent developments 2024",
                "focus": "Market sentiment, analyst opinions, recent news"
            },
            {
                "area": "sector_analysis",
                "query": f"{company_name} sector industry trends market outlook competition competitive advantages moats industry growth 2024 2025",
                "focus": "Sector dynamics, competitive positioning, industry trends"
            },
            {
                "area": "management_governance",
                "query": f"{company_name} management team CEO leadership corporate governance board quality strategic vision execution track record",
                "focus": "Management quality, governance practices, strategic direction"
            },
            {
                "area": "growth_prospects",
                "query": f"{company_name} future growth prospects business expansion new projects order book guidance outlook 2024 2025 2026",
                "focus": "Growth catalysts, future opportunities, business expansion"
            },
            {
                "area": "risk_factors",
                "query": f"{company_name} {clean_symbol} risks challenges regulatory issues debt concerns market risks sector headwinds competition threats",
                "focus": "Risk assessment, potential challenges, headwinds"
            }
        ]
        
        # Execute research queries concurrently
        research_results = {}
        tasks = []
        
        for query_info in research_queries:
            task = self._execute_research_query(
                query_info["query"], 
                query_info["area"], 
                query_info["focus"]
            )
            tasks.append(task)
        
        # Wait for all research to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"⚠️ Research query {research_queries[i]['area']} failed: {result}")
                research_results[research_queries[i]['area']] = {
                    "analysis": "Research failed - using fallback analysis",
                    "key_points": [],
                    "sources": [],
                    "confidence": 0.1
                }
            else:
                research_results[research_queries[i]['area']] = result
        
        # Generate comprehensive synthesis
        synthesis = await self._synthesize_research(research_results, symbol, company_name)
        
        return {
            "symbol": symbol,
            "company_name": company_name,
            "research_timestamp": datetime.now().isoformat(),
            "research_areas": research_results,
            "synthesis": synthesis,
            "metadata": {
                "total_sources": sum(len(r.get("sources", [])) for r in research_results.values()),
                "research_queries_count": len(research_queries),
                "average_confidence": sum(r.get("confidence", 0) for r in research_results.values()) / len(research_queries)
            }
        }
    
    async def _execute_research_query(self, query: str, area: str, focus: str) -> Dict[str, Any]:
        """Execute a single research query with Google Grounding."""
        try:
            print(f"  🔍 Researching {area}...")
            
            # Create detailed prompt for the specific research area
            prompt = f"""
            As a professional stock market research analyst, conduct comprehensive research on: {focus}

            Search Query: {query}

            Please provide:
            1. Key findings and insights from current market data
            2. 5-7 specific bullet points with actionable information
            3. Current trends and patterns identified
            4. Quantitative data where available (numbers, percentages, ratios)
            5. Recent developments and their implications
            6. Overall assessment with confidence level

            Focus on factual, recent, and actionable insights. Cite specific sources and data points.
            """
            
            # Execute grounded search
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=self.config
            )
            
            # Extract grounding metadata
            sources = []
            confidence = 0.8  # Default confidence
            
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    # Extract sources from grounding metadata
                    chunks = candidate.grounding_metadata.grounding_chunks or []
                    sources = [
                        {
                            "title": chunk.web.title if hasattr(chunk, 'web') else "Unknown",
                            "url": chunk.web.uri if hasattr(chunk, 'web') else "Unknown"
                        }
                        for chunk in chunks
                    ]
                    
                    # Calculate confidence based on number and quality of sources
                    if len(sources) >= 5:
                        confidence = 0.9
                    elif len(sources) >= 3:
                        confidence = 0.8
                    elif len(sources) >= 1:
                        confidence = 0.6
                    else:
                        confidence = 0.3
            
            # Parse key points from response
            analysis_text = response.text if hasattr(response, 'text') else str(response)
            key_points = self._extract_key_points(analysis_text)
            
            return {
                "analysis": analysis_text,
                "key_points": key_points,
                "sources": sources,
                "confidence": confidence,
                "research_area": area,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error in research query for {area}: {e}")
            return {
                "analysis": f"Research failed for {area}: {str(e)}",
                "key_points": [],
                "sources": [],
                "confidence": 0.1,
                "research_area": area,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _synthesize_research(self, research_results: Dict[str, Any], symbol: str, company_name: str) -> Dict[str, Any]:
        """Synthesize all research areas into a comprehensive assessment."""
        try:
            # Prepare synthesis prompt
            research_summary = []
            for area, result in research_results.items():
                research_summary.append(f"{area.replace('_', ' ').title()}:")
                research_summary.append(f"- Analysis: {result.get('analysis', 'N/A')[:500]}...")
                research_summary.append(f"- Confidence: {result.get('confidence', 0.0):.1f}")
                research_summary.append("")
            
            synthesis_prompt = f"""
            As a senior equity research analyst, synthesize the following comprehensive research on {company_name} ({symbol}) into a final investment perspective:

            RESEARCH FINDINGS:
            {chr(10).join(research_summary)}

            Please provide:
            1. OVERALL INVESTMENT THESIS (2-3 sentences)
            2. KEY STRENGTHS (3-4 bullet points)
            3. MAJOR CONCERNS (3-4 bullet points) 
            4. CRITICAL FACTORS TO MONITOR (3-4 bullet points)
            5. INVESTMENT SUITABILITY (who should consider this stock)
            6. OVERALL CONVICTION LEVEL (1-10 scale with reasoning)

            Be objective, balanced, and focus on actionable insights for investment decisions.
            """
            
            # Generate synthesis
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash", 
                contents=synthesis_prompt,
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=1500)
            )
            
            synthesis_text = response.text if hasattr(response, 'text') else str(response)
            
            # Extract structured insights
            structured_insights = self._parse_synthesis(synthesis_text)
            
            return {
                "investment_thesis": structured_insights.get("thesis", ""),
                "key_strengths": structured_insights.get("strengths", []),
                "major_concerns": structured_insights.get("concerns", []),
                "critical_factors": structured_insights.get("factors", []),
                "investment_suitability": structured_insights.get("suitability", ""),
                "conviction_level": structured_insights.get("conviction", 5),
                "full_synthesis": synthesis_text,
                "synthesis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error in research synthesis: {e}")
            return {
                "investment_thesis": "Synthesis failed - review individual research areas",
                "key_strengths": ["Research data available in individual sections"],
                "major_concerns": ["Unable to complete comprehensive synthesis"],
                "critical_factors": ["Manual review recommended"],
                "investment_suitability": "Requires detailed manual analysis",
                "conviction_level": 3,
                "full_synthesis": f"Synthesis error: {str(e)}",
                "synthesis_timestamp": datetime.now().isoformat()
            }
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol mapping."""
        company_mapping = {
            'TCS': 'Tata Consultancy Services',
            'RELIANCE': 'Reliance Industries',
            'HDFCBANK': 'HDFC Bank',
            'INFY': 'Infosys',
            'ICICIBANK': 'ICICI Bank',
            'ITC': 'ITC Limited',
            'BHARTIARTL': 'Bharti Airtel',
            'AXISBANK': 'Axis Bank',
            'MARUTI': 'Maruti Suzuki',
            'WIPRO': 'Wipro'
        }
        return company_mapping.get(symbol, symbol)
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key bullet points from analysis text."""
        lines = text.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            # Look for bullet points, numbered items, or key insights
            if (line.startswith('•') or line.startswith('-') or line.startswith('*') or 
                (len(line) > 10 and any(char.isdigit() for char in line[:3]) and '.' in line[:3])):
                # Clean up the bullet point
                cleaned = line.lstrip('•-*0123456789. ').strip()
                if len(cleaned) > 20:  # Ensure substantial content
                    key_points.append(cleaned)
        
        # If no bullet points found, extract sentences that seem like key insights
        if not key_points:
            sentences = text.split('.')
            for sentence in sentences[:7]:  # Limit to 7 points
                sentence = sentence.strip()
                if (len(sentence) > 30 and 
                    any(keyword in sentence.lower() for keyword in 
                        ['growth', 'revenue', 'profit', 'margin', 'debt', 'ratio', 'target', 'outlook', 'strong', 'weak'])):
                    key_points.append(sentence)
        
        return key_points[:7]  # Limit to 7 key points
    
    def _parse_synthesis(self, synthesis_text: str) -> Dict[str, Any]:
        """Parse structured insights from synthesis text."""
        insights = {
            "thesis": "",
            "strengths": [],
            "concerns": [],
            "factors": [],
            "suitability": "",
            "conviction": 5
        }
        
        try:
            lines = synthesis_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                line_lower = line.lower()
                if 'investment thesis' in line_lower:
                    current_section = 'thesis'
                elif 'key strengths' in line_lower or 'strengths' in line_lower:
                    current_section = 'strengths'
                elif 'major concerns' in line_lower or 'concerns' in line_lower:
                    current_section = 'concerns'
                elif 'critical factors' in line_lower or 'factors to monitor' in line_lower:
                    current_section = 'factors'
                elif 'investment suitability' in line_lower or 'suitability' in line_lower:
                    current_section = 'suitability'
                elif 'conviction level' in line_lower or 'conviction' in line_lower:
                    # Extract conviction score
                    conviction_match = [char for char in line if char.isdigit()]
                    if conviction_match:
                        insights['conviction'] = int(conviction_match[0])
                    current_section = None
                elif current_section:
                    # Add content to current section
                    if current_section == 'thesis' and len(line) > 20:
                        insights['thesis'] += line + ' '
                    elif current_section == 'suitability' and len(line) > 20:
                        insights['suitability'] += line + ' '
                    elif current_section in ['strengths', 'concerns', 'factors']:
                        # Extract bullet points
                        if line.startswith(('•', '-', '*')) or any(char.isdigit() for char in line[:3]):
                            cleaned = line.lstrip('•-*0123456789. ').strip()
                            if len(cleaned) > 15:
                                insights[current_section].append(cleaned)
            
            # Clean up text fields
            insights['thesis'] = insights['thesis'].strip()
            insights['suitability'] = insights['suitability'].strip()
            
        except Exception as e:
            print(f"⚠️ Error parsing synthesis: {e}")
        
        return insights


# Example usage and testing
async def main():
    """Test the Stock Research Agent"""
    try:
        # Initialize agent
        agent = StockResearchAgent()
        
        # Test with TCS
        print("🚀 Testing Stock Research Agent with TCS...")
        result = await agent.research_stock_comprehensive("TCS.NS", "Tata Consultancy Services")
        
        print("\n📊 RESEARCH RESULTS:")
        print(f"Symbol: {result['symbol']}")
        print(f"Company: {result['company_name']}")
        print(f"Total Sources: {result['metadata']['total_sources']}")
        print(f"Average Confidence: {result['metadata']['average_confidence']:.2f}")
        
        print("\n🎯 INVESTMENT THESIS:")
        print(result['synthesis']['investment_thesis'])
        
        print("\n✅ KEY STRENGTHS:")
        for strength in result['synthesis']['key_strengths'][:3]:
            print(f"  • {strength}")
        
        print("\n⚠️ MAJOR CONCERNS:")
        for concern in result['synthesis']['major_concerns'][:3]:
            print(f"  • {concern}")
        
        print(f"\n📈 CONVICTION LEVEL: {result['synthesis']['conviction_level']}/10")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())