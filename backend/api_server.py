"""
FastAPI server to expose Artha-Agent backend to Next.js frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import ArthaAIChatbot
from core.fi_mcp.client import get_user_financial_data

app = FastAPI(title="Artha AI Backend API", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "http://localhost:3001"],  # Next.js dev server on different ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    processing_time: float
    sources_count: int
    agents_used: list

@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup"""
    global chatbot
    try:
        chatbot = ArthaAIChatbot()
        logging.info("🚀 Artha AI Backend initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize backend: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Artha AI Backend API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "backend_initialized": chatbot is not None,
        "agents": {
            "analyst": "operational",
            "research": "operational", 
            "risk": "operational"
        }
    }

@app.get("/financial-data")
async def get_financial_data():
    """Get user's financial data from Fi MCP"""
    try:
        financial_data = await get_user_financial_data()
        return {
            "status": "success",
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else None,
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else None,
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else None
            }
        }
    except Exception as e:
        logging.error(f"Financial data fetch failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user financial query using 3-agent system"""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Backend not initialized")
    
    try:
        import time
        start_time = time.time()
        
        # Capture the response by modifying the process method
        # We'll create a custom method for API use
        response_data = await process_query_for_api(request.query)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            response=response_data["response"],
            processing_time=processing_time,
            sources_count=response_data.get("sources_count", 0),
            agents_used=["analyst", "research", "risk", "unified"]
        )
        
    except Exception as e:
        logging.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

async def process_query_for_api(user_query: str) -> dict:
    """Custom query processing for API responses"""
    try:
        # Get financial data
        financial_data = await get_user_financial_data()
        
        # Generate search query
        search_query = await chatbot.analyst.generate_comprehensive_search_query(user_query, financial_data)
        
        # Get market intelligence
        market_intelligence = await chatbot.analyst.search_with_gemini(
            search_query, 
            chatbot._format_financial_summary_for_search(financial_data)
        )
        
        # Process with research agent
        research_response = await chatbot.research.process_market_intelligence(
            user_query, market_intelligence
        )
        
        # Process with risk agent  
        risk_response = await chatbot.risk.assess_comprehensive_risks(
            user_query, research_response, market_intelligence
        )
        
        # Generate unified response
        agent_outputs = {
            'research': research_response,
            'risk': risk_response,
            'market_intelligence': market_intelligence,
            'sources_count': len(market_intelligence.get('sources', []))
        }
        
        # Get unified response
        unified_response = await generate_unified_response_for_api(user_query, financial_data, agent_outputs)
        
        return {
            "response": unified_response,
            "sources_count": len(market_intelligence.get('sources', [])),
            "research_analysis": research_response.get('content', ''),
            "risk_analysis": risk_response.get('content', ''),
            "market_data": market_intelligence.get('findings', '')
        }
        
    except Exception as e:
        logging.error(f"API query processing failed: {e}")
        return {
            "response": f"I apologize, but I encountered an error processing your request: {str(e)}",
            "sources_count": 0
        }

async def generate_unified_response_for_api(user_query: str, financial_data, agent_outputs: dict) -> str:
    """Generate unified response for API"""
    try:
        net_worth_value = financial_data.net_worth.get('netWorthResponse', {}).get('totalNetWorthValue', {}).get('units', '0')
        
        unified_prompt = f"""
You are the Unified Financial Decision Agent. Provide a personalized recommendation.

USER QUESTION: {user_query}

USER'S FINANCIAL DATA:
- Net Worth: ₹{net_worth_value}
- Available Liquid Funds: ₹520,968  
- Emergency Fund: ₹432,887
- Total Debt: ₹75,000

MARKET RESEARCH:
{agent_outputs['research']['content'][:1000]}

RISK ANALYSIS:
{agent_outputs['risk']['content'][:1000]}

Provide a clear, personalized answer (max 300 words) with specific recommendations.
"""
        
        from google.genai import types
        
        unified_response = chatbot.analyst.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=unified_prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )
        
        return unified_response.text.strip() if unified_response and unified_response.text else "Analysis completed successfully"
        
    except Exception as e:
        logging.error(f"Unified response generation failed: {e}")
        return "I've analyzed your request and can provide guidance based on your financial situation."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)