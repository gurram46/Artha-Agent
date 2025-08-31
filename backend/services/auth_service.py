"""
Advanced Authentication Service for Artha AI
===========================================

Comprehensive user authentication with JWT, encryption, and security features.
"""

import os
import sys
import hashlib
import secrets
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import jwt
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
import re
from email_validator import validate_email, EmailNotValidError

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_database_url
from utils.encryption import EncryptionHelper

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class ValidationError(Exception):
    """Custom validation error"""
    pass

class AuthService:
    """
    Comprehensive authentication service with enterprise-level security
    """
    
    def __init__(self):
        self.database_url = get_database_url()
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'artha_ai_jwt_secret_2024_secure')
        self.jwt_algorithm = 'HS256'
        self.access_token_expire = 24 * 60 * 60  # 24 hours
        self.refresh_token_expire = 7 * 24 * 60 * 60  # 7 days
        self.max_login_attempts = 5
        self.lockout_duration = 30 * 60  # 30 minutes
        self.encryption = EncryptionHelper()
        
        # Password requirements - Enhanced security
        self.min_password_length = 12
        self.max_password_length = 128
        self.password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,128}$')
    
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
            raise AuthenticationError("Database connection failed")
    
    def _hash_email(self, email: str) -> str:
        """Create consistent hash of email for indexing"""
        return hashlib.sha256(email.lower().encode()).hexdigest()
    
    def _validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength with detailed error messages"""
        if not password:
            return False, "Password is required"
        
        if len(password) < self.min_password_length:
            return False, f"Password must be at least {self.min_password_length} characters long"
        
        if len(password) > self.max_password_length:
            return False, f"Password must not exceed {self.max_password_length} characters"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[@$!%*?&]', password):
            return False, "Password must contain at least one special character (@$!%*?&)"
        
        # Check for common weak patterns
        if password.lower() in ['password', '123456789', 'qwertyuiop']:
            return False, "Password is too common and easily guessable"
        
        return True, "Password is valid"
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    def _generate_salt(self) -> str:
        """Generate cryptographic salt"""
        return secrets.token_hex(16)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using bcrypt"""
        salted_password = (password + salt).encode('utf-8')
        return bcrypt.hashpw(salted_password, bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, salt: str, hashed: str) -> bool:
        """Verify password against hash"""
        salted_password = (password + salt).encode('utf-8')
        return bcrypt.checkpw(salted_password, hashed.encode('utf-8'))
    
    def _generate_tokens(self, user_id: str, email: str) -> Tuple[str, str]:
        """Generate JWT access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'email': email,
            'type': 'access',
            'exp': now + timedelta(seconds=self.access_token_expire),
            'iat': now
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'email': email,
            'type': 'refresh',
            'exp': now + timedelta(seconds=self.refresh_token_expire),
            'iat': now
        }
        
        access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        return access_token, refresh_token
    
    def _is_account_locked(self, user_data: Dict) -> bool:
        """Check if account is locked due to failed attempts"""
        if not user_data.get('locked_until'):
            return False
        
        locked_until = user_data['locked_until']
        if isinstance(locked_until, str):
            locked_until = datetime.fromisoformat(locked_until.replace('Z', '+00:00'))
        
        return datetime.now(locked_until.tzinfo) < locked_until
    
    def register_user(self, email: str, password: str, full_name: str, 
                     phone: Optional[str] = None, date_of_birth: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new user with comprehensive validation and security
        """
        try:
            # Validate inputs
            if not self._validate_email(email):
                raise ValidationError("Invalid email format")
            
            password_valid, password_error = self._validate_password(password)
            if not password_valid:
                raise ValidationError(password_error)
            
            if not full_name or len(full_name.strip()) < 2:
                raise ValidationError("Full name must be at least 2 characters")
            
            email = email.lower().strip()
            email_hash = self._hash_email(email)
            user_id = str(uuid.uuid4())
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)
            
            # Encrypt sensitive data using GCM mode
            full_name_enc = self.encryption.encrypt_data_gcm(full_name.strip())
            phone_enc = self.encryption.encrypt_data_gcm(phone) if phone else None
            dob_enc = self.encryption.encrypt_data_gcm(date_of_birth) if date_of_birth else None
            
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if user already exists
                    cursor.execute(
                        "SELECT id FROM users WHERE email_hash = %s",
                        (email_hash,)
                    )
                    if cursor.fetchone():
                        raise ValidationError("User with this email already exists")
                    
                    # Insert new user
                    cursor.execute("""
                        INSERT INTO users (
                            id, email, email_hash, password_hash, salt,
                            full_name_encrypted, full_name_nonce, full_name_auth_tag,
                            phone_encrypted, phone_nonce, phone_auth_tag,
                            date_of_birth_encrypted, date_of_birth_nonce, date_of_birth_auth_tag,
                            verification_token, is_verified, is_active
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s
                        )
                    """, (
                        user_id, email, email_hash, password_hash, salt,
                        full_name_enc['encrypted_data'], full_name_enc['nonce'], full_name_enc['auth_tag'],
                        phone_enc['encrypted_data'] if phone_enc else None,
                        phone_enc['nonce'] if phone_enc else None,
                        phone_enc['auth_tag'] if phone_enc else None,
                        dob_enc['encrypted_data'] if dob_enc else None,
                        dob_enc['nonce'] if dob_enc else None,
                        dob_enc['auth_tag'] if dob_enc else None,
                        secrets.token_urlsafe(32), True, True  # Auto-verify for now, can add email verification later
                    ))
                    
                    # Create default investment preferences
                    prefs_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO investment_preferences (
                            id, user_id, risk_tolerance, investment_horizon,
                            investment_goals, emergency_fund_months, investment_experience
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        prefs_id, user_id, 'moderate', 'long_term',
                        '["wealth_building"]', 6, 'beginner'
                    ))
                    
                    # Create default user profile
                    profile_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO user_profiles (id, user_id) VALUES (%s, %s)
                    """, (profile_id, user_id))
                    
                    conn.commit()
            
            logger.info(f"✅ User registered successfully: {email}")
            
            # Generate tokens for immediate login
            access_token, refresh_token = self._generate_tokens(user_id, email)
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "is_verified": True,
                    "last_login": None
                },
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": self.access_token_expire
                }
            }
            
        except ValidationError as e:
            logger.warning(f"Registration validation failed: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {"success": False, "message": "Registration failed. Please try again."}
    
    def login_user(self, email: str, password: str, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate user with comprehensive security checks
        """
        try:
            email = email.lower().strip()
            email_hash = self._hash_email(email)
            
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get user data
                    cursor.execute("""
                        SELECT id, email, password_hash, salt, login_attempts, locked_until,
                               is_active, is_verified, full_name_encrypted, full_name_nonce, full_name_auth_tag,
                               last_login
                        FROM users WHERE email_hash = %s
                    """, (email_hash,))
                    
                    user = cursor.fetchone()
                    if not user:
                        raise ValidationError("Invalid email or password")
                    
                    user_dict = dict(user)
                    
                    # Check if account is active
                    if not user_dict['is_active']:
                        raise ValidationError("Account is deactivated")
                    
                    # Check if account is locked
                    if self._is_account_locked(user_dict):
                        raise ValidationError("Account is temporarily locked. Please try again later.")
                    
                    # Verify password
                    if not self._verify_password(password, user_dict['salt'], user_dict['password_hash']):
                        # Increment login attempts
                        login_attempts = user_dict['login_attempts'] + 1
                        locked_until = None
                        
                        if login_attempts >= self.max_login_attempts:
                            locked_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
                        
                        cursor.execute("""
                            UPDATE users SET login_attempts = %s, locked_until = %s
                            WHERE id = %s
                        """, (login_attempts, locked_until, user_dict['id']))
                        conn.commit()
                        
                        if locked_until:
                            raise ValidationError("Too many failed attempts. Account locked for 30 minutes.")
                        else:
                            raise ValidationError("Invalid email or password")
                    
                    # Successful login - reset attempts and update last login
                    cursor.execute("""
                        UPDATE users SET login_attempts = 0, locked_until = NULL, last_login = %s
                        WHERE id = %s
                    """, (datetime.utcnow(), user_dict['id']))
                    
                    # Generate session tokens
                    access_token, refresh_token = self._generate_tokens(user_dict['id'], email)
                    
                    # Create session record
                    session_id = str(uuid.uuid4())
                    expires_at = datetime.utcnow() + timedelta(seconds=self.access_token_expire)
                    refresh_expires_at = datetime.utcnow() + timedelta(seconds=self.refresh_token_expire)
                    
                    cursor.execute("""
                        INSERT INTO user_sessions (
                            id, user_id, session_token, refresh_token,
                            expires_at, refresh_expires_at, ip_address, user_agent
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        session_id, user_dict['id'], access_token, refresh_token,
                        expires_at, refresh_expires_at, ip_address, user_agent
                    ))
                    
                    conn.commit()
                    
                    # Decrypt full name for response
                    full_name = self.encryption.decrypt_data_gcm({
                        'encrypted_data': user_dict['full_name_encrypted'],
                        'nonce': user_dict['full_name_nonce'],
                        'auth_tag': user_dict['full_name_auth_tag']
                    }) if user_dict['full_name_encrypted'] else "User"
                    
                    logger.info(f"✅ User logged in successfully: {email}")
                    
                    return {
                        "success": True,
                        "message": "Login successful",
                        "user": {
                            "id": user_dict['id'],
                            "email": email,
                            "full_name": full_name,
                            "is_verified": user_dict['is_verified'],
                            "last_login": user_dict['last_login'].isoformat() if user_dict['last_login'] else None
                        },
                        "tokens": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "bearer",
                            "expires_in": self.access_token_expire
                        },
                        "session_id": session_id
                    }
                    
        except ValidationError as e:
            logger.warning(f"Login validation failed: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {"success": False, "message": "Login failed. Please try again."}
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return user information
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            if payload.get('type') != 'access':
                raise jwt.InvalidTokenError("Invalid token type")
            
            user_id = payload.get('user_id')
            email = payload.get('email')
            
            if not user_id or not email:
                raise jwt.InvalidTokenError("Invalid token payload")
            
            # Verify user still exists and is active
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, email, is_active, is_verified,
                               full_name_encrypted, full_name_nonce, full_name_auth_tag
                        FROM users WHERE id = %s AND email = %s
                    """, (user_id, email))
                    
                    user = cursor.fetchone()
                    if not user or not user['is_active']:
                        raise jwt.InvalidTokenError("User not found or inactive")
                    
                    user_dict = dict(user)
                    
                    # Decrypt full name
                    full_name = self.encryption.decrypt_data_gcm({
                        'encrypted_data': user_dict['full_name_encrypted'],
                        'nonce': user_dict['full_name_nonce'],
                        'auth_tag': user_dict['full_name_auth_tag']
                    }) if user_dict['full_name_encrypted'] else "User"
                    
                    return {
                        "valid": True,
                        "user": {
                            "id": user_dict['id'],
                            "email": user_dict['email'],
                            "full_name": full_name,
                            "is_verified": user_dict['is_verified']
                        }
                    }
                    
        except jwt.ExpiredSignatureError:
            return {"valid": False, "message": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "message": "Invalid token"}
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return {"valid": False, "message": "Token verification failed"}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Generate new access token using refresh token
        """
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError("Invalid token type")
            
            user_id = payload.get('user_id')
            email = payload.get('email')
            
            # Verify session exists
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM user_sessions 
                        WHERE refresh_token = %s AND is_active = TRUE 
                        AND refresh_expires_at > %s
                    """, (refresh_token, datetime.utcnow()))
                    
                    if not cursor.fetchone():
                        raise jwt.InvalidTokenError("Invalid refresh token session")
                    
                    # Generate new access token
                    new_access_token, _ = self._generate_tokens(user_id, email)
                    
                    # Update session with new access token
                    new_expires_at = datetime.utcnow() + timedelta(seconds=self.access_token_expire)
                    cursor.execute("""
                        UPDATE user_sessions 
                        SET session_token = %s, expires_at = %s, last_used = %s
                        WHERE refresh_token = %s
                    """, (new_access_token, new_expires_at, datetime.utcnow(), refresh_token))
                    
                    conn.commit()
                    
                    return {
                        "success": True,
                        "access_token": new_access_token,
                        "token_type": "bearer",
                        "expires_in": self.access_token_expire
                    }
                    
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Refresh token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid refresh token"}
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {"success": False, "message": "Token refresh failed"}
    
    def logout_user(self, access_token: str) -> Dict[str, Any]:
        """
        Logout user and invalidate session
        """
        try:
            # Decode token to get session info
            payload = jwt.decode(access_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Deactivate all sessions for this token
                    cursor.execute("""
                        UPDATE user_sessions 
                        SET is_active = FALSE 
                        WHERE session_token = %s
                    """, (access_token,))
                    
                    conn.commit()
                    
                    return {"success": True, "message": "Logged out successfully"}
                    
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return {"success": False, "message": "Logout failed"}
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
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
                               u.date_of_birth_encrypted, u.date_of_birth_nonce, u.date_of_birth_auth_tag
                        FROM users u WHERE u.id = %s
                    """, (user_id,))
                    
                    user = cursor.fetchone()
                    if not user:
                        return {"success": False, "message": "User not found"}
                    
                    user_dict = dict(user)
                    
                    # Get investment preferences
                    cursor.execute("""
                        SELECT risk_tolerance, investment_horizon, investment_goals,
                               preferred_asset_classes, monthly_investment_amount,
                               emergency_fund_months, investment_experience, advisor_preference
                        FROM investment_preferences WHERE user_id = %s
                    """, (user_id,))
                    
                    prefs = cursor.fetchone()
                    prefs_dict = dict(prefs) if prefs else {}
                    
                    # Decrypt sensitive data
                    profile = {
                        "id": user_dict['id'],
                        "email": user_dict['email'],
                        "created_at": user_dict['created_at'].isoformat(),
                        "last_login": user_dict['last_login'].isoformat() if user_dict['last_login'] else None,
                        "is_verified": user_dict['is_verified']
                    }
                    
                    # Decrypt personal info
                    if user_dict['full_name_encrypted']:
                        profile['full_name'] = self.encryption.decrypt_data_gcm({
                            'encrypted_data': user_dict['full_name_encrypted'],
                            'nonce': user_dict['full_name_nonce'],
                            'auth_tag': user_dict['full_name_auth_tag']
                        })
                    
                    if user_dict['phone_encrypted']:
                        profile['phone'] = self.encryption.decrypt_data_gcm({
                            'encrypted_data': user_dict['phone_encrypted'],
                            'nonce': user_dict['phone_nonce'],
                            'auth_tag': user_dict['phone_auth_tag']
                        })
                    
                    if user_dict['date_of_birth_encrypted']:
                        profile['date_of_birth'] = self.encryption.decrypt_data_gcm({
                            'encrypted_data': user_dict['date_of_birth_encrypted'],
                            'nonce': user_dict['date_of_birth_nonce'],
                            'auth_tag': user_dict['date_of_birth_auth_tag']
                        })
                    
                    profile['investment_preferences'] = prefs_dict
                    
                    return {"success": True, "profile": profile}
                    
        except Exception as e:
            logger.error(f"Get user profile failed: {e}")
            return {"success": False, "message": "Failed to get user profile"}


# Global auth service instance
_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get or create global auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service