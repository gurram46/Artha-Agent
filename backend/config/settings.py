"""
Configuration settings for the Revolutionary 3-Agent Financial AI System
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Main configuration class"""
    
    # Google AI Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Fi MCP Configuration
    FI_MCP_URL = os.getenv("FI_MCP_URL", "https://mcp.fi.money:8080/mcp/stream")
    FI_MCP_AUTH_TOKEN = os.getenv("FI_MCP_AUTH_TOKEN")
    
    # Performance Configuration - Optimized for Speed
    MAX_GROUNDING_QUERIES = int(os.getenv("MAX_GROUNDING_QUERIES", "3"))  # Reduced from 5 to 3 for faster response
    COLLABORATION_TIMEOUT = int(os.getenv("COLLABORATION_TIMEOUT", "8"))   # Reduced from 15 to 8 seconds
    STREAMING_CHUNK_SIZE = int(os.getenv("STREAMING_CHUNK_SIZE", "1024"))  # Increased chunk size
    ENABLE_RESPONSE_CACHING = os.getenv("ENABLE_RESPONSE_CACHING", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))        # Increased cache time for better performance
    PARALLEL_AGENT_PROCESSING = os.getenv("PARALLEL_AGENT_PROCESSING", "false").lower() == "true"  # Sequential for complete analysis
    PARALLEL_SEARCH_PROCESSING = os.getenv("PARALLEL_SEARCH_PROCESSING", "true").lower() == "true"  # Parallel searches for speed
    GEMINI_GENERATION_CONFIG = {
        "temperature": 0.3,
        "max_output_tokens": 6000,  # Increased for complete responses 
        "top_p": 0.8,
        "top_k": 40
    }
    RESPONSE_LENGTH_LIMIT = 12000  # Increased to prevent truncation
    SEARCH_TIMEOUT_SECONDS = int(os.getenv("SEARCH_TIMEOUT_SECONDS", "5"))  # Fast search timeout
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required environment variables"""
        required = ["GOOGLE_API_KEY"]
        missing = [var for var in required if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
        return True

class AgentConfig:
    """Agent-specific configuration for comprehensive financial advisory"""
    
    ANALYST_AGENT = {
        "name": "Financial Data Intelligence Analyst",
        "emoji": "🕵️",
        "personality": "excited data detective, enthusiastic about numbers, loves revealing insights",
        "grounding_focus": ["financial_data", "market_trends", "economic_indicators", "cost_analysis", "budget_assessment"],
        "response_style": "🔥 Energetic analysis revealing what your numbers show! Gets excited about financial discoveries and patterns",
        "specialization": "Analyzes your complete financial situation for ANY query - whether it's buying a car, renting a house, changing jobs, planning vacation, filing taxes, or any financial decision"
    }
    
    RESEARCH_AGENT = {
        "name": "Universal Financial Strategist & Planner", 
        "emoji": "🎯",
        "personality": "strategic mastermind, opportunity hunter, gets excited about perfect plans",
        "grounding_focus": ["opportunities", "financial_products", "market_research", "planning_strategies", "alternatives"],
        "response_style": "💎 Discovers amazing opportunities and creates winning strategies! Enthusiastic about finding the perfect path forward",
        "specialization": "Creates comprehensive financial plans and finds opportunities for ANY financial need - car buying, house renting, career moves, vacation planning, tax optimization, and all life decisions"
    }
    
    RISK_AGENT = {
        "name": "Comprehensive Risk & Protection Advisor",
        "emoji": "🛡️", 
        "personality": "protective guardian, urgent about safety, passionate about financial security",
        "grounding_focus": ["risk_assessment", "financial_protection", "regulatory_compliance", "insurance", "emergency_planning"],
        "response_style": "⚠️ Urgent protection alerts! Passionate about securing your financial future with specific safeguards",
        "specialization": "Assesses ALL risks and provides protection for ANY financial decision - whether buying assets, making career moves, major purchases, travel, or any financial commitment"
    }

class GroundingConfig:
    """Google Search Grounding configuration"""
    
    # Market Data Queries
    MARKET_QUERIES = [
        "nifty 50 index current price today",
        "indian stock market performance today", 
        "rbi repo rate current 2024",
        "inflation rate india current month"
    ]
    
    # Interest Rate Queries  
    RATE_QUERIES = [
        "home loan interest rates india today",
        "fixed deposit rates major banks current",
        "mutual fund returns top performers 2024",
        "credit card interest rates comparison"
    ]
    
    # Economic Indicator Queries
    ECONOMIC_QUERIES = [
        "gdp growth rate india latest quarter",
        "unemployment rate india current statistics",
        "forex reserves rbi latest data",
        "corporate earnings outlook india"
    ]

# Load and validate configuration
config = Config()
config.validate()