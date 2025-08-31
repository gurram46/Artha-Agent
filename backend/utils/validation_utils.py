#!/usr/bin/env python3
"""
Input Validation and Sanitization Utilities for Artha AI
========================================================

Provides comprehensive input validation, sanitization, and security checks
for all API endpoints to prevent injection attacks and ensure data integrity.

Author: Artha AI Team
Version: 1.0
"""

import re
import html
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from urllib.parse import urlparse
from email.utils import parseaddr
import bleach
from pydantic import BaseModel, field_validator, ValidationError
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

class InputSanitizer:
    """Handles input sanitization and cleaning"""
    
    # Allowed HTML tags for rich text (very restrictive)
    ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    
    # Common injection patterns
    SQL_INJECTION_PATTERNS = [
        r"('|(\-\-)|(;)|(\||\|)|(\*|\*))",
        r"(union|select|insert|delete|update|drop|create|alter|exec|execute)",
        r"(script|javascript|vbscript|onload|onerror|onclick)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>"
    ]
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 10000, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            raise ValidationError("Input must be a string", code="INVALID_TYPE")
        
        # Check length
        if len(text) > max_length:
            raise ValidationError(f"Input too long (max {max_length} characters)", code="TOO_LONG")
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # HTML escape if HTML not allowed
        if not allow_html:
            text = html.escape(text)
        else:
            # Use bleach for HTML sanitization
            text = bleach.clean(
                text,
                tags=InputSanitizer.ALLOWED_TAGS,
                attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
                strip=True
            )
        
        # Check for injection patterns
        InputSanitizer._check_injection_patterns(text)
        
        return text.strip()
    
    @staticmethod
    def _check_injection_patterns(text: str) -> None:
        """Check for common injection patterns"""
        text_lower = text.lower()
        
        # Check SQL injection patterns
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential SQL injection attempt detected: {pattern}")
                raise ValidationError("Invalid input detected", code="SECURITY_VIOLATION")
        
        # Check XSS patterns
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential XSS attempt detected: {pattern}")
                raise ValidationError("Invalid input detected", code="SECURITY_VIOLATION")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            raise ValidationError("Filename cannot be empty", code="EMPTY_FILENAME")
        
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*\x00-\x1f]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        if not filename:
            raise ValidationError("Invalid filename", code="INVALID_FILENAME")
        
        return filename
    
    @staticmethod
    def validate_json(data: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
        """Validate and parse JSON data"""
        if len(data) > max_size:
            raise ValidationError(f"JSON data too large (max {max_size} bytes)", code="TOO_LARGE")
        
        try:
            parsed = json.loads(data)
            return parsed
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {str(e)}", code="INVALID_JSON")

class InputValidator:
    """Handles input validation with specific rules"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address"""
        if not email:
            raise ValidationError("Email cannot be empty", field="email", code="EMPTY_EMAIL")
        
        # Basic format check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format", field="email", code="INVALID_EMAIL")
        
        # Additional security check
        parsed = parseaddr(email)
        if not parsed[1] or parsed[1] != email:
            raise ValidationError("Invalid email format", field="email", code="INVALID_EMAIL")
        
        return email.lower().strip()
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: List[str] = None) -> str:
        """Validate URL"""
        if not url:
            raise ValidationError("URL cannot be empty", field="url", code="EMPTY_URL")
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        try:
            parsed = urlparse(url)
            if parsed.scheme not in allowed_schemes:
                raise ValidationError(
                    f"URL scheme must be one of: {', '.join(allowed_schemes)}",
                    field="url",
                    code="INVALID_SCHEME"
                )
            
            if not parsed.netloc:
                raise ValidationError("Invalid URL format", field="url", code="INVALID_URL")
            
            return url
        except Exception as e:
            raise ValidationError(f"Invalid URL: {str(e)}", field="url", code="INVALID_URL")
    
    @staticmethod
    def validate_chat_message(message: str) -> str:
        """Validate chat message content"""
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty", field="message", code="EMPTY_MESSAGE")
        
        # Sanitize the message
        sanitized = InputSanitizer.sanitize_string(message, max_length=5000)
        
        # Check minimum length
        if len(sanitized.strip()) < 1:
            raise ValidationError("Message too short", field="message", code="TOO_SHORT")
        
        return sanitized
    
    @staticmethod
    def validate_user_id(user_id: str) -> str:
        """Validate user ID format"""
        if not user_id:
            raise ValidationError("User ID cannot be empty", field="user_id", code="EMPTY_USER_ID")
        
        # Allow alphanumeric, hyphens, underscores, and dots for user IDs
        if not re.match(r'^[a-zA-Z0-9_.-]+$', user_id):
            raise ValidationError(
                "User ID can only contain letters, numbers, hyphens, underscores, and dots",
                field="user_id",
                code="INVALID_USER_ID"
            )
        
        if len(user_id) > 50:
            raise ValidationError("User ID too long (max 50 characters)", field="user_id", code="TOO_LONG")
        
        return user_id
    
    @staticmethod
    def validate_session_id(session_id: str) -> str:
        """Validate session ID format"""
        if not session_id:
            raise ValidationError("Session ID cannot be empty", field="session_id", code="EMPTY_SESSION_ID")
        
        # Should be a valid UUID or similar format
        if not re.match(r'^[a-fA-F0-9-]{8,}$', session_id):
            raise ValidationError("Invalid session ID format", field="session_id", code="INVALID_SESSION_ID")
        
        return session_id
    
    @staticmethod
    def validate_file_upload(filename: str, content_type: str, file_size: int, 
                           allowed_types: List[str] = None, max_size: int = 10 * 1024 * 1024) -> Tuple[str, str]:
        """Validate file upload parameters"""
        # Validate filename
        clean_filename = InputSanitizer.sanitize_filename(filename)
        
        # Check file size
        if file_size > max_size:
            raise ValidationError(
                f"File too large (max {max_size // (1024*1024)}MB)",
                field="file",
                code="FILE_TOO_LARGE"
            )
        
        # Check content type
        if allowed_types and content_type not in allowed_types:
            raise ValidationError(
                f"File type not allowed. Allowed types: {', '.join(allowed_types)}",
                field="file",
                code="INVALID_FILE_TYPE"
            )
        
        return clean_filename, content_type

