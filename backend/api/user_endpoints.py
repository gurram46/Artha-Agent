"""
User Profile Management API Endpoints for Artha AI
=================================================

Comprehensive user profile and preferences management REST API.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
import logging
from datetime import date, datetime
from decimal import Decimal

from services.user_service import get_user_service, UserService
from api.auth_endpoints import get_current_user

logger = logging.getLogger(__name__)

# Initialize services
user_service = get_user_service()
security = HTTPBearer()

# Create router
router = APIRouter(prefix="/api/user", tags=["user_profile"])

# Pydantic models for request/response
class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    occupation: Optional[str] = Field(None, description="Occupation/Job title")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income")
    company: Optional[str] = Field(None, description="Company name")
    experience_years: Optional[int] = Field(None, ge=0, le=50, description="Years of experience")
    address: Optional[str] = Field(None, description="Address")

class InvestmentPreferencesRequest(BaseModel):
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance: conservative, moderate, aggressive, very_aggressive")
    investment_horizon: Optional[str] = Field(None, description="Investment horizon: short_term, medium_term, long_term")
    investment_goals: Optional[List[str]] = Field(None, description="Investment goals")
    preferred_asset_classes: Optional[List[str]] = Field(None, description="Preferred asset classes")
    monthly_investment_amount: Optional[float] = Field(None, ge=0, description="Monthly investment amount")
    emergency_fund_months: Optional[int] = Field(None, ge=1, le=24, description="Emergency fund in months")
    debt_to_income_ratio: Optional[float] = Field(None, ge=0, le=100, description="Debt to income ratio (%)")
    current_investments: Optional[Dict[str, Any]] = Field(None, description="Current investments")
    financial_dependents: Optional[int] = Field(None, ge=0, description="Number of financial dependents")
    retirement_age: Optional[int] = Field(None, ge=45, le=80, description="Target retirement age")
    major_expenses: Optional[List[Dict[str, Any]]] = Field(None, description="Planned major expenses")
    insurance_coverage: Optional[Dict[str, Any]] = Field(None, description="Insurance coverage details")
    tax_bracket: Optional[str] = Field(None, description="Tax bracket")
    investment_experience: Optional[str] = Field(None, description="Investment experience: beginner, intermediate, experienced, expert")
    advisor_preference: Optional[str] = Field(None, description="Advisor preference: ai_guided, human_advisor, self_directed, hybrid")

class CreateGoalRequest(BaseModel):
    goal_name: str = Field(..., min_length=3, max_length=255, description="Goal name")
    goal_type: str = Field(..., description="Goal type: retirement, emergency_fund, home_purchase, education, etc.")
    target_amount: float = Field(..., gt=0, description="Target amount")
    current_amount: Optional[float] = Field(0, ge=0, description="Current amount saved")
    target_date: Optional[str] = Field(None, description="Target date (YYYY-MM-DD)")
    monthly_contribution: Optional[float] = Field(None, ge=0, description="Monthly contribution")
    priority_level: Optional[int] = Field(3, ge=1, le=5, description="Priority level (1-5)")
    description: Optional[str] = Field(None, description="Goal description")
    strategy: Optional[Dict[str, Any]] = Field(None, description="Investment strategy")

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.get("/profile")
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get complete user profile with decrypted sensitive data
    """
    try:
        logger.info(f"👤 Getting complete profile for user: {current_user['id']}")
        
        result = user_service.get_complete_profile(current_user['id'])
        
        if result['success']:
            return {
                "success": True,
                "profile": result['profile']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get profile endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/profile", response_model=StandardResponse)
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user profile with encrypted storage of sensitive data
    """
    try:
        logger.info(f"📝 Updating profile for user: {current_user['id']}")
        
        # Convert request to dict, excluding None values
        profile_data = {k: v for k, v in request.dict().items() if v is not None}
        
        result = user_service.update_user_profile(current_user['id'], profile_data)
        
        if result['success']:
            return StandardResponse(
                success=True,
                message=result['message']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update profile endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.put("/investment-preferences", response_model=StandardResponse)
async def update_investment_preferences(
    request: InvestmentPreferencesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user investment preferences and financial settings
    """
    try:
        logger.info(f"📊 Updating investment preferences for user: {current_user['id']}")
        
        # Convert request to dict, excluding None values
        preferences_data = {k: v for k, v in request.dict().items() if v is not None}
        
        # Validate enum values
        if 'risk_tolerance' in preferences_data:
            valid_risk = ['conservative', 'moderate', 'aggressive', 'very_aggressive']
            if preferences_data['risk_tolerance'] not in valid_risk:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid risk_tolerance. Must be one of: {valid_risk}"
                )
        
        if 'investment_horizon' in preferences_data:
            valid_horizon = ['short_term', 'medium_term', 'long_term']
            if preferences_data['investment_horizon'] not in valid_horizon:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid investment_horizon. Must be one of: {valid_horizon}"
                )
        
        if 'investment_experience' in preferences_data:
            valid_experience = ['beginner', 'intermediate', 'experienced', 'expert']
            if preferences_data['investment_experience'] not in valid_experience:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid investment_experience. Must be one of: {valid_experience}"
                )
        
        if 'advisor_preference' in preferences_data:
            valid_advisor = ['ai_guided', 'human_advisor', 'self_directed', 'hybrid']
            if preferences_data['advisor_preference'] not in valid_advisor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid advisor_preference. Must be one of: {valid_advisor}"
                )
        
        result = user_service.update_investment_preferences(current_user['id'], preferences_data)
        
        if result['success']:
            return StandardResponse(
                success=True,
                message=result['message']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update investment preferences endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update investment preferences"
        )

@router.post("/goals", response_model=StandardResponse)
async def create_financial_goal(
    request: CreateGoalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new financial goal for the user
    """
    try:
        logger.info(f"🎯 Creating goal for user: {current_user['id']} - {request.goal_name}")
        
        # Validate goal type
        valid_goal_types = [
            'retirement', 'emergency_fund', 'home_purchase', 'education', 'travel',
            'business', 'wedding', 'car_purchase', 'investment', 'debt_payoff', 'other'
        ]
        if request.goal_type not in valid_goal_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid goal_type. Must be one of: {valid_goal_types}"
            )
        
        # Convert request to dict
        goal_data = request.dict()
        
        result = user_service.create_user_goal(current_user['id'], goal_data)
        
        if result['success']:
            return StandardResponse(
                success=True,
                message=result['message'],
                data={"goal_id": result.get('goal_id')}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Create goal endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create financial goal"
        )

@router.get("/goals")
async def get_user_goals(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all financial goals for the user
    """
    try:
        logger.info(f"🎯 Getting goals for user: {current_user['id']}")
        
        result = user_service.get_user_goals(current_user['id'])
        
        if result['success']:
            return {
                "success": True,
                "goals": result['goals']
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get goals endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user goals"
        )

@router.get("/dashboard")
async def get_user_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user dashboard with profile summary and key metrics
    """
    try:
        logger.info(f"📊 Getting dashboard for user: {current_user['id']}")
        
        # Get complete profile
        profile_result = user_service.get_complete_profile(current_user['id'])
        if not profile_result['success']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Get goals
        goals_result = user_service.get_user_goals(current_user['id'])
        goals = goals_result.get('goals', []) if goals_result['success'] else []
        
        # Calculate dashboard metrics
        profile = profile_result['profile']
        investment_prefs = profile.get('investment_preferences', {})
        
        # Goals summary
        total_goals = len(goals)
        active_goals = len([g for g in goals if g['status'] == 'active'])
        completed_goals = len([g for g in goals if g['status'] == 'completed'])
        
        total_target_amount = sum(g.get('target_amount', 0) for g in goals)
        total_current_amount = sum(g.get('current_amount', 0) for g in goals)
        
        # Profile completion score
        profile_fields = [
            'full_name', 'phone', 'date_of_birth', 'occupation', 
            'annual_income', 'company', 'experience_years'
        ]
        completed_fields = sum(1 for field in profile_fields if profile.get(field))
        profile_completion = (completed_fields / len(profile_fields)) * 100
        
        # Investment preferences completion
        prefs_fields = [
            'risk_tolerance', 'investment_horizon', 'investment_goals',
            'emergency_fund_months', 'investment_experience'
        ]
        completed_prefs = sum(1 for field in prefs_fields if investment_prefs.get(field))
        prefs_completion = (completed_prefs / len(prefs_fields)) * 100 if investment_prefs else 0
        
        dashboard = {
            "user_info": {
                "id": profile['id'],
                "full_name": profile.get('full_name', 'User'),
                "email": profile['email'],
                "member_since": profile['created_at'],
                "last_login": profile.get('last_login')
            },
            "profile_completion": {
                "percentage": round(profile_completion, 1),
                "completed_fields": completed_fields,
                "total_fields": len(profile_fields)
            },
            "investment_readiness": {
                "percentage": round(prefs_completion, 1),
                "risk_tolerance": investment_prefs.get('risk_tolerance', 'Not set'),
                "investment_experience": investment_prefs.get('investment_experience', 'Not set'),
                "monthly_investment": investment_prefs.get('monthly_investment_amount', 0)
            },
            "goals_summary": {
                "total_goals": total_goals,
                "active_goals": active_goals,
                "completed_goals": completed_goals,
                "total_target_amount": total_target_amount,
                "total_saved": total_current_amount,
                "progress_percentage": round((total_current_amount / total_target_amount * 100) if total_target_amount > 0 else 0, 1)
            },
            "next_steps": []
        }
        
        # Generate next steps recommendations
        if profile_completion < 80:
            dashboard["next_steps"].append({
                "priority": "high",
                "action": "complete_profile",
                "title": "Complete Your Profile",
                "description": "Add missing information to get personalized recommendations"
            })
        
        if prefs_completion < 60:
            dashboard["next_steps"].append({
                "priority": "high",
                "action": "set_preferences",
                "title": "Set Investment Preferences",
                "description": "Define your risk tolerance and investment goals"
            })
        
        if total_goals == 0:
            dashboard["next_steps"].append({
                "priority": "medium",
                "action": "create_goals",
                "title": "Create Financial Goals",
                "description": "Set specific targets for your financial future"
            })
        
        if not investment_prefs.get('emergency_fund_months'):
            dashboard["next_steps"].append({
                "priority": "medium",
                "action": "set_emergency_fund",
                "title": "Plan Emergency Fund",
                "description": "Determine your emergency fund target"
            })
        
        return {
            "success": True,
            "dashboard": dashboard
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get dashboard endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user dashboard"
        )

@router.get("/settings")
async def get_user_settings(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user settings and preferences for app configuration
    """
    try:
        logger.info(f"⚙️ Getting settings for user: {current_user['id']}")
        
        # Get profile to extract settings
        profile_result = user_service.get_complete_profile(current_user['id'])
        if not profile_result['success']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        profile = profile_result['profile']
        investment_prefs = profile.get('investment_preferences', {})
        
        settings = {
            "account": {
                "email": profile['email'],
                "is_verified": profile['is_verified'],
                "created_at": profile['created_at']
            },
            "notifications": {
                "portfolio_updates": True,
                "goal_progress": True,
                "market_alerts": True,
                "weekly_summary": True
            },
            "privacy": {
                "data_sharing": False,
                "analytics_tracking": True,
                "marketing_emails": False
            },
            "investment": {
                "risk_tolerance": investment_prefs.get('risk_tolerance', 'moderate'),
                "advisor_preference": investment_prefs.get('advisor_preference', 'ai_guided'),
                "auto_rebalancing": False,
                "tax_optimization": True
            },
            "display": {
                "currency": "INR",
                "date_format": "DD/MM/YYYY",
                "theme": "light",
                "language": "en"
            }
        }
        
        return {
            "success": True,
            "settings": settings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get settings endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user settings"
        )