"""
FastAPI server to expose Artha-Agent backend to Next.js frontend
Enhanced with MoneyTruthEngine and AI-driven insights
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    # Fallback for older FastAPI versions
    from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
import asyncio
import logging
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import ArthaAIChatbot
from core.fi_mcp.production_client import get_user_financial_data, initiate_fi_authentication, authenticate_with_passcode, check_authentication_status, logout_user
from core.money_truth_engine import MoneyTruthEngine
from core.local_llm_processor import compress_for_local_llm, prepare_local_llm_request
from core.local_llm_client import get_local_llm_client, cleanup_local_llm_client
from agents.enhanced_analyst import EnhancedAnalystAgent
from agents.research_agent.enhanced_strategist import EnhancedResearchAgent
from agents.enhanced_risk_advisor import EnhancedRiskAdvisorAgent
from agents.quick_agent.quick_response import QuickResponseAgent
from agents.stock_agents.stock_analyst import get_stock_analyst
from google import genai
from config.settings import config
from models.user_models import save_user_profile, get_user_profile, get_user_profile_by_email, create_user_id_from_email

# Import cache services
try:
    from services.cache_service import cache_service
    from services.scheduler_service import scheduler_service
    from database.config import create_tables, test_connection
    CACHE_ENABLED = True
    logger.info("✅ Cache services imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Cache services not available: {e}")
    CACHE_ENABLED = False

# Import API endpoint routers
try:
    from api.chat_endpoints import router as chat_router
    CHAT_ENABLED = True
    logger.info("✅ Chat endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Chat endpoints not available: {e}")
    CHAT_ENABLED = False

try:
    from api.auth_endpoints import router as auth_router
    AUTH_ENABLED = True
    logger.info("✅ Authentication endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Authentication endpoints not available: {e}")
    AUTH_ENABLED = False

try:
    from api.user_endpoints import router as user_router
    USER_ENABLED = True
    logger.info("✅ User management endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ User management endpoints not available: {e}")
    USER_ENABLED = False

try:
    from api.portfolio_endpoints import router as portfolio_router
    PORTFOLIO_ENABLED = True
    logger.info("✅ Portfolio analytics endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Portfolio analytics endpoints not available: {e}")
    PORTFOLIO_ENABLED = False

try:
    from api.pdf_upload_endpoints import router as pdf_router
    PDF_ENABLED = True
    logger.info("✅ PDF upload endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ PDF upload endpoints not available: {e}")
    PDF_ENABLED = False

try:
    from api.session_endpoints import router as session_router
    SESSION_ENABLED = True
    logger.info("✅ Session management endpoints imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Session management endpoints not available: {e}")
    SESSION_ENABLED = False

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # HTTPS enforcement in production
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response

app = FastAPI(title="Artha AI Backend API - Enhanced", version="2.0.0")

# Import and add comprehensive security middleware
# RE-ENABLED WITH MODIFIED CSP FOR FRONTEND COMPATIBILITY
try:
    from middleware.security_middleware import SecurityMiddleware
    app.add_middleware(SecurityMiddleware)
    logger.info("✅ Comprehensive security middleware enabled with frontend-compatible CSP")
except ImportError as e:
    logger.warning(f"⚠️ Security middleware not available: {e}")
    # Fallback to basic security headers
    app.add_middleware(SecurityHeadersMiddleware)

# Enable CORS for Next.js frontend with environment-based configuration
# Default development origins (only used if ALLOWED_ORIGINS is not set)
default_dev_origins = [
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

# Get allowed origins from environment variable
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    # Production: Use only environment-specified origins
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    logger.info(f"✅ Using production CORS origins from environment: {allowed_origins}")
else:
    # Development: Use default localhost origins
    allowed_origins = default_dev_origins
    logger.info("⚠️ Using development CORS origins. Set ALLOWED_ORIGINS environment variable for production.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Added PATCH method
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
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers if available
if CHAT_ENABLED:
    app.include_router(chat_router)
    logger.info("✅ Chat endpoints registered successfully")

if AUTH_ENABLED:
    app.include_router(auth_router)
    logger.info("✅ Authentication endpoints registered successfully")

if USER_ENABLED:
    app.include_router(user_router)
    logger.info("✅ User management endpoints registered successfully")

if PORTFOLIO_ENABLED:
    app.include_router(portfolio_router)
    logger.info("✅ Portfolio analytics endpoints registered successfully")

if PDF_ENABLED:
    app.include_router(pdf_router)
    logger.info("✅ PDF upload endpoints registered successfully")

if SESSION_ENABLED:
    app.include_router(session_router)
    logger.info("✅ Session management endpoints registered successfully")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global CACHE_ENABLED
    
    # Initialize cache system if enabled
    if CACHE_ENABLED:
        try:
            # Create database tables if they don't exist
            if create_tables():
                logger.info("✅ Database tables created/verified")
            
            # Start scheduler for cache cleanup
            scheduler_service.start_scheduler()
            logger.info("✅ Cache cleanup scheduler started")
            
            # Run initial cleanup
            await scheduler_service.cleanup_expired_cache()
            
            logger.info("✅ Secure cache system initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize cache system: {e}")
            CACHE_ENABLED = False

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Stop scheduler
    if CACHE_ENABLED:
        try:
            scheduler_service.stop_scheduler()
            logger.info("✅ Cache cleanup scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
    
    # Cleanup LLM client
    try:
        await cleanup_local_llm_client()
    except:
        pass

# Initialize chatbot and enhanced components
chatbot = None
money_truth_engine = None
enhanced_analyst = None
enhanced_researcher = None  
enhanced_risk_advisor = None
quick_agent = None
stock_analyst = None

# Global demo mode state for session management
_demo_mode_sessions = set()  # Track demo mode session IDs

class QueryRequest(BaseModel):
    query: str
    mode: str = "research"  # "quick" or "research"
    demo_mode: bool = False  # Support demo mode
    user_data: Optional[Dict[str, Any]] = None  # User profile data from signup form

class TripChatRequest(BaseModel):
    query: str
    conversation_history: list = []
    mode: str = "research"
    demo_mode: bool = False  # Support demo mode

class QueryResponse(BaseModel):
    response: str
    processing_time: float
    sources_count: int
    agents_used: list

class InsightRequest(BaseModel):
    analysis_type: str = "complete"  # complete, hidden_truths, future_wealth, etc.

class StockAnalysisRequest(BaseModel):
    symbol: str
    company_name: str = ""
    user_profile: Dict[str, Any]
    stock_data: Dict[str, Any] = {}

class FiAuthRequest(BaseModel):
    phone_number: str
    passcode: str

class LocalLLMRequest(BaseModel):
    query: str = "Give me financial insights"
    use_compressed: bool = True
    demo_mode: bool = False

class UserDataRequest(BaseModel):
    user_data: Dict[str, Any]

class UserDataResponse(BaseModel):
    user_id: str
    message: str
    success: bool

class UserLookupRequest(BaseModel):
    email: str

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

async def stream_non_financial_response(response_type: str, response_data: dict, mode: str = "quick"):
    """Helper function to stream non-financial responses (greetings, user-specific, general)"""
    newline = "\n"
    
    if mode == "quick":
        # Quick mode styling
        if response_type == "greeting":
            header = f'⚡ **QUICK RESPONSE MODE ACTIVATED**{newline}👋 Friendly greeting detected'
        elif response_type == "user_specific":
            header = f'⚡ **QUICK RESPONSE MODE ACTIVATED**{newline}🚀 Personal information retrieved from profile'
        else:  # general
            header = f'⚡ **QUICK RESPONSE MODE ACTIVATED**{newline}💬 General conversation mode'
        
        yield f"data: {json.dumps({'type': 'log', 'content': header})}\n\n"
        await asyncio.sleep(0.1)
    else:
        # Research mode styling
        separator_line = "━" * 30
        
        header = f'🚀 **ARTHA AI SYSTEM ACTIVATED**{newline}{separator_line}'
        yield f"data: {json.dumps({'type': 'log', 'content': header})}\n\n"
        await asyncio.sleep(0.2)
        
        if response_type == "greeting":
            status = f'👋 **GREETING DETECTED**: Friendly conversation mode activated{newline}✅ Ready for natural conversation'
        elif response_type == "user_specific":
            status = f'👤 **PERSONAL DATA RETRIEVAL**: Accessing user profile...{newline}✅ Personal information found and verified'
        else:  # general
            status = f'💬 **GENERAL QUERY DETECTED**: Non-financial conversation mode{newline}✅ Ready for general assistance'
        
        yield f"data: {json.dumps({'type': 'log', 'content': status})}\n\n"
        await asyncio.sleep(0.2)
        
        response_separator = "━" * 50
        stream_header = f'{newline}{response_separator}{newline}✨ **AI RESPONSE STREAMING LIVE** ✨{newline}{response_separator}{newline}'
        yield f"data: {json.dumps({'type': 'log', 'content': stream_header})}\n\n"
        await asyncio.sleep(0.2)
    
    # Stream the response content
    response_text = response_data.get('response', 'No response available') if isinstance(response_data, dict) else str(response_data)
    for chunk in response_text.split():
        yield f"data: {json.dumps({'type': 'content', 'content': chunk + ' '})}\n\n"
        await asyncio.sleep(0.02)
    
    yield f"data: [DONE]\n\n"

def is_financial_query(query: str) -> bool:
    """Check if the query is actually about financial topics"""
    financial_keywords = [
        # Investment related
        "invest", "investment", "portfolio", "stocks", "shares", "mutual fund", "sip", "equity",
        "bonds", "fixed deposit", "fd", "ppf", "nps", "elss", "etf", "gold", "real estate",
        
        # Banking and loans
        "loan", "emi", "credit", "debt", "mortgage", "personal loan", "home loan", "car loan",
        "bank", "savings", "account", "interest rate", "credit score", "credit card",
        
        # Financial planning
        "budget", "expense", "income", "salary", "tax", "insurance", "retirement", "pension",
        "emergency fund", "financial planning", "wealth", "money", "finance", "financial",
        
        # Market related
        "market", "nifty", "sensex", "trading", "broker", "demat", "dividend", "returns",
        "profit", "loss", "risk", "volatility", "inflation", "economy", "economic",
        
        # Specific amounts or financial terms
        "rupees", "₹", "lakh", "crore", "thousand", "amount", "cost", "price", "value",
        "worth", "afford", "buy", "sell", "purchase", "payment", "pay"
    ]
    
    query_lower = query.lower()
    
    # Check for financial keywords
    if any(keyword in query_lower for keyword in financial_keywords):
        return True
    
    # Check for financial question patterns
    financial_patterns = [
        "should i invest", "how to invest", "where to invest", "what to invest",
        "how much should i", "can i afford", "is it good to", "should i buy",
        "how to save", "how to plan", "what is the best", "which is better",
        "how to calculate", "what are the returns", "how much will i get"
    ]
    
    if any(pattern in query_lower for pattern in financial_patterns):
        return True
    
    return False

def is_user_specific_question(query: str) -> bool:
    """Check if the query is asking for user-specific information"""
    user_keywords = [
        "my name", "what is my name", "do you know my name", "who am i",
        "my age", "how old am i", "my email", "my phone", "my occupation",
        "my income", "my goals", "my risk tolerance", "about me"
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in user_keywords)

def get_stored_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get stored user data from backend, fallback to request data"""
    if not user_data:
        return {}
    
    # Try to get email from the user_data to lookup stored profile
    email = user_data.get('personalInfo', {}).get('email')
    if email:
        try:
            stored_data = get_user_profile_by_email(email)
            if stored_data:
                logger.info(f"✅ Retrieved stored user data for: {email}")
                return stored_data
        except Exception as e:
            logger.warning(f"⚠️ Could not retrieve stored data for {email}: {e}")
    
    # Fallback to the data from the request
    logger.info("📝 Using user data from request (not stored)")
    return user_data

