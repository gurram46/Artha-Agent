"""
Secure Session Management Endpoints for Artha AI
Provides server-side session storage for sensitive user data
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import redis
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/session", tags=["session"])

# Redis connection for session storage
try:
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_client = redis.from_url(redis_url, decode_responses=True)
    redis_client.ping()  # Test connection
    logger.info("✅ Redis connected for session management")
except Exception as e:
    logger.warning(f"⚠️ Redis not available, using in-memory storage: {e}")
    redis_client = None

# Fallback in-memory storage (not recommended for production)
memory_sessions: Dict[str, Dict[str, Any]] = {}
session_expiry: Dict[str, datetime] = {}

class SessionRequest(BaseModel):
    sessionId: str
    key: str
    value: Optional[str] = None

class SessionResponse(BaseModel):
    success: bool
    value: Optional[str] = None
    message: Optional[str] = None

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    if not session_id or not session_id.startswith('sess_'):
        return False
    if len(session_id) < 10 or len(session_id) > 50:
        return False
    return True

def get_session_key(session_id: str, key: str) -> str:
    """Generate Redis key for session data"""
    return f"artha_session:{session_id}:{key}"

def get_session_expiry_key(session_id: str) -> str:
    """Generate Redis key for session expiry"""
    return f"artha_session_expiry:{session_id}"

async def cleanup_expired_sessions():
    """Clean up expired sessions (for memory storage)"""
    if redis_client:
        return  # Redis handles expiry automatically
    
    current_time = datetime.utcnow()
    expired_sessions = [
        session_id for session_id, expiry in session_expiry.items()
        if expiry < current_time
    ]
    
    for session_id in expired_sessions:
        if session_id in memory_sessions:
            del memory_sessions[session_id]
        if session_id in session_expiry:
            del session_expiry[session_id]

@router.post("/set", response_model=SessionResponse)
async def set_session_data(request: SessionRequest, req: Request):
    """Store data in secure server-side session"""
    try:
        # Validate session ID
        if not validate_session_id(request.sessionId):
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        # Validate key
        if not request.key or len(request.key) > 100:
            raise HTTPException(status_code=400, detail="Invalid key")
        
        # Validate value size (max 1MB)
        if request.value and len(request.value) > 1024 * 1024:
            raise HTTPException(status_code=400, detail="Value too large")
        
        client_ip = get_client_ip(req)
        expiry_time = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
        
        if redis_client:
            # Store in Redis with expiry
            session_key = get_session_key(request.sessionId, request.key)
            redis_client.setex(session_key, 86400, request.value or "")  # 24 hours
            
            # Store session metadata
            metadata = {
                "created_at": datetime.utcnow().isoformat(),
                "client_ip": client_ip,
                "last_accessed": datetime.utcnow().isoformat()
            }
            metadata_key = get_session_key(request.sessionId, "_metadata")
            redis_client.setex(metadata_key, 86400, json.dumps(metadata))
        else:
            # Fallback to memory storage
            await cleanup_expired_sessions()
            
            if request.sessionId not in memory_sessions:
                memory_sessions[request.sessionId] = {}
            
            memory_sessions[request.sessionId][request.key] = request.value
            session_expiry[request.sessionId] = expiry_time
        
        logger.info(f"✅ Session data set for {request.sessionId}:{request.key}")
        return SessionResponse(success=True, message="Data stored successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error setting session data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/get", response_model=SessionResponse)
async def get_session_data(request: SessionRequest, req: Request):
    """Retrieve data from secure server-side session"""
    try:
        # Validate session ID
        if not validate_session_id(request.sessionId):
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        if redis_client:
            # Get from Redis
            session_key = get_session_key(request.sessionId, request.key)
            value = redis_client.get(session_key)
            
            if value is not None:
                # Update last accessed time
                metadata_key = get_session_key(request.sessionId, "_metadata")
                existing_metadata = redis_client.get(metadata_key)
                if existing_metadata:
                    metadata = json.loads(existing_metadata)
                    metadata["last_accessed"] = datetime.utcnow().isoformat()
                    redis_client.setex(metadata_key, 86400, json.dumps(metadata))
                
                return SessionResponse(success=True, value=value)
        else:
            # Get from memory storage
            await cleanup_expired_sessions()
            
            if (request.sessionId in memory_sessions and 
                request.key in memory_sessions[request.sessionId]):
                value = memory_sessions[request.sessionId][request.key]
                return SessionResponse(success=True, value=value)
        
        return SessionResponse(success=True, value=None)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting session data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/remove", response_model=SessionResponse)
async def remove_session_data(request: SessionRequest, req: Request):
    """Remove specific data from session"""
    try:
        # Validate session ID
        if not validate_session_id(request.sessionId):
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        if redis_client:
            # Remove from Redis
            session_key = get_session_key(request.sessionId, request.key)
            redis_client.delete(session_key)
        else:
            # Remove from memory storage
            if (request.sessionId in memory_sessions and 
                request.key in memory_sessions[request.sessionId]):
                del memory_sessions[request.sessionId][request.key]
        
        logger.info(f"✅ Session data removed for {request.sessionId}:{request.key}")
        return SessionResponse(success=True, message="Data removed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error removing session data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/clear", response_model=SessionResponse)
async def clear_session(request: SessionRequest, req: Request):
    """Clear all session data"""
    try:
        # Validate session ID
        if not validate_session_id(request.sessionId):
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        if redis_client:
            # Clear all session keys from Redis
            pattern = f"artha_session:{request.sessionId}:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
        else:
            # Clear from memory storage
            if request.sessionId in memory_sessions:
                del memory_sessions[request.sessionId]
            if request.sessionId in session_expiry:
                del session_expiry[request.sessionId]
        
        logger.info(f"✅ Session cleared for {request.sessionId}")
        return SessionResponse(success=True, message="Session cleared successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error clearing session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def session_health():
    """Health check for session service"""
    try:
        if redis_client:
            redis_client.ping()
            storage_type = "Redis"
        else:
            storage_type = "Memory"
        
        return {
            "status": "healthy",
            "storage_type": storage_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Session health check failed: {e}")
        raise HTTPException(status_code=503, detail="Session service unavailable")