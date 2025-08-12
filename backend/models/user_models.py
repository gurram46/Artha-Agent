"""
User data models and storage for Artha AI
"""

from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

class PersonalInfo(BaseModel):
    fullName: str
    email: EmailStr
    phoneNumber: str
    dateOfBirth: str
    occupation: str

class ProfessionalInfo(BaseModel):
    occupation: str
    annualIncome: str
    workExperience: Optional[str] = None
    industry: Optional[str] = None

class InvestmentPreferences(BaseModel):
    riskTolerance: str
    investmentGoals: List[str]
    investmentHorizon: Optional[str] = None
    preferredAssets: Optional[List[str]] = None

class UserProfile(BaseModel):
    user_id: str
    personalInfo: PersonalInfo
    professionalInfo: ProfessionalInfo
    investmentPreferences: InvestmentPreferences
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class UserDataStorage:
    """Simple file-based storage for user data"""
    
    def __init__(self, storage_dir: str = "user_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_user_file_path(self, user_id: str) -> Path:
        """Get the file path for a user's data"""
        return self.storage_dir / f"{user_id}.json"
    
    def save_user_data(self, user_profile: UserProfile) -> bool:
        """Save user profile data to file"""
        try:
            user_file = self._get_user_file_path(user_profile.user_id)
            user_profile.updated_at = datetime.now()
            
            with open(user_file, 'w') as f:
                json.dump(user_profile.dict(), f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    def load_user_data(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile data from file"""
        try:
            user_file = self._get_user_file_path(user_id)
            
            if not user_file.exists():
                return None
            
            with open(user_file, 'r') as f:
                data = json.load(f)
            
            return UserProfile(**data)
        except Exception as e:
            print(f"Error loading user data: {e}")
            return None
    
    def update_user_data(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields in user profile"""
        try:
            user_profile = self.load_user_data(user_id)
            if not user_profile:
                return False
            
            # Update the profile with new data
            profile_dict = user_profile.dict()
            for key, value in updates.items():
                if key in profile_dict:
                    profile_dict[key] = value
            
            updated_profile = UserProfile(**profile_dict)
            return self.save_user_data(updated_profile)
        except Exception as e:
            print(f"Error updating user data: {e}")
            return False
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete user profile data"""
        try:
            user_file = self._get_user_file_path(user_id)
            if user_file.exists():
                user_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    def list_all_users(self) -> List[str]:
        """List all user IDs"""
        try:
            return [f.stem for f in self.storage_dir.glob("*.json")]
        except Exception as e:
            print(f"Error listing users: {e}")
            return []

# Global storage instance
user_storage = UserDataStorage()

def create_user_id_from_email(email: str) -> str:
    """Create a user ID from email address"""
    import hashlib
    return hashlib.md5(email.encode()).hexdigest()[:12]

def save_user_profile(user_data: Dict[str, Any]) -> str:
    """Save user profile and return user ID"""
    try:
        # Extract email to create user ID
        email = user_data.get('personalInfo', {}).get('email', '')
        if not email:
            raise ValueError("Email is required to create user profile")
        
        user_id = create_user_id_from_email(email)
        
        # Create UserProfile object
        user_profile = UserProfile(
            user_id=user_id,
            personalInfo=PersonalInfo(**user_data['personalInfo']),
            professionalInfo=ProfessionalInfo(**user_data['professionalInfo']),
            investmentPreferences=InvestmentPreferences(**user_data['investmentPreferences'])
        )
        
        # Save to storage
        if user_storage.save_user_data(user_profile):
            return user_id
        else:
            raise Exception("Failed to save user data")
    
    except Exception as e:
        print(f"Error creating user profile: {e}")
        raise

def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by user ID"""
    user_profile = user_storage.load_user_data(user_id)
    if user_profile:
        return user_profile.dict()
    return None

def get_user_profile_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user profile by email"""
    user_id = create_user_id_from_email(email)
    return get_user_profile(user_id)