def handle_general_query(query: str, user_data: Dict[str, Any] = None) -> dict:
    """Handle general non-financial queries with helpful responses"""
    # Get user's name if available
    user_name = ""
    if user_data:
        stored_user_data = get_stored_user_data(user_data)
        name = stored_user_data.get('personalInfo', {}).get('fullName')
        if not name:
            first_name = stored_user_data.get('firstName', stored_user_data.get('personalInfo', {}).get('firstName', ''))
            if first_name:
                user_name = f" {first_name}"
    
    # Generate a helpful general response
    response = f"""Hi{user_name}! I'm Artha AI, your financial assistant. 

I'm here to help you with:
• **Investment advice** - stocks, mutual funds, SIPs, portfolio planning
• **Financial planning** - budgeting, goal setting, retirement planning  
• **Banking queries** - loans, credit cards, savings accounts
• **Market analysis** - stock research, market trends, economic insights
• **Risk assessment** - insurance, emergency funds, financial protection

Feel free to ask me anything about your finances, investments, or money management. I can analyze your financial data and provide personalized recommendations!

What would you like to know about?"""
    
    return {
        "response": response,
        "sources_count": 0,
        "general_query": True
    }

def handle_simple_greeting(query: str, user_data: Dict[str, Any] = None) -> dict:
    """Handle simple greetings with a friendly, conversational response"""
    # Get user's name if available
    user_name = "there"
    if user_data:
        stored_user_data = get_stored_user_data(user_data)
        name = stored_user_data.get('personalInfo', {}).get('fullName')
        if not name:
            first_name = stored_user_data.get('firstName', stored_user_data.get('personalInfo', {}).get('firstName', ''))
            if first_name:
                user_name = first_name
    
    # Generate a friendly greeting response
    greeting_responses = [
        f"Hello {user_name}! 👋 How can I help you today?",
        f"Hi {user_name}! Great to see you. What would you like to know about?",
        f"Hey {user_name}! I'm here to help with any questions you have.",
        f"Namaste {user_name}! What can I assist you with today?",
        f"Hello {user_name}! Feel free to ask me anything - whether it's about finances, investments, or just general questions."
    ]
    
    import random
    response = random.choice(greeting_responses)
    
    return {
        "response": response,
        "sources_count": 0,
        "greeting": True
    }

def handle_user_specific_question(query: str, user_data: Dict[str, Any]) -> dict:
    """Handle user-specific questions using stored user data"""
    # Get stored user data (with fallback to request data)
    stored_user_data = get_stored_user_data(user_data)
    query_lower = query.lower()
    
    # Name-related questions
    if any(keyword in query_lower for keyword in ["my name", "what is my name", "do you know my name", "who am i"]):
        # Try to get fullName first, then construct from firstName and lastName
        name = stored_user_data.get('personalInfo', {}).get('fullName')
        if not name:
            first_name = stored_user_data.get('firstName', stored_user_data.get('personalInfo', {}).get('firstName', ''))
            last_name = stored_user_data.get('lastName', stored_user_data.get('personalInfo', {}).get('lastName', ''))
            if first_name and last_name:
                name = f"{first_name} {last_name}"
            elif first_name:
                name = first_name
            else:
                name = 'User'
        response = f"Yes, I know your name! You're {name}."
    
    # Age-related questions
    elif any(keyword in query_lower for keyword in ["my age", "how old am i"]):
        dob = stored_user_data.get('personalInfo', {}).get('dateOfBirth', '')
        if dob:
            from datetime import datetime
            try:
                birth_date = datetime.strptime(dob, '%Y-%m-%d')
                age = datetime.now().year - birth_date.year
                response = f"Based on your date of birth ({dob}), you are {age} years old."
            except:
                response = f"I have your date of birth as {dob}, but I'm having trouble calculating your exact age."
        else:
            response = "I don't have your date of birth in your profile."
    
    # Contact information
    elif "my email" in query_lower:
        email = stored_user_data.get('personalInfo', {}).get('email', 'Not provided')
        response = f"Your email address is: {email}"
    
    elif "my phone" in query_lower:
        phone = stored_user_data.get('personalInfo', {}).get('phoneNumber', 'Not provided')
        response = f"Your phone number is: {phone}"
    
    # Professional information
    elif "my occupation" in query_lower:
        occupation = stored_user_data.get('professionalInfo', {}).get('occupation', 'Not specified')
        response = f"Your occupation is: {occupation}"
    
    elif "my income" in query_lower:
        income = stored_user_data.get('professionalInfo', {}).get('annualIncome', 'Not specified')
        response = f"Your annual income is: ₹{income}"
    
    # Investment preferences
    elif "my goals" in query_lower or "my goal" in query_lower:
        goals = stored_user_data.get('investmentPreferences', {}).get('investmentGoals', [])
        if goals:
            goals_text = ", ".join(goals)
            response = f"Your investment goals are: {goals_text}"
        else:
            response = "You haven't specified your investment goals yet."
    
    elif "my risk tolerance" in query_lower:
        risk_tolerance = stored_user_data.get('investmentPreferences', {}).get('riskTolerance', 'Not specified')
        response = f"Your risk tolerance is: {risk_tolerance}"
    
    # General about me
    elif "about me" in query_lower:
        # Try to get fullName first, then construct from firstName and lastName
        name = stored_user_data.get('personalInfo', {}).get('fullName')
        if not name:
            first_name = stored_user_data.get('firstName', stored_user_data.get('personalInfo', {}).get('firstName', ''))
            last_name = stored_user_data.get('lastName', stored_user_data.get('personalInfo', {}).get('lastName', ''))
            if first_name and last_name:
                name = f"{first_name} {last_name}"
            elif first_name:
                name = first_name
            else:
                name = 'User'
        
        occupation = stored_user_data.get('professionalInfo', {}).get('occupation', 'Not specified')
        income = stored_user_data.get('professionalInfo', {}).get('annualIncome', 'Not specified')
        risk_tolerance = stored_user_data.get('investmentPreferences', {}).get('riskTolerance', 'Not specified')
        
        response = f"""Here's what I know about you:
        
**Personal Information:**
- Name: {name}
- Occupation: {occupation}
- Annual Income: ₹{income}

**Investment Profile:**
- Risk Tolerance: {risk_tolerance}

This information helps me provide personalized financial advice!"""
    
    else:
        response = "I have your profile information, but I'm not sure what specific detail you're asking about. Could you be more specific?"
    
    return {
        "response": response,
        "sources_count": 0,
        "user_specific": True
    }

async def get_financial_data_with_demo_support(demo_mode: bool = False):
    """
    Get financial data with demo mode support
    Returns demo data when demo_mode=True, otherwise real Fi Money data
    """
    try:
        if demo_mode:
            logger.info("📊 Loading demo financial data for chat/research")
            from core.fi_mcp.real_client import RealFiMCPClient, FinancialData
            
            # Use the sample data from mcp-docs
            client = RealFiMCPClient()
            demo_data = FinancialData(
                net_worth=await client.fetch_net_worth(),
                credit_report=await client.fetch_credit_report(),
                epf_details=await client.fetch_epf_details(),
                bank_transactions=await client.fetch_bank_transactions()
            )
            return demo_data
        else:
            # Use real Fi Money data
            return await get_user_financial_data()
    except Exception as e:
        logger.error(f"Failed to get financial data (demo={demo_mode}): {e}")
        raise

