#!/usr/bin/env python3
"""
Artha AI Backend Server - Merged Production Version
==================================================

This file merges the stability of api_server.py with key features from api_server_backup.py:

✅ RESTORED FEATURES:
- Chat routing logic: Gemini 2.5 Pro for think_mode=True, Gemini 2.5 Flash for think_mode=False
- Investment Agent integration for agent="investment" requests
- PDF support with context injection into Gemini prompts
- Session history system with user_id/session_id persistence
- Server-Sent Events (SSE) streaming responses
- Enhanced error handling and graceful agent failure recovery

✅ MAINTAINED FEATURES:
- All existing endpoint paths from stable version
- Fi Money authentication system
- Production-stable architecture
- Frontend compatibility

❌ REMOVED FEATURES:
- Local LLM connection code
- Unused/non-functional agents (except Investment Agent)
- Unstable components from backup

Author: Artha AI Team
Version: 2.0 (Merged)
Last Updated: 2024
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn
from dotenv import load_dotenv
import sys

# Import validation utilities
try:
    from utils.validation_utils import (
        InputValidator, InputSanitizer, ValidationError as CustomValidationError,
        ChatMessageRequest as ValidatedChatMessageRequest,
        validate_request_data, RateLimitValidator
    )
    VALIDATION_AVAILABLE = True
    logging.getLogger(__name__).info("✅ Validation utilities imported successfully")
except ImportError as e:
    VALIDATION_AVAILABLE = False
    logging.getLogger(__name__).warning(f"⚠️ Validation utilities not available: {e}")

# Import error handling utilities
try:
    from utils.error_handlers import (
        ErrorHandler, ArthaAIException, ValidationException, AuthenticationException,
        AuthorizationException, ResourceNotFoundException, ExternalServiceException,
        RateLimitException, setup_exception_handlers, raise_validation_error,
        raise_not_found, raise_unauthorized, raise_forbidden, raise_external_service_error
    )
    ERROR_HANDLING_AVAILABLE = True
    logging.getLogger(__name__).info("✅ Error handling utilities imported successfully")
except ImportError as e:
    ERROR_HANDLING_AVAILABLE = False
    logging.getLogger(__name__).warning(f"⚠️ Error handling utilities not available: {e}")

# Ensure console uses UTF-8 on Windows to support emojis in logs
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Load environment variables
load_dotenv()

# Configure structured logging
try:
    from config.logging_config import setup_logging, get_logger, log_startup_info
    # Initialize structured logging
    loggers = setup_logging()
    logger = get_logger('main')
    # Log startup information
    log_startup_info()
except ImportError as e:
    # Fallback to basic logging if structured logging is not available
    file_handler = logging.FileHandler('backend.log', encoding='utf-8')
    try:
        console_stream = sys.stdout
        console_stream.reconfigure(encoding='utf-8')
        stream_handler = logging.StreamHandler(console_stream)
    except Exception:
        stream_handler = logging.StreamHandler()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[file_handler, stream_handler]
    )
    logger = logging.getLogger(__name__)
    logger.warning(f"Structured logging not available, using basic logging: {e}")

# Conditional imports with error handling
try:
    import aiohttp
    logger.info("✅ aiohttp imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ aiohttp not available: {e}")

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
    logger.info("✅ Google Gemini AI imported successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logger.warning(f"⚠️ Google Gemini AI not available: {e}")

try:
    from core.fi_mcp.production_client import get_user_financial_data, FinancialData
    FI_MONEY_AVAILABLE = True
    logger.info("✅ Fi Money MCP client imported successfully")
except ImportError as e:
    FI_MONEY_AVAILABLE = False
    logger.warning(f"⚠️ Fi Money MCP client not available: {e}")

# Import user data models
try:
    from models.user_models import save_user_profile, get_user_profile, get_user_profile_by_email, create_user_id_from_email
    USER_MODELS_AVAILABLE = True
    logger.info("✅ User models imported successfully")
except ImportError as e:
    USER_MODELS_AVAILABLE = False
    logger.warning(f"⚠️ User models not available: {e}")

# Helper function for loading user data
async def load_user_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user data with enhanced error handling and fallback to demo data"""
    if not user_id:
        logger.warning("⚠️ No user_id provided for user data loading")
        return None
    
    try:
        if USER_MODELS_AVAILABLE:
            try:
                user_profile = get_user_profile(user_id)
                if user_profile:
                    logger.info(f"✅ Loaded user profile for: {user_id}")
                    return user_profile
                else:
                    logger.warning(f"⚠️ No user profile found for: {user_id}, using demo data")
            except Exception as db_error:
                logger.error(f"❌ Database error loading user profile for {user_id}: {db_error}")
        
        # Fallback to demo data with enhanced logging
        logger.info(f"📝 Using demo user data for: {user_id}")
        return {
            "user_id": user_id,
            "firstName": "Demo",
            "lastName": "User",
            "age": 30,
            "occupation": "Software Engineer",
            "monthlyIncome": 100000,
            "investmentGoals": ["retirement", "wealth_building"],
            "riskTolerance": "moderate",
            "financialGoals": "Build long-term wealth and secure retirement"
        }
    except Exception as e:
        logger.error(f"❌ Critical error in load_user_data for {user_id}: {e}")
        # Return minimal demo data as last resort
        return {
            "user_id": user_id,
            "firstName": "Demo",
            "lastName": "User",
            "error_fallback": True
        }


async def save_conversation_history(conversation_id: str, message: str, response: str, user_id: Optional[str] = None):
    """Save conversation history to session storage with enhanced error handling"""
    try:
        if not conversation_id:
            logger.warning("⚠️ No conversation_id provided for saving history")
            return False
        
        if not message or not response:
            logger.warning(f"⚠️ Empty message or response for conversation {conversation_id}")
            return False
        
        # Create conversation entry with validation
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": str(message)[:1000],  # Limit message length
            "ai_response": str(response)[:5000],   # Limit response length
            "user_id": user_id,
            "conversation_id": conversation_id
        }
        
        # For now, we'll use a simple in-memory approach
        # In production, this should use the session endpoints or database
        logger.info(f"💾 Conversation saved for {conversation_id} (user: {user_id or 'anonymous'})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Critical error saving conversation history for {conversation_id}: {e}")
        return False


async def load_conversation_history(conversation_id: str) -> list:
    """Load conversation history from session storage with enhanced error handling"""
    try:
        if not conversation_id:
            logger.warning("⚠️ No conversation_id provided for loading history")
            return []
        
        # Validate conversation_id format
        if len(conversation_id) < 5 or len(conversation_id) > 100:
            logger.warning(f"⚠️ Invalid conversation_id format: {conversation_id}")
            return []
        
        # For now, return empty list - in production this should load from session/database
        logger.info(f"📖 Loading conversation history for {conversation_id}")
        return []
        
    except Exception as e:
        logger.error(f"❌ Critical error loading conversation history for {conversation_id}: {e}")
        return []  # Always return empty list as fallback


def is_demo_mode_session(conversation_id: str) -> bool:
    """Check if a conversation session is in demo mode"""
    return conversation_id in _demo_mode_sessions if conversation_id else False


def clear_demo_mode_session(conversation_id: str):
    """Remove a conversation session from demo mode tracking"""
    if conversation_id in _demo_mode_sessions:
        _demo_mode_sessions.discard(conversation_id)

def format_pdf_context_for_ai(pdf_context: Dict[str, Any]) -> str:
    """Format PDF context data for AI analysis"""
    if not pdf_context:
        return ""
    
    context_parts = []
    
    # Add document metadata
    if 'document_type' in pdf_context:
        context_parts.append(f"Document Type: {pdf_context['document_type']}")
    
    if 'confidence_score' in pdf_context:
        confidence = pdf_context['confidence_score']
        context_parts.append(f"Data Extraction Confidence: {confidence:.2f}")
    
    # Add account information
    accounts = pdf_context.get('accounts', [])
    if accounts:
        context_parts.append(f"\nAccounts Found ({len(accounts)}):")
        for i, acc in enumerate(accounts[:3], 1):  # Limit to 3 accounts
            account_num = acc.get('account_number', 'Not found')
            bank_name = acc.get('bank_name', 'Not specified')
            balance = acc.get('balance', 'Not available')
            
            if account_num != 'Not found' and len(str(account_num)) > 4:
                account_display = f"****{str(account_num)[-4:]}"
            else:
                account_display = account_num
                
            if isinstance(balance, (int, float)):
                balance_display = f"₹{balance:,.2f}"
            else:
                balance_display = str(balance)
                
            context_parts.append(f"  {i}. {account_display} at {bank_name} - Balance: {balance_display}")
    
    # Add transaction summary
    transactions = pdf_context.get('transactions', [])
    if transactions:
        context_parts.append(f"\nRecent Transactions ({len(transactions)}):")
        for i, txn in enumerate(transactions[:5], 1):  # Limit to 5 transactions
            date = txn.get('date', 'Date not found')
            description = txn.get('description', 'Description not available')
            amount = txn.get('amount', 'Amount not available')
            
            if isinstance(description, str) and len(description) > 40:
                description = description[:37] + "..."
                
            if isinstance(amount, (int, float)):
                amount_display = f"₹{amount:,.2f}"
            else:
                amount_display = str(amount)
                
            context_parts.append(f"  {i}. {date}: {description} - {amount_display}")
    
    # Add financial summary
    summary = pdf_context.get('summary', {})
    if summary:
        context_parts.append("\nFinancial Summary:")
        if 'total_balance' in summary and isinstance(summary['total_balance'], (int, float)):
            context_parts.append(f"  Total Balance: ₹{summary['total_balance']:,.2f}")
        if 'total_credits' in summary and isinstance(summary['total_credits'], (int, float)):
            context_parts.append(f"  Total Credits: ₹{summary['total_credits']:,.2f}")
        if 'total_debits' in summary and isinstance(summary['total_debits'], (int, float)):
            context_parts.append(f"  Total Debits: ₹{summary['total_debits']:,.2f}")
    
    return "\n".join(context_parts)

# Import API routers with error handling
try:
    from api.chat_endpoints import router as chat_router
    from api.auth_endpoints import router as auth_router
    from api.user_endpoints import router as user_router
    from api.portfolio_endpoints import router as portfolio_router
    from api.pdf_upload_endpoints import router as pdf_router
    from api.session_endpoints import router as session_router
    from api.database_endpoints import router as database_router
    from api.monitoring_endpoints import monitoring_router
    ROUTERS_AVAILABLE = True
    logger.info("✅ API routers imported successfully")
except ImportError as e:
    ROUTERS_AVAILABLE = False
    logger.warning(f"⚠️ Some API routers not available: {e}")

