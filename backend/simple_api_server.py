"""Simplified FastAPI server for Artha-Agent frontend"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    user_data: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None

class ConversationCreate(BaseModel):
    user_id: str
    title: Optional[str] = "New Conversation"

# In-memory storage for demo
conversations = {}
messages = {}

# Create FastAPI app
app = FastAPI(title="Artha AI Backend API - Simplified", version="1.0.0")

# Enable CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "https://localhost:3000",
    "https://localhost:3001",
    "https://localhost:3002",
    "https://localhost:3003",
    "https://localhost:3004"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Accept", 
        "Origin", 
        "X-Requested-With",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
        "Cache-Control",
        "Pragma"
    ],
    expose_headers=["X-Total-Count", "Access-Control-Allow-Origin"],
    max_age=600,
)

@app.get("/")
async def root():
    return {"message": "Artha AI Backend API - Simplified", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Chat endpoints
@app.post("/api/chat/conversations")
async def create_conversation(conversation: ConversationCreate):
    conversation_id = str(uuid.uuid4())
    conversations[conversation_id] = {
        "id": conversation_id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    messages[conversation_id] = []
    logger.info(f"✅ Created conversation {conversation_id}")
    return conversations[conversation_id]

@app.get("/api/chat/conversations")
async def get_conversations(user_id: str):
    user_conversations = [
        conv for conv in conversations.values() 
        if conv["user_id"] == user_id
    ]
    return user_conversations

@app.get("/api/chat/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, user_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[conversation_id]
    if conversation["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    conversation_messages = messages.get(conversation_id, [])
    logger.info(f"✅ Retrieved conversation {conversation_id} with {len(conversation_messages)} messages")
    
    return {
        **conversation,
        "messages": conversation_messages
    }

@app.post("/api/chat/messages")
async def add_message(message: ChatMessage):
    if message.conversation_id and message.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Create conversation if not provided
    if not message.conversation_id:
        conversation_id = str(uuid.uuid4())
        conversations[conversation_id] = {
            "id": conversation_id,
            "user_id": message.user_id,
            "title": message.message[:50] + "..." if len(message.message) > 50 else message.message,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        messages[conversation_id] = []
        message.conversation_id = conversation_id
    
    # Add message
    new_message = {
        "id": str(uuid.uuid4()),
        "conversation_id": message.conversation_id,
        "content": message.message,
        "role": "user",
        "timestamp": datetime.now().isoformat()
    }
    
    messages[message.conversation_id].append(new_message)
    conversations[message.conversation_id]["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"✅ Added user message to conversation {message.conversation_id}")
    return new_message

# Stream query endpoint
@app.post("/api/stream/query")
async def stream_query(request: QueryRequest):
    async def generate_response():
        # Simulate AI response
        responses = [
            "I'm analyzing your financial query...",
            "Based on current market conditions...",
            "Here are my recommendations:",
            "1. Consider diversifying your portfolio",
            "2. Monitor market trends closely",
            "3. Maintain a balanced risk profile",
            "This analysis is based on current market data and your profile."
        ]
        
        for i, response in enumerate(responses):
            chunk = {
                "type": "content",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "chunk_id": i
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.5)  # Simulate processing time
        
        # Final chunk
        final_chunk = {
            "type": "done",
            "content": "",
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

# Stock proxy endpoint
@app.get("/api/stocks/proxy")
async def stock_proxy(action: str, symbol: Optional[str] = None):
    if action == "top-stocks":
        # Mock top Indian stocks data
        mock_stocks = [
            {"symbol": "RELIANCE", "price": 2500.50, "change": "+1.2%", "name": "Reliance Industries"},
            {"symbol": "TCS", "price": 3200.75, "change": "+0.8%", "name": "Tata Consultancy Services"},
            {"symbol": "HDFCBANK", "price": 1650.25, "change": "-0.5%", "name": "HDFC Bank"},
            {"symbol": "INFY", "price": 1450.80, "change": "+1.5%", "name": "Infosys"},
            {"symbol": "ICICIBANK", "price": 950.30, "change": "+0.3%", "name": "ICICI Bank"},
            {"symbol": "HINDUNILVR", "price": 2800.90, "change": "-0.2%", "name": "Hindustan Unilever"},
            {"symbol": "ITC", "price": 420.15, "change": "+0.7%", "name": "ITC Limited"},
            {"symbol": "SBIN", "price": 580.45, "change": "+1.1%", "name": "State Bank of India"},
            {"symbol": "BHARTIARTL", "price": 850.60, "change": "-0.8%", "name": "Bharti Airtel"},
            {"symbol": "KOTAKBANK", "price": 1750.25, "change": "+0.4%", "name": "Kotak Mahindra Bank"}
        ]
        logger.info(f"📊 Returning mock top 10 Indian stocks")
        return {"stocks": mock_stocks, "status": "success"}
    
    return {"error": "Unsupported action", "status": "error"}

# Regular query endpoint (fallback)
@app.post("/query")
async def regular_query(request: QueryRequest):
    return {
        "response": "This is a simplified response. The full AI system is being initialized.",
        "query": request.query,
        "timestamp": datetime.now().isoformat(),
        "status": "simplified_mode"
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Artha AI Simplified Backend Server")
    logger.info("🔧 Server will start at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)