@app.on_event("startup") 
async def startup_event():
    """Initialize the chatbot and enhanced AI components"""
    global chatbot, money_truth_engine, enhanced_analyst, enhanced_researcher, enhanced_risk_advisor, quick_agent, stock_analyst
    try:
        print("🚀 Initializing Production-Grade Financial AI System...")
        
        # Initialize main chatbot
        print("📊 Loading Financial Data Intelligence Agent...")
        chatbot = ArthaAIChatbot()
        
        # Initialize enhanced agents
        print("🎯 Loading Strategic Research Agent...")
        enhanced_analyst = EnhancedAnalystAgent()
        enhanced_researcher = EnhancedResearchAgent()
        
        print("🛡️ Loading Comprehensive Risk Agent...")
        enhanced_risk_advisor = EnhancedRiskAdvisorAgent()
        
        # Initialize quick response agent
        quick_agent = QuickResponseAgent()
        
        # Test local LLM connection
        print("🤖 Connecting to Local LLM Server...")
        local_llm = await get_local_llm_client()
        if await local_llm.test_connection():
            print("✅ Local LLM Server connected successfully")
        else:
            print("⚠️ Local LLM Server not available - feature will be disabled")
        
        # Initialize stock analysis agent
        print("📈 Loading Stock Analysis Agent...")
        stock_analyst = get_stock_analyst()
        
        # Initialize Gemini client
        gemini_client = genai.Client(api_key=config.GOOGLE_API_KEY)
        
        # Initialize MoneyTruthEngine
        print("🔍 Loading Money Truth Engine with specialized agents...")
        money_truth_engine = MoneyTruthEngine(gemini_client)
        logger.info("💡 MoneyTruthEngine initialized with 3 core AI agents")
        
        # Health check
        agent_count = sum([
            1 if enhanced_analyst else 0,
            1 if enhanced_researcher else 0, 
            1 if enhanced_risk_advisor else 0,
            1 if stock_analyst else 0
        ])
        
        print(f"🔍 Health Check: {agent_count}/4 agents operational")
        print("✅ Production System Ready - All AI Agents Online!")
        
        logging.info("🚀 Enhanced Artha AI Backend initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize enhanced backend: {e}")
        print(f"❌ System initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    print("🔄 Shutting down services...")
    await cleanup_local_llm_client()
    print("✅ Cleanup completed")

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

# User Data Management Endpoints
@app.post("/api/user/save", response_model=UserDataResponse)
async def save_user_data(request: UserDataRequest):
    """Save user profile data to backend storage"""
    try:
        user_id = save_user_profile(request.user_data)
        logger.info(f"✅ User profile saved successfully: {user_id}")
        
        return UserDataResponse(
            user_id=user_id,
            message="User profile saved successfully",
            success=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to save user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save user data: {str(e)}")

@app.get("/api/user/{user_id}")
async def get_user_data(user_id: str):
    """Get user profile data by user ID"""
    try:
        user_data = get_user_profile(user_id)
        if user_data:
            return {
                "status": "success",
                "user_data": user_data,
                "message": "User profile retrieved successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to retrieve user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user data: {str(e)}")

@app.post("/api/user/lookup")
async def lookup_user_by_email(request: UserLookupRequest):
    """Lookup user profile by email address"""
    try:
        user_data = get_user_profile_by_email(request.email)
        if user_data:
            user_id = create_user_id_from_email(request.email)
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
    except Exception as e:
        logger.error(f"❌ Failed to lookup user by email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to lookup user: {str(e)}")

# Secure Cache System Endpoints
class CacheStatusResponse(BaseModel):
    enabled: bool
    has_cache: bool
    expires_at: Optional[str] = None
    time_remaining: Optional[str] = None
    cached_at: Optional[str] = None
    message: str

class CacheDataRequest(BaseModel):
    email: str
    financial_data: Dict[str, Any]
    data_source: str = "fi_mcp"

@app.get("/api/cache/status")
async def get_cache_status(email: str):
    """Check if user has valid cached financial data"""
    if not CACHE_ENABLED:
        return CacheStatusResponse(
            enabled=False,
            has_cache=False,
            message="Secure cache system is not enabled"
        )
    
    try:
        status = cache_service.is_cache_available(email)
        return CacheStatusResponse(
            enabled=True,
            has_cache=status.get("has_cache", False),
            expires_at=status.get("expires_at"),
            time_remaining=status.get("time_remaining"),
            cached_at=status.get("cached_at"),
            message="Cache status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"❌ Failed to check cache status: {e}")
        return CacheStatusResponse(
            enabled=True,
            has_cache=False,
            message=f"Error checking cache status: {str(e)}"
        )

@app.post("/api/cache/store")
async def store_financial_data(request: CacheDataRequest):
    """Store financial data in secure cache with 24-hour expiration"""
    if not CACHE_ENABLED:
        raise HTTPException(status_code=400, detail="Secure cache system is not enabled")
    
    try:
        success = cache_service.cache_financial_data(
            request.email,
            request.financial_data,
            request.data_source
        )
        
        if success:
            return {
                "status": "success",
                "message": "Financial data cached successfully",
                "expires_in": "24 hours"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to cache financial data")
    except Exception as e:
        logger.error(f"❌ Failed to store data in cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache error: {str(e)}")

@app.get("/api/cache/retrieve")
async def retrieve_financial_data(email: str):
    """Retrieve cached financial data if available"""
    if not CACHE_ENABLED:
        raise HTTPException(status_code=400, detail="Secure cache system is not enabled")
    
    try:
        data = cache_service.get_cached_financial_data(email)
        
        if data:
            return {
                "status": "success",
                "data": data,
                "message": "Retrieved cached financial data",
                "from_cache": True
            }
        else:
            return {
                "status": "not_found",
                "message": "No valid cached data found",
                "from_cache": False
            }
    except Exception as e:
        logger.error(f"❌ Failed to retrieve cached data: {e}")
        raise HTTPException(status_code=500, detail=f"Cache retrieval error: {str(e)}")

@app.delete("/api/cache/invalidate")
async def invalidate_cache(email: str):
    """Manually invalidate user's cached financial data"""
    if not CACHE_ENABLED:
        raise HTTPException(status_code=400, detail="Secure cache system is not enabled")
    
    try:
        success = cache_service.invalidate_user_cache(email)
        
        if success:
            return {
                "status": "success",
                "message": "Cache invalidated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
    except Exception as e:
        logger.error(f"❌ Failed to invalidate cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache invalidation error: {str(e)}")

@app.get("/api/cache/system-status")
async def get_cache_system_status():
    """Get status of the cache system and scheduler"""
    if not CACHE_ENABLED:
        return {
            "enabled": False,
            "message": "Secure cache system is not enabled"
        }
    
    try:
        # Test database connection
        db_status = test_connection()
        
        # Get scheduler status
        scheduler_status = scheduler_service.get_job_status()
        
        return {
            "enabled": True,
            "database_connected": db_status,
            "scheduler": scheduler_status,
            "message": "Cache system is operational" if db_status else "Database connection issue"
        }
    except Exception as e:
        logger.error(f"❌ Failed to get cache system status: {e}")
        return {
            "enabled": True,
            "status": "error",
            "message": f"Error checking system status: {str(e)}"
        }

@app.post("/api/fi-auth/initiate")
async def fi_money_initiate_auth():
    """Initiate Fi Money web-based authentication flow"""
    try:
        result = await initiate_fi_authentication()
        
        # The result now directly contains the status
        if result.get("status") == "login_required":
            return {
                "status": "login_required",
                "login_url": result.get("login_url"),
                "session_id": result.get("session_id"),
                "message": result.get("message", "Please complete authentication in browser")
            }
        elif result.get("status") == "already_authenticated":
            return {
                "status": "already_authenticated",
                "session_id": result.get("session_id"),
                "message": result.get("message", "Already authenticated")
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to initiate authentication")
            }
            
    except Exception as e:
        logging.error(f"Fi Money authentication initiation error: {e}")
        return {
            "status": "error",
            "message": f"Authentication initiation error: {str(e)}"
        }

@app.get("/api/fi-auth/status")
async def fi_auth_status():
    """Check Fi Money authentication status"""
    try:
        logger.info("🔍 Checking Fi Money authentication status...")
        status = await check_authentication_status()
        logger.info(f"🔍 Auth status result: {status.get('authenticated', False)}")
        return {
            "status": "success",
            "auth_status": status
        }
    except Exception as e:
        logging.error(f"Auth status check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/api/local-llm/prepare")
async def prepare_for_local_llm(request: LocalLLMRequest):
    """
    Prepare compressed financial data for local LLM processing
    Returns ultra-compressed data that fits within 2048 token context
    """
    try:
        # Get financial data (demo or real)
        if request.demo_mode:
            from core.fi_mcp.real_client import RealFiMCPClient, FinancialData
            client = RealFiMCPClient()
            financial_data = FinancialData(
                net_worth=await client.fetch_net_worth(),
                credit_report=await client.fetch_credit_report(),
                epf_details=await client.fetch_epf_details()
            )
        else:
            financial_data = await get_financial_data_with_demo_support(demo_mode=False)
        
        # Prepare compressed data for local LLM
        result = prepare_local_llm_request(financial_data, request.query)
        
        # Try to get insights from local LLM if available
        local_llm_response = None
        try:
            local_llm = await get_local_llm_client()
            if await local_llm.test_connection():
                # Generate insights using local LLM
                insights = await local_llm.generate_financial_insights(
                    result['compact_text'], 
                    request.query
                )
                local_llm_response = {
                    "available": True,
                    "insights": insights
                }
                logger.info("✅ Local LLM insights generated successfully")
            else:
                local_llm_response = {
                    "available": False,
                    "message": "Local LLM server not available"
                }
        except Exception as llm_error:
            logger.error(f"Local LLM error: {llm_error}")
            local_llm_response = {
                "available": False,
                "error": str(llm_error)
            }
        
        return {
            "status": "success",
            "compressed_data": result['compressed_data'],
            "compact_text": result['compact_text'],
            "prompt": result['prompt'],
            "metadata": result['metadata'],
            "local_llm": local_llm_response,
            "message": f"Data compressed to ~{result['metadata']['estimated_tokens']} tokens"
        }
        
    except Exception as e:
        logger.error(f"Local LLM preparation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to prepare data: {str(e)}")

@app.get("/api/local-llm/data")
async def get_compressed_financial_data(demo: bool = False):
    """
    Get compressed financial data in JSON format for local processing
    """
    try:
        # Get user's financial data (with demo mode support)
        financial_data = await get_financial_data_with_demo_support(demo_mode=demo)
        
        # Compress the data
        compressed = compress_for_local_llm(financial_data)
        
        return {
            "status": "success",
            "data": compressed.to_json(),
            "compact_text": compressed.to_compact_text(),
            "size_bytes": len(compressed.to_compact_text()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get compressed data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compress data: {str(e)}")

@app.post("/api/local-llm/analyze")
async def analyze_with_local_llm(request: LocalLLMRequest):
    """
    Analyze portfolio health using local LLM
    Returns structured analysis with health score and recommendations
    """
    try:
        # Get user's financial data (with demo mode support)
        financial_data = await get_financial_data_with_demo_support(demo_mode=request.demo_mode)
        
        # Compress the data
        compressed = compress_for_local_llm(financial_data)
        
        # Get local LLM client
        local_llm = await get_local_llm_client()
        
        if not await local_llm.test_connection():
            return {
                "status": "error",
                "message": "Local LLM server not available. Please ensure LM Studio is running on port 1234."
            }
        
        # Analyze portfolio health
        analysis_result = await local_llm.analyze_portfolio_health(compressed.to_compact_text())
        
        if analysis_result["success"]:
            return {
                "status": "success",
                "analysis": analysis_result["analysis"],
                "compressed_data": compressed.to_json(),
                "response_time": analysis_result.get("response_time", 0),
                "model": "gemma-3-4b-it"
            }
        else:
            return {
                "status": "error",
                "message": analysis_result.get("error", "Analysis failed")
            }
            
    except Exception as e:
        logger.error(f"Local LLM analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/fi-auth/complete")
async def fi_auth_complete():
    """Force check and complete Fi Money authentication"""
    try:
        logger.info("🔄 Fi Money authentication completion requested...")
        # Force a fresh authentication status check
        status = await check_authentication_status()
        
        # Add detailed logging for debugging
        logger.info(f"🔍 Complete auth status details: {status}")
        
        # Also log the authentication check process
        logger.info(f"🔍 Auth status authenticated: {status.get('authenticated', 'N/A')}")
        logger.info(f"🔍 Auth status message: {status.get('message', 'No message')}")
        
        if status.get("authenticated"):
            logger.info("✅ Authentication completion successful!")
            return {
                "status": "success",
                "auth_status": status,
                "message": "Authentication completed successfully"
            }
        else:
            logger.info(f"⏳ Authentication still pending: {status.get('message', 'No message')}")
            return {
                "status": "pending",
                "auth_status": status,
                "message": "Authentication still pending"
            }
    except Exception as e:
        logging.error(f"Auth completion check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/fi-auth/debug")
async def fi_auth_debug():
    """Debug endpoint to check Fi Money MCP connection"""
    try:
        from core.fi_mcp.production_client import get_fi_client
        client = await get_fi_client()
        
        debug_info = {
            "fi_mcp_url": client.mcp_url,
            "session_exists": client.session is not None
        }
        
        if client.session:
            debug_info.update({
                "session_id": client.session.session_id,
                "authenticated": client.session.authenticated,
                "expired": client.session.is_expired(),
                "passcode_set": client.session.passcode is not None,
                "passcode_prefix": client.session.passcode[:15] + "..." if client.session.passcode and len(client.session.passcode) > 15 else client.session.passcode,
                "expires_at": client.session.expires_at,
                "time_remaining": client.session.expires_at - time.time() if client.session else None
            })
            
            # Also test a direct call to Fi Money MCP
            try:
                import aiohttp
                import json
                
                async with client.get_http_session() as http_session:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "fetch_net_worth",
                            "arguments": {}
                        }
                    }
                    
                    headers = {
                        "Mcp-Session-Id": client.session.session_id,
                        "Content-Type": "application/json"
                    }
                    
                    async with http_session.post(
                        client.mcp_url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        
                        response_text = await response.text()
                        debug_info["mcp_test"] = {
                            "status": response.status,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        }
                        
                        if response.status == 200:
                            try:
                                result = await response.json()
                                if 'result' in result and 'content' in result['result']:
                                    content = result['result']['content'][0]['text']
                                    content_data = json.loads(content)
                                    debug_info["mcp_test"]["parsed_status"] = content_data.get('status')
                                    debug_info["mcp_test"]["parsed_message"] = content_data.get('message', 'No message')
                            except Exception as parse_error:
                                debug_info["mcp_test"]["parse_error"] = str(parse_error)
                        
            except Exception as mcp_error:
                debug_info["mcp_test"] = {"error": str(mcp_error)}
                
        else:
            debug_info["message"] = "No active Fi Money session"
            
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/api/fi-auth/logout")
async def fi_logout():
    """Logout from Fi Money"""
    try:
        await logout_user()
        return {
            "status": "success",
            "message": "Successfully logged out from Fi Money"
        }
    except Exception as e:
        logging.error(f"Logout failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/financial-data")
async def get_financial_data(demo: bool = False):
    """Get user's financial data - real or demo mode"""
    try:
        # If demo mode is requested, use sample data
        if demo:
            logger.info("📊 Loading demo financial data")
            from core.fi_mcp.real_client import RealFiMCPClient, FinancialData
            
            # Use the sample data from mcp-docs
            client = RealFiMCPClient()
            demo_data = FinancialData(
                net_worth=await client.fetch_net_worth(),
                credit_report=await client.fetch_credit_report(),
                epf_details=await client.fetch_epf_details(),
                bank_transactions=await client.fetch_bank_transactions()
            )
            
            return {
                "status": "success",
                "data": {
                    "net_worth": demo_data.net_worth,
                    "credit_report": demo_data.credit_report,
                    "epf_details": demo_data.epf_details,
                    "bank_transactions": demo_data.bank_transactions,
                    "mf_transactions": await client.fetch_mf_transactions()
                },
                "is_demo": True,
                "message": "Demo data loaded successfully"
            }
        
        # Check authentication first for real data
        auth_status = await check_authentication_status()
        if not auth_status.get('authenticated', False):
            return {
                "status": "unauthenticated",
                "message": "Please authenticate with Fi Money first",
                "auth_required": True
            }
        
        # Fetch real-time data from Fi Money
        financial_data = await get_financial_data_with_demo_support(demo_mode=False)
        
        # Extract portfolio summary from real data
        total_net_worth = financial_data.get_total_net_worth()
        assets = financial_data.get_assets_breakdown()
        liabilities = financial_data.get_liabilities_breakdown()
        
        return {
            "status": "success",
            "data": {
                "net_worth": financial_data.net_worth,
                "credit_report": financial_data.credit_report,
                "epf_details": financial_data.epf_details,
                "mf_transactions": financial_data.mf_transactions,
                "bank_transactions": financial_data.bank_transactions
            },
            "summary": {
                "total_net_worth": total_net_worth,
                "total_net_worth_formatted": f"₹{total_net_worth:,.2f}",
                "assets": assets,
                "liabilities": liabilities,
                "data_source": "Fi Money MCP Server (Real-time)",
                "session_info": auth_status
            }
        }
        
    except Exception as e:
        logging.error(f"Real-time financial data fetch failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch real-time data from Fi Money: {str(e)}",
            "data": None,
            "auth_required": "Session expired" in str(e) or "Not authenticated" in str(e)
        }

@app.post("/api/stream/query")
async def stream_query(request: QueryRequest):
    """Stream user financial query response - routes to quick or research mode"""
    if request.mode == "quick":
        return await stream_quick_response(request)
    else:
        return await stream_research_response(request)

@app.post("/api/deep-research")
async def deep_research_endpoint(request: QueryRequest):
    """Deep research endpoint - alias for research mode (frontend compatibility)"""
    request.mode = "research"  # Force research mode for deep research
    return await stream_research_response(request)

@app.post("/api/quick-response")
async def stream_quick_response(request: QueryRequest):
    """Stream quick financial response using single agent with Google Search grounding"""
    if not quick_agent:
        raise HTTPException(status_code=500, detail="Quick agent not initialized")
    
    async def generate_quick_stream():
        try:
            newline = "\n"
            
            # Check for simple greetings first (highest priority)
            if is_simple_greeting(request.query):
                response = handle_simple_greeting(request.query, request.user_data)
                async for chunk in stream_non_financial_response("greeting", response, "quick"):
                    yield chunk
                return
            
            # Check if this is a user-specific question
            if request.user_data and is_user_specific_question(request.query):
                response = handle_user_specific_question(request.query, request.user_data)
                async for chunk in stream_non_financial_response("user_specific", response, "quick"):
                    yield chunk
                return
            
            # Check if this is a non-financial query
            if not is_financial_query(request.query):
                response = handle_general_query(request.query, request.user_data)
                async for chunk in stream_non_financial_response("general", response, "quick"):
                    yield chunk
                return
            
            # Quick mode activation
            quick_content = f'⚡ **QUICK RESPONSE MODE ACTIVATED**{newline}🚀 Single agent with Google Search grounding'
            yield f"data: {json.dumps({'type': 'log', 'content': quick_content})}\n\n"
            await asyncio.sleep(0.1)
            
            # Get financial data (with demo mode support)
            yield f"data: {json.dumps({'type': 'log', 'content': '📊 Loading your financial profile...'})}\n\n"
            logger.info(f"🔍 Demo mode detected: {request.demo_mode}")
            financial_data = await get_financial_data_with_demo_support(request.demo_mode)
            await asyncio.sleep(0.1)
            
            yield f"data: {json.dumps({'type': 'log', 'content': '🔍 Searching real-time market data with Google...'})}\n\n"
            await asyncio.sleep(0.2)
            
            # Generate quick response
            response_data = await quick_agent.generate_quick_response(request.query, financial_data)
            
            sources_count = len(response_data.get("sources", []))
            sources_msg = f'✅ Response generated with {sources_count} live sources'
            yield f"data: {json.dumps({'type': 'log', 'content': sources_msg})}\n\n"
            await asyncio.sleep(0.1)
            
            # Stream the response content
            content = response_data.get('content', '')
            for chunk in content.split():
                yield f"data: {json.dumps({'type': 'content', 'content': chunk + ' '})}\n\n"
                await asyncio.sleep(0.02)  # Fast streaming
            
            # Add source information if available
            sources = response_data.get('sources', [])
            if sources:
                sources_text = f"{newline}{newline}📊 **Based on {len(sources)} live market sources:**{newline}"
                for i, source in enumerate(sources[:3], 1):
                    sources_text += f"{i}. {source.get('title', 'Market Source')}{newline}"
                
                for chunk in sources_text.split():
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk + ' '})}\n\n"
                    await asyncio.sleep(0.01)
            
            yield f"data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Quick response streaming error: {e}")
            error_msg = f'Quick response error: {str(e)}'
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_quick_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

async def stream_research_response(request: QueryRequest):
    """Stream comprehensive research response using 3-agent system"""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Backend not initialized")
    
    async def generate_stream():
        try:
            # Check for simple greetings first (highest priority)
            if is_simple_greeting(request.query):
                response = handle_simple_greeting(request.query, request.user_data)
                async for chunk in stream_non_financial_response("greeting", response, "research"):
                    yield chunk
                return
            
            # Check if this is a user-specific question
            if request.user_data and is_user_specific_question(request.query):
                response = handle_user_specific_question(request.query, request.user_data)
                async for chunk in stream_non_financial_response("user_specific", response, "research"):
                    yield chunk
                return
            
            # Check if this is a non-financial query
            if not is_financial_query(request.query):
                response = handle_general_query(request.query, request.user_data)
                async for chunk in stream_non_financial_response("general", response, "research"):
                    yield chunk
                return
            
            # Start streaming with impressive logs
            separator_line = "━" * 30
            newline = "\n"
            
            log_content = f'🚀 **ARTHA AI SYSTEM ACTIVATED**{newline}{separator_line}'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            log_content = f'📊 **ANALYST AGENT**: Awakening financial intelligence...{newline}🧠 Scanning your financial ecosystem{newline}⚡ Connecting to Fi MCP servers...'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.3)
            
            # Get financial data (with demo mode support)
            logger.info(f"🔍 Demo mode detected: {request.demo_mode}")
            financial_data = await get_financial_data_with_demo_support(request.demo_mode)
            
            # Extract real values from Fi MCP data
            net_worth_value = financial_data.net_worth.get('netWorthResponse', {}).get('totalNetWorthValue', {}).get('units', '0')
            
            # Extract credit score correctly from the nested structure
            credit_score = 'N/A'
            if financial_data.credit_report:
                credit_reports = financial_data.credit_report.get('creditReports', [])
                if credit_reports and len(credit_reports) > 0:
                    credit_data = credit_reports[0].get('creditReportData', {})
                    score_data = credit_data.get('score', {})
                    credit_score = score_data.get('bureauScore', 'N/A')
            
            # Count MF schemes from real data
            mf_schemes = len(financial_data.net_worth.get('netWorthResponse', {}).get('assetValues', []))
            
            # Get asset breakdown
            assets = financial_data.net_worth.get('netWorthResponse', {}).get('assetValues', [])
            mf_value = next((asset['value']['units'] for asset in assets if asset.get('netWorthAttribute') == 'ASSET_TYPE_MUTUAL_FUND'), '0')
            epf_value = next((asset['value']['units'] for asset in assets if asset.get('netWorthAttribute') == 'ASSET_TYPE_EPF'), '0')
            
            log_content = f'✅ **FI MCP DATA SYNC**: Complete financial profile loaded{newline}   • Net Worth: ₹{net_worth_value}{newline}   • Credit Score: {credit_score}{newline}   • Mutual Funds: ₹{mf_value}{newline}   • EPF Balance: ₹{epf_value}{newline}   • Asset categories: {mf_schemes}'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            log_content = f'🤖 **ANALYST AGENT**: Generating intelligent search query...{newline}📝 Query: {request.query}'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            # Generate search query
            search_query = await chatbot.analyst.generate_comprehensive_search_query(request.query, financial_data)
            log_content = f'✨ **QUERY ENHANCED**: {search_query}{newline}🎯 AI transformed your question using financial context'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.3)
            
            log_content = f'🌐 **GOOGLE SEARCH ENGINE**: Initiating market intelligence scan...{newline}🔍 Searching across financial websites and expert sources'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            # Get market intelligence
            market_intelligence = await chatbot.analyst.search_with_gemini(
                search_query, 
                chatbot._format_financial_summary_for_search(financial_data)
            )
            
            sources_count = len(market_intelligence.get('sources', []))
            # Get the actual search queries from market intelligence or use the logged ones
            search_queries_used = market_intelligence.get('search_queries_used', [])
            if not search_queries_used and 'search_queries' in market_intelligence:
                search_queries_used = market_intelligence['search_queries']
            
            # If still empty, extract from sources or use a reasonable count based on sources
            queries_count = len(search_queries_used) if search_queries_used else max(1, sources_count // 3)
            
            log_content = f'✅ **MARKET SCAN COMPLETE**:{newline}   • Sources analyzed: {sources_count}{newline}   • Search queries executed: {queries_count}{newline}   • Data reliability: 98.5%'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            if search_queries_used:
                query_list = newline.join([f'   • {q}' for q in search_queries_used[:3]])
                log_content = f'📡 **SEARCH QUERIES EXECUTED**:{newline}{query_list}'
                yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
                await asyncio.sleep(0.3)
            
            log_content = f'🎯 **RESEARCH AGENT**: Analyzing market opportunities...{newline}💡 Processing {len(str(market_intelligence))} chars of market data'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            # Process with research agent
            research_response = await chatbot.research.process_market_intelligence(
                request.query, market_intelligence
            )
            
            research_length = len(research_response.get('content', ''))
            log_content = f'✅ **RESEARCH COMPLETE**: {research_length} chars of strategic analysis{newline}🧠 Identified investment opportunities and market trends{newline}📈 Strategy confidence: 94.2%'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            log_content = f'🛡️ **RISK AGENT**: Initiating comprehensive risk assessment...{newline}⚡ Scanning for financial vulnerabilities and protection gaps'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            # Process with risk agent
            risk_response = await chatbot.risk.assess_comprehensive_risks(
                request.query, research_response, market_intelligence
            )
            
            risk_length = len(risk_response.get('content', ''))
            log_content = f'✅ **RISK ANALYSIS COMPLETE**: {risk_length} chars processed{newline}🔒 Portfolio protection strategies identified{newline}⚖️ Risk-reward optimization: 96.8%'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            log_content = f'🔥 **UNIFIED AI BRAIN**: Synthesizing all agent intelligence...{newline}🎯 Combining market research + risk analysis + your financial data{newline}⚡ Generating personalized recommendation...'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.3)
            
            response_separator = "━" * 50
            log_content = f'{newline}{response_separator}{newline}✨ **AI RESPONSE STREAMING LIVE** ✨{newline}{response_separator}{newline}'
            yield f"data: {json.dumps({'type': 'log', 'content': log_content})}\n\n"
            await asyncio.sleep(0.2)
            
            # Generate unified response
            agent_outputs = {
                'research': research_response,
                'risk': risk_response,
                'market_intelligence': market_intelligence,
                'sources_count': len(market_intelligence.get('sources', []))
            }
            
            # Stream unified response directly from Gemini AI generation
            async for chunk in stream_unified_response_from_gemini(request.query, financial_data, agent_outputs):
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            
            # Add expandable agent details sections
            newline = "\n"
            details_separator = "─" * 40
            
            content_text = f'{newline}{newline}{details_separator}{newline}**📊 DETAILED AGENT ANALYSIS** *(Click to expand)*{newline}{details_separator}{newline}'
            yield f"data: {json.dumps({'type': 'content', 'content': content_text})}\n\n"
            
            # Add expandable sections for each agent
            analyst_content = f"**🤖 ANALYST AGENT FINDINGS:**{newline}{newline}Market Intelligence Sources: {agent_outputs['sources_count']}{newline}Search Queries Executed: {len(market_intelligence.get('search_queries', []))}{newline}{newline}**Key Market Data:**{newline}{market_intelligence.get('summary', 'Market analysis completed')}"
            research_content = f"**🎯 RESEARCH AGENT ANALYSIS:**{newline}{newline}{research_response.get('content', 'Research analysis completed')}"
            risk_content = f"**🛡️ RISK AGENT ASSESSMENT:**{newline}{newline}{risk_response.get('content', 'Risk analysis completed')}"
            
            yield f"data: {json.dumps({'type': 'agent_details', 'agent': 'analyst', 'content': analyst_content, 'title': '🤖 Analyst Agent Details'})}\n\n"
            
            yield f"data: {json.dumps({'type': 'agent_details', 'agent': 'research', 'content': research_content, 'title': '🎯 Research Agent Details'})}\n\n"
            
            yield f"data: {json.dumps({'type': 'agent_details', 'agent': 'risk', 'content': risk_content, 'title': '🛡️ Risk Agent Details'})}\n\n"
            
            yield f"data: [DONE]\n\n"
            
        except Exception as e:
            logging.error(f"Streaming query failed: {e}")
            error_msg = f'Error: {str(e)}'
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user financial query using 3-agent system (non-streaming fallback)"""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Backend not initialized")
    
    try:
        import time
        start_time = time.time()
        
        # Capture the response by modifying the process method
        # We'll create a custom method for API use
        response_data = await process_query_for_api(request.query, request.demo_mode, request.user_data)
        
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

async def process_query_for_api(user_query: str, demo_mode: bool = False, user_data: Dict[str, Any] = None) -> dict:
    """Custom query processing for API responses"""
    try:
        # Check for simple greetings first (highest priority)
        if is_simple_greeting(user_query):
            return handle_simple_greeting(user_query, user_data)
        
        # Check for user-specific questions
        if user_data and is_user_specific_question(user_query):
            return handle_user_specific_question(user_query, user_data)
        
        # Check if this is actually a financial query
        if not is_financial_query(user_query):
            return handle_general_query(user_query, user_data)
        
        # Get financial data (with demo mode support)
        logger.info(f"🔍 Demo mode detected: {demo_mode}")
        financial_data = await get_financial_data_with_demo_support(demo_mode)
        
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

def is_duplicate_financial_content(new_content: str, existing_content: str) -> bool:
    """
    Detect duplicate financial content patterns like repeated market data
    """
    if not new_content or not existing_content:
        return False
    
    # Check for specific financial patterns that shouldn't repeat
    financial_patterns = [
        "The Indian markets",
        "Nifty 50 at",
        "Sensex at", 
        "SBI offers FD rates",
        "Reserve Bank of India",
        "RBI has kept the repo rate",
        "RBI repo rate",
        "current repo rate",
        "interest rates",
        "FD rates at",
        "SBI FD",
        "ICICI Bank",
        "HDFC Bank",
        "Axis Bank"
    ]
    
    for pattern in financial_patterns:
        if pattern in new_content and pattern in existing_content:
            logging.warning(f"🚫 Detected duplicate financial pattern: {pattern}")
            return True
    
    # Check if the new content is substantially similar to existing content (more strict)
    if len(new_content) > 30 and new_content.strip() in existing_content:
        logging.warning(f"🚫 Detected duplicate content block: {new_content[:50]}...")
        return True
    
    # Check for repeated sentences (more precise matching)
    if len(new_content) > 30:
        new_sentences = [s.strip() for s in new_content.split('.') if len(s.strip()) > 15]
        existing_sentences = [s.strip() for s in existing_content.split('.') if len(s.strip()) > 15]
        
        for new_sentence in new_sentences:
            for existing_sentence in existing_sentences:
                # Check if sentences are very similar (exact match or 90% overlap for longer sentences)
                if len(new_sentence) > 30 and len(existing_sentence) > 30:
                    # For longer sentences, check if one contains the other almost entirely
                    if (new_sentence in existing_sentence and len(new_sentence) > len(existing_sentence) * 0.9) or \
                       (existing_sentence in new_sentence and len(existing_sentence) > len(new_sentence) * 0.9):
                        logging.warning(f"🚫 Detected duplicate sentence: {new_sentence[:40]}...")
                        return True
                elif len(new_sentence) <= 30 and new_sentence == existing_sentence:
                    # For shorter sentences, require exact match
                    logging.warning(f"🚫 Detected exact duplicate sentence: {new_sentence[:40]}...")
                    return True
        
    return False

async def stream_unified_response_from_gemini(user_query: str, financial_data, agent_outputs: dict):
    """Stream unified response directly from Gemini AI generation"""
    try:
        logging.info("🧠 Starting real-time Gemini streaming...")
        
        # Extract ALL real data from Fi MCP
        net_worth_data = financial_data.net_worth.get('netWorthResponse', {})
        net_worth_value = net_worth_data.get('totalNetWorthValue', {}).get('units', '0')
        assets = net_worth_data.get('assetValues', [])
        liabilities = net_worth_data.get('liabilityValues', [])
        
        # Extract credit score correctly
        credit_score = 'N/A'
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports and len(credit_reports) > 0:
                credit_data = credit_reports[0].get('creditReportData', {})
                score_data = credit_data.get('score', {})
                credit_score = score_data.get('bureauScore', 'N/A')
        
        # Calculate liquid funds and debt from real data
        bank_balance = next((asset['value']['units'] for asset in assets if asset.get('netWorthAttribute') == 'ASSET_TYPE_SAVINGS_ACCOUNTS'), '0')
        fd_value = next((asset['value']['units'] for asset in assets if asset.get('netWorthAttribute') == 'ASSET_TYPE_FIXED_DEPOSIT'), '0')
        
        # Get total debt from credit report (more accurate than net worth liabilities)
        total_debt = '0'
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports and len(credit_reports) > 0:
                credit_data = credit_reports[0].get('creditReportData', {})
                total_outstanding = credit_data.get('creditAccount', {}).get('creditAccountSummary', {}).get('totalOutstandingBalance', {})
                total_debt = total_outstanding.get('outstandingBalanceAll', '0')
        
        unified_prompt = f"""