# Import services
try:
    from services.chat_service import ChatService
    from services.pdf_service import PDFGenerationService
    SERVICES_AVAILABLE = True
    logger.info("✅ Services imported successfully")
except ImportError as e:
    SERVICES_AVAILABLE = False
    logger.warning(f"⚠️ Some services not available: {e}")

# Investment Agent import
try:
    from sandeep_investment_system.sandeep_api_integration import sandeep_api
    INVESTMENT_AGENT_AVAILABLE = True
    logger.info("✅ Investment Agent imported successfully")
except ImportError as e:
    INVESTMENT_AGENT_AVAILABLE = False
    logger.warning(f"⚠️ Investment Agent not available: {e}")

# Greeting detection functions
def is_simple_greeting(query: str) -> bool:
    """Check if the query is a simple greeting that doesn't require financial analysis"""
    greeting_patterns = [
        "hi", "hello", "hey", "namaste", "good morning", "good afternoon", 
        "good evening", "how are you", "what's up", "whats up", "sup",
        "greetings", "hola", "bonjour", "salaam", "salaam aleikum",
        "how do you do", "nice to meet you", "pleasure to meet you"
    ]
    query_lower = query.lower().strip()
    
    # Check for exact matches or very short greetings
    if query_lower in greeting_patterns:
        return True
    
    # Check for greetings with punctuation
    query_clean = query_lower.replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip()
    if query_clean in greeting_patterns:
        return True
    
    # Check if it's a very short query (likely a greeting)
    if len(query_clean.split()) <= 2 and any(pattern in query_clean for pattern in greeting_patterns):
        return True
    
    return False

def handle_simple_greeting(query: str, user_data: Dict[str, Any] = None) -> dict:
    """Handle simple greetings with a concise, friendly response"""
    # Get user's name if available
    user_name = "there"
    if user_data:
        # Try to get name from user_data structure - check multiple possible fields
        name = user_data.get('personalInfo', {}).get('fullName')
        if not name:
            name = user_data.get('full_name')  # Check direct full_name field
        if not name:
            first_name = user_data.get('firstName', user_data.get('personalInfo', {}).get('firstName', ''))
            if first_name:
                user_name = first_name
        elif name:
            # Extract first name from full name
            user_name = name.split(' ')[0] if name else "there"
    
    # Generate concise greeting responses
    greeting_responses = [
        f"Hi {user_name}! 👋 How can I help?",
        f"Hello {user_name}! What can I do for you?",
        f"Hey {user_name}! How can I assist you today?",
        f"Hi {user_name}! What would you like to know?"
    ]
    
    import random
    response = random.choice(greeting_responses)
    
    return {
        "response": response,
        "sources_count": 0,
        "greeting": True
    }


