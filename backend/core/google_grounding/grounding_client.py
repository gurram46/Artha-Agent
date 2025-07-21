"""
Google Search Grounding Integration
Provides real-time market intelligence using Google's Search Grounding feature with Gemini
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from google import genai
from google.genai import types
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import config

logger = logging.getLogger(__name__)

@dataclass
class GroundingResult:
    """Container for grounding results with citations"""
    text: str
    search_queries: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_citations(self) -> str:
        """Add inline citations to the text"""
        if not self.citations:
            return self.text
            
        text_with_citations = self.text
        
        # Sort by end_index descending to avoid shifting issues
        sorted_citations = sorted(self.citations, key=lambda x: x.get('end_index', 0), reverse=True)
        
        for citation in sorted_citations:
            end_index = citation.get('end_index', 0)
            source_indices = citation.get('source_indices', [])
            
            if source_indices and end_index < len(text_with_citations):
                citation_links = []
                for idx in source_indices:
                    if idx < len(self.sources):
                        source = self.sources[idx]
                        uri = source.get('uri', '#')
                        title = source.get('title', f'Source {idx+1}')
                        citation_links.append(f"[{idx+1}]({uri})")
                
                citation_string = ", ".join(citation_links) 
                text_with_citations = (text_with_citations[:end_index] + 
                                     citation_string + 
                                     text_with_citations[end_index:])
        
        return text_with_citations

class GoogleGroundingClient:
    """Client for Google Search Grounding with Gemini"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.GOOGLE_API_KEY
        self.model = model or config.GEMINI_MODEL
        self.client = genai.Client(api_key=self.api_key)
        
        # Configure grounding tool
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        self.config = types.GenerateContentConfig(
            tools=[self.grounding_tool]
        )
        
    async def ground_query(self, query: str, context: str = "") -> GroundingResult:
        """Execute a grounded query with real-time search"""
        try:
            full_prompt = f"{context}\n\n{query}" if context else query
            
            logger.info(f"Executing grounded query: {query}")
            
            # Make grounded request
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=self.config
            )
            
            result = GroundingResult(text=response.text)
            
            # Extract grounding metadata if available
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    
                    # Extract search queries
                    if hasattr(metadata, 'web_search_queries'):
                        result.search_queries = metadata.web_search_queries
                    
                    # Extract sources
                    if hasattr(metadata, 'grounding_chunks'):
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web'):
                                result.sources.append({
                                    'uri': chunk.web.uri,
                                    'title': chunk.web.title
                                })
                    
                    # Extract citations
                    if hasattr(metadata, 'grounding_supports'):
                        for support in metadata.grounding_supports:
                            if hasattr(support, 'segment') and hasattr(support, 'grounding_chunk_indices'):
                                result.citations.append({
                                    'start_index': support.segment.start_index,
                                    'end_index': support.segment.end_index, 
                                    'text': support.segment.text,
                                    'source_indices': list(support.grounding_chunk_indices)
                                })
            
            logger.info(f"Grounded query successful with {len(result.sources)} sources")
            return result
            
        except Exception as e:
            logger.error(f"Grounding query failed: {e}")
            return GroundingResult(text=f"Unable to fetch real-time data: {str(e)}")
    
    async def ground_multiple_queries(self, queries: List[str], context: str = "") -> List[GroundingResult]:
        """Execute multiple grounded queries concurrently"""
        logger.info(f"Executing {len(queries)} grounded queries concurrently")
        
        tasks = [self.ground_query(query, context) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Query {i} failed: {result}")
                processed_results.append(GroundingResult(text=f"Query failed: {str(result)}"))
            else:
                processed_results.append(result)
        
        return processed_results

class MarketDataGrounder:
    """Specialized grounder for market data queries"""
    
    def __init__(self, grounding_client: GoogleGroundingClient):
        self.client = grounding_client
        
    async def get_current_market_data(self) -> GroundingResult:
        """Get current market performance data"""
        query = """
        What is the current performance of Indian stock markets today? 
        Include Nifty 50 index level, Sensex, major sector performance, and market sentiment.
        Provide specific numbers and percentage changes.
        """
        
        context = "Focus on factual, current market data with specific numbers and sources."
        return await self.client.ground_query(query, context)
    
    async def get_interest_rates(self) -> GroundingResult:
        """Get current interest rates"""
        query = """
        What are the current interest rates in India for December 2024?
        Include RBI repo rate, home loan rates from major banks, fixed deposit rates, 
        and credit card interest rates.
        """
        
        context = "Focus on current, accurate interest rate data from reliable sources."
        return await self.client.ground_query(query, context)
    
    async def get_economic_indicators(self) -> GroundingResult:
        """Get current economic indicators"""
        query = """
        What are India's current economic indicators for December 2024?
        Include GDP growth rate, inflation rate, unemployment rate, forex reserves,
        and RBI's monetary policy stance.
        """
        
        context = "Focus on official economic data from RBI, government sources, and reliable financial institutions."
        return await self.client.ground_query(query, context)

class PolicyGrounder:
    """Specialized grounder for policy and regulatory updates"""
    
    def __init__(self, grounding_client: GoogleGroundingClient):
        self.client = grounding_client
        
    async def get_tax_policy_updates(self) -> GroundingResult:
        """Get latest tax policy changes"""
        query = """
        What are the latest tax policy changes in India affecting investments for December 2024?
        Include capital gains tax, TDS changes, investment tax benefits, and new rules.
        """
        
        return await self.client.ground_query(query)
    
    async def get_regulatory_changes(self) -> GroundingResult:
        """Get regulatory changes affecting finance"""
        query = """
        What are the latest regulatory changes from RBI, SEBI, and other financial regulators 
        in India for December 2024 affecting personal finance and investments?
        """
        
        return await self.client.ground_query(query)

# Convenience functions
async def ground_market_intelligence(queries: List[str]) -> List[GroundingResult]:
    """Get grounded market intelligence"""
    client = GoogleGroundingClient()
    return await client.ground_multiple_queries(queries)

async def get_live_market_context() -> Dict[str, GroundingResult]:
    """Get comprehensive live market context"""
    client = GoogleGroundingClient()
    market_grounder = MarketDataGrounder(client)
    policy_grounder = PolicyGrounder(client)
    
    # Get all context concurrently
    tasks = {
        'market_data': market_grounder.get_current_market_data(),
        'interest_rates': market_grounder.get_interest_rates(), 
        'economic_indicators': market_grounder.get_economic_indicators(),
        'tax_updates': policy_grounder.get_tax_policy_updates(),
        'regulatory_changes': policy_grounder.get_regulatory_changes()
    }
    
    results = {}
    for key, task in tasks.items():
        try:
            results[key] = await task
        except Exception as e:
            logger.error(f"Failed to get {key}: {e}")
            results[key] = GroundingResult(text=f"Failed to fetch {key}: {str(e)}")
    
    return results