# Pydantic models for request validation
class ChatMessageRequest(BaseModel):
    """Chat message request model"""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    think_mode: bool = False
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        return InputValidator.validate_chat_message(v)
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if v is not None:
            return InputValidator.validate_user_id(v)
        return v
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        if v is not None:
            return InputValidator.validate_session_id(v)
        return v

class FileUploadRequest(BaseModel):
    """File upload request model"""
    filename: str
    content_type: str
    file_size: int
    
    @field_validator('filename', 'content_type', 'file_size', mode='before')
    @classmethod
    def validate_file_params(cls, v, info):
        if info.field_name == 'filename':
            return InputSanitizer.sanitize_filename(v)
        elif info.field_name == 'file_size':
            if not isinstance(v, int) or v <= 0:
                raise ValueError("File size must be a positive integer")
        return v

def validate_request_data(data: Dict[str, Any], model_class: BaseModel) -> BaseModel:
    """Validate request data using Pydantic model"""
    try:
        return model_class(**data)
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )

def create_validation_middleware():
    """Create middleware for request validation"""
    async def validation_middleware(request, call_next):
        # Add request validation logic here
        response = await call_next(request)
        return response
    
    return validation_middleware

# Rate limiting helpers
class RateLimitValidator:
    """Validates rate limiting parameters"""
    
    @staticmethod
    def validate_rate_limit_key(key: str) -> str:
        """Validate rate limit key format"""
        if not key or len(key) > 100:
            raise ValidationError("Invalid rate limit key", code="INVALID_RATE_KEY")
        
        # Only allow safe characters
        if not re.match(r'^[a-zA-Z0-9:._-]+$', key):
            raise ValidationError("Rate limit key contains invalid characters", code="INVALID_RATE_KEY")
        
        return key

if __name__ == "__main__":
    # Test validation functions
    print("🧪 Testing validation utilities...")
    
    try:
        # Test message validation
        message = InputValidator.validate_chat_message("Hello, how are you?")
        print(f"✅ Message validation: {message}")
        
        # Test email validation
        email = InputValidator.validate_email("test@example.com")
        print(f"✅ Email validation: {email}")
        
        # Test URL validation
        url = InputValidator.validate_url("https://example.com")
        print(f"✅ URL validation: {url}")
        
        print("✅ All validation tests passed!")
        
    except ValidationError as e:
        print(f"❌ Validation test failed: {e}")