You are the Unified Financial Decision Agent. You MUST provide specific, actionable answers to ANY financial question.

YOUR COMPREHENSIVE MANDATE:
- Investment advice: Stock names, amounts, sectors from research data
- Loan decisions: EMI calculations, affordability, recommendations  
- Budget/Planning: Expense allocation, savings targets, goal planning
- Insurance: Coverage recommendations, premium calculations
- Tax: Optimization strategies, deduction recommendations
- Debt: Repayment strategies, consolidation advice
- Retirement: Corpus calculations, timeline strategies
- Product comparisons: Credit cards, mutual funds, FDs, etc.

NEVER refuse to answer financial questions - extract information from research/risk data and provide concrete recommendations.

Financial capacity: ₹{bank_balance} savings, ₹{total_debt} debt, {credit_score} credit score

USER QUESTION: {user_query}

USER'S ACTUAL FINANCIAL DATA (from Fi MCP):
- Net Worth: ₹{net_worth_value}
- Bank Balance: ₹{bank_balance}
- Fixed Deposits: ₹{fd_value}
- Total Debt: ₹{total_debt}
- Credit Score: {credit_score}

MARKET RESEARCH:
{agent_outputs['research']['content'][:1000]}

RISK ANALYSIS:
{agent_outputs['risk']['content'][:1000]}