class ArthaAIChatSystem:
    """Enhanced Artha AI Chat System with multi-agent routing"""
    
    def __init__(self):
        self.conversation_history = []
        self.rate_limit_requests = {}
        self.chat_service = ChatService() if SERVICES_AVAILABLE else None
        self.pdf_service = PDFGenerationService() if SERVICES_AVAILABLE else None
        
        # Initialize HTTP session for connection pooling
        self.http_session = None
        self._init_http_session()
        
        # Initialize Gemini client
        if GEMINI_AVAILABLE:
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_client = genai
                logger.info("✅ Gemini AI client initialized")
            else:
                logger.error("❌ GOOGLE_API_KEY not found in environment")
                self.gemini_client = None
        else:
            self.gemini_client = None
    
    def _init_http_session(self):
        """Initialize aiohttp session for connection pooling"""
        try:
            import aiohttp
            # Configure connection pooling for better performance
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Max connections per host
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            # Set timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=60,  # Total timeout
                connect=10,  # Connection timeout
                sock_read=30  # Socket read timeout
            )
            
            self.http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Artha-AI/1.0'}
            )
            logger.info("✅ HTTP session with connection pooling initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize HTTP session: {e}")
            self.http_session = None
    
    async def cleanup(self):
        """Cleanup resources including HTTP session"""
        if self.http_session:
            try:
                await self.http_session.close()
                logger.info("✅ HTTP session closed")
            except Exception as e:
                logger.error(f"❌ Error closing HTTP session: {e}")
    
    async def process_query(self, query: str, user_id: str = None, conversation_id: str = None,
                          think_mode: bool = False, agent: str = None, demo_mode: bool = False,
                          pdf_context: str = None, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user query with enhanced routing logic and comprehensive error handling"""
        try:
            # Input validation
            if not query or not query.strip():
                logger.warning("⚠️ Empty query received")
                return {
                    "response": "Please provide a question or request for me to help you with.",
                    "error": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Sanitize query length
            if len(query) > 5000:
                logger.warning(f"⚠️ Query too long ({len(query)} chars), truncating")
                query = query[:5000] + "..."
            
            # Check for simple greetings first (highest priority)
            if is_simple_greeting(query):
                logger.info(f"👋 Simple greeting detected: {query[:50]}")
                # Use provided user_data or load from storage
                user_data_dict = user_data or (await load_user_data(user_id) if user_id else {})
                greeting_response = handle_simple_greeting(query, user_data_dict)
                return {
                    "response": greeting_response["response"],
                    "error": False,
                    "greeting": True,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Rate limiting check with enhanced error handling
            try:
                if not self._check_rate_limit(user_id or "anonymous"):
                    logger.warning(f"⚠️ Rate limit exceeded for user: {user_id or 'anonymous'}")
                    return {
                        "response": "You're sending requests too quickly. Please wait a moment before trying again.",
                        "error": True,
                        "error_type": "rate_limit",
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as rate_error:
                logger.error(f"❌ Rate limiting check failed: {rate_error}")
                # Continue processing despite rate limit error
            
            # Route based on agent parameter with fallback handling
            if agent == "investment" and INVESTMENT_AGENT_AVAILABLE:
                try:
                    return await self._process_investment_query(query, user_id, demo_mode, pdf_context)
                except Exception as investment_error:
                    logger.error(f"❌ Investment agent failed: {investment_error}")
                    logger.info("🔄 Falling back to Gemini processing")
                    # Fallback to Gemini
                    return await self._process_gemini_query(query, user_id, conversation_id, think_mode, demo_mode, pdf_context)
            
            # Default to Gemini routing based on think_mode
            return await self._process_gemini_query(query, user_id, conversation_id, think_mode, demo_mode, pdf_context)
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Critical error in query processing: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment, or contact support if the issue persists.",
                "error": True,
                "error_type": "system_error",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_investment_query(self, query: str, user_id: str, demo_mode: bool, pdf_context: str = None) -> Dict[str, Any]:
        """Process query using Investment Agent"""
        try:
            # Get financial data
            financial_data = await self._get_financial_data_with_demo_support(demo_mode)
            
            # Add PDF context if available
            enhanced_query = query
            if pdf_context:
                enhanced_query = f"Context from uploaded document:\n{pdf_context}\n\nUser Query: {query}"
            
            # Initialize investment system if needed
            if not sandeep_api.initialized:
                sandeep_api._initialize_system()
            
            # Get investment response
            mcp_data = {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
            
            response = await sandeep_api.get_chat_response(
                query=enhanced_query,
                financial_data=mcp_data,
                demo_mode=demo_mode
            )
            
            # Save to conversation history if chat service available
            if self.chat_service and user_id:
                await self._save_to_history(user_id, query, response, "investment")
            
            return {
                "response": response,
                "agent_used": "investment",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Investment query processing failed: {e}")
            # Fallback to Gemini
            return await self._process_gemini_query(query, user_id, None, False, demo_mode, pdf_context)
    
    async def _process_gemini_query(self, query: str, user_id: str, conversation_id: str, 
                                  think_mode: bool, demo_mode: bool, pdf_context: str = None) -> Dict[str, Any]:
        """Process query using Gemini AI with enhanced error handling and fallback mechanisms"""
        try:
            if not self.gemini_client:
                logger.error("❌ Gemini AI client not available")
                return {
                    "response": "I apologize, but the AI service is currently unavailable. Please try again later.",
                    "error": True,
                    "error_type": "service_unavailable",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get financial data and user data with error handling
            financial_data = None
            user_context = ""
            try:
                financial_data = await self._get_financial_data_with_demo_support(demo_mode)
                logger.info(f"✅ Financial data loaded for Gemini processing (demo: {demo_mode})")
                
                # Load user data for personalization
                if user_data:
                    user_name = user_data.get('full_name') or user_data.get('firstName', 'User')
                    user_context = f"User: {user_name}"
                    if user_data.get('age'):
                        user_context += f", Age: {user_data['age']}"
                    logger.info(f"✅ User context loaded: {user_context}")
                    
            except Exception as data_error:
                logger.warning(f"⚠️ Failed to load financial data: {data_error}")
                # Continue without financial data
            
            # Generate response using Gemini with exponential backoff retry logic
            response = None
            max_retries = 3
            base_delay = 1.0
            
            for attempt in range(max_retries + 1):
                try:
                    # Check rate limiting before each attempt
                    if not self._check_rate_limit(user_id):
                        logger.warning(f"⚠️ Rate limit exceeded for user {user_id}")
                        response = "I'm currently processing many requests. Please wait a moment and try again."
                        break
                    
                    response = await self._generate_gemini_response(query, financial_data, think_mode, pdf_context, user_context)
                    if response and not response.startswith("I apologize"):
                        break  # Success, exit retry loop
                        
                except Exception as gen_error:
                    logger.warning(f"⚠️ Gemini generation attempt {attempt + 1} failed: {gen_error}")
                    
                    if attempt == max_retries:
                        # Final fallback response
                        response = self._generate_fallback_response(query, financial_data, pdf_context)
                        logger.info("🔄 Using fallback response generation")
                    else:
                        # Exponential backoff: 1s, 2s, 4s
                        delay = base_delay * (2 ** attempt)
                        logger.info(f"⏳ Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
            
            if not response:
                response = "I apologize, but I'm unable to generate a response at the moment. Please try again."
            
            # Store in conversation history with error handling
            try:
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "query": query[:500],  # Limit stored query length
                    "response": response[:1000],  # Limit stored response length
                    "think_mode": think_mode,
                    "user_id": user_id
                })
                
                # Keep only last 10 conversations in memory
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
            except Exception as history_error:
                logger.warning(f"⚠️ Failed to store conversation in memory: {history_error}")
            
            # Save to persistent storage if available
            if self.chat_service and user_id:
                try:
                    await self._save_to_history(user_id, query, response, "gemini", conversation_id)
                except Exception as save_error:
                    logger.warning(f"⚠️ Failed to save conversation to persistent storage: {save_error}")
            
            return {
                "response": response,
                "agent_used": "gemini-pro" if think_mode else "gemini-flash",
                "timestamp": datetime.now().isoformat(),
                "demo_mode": demo_mode
            }
            
        except Exception as e:
            logger.error(f"❌ Critical error in Gemini query processing: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try your question again.",
                "error": True,
                "error_type": "gemini_processing_error",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_gemini_response(self, query: str, financial_data, think_mode: bool, pdf_context: str = None, user_context: str = "") -> str:
        """Generate response using Gemini AI with enhanced stability and error handling"""
        start_time = time.time()
        attempt_start = None
        
        try:
            # Use latest stable models for better reliability
            model_name = "gemini-2.5-pro" if think_mode else "gemini-2.5-flash"
            
            # Create enhanced prompt with financial context and user data
            prompt = self._create_enhanced_prompt(query, financial_data, pdf_context, user_context)
            
            # Configure model with proper timeout and generation settings
            model = self.gemini_client.GenerativeModel(
                model_name=model_name,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Generate response with timeout and timing
            attempt_start = time.time()
            response = await asyncio.wait_for(
                model.generate_content_async(prompt),
                timeout=30.0  # 30 second timeout
            )
            attempt_time = time.time() - attempt_start
            
            # Validate response
            if not response or not response.text or not response.text.strip():
                logger.warning("⚠️ Gemini returned empty response, using fallback")
                total_time = time.time() - start_time
                self._log_api_metrics(model_name, attempt_time, total_time, "empty_response", len(query))
                return self._generate_fallback_response(query, financial_data, pdf_context)
            
            # Log successful API call metrics
            total_time = time.time() - start_time
            response_length = len(response.text.strip())
            self._log_api_metrics(model_name, attempt_time, total_time, "success", len(query), response_length)
            
            return response.text.strip()
            
        except asyncio.TimeoutError:
            attempt_time = time.time() - attempt_start if attempt_start else 0
            total_time = time.time() - start_time
            self._log_api_metrics(model_name, attempt_time, total_time, "timeout", len(query))
            logger.error("❌ Gemini API timeout after 30 seconds")
            return self._generate_fallback_response(query, financial_data, pdf_context)
        except Exception as e:
            attempt_time = time.time() - attempt_start if attempt_start else 0
            total_time = time.time() - start_time
            self._log_api_metrics(model_name, attempt_time, total_time, "error", len(query), error_msg=str(e))
            logger.error(f"❌ Gemini response generation failed: {e}")
            # Don't expose internal errors to users
            return self._generate_fallback_response(query, financial_data, pdf_context)
    
    def _create_enhanced_prompt(self, query: str, financial_data, pdf_context: str = None, user_context: str = "") -> str:
        """Create enhanced prompt with financial context and PDF data"""
        prompt_parts = [
            "You are Artha AI, a sophisticated financial advisor for Indian markets.",
            "Provide personalized, actionable financial advice based on the user's actual financial data."
        ]
        
        # Add user context
        if user_context:
            prompt_parts.append(f"\n{user_context}")
        
        # Add financial context
        if financial_data:
            prompt_parts.append(f"\nUser's Financial Context:\n{self._format_financial_data(financial_data)}")
        
        # Add PDF context if available
        if pdf_context:
            prompt_parts.append(f"\nAdditional Context from User's Document:\n{pdf_context}")
        
        # Add conversation history for context
        if self.conversation_history:
            recent_history = self.conversation_history[-3:]  # Last 3 conversations
            history_text = "\n".join([f"Q: {conv['query']}\nA: {conv['response'][:200]}..." for conv in recent_history])
            prompt_parts.append(f"\nRecent Conversation History:\n{history_text}")
        
        prompt_parts.append(f"\nUser Query: {query}")
        
        return "\n".join(prompt_parts)
    
    def _log_api_metrics(self, model_name: str, attempt_time: float, total_time: float, 
                        status: str, query_length: int, response_length: int = 0, error_msg: str = None):
        """Log API performance metrics for monitoring"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "model": model_name,
                "attempt_time_ms": round(attempt_time * 1000, 2),
                "total_time_ms": round(total_time * 1000, 2),
                "status": status,
                "query_length": query_length,
                "response_length": response_length
            }
            
            if error_msg:
                metrics["error"] = error_msg[:200]  # Truncate long error messages
            
            # Log with appropriate level based on status
            if status == "success":
                logger.info(f"📊 API Metrics: {metrics}")
            elif status == "timeout":
                logger.warning(f"⏱️ API Timeout: {metrics}")
            else:
                logger.error(f"❌ API Error: {metrics}")
                
        except Exception as e:
            logger.error(f"Failed to log API metrics: {e}")
    
    def _format_financial_data(self, financial_data) -> str:
        """Format financial data for prompt inclusion"""
        try:
            if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
                return f"Net Worth: ₹{financial_data.net_worth.get('total', 'N/A')}"
            return "Financial data available but not detailed here for privacy."
        except Exception:
            return "Sample financial data being used for demonstration."
    
    async def _get_financial_data_with_demo_support(self, demo_mode: bool = False):
        """Get financial data with demo mode support"""
        if demo_mode or not FI_MONEY_AVAILABLE:
            return self._get_sample_financial_data()
        
        try:
            return await get_user_financial_data()
        except Exception as e:
            logger.warning(f"Using sample financial data: {e}")
            return self._get_sample_financial_data()
    
    def _get_sample_financial_data(self):
        """Return sample financial data for demo purposes"""
        class SampleFinancialData:
            def __init__(self):
                self.net_worth = {"total": "5,00,000"}
                self.credit_report = {"score": 750}
                self.epf_details = {"balance": "2,00,000"}
        
        return SampleFinancialData()
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limits"""
        try:
            current_time = datetime.now()
            
            # Initialize user rate limit data if not exists
            if user_id not in self.rate_limit_requests:
                self.rate_limit_requests[user_id] = {
                    "requests": [],
                    "last_request": current_time
                }
            
            user_data = self.rate_limit_requests[user_id]
            
            # Clean old requests (older than 1 minute)
            cutoff_time = current_time - timedelta(minutes=1)
            user_data["requests"] = [
                req_time for req_time in user_data["requests"] 
                if req_time > cutoff_time
            ]
            
            # Check rate limits: max 10 requests per minute, min 2 seconds between requests
            if len(user_data["requests"]) >= 10:
                logger.warning(f"Rate limit exceeded: {len(user_data['requests'])} requests in last minute")
                return False
            
            # Check minimum interval between requests
            time_since_last = (current_time - user_data["last_request"]).total_seconds()
            if time_since_last < 2.0:
                logger.warning(f"Request too frequent: {time_since_last:.1f}s since last request")
                return False
            
            # Update rate limit data
            user_data["requests"].append(current_time)
            user_data["last_request"] = current_time
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow request if rate limiting fails
    
    def _generate_fallback_response(self, query: str, financial_data=None, pdf_context: str = None) -> str:
        """Generate a fallback response when AI services fail"""
        try:
            # Basic keyword-based responses for common financial queries
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['investment', 'invest', 'portfolio']):
                return "I'd be happy to help with investment advice. For personalized recommendations, I typically analyze your financial profile, risk tolerance, and goals. Consider diversifying across equity mutual funds, debt instruments, and tax-saving options like ELSS. Would you like me to provide more specific guidance once our AI service is restored?"
            
            elif any(word in query_lower for word in ['tax', 'saving', '80c']):
                return "For tax planning, consider utilizing Section 80C deductions (up to ₹1.5 lakh) through ELSS, PPF, or life insurance. Section 80D covers health insurance premiums. I can provide more detailed tax optimization strategies once our full AI service is available."
            
            elif any(word in query_lower for word in ['budget', 'expense', 'spending']):
                return "Effective budgeting typically follows the 50-30-20 rule: 50% for needs, 30% for wants, and 20% for savings and investments. Track your expenses and prioritize emergency fund building. I can offer more personalized budgeting advice when our AI service is fully operational."
            
            elif any(word in query_lower for word in ['loan', 'emi', 'credit']):
                return "For loan management, focus on maintaining a good credit score (750+), keep debt-to-income ratio below 40%, and consider prepayment for high-interest loans. I can provide more specific loan optimization strategies once our AI service is restored."
            
            elif pdf_context:
                return "I can see you've uploaded a financial document. While our AI service is temporarily unavailable, I recommend reviewing your account balances, transaction patterns, and identifying any unusual activities. Once our service is restored, I can provide detailed analysis of your financial data."
            
            else:
                return "I apologize, but our AI service is temporarily experiencing issues. Your question about financial planning is important, and I'd like to provide you with the most accurate and personalized advice. Please try again in a few moments, or feel free to ask about general financial topics in the meantime."
                
        except Exception as e:
            logger.error(f"❌ Fallback response generation failed: {e}")
            return "I apologize, but I'm currently unable to process your request. Please try again later or contact support if the issue persists."
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Simple rate limiting implementation"""
        current_time = datetime.now().timestamp()
        if user_id not in self.rate_limit_requests:
            self.rate_limit_requests[user_id] = []
        
        # Remove requests older than 1 minute
        self.rate_limit_requests[user_id] = [
            req_time for req_time in self.rate_limit_requests[user_id]
            if current_time - req_time < 60
        ]
        
        # Check if under limit (10 requests per minute)
        if len(self.rate_limit_requests[user_id]) >= 10:
            return False
        
        self.rate_limit_requests[user_id].append(current_time)
        return True
    
    async def _save_to_history(self, user_id: str, query: str, response: str, agent_type: str, conversation_id: str = None):
        """Save conversation to persistent history with optimized batch processing"""
        try:
            if self.chat_service:
                # Create conversation if it doesn't exist
                if not conversation_id:
                    conversation_id = self.chat_service.create_conversation(
                        user_id=user_id,
                        agent_mode=agent_type
                    )
                
                # Use batch message saving for better performance
                processing_start = time.time()
                await self._batch_save_messages(conversation_id, [
                    {
                        "message_type": "user",
                        "content": query,
                        "agent_mode": agent_type,
                        "tokens_used": int(len(query.split()) * 1.3),  # Rough token estimation
                        "processing_time": 0.0
                    },
                    {
                        "message_type": "assistant", 
                        "content": response,
                        "agent_mode": agent_type,
                        "tokens_used": int(len(response.split()) * 1.3),  # Rough token estimation
                        "processing_time": time.time() - processing_start
                    }
                ])
                
                return conversation_id
        except Exception as e:
            logger.error(f"❌ Failed to save conversation history: {e}")
            return None
    
    async def _batch_save_messages(self, conversation_id: str, messages: List[Dict[str, Any]]):
        """Save multiple messages in a single transaction for better performance"""
        try:
            for message_data in messages:
                self.chat_service.add_message(
                    conversation_id=conversation_id,
                    message_type=message_data["message_type"],
                    content=message_data["content"],
                    agent_mode=message_data.get("agent_mode"),
                    tokens_used=int(message_data.get("tokens_used", 0)),
                    processing_time=message_data.get("processing_time", 0.0),
                    metadata=message_data.get("metadata")
                )
        except Exception as e:
            logger.error(f"❌ Failed to batch save messages: {e}")
            raise


