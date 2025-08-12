"""
Input Validation Middleware for Artha AI Backend
===============================================

Comprehensive input validation and sanitization to prevent security vulnerabilities.
"""

import re
import html
import json
from typing import Any, Dict, List, Union
from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(UNION\s+SELECT)",
            r"(EXEC\s*\()",
            r"(SCRIPT\s*>)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"..%2f",
            r"..%5c",
        ]
        
        # Compile patterns for better performance
        self.compiled_sql_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
        self.compiled_xss_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]
        self.compiled_path_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.path_traversal_patterns]
        
        # Endpoints that require strict validation
        self.strict_endpoints = [
            "/api/auth/",
            "/api/user/",
            "/api/upload/",
        ]
        
        # Endpoints to skip validation (health checks, etc.)
        self.skip_endpoints = [
            "/health",
            "/status",
            "/docs",
            "/openapi.json",
        ]
    
    def _should_validate(self, path: str) -> bool:
        """Determine if endpoint should be validated"""
        # Skip validation for certain endpoints
        for skip_path in self.skip_endpoints:
            if path.startswith(skip_path):
                return False
        return True
    
    def _is_strict_endpoint(self, path: str) -> bool:
        """Check if endpoint requires strict validation"""
        for strict_path in self.strict_endpoints:
            if path.startswith(strict_path):
                return True
        return False
    
    def _detect_sql_injection(self, text: str) -> bool:
        """Detect potential SQL injection attempts"""
        if not isinstance(text, str):
            return False
        
        for pattern in self.compiled_sql_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _detect_xss(self, text: str) -> bool:
        """Detect potential XSS attempts"""
        if not isinstance(text, str):
            return False
        
        for pattern in self.compiled_xss_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _detect_path_traversal(self, text: str) -> bool:
        """Detect potential path traversal attempts"""
        if not isinstance(text, str):
            return False
        
        for pattern in self.compiled_path_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            return text
        
        # HTML escape
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        if len(text) > 10000:  # 10KB limit
            text = text[:10000]
        
        return text
    
    def _validate_value(self, value: Any, strict: bool = False) -> Any:
        """Validate and sanitize a single value"""
        if isinstance(value, str):
            # Check for malicious patterns
            if self._detect_sql_injection(value):
                logger.warning(f"SQL injection attempt detected: {value[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            if self._detect_xss(value):
                logger.warning(f"XSS attempt detected: {value[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            if self._detect_path_traversal(value):
                logger.warning(f"Path traversal attempt detected: {value[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            # Sanitize if not strict mode
            if not strict:
                value = self._sanitize_string(value)
        
        elif isinstance(value, dict):
            return {k: self._validate_value(v, strict) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._validate_value(item, strict) for item in value]
        
        return value
    
    def _validate_query_params(self, request: Request, strict: bool = False):
        """Validate query parameters"""
        for key, value in request.query_params.items():
            self._validate_value(value, strict)
    
    def _validate_path_params(self, request: Request, strict: bool = False):
        """Validate path parameters"""
        path = str(request.url.path)
        self._validate_value(path, strict)
    
    async def _validate_body(self, request: Request, strict: bool = False):
        """Validate request body"""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Get content type
                content_type = request.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    # Read body
                    body = await request.body()
                    if body:
                        try:
                            # Parse JSON
                            json_data = json.loads(body)
                            # Validate JSON data
                            self._validate_value(json_data, strict)
                        except json.JSONDecodeError:
                            if strict:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Invalid JSON format"
                                )
                
                elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
                    # For form data, validation will happen at the endpoint level
                    pass
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error validating request body: {e}")
                if strict:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid request body"
                    )
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for certain endpoints
        if not self._should_validate(request.url.path):
            return await call_next(request)
        
        try:
            # Determine if strict validation is needed
            strict = self._is_strict_endpoint(request.url.path)
            
            # Validate different parts of the request
            self._validate_query_params(request, strict)
            self._validate_path_params(request, strict)
            
            # For body validation, we need to be careful not to consume the body
            # Let the endpoint handle body validation for now
            
            # Process request
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            # If validation fails, allow the request to proceed with a warning
            logger.warning("Input validation failed, allowing request to proceed")
            return await call_next(request)

# Utility functions for manual validation
def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits_only) <= 15

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path traversal attempts
    filename = filename.replace('..', '')
    # Remove special characters except dots, hyphens, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    return filename

def validate_json_schema(data: dict, required_fields: list) -> bool:
    """Validate that JSON data contains required fields"""
    return all(field in data for field in required_fields)