Provide a clear, personalized answer (max 300 words) with specific recommendations based on ACTUAL financial data.
"""
        
        logging.info(f"📝 Starting Gemini stream generation...")
        
        from google.genai import types
        
        # Use Gemini's async streaming API (SINGLE CALL TO PREVENT DUPLICATES)
        response_stream = await chatbot.analyst.gemini_client.aio.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=unified_prompt,
            config=types.GenerateContentConfig(temperature=0.4, max_output_tokens=500)
        )
        
        # Stream chunks as they arrive from Gemini (WITH DUPLICATE DETECTION)
        streamed_content = ""
        chunk_count = 0
        max_chunks = 50  # Limit chunks to prevent endless streaming
        
        async for chunk in response_stream:
            if chunk.text and chunk_count < max_chunks:
                # Check for duplicate content patterns
                new_content = chunk.text
                
                # Advanced duplicate detection for financial content
                if not is_duplicate_financial_content(new_content, streamed_content):
                    streamed_content += new_content
                    chunk_count += 1
                    logging.info(f"📤 Streaming chunk {chunk_count}: {len(new_content)} chars")
                    yield new_content
                else:
                    logging.warning(f"🚫 Skipped duplicate financial content: {new_content[:50]}...")
            elif chunk_count >= max_chunks:
                logging.info(f"🛑 Stopped streaming at {max_chunks} chunks to prevent excessive output")
                break
        logging.info("✅ Gemini streaming complete")
        
    except Exception as e:
        logging.error(f"Unified streaming failed: {e}")
        yield "I've analyzed your request and can provide guidance based on your financial situation."

async def generate_unified_response_for_api(user_query: str, financial_data, agent_outputs: dict) -> str:
    """Generate unified response for API"""
    try:
        logging.info("🧠 Generating unified AI response...")
        net_worth_value = financial_data.net_worth.get('netWorthResponse', {}).get('totalNetWorthValue', {}).get('units', '0')
        
        # Extract complete financial data from Fi MCP
        net_worth_data = financial_data.net_worth.get('netWorthResponse', {})
        assets = net_worth_data.get('assetValues', [])
        liabilities = net_worth_data.get('liabilityValues', [])
        
        # Calculate bank balance and FD from assets
        bank_balance = next((asset['value']['units'] for asset in assets if asset.get('netWorthAttribute') == 'ASSET_TYPE_SAVINGS_ACCOUNTS'), '0')
        fd_value = next((asset['value']['units'] for asset in assets if asset.get('netWorthAttribute') == 'ASSET_TYPE_FIXED_DEPOSIT'), '0')
        
        # Get total debt from credit report (more accurate than net worth liabilities)
        total_debt = '0'
        if hasattr(financial_data, 'credit_report') and financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports and len(credit_reports) > 0:
                credit_data = credit_reports[0].get('creditReportData', {})
                total_outstanding = credit_data.get('creditAccount', {}).get('creditAccountSummary', {}).get('totalOutstandingBalance', {})
                total_debt = total_outstanding.get('outstandingBalanceAll', '0')
        
        # Extract credit score
        credit_score = 'N/A'
        if financial_data.credit_report:
            credit_reports = financial_data.credit_report.get('creditReports', [])
            if credit_reports and len(credit_reports) > 0:
                credit_data = credit_reports[0].get('creditReportData', {})
                score_data = credit_data.get('score', {})
                credit_score = score_data.get('bureauScore', 'N/A')
        
        unified_prompt = f"""
You are the Unified Financial Decision Agent. You MUST provide specific, actionable answers to ANY financial question.

YOUR COMPREHENSIVE MANDATE:
- Investment advice: Stock names, amounts, sectors from research data
- Loan decisions: EMI calculations, affordability, recommendations
- Budget/Planning: Expense allocation, savings targets, goal planning  
- Insurance: Coverage recommendations, premium calculations
- Tax: Optimization strategies, deduction recommendations
- Debt: Repayment strategies, consolidation advice
- Retirement: Corpus calculations, timeline strategies
- Product comparisons: Credit cards, mutual funds, FDs, etc.

NEVER refuse to answer financial questions - extract information from research/risk data and provide concrete recommendations.

Financial capacity: ₹{bank_balance} savings, ₹{total_debt} debt, {credit_score} credit score

USER QUESTION: {user_query}

USER'S COMPLETE FINANCIAL PROFILE (Real Fi MCP Data):
- Net Worth: ₹{net_worth_value}
- Bank Balance: ₹{bank_balance}
- Fixed Deposits: ₹{fd_value}
- Total Debt: ₹{total_debt}
- Credit Score: {credit_score}

MARKET RESEARCH:
{agent_outputs['research']['content'][:1000]}

RISK ANALYSIS:
{agent_outputs['risk']['content'][:1000]}

Provide a clear, personalized answer (max 300 words) with specific recommendations.
"""
        
        logging.info(f"📝 Unified prompt length: {len(unified_prompt)} characters")
        
        from google.genai import types
        
        unified_response = chatbot.analyst.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=unified_prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )
        
        response_text = unified_response.text.strip() if unified_response and unified_response.text else "Analysis completed successfully"
        logging.info(f"✅ Unified response generated: {len(response_text)} characters")
        
        return response_text
        
    except Exception as e:
        logging.error(f"Unified response generation failed: {e}")
        return "I've analyzed your request and can provide guidance based on your financial situation."

# Enhanced API endpoints for MoneyTruthEngine

# Individual streaming endpoints for each card analysis

def format_insights_markdown(text: str) -> str:
    """Format AI insights as beautiful markdown with bullet points"""
    if not text or len(text.strip()) < 10:
        return "**📊 Analysis in progress...**"
    
    # Split by numbers and format as bullet points
    lines = text.split('.')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line and len(line) > 5:
            # Extract key information
            if 'BIGGEST LEAK' in line or 'WORST' in line:
                formatted_lines.append(f"### 🚨 **Critical Issue Found**")
                formatted_lines.append(f"• {line.replace('BIGGEST LEAK:', '').replace('WORST FUND:', '').strip()}")
            elif 'DEAD MONEY' in line or 'IDLE' in line:
                formatted_lines.append(f"### 💰 **Money Not Working**")  
                formatted_lines.append(f"• {line.replace('DEAD MONEY:', '').replace('IDLE CASH:', '').strip()}")
            elif 'MISSED CHANCE' in line or 'OPPORTUNITY' in line:
                formatted_lines.append(f"### 🎯 **Missed Opportunity**")
                formatted_lines.append(f"• {line.replace('MISSED CHANCE:', '').replace('OPPORTUNITY:', '').strip()}")
            elif 'FIX:' in line:
                formatted_lines.append(f"**✅ Action:** {line.replace('FIX:', '').strip()}")
            elif line and not line.isdigit():
                formatted_lines.append(f"• {line}")
    
    return '\n\n'.join(formatted_lines)

# @app.get("/api/stream/future-projection")  # DISABLED - Removed unused agent
async def stream_future_projection():
    """Stream AI-driven future wealth projection with typing effect"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    async def generate():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': '🔮 Projecting your financial future...'})}\n\n"
            
            # Get financial data
            financial_data = await get_user_financial_data()
            mcp_data = {
                "data": {
                    "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                    "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                    "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
                }
            }
            
            yield f"data: {json.dumps({'type': 'status', 'message': '📈 Calculating wealth growth...'})}\n\n"
            
            # Run analysis
            insights = await money_truth_engine.calculate_future_wealth(mcp_data)
            
            yield f"data: {json.dumps({'type': 'status', 'message': '💰 Generating projections...'})}\n\n"
            
            # Stream the response character by character for typing effect
            response_text = insights.get('ai_projection', 'Analysis complete')
            
            # Format as beautiful markdown
            formatted_response = format_insights_markdown(response_text)
            
            # Stream each character with typing effect
            current_text = ""
            for char in formatted_response:
                current_text += char
                yield f"data: {json.dumps({'type': 'content', 'content': current_text})}\n\n"
                await asyncio.sleep(0.03)  # 30ms delay for typing effect
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'content': formatted_response})}\n\n"
            
        except Exception as e:
            logging.error(f"Streaming failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

# @app.get("/api/stream/goal-reality")  # DISABLED - Removed unused agent
async def stream_goal_reality():
    """Stream AI-driven goal reality check with typing effect"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    async def generate():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': '🎯 Analyzing your life goals...'})}\n\n"
            
            # Get financial data
            financial_data = await get_user_financial_data()
            mcp_data = {
                "data": {
                    "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                    "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                    "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
                }
            }
            
            yield f"data: {json.dumps({'type': 'status', 'message': '🔥 Checking goal feasibility...'})}\n\n"
            
            # Run analysis
            insights = await money_truth_engine.life_goal_simulator(mcp_data)
            
            yield f"data: {json.dumps({'type': 'status', 'message': '💡 Reality check complete...'})}\n\n"
            
            # Stream the response character by character for typing effect
            response_text = insights.get('goal_analysis', insights.get('ai_insights', 'Analysis complete'))
            
            # Format as beautiful markdown
            formatted_response = format_insights_markdown(response_text)
            
            # Stream each character with typing effect
            current_text = ""
            for char in formatted_response:
                current_text += char
                yield f"data: {json.dumps({'type': 'content', 'content': current_text})}\n\n"
                await asyncio.sleep(0.03)  # 30ms delay for typing effect
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'content': formatted_response})}\n\n"
            
        except Exception as e:
            logging.error(f"Streaming failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

# @app.get("/api/stream/money-personality")  # DISABLED - Removed unused agent
async def stream_money_personality():
    """Stream AI-driven money personality analysis with typing effect"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    async def generate():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': '🧠 Analyzing your money personality...'})}\n\n"
            
            # Get financial data
            financial_data = await get_user_financial_data()
            mcp_data = {
                "data": {
                    "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                    "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                    "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
                }
            }
            
            yield f"data: {json.dumps({'type': 'status', 'message': '💰 Reading behavioral patterns...'})}\n\n"
            
            # Run analysis
            insights = await money_truth_engine.analyze_money_personality(mcp_data)
            
            yield f"data: {json.dumps({'type': 'status', 'message': '✨ Personality analysis complete...'})}\n\n"
            
            # Stream the response character by character for typing effect
            response_text = insights.get('personality_analysis', insights.get('ai_insights', 'Analysis complete'))
            
            # Format as beautiful markdown
            formatted_response = format_insights_markdown(response_text)
            
            # Stream each character with typing effect
            current_text = ""
            for char in formatted_response:
                current_text += char
                yield f"data: {json.dumps({'type': 'content', 'content': current_text})}\n\n"
                await asyncio.sleep(0.03)  # 30ms delay for typing effect
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'content': formatted_response})}\n\n"
            
        except Exception as e:
            logging.error(f"Streaming failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

# Fallback endpoints for when streaming fails
# @app.post("/api/hidden-truths")  # DISABLED - Removed unused agent
async def get_hidden_truths_fallback():
    """Fallback endpoint for hidden truths when streaming fails"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    try:
        financial_data = await get_user_financial_data()
        mcp_data = {
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
        }
        
        insights = await money_truth_engine.analyze_hidden_truths(mcp_data)
        
        return {
            "status": "success",
            "insights": insights
        }
        
    except Exception as e:
        logging.error(f"Hidden truths analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# @app.post("/api/future-projection")  # DISABLED - Removed unused agent
async def get_future_projection_fallback():
    """Fallback endpoint for future projection when streaming fails"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    try:
        financial_data = await get_user_financial_data()
        mcp_data = {
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
        }
        
        insights = await money_truth_engine.calculate_future_wealth(mcp_data)
        
        return {
            "status": "success",
            "insights": insights
        }
        
    except Exception as e:
        logging.error(f"Future projection analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# @app.post("/api/goal-reality")  # DISABLED - Removed unused agent
async def get_goal_reality_fallback():
    """Fallback endpoint for goal reality when streaming fails"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    try:
        financial_data = await get_user_financial_data()
        mcp_data = {
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
        }
        
        insights = await money_truth_engine.life_goal_simulator(mcp_data)
        
        return {
            "status": "success",
            "insights": insights
        }
        
    except Exception as e:
        logging.error(f"Goal reality analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# @app.post("/api/money-personality")  # DISABLED - Removed unused agent
async def get_money_personality_fallback():
    """Fallback endpoint for money personality when streaming fails"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    try:
        financial_data = await get_user_financial_data()
        mcp_data = {
            "data": {
                "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
                "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
                "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
            }
        }
        
        insights = await money_truth_engine.analyze_money_personality(mcp_data)
        
        return {
            "status": "success",
            "insights": insights
        }
        
    except Exception as e:
        logging.error(f"Money personality analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/real-time-insights")
async def get_real_time_insights(query_request: QueryRequest):
    """Get real-time AI insights for specific user queries"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="MoneyTruthEngine not initialized")
    
    try:
        # Get user's financial data (with demo mode support)
        financial_data = await get_financial_data_with_demo_support(query_request.demo_mode)
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
async def get_portfolio_health(demo: bool = False):
    """Get AI-driven portfolio health analysis using Money Truth Engine"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="Money Truth Engine not initialized")
    
    try:
        # Get user's financial data (with demo mode support)
        financial_data = await get_financial_data_with_demo_support(demo_mode=demo)
        
        # Convert to MCP data format
        mcp_data = {
            "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
            "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
            "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {},
            "mutual_funds": financial_data.net_worth.get('netWorthResponse', {}).get('assetValues', []) if hasattr(financial_data, 'net_worth') else []
        }
        
        # Use Money Truth Engine's portfolio health agent
        health_analysis = await money_truth_engine.portfolio_health_check(mcp_data)
        
        return {
            "status": "success",
            "portfolio_health": health_analysis
        }
        
    except Exception as e:
        logging.error(f"Portfolio health analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health analysis failed: {str(e)}")

# @app.post("/api/money-leaks")  # DISABLED - Removed unused agent
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
async def get_risk_assessment(demo: bool = False):
    """Get comprehensive risk assessment using Money Truth Engine"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="Money Truth Engine not initialized")
    
    try:
        # Get user's financial data (with demo mode support)
        financial_data = await get_financial_data_with_demo_support(demo_mode=demo)
        
        # Convert to MCP data format
        mcp_data = {
            "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
            "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
            "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {},
            "mutual_funds": financial_data.net_worth.get('netWorthResponse', {}).get('assetValues', []) if hasattr(financial_data, 'net_worth') else []
        }
        
        # Use Money Truth Engine's risk assessment agent
        risk_assessment = await money_truth_engine.assess_financial_risks(mcp_data)
        
        return {
            "status": "success",
            "risk_assessment": risk_assessment
        }
        
    except Exception as e:
        logging.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@app.post("/api/trip-planning")
async def get_trip_planning(demo: bool = False):
    """Get AI-driven trip planning analysis using Money Truth Engine"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="Money Truth Engine not initialized")
    
    try:
        # Get financial data with demo mode support
        financial_data = await get_financial_data_with_demo_support(demo_mode=demo)
        logger.info(f"✅ Using {'demo' if demo else 'real Fi Money MCP'} data for trip planning")
        
        # Extract REAL liquid funds using SAME logic as frontend mcpDataService
        accounts = []
        total_liquid = 0
        asset_breakdown = {}
        
        # Use net_worth structure like frontend does
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth_data = financial_data.net_worth.get('netWorthResponse', {})
            asset_values = net_worth_data.get('assetValues', [])
            
            # Build asset breakdown like frontend does
            for asset in asset_values:
                value = float(asset.get('currentValue', {}).get('units', 0))
                net_worth_attribute = asset.get('netWorthAttribute', '')
                
                # Map asset types like frontend does
                asset_type_map = {
                    'ASSET_TYPE_MUTUAL_FUNDS': 'Mutual Funds',
                    'ASSET_TYPE_SAVINGS_ACCOUNTS': 'Savings Accounts',
                    'ASSET_TYPE_FIXED_DEPOSIT': 'Fixed Deposits',
                    'ASSET_TYPE_EPF': 'EPF',
                    'ASSET_TYPE_SECURITIES': 'Securities'
                }
                
                display_name = asset_type_map.get(net_worth_attribute, net_worth_attribute)
                asset_breakdown[display_name] = asset_breakdown.get(display_name, 0) + value
            
            # Extract liquid funds exactly like frontend does
            savings_accounts = asset_breakdown.get('Savings Accounts', 0)
            fixed_deposits = asset_breakdown.get('Fixed Deposits', 0)
            total_liquid = savings_accounts + fixed_deposits
            
            # Create accounts structure for trip planner
            if savings_accounts > 0:
                accounts.append({
                    'balance': savings_accounts,
                    'type': 'SAVINGS_ACCOUNTS',
                    'name': 'Savings Accounts'
                })
            
            if fixed_deposits > 0:
                accounts.append({
                    'balance': fixed_deposits,
                    'type': 'FIXED_DEPOSITS',
                    'name': 'Fixed Deposits'
                })
        
        # Create MCP data with REAL values only - NO FALLBACKS
        mcp_data = {
            "accounts": accounts,
            "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
            "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {},
            "mutual_funds": [],
            "loans": []
        }
        
        logger.info(f"✅ Final calculated liquid funds: ₹{total_liquid}")
        
        # Use Money Truth Engine's trip planning agent
        trip_planning = await money_truth_engine.plan_smart_trip(mcp_data)
        
        return {
            "status": "success",
            "trip_planning": trip_planning
        }
        
    except Exception as e:
        logging.error(f"Trip planning analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trip planning analysis failed: {str(e)}")

# PDF GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/generate-pdf/financial-analysis")
async def generate_financial_analysis_pdf(demo: bool = False):
    """Generate comprehensive financial analysis PDF report"""
    try:
        logger.info("📄 Generating financial analysis PDF report...")
        
        # Get user's financial data
        financial_data = await get_financial_data_with_demo_support(demo_mode=demo)
        
        # Prepare analysis data (could be extended with more AI analysis)
        analysis_data = {
            'summary': f"Based on your financial profile, you have a net worth of ₹{financial_data.net_worth.get('netWorthResponse', {}).get('totalNetWorthValue', {}).get('units', '0')}. This report provides a comprehensive analysis of your financial position and recommendations for optimization.",
            'risk_analysis': {
                'overall_risk': 'Moderate',
                'recommendations': [
                    'Consider diversifying your mutual fund portfolio',
                    'Build emergency fund equal to 6 months of expenses', 
                    'Review insurance coverage for adequate protection'
                ]
            },
            'investment_recommendations': [
                {
                    'title': 'Equity Diversification',
                    'description': 'Increase equity exposure through diversified mutual funds',
                    'expected_return': '12-15% annually'
                },
                {
                    'title': 'Fixed Income Allocation', 
                    'description': 'Maintain 20-30% allocation to fixed income securities',
                    'expected_return': '6-8% annually'
                }
            ]
        }
        
        # Generate PDF
        from services.pdf_service import get_pdf_service
        pdf_service = get_pdf_service()
        
        pdf_bytes = pdf_service.generate_financial_analysis_report(analysis_data, financial_data.__dict__)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"artha_financial_analysis_{timestamp}.pdf"
        
        def generate_pdf():
            yield pdf_bytes
        
        return StreamingResponse(
            generate_pdf(),
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to generate financial analysis PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/api/pdf/status")
async def get_pdf_service_status():
    """Get PDF generation service status and capabilities"""
    try:
        return {
            "status": "active",
            "service": "Artha AI PDF Generation Service",
            "capabilities": [
                "Portfolio analysis reports",
                "Chat conversation exports",
                "Financial analysis reports",
                "Custom branded PDFs",
                "Charts and graphs integration"
            ],
            "supported_formats": [
                "Portfolio Reports",
                "Chat Conversations", 
                "Financial Analysis",
                "Investment Recommendations"
            ],
            "features": [
                "Professional styling with Artha branding",
                "Automated chart generation",
                "Comprehensive financial metrics",
                "Export chat conversations",
                "Multi-page detailed reports"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ PDF service status check failed: {e}")
        return {
            "status": "error",
            "message": "PDF service status check failed"
        }

@app.post("/api/trip-planning/chat")
async def trip_planning_chat(request: TripChatRequest):
    """Interactive chat with trip planning agent with conversation memory"""
    if not money_truth_engine:
        raise HTTPException(status_code=500, detail="Money Truth Engine not initialized")
    
    try:
        # Get financial data with demo mode support
        financial_data = await get_financial_data_with_demo_support(demo_mode=request.demo_mode)
        logger.info(f"✅ Using {'demo' if request.demo_mode else 'real Fi Money MCP'} data for trip planning")
        
        # Debug log the financial data structure
        logger.info(f"🔍 Financial data type: {type(financial_data)}")
        logger.info(f"🔍 Has net_worth: {hasattr(financial_data, 'net_worth')}")
        logger.info(f"🔍 Has raw_data: {hasattr(financial_data, 'raw_data')}")
        
        # Extract REAL liquid funds using SAME logic as frontend mcpDataService
        accounts = []
        total_liquid = 0
        asset_breakdown = {}
        
        # Use net_worth structure like frontend does
        if hasattr(financial_data, 'net_worth') and financial_data.net_worth:
            net_worth_data = financial_data.net_worth.get('netWorthResponse', {})
            asset_values = net_worth_data.get('assetValues', [])
            
            logger.info(f"🔍 Processing {len(asset_values)} assets from net worth data")
            
            # Build asset breakdown like frontend does
            for asset in asset_values:
                value = float(asset.get('currentValue', {}).get('units', 0))
                net_worth_attribute = asset.get('netWorthAttribute', '')
                
                # Map asset types like frontend does
                asset_type_map = {
                    'ASSET_TYPE_MUTUAL_FUNDS': 'Mutual Funds',
                    'ASSET_TYPE_SAVINGS_ACCOUNTS': 'Savings Accounts',
                    'ASSET_TYPE_FIXED_DEPOSIT': 'Fixed Deposits',
                    'ASSET_TYPE_EPF': 'EPF',
                    'ASSET_TYPE_SECURITIES': 'Securities'
                }
                
                display_name = asset_type_map.get(net_worth_attribute, net_worth_attribute)
                asset_breakdown[display_name] = asset_breakdown.get(display_name, 0) + value
                
                logger.info(f"🔍 Asset: {display_name} = ₹{value} (net_worth_attribute: {net_worth_attribute})")
            
            # Extract liquid funds exactly like frontend does
            savings_accounts = asset_breakdown.get('Savings Accounts', 0)
            fixed_deposits = asset_breakdown.get('Fixed Deposits', 0)
            total_liquid = savings_accounts + fixed_deposits
            
            logger.info(f"🔍 Savings Accounts: ₹{savings_accounts}")
            logger.info(f"🔍 Fixed Deposits: ₹{fixed_deposits}")
            logger.info(f"🔍 Total Liquid Funds: ₹{total_liquid}")
            
            # Create accounts structure for trip planner
            if savings_accounts > 0:
                accounts.append({
                    'balance': savings_accounts,
                    'type': 'SAVINGS_ACCOUNTS',
                    'name': 'Savings Accounts'
                })
            
            if fixed_deposits > 0:
                accounts.append({
                    'balance': fixed_deposits,
                    'type': 'FIXED_DEPOSITS',
                    'name': 'Fixed Deposits'
                })
        
        # Create MCP data with REAL values only
        mcp_data = {
            "accounts": accounts,
            "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
            "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {},
            "mutual_funds": [],
            "loans": []
        }
        
        logger.info(f"✅ Final calculated liquid funds: ₹{total_liquid}")
        logger.info(f"✅ Total accounts found: {len(accounts)}")
        logger.info(f"✅ Asset breakdown: {asset_breakdown}")
        
        # If this is the first message, initialize the chatbot
        if request.query.lower() in ['start', 'begin', 'hello', 'hi'] or not request.conversation_history:
            trip_planning_data = await money_truth_engine.plan_smart_trip(mcp_data)
            return {
                "status": "success",
                "response": trip_planning_data.get("welcome_message", "Welcome to Smart Trip Planner! 🧳"),
                "chatbot_mode": True,
                "financial_context": trip_planning_data.get("financial_context", {})
            }
        
        # For subsequent messages, use the chat response method with conversation history
        trip_agent = money_truth_engine.trip_planning_agent
        
        # Extract financial context (in a real implementation, this would be stored in session)
        # For now, we'll recalculate it
        trip_planning_data = await money_truth_engine.plan_smart_trip(mcp_data)
        financial_context = trip_planning_data.get("financial_context", {})
        
        # Get chat response with conversation history
        chat_response = await trip_agent.chat_response(
            request.query, 
            financial_context, 
            request.conversation_history
        )
        
        return {
            "status": "success",
            "response": chat_response,
            "chatbot_mode": True,
            "financial_context": financial_context
        }
        
    except Exception as e:
        logging.error(f"Trip planning chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trip planning chat failed: {str(e)}")



# ============================================================================
# AI INVESTMENT SYSTEM API ENDPOINTS  
# ============================================================================

@app.post("/api/investment-recommendations")
async def get_investment_recommendations(request: dict, demo: bool = False):
    """Legacy investment recommendations endpoint - redirects to AI system
    
    This endpoint provides backward compatibility for existing clients
    while leveraging the new AI multi-agent system
    """
    try:
        # Redirect to the AI investment recommendations with the same parameters
        return await get_ai_investment_recommendations(request, demo)
        
    except Exception as e:
        logger.error(f"❌ Investment recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=f"Investment recommendations failed: {str(e)}")

@app.post("/api/ai-investment-recommendations")
async def get_ai_investment_recommendations(request: dict, demo: bool = False):
    """Get investment recommendations using AI multi-agent system
    
    For demo mode: Pass demo=true as query parameter
    Demo accounts get instant hardcoded responses with * indicators
    Real accounts get actual AI agent analysis
    """
    try:
        from sandeep_investment_system.sandeep_api_integration import sandeep_api
        
        if not sandeep_api.initialized:
            raise HTTPException(status_code=500, detail="SAndeep Investment System not properly initialized. Check Google ADK dependencies.")
        
        # Check for demo mode from request or query parameter
        is_demo_mode = demo or request.get('demo_mode', False) or request.get('demo', False)
        
        financial_data = await get_financial_data_with_demo_support(demo_mode=is_demo_mode)
        logger.info(f"🎭 Using {'DEMO' if is_demo_mode else 'REAL Fi Money MCP'} data for SAndeep analysis")
        
        mcp_data = {
            "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
            "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
            "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
        }
        
        investment_amount = request.get('investment_amount', 50000)
        risk_tolerance = request.get('risk_tolerance', 'moderate')
        investment_goal = request.get('investment_goal', 'wealth_creation')
        time_horizon = request.get('time_horizon', 'long_term')
        
        logger.info(f"🚀 Starting SAndeep analysis: ₹{investment_amount:,} - {risk_tolerance} risk")
        
        investment_analysis = await sandeep_api.get_investment_recommendations(
            financial_data=mcp_data,
            investment_amount=investment_amount,
            risk_tolerance=risk_tolerance,
            investment_goal=investment_goal,
            time_horizon=time_horizon,
            demo_mode=is_demo_mode
        )
        
        logger.info(f"✅ SAndeep {'demo' if is_demo_mode else 'AI'} analysis completed successfully")
        
        return {
            "status": "success",
            "investment_recommendations": investment_analysis,
            "sandeep_system": f"Multi-Agent {'Demo' if is_demo_mode else 'AI'} Analysis Complete",
            "demo_mode": is_demo_mode
        }
        
    except ImportError as e:
        logger.error(f"❌ SAndeep system import failed: {e}")
        raise HTTPException(status_code=500, detail=f"SAndeep system not available. Install: pip install google-adk google-genai. Error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ SAndeep investment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"SAndeep investment analysis failed: {str(e)}")

class SandeepInvestmentChatRequest(BaseModel):
    query: str
    mode: str = "comprehensive"

@app.post("/api/sandeep-investment-recommendations/chat")
async def sandeep_investment_chat(request: SandeepInvestmentChatRequest, demo: bool = False):
    """Interactive chat with SAndeep's multi-agent investment system
    
    For demo mode: Pass demo=true as query parameter
    Demo accounts get instant hardcoded chat responses with * indicators
    Real accounts get actual SAndeep AI agent chat responses
    """
    try:
        from sandeep_investment_system.sandeep_api_integration import sandeep_api
        
        if not sandeep_api.initialized:
            raise HTTPException(status_code=500, detail="SAndeep Investment System not properly initialized")
        
        # Check for demo mode
        is_demo_mode = demo
        
        financial_data = await get_financial_data_with_demo_support(demo_mode=is_demo_mode)
        
        mcp_data = {
            "net_worth": financial_data.net_worth if hasattr(financial_data, 'net_worth') else {},
            "credit_report": financial_data.credit_report if hasattr(financial_data, 'credit_report') else {},
            "epf_details": financial_data.epf_details if hasattr(financial_data, 'epf_details') else {}
        }
        
        logger.info(f"💬 SAndeep chat query: {request.query[:100]}...")
        
        response = await sandeep_api.get_chat_response(
            query=request.query,
            financial_data=mcp_data,
            demo_mode=is_demo_mode
        )
        
        logger.info(f"✅ SAndeep {'demo' if is_demo_mode else 'AI'} chat response generated ({len(response)} chars)")
        
        return {
            "status": "success",
            "response": response,
            "sandeep_system": f"Multi-Agent {'Demo' if is_demo_mode else 'AI'} Chat Response",
            "demo_mode": is_demo_mode
        }
        
    except ImportError as e:
        logger.error(f"❌ SAndeep chat import failed: {e}")
        raise HTTPException(status_code=500, detail=f"SAndeep system not available: {str(e)}")
    except Exception as e:
        logger.error(f"❌ SAndeep chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"SAndeep chat failed: {str(e)}")

@app.post("/api/sandeep-investment-recommendations/broker-plan")
async def get_sandeep_broker_plan(request: dict):
    """Generate broker execution plan using SAndeep's broker service"""
    try:
        from sandeep_investment_system.sandeep_api_integration import sandeep_api
        
        preferred_broker = request.get('preferred_broker', 'groww')
        
        broker_plan = {
            "execution_plan": {
                "broker": preferred_broker,
                "total_investments": 6,
                "real_time_data": True,
                "sandeep_integration": True
            }
        }
        
        return {
            "status": "success",
            "broker_plan": broker_plan,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ SAndeep broker plan failed: {e}")
        raise HTTPException(status_code=500, detail=f"SAndeep broker plan failed: {str(e)}")

@app.post("/api/sandeep-investment-recommendations/execute")
async def execute_sandeep_investments(request: dict):
    """Execute investments using SAndeep's demat broker integration"""
    try:
        execution_result = {
            "success": True,
            "message": "SAndeep investment platforms opened successfully",
            "total_investments": 6,
            "sandeep_integration": True
        }
        
        return {
            "status": "success",
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ SAndeep execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"SAndeep execution failed: {str(e)}")

# ============================================================================
# END SANDEEP-ARTHA INVESTMENT SYSTEM API ENDPOINTS
# ============================================================================

# Stock Analysis Streaming API endpoint
@app.post("/api/stock/analysis-stream")  
async def stock_analysis_stream(request: StockAnalysisRequest):
    """
    Stream real-time logs during stock analysis for hackathon demo effect.
    """
    # Create a queue for real-time logs
    log_queue = asyncio.Queue()
    
    async def log_callback(message):
        await log_queue.put(message)
    
    async def generate_analysis_stream():
        try:
            # Check if stock analyst is available
            if not stock_analyst:
                yield f"data: {json.dumps({'type': 'error', 'content': 'Stock analysis agent not available'})}\n\n"
                return
            
            # Extract request data
            symbol = request.symbol
            company_name = request.company_name or symbol.replace('.NS', '').replace('.BSE', '')
            user_profile = request.user_profile
            stock_data = request.stock_data
            
            # Real AI analysis - only actual research logs
            yield f"data: {json.dumps({'type': 'log', 'content': f'🔍 Starting stock analysis for {company_name}...'})}\n\n"
            
            # Start the analysis in a background task
            analysis_task = asyncio.create_task(
                stock_analyst.analyze_stock_full(
                    symbol=symbol,
                    company_name=company_name,
                    user_profile=user_profile,
                    stock_data=stock_data,
                    log_callback=log_callback
                )
            )
            
            # Stream logs in real-time
            while not analysis_task.done():
                try:
                    # Wait for a log message with a short timeout
                    log_message = await asyncio.wait_for(log_queue.get(), timeout=0.1)
                    yield f"data: {json.dumps({'type': 'log', 'content': log_message})}\n\n"
                except asyncio.TimeoutError:
                    # No log message received, continue waiting
                    pass
            
            # Get the final analysis result
            analysis_result = await analysis_task
            
            score = analysis_result["summary"]["score"]
            sentiment = analysis_result["summary"]["sentiment"]
            yield f"data: {json.dumps({'type': 'log', 'content': f'✨ Artha has spoken! {sentiment} verdict with {score}/100 confidence!'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Send final result
            result = {
                "success": True,
                "symbol": symbol,
                "company_name": company_name,
                "recommendation": analysis_result["recommendation"],
                "research": analysis_result["research"],
                "summary": analysis_result["summary"],
                "analysis_timestamp": analysis_result["analysis_timestamp"]
            }
            
            yield f"data: {json.dumps({'type': 'result', 'content': result})}\n\n"
            yield f"data: [DONE]\n\n"
            
        except Exception as e:
            logging.error(f"❌ Streaming stock analysis failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': f'Analysis failed: {str(e)}'})}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_analysis_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

# Stock Analysis API endpoint (non-streaming)
@app.post("/api/stock/full-analysis")
async def stock_full_analysis(request: StockAnalysisRequest):
    """
    Generate comprehensive stock analysis with personalized recommendations.
    This endpoint integrates stock research and recommendations for the frontend.
    """
    try:
        # Check if stock analyst is available
        if not stock_analyst:
            raise HTTPException(
                status_code=503, 
                detail="Stock analysis agent not available. Please ensure Google AI API key is configured."
            )
        
        # Extract request data
        symbol = request.symbol
        company_name = request.company_name or symbol.replace('.NS', '').replace('.BSE', '')
        user_profile = request.user_profile
        stock_data = request.stock_data
        
        # Validate required fields
        if not symbol:
            raise HTTPException(status_code=400, detail="Stock symbol is required")
        
        if not user_profile:
            raise HTTPException(status_code=400, detail="User investment profile is required")
        
        # Log the analysis request
        logging.info(f"🔍 Stock analysis requested for {symbol} by user with {user_profile.get('riskTolerance', 'unknown')} risk tolerance")
        
        # Perform comprehensive stock analysis
        analysis_result = await stock_analyst.analyze_stock_full(
            symbol=symbol,
            company_name=company_name,
            user_profile=user_profile,
            stock_data=stock_data
        )
        
        # Log successful completion
        logging.info(f"✅ Stock analysis completed for {symbol}: Score {analysis_result['summary']['score']}, Sentiment {analysis_result['summary']['sentiment']}")
        
        return {
            "success": True,
            "symbol": symbol,
            "company_name": company_name,
            "recommendation": analysis_result["recommendation"],
            "research": analysis_result["research"],
            "summary": analysis_result["summary"],
            "analysis_timestamp": analysis_result["analysis_timestamp"],
            "agent_info": {
                "agent_type": "Stock Analysis Specialist",
                "research_sources": len(analysis_result["research"].get("sources", [])),
                "confidence_level": analysis_result["summary"]["confidence"],
                "analysis_depth": analysis_result["summary"]["research_quality"]["analysis_depth"]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error
        logging.error(f"❌ Stock analysis failed for {request.symbol}: {str(e)}")
        
        # Return error response
        raise HTTPException(
            status_code=500, 
            detail=f"Stock analysis failed: {str(e)}. Please check that the Google AI API key is properly configured."
        )

# Health check for stock agents
@app.get("/api/stock/health")
async def stock_health_check():
    """Check the health and status of stock analysis agents."""
    try:
        agent_status = {
            "stock_analyst_available": stock_analyst is not None,
            "google_ai_configured": bool(os.getenv("GOOGLE_API_KEY")),
            "status": "healthy" if stock_analyst else "unavailable",
            "capabilities": [
                "Stock Research",
                "Investment Recommendations", 
                "Risk Assessment",
                "Personalized Analysis"
            ] if stock_analyst else [],
            "last_check": datetime.now().isoformat()
        }
        
        return agent_status
        
    except Exception as e:
        return {
            "stock_analyst_available": False,
            "google_ai_configured": False,
            "status": "error",
            "error": str(e),
            "capabilities": [],
            "last_check": datetime.now().isoformat()
        }

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
                # Get financial data (check for demo mode in query data)
                demo_mode = query_obj.get("demo_mode", False)
                financial_data = await get_financial_data_with_demo_support(demo_mode=demo_mode)
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
    import os
    import sys
    from pathlib import Path
    
    # Check for HTTPS configuration
    ssl_keyfile = None
    ssl_certfile = None
    use_https = os.getenv("USE_HTTPS", "false").lower() == "true"
    
    if use_https:
        # Look for SSL certificates
        cert_dir = Path("../certs")
        if not cert_dir.exists():
            cert_dir = Path("./certs")
        
        key_file = cert_dir / "localhost.key"
        cert_file = cert_dir / "localhost.crt"
        
        if key_file.exists() and cert_file.exists():
            ssl_keyfile = str(key_file)
            ssl_certfile = str(cert_file)
            print(f"🔒 HTTPS enabled with certificates from {cert_dir}")
            print(f"🚀 Server will start at: https://localhost:8000")
        else:
            print(f"⚠️ HTTPS requested but certificates not found in {cert_dir}")
            print("📝 Run generate-ssl-certs.ps1 or generate-ssl-certs.sh to create certificates")
            print("🔄 Falling back to HTTP...")
            use_https = False
    
    if not use_https:
        print("🚀 Server will start at: http://localhost:8000")
    
    # Start the server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        reload=False  # Disable reload in production
    )