"""
Base Agent Class for the Revolutionary 3-Agent Financial AI System
Provides common functionality for all specialized financial agents
"""

import asyncio
import json
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
import logging
from google import genai
from google.genai import types

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fi_mcp.client import FinancialData
from core.google_grounding.grounding_client import GoogleGroundingClient, GroundingResult
from config.settings import config, AgentConfig
from utils.response_cache import response_cache

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Structured agent response with grounding data"""
    agent_name: str
    agent_emoji: str
    content: str
    grounded_data: List[GroundingResult] = field(default_factory=list)
    confidence_level: float = 0.0
    processing_time: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'agent_name': self.agent_name,
            'agent_emoji': self.agent_emoji,
            'content': self.content,
            'grounded_sources': len(self.grounded_data),
            'confidence_level': self.confidence_level,
            'processing_time': self.processing_time,
            'recommendations': self.recommendations,
            'risk_factors': self.risk_factors,
            'timestamp': self.timestamp
        }

class BaseFinancialAgent(ABC):
    """Abstract base class for all financial agents"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.config = getattr(AgentConfig, f"{agent_type.upper()}_AGENT")
        self.name = self.config["name"]
        self.emoji = self.config["emoji"]
        self.personality = self.config["personality"]
        self.grounding_focus = self.config["grounding_focus"]
        self.response_style = self.config["response_style"]
        
        # Initialize Google Grounding client
        self.grounding_client = GoogleGroundingClient()
        
        # Initialize Gemini client for general reasoning
        self.gemini_client = genai.Client(api_key=config.GOOGLE_API_KEY)
        
        logger.info(f"Initialized {self.name} with personality: {self.personality}")
    
    @abstractmethod
    async def generate_grounding_queries(self, user_query: str, financial_data: FinancialData) -> List[str]:
        """Generate search queries using AI based on user query and financial data"""
        pass
    
    @abstractmethod
    async def analyze_financial_data(self, financial_data: FinancialData) -> Dict[str, Any]:
        """Analyze user's financial data"""
        pass
    
    @abstractmethod  
    async def process_grounded_intelligence(self, search_results: List[Dict[str, Any]], financial_data: FinancialData) -> Dict[str, Any]:
        """Process search results from Gemini Google Search"""
        pass
    
    @abstractmethod
    async def generate_response(self, user_query: str, financial_data: FinancialData, grounded_intelligence: Dict[str, Any]) -> str:
        """Generate final agent response"""
        pass
    
    async def search_with_gemini(self, query: str, financial_context: str) -> Dict[str, Any]:
        """Use Google Search grounding exactly as per official documentation"""
        logger.info(f"{self.name}: Executing Google Search grounding for: {query}")
        
        try:
            # Configure the grounding tool exactly as per Google documentation
            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            
            # Configure generation settings for grounding
            config_grounding = types.GenerateContentConfig(
                tools=[grounding_tool]
            )
            
            # Use query as-is if it's already comprehensive (for stocks)
            if len(query.split()) > 10:  # Comprehensive query
                search_prompt = query
            else:
                # Add context for simple queries
                search_prompt = f"{query} India financial market 2025 expert analysis"
            
            # Make the grounded request using official documentation method
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=search_prompt,
                config=config_grounding
            )
            
            # Initialize result structure
            result = {
                'query': query,
                'findings': response.text,
                'sources': [],
                'web_search_queries': [],
                'search_success': True
            }
            
            # Process grounding metadata exactly as per official documentation
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    logger.info(f"{self.name}: Grounding metadata found!")
                    
                    # Extract webSearchQueries as per documentation
                    if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                        result['web_search_queries'] = list(metadata.web_search_queries)
                        logger.info(f"{self.name}: Search queries used: {result['web_search_queries']}")
                    
                    # Extract groundingChunks as per documentation  
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        sources = []
                        for i, chunk in enumerate(metadata.grounding_chunks):
                            if hasattr(chunk, 'web') and chunk.web:
                                source = {
                                    'index': i + 1,
                                    'title': getattr(chunk.web, 'title', f'Source {i+1}'),
                                    'uri': getattr(chunk.web, 'uri', '#')
                                }
                                sources.append(source)
                        
                        result['sources'] = sources
                        logger.info(f"{self.name}: Retrieved {len(sources)} sources from grounding")
                    
                    # Extract groundingSupports as per documentation
                    if hasattr(metadata, 'grounding_supports') and metadata.grounding_supports:
                        result['grounding_supports'] = []
                        for support in metadata.grounding_supports:
                            if hasattr(support, 'segment') and support.segment:
                                support_info = {
                                    'text_segment': getattr(support.segment, 'text', ''),
                                    'start_index': getattr(support.segment, 'start_index', 0),
                                    'end_index': getattr(support.segment, 'end_index', 0),
                                    'chunk_indices': list(support.grounding_chunk_indices) if hasattr(support, 'grounding_chunk_indices') and support.grounding_chunk_indices else []
                                }
                                result['grounding_supports'].append(support_info)
                        logger.info(f"{self.name}: Processed {len(result['grounding_supports'])} citation supports")
                    
                else:
                    logger.warning(f"{self.name}: No grounding metadata found")
                    result['search_success'] = False
            
            # Add source count to findings
            if result['sources']:
                source_count = len(result['sources'])
                result['findings'] += f"\n\n**Live Market Sources**: {source_count} verified web sources"
                
                # Add source list
                source_list = "\n".join([f"• {s['title']}" for s in result['sources'][:3]])
                result['findings'] += f"\n**Key Sources**: \n{source_list}"
            
            logger.info(f"{self.name}: Search completed - {len(result['sources'])} sources, {len(result['web_search_queries'])} queries")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"{self.name}: Search timeout after {config.SEARCH_TIMEOUT_SECONDS} seconds")
            return {
                'query': query,
                'findings': "Search timeout - no market data available",
                'sources': [],
                'web_search_queries': [],
                'search_success': False,
                'error': 'timeout'
            }
            
        except Exception as e:
            logger.error(f"{self.name}: Google Search grounding failed: {str(e)}")
            return {
                'query': query,
                'findings': f"Search error: {str(e)}",
                'sources': [],
                'web_search_queries': [],
                'search_success': False,
                'error': str(e)
            }
    
    async def stream_thinking_process(self, stage: str, content: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream agent's thinking process for real-time terminal display"""
        yield {
            'type': 'thinking',
            'agent': self.name,
            'emoji': self.emoji,
            'stage': stage,
            'content': content,
            'timestamp': time.time()
        }
        
        # Simulate thinking delay for dramatic effect
        await asyncio.sleep(0.5)
    
    async def process_user_query(self, user_query: str, financial_data: FinancialData) -> AgentResponse:
        """Main processing pipeline using REAL Gemini with Google Search"""
        start_time = time.time()
        
        try:
            # Stage 1: Analyze Financial Data with AI
            async for thinking in self.stream_thinking_process(
                "financial_analysis", 
                f"AI analyzing your financial portfolio..."
            ):
                yield thinking
            
            financial_analysis = await self.analyze_financial_data(financial_data)
            
            # Stage 2: Generate Search Queries with AI
            async for thinking in self.stream_thinking_process(
                "query_generation",
                f"AI generating targeted search queries..."
            ):
                yield thinking
            
            search_queries = await self.generate_grounding_queries(user_query, financial_data)
            
            # Stage 3: Execute Google Searches via Gemini
            async for thinking in self.stream_thinking_process(
                "market_research", 
                f"Searching Google for: {search_queries[0] if search_queries else 'market data'}..."
            ):
                yield thinking
            
            # Perform searches using Gemini with Google Search
            search_results = []
            financial_context = self._format_financial_summary(financial_data)
            
            # Process searches with parallel processing for speed optimization
            if config.PARALLEL_SEARCH_PROCESSING and len(search_queries) > 1:
                # Parallel processing for multiple queries
                search_tasks = []
                for query in search_queries[:config.MAX_GROUNDING_QUERIES]:
                    task = asyncio.wait_for(
                        self.search_with_gemini(query, financial_context),
                        timeout=config.SEARCH_TIMEOUT_SECONDS
                    )
                    search_tasks.append(task)
                
                search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
                search_results = [r for r in search_results if not isinstance(r, Exception)]
            else:
                # Sequential processing for single query or when parallel is disabled
                search_results = []
                for query in search_queries[:config.MAX_GROUNDING_QUERIES]:
                    try:
                        result = await asyncio.wait_for(
                            self.search_with_gemini(query, financial_context),
                            timeout=config.SEARCH_TIMEOUT_SECONDS
                        )
                        search_results.append(result)
                    except asyncio.TimeoutError:
                        logger.warning(f"{self.name}: Search timeout for query: {query}")
                    except Exception as e:
                        logger.error(f"{self.name}: Search failed for query {query}: {e}")
                        
            logger.info(f"{self.name}: Completed {len(search_results)} searches out of {len(search_queries)} queries")
            
            # Stage 4: Process Search Results with AI
            async for thinking in self.stream_thinking_process(
                "intelligence_processing",
                f"AI processing {len(search_results)} search results..."
            ):
                yield thinking
            
            grounded_intelligence = await self.process_grounded_intelligence(search_results, financial_data)
            
            # Stage 5: Generate Final Response with Grounding
            async for thinking in self.stream_thinking_process(
                "response_generation",
                f"AI formulating grounded recommendations..."
            ):
                yield thinking
            
            response_content = await self.generate_response(user_query, financial_data, grounded_intelligence)
            
            processing_time = time.time() - start_time
            
            # Extract all sources from search results
            all_sources = []
            for result in search_results:
                all_sources.extend(result.get('sources', []))
            
            response = AgentResponse(
                agent_name=self.name,
                agent_emoji=self.emoji,
                content=response_content,
                grounded_data=search_results,
                confidence_level=0.95 if search_results else 0.5,
                processing_time=processing_time,
                recommendations=grounded_intelligence.get('recommendations', []),
                risk_factors=grounded_intelligence.get('risks', [])
            )
            
            # Final response stream
            yield {
                'type': 'response',
                'agent': self.name,
                'emoji': self.emoji,
                'response': response.to_dict(),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"{self.name}: Processing failed: {e}")
            
            error_response = AgentResponse(
                agent_name=self.name,
                agent_emoji=self.emoji,
                content=f"I encountered an error: {str(e)}",
                confidence_level=0.0,
                processing_time=time.time() - start_time
            )
            
            yield {
                'type': 'error',
                'agent': self.name,
                'emoji': self.emoji,
                'error': str(e),
                'response': error_response.to_dict(),
                'timestamp': time.time()
            }
    
    def format_currency(self, amount: float, currency: str = "INR") -> str:
        """Format currency amounts for display"""
        if currency == "INR":
            if amount >= 10000000:  # 1 crore
                return f"₹{amount/10000000:.2f}Cr"
            elif amount >= 100000:  # 1 lakh
                return f"₹{amount/100000:.2f}L"
            elif amount >= 1000:  # 1 thousand
                return f"₹{amount/1000:.1f}K"
            else:
                return f"₹{amount:.0f}"
        else:
            return f"{currency} {amount:,.2f}"
    
    def calculate_percentage_change(self, current: float, previous: float) -> str:
        """Calculate and format percentage change"""
        if previous == 0:
            return "N/A"
        
        change = ((current - previous) / previous) * 100
        sign = "+" if change > 0 else ""
        return f"{sign}{change:.1f}%"
    
    def _format_financial_summary(self, financial_data: FinancialData) -> str:
        """Format financial data summary for search context"""
        summary_parts = []
        
        # Add net worth if available
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth_resp = financial_data.net_worth.get('netWorthResponse', {})
            total_value = net_worth_resp.get('totalNetWorthValue', {})
            if total_value.get('units'):
                summary_parts.append(f"Net worth: ₹{total_value.get('units')}")
        
        # Add credit score if available
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports:
                score = credit_reports[0].get('creditReportData', {}).get('score', {}).get('bureauScore')
                if score:
                    summary_parts.append(f"Credit score: {score}")
        
        return "User's financial profile: " + ", ".join(summary_parts) if summary_parts else "General user"
    
    async def generate_ai_response(self, system_prompt: str, user_context: str, market_context: str = "") -> str:
        """Generate AI-powered response using Gemini with REAL Google Search Grounding"""
        
        # Check cache first
        cache_key = f"{user_context[:100]}_{market_context[:50]}"
        cached_response = response_cache.get(cache_key)
        if cached_response:
            return cached_response
        
        try:
            # Configure REAL Google Search Grounding tool
            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            
            # Configure generation with grounding
            gen_config = types.GenerateContentConfig(
                tools=[grounding_tool],
                system_instruction=f"You are an {self.personality} Indian financial agent specializing in {self.grounding_focus}. {self.response_style}. Focus on INDIAN financial context - use INR currency, Indian financial products, Indian market conditions. Use Google Search to find current Indian market data and cite your sources.",
                **config.GEMINI_GENERATION_CONFIG
            )
            
            # Construct comprehensive prompt
            full_prompt = f"""
{system_prompt}

{market_context}

{user_context}

IMPORTANT: Use Google Search to find current, accurate information about market conditions, prices, and financial data. Provide data-driven insights with citations.
"""
            
            # Generate AI response with REAL grounding
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=gen_config
            )
            
            # Check for empty response
            if not response or not response.text:
                logger.error(f"{self.name}: AI response was empty")
                if hasattr(response, 'candidates') and response.candidates:
                    logger.error(f"Finish reason: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
                if hasattr(response, 'usage_metadata'):
                    logger.error(f"Token usage: {response.usage_metadata}")
                raise ValueError("AI returned empty response")
            
            # Process grounding metadata if available
            if response.candidates and response.candidates[0].grounding_metadata:
                result = self._process_grounded_response(response)
            else:
                result = self._add_agent_personality(response.text)
            
            # Cache the response
            response_cache.set(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"{self.name}: AI generation with grounding failed: {e}")
            # Try without grounding as fallback
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(**config.GEMINI_GENERATION_CONFIG)
                )
                result = self._add_agent_personality(response.text)
                response_cache.set(cache_key, result)
                return result
            except Exception as e2:
                logger.error(f"{self.name}: Fallback AI generation also failed: {e2}")
                return self._generate_intelligent_fallback(user_context)
    
    def _trim_response_length(self, response: str) -> str:
        """Return complete response without truncation - improved for full analysis"""
        # Remove truncation logic completely - users want complete analysis
        return response
    
    def _add_agent_personality(self, ai_response: str) -> str:
        """Inject agent personality into AI responses"""
        
        personality_enhancements = {
            'analyst': {
                'openings': [
                    "Financial detective mode: ACTIVATED! Here's what I found...",
            "Your numbers just revealed something INCREDIBLE!",
            "I've uncovered fascinating insights in your financial data!",
            "Detective work complete! Your financial story is amazing..."
                ],
                'conclusions': [
                    "The data is crystal clear - you've got solid potential!",
                    "Numbers never lie - this analysis reveals your true position!",
                    "Data-driven confidence: The evidence supports this path!"
                ]
            },
            'research': {
                'openings': [
                    "Strategy radar: LOCKED ON TARGET!",
            "I've discovered the PERFECT strategy for you!",
            "Opportunity hunter mode: Amazing findings ahead!",
            "Strategic mastermind activated! Here's your winning plan..."
                ],
                'conclusions': [
                    "This strategy is absolutely BRILLIANT for your situation!",
                    "Perfect timing + perfect strategy = SUCCESS!",
                    "Strategic confidence: This plan will deliver results!"
                ]
            },
            'risk': {
                'openings': [
                    "Risk radar: ACTIVE MONITORING!",
            "ALERT: Critical financial threats detected!",
            "Financial guardian mode: Protection analysis ready!",
            "Security scan complete! Urgent safeguards needed..."
                ],
                'conclusions': [
                    "SECURE your financial future with these protections!",
                    "Financial fortress: Your wealth WILL be protected!",
                    "Protection confidence: These safeguards are ESSENTIAL!"
                ]
            }
        }
        
        agent_personality = personality_enhancements.get(self.agent_type, personality_enhancements['analyst'])
        
        # Add enthusiastic opening
        import random
        opening = random.choice(agent_personality['openings'])
        
        # Enhance response with personality
        enhanced_response = f"{opening}\n\n{ai_response}"
        
        # Add confident conclusion
        conclusion = random.choice(agent_personality['conclusions'])
        enhanced_response += f"\n\n**{conclusion}**"
        
        # Trim response if too long
        return self._trim_response_length(enhanced_response)
    
    def _process_grounded_response(self, response) -> str:
        """Process response with grounding metadata but remove citation links"""
        try:
            text = response.text
            
            # Remove any citation URLs that may appear in the text
            import re
            # Remove citation links like [title](url)
            text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
            # Remove raw URLs
            text = re.sub(r'https?://[^\s]+', '', text)
            # Remove grounding redirect URLs specifically
            text = re.sub(r'https://vertexaisearch\.cloud\.google\.com/grounding-api-redirect/[^\s\)]+', '', text)
            
            return self._add_agent_personality(text)
            
        except Exception as e:
            logger.warning(f"Failed to process grounding metadata: {e}")
            return self._add_agent_personality(response.text)
    
    def _generate_intelligent_fallback(self, user_context: str) -> str:
        """Generate fallback when AI fails"""
        return f"{self.emoji} I encountered an issue accessing the AI service. Please try again in a moment."
    
    async def participate_in_collaboration(self, peer_responses: Dict, context: Dict) -> Dict:
        """Use AI to participate in multi-agent collaboration"""
        
        collaboration_prompt = f"""
You are an AI-powered {self.agent_type} participating in a collaborative financial discussion.

Your Specialty: {self.grounding_focus}
Your Personality: {self.personality}

Peer Agent Responses:
{json.dumps(peer_responses, indent=2)}

User Context:
{json.dumps(context, indent=2)}

As the {self.agent_type} expert, provide:
1. {self.grounding_focus}-specific insights that support or challenge peer recommendations
2. Specific evidence from user's financial profile
3. Questions for other agents based on your analysis
4. Compromise suggestions using your expertise

Maintain your {self.personality} personality while being collaborative.
"""
        
        try:
            ai_collaboration = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=collaboration_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=f"You are a {self.personality} {self.agent_type} agent in a collaborative discussion.",
                    **config.GEMINI_GENERATION_CONFIG
                )
            )
            
            return {
                'agent': self.agent_type,
                'position': ai_collaboration.text,
                'confidence': 0.9,  # High confidence with AI reasoning
                'supporting_data': context.get('financial_metrics', {}),
                'collaboration_style': f'{self.agent_type}_ai_powered'
            }
            
        except Exception as e:
            logger.error(f"{self.name}: AI collaboration failed: {e}")
            return self._generate_fallback_collaboration(peer_responses, context)
    
    def _generate_fallback_collaboration(self, peer_responses: Dict, context: Dict) -> Dict:
        """Generate fallback collaboration when AI fails"""
        
        return {
            'agent': self.agent_type,
            'position': f"As the {self.agent_type} expert, I'm temporarily using fallback analysis. My {self.grounding_focus} assessment suggests reviewing the peer recommendations with focus on data-driven evidence.",
            'confidence': 0.5,
            'supporting_data': context.get('financial_metrics', {}),
            'collaboration_style': f'{self.agent_type}_fallback'
        }
    