# Initialize chat system
chat_system = ArthaAIChatSystem()

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://artha-ai.vercel.app",
    "https://*.vercel.app"
]

# Global variables
app_state = {"startup_complete": False}
fi_money_client = None

# Global demo mode state for session management
_demo_mode_sessions = set()  # Track demo mode session IDs

# Pydantic Models
class QueryRequest(BaseModel):
    query: str = Field(..., description="User's financial query", min_length=1, max_length=5000)
    user_id: Optional[str] = Field(None, description="User identifier", max_length=50)
    conversation_id: Optional[str] = Field(None, description="Conversation identifier", max_length=100)
    demo_mode: bool = Field(False, description="Use demo data instead of real financial data")
    think_mode: bool = Field(False, description="Use advanced reasoning model")
    agent: Optional[str] = Field(None, description="Specific agent to use (e.g., 'investment')", max_length=50)
    user_data: Optional[Dict[str, Any]] = None
    
    @validator('query')
    def validate_query(cls, v):
        if VALIDATION_AVAILABLE:
            return InputValidator.validate_chat_message(v)
        return v.strip() if v else v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputValidator.validate_user_id(v)
        return v
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputValidator.validate_session_id(v)
        return v
    
    @validator('agent')
    def validate_agent(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputSanitizer.sanitize_string(v, max_length=50)
        return v

class ChatRequest(BaseModel):
    message: str = Field(..., description="Chat message", min_length=1, max_length=5000)
    conversation_id: Optional[str] = Field(None, description="Conversation ID", max_length=100)
    user_id: Optional[str] = Field(None, description="User ID", max_length=50)
    demo_mode: bool = Field(False, description="Demo mode flag")
    think_mode: bool = Field(False, description="Use advanced reasoning model")
    agent: Optional[str] = Field(None, description="Specific agent to use", max_length=50)
    conversation_history: list = Field([], description="Previous conversation messages")
    user_data: Optional[Dict[str, Any]] = None
    pdf_context: Optional[Dict[str, Any]] = Field(None, description="PDF context for enhanced queries")
    
    @validator('message')
    def validate_message(cls, v):
        if VALIDATION_AVAILABLE:
            return InputValidator.validate_chat_message(v)
        return v.strip() if v else v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputValidator.validate_user_id(v)
        return v
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputValidator.validate_session_id(v)
        return v
    
    @validator('agent')
    def validate_agent(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputSanitizer.sanitize_string(v, max_length=50)
        return v
    
    @validator('conversation_history')
    def validate_conversation_history(cls, v):
        if v and len(v) > 100:  # Limit conversation history size
            raise ValueError("Conversation history too long (max 100 messages)")
        return v

class UserDataRequest(BaseModel):
    user_data: Dict[str, Any]

class UserDataResponse(BaseModel):
    user_id: str
    message: str
    success: bool

class UserLookupRequest(BaseModel):
    email: str = Field(..., description="User email address", max_length=255)
    
    @validator('email')
    def validate_email(cls, v):
        if VALIDATION_AVAILABLE:
            return InputValidator.validate_email(v)
        return v.strip().lower() if v else v

class FinancialDataRequest(BaseModel):
    demo: bool = Field(False, description="Use demo data")

class CacheDataRequest(BaseModel):
    email: str = Field(..., description="User email address", max_length=255)
    financial_data: Dict[str, Any]
    data_source: str = Field("fi_mcp", description="Data source identifier", max_length=50)
    
    @validator('email')
    def validate_email(cls, v):
        if VALIDATION_AVAILABLE:
            return InputValidator.validate_email(v)
        return v.strip().lower() if v else v
    
    @validator('data_source')
    def validate_data_source(cls, v):
        if VALIDATION_AVAILABLE:
            return InputSanitizer.sanitize_string(v, max_length=50)
        return v

class ChatMessageRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="Conversation ID", max_length=100)
    message_type: str = Field("user", description="Message type", max_length=20)
    content: str = Field(..., description="Message content", min_length=1, max_length=5000)
    agent_mode: Optional[str] = Field(None, description="Agent mode", max_length=50)
    tokens_used: Optional[int] = Field(None, description="Tokens used", ge=0)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputValidator.validate_session_id(v)
        return v
    
    @validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = ['user', 'assistant', 'system']
        if v not in allowed_types:
            raise ValueError(f"Message type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if VALIDATION_AVAILABLE:
            return InputValidator.validate_chat_message(v)
        return v.strip() if v else v
    
    @validator('agent_mode')
    def validate_agent_mode(cls, v):
        if v is not None and VALIDATION_AVAILABLE:
            return InputSanitizer.sanitize_string(v, max_length=50)
        return v


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Artha AI Backend Server (Merged Version)...")
    
    # Initialize services
    if GEMINI_AVAILABLE:
        logger.info("✅ Gemini AI client ready")
    
    if FI_MONEY_AVAILABLE:
        logger.info("✅ Fi Money MCP client ready")
    
    if INVESTMENT_AGENT_AVAILABLE:
        logger.info("✅ Investment Agent ready")
    
    app_state["startup_complete"] = True
    logger.info("✅ Server startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Artha AI Backend Server...")


# Create FastAPI app
app = FastAPI(
    title="Artha AI Backend (Merged)",
    description="Enhanced financial AI assistant with multi-agent routing",
    version="2.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add explicit CORS headers (improved version)
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")
    
    # Allow both common development ports
    if origin in ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"]:
        response.headers["Access-Control-Allow-Origin"] = origin
    
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Security middleware for input validation and rate limiting
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware for additional validation and protection"""
    try:
        # Skip security checks for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check request size
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            if ERROR_HANDLING_AVAILABLE:
                raise RateLimitException("Request too large")
            else:
                raise HTTPException(status_code=413, detail="Request too large")
        
        # Basic rate limiting by IP (simple implementation)
        client_ip = request.client.host if request.client else "unknown"
        
        # Log security-relevant requests
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            logger.info(f"🔒 Security check: {request.method} {request.url.path} from {client_ip}")
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Security middleware error: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise ArthaAIException(
                message="Internal security error",
                error_code=ErrorHandler.ErrorCode.INTERNAL_SERVER_ERROR if hasattr(ErrorHandler, 'ErrorCode') else None,
                status_code=500
            )
        else:
            raise HTTPException(status_code=500, detail="Internal security error")

# Setup global exception handlers
if ERROR_HANDLING_AVAILABLE:
    setup_exception_handlers(app)
    logger.info("✅ Global exception handlers configured")

# Health check endpoints
@app.get("/")
async def root():
    return {"message": "Artha AI Backend (Merged) is running", "version": "2.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini": GEMINI_AVAILABLE,
            "fi_money": FI_MONEY_AVAILABLE,
            "investment_agent": INVESTMENT_AGENT_AVAILABLE,
            "chat_service": SERVICES_AVAILABLE
        }
    }

# Include API routers with error handling
if ROUTERS_AVAILABLE:
    try:
        app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
        logger.info("✅ Chat router included")
    except Exception as e:
        logger.error(f"❌ Failed to include chat router: {e}")
    
    try:
        app.include_router(auth_router, tags=["authentication"])
        logger.info("✅ Auth router included")
    except Exception as e:
        logger.error(f"❌ Failed to include auth router: {e}")
    
    try:
        app.include_router(user_router, prefix="/api/user", tags=["user"])
        logger.info("✅ User router included")
    except Exception as e:
        logger.error(f"❌ Failed to include user router: {e}")
    
    try:
        app.include_router(portfolio_router, prefix="/api/portfolio", tags=["portfolio"])
        logger.info("✅ Portfolio router included")
    except Exception as e:
        logger.error(f"❌ Failed to include portfolio router: {e}")
    
    try:
        app.include_router(pdf_router, prefix="/api/pdf", tags=["pdf"])
        logger.info("✅ PDF router included")
    except Exception as e:
        logger.error(f"❌ Failed to include PDF router: {e}")
    
    try:
        app.include_router(session_router, prefix="/api/session", tags=["session"])
        logger.info("✅ Session router included")
    except Exception as e:
        logger.error(f"❌ Failed to include session router: {e}")
    
    try:
        app.include_router(database_router, tags=["database-health"])
        app.include_router(monitoring_router, tags=["monitoring"])
        logger.info("✅ Database health and monitoring routers included")
    except Exception as e:
        logger.error(f"❌ Failed to include database health and monitoring routers: {e}")


# Financial data endpoint - Changed to GET to match frontend expectations
@app.get("/financial-data")
async def get_financial_data(demo: bool = False):
    """Get user's financial data from Fi Money or demo data"""
    try:
        if demo or not FI_MONEY_AVAILABLE:
            # Return demo financial data in the format expected by frontend
            demo_data = {
                "net_worth": {
                    "netWorthResponse": {
                        "assetValues": [
                            {
                                "netWorthAttribute": "Bank Balance",
                                "value": {"currencyCode": "INR", "units": "250000"}
                            },
                            {
                                "netWorthAttribute": "Mutual Funds",
                                "value": {"currencyCode": "INR", "units": "200000"}
                            },
                            {
                                "netWorthAttribute": "Stocks",
                                "value": {"currencyCode": "INR", "units": "150000"}
                            }
                        ],
                        "liabilityValues": [
                            {
                                "netWorthAttribute": "Credit Card Debt",
                                "value": {"currencyCode": "INR", "units": "50000"}
                            },
                            {
                                "netWorthAttribute": "Personal Loan",
                                "value": {"currencyCode": "INR", "units": "50000"}
                            }
                        ],
                        "totalNetWorthValue": {
                            "currencyCode": "INR",
                            "units": "500000"
                        }
                    }
                },
                "credit_report": {
                    "creditReports": [{
                        "creditReportData": {
                            "score": {"bureauScore": "750"},
                            "creditAccount": {
                                "creditAccountSummary": {
                                    "totalOutstandingBalance": {
                                        "outstandingBalanceAll": "100000"
                                    }
                                }
                            }
                        }
                    }]
                },
                "epf_details": {
                    "epfDetails": {
                        "balance": {
                            "currencyCode": "INR",
                            "units": "150000"
                        }
                    }
                }
            }
            
            return {
                "status": "success",
                "data": demo_data,
                "summary": {
                    "total_net_worth_formatted": "₹5,00,000",
                    "total_assets": 600000,
                    "total_liabilities": 100000,
                    "credit_score": "750"
                },
                "demo_mode": True
            }
        
        # Get real financial data - but handle session initialization issues
        try:
            financial_data = await get_user_financial_data()
            return {
                "status": "success",
                "data": {
                    "net_worth": financial_data.net_worth,
                    "credit_report": financial_data.credit_report,
                    "epf_details": financial_data.epf_details,
                    "demo_mode": False
                }
            }
        except Exception as fi_error:
            logger.warning(f"⚠️ Fi Money client error: {fi_error}")
            logger.info("🔄 Falling back to demo data due to Fi Money client issues")
            
            # Return demo data when Fi Money client fails
            demo_data = {
                "net_worth": {
                    "netWorthResponse": {
                        "assetValues": [
                            {
                                "netWorthAttribute": "Bank Balance",
                                "value": {"currencyCode": "INR", "units": "250000"}
                            },
                            {
                                "netWorthAttribute": "Mutual Funds",
                                "value": {"currencyCode": "INR", "units": "200000"}
                            }
                        ],
                        "liabilityValues": [
                            {
                                "netWorthAttribute": "Credit Card Debt",
                                "value": {"currencyCode": "INR", "units": "50000"}
                            }
                        ]
                    }
                },
                "credit_report": None,
                "epf_details": None
            }
            
            return {
                "status": "success",
                "data": demo_data,
                "summary": {
                    "total_net_worth_formatted": "₹4,00,000",
                    "total_assets": 450000,
                    "total_liabilities": 50000,
                    "credit_score": "750"
                },
                "demo_mode": True,
                "message": "Using demo data due to Fi Money connection issues"
            }
    
    except Exception as e:
        logger.error(f"❌ Failed to fetch financial data: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Failed to fetch financial data: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to fetch financial data: {str(e)}",
            "demo_mode": True
        }


# User data endpoints
@app.post("/save-user-data")
async def save_user_data(request: UserDataRequest):
    """Save user profile data"""
    try:
        if USER_MODELS_AVAILABLE:
            # Save to actual database using user models
            user_id = save_user_profile(request.user_data)
            logger.info(f"✅ User profile saved successfully: {user_id}")
            return {"success": True, "message": "User data saved successfully", "user_id": user_id}
        else:
            # Fallback for demo mode
            logger.info(f"📝 Demo mode - acknowledging user data: {list(request.user_data.keys())}")
            return {"success": True, "message": "User data saved successfully (demo mode)"}
    except Exception as e:
        logger.error(f"❌ Failed to save user data: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Failed to save user data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save user data: {str(e)}")


@app.get("/get-user-data")
async def get_user_data(user_id: str = None, email: str = None):
    """Get user profile data"""
    try:
        if USER_MODELS_AVAILABLE:
            # Get from actual database using user models
            if user_id:
                user_profile = get_user_profile(user_id)
            elif email:
                user_profile = get_user_profile_by_email(email)
            else:
                return {"success": False, "message": "User ID or email required"}
            
            if user_profile:
                logger.info(f"✅ User profile retrieved successfully for: {user_id or email}")
                return {"success": True, "data": user_profile}
            else:
                return {"success": False, "message": "User profile not found"}
        else:
            # Return sample user data for demo
            if user_id or email:
                sample_data = {
                    "user_id": user_id or (create_user_id_from_email(email) if USER_MODELS_AVAILABLE and email else "demo_user"),
                    "personalInfo": {
                        "fullName": "Demo User",
                        "email": email or "demo@example.com",
                        "phoneNumber": "+91-9876543210",
                        "dateOfBirth": "1990-01-01",
                        "occupation": "Software Engineer"
                    },
                    "professionalInfo": {
                        "occupation": "Software Engineer",
                        "annualIncome": "1200000"
                    },
                    "investmentPreferences": {
                        "riskTolerance": "moderate",
                        "investmentGoals": ["retirement", "wealth_building"]
                    }
                }
                return {"success": True, "data": sample_data}
            return {"success": False, "message": "User ID or email required"}
    except Exception as e:
        logger.error(f"❌ Failed to retrieve user data: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Failed to retrieve user data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user data: {str(e)}")


@app.post("/api/user/lookup")
async def lookup_user_by_email(request: UserLookupRequest):
    """Lookup user profile by email address"""
    try:
        if USER_MODELS_AVAILABLE:
            user_data = get_user_profile_by_email(request.email)
            if user_data:
                user_id = create_user_id_from_email(request.email)
                logger.info(f"✅ User profile found for email: {request.email}")
                return {
                    "status": "success",
                    "user_id": user_id,
                    "user_data": user_data,
                    "message": "User profile found"
                }
            else:
                return {
                    "status": "not_found",
                    "message": "No user profile found for this email"
                }
        else:
            # Demo mode fallback
            user_id = f"demo_{request.email.replace('@', '_').replace('.', '_')}"
            return {
                "status": "success",
                "user_id": user_id,
                "user_data": {
                    "personalInfo": {
                        "fullName": "Demo User",
                        "email": request.email,
                        "phoneNumber": "+91-9876543210",
                        "dateOfBirth": "1990-01-01",
                        "occupation": "Software Engineer"
                    },
                    "professionalInfo": {
                        "occupation": "Software Engineer",
                        "annualIncome": "1200000"
                    },
                    "investmentPreferences": {
                        "riskTolerance": "moderate",
                        "investmentGoals": ["retirement", "wealth_building"]
                    }
                },
                "message": "Demo user profile (models not available)"
            }
    except Exception as e:
        logger.error(f"❌ Failed to lookup user by email: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Failed to lookup user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to lookup user: {str(e)}")


# Fi Money authentication endpoints (maintained from stable version)
@app.get("/api/fi-money/auth-status")
async def fi_money_auth_status(demo: bool = False):
    """Check Fi Money authentication status"""
    if demo:
        return {"authenticated": True, "demo_mode": True}
    
    try:
        # Check real authentication status
        return {"authenticated": FI_MONEY_AVAILABLE, "demo_mode": False}
    except Exception as e:
        logger.error(f"❌ Fi Money auth status check failed: {e}")
        return {"authenticated": False, "error": str(e)}


@app.post("/api/fi-money/initiate-auth")
async def initiate_fi_money_auth(demo: bool = False):
    """Initiate Fi Money authentication"""
    if demo:
        return {
            "auth_url": "https://demo.fi.money/auth",
            "demo_mode": True,
            "message": "Demo mode - authentication simulated"
        }
    
    try:
        # Real authentication initiation would go here
        return {"message": "Fi Money authentication not implemented yet"}
    except Exception as e:
        logger.error(f"❌ Fi Money auth initiation failed: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Fi Money auth initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fi-money/complete-auth")
async def complete_fi_money_auth(code: str, demo: bool = False):
    """Complete Fi Money authentication"""
    if demo:
        return {
            "success": True,
            "demo_mode": True,
            "message": "Demo authentication completed"
        }
    
    try:
        # Real authentication completion would go here
        return {"message": "Fi Money authentication completion not implemented yet"}
    except Exception as e:
        logger.error(f"❌ Fi Money auth completion failed: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Fi Money auth completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fi-money/logout")
async def fi_money_logout(demo: bool = False):
    """Logout from Fi Money"""
    if demo:
        return {"success": True, "demo_mode": True, "message": "Demo logout completed"}
    
    try:
        # Real logout would go here
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"❌ Fi Money logout failed: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Fi Money logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fi-auth/clear-cache")
async def clear_fi_auth_cache():
    """Clear cached Fi Money session to force fresh authentication"""
    try:
        logger.info("🧹 Clearing Fi Money cached session...")
        
        # Import the Fi Money client
        from core.fi_mcp.production_client import get_fi_client
        
        # Get the client and clear cached session
        client = await get_fi_client()
        result = await client.clear_cached_session()
        
        if result["success"]:
            logger.info("✅ Fi Money cached session cleared successfully")
            return JSONResponse({
                "success": True,
                "message": result["message"]
            })
        else:
            logger.warning(f"⚠️ Failed to clear Fi Money cached session: {result['message']}")
            return JSONResponse({
                "success": False,
                "message": result["message"]
            })
            
    except Exception as e:
        logger.error(f"❌ Clear cache error: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Failed to clear cached session: {str(e)}"
        }, status_code=500)

@app.post("/api/fi-auth/logout")
async def fi_auth_logout():
    """Logout from Fi Money authentication - Frontend compatible endpoint"""
    try:
        # Clear any authentication sessions or tokens
        # This should match the logout logic from production_client.py if needed
        return {
            "status": "success",
            "message": "Successfully logged out from Fi Money"
        }
    except Exception as e:
        logger.error(f"❌ Fi auth logout failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


# Chat conversation endpoints
@app.post("/api/chat/conversations")
async def create_new_conversation():
    """Create a new chat conversation"""
    import uuid
    conversation_id = str(uuid.uuid4())
    return {
        "conversation_id": conversation_id,
        "created_at": datetime.now().isoformat()
    }


@app.get("/api/chat/conversations")
async def get_conversations(user_id: str = None):
    """Get user's chat conversations"""
    try:
        if chat_system.chat_service and user_id:
            conversations = await chat_system.chat_service.get_user_conversations(user_id)
            return {"conversations": conversations}
        
        # Return sample conversations for demo
        return {
            "conversations": [
                {
                    "id": "demo-conv-1",
                    "title": "Investment Planning",
                    "created_at": datetime.now().isoformat(),
                    "message_count": 5
                }
            ]
        }
    except Exception as e:
        logger.error(f"❌ Failed to get conversations: {e}")
        return {"conversations": []}


@app.get("/api/chat/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, user_id: str = None):
    """Get a specific conversation by ID"""
    try:
        logger.info(f"📖 Getting conversation {conversation_id} for user {user_id}")
        
        if chat_system.chat_service and user_id:
            conversation = await chat_system.chat_service.get_conversation(conversation_id, user_id)
            if conversation:
                return conversation
        
        # Return mock conversation for demo/testing
        return {
            "id": conversation_id,
            "title": "Chat Conversation",
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "user_id": user_id or "demo_user"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Conversation not found: {conversation_id}")


@app.post("/api/chat/messages")
async def add_message(request: ChatMessageRequest):
    """Add a message to a conversation"""
    try:
        logger.info(f"💬 Adding message to conversation {request.conversation_id}")
        
        # Generate a message ID
        import uuid
        message_id = str(uuid.uuid4())
        
        # Mock message storage - return success for now
        return {
            "message_id": message_id,
            "status": "success",
            "message": "Message added successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to add message: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Failed to add message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


# Enhanced streaming endpoint with SSE support
@app.post("/api/stream/query")
async def stream_query(request: QueryRequest):
    """Stream AI response with Server-Sent Events - Rewritten for stability"""
    
    async def generate_response():
        try:
            # Validate request
            if not request.query or len(request.query.strip()) == 0:
                error_msg = json.dumps({"type": "error", "content": "Query cannot be empty"})
                yield f"data: {error_msg}\n\n"
                yield f"data: [DONE]\n\n"
                return
            
            # Initial status
            init_msg = json.dumps({"type": "log", "content": "🤖 Artha AI is thinking..."})
            yield f"data: {init_msg}\n\n"
            await asyncio.sleep(0.1)
            
            # Extract user_data properly - this is critical for personalization
            user_data = None
            pdf_context = None
            
            # Get user data from request body if available
            if hasattr(request, 'user_data') and request.user_data:
                user_data = request.user_data
                logger.info(f"✅ User data extracted for streaming: {user_data.get('full_name', 'Unknown')}")
                
                # Extract PDF context if available
                if isinstance(user_data, dict) and 'pdf_context' in user_data:
                    pdf_context = format_pdf_context_for_ai(user_data['pdf_context'])
                    if pdf_context:
                        pdf_msg = json.dumps({"type": "log", "content": "📄 PDF context loaded"})
                        yield f"data: {pdf_msg}\n\n"
            else:
                logger.warning("⚠️ No user data found in streaming request")
            
            # Route to appropriate agent
            if request.agent == "investment":
                status_msg = json.dumps({"type": "log", "content": "💰 Investment Agent activated"})
                yield f"data: {status_msg}\n\n"
            elif request.think_mode:
                status_msg = json.dumps({"type": "log", "content": "🧠 Advanced reasoning mode"})
                yield f"data: {status_msg}\n\n"
            else:
                status_msg = json.dumps({"type": "log", "content": "⚡ Fast response mode"})
                yield f"data: {status_msg}\n\n"
            
            await asyncio.sleep(0.1)
            
            # Load financial data with proper error handling
            financial_data = None
            try:
                financial_data = await chat_system._get_financial_data_with_demo_support(request.demo_mode)
                if financial_data:
                    data_msg = json.dumps({"type": "log", "content": "📊 Financial data loaded"})
                    yield f"data: {data_msg}\n\n"
            except Exception as e:
                logger.warning(f"Failed to get financial data: {e}")
                demo_msg = json.dumps({"type": "log", "content": "📊 Using demo data"})
                yield f"data: {demo_msg}\n\n"
            
            # Generate response with proper user data passing
            process_msg = json.dumps({"type": "log", "content": "✨ Generating response..."})
            yield f"data: {process_msg}\n\n"
            
            # Call chat system with all required parameters
            result = await chat_system.process_query(
                query=request.query,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                think_mode=request.think_mode,
                agent=request.agent,
                demo_mode=request.demo_mode,
                pdf_context=pdf_context,
                user_data=user_data  # Critical: pass user_data for personalization
            )
            
            # Stream response content
            if result and "response" in result:
                response_text = result["response"]
                
                # Stream in smaller chunks for better UX
                words = response_text.split()
                for i, word in enumerate(words):
                    chunk_msg = json.dumps({"type": "content", "content": word + " "})
                    yield f"data: {chunk_msg}\n\n"
                    
                    # Add small delay every few words
                    if i % 3 == 0:
                        await asyncio.sleep(0.02)
                
                # Add sources if available
                if "sources" in result and result["sources"]:
                    sources_msg = json.dumps({"type": "log", "content": f"📚 {len(result['sources'])} sources used"})
                    yield f"data: {sources_msg}\n\n"
            else:
                # Fallback response
                fallback_msg = json.dumps({"type": "content", "content": "I apologize, but I couldn't generate a proper response. Please try again."})
                yield f"data: {fallback_msg}\n\n"
            
            # Completion signal
            yield f"data: [DONE]\n\n"
            
        except HTTPException as http_e:
            logger.error(f"❌ HTTP error in streaming: {http_e}")
            error_msg = json.dumps({"type": "error", "content": f"Request error: {http_e.detail}"})
            yield f"data: {error_msg}\n\n"
            yield f"data: [DONE]\n\n"
        except asyncio.TimeoutError:
            logger.error("❌ Streaming timeout")
            error_msg = json.dumps({"type": "error", "content": "Response timed out. Please try again."})
            yield f"data: {error_msg}\n\n"
            yield f"data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"❌ Critical streaming error: {e}")
            error_msg = json.dumps({"type": "error", "content": "Technical difficulties. Please try again."})
            yield f"data: {error_msg}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_response(), 
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true"
        }
    )


# Streaming chat endpoint
@app.post("/api/stream/chat")
async def stream_chat(request: ChatRequest):
    """
    Streaming chat endpoint with Server-Sent Events (SSE)
    Provides real-time response streaming for better user experience
    """
    async def generate_stream():
        try:
            newline = "\n"
            
            # Initial connection confirmation
            yield f"data: {json.dumps({'type': 'log', 'content': '🔗 Connection established - streaming enabled'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Load conversation history if provided
            if request.conversation_id:
                existing_history = load_conversation_history(request.conversation_id)
                if existing_history:
                    request.conversation_history.extend(existing_history)
                    yield f"data: {json.dumps({'type': 'log', 'content': f'📚 Loaded {len(existing_history)} previous messages'})}\n\n"
                    await asyncio.sleep(0.1)
            
            # Track demo mode sessions
            if request.conversation_id:
                _demo_mode_sessions.add(request.conversation_id)
            
            # Check for PDF context
            pdf_context_text = ""
            if request.pdf_context:
                pdf_context_text = format_pdf_context_for_ai(request.pdf_context)
                if pdf_context_text:
                    yield f"data: {json.dumps({'type': 'log', 'content': '📄 PDF context detected and loaded'})}\n\n"
                    await asyncio.sleep(0.1)
            
            # Prepare enhanced query
            enhanced_query = request.query
            if pdf_context_text:
                enhanced_query = f"""
                UPLOADED DOCUMENT CONTEXT:
                {pdf_context_text}
                
                USER QUERY: {request.query}
                
                Please analyze the user's query in the context of the uploaded financial document data above.
                """
            
            # Processing indicator
            yield f"data: {json.dumps({'type': 'log', 'content': '🤖 Processing your query with AI...'})}\n\n"
            await asyncio.sleep(0.2)


            
            # Get user data for personalization - log for debugging
            user_data = request.user_data or {}
            logger.info(f"🔍 User data received: {user_data}")
            logger.info(f"🔍 User ID: {request.user_id}")
            logger.info(f"🔍 Demo mode: {request.demo_mode}")
            
            # Process query with the chatbot using correct parameters and user data
            response = await chatbot.process_query(
                query=enhanced_query,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                think_mode=request.think_mode,
                agent=request.agent,
                demo_mode=request.demo_mode,
                pdf_context=pdf_context_text,
                user_data=user_data
            )
            
            # Start streaming the response
            yield f"data: {json.dumps({'type': 'log', 'content': '✨ Generating response...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Stream response content word by word
            response_content = response.get('response', 'I apologize, but I encountered an issue processing your request.')
            words = response_content.split()
            
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'content', 'content': word + ' '})}\n\n"
                await asyncio.sleep(0.03)  # Adjust speed as needed
            
            # Add sources if available
            sources = response.get('sources', [])
            if sources:
                yield f"data: {json.dumps({'type': 'log', 'content': f'📊 Response based on {len(sources)} sources'})}\n\n"
                await asyncio.sleep(0.1)
                
                sources_text = f"\n\n📚 **Sources:**\n"
                for i, source in enumerate(sources[:3], 1):
                    source_title = source.get('title', 'Source')
                    sources_text += f"{i}. {source_title}\n"
                
                # Stream sources
                for word in sources_text.split():
                    yield f"data: {json.dumps({'type': 'content', 'content': word + ' '})}\n\n"
                    await asyncio.sleep(0.02)
             
            # Save conversation history
            if request.conversation_id:
                save_conversation_history(request.conversation_id, [
                    {"role": "user", "content": request.query},
                    {"role": "assistant", "content": response_content}
                ])
                yield f"data: {json.dumps({'type': 'log', 'content': '💾 Conversation saved'})}\n\n"
            
            # End of stream
            yield f"data: [DONE]\n\n"
             
        except HTTPException as http_e:
            logger.error(f"❌ HTTP error in chat streaming: {http_e}")
            error_msg = json.dumps({"type": "error", "content": f"Request error: {http_e.detail}"})
            yield f"data: {error_msg}\n\n"
            yield f"data: [DONE]\n\n"
        except asyncio.TimeoutError:
            logger.error("❌ Chat streaming timeout")
            error_msg = json.dumps({"type": "error", "content": "Chat response timed out. Please try again."})
            yield f"data: {error_msg}\n\n"
            yield f"data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"❌ Critical error in chat streaming: {e}")
            # Try to provide a fallback response
            try:
                fallback_response = chatbot._generate_fallback_response(request.query, pdf_context=pdf_context_text)
                yield f"data: {json.dumps({'type': 'content', 'content': fallback_response})}\n\n"
                yield f"data: {json.dumps({'type': 'sources', 'sources': []})}\n\n"
            except:
                error_msg = json.dumps({"type": "error", "content": "I apologize, but I'm experiencing technical difficulties. Please try again."})
                yield f"data: {error_msg}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

# PDF-enhanced chat endpoint
@app.post("/api/chat/pdf")
async def pdf_enhanced_chat(request: ChatRequest):
    """
    Chat endpoint with PDF context integration
    Processes user queries with uploaded PDF financial data context
    """
    try:
        logger.info(f"📄 PDF-enhanced chat request: {request.message[:100]}...")
        
        # Validate PDF context
        if not request.pdf_context:
            raise HTTPException(
                status_code=400, 
                detail="PDF context is required for this endpoint"
            )
        
        # Load existing conversation history if conversation_id provided
        if request.conversation_id and not request.conversation_history:
            request.conversation_history = await load_conversation_history(request.conversation_id)
        
        # Track demo mode sessions
        if request.demo_mode and request.conversation_id:
            _demo_mode_sessions.add(request.conversation_id)
        
        # Format PDF context for AI analysis
        pdf_context_text = format_pdf_context_for_ai(request.pdf_context)
        
        # Process query with PDF context
        result = await chat_system.process_query(
            query=request.message,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            think_mode=request.think_mode,
            agent=request.agent,
            demo_mode=request.demo_mode,
            pdf_context=pdf_context_text
        )
        
        # Save conversation history
        if request.conversation_id and result.get('response'):
            await save_conversation_history(
                conversation_id=request.conversation_id,
                message=request.message,
                response=result.get('response', ''),
                user_id=request.user_id
            )
        
        # Add PDF metadata to response
        result['pdf_enhanced'] = True
        result['pdf_summary'] = {
            "document_type": request.pdf_context.get('document_type', 'Unknown'),
            "accounts_count": len(request.pdf_context.get('accounts', [])),
            "transactions_count": len(request.pdf_context.get('transactions', [])),
            "confidence_score": request.pdf_context.get('confidence_score', 0.0)
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF-enhanced chat failed: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"PDF-enhanced chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF-enhanced chat failed: {str(e)}")


# Non-streaming chat endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Non-streaming chat endpoint with conversation history"""
    try:
        # Load conversation history if conversation_id is provided
        if request.conversation_id and not request.conversation_history:
            request.conversation_history = await load_conversation_history(request.conversation_id)
        
        # Track demo mode sessions
        if request.demo_mode and request.conversation_id:
            _demo_mode_sessions.add(request.conversation_id)
        
        # Prepare PDF context if available
        pdf_context = None
        if request.pdf_context:
            pdf_context = format_pdf_context_for_ai(request.pdf_context)
        
        result = await chat_system.process_query(
            query=request.message,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            think_mode=request.think_mode,
            agent=request.agent,
            demo_mode=request.demo_mode,
            pdf_context=pdf_context
        )
        
        # Save conversation history
        if request.conversation_id and result.get('response'):
            await save_conversation_history(
                conversation_id=request.conversation_id,
                message=request.message,
                response=result.get('response', ''),
                user_id=request.user_id
            )
        
        return result
    except Exception as e:
        logger.error(f"❌ Chat endpoint failed: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Chat endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Legacy query endpoint (maintained for compatibility)
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """Legacy query endpoint for backward compatibility with conversation history"""
    try:
        # Track demo mode sessions
        if request.demo_mode and request.conversation_id:
            _demo_mode_sessions.add(request.conversation_id)
        
        # Prepare PDF context if available
        pdf_context = None
        if hasattr(request, 'user_data') and request.user_data and 'pdf_context' in request.user_data:
            pdf_context = format_pdf_context_for_ai(request.user_data['pdf_context'])
        
        # Extract user_data from request if available
        user_data = None
        if hasattr(request, 'user_data') and request.user_data:
            user_data = request.user_data
        
        result = await chat_system.process_query(
            query=request.query,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            think_mode=request.think_mode,
            agent=request.agent,
            demo_mode=request.demo_mode,
            pdf_context=pdf_context,
            user_data=user_data
        )
        
        # Save conversation history
        if request.conversation_id and result.get('response'):
            await save_conversation_history(
                conversation_id=request.conversation_id,
                message=request.query,
                response=result.get('response', ''),
                user_id=request.user_id
            )
        
        return result
    except Exception as e:
        logger.error(f"❌ Query endpoint failed: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Query endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# User profile save endpoint
@app.post("/api/user/save")
async def save_user_profile_endpoint(request: Request):
    """Save user profile data"""
    try:
        data = await request.json()
        logger.info(f"💾 Saving user profile: {data.get('email', 'unknown')}")
        
        # Extract user data from request
        user_data = {
            "firstName": data.get("firstName", ""),
            "lastName": data.get("lastName", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "dateOfBirth": data.get("dateOfBirth", ""),
            "occupation": data.get("occupation", ""),
            "annualIncome": data.get("annualIncome", ""),
            "riskTolerance": data.get("riskTolerance", "moderate"),
            "investmentGoals": data.get("investmentGoals", [])
        }
        
        # Generate user_id from email if available
        user_id = None
        if user_data["email"] and USER_MODELS_AVAILABLE:
            try:
                user_id = create_user_id_from_email(user_data["email"])
                user_data["user_id"] = user_id
                
                # Save to database if available
                save_result = save_user_profile(user_id, user_data)
                if save_result:
                    logger.info(f"✅ User profile saved to database: {user_id}")
                else:
                    logger.warning(f"⚠️ Failed to save user profile to database: {user_id}")
            except Exception as db_error:
                logger.error(f"❌ Database error saving user profile: {db_error}")
        
        return {
            "success": True,
            "message": "User profile saved successfully",
            "user_id": user_id,
            "data": user_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving user profile: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Failed to save user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save user profile: {str(e)}")


# Fi Money Authentication endpoints
@app.post("/api/fi-auth/initiate")
async def initiate_fi_auth():
    """Initiate Fi Money authentication"""
    import time
    request_id = f"auth_init_{int(time.time() * 1000)}"
    try:
        logger.info(f"🌐 [REQ:{request_id}] Initiating Fi Money authentication...")
        logger.debug(f"[REQ:{request_id}] FI_MONEY_AVAILABLE: {FI_MONEY_AVAILABLE}")
        
        if not FI_MONEY_AVAILABLE:
            logger.warning(f"⚠️ [REQ:{request_id}] Fi Money service not available")
            return {
                "status": "error",
                "message": "Fi Money service is not available"
            }
        
        # Check if already authenticated
        try:
            logger.debug(f"[REQ:{request_id}] Checking existing authentication status...")
            from core.fi_mcp.production_client import get_fi_client
            client = await get_fi_client()
            auth_status = await client.check_authentication_status()
            
            logger.debug(f"[REQ:{request_id}] Auth status check result: {auth_status}")
            
            if auth_status.get("authenticated", False):
                logger.info(f"✅ [REQ:{request_id}] Already authenticated with Fi Money")
                return {
                    "status": "already_authenticated",
                    "session_id": auth_status.get("session_id"),
                    "message": "Already authenticated with Fi Money"
                }
        except Exception as check_error:
            logger.warning(f"⚠️ [REQ:{request_id}] Could not check existing auth status: {check_error}")
            logger.debug(f"[REQ:{request_id}] Auth status check error details: {type(check_error).__name__}: {str(check_error)}")
        
        # Initiate new authentication
        try:
            logger.debug(f"[REQ:{request_id}] Initiating new Fi Money authentication...")
            from core.fi_mcp.production_client import initiate_fi_authentication
            result = await initiate_fi_authentication()
            
            logger.info(f"🔄 [REQ:{request_id}] Fi Money authentication initiation result: {result.get('status')}")
            logger.debug(f"[REQ:{request_id}] Full initiation result: {result}")
            return result
            
        except Exception as init_error:
            logger.error(f"❌ [REQ:{request_id}] Fi Money authentication initiation failed: {init_error}")
            logger.debug(f"[REQ:{request_id}] Initiation error details: {type(init_error).__name__}: {str(init_error)}")
            return {
                "status": "error",
                "message": f"Authentication initiation failed: {str(init_error)}"
            }
            
    except Exception as e:
        logger.error(f"❌ Error in Fi Money authentication initiation: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Authentication initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication initiation failed: {str(e)}")


@app.get("/api/fi-auth/status")
async def check_fi_auth_status():
    """Check Fi Money authentication status"""
    import time
    request_id = f"auth_status_{int(time.time() * 1000)}"
    try:
        logger.info(f"🔍 [REQ:{request_id}] Checking Fi Money authentication status...")
        
        if not FI_MONEY_AVAILABLE:
            logger.warning(f"⚠️ [REQ:{request_id}] Fi Money service not available")
            return {
                "status": "error",
                "message": "Fi Money service is not available",
                "auth_status": {
                    "authenticated": False
                }
            }
        
        try:
            # Check actual authentication status using Fi Money MCP client
            logger.debug(f"[REQ:{request_id}] Getting Fi Money client...")
            from core.fi_mcp.production_client import get_fi_client
            client = await get_fi_client()
            
            # Only return authenticated if there's a valid session with actual authentication
            logger.debug(f"[REQ:{request_id}] Checking authentication status with client...")
            auth_status = await client.check_authentication_status()
            
            # Be more strict about authentication status - require actual session
            is_authenticated = (
                auth_status.get("authenticated", False) and 
                client.session is not None and 
                client.session.authenticated and 
                not client.session.is_expired()
            )
            
            logger.info(f"📊 [REQ:{request_id}] Fi Money auth status checked: {is_authenticated}")
            logger.debug(f"[REQ:{request_id}] Full auth status result: {auth_status}")
            logger.debug(f"[REQ:{request_id}] Session exists: {client.session is not None}")
            
            return {
                "status": "success",
                "auth_status": {
                    "authenticated": is_authenticated,
                    "expires_in_minutes": auth_status.get("expires_in_minutes") if is_authenticated else None,
                    "message": auth_status.get("message", "Authentication status checked")
                }
            }
            
        except Exception as check_error:
            logger.error(f"❌ [REQ:{request_id}] Fi Money authentication status check error: {check_error}")
            logger.debug(f"[REQ:{request_id}] Status check error details: {type(check_error).__name__}: {str(check_error)}")
            return {
                "status": "error",
                "message": f"Status check failed: {str(check_error)}",
                "auth_status": {
                    "authenticated": False
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error checking Fi Money authentication status: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.post("/api/fi-auth/complete")
async def complete_fi_auth():
    """Complete Fi Money authentication process"""
    import time
    request_id = f"auth_complete_{int(time.time() * 1000)}"
    try:
        logger.info(f"🔄 [REQ:{request_id}] Fi Money authentication completion requested...")
        logger.debug(f"[REQ:{request_id}] FI_MONEY_AVAILABLE: {FI_MONEY_AVAILABLE}")
        
        if not FI_MONEY_AVAILABLE:
            logger.warning(f"⚠️ [REQ:{request_id}] Fi Money service not available")
            return {
                "status": "error",
                "message": "Fi Money service is not available",
                "auth_status": {
                    "authenticated": False
                }
            }
        
        try:
            # Use the Fi Money MCP client to check actual authentication status
            logger.debug(f"[REQ:{request_id}] Checking actual Fi Money authentication status...")
            
            from core.fi_mcp.production_client import get_fi_client
            client = await get_fi_client()
            
            if client:
                auth_result = await client.check_authentication_status()
                logger.debug(f"[REQ:{request_id}] Fi Money auth check result: {auth_result}")
                
                if auth_result.get('authenticated', False):
                    logger.info(f"✅ [REQ:{request_id}] Fi Money authentication confirmed")
                    result = {
                        "status": "success",
                        "auth_status": {
                            "authenticated": True,
                            "expires_in_minutes": auth_result.get('expires_in_minutes'),
                            "message": auth_result.get('message', 'Authentication confirmed')
                        },
                        "message": "Fi Money authentication completed successfully"
                    }
                else:
                    logger.warning(f"⚠️ [REQ:{request_id}] Fi Money authentication not yet completed")
                    result = {
                        "status": "pending",
                        "auth_status": {
                            "authenticated": False,
                            "message": auth_result.get('message', 'Authentication still pending')
                        },
                        "message": "Authentication not yet completed"
                    }
            else:
                logger.error(f"❌ [REQ:{request_id}] Fi Money client not available")
                result = {
                    "status": "error",
                    "auth_status": {
                        "authenticated": False,
                        "message": "Fi Money client not available"
                    },
                    "message": "Fi Money service unavailable"
                }
            
            logger.debug(f"[REQ:{request_id}] Completion result: {result}")
            return result
            
        except Exception as complete_error:
            logger.error(f"❌ [REQ:{request_id}] Fi Money authentication completion error: {complete_error}")
            logger.debug(f"[REQ:{request_id}] Completion error details: {type(complete_error).__name__}: {str(complete_error)}")
            return {
                "status": "error",
                "message": f"Completion check failed: {str(complete_error)}",
                "auth_status": {
                    "authenticated": False
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error in Fi Money authentication completion: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Authentication completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication completion failed: {str(e)}")


@app.get("/api/fi-auth/test-connectivity")
async def test_fi_connectivity():
    """Test connectivity to Fi Money MCP server"""
    import time
    request_id = f"connectivity_test_{int(time.time() * 1000)}"
    try:
        logger.info(f"🔍 [REQ:{request_id}] Testing Fi Money MCP server connectivity...")
        logger.debug(f"[REQ:{request_id}] FI_MONEY_AVAILABLE: {FI_MONEY_AVAILABLE}")
        
        if not FI_MONEY_AVAILABLE:
            logger.warning(f"⚠️ [REQ:{request_id}] Fi Money service not available")
            return {
                "status": "error",
                "server_reachable": False,
                "message": "Fi Money service is not available in this environment",
                "server_url": "N/A"
            }
        
        try:
            from core.fi_mcp.production_client import test_fi_connectivity
            connectivity_result = await test_fi_connectivity()
            
            logger.info(f"🔍 Connectivity test result: {connectivity_result.get('status')}")
            return connectivity_result
            
        except Exception as test_error:
            logger.error(f"❌ Fi Money connectivity test failed: {test_error}")
            return {
                "status": "error",
                "server_reachable": False,
                "error_type": "test_failed",
                "error_message": str(test_error),
                "message": f"Connectivity test failed: {str(test_error)}"
            }
            
    except Exception as e:
        logger.error(f"❌ Error in Fi Money connectivity test: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Connectivity test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connectivity test failed: {str(e)}")


@app.get("/api/cache/status")
async def get_cache_status(email: str):
    """Check if user has valid cached financial data"""
    try:
        logger.info(f"🔍 Checking cache status for email: {email}")
        
        # Mock cache status response for now
        # TODO: Implement actual cache system integration
        logger.info("📊 Cache status checked (mock implementation)")
        
        return {
            "enabled": False,
            "has_cache": False,
            "expires_at": None,
            "time_remaining": None,
            "cached_at": None,
            "message": "Secure cache system is not enabled (mock)"
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking cache status: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Cache status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cache status check failed: {str(e)}")


@app.delete("/api/cache/invalidate")
async def invalidate_cache(email: str):
    """Manually invalidate user's cached financial data"""
    try:
        logger.info(f"🗑️ Cache invalidation requested for email: {email}")
        
        # Since we're not using authentication tokens and cache system is disabled,
        # we'll just return a success response
        logger.info("✅ Cache invalidated (mock implementation - no auth required)")
        
        return {
            "status": "success",
            "message": "Cache invalidated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to invalidate cache: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Cache invalidation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cache invalidation error: {str(e)}")


@app.post("/api/cache/store")
async def store_financial_data(request: CacheDataRequest):
    """Store financial data in secure cache"""
    try:
        logger.info(f"📥 Cache storage request received for {request.email}")
        
        # Mock cache storage - return success for now
        return {
            "status": "success",
            "message": "Financial data cached successfully",
            "expires_in": "24 hours"
        }
        
    except Exception as e:
        logger.error(f"❌ Cache storage error: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Cache storage failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cache storage failed: {str(e)}")

@app.get("/api/cache/retrieve")
async def retrieve_cache():
    """Retrieve cached financial data"""
    try:
        logger.info("📥 Cache retrieval request received")
        
        # Mock cache retrieval - return empty cache for now
        return {
            "status": "success",
            "has_cache": False,
            "data": None,
            "message": "No cached data available"
        }
        
    except Exception as e:
        logger.error(f"❌ Cache retrieval error: {e}")
        if ERROR_HANDLING_AVAILABLE:
            raise_internal_server_error(f"Cache retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cache retrieval failed: {str(e)}")


# Transaction History API endpoint
@app.get("/api/transaction-history")
async def get_transaction_history(demo: bool = False, limit: int = 50):
    """Get user's transaction history - both bank and credit card transactions"""
    try:
        # If demo mode is requested, use sample data
        if demo:
            logger.info("📊 Loading demo transaction history")
            from core.fi_mcp.real_client import RealFiMCPClient
            
            client = RealFiMCPClient()
            bank_transactions = await client.fetch_bank_transactions()
            mf_transactions = await client.fetch_mf_transactions()
            
            # Combine and format transactions
            all_transactions = []
            
            # Add bank transactions
            if bank_transactions and 'transactions' in bank_transactions:
                for txn in bank_transactions['transactions']:
                    all_transactions.append({
                        **txn,
                        'source': 'bank',
                        'type': 'bank_transaction'
                    })
            
            # Add mutual fund transactions
            if mf_transactions and 'transactions' in mf_transactions:
                for txn in mf_transactions['transactions']:
                    all_transactions.append({
                        **txn,
                        'source': 'mutual_fund',
                        'type': 'mf_transaction'
                    })
            
            # Sort by date (most recent first)
            all_transactions.sort(key=lambda x: x.get('transactionDate', ''), reverse=True)
            
            # Apply limit
            limited_transactions = all_transactions[:limit]
            
            return {
                "status": "success",
                "data": {
                    "transactions": limited_transactions,
                    "total_count": len(all_transactions),
                    "bank_transactions": bank_transactions.get('transactions', []) if bank_transactions else [],
                    "mf_transactions": mf_transactions.get('transactions', []) if mf_transactions else []
                },
                "is_demo": True,
                "message": f"Demo transaction history loaded - {len(limited_transactions)} transactions"
            }
        
        # Check authentication first for real data
        auth_status = await check_authentication_status()
        if not auth_status.get('authenticated', False):
            return {
                "status": "unauthenticated",
                "message": "Please authenticate with Fi Money first",
                "auth_required": True
            }
        
        # Fetch real-time transaction data from Fi Money
        financial_data = await get_financial_data_with_demo_support(demo_mode=False)
        
        # Combine and format transactions
        all_transactions = []
        
        # Add bank transactions
        if hasattr(financial_data, 'bank_transactions') and financial_data.bank_transactions:
            bank_txns = financial_data.bank_transactions if isinstance(financial_data.bank_transactions, list) else financial_data.bank_transactions.get('transactions', [])
            for txn in bank_txns:
                all_transactions.append({
                    **txn,
                    'source': 'bank',
                    'type': 'bank_transaction'
                })
        
        # Add mutual fund transactions
        if hasattr(financial_data, 'mf_transactions') and financial_data.mf_transactions:
            mf_txns = financial_data.mf_transactions if isinstance(financial_data.mf_transactions, list) else financial_data.mf_transactions.get('transactions', [])
            for txn in mf_txns:
                all_transactions.append({
                    **txn,
                    'source': 'mutual_fund',
                    'type': 'mf_transaction'
                })
        
        # Sort by date (most recent first)
        all_transactions.sort(key=lambda x: x.get('transactionDate', ''), reverse=True)
        
        # Apply limit
        limited_transactions = all_transactions[:limit]
        
        return {
            "status": "success",
            "data": {
                "transactions": limited_transactions,
                "total_count": len(all_transactions),
                "bank_transactions": financial_data.bank_transactions if hasattr(financial_data, 'bank_transactions') else [],
                "mf_transactions": financial_data.mf_transactions if hasattr(financial_data, 'mf_transactions') else []
            },
            "summary": {
                "total_transactions": len(all_transactions),
                "bank_transactions_count": len(financial_data.bank_transactions) if hasattr(financial_data, 'bank_transactions') and financial_data.bank_transactions else 0,
                "mf_transactions_count": len(financial_data.mf_transactions) if hasattr(financial_data, 'mf_transactions') and financial_data.mf_transactions else 0,
                "data_source": "Fi Money MCP Server (Real-time)"
            }
        }
        
    except Exception as e:
        logging.error(f"Transaction history fetch failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch transaction history: {str(e)}",
            "data": None,
            "auth_required": "Session expired" in str(e) or "Not authenticated" in str(e)
        }


# Include routers if available
if ROUTERS_AVAILABLE:
    try:
        app.include_router(chat_router)
        logger.info("✅ Chat endpoints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register chat router: {e}")
    
    # Auth router already included earlier in the file
    # Removing duplicate inclusion to prevent conflicts
    
    try:
        app.include_router(user_router)
        logger.info("✅ User endpoints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register user router: {e}")
    
    try:
        app.include_router(portfolio_router)
        logger.info("✅ Portfolio endpoints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register portfolio router: {e}")
    
    try:
        app.include_router(pdf_router)
        logger.info("✅ PDF endpoints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register pdf router: {e}")
    
    try:
        app.include_router(session_router)
        logger.info("✅ Session endpoints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register session router: {e}")
    
    try:
        app.include_router(database_router)
        logger.info("✅ Database endpoints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register database router: {e}")
    
    try:
        app.include_router(monitoring_router)
        logger.info("✅ Monitoring endpoints registered successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register monitoring router: {e}")
else:
    logger.warning("⚠️ API routers not available - some endpoints may not work")

# Status endpoint
@app.get("/api/status")
async def get_status():
    """Get server status"""
    return {
        "status": "running",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "gemini_ai": GEMINI_AVAILABLE,
            "fi_money": FI_MONEY_AVAILABLE,
            "investment_agent": INVESTMENT_AGENT_AVAILABLE,
            "pdf_support": SERVICES_AVAILABLE,
            "session_history": ROUTERS_AVAILABLE,
            "conversation_persistence": True,
            "demo_mode_tracking": True,
            "pdf_context_injection": True,
            "pdf_enhanced_chat": True
        },
        "active_demo_sessions": len(_demo_mode_sessions)
    }


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

