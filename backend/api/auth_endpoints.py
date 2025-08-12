"""
Authentication API Endpoints for Artha AI
========================================

Comprehensive user authentication REST API with JWT, security, and validation.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from services.auth_service import get_auth_service, AuthService

logger = logging.getLogger(__name__)

# Initialize auth service and security
auth_service = get_auth_service()
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Pydantic models for request/response
class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=12, max_length=128, description="User password (min 12 chars, must contain uppercase, lowercase, number, and special character)")
    full_name: str = Field(..., min_length=2, description="User full name")
    phone: Optional[str] = Field(None, description="Phone number (optional)")
    date_of_birth: Optional[str] = Field(None, description="Date of birth in YYYY-MM-DD format")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_verified: bool
    last_login: Optional[str]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    tokens: Optional[TokenResponse] = None
    session_id: Optional[str] = None

class ProfileResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None

# Dependency for authenticated routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required"
        )
    
    token = credentials.credentials
    verification_result = auth_service.verify_token(token)
    
    if not verification_result.get('valid'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=verification_result.get('message', 'Invalid authentication token')
        )
    
    return verification_result['user']

@router.post("/register", response_model=AuthResponse)
async def register_user(
    request: RegisterRequest,
    client_request: Request
):
    """
    Register a new user account with comprehensive validation
    """
    try:
        logger.info(f"📝 User registration attempt: {request.email}")
        
        # Get client info for security logging
        ip_address = client_request.client.host
        user_agent = client_request.headers.get("user-agent", "Unknown")
        
        # Register user
        result = auth_service.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone,
            date_of_birth=request.date_of_birth
        )
        
        if result['success']:
            # Log successful registration
            logger.info(f"✅ User registered successfully: {request.email} from {ip_address}")
            
            return AuthResponse(
                success=True,
                message=result['message'],
                user=UserResponse(**result['user']),
                tokens=TokenResponse(**result['tokens'])
            )
        else:
            # Log failed registration
            logger.warning(f"❌ Registration failed: {request.email} - {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    request: LoginRequest,
    client_request: Request
):
    """
    Authenticate user and return JWT tokens
    """
    try:
        logger.info(f"🔐 Login attempt: {request.email}")
        
        # Get client info for security
        ip_address = client_request.client.host
        user_agent = client_request.headers.get("user-agent", "Unknown")
        
        # Authenticate user
        result = auth_service.login_user(
            email=request.email,
            password=request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if result['success']:
            logger.info(f"✅ User logged in successfully: {request.email} from {ip_address}")
            
            return AuthResponse(
                success=True,
                message=result['message'],
                user=UserResponse(**result['user']),
                tokens=TokenResponse(**result['tokens']),
                session_id=result.get('session_id')
            )
        else:
            # Log failed login
            logger.warning(f"❌ Login failed: {request.email} - {result['message']} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/refresh")
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        logger.info("🔄 Token refresh attempt")
        
        result = auth_service.refresh_token(request.refresh_token)
        
        if result['success']:
            logger.info("✅ Token refreshed successfully")
            return {
                "success": True,
                "access_token": result['access_token'],
                "token_type": result['token_type'],
                "expires_in": result['expires_in']
            }
        else:
            logger.warning(f"❌ Token refresh failed: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user and invalidate session
    """
    try:
        logger.info("🚪 Logout attempt")
        
        token = credentials.credentials
        result = auth_service.logout_user(token)
        
        if result['success']:
            logger.info("✅ User logged out successfully")
            return {"success": True, "message": result['message']}
        else:
            logger.warning(f"❌ Logout failed: {result['message']}")
            return {"success": False, "message": result['message']}
            
    except Exception as e:
        logger.error(f"❌ Logout endpoint error: {e}")
        return {"success": False, "message": "Logout failed"}

@router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify JWT token and return user info
    """
    try:
        token = credentials.credentials
        result = auth_service.verify_token(token)
        
        if result['valid']:
            return {
                "valid": True,
                "user": result['user']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token verification endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )

@router.get("/profile", response_model=ProfileResponse)
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user's complete profile
    """
    try:
        logger.info(f"👤 Profile request for user: {current_user['id']}")
        
        result = auth_service.get_user_profile(current_user['id'])
        
        if result['success']:
            return ProfileResponse(
                success=True,
                profile=result['profile']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Profile endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current authenticated user basic info
    """
    try:
        return {
            "success": True,
            "user": current_user
        }
        
    except Exception as e:
        logger.error(f"❌ Current user endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current user info"
        )

@router.get("/status")
async def auth_status():
    """
    Get authentication service status
    """
    try:
        return {
            "status": "active",
            "service": "Artha AI Authentication Service",
            "features": [
                "JWT token authentication",
                "AES-256 data encryption",
                "Account lockout protection",
                "Session management",
                "Comprehensive audit logging"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Auth status endpoint error: {e}")
        return {
            "status": "error",
            "message": "Service status check failed"
        }