"""
User Profile Management Service for Artha AI
==========================================

Comprehensive user profile management with encrypted storage and preferences.
"""

import os
import sys
import uuid
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_database_url
from utils.encryption import EncryptionHelper

logger = logging.getLogger(__name__)

class UserService:
    """
    Comprehensive user profile management service
    """
    
    def __init__(self):
        self.database_url = get_database_url()
        self.encryption = EncryptionHelper()
    
    def _get_db_connection(self):
        """Get database connection with proper error handling"""
        try:
            # Parse database URL
            import re
            match = re.match(r'postgresql://([^:]+):?([^@]*)@([^:]+):(\d+)/(.+)', self.database_url)
            if not match:
                match = re.match(r'postgresql://([^@]+)@([^:]+):(\d+)/(.+)', self.database_url)
                if match:
                    user, host, port, database = match.groups()
                    password = ''
                else:
                    raise ValueError(f"Invalid database URL format: {self.database_url}")
            else:
                user, password, host, port, database = match.groups()
            
            conn = psycopg2.connect(
                host=host,
                port=int(port),
                database=database,
                user=user,
                password=password,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise Exception("Database connection failed")
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile with encrypted sensitive data
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Update basic user info if provided
                    user_updates = {}
                    if 'full_name' in profile_data:
                        full_name_enc = self.encryption.encrypt_data(profile_data['full_name'])
                        user_updates.update({
                            'full_name_encrypted': full_name_enc['encrypted_data'],
                            'full_name_nonce': full_name_enc['nonce'],
                            'full_name_auth_tag': full_name_enc['auth_tag']
                        })
                    
                    if 'phone' in profile_data:
                        phone_enc = self.encryption.encrypt_data(profile_data['phone'])
                        user_updates.update({
                            'phone_encrypted': phone_enc['encrypted_data'],
                            'phone_nonce': phone_enc['nonce'],
                            'phone_auth_tag': phone_enc['auth_tag']
                        })
                    
                    if 'date_of_birth' in profile_data:
                        dob_enc = self.encryption.encrypt_data(profile_data['date_of_birth'])
                        user_updates.update({
                            'date_of_birth_encrypted': dob_enc['encrypted_data'],
                            'date_of_birth_nonce': dob_enc['nonce'],
                            'date_of_birth_auth_tag': dob_enc['auth_tag']
                        })
                    
                    if user_updates:
                        set_clause = ', '.join([f"{k} = %s" for k in user_updates.keys()])
                        cursor.execute(f"""
                            UPDATE users SET {set_clause}, updated_at = %s
                            WHERE id = %s
                        """, list(user_updates.values()) + [datetime.utcnow(), user_id])
                    
                    # Update extended profile info
                    profile_updates = {}
                    if 'occupation' in profile_data:
                        occ_enc = self.encryption.encrypt_data(profile_data['occupation'])
                        profile_updates.update({
                            'occupation_encrypted': occ_enc['encrypted_data'],
                            'occupation_nonce': occ_enc['nonce'],
                            'occupation_auth_tag': occ_enc['auth_tag']
                        })
                    
                    if 'annual_income' in profile_data:
                        income_enc = self.encryption.encrypt_data(str(profile_data['annual_income']))
                        profile_updates.update({
                            'annual_income_encrypted': income_enc['encrypted_data'],
                            'annual_income_nonce': income_enc['nonce'],
                            'annual_income_auth_tag': income_enc['auth_tag']
                        })
                    
                    if 'company' in profile_data:
                        company_enc = self.encryption.encrypt_data(profile_data['company'])
                        profile_updates.update({
                            'company_encrypted': company_enc['encrypted_data'],
                            'company_nonce': company_enc['nonce'],
                            'company_auth_tag': company_enc['auth_tag']
                        })
                    
                    if 'experience_years' in profile_data:
                        profile_updates['experience_years'] = profile_data['experience_years']
                    
                    if 'address' in profile_data:
                        addr_enc = self.encryption.encrypt_data(profile_data['address'])
                        profile_updates.update({
                            'address_encrypted': addr_enc['encrypted_data'],
                            'address_nonce': addr_enc['nonce'],
                            'address_auth_tag': addr_enc['auth_tag']
                        })
                    
                    if profile_updates:
                        # Check if profile exists
                        cursor.execute("SELECT id FROM user_profiles WHERE user_id = %s", (user_id,))
                        if cursor.fetchone():
                            # Update existing profile
                            set_clause = ', '.join([f"{k} = %s" for k in profile_updates.keys()])
                            cursor.execute(f"""
                                UPDATE user_profiles SET {set_clause}, updated_at = %s
                                WHERE user_id = %s
                            """, list(profile_updates.values()) + [datetime.utcnow(), user_id])
                        else:
                            # Create new profile
                            profile_id = str(uuid.uuid4())
                            profile_updates['id'] = profile_id
                            profile_updates['user_id'] = user_id
                            
                            columns = ', '.join(profile_updates.keys())
                            placeholders = ', '.join(['%s'] * len(profile_updates))
                            cursor.execute(f"""
                                INSERT INTO user_profiles ({columns}) VALUES ({placeholders})
                            """, list(profile_updates.values()))
                    
                    conn.commit()
                    
                    logger.info(f"✅ User profile updated successfully: {user_id}")
                    return {"success": True, "message": "Profile updated successfully"}
                    
        except Exception as e:
            logger.error(f"Update user profile failed: {e}")
            return {"success": False, "message": "Failed to update profile"}
    
    def update_investment_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user investment preferences
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if preferences exist
                    cursor.execute("SELECT id FROM investment_preferences WHERE user_id = %s", (user_id,))
                    existing = cursor.fetchone()
                    
                    # Prepare update data
                    update_data = {}
                    
                    if 'risk_tolerance' in preferences:
                        update_data['risk_tolerance'] = preferences['risk_tolerance']
                    
                    if 'investment_horizon' in preferences:
                        update_data['investment_horizon'] = preferences['investment_horizon']
                    
                    if 'investment_goals' in preferences:
                        update_data['investment_goals'] = json.dumps(preferences['investment_goals'])
                    
                    if 'preferred_asset_classes' in preferences:
                        update_data['preferred_asset_classes'] = json.dumps(preferences['preferred_asset_classes'])
                    
                    if 'monthly_investment_amount' in preferences:
                        update_data['monthly_investment_amount'] = Decimal(str(preferences['monthly_investment_amount']))
                    
                    if 'emergency_fund_months' in preferences:
                        update_data['emergency_fund_months'] = preferences['emergency_fund_months']
                    
                    if 'debt_to_income_ratio' in preferences:
                        update_data['debt_to_income_ratio'] = Decimal(str(preferences['debt_to_income_ratio']))
                    
                    if 'current_investments' in preferences:
                        update_data['current_investments'] = json.dumps(preferences['current_investments'])
                    
                    if 'financial_dependents' in preferences:
                        update_data['financial_dependents'] = preferences['financial_dependents']
                    
                    if 'retirement_age' in preferences:
                        update_data['retirement_age'] = preferences['retirement_age']
                    
                    if 'major_expenses' in preferences:
                        update_data['major_expenses'] = json.dumps(preferences['major_expenses'])
                    
                    if 'insurance_coverage' in preferences:
                        update_data['insurance_coverage'] = json.dumps(preferences['insurance_coverage'])
                    
                    if 'tax_bracket' in preferences:
                        update_data['tax_bracket'] = preferences['tax_bracket']
                    
                    if 'investment_experience' in preferences:
                        update_data['investment_experience'] = preferences['investment_experience']
                    
                    if 'advisor_preference' in preferences:
                        update_data['advisor_preference'] = preferences['advisor_preference']
                    
                    if update_data:
                        if existing:
                            # Update existing preferences
                            set_clause = ', '.join([f"{k} = %s" for k in update_data.keys()])
                            cursor.execute(f"""
                                UPDATE investment_preferences SET {set_clause}, updated_at = %s
                                WHERE user_id = %s
                            """, list(update_data.values()) + [datetime.utcnow(), user_id])
                        else:
                            # Create new preferences
                            prefs_id = str(uuid.uuid4())
                            update_data['id'] = prefs_id
                            update_data['user_id'] = user_id
                            
                            columns = ', '.join(update_data.keys())
                            placeholders = ', '.join(['%s'] * len(update_data))
                            cursor.execute(f"""
                                INSERT INTO investment_preferences ({columns}) VALUES ({placeholders})
                            """, list(update_data.values()))
                    
                    conn.commit()
                    
                    logger.info(f"✅ Investment preferences updated successfully: {user_id}")
                    return {"success": True, "message": "Investment preferences updated successfully"}
                    
        except Exception as e:
            logger.error(f"Update investment preferences failed: {e}")
            return {"success": False, "message": "Failed to update investment preferences"}
    
    def get_complete_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete user profile with decrypted data
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get user basic info
                    cursor.execute("""
                        SELECT u.id, u.email, u.created_at, u.last_login, u.is_verified,
                               u.full_name_encrypted, u.full_name_nonce, u.full_name_auth_tag,
                               u.phone_encrypted, u.phone_nonce, u.phone_auth_tag,
                               u.date_of_birth_encrypted, u.date_of_birth_nonce, u.date_of_birth_auth_tag,
                               up.occupation_encrypted, up.occupation_nonce, up.occupation_auth_tag,
                               up.annual_income_encrypted, up.annual_income_nonce, up.annual_income_auth_tag,
                               up.company_encrypted, up.company_nonce, up.company_auth_tag,
                               up.experience_years,
                               up.address_encrypted, up.address_nonce, up.address_auth_tag
                        FROM users u
                        LEFT JOIN user_profiles up ON u.id = up.user_id
                        WHERE u.id = %s
                    """, (user_id,))
                    
                    user_data = cursor.fetchone()
                    if not user_data:
                        return {"success": False, "message": "User not found"}
                    
                    user_dict = dict(user_data)
                    
                    # Get investment preferences
                    cursor.execute("""
                        SELECT risk_tolerance, investment_horizon, investment_goals,
                               preferred_asset_classes, monthly_investment_amount,
                               emergency_fund_months, debt_to_income_ratio,
                               current_investments, financial_dependents, retirement_age,
                               major_expenses, insurance_coverage, tax_bracket,
                               investment_experience, advisor_preference, created_at, updated_at
                        FROM investment_preferences WHERE user_id = %s
                    """, (user_id,))
                    
                    prefs_data = cursor.fetchone()
                    prefs_dict = dict(prefs_data) if prefs_data else {}
                    
                    # Build profile response
                    profile = {
                        "id": user_dict['id'],
                        "email": user_dict['email'],
                        "created_at": user_dict['created_at'].isoformat(),
                        "last_login": user_dict['last_login'].isoformat() if user_dict['last_login'] else None,
                        "is_verified": user_dict['is_verified']
                    }
                    
                    # Decrypt personal information
                    if user_dict.get('full_name_encrypted'):
                        try:
                            profile['full_name'] = self.encryption.decrypt_data({
                                'encrypted_data': user_dict['full_name_encrypted'],
                                'nonce': user_dict['full_name_nonce'],
                                'auth_tag': user_dict['full_name_auth_tag']
                            })
                        except:
                            profile['full_name'] = "User"
                    
                    if user_dict.get('phone_encrypted'):
                        try:
                            profile['phone'] = self.encryption.decrypt_data({
                                'encrypted_data': user_dict['phone_encrypted'],
                                'nonce': user_dict['phone_nonce'],
                                'auth_tag': user_dict['phone_auth_tag']
                            })
                        except:
                            pass
                    
                    if user_dict.get('date_of_birth_encrypted'):
                        try:
                            profile['date_of_birth'] = self.encryption.decrypt_data({
                                'encrypted_data': user_dict['date_of_birth_encrypted'],
                                'nonce': user_dict['date_of_birth_nonce'],
                                'auth_tag': user_dict['date_of_birth_auth_tag']
                            })
                        except:
                            pass
                    
                    # Decrypt professional information
                    if user_dict.get('occupation_encrypted'):
                        try:
                            profile['occupation'] = self.encryption.decrypt_data({
                                'encrypted_data': user_dict['occupation_encrypted'],
                                'nonce': user_dict['occupation_nonce'],
                                'auth_tag': user_dict['occupation_auth_tag']
                            })
                        except:
                            pass
                    
                    if user_dict.get('annual_income_encrypted'):
                        try:
                            income_str = self.encryption.decrypt_data({
                                'encrypted_data': user_dict['annual_income_encrypted'],
                                'nonce': user_dict['annual_income_nonce'],
                                'auth_tag': user_dict['annual_income_auth_tag']
                            })
                            profile['annual_income'] = float(income_str)
                        except:
                            pass
                    
                    if user_dict.get('company_encrypted'):
                        try:
                            profile['company'] = self.encryption.decrypt_data({
                                'encrypted_data': user_dict['company_encrypted'],
                                'nonce': user_dict['company_nonce'],
                                'auth_tag': user_dict['company_auth_tag']
                            })
                        except:
                            pass
                    
                    if user_dict.get('experience_years'):
                        profile['experience_years'] = user_dict['experience_years']
                    
                    if user_dict.get('address_encrypted'):
                        try:
                            profile['address'] = self.encryption.decrypt_data({
                                'encrypted_data': user_dict['address_encrypted'],
                                'nonce': user_dict['address_nonce'],
                                'auth_tag': user_dict['address_auth_tag']
                            })
                        except:
                            pass
                    
                    # Process investment preferences
                    if prefs_dict:
                        investment_prefs = {}
                        for key, value in prefs_dict.items():
                            if key in ['created_at', 'updated_at'] and value:
                                investment_prefs[key] = value.isoformat()
                            elif key in ['investment_goals', 'preferred_asset_classes', 'current_investments', 
                                       'major_expenses', 'insurance_coverage'] and value:
                                try:
                                    investment_prefs[key] = json.loads(value)
                                except:
                                    investment_prefs[key] = value
                            elif key in ['monthly_investment_amount', 'debt_to_income_ratio'] and value:
                                investment_prefs[key] = float(value)
                            else:
                                investment_prefs[key] = value
                        
                        profile['investment_preferences'] = investment_prefs
                    
                    return {"success": True, "profile": profile}
                    
        except Exception as e:
            logger.error(f"Get complete profile failed: {e}")
            return {"success": False, "message": "Failed to get user profile"}
    
    def create_user_goal(self, user_id: str, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new financial goal for user
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    goal_id = str(uuid.uuid4())
                    
                    # Encrypt description if provided
                    description_enc = None
                    if goal_data.get('description'):
                        description_enc = self.encryption.encrypt_data(goal_data['description'])
                    
                    cursor.execute("""
                        INSERT INTO user_goals (
                            id, user_id, goal_name, goal_type, target_amount,
                            current_amount, target_date, monthly_contribution,
                            priority_level, description_encrypted, description_nonce, description_auth_tag,
                            strategy, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        goal_id, user_id, goal_data['goal_name'], goal_data['goal_type'],
                        Decimal(str(goal_data['target_amount'])),
                        Decimal(str(goal_data.get('current_amount', 0))),
                        goal_data.get('target_date'),
                        Decimal(str(goal_data.get('monthly_contribution', 0))) if goal_data.get('monthly_contribution') else None,
                        goal_data.get('priority_level', 3),
                        description_enc['encrypted_data'] if description_enc else None,
                        description_enc['nonce'] if description_enc else None,
                        description_enc['auth_tag'] if description_enc else None,
                        json.dumps(goal_data.get('strategy', {})),
                        'active'
                    ))
                    
                    conn.commit()
                    
                    logger.info(f"✅ User goal created successfully: {user_id} - {goal_data['goal_name']}")
                    return {"success": True, "message": "Goal created successfully", "goal_id": goal_id}
                    
        except Exception as e:
            logger.error(f"Create user goal failed: {e}")
            return {"success": False, "message": "Failed to create goal"}
    
    def get_user_goals(self, user_id: str) -> Dict[str, Any]:
        """
        Get all user goals with decrypted data
        """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, goal_name, goal_type, target_amount, current_amount,
                               target_date, monthly_contribution, priority_level, status,
                               description_encrypted, description_nonce, description_auth_tag,
                               strategy, progress_tracking, created_at, updated_at
                        FROM user_goals WHERE user_id = %s ORDER BY priority_level, created_at DESC
                    """, (user_id,))
                    
                    goals_data = cursor.fetchall()
                    goals = []
                    
                    for goal in goals_data:
                        goal_dict = dict(goal)
                        
                        # Convert decimals to floats
                        if goal_dict['target_amount']:
                            goal_dict['target_amount'] = float(goal_dict['target_amount'])
                        if goal_dict['current_amount']:
                            goal_dict['current_amount'] = float(goal_dict['current_amount'])
                        if goal_dict['monthly_contribution']:
                            goal_dict['monthly_contribution'] = float(goal_dict['monthly_contribution'])
                        
                        # Decrypt description
                        if goal_dict.get('description_encrypted'):
                            try:
                                goal_dict['description'] = self.encryption.decrypt_data({
                                    'encrypted_data': goal_dict['description_encrypted'],
                                    'nonce': goal_dict['description_nonce'],
                                    'auth_tag': goal_dict['description_auth_tag']
                                })
                            except:
                                goal_dict['description'] = None
                        
                        # Remove encrypted fields from response
                        goal_dict.pop('description_encrypted', None)
                        goal_dict.pop('description_nonce', None)
                        goal_dict.pop('description_auth_tag', None)
                        
                        # Parse JSON fields
                        if goal_dict['strategy']:
                            try:
                                goal_dict['strategy'] = json.loads(goal_dict['strategy'])
                            except:
                                goal_dict['strategy'] = {}
                        
                        if goal_dict['progress_tracking']:
                            try:
                                goal_dict['progress_tracking'] = json.loads(goal_dict['progress_tracking'])
                            except:
                                goal_dict['progress_tracking'] = {}
                        
                        # Format dates
                        if goal_dict['target_date']:
                            goal_dict['target_date'] = goal_dict['target_date'].isoformat()
                        if goal_dict['created_at']:
                            goal_dict['created_at'] = goal_dict['created_at'].isoformat()
                        if goal_dict['updated_at']:
                            goal_dict['updated_at'] = goal_dict['updated_at'].isoformat()
                        
                        goals.append(goal_dict)
                    
                    return {"success": True, "goals": goals}
                    
        except Exception as e:
            logger.error(f"Get user goals failed: {e}")
            return {"success": False, "message": "Failed to get user goals"}


# Global user service instance
_user_service: Optional[UserService] = None

def get_user_service() -> UserService:
    """Get or create global user service instance"""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service