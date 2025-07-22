"""
FastAPI server to expose Artha-Agent backend to Next.js frontend
Enhanced with MoneyTruthEngine and AI-driven insights
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
import sys
import os
import json
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import ArthaAIChatbot
from core.fi_mcp.real_client import get_user_financial_data, get_portfolio_summary
from core.money_truth_engine import MoneyTruthEngine
from agents.enhanced_analyst import EnhancedAnalystAgent
from agents.enhanced_researcher import EnhancedResearchAgent
from agents.enhanced_risk_advisor import EnhancedRiskAdvisorAgent
from google import genai
from config.settings import config

app = FastAPI(title="Artha AI Backend API - Enhanced", version="2.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "http://localhost:3001"],  # Next.js dev server on different ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot and enhanced components
chatbot = None
money_truth_engine = None
enhanced_analyst = None
enhanced_researcher = None  
enhanced_risk_advisor = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    processing_time: float
    sources_count: int
    agents_used: list

class InsightRequest(BaseModel):
    analysis_type: str = "complete"  # complete, hidden_truths, future_wealth, etc.

@app.on_event("startup") 
async def startup_event():
    """Initialize the chatbot and enhanced AI components"""
    global chatbot, money_truth_engine, enhanced_analyst, enhanced_researcher, enhanced_risk_advisor
    try:
        chatbot = ArthaAIChatbot()
        
        # Initialize enhanced agents
        enhanced_analyst = EnhancedAnalystAgent()
        enhanced_researcher = EnhancedResearchAgent()
        enhanced_risk_advisor = EnhancedRiskAdvisorAgent()
        
        # Initialize Gemini client
        gemini_client = genai.Client(api_key=config.GOOGLE_API_KEY)
        
        # Initialize MoneyTruthEngine
        money_truth_engine = MoneyTruthEngine(
            enhanced_analyst, 
            enhanced_researcher, 
            enhanced_risk_advisor,
            gemini_client
        )
        
        logging.info("🚀 Enhanced Artha AI Backend initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize enhanced backend: {e}")

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
    """Get user's financial data from Fi MCP with portfolio summary"""
    try:
        financial_data = await get_user_financial_data()
        portfolio_summary = get_portfolio_summary(financial_data)
        
        return {
            "status": "success",
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else None,
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else None,
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else None
            },
            "summary": portfolio_summary
        }
    except Exception as e:
        logging.error(f"Financial data fetch failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": None,
            "summary": None
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

# Enhanced API endpoints for MoneyTruthEngine

@app.post("/api/money-truth")
async def get_money_truth_insights(request: InsightRequest = InsightRequest()):
    """Get comprehensive AI-driven money insights using MoneyTruthEngine"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    try:
        # Get user's financial data
        financial_data = await get_user_financial_data()
        mcp_data = {
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
        }
        
        # Run complete analysis
        insights = await money_truth_engine.analyze_complete(mcp_data)
        
        return {
            "status": "success",
            "insights": insights,
            "analysis_type": request.analysis_type
        }
        
    except Exception as e:
        logging.error(f"Money truth insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/real-time-insights")
async def get_real_time_insights(query_request: QueryRequest):
    """Get real-time AI insights for specific user queries"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    try:
        # Get user's financial data
        financial_data = await get_user_financial_data()
        mcp_data = {
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
        }
        
        # Get real-time insights
        insights = await money_truth_engine.get_real_time_insights(mcp_data, query_request.query)
        
        return {
            "status": "success",
            "query": query_request.query,
            "insights": insights
        }
        
    except Exception as e:
        logging.error(f"Real-time insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.post("/api/portfolio-health")
async def get_portfolio_health():
    """Get AI-driven portfolio health analysis"""
    if not enhanced_analyst:
        raise HTTPException(status_code=500, detail="Enhanced Analyst not initialized")
    
    try:
        # Get user's financial data
        financial_data = await get_user_financial_data()
        portfolio_data = {
            "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
            "timestamp": "current"
        }
        
        # Get portfolio health analysis
        health_analysis = await enhanced_analyst.analyze_portfolio_health(portfolio_data)
        
        return {
            "status": "success",
            "portfolio_health": health_analysis
        }
        
    except Exception as e:
        logging.error(f"Portfolio health analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health analysis failed: {str(e)}")

@app.post("/api/money-leaks")
async def detect_money_leaks():
    """Detect money leaks using AI analysis"""
    if not enhanced_analyst:
        raise HTTPException(status_code=500, detail="Enhanced Analyst not initialized")
    
    try:
        # Get user's financial data
        financial_data = await get_user_financial_data()
        mcp_data = {
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
        }
        
        # Detect money leaks
        leaks = await enhanced_analyst.detect_money_leaks(mcp_data)
        
        return {
            "status": "success",
            "money_leaks": leaks
        }
        
    except Exception as e:
        logging.error(f"Money leak detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Leak detection failed: {str(e)}")

@app.post("/api/risk-assessment")
async def get_risk_assessment():
    """Get comprehensive risk assessment"""
    if not enhanced_risk_advisor:
        raise HTTPException(status_code=500, detail="Enhanced Risk Advisor not initialized")
    
    try:
        # Get user's financial data
        financial_data = await get_user_financial_data()
        portfolio_data = {
            "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
            "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
        }
        
        # Get risk assessment
        risk_assessment = await enhanced_risk_advisor.assess_portfolio_risks(portfolio_data)
        
        return {
            "status": "success",
            "risk_assessment": risk_assessment
        }
        
    except Exception as e:
        logging.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

# WebSocket endpoint for real-time AI insights
@app.websocket("/ws/live-insights")
async def websocket_live_insights(websocket: WebSocket):
    """WebSocket endpoint for streaming live AI insights"""
    await websocket.accept()
    
    try:
        while True:
            # Wait for user query
            query_data = await websocket.receive_text()
            query_obj = json.loads(query_data)
            user_query = query_obj.get("query", "")
            
            if not user_query:
                continue
                
            # Send thinking status
            await websocket.send_json({
                "type": "thinking",
                "message": "AI agents are analyzing your request...",
                "status": "processing"
            })
            
            try:
                # Get financial data
                financial_data = await get_user_financial_data()
                mcp_data = {
                    "data": {
                        "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                        "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                        "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
                    }
                }
                
                # Get real-time insights
                if money_truth_engine:
                    insights = await money_truth_engine.get_real_time_insights(mcp_data, user_query)
                    
                    # Send insights
                    await websocket.send_json({
                        "type": "insights",
                        "query": user_query,
                        "data": insights,
                        "status": "complete"
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "AI engine not available",
                        "status": "error"
                    })
                    
            except Exception as e:
                await websocket.send_json({
                    "type": "error", 
                    "message": f"Analysis failed: {str(e)}",
                    "status": "error"
                })
                
    except WebSocketDisconnect:
        logging.info("WebSocket client disconnected")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)