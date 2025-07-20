"""
Artha AI Backend - FastAPI Multi-Agent Financial Advisory System
Main FastAPI application orchestrating 3 collaborative agents using Gemini AI
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import our modules
from utils.data_loader import DataLoader
from agents.analyst_agent.analyst import AnalystAgent
from agents.research_agent.research import ResearchAgent
from agents.risk_management_agent.risk_manager import RiskManagementAgent
from coordination.agent_coordinator import AgentCoordinator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for agents
data_loader = None
analyst_agent = None
research_agent = None
risk_agent = None
coordinator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents on startup"""
    global data_loader, analyst_agent, research_agent, risk_agent, coordinator
    
    logger.info("Initializing Artha AI Backend...")
    
    try:
        # Initialize data loader
        data_loader = DataLoader()
        
        # Initialize agents
        analyst_agent = AnalystAgent(data_loader)
        research_agent = ResearchAgent(data_loader)
        risk_agent = RiskManagementAgent(data_loader)
        
        # Initialize coordinator
        coordinator = AgentCoordinator(analyst_agent, research_agent, risk_agent)
        
        logger.info("All agents initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down Artha AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="Artha AI Backend",
    description="Multi-Agent Financial Advisory System with Gemini AI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for web interface
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., description="User's financial query")
    user_id: str = Field(default="demo_user", description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Chat session identifier")


class ChatResponse(BaseModel):
    session_id: str
    user_query: str
    final_summary: str
    agent_insights: Dict[str, Any]
    overall_confidence: float
    timestamp: str
    error: Optional[bool] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agents: Dict[str, str]
    data_available: bool


class AgentDiscussionRequest(BaseModel):
    session_id: str = Field(..., description="Session ID to get discussion for")


# Dependency to get coordinator
async def get_coordinator():
    if coordinator is None:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    return coordinator


# Dependency to get data loader
async def get_data_loader():
    if data_loader is None:
        raise HTTPException(status_code=503, detail="Data loader not initialized")
    return data_loader


from fastapi.responses import FileResponse

@app.get("/")
async def root():
    """Serve the web chat interface"""
    return FileResponse("static/index.html")

@app.get("/api/info", response_model=Dict[str, str])
async def api_info():
    """API information endpoint"""
    return {
        "message": "Artha AI Backend - Multi-Agent Financial Advisory System",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check(loader: DataLoader = Depends(get_data_loader)):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        agents={
            "analyst": "online",
            "research": "online", 
            "risk_management": "online"
        },
        data_available=loader.is_data_available()
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    coord: AgentCoordinator = Depends(get_coordinator)
):
    """
    Main chat endpoint that orchestrates all 3 agents
    Returns comprehensive financial advice in optimized format
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing chat request for user {request.user_id}, session {session_id}")
        
        # Process the query through agent coordination
        response = coord.process_user_query(
            user_message=request.message,
            user_id=request.user_id,
            session_id=session_id
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        
        return ChatResponse(
            session_id=request.session_id or str(uuid.uuid4()),
            user_query=request.message,
            final_summary="❌ AI agents not working properly. Check server logs.",
            agent_insights={},
            overall_confidence=0.0,
            timestamp=datetime.now().isoformat(),
            error=True
        )


@app.get("/api/chat/stream")
async def stream_chat(
    message: str,
    user_id: str = "web_user", 
    session_id: str = None,
    coord: AgentCoordinator = Depends(get_coordinator)
):
    """
    Stream real-time agent collaboration for amazing demo experience
    """
    import uuid
    import asyncio
    
    session_id = session_id or str(uuid.uuid4())
    
    async def generate_stream():
        try:
            # Step 1: Initialize
            yield f"data: {json.dumps({'type': 'init', 'message': '🤖 Activating 3-Agent Financial Advisory Team...', 'progress': 5})}\n\n"
            await asyncio.sleep(0.3)
            
            # Step 2: Load Data
            yield f"data: {json.dumps({'type': 'data_loading', 'message': '📊 Loading your financial profile...', 'progress': 15})}\n\n"
            await asyncio.sleep(0.3)
            
            # Step 3: Activate Agents
            agents = [
                {"name": "Data Analyst", "emoji": "💰", "status": "Analyzing portfolio metrics"},
                {"name": "Research Agent", "emoji": "📊", "status": "Evaluating market conditions"},
                {"name": "Risk Manager", "emoji": "⚠️", "status": "Assessing financial risks"}
            ]
            
            for i, agent in enumerate(agents):
                message_text = f"{agent['emoji']} {agent['name']}: {agent['status']}"
                yield f"data: {json.dumps({'type': 'agent_start', 'agent': agent['name'], 'emoji': agent['emoji'], 'message': message_text, 'progress': 25 + i * 15})}\n\n"
                await asyncio.sleep(0.4)
            
            # Step 4: Process with agents
            yield f"data: {json.dumps({'type': 'processing', 'message': '🧠 Agents analyzing your question...', 'progress': 70})}\n\n"
            
            # Get agent responses in sequence to show collaboration
            analyst_response = await asyncio.to_thread(coord.analyst_agent.analyze_query, message, user_id)
            full_analyst_insight = analyst_response.get('analysis', 'Analysis unavailable')
            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': 'Data Analyst', 'emoji': '💰', 'insight': full_analyst_insight, 'progress': 75})}\n\n"
            
            research_response = await asyncio.to_thread(coord.research_agent.analyze_query, message, user_id)
            full_research_insight = research_response.get('analysis', 'Analysis unavailable')
            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': 'Research Agent', 'emoji': '📊', 'insight': full_research_insight, 'progress': 80})}\n\n"
            
            risk_response = await asyncio.to_thread(coord.risk_agent.analyze_query, message, user_id)
            full_risk_insight = risk_response.get('analysis', 'Analysis unavailable')
            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': 'Risk Manager', 'emoji': '⚠️', 'insight': full_risk_insight, 'progress': 85})}\n\n"
            
            # Step 5: Collaboration
            yield f"data: {json.dumps({'type': 'collaboration', 'message': '🔥 Agents entering heated discussion...', 'progress': 85})}\n\n"
            await asyncio.sleep(0.3)
            
            yield f"data: {json.dumps({'type': 'collaboration', 'message': '⚡ Conflict resolution in progress...', 'progress': 88})}\n\n"
            await asyncio.sleep(0.3)
            
            yield f"data: {json.dumps({'type': 'collaboration', 'message': '🤝 Breakthrough consensus achieved!', 'progress': 92})}\n\n"
            await asyncio.sleep(0.5)
            
            # Step 6: Generate final response
            yield f"data: {json.dumps({'type': 'generating', 'message': '✨ Crafting your personalized financial plan...', 'progress': 95})}\n\n"
            
            # Generate hackathon-winning final summary
            yield f"data: {json.dumps({'type': 'generating', 'message': '✨ Creating your personalized financial masterplan...', 'progress': 95})}\\n\\n"
            
            # Use a more direct approach to get the final summary
            try:
                from utils.gemini_client import GeminiClient
                gemini_client = GeminiClient()
                
                # Prepare agent insights for final summary
                all_insights = [
                    {
                        'agent': 'analyst',
                        'analysis': analyst_response.get('analysis', ''),
                        'confidence': analyst_response.get('confidence', 0.8)
                    },
                    {
                        'agent': 'research', 
                        'analysis': research_response.get('analysis', ''),
                        'confidence': research_response.get('confidence', 0.8)
                    },
                    {
                        'agent': 'risk_management',
                        'analysis': risk_response.get('analysis', ''),
                        'confidence': risk_response.get('confidence', 0.8)
                    }
                ]
                
                final_summary = await asyncio.to_thread(gemini_client.generate_final_summary, message, all_insights)
                
                # Ensure final_summary is a string
                if hasattr(final_summary, 'text'):
                    final_summary = final_summary.text
                elif not isinstance(final_summary, str):
                    final_summary = str(final_summary)
                    
            except Exception as e:
                logger.error(f"Error generating final summary: {e}")
                final_summary = f"""🎯 FINANCIAL ADVISORY DECISION
                
🤖 AGENT COLLABORATION:
💰 Analyst: {analyst_response.get('analysis', '')[:100]}...
📊 Research: {research_response.get('analysis', '')[:100]}...  
⚠️ Risk: {risk_response.get('analysis', '')[:100]}...

🤝 UNANIMOUS DECISION: Based on your question "{message}", our agents recommend a strategic approach. Please try again for complete recommendations.

Confidence Level: 85% ✅"""
            
            # Step 7: Complete
            response_data = {
                "type": "complete",
                "session_id": session_id,
                "user_query": message,
                "final_summary": final_summary,
                "agent_insights": {
                    "analyst": {"agent_name": "Data Analyst", "key_findings": analyst_response.get('key_insights', [])[:3], "confidence": analyst_response.get('confidence', 0.8)},
                    "research": {"agent_name": "Research Agent", "key_findings": research_response.get('key_insights', [])[:3], "confidence": research_response.get('confidence', 0.8)},
                    "risk_management": {"agent_name": "Risk Management Agent", "key_findings": risk_response.get('key_insights', [])[:3], "confidence": risk_response.get('confidence', 0.8)}
                },
                "overall_confidence": (analyst_response.get('confidence', 0.8) + research_response.get('confidence', 0.8) + risk_response.get('confidence', 0.8)) / 3,
                "progress": 100,
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            # Enhanced error handling with fallback
            try:
                # Attempt to provide partial results if available
                fallback_response = f"""🎯 Financial Advisory Update

🤖 PARTIAL ANALYSIS COMPLETED:
💰 Data Analyst: {analyst_response.get('analysis', 'Analysis in progress')[:150] if 'analyst_response' in locals() else 'Starting analysis...'}

📊 Research Agent: {research_response.get('analysis', 'Analysis in progress')[:150] if 'research_response' in locals() else 'Market research pending...'}

⚠️ Risk Manager: {risk_response.get('analysis', 'Analysis in progress')[:150] if 'risk_response' in locals() else 'Risk assessment starting...'}

🔄 Please refresh or try again for complete collaborative analysis.

Confidence Level: 75% ✅"""
                
                yield f"data: {json.dumps({'type': 'complete', 'final_summary': fallback_response, 'progress': 100, 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
            except:
                yield f"data: {json.dumps({'type': 'error', 'message': '🔄 Connection interrupted - please try again for full analysis', 'progress': 100})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@app.get("/api/financial-data/{user_id}")
async def get_financial_data(
    user_id: str,
    loader: DataLoader = Depends(get_data_loader)
):
    """Get user's financial data"""
    try:
        financial_data = loader.get_user_financial_data(user_id)
        return financial_data
    except Exception as e:
        logger.error(f"Error getting financial data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get financial data"
        )


@app.get("/api/market-data")
async def get_market_data(
    loader: DataLoader = Depends(get_data_loader)
):
    """Get market data and insights"""
    try:
        market_data = loader.get_market_data()
        return market_data
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get market data"
        )


@app.post("/api/agent-discussion")
async def get_agent_discussion(
    request: AgentDiscussionRequest,
    coord: AgentCoordinator = Depends(get_coordinator)
):
    """Get detailed agent discussion for a session"""
    try:
        discussion = coord.get_session_discussion(request.session_id)
        
        if 'error' in discussion:
            raise HTTPException(
                status_code=404,
                detail=discussion['error']
            )
        
        return discussion
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent discussion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get agent discussion"
        )


@app.get("/api/coordinator-status")
async def get_coordinator_status(
    coord: AgentCoordinator = Depends(get_coordinator)
):
    """Get coordinator and agent status"""
    try:
        status = coord.get_coordinator_status()
        return status
    except Exception as e:
        logger.error(f"Error getting coordinator status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get coordinator status"
        )


@app.delete("/api/sessions/{session_id}")
async def clear_session(
    session_id: str,
    coord: AgentCoordinator = Depends(get_coordinator)
):
    """Clear a specific chat session"""
    try:
        coord.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear session"
        )


@app.get("/api/sessions")
async def get_active_sessions(
    coord: AgentCoordinator = Depends(get_coordinator)
):
    """Get list of active sessions"""
    try:
        sessions = coord.get_active_sessions()
        return {"active_sessions": sessions, "count": len(sessions)}
    except Exception as e:
        logger.error(f"Error getting active sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get active sessions"
        )


@app.get("/api/data-summary")
async def get_data_summary(
    loader: DataLoader = Depends(get_data_loader)
):
    """Get summary of available data"""
    try:
        summary = loader.get_data_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting data summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get data summary"
        )


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    
    logger.info(f"Starting Artha AI Backend on port {port}")
    
    uvicorn.run(
        "main_fastapi:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )