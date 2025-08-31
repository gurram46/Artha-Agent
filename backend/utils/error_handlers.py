#!/usr/bin/env python3
"""
Error Handling Utilities for Artha AI Backend
============================================

Provides comprehensive error handling with:
- Consistent HTTP status codes
- Structured error responses
- Error logging and monitoring
- Custom exception classes
- Global exception handlers

Author: Artha AI Team
Version: 1.0
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

# Configure logger
logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """Standardized error codes for the application"""
    # Authentication & Authorization
    UNAUTHORIZED = "AUTH_001"
    FORBIDDEN = "AUTH_002"
    TOKEN_EXPIRED = "AUTH_003"
    INVALID_CREDENTIALS = "AUTH_004"
    
    # Validation Errors
    VALIDATION_ERROR = "VAL_001"
    INVALID_INPUT = "VAL_002"
    MISSING_REQUIRED_FIELD = "VAL_003"
    INVALID_FORMAT = "VAL_004"
    
    # Business Logic Errors
    RESOURCE_NOT_FOUND = "BIZ_001"
    RESOURCE_ALREADY_EXISTS = "BIZ_002"
    OPERATION_NOT_ALLOWED = "BIZ_003"
    INSUFFICIENT_PERMISSIONS = "BIZ_004"
    
    # External Service Errors
    EXTERNAL_SERVICE_ERROR = "EXT_001"
    GEMINI_API_ERROR = "EXT_002"
    FI_MONEY_API_ERROR = "EXT_003"
    DATABASE_ERROR = "EXT_004"
    
    # System Errors
    INTERNAL_SERVER_ERROR = "SYS_001"
    SERVICE_UNAVAILABLE = "SYS_002"
    TIMEOUT_ERROR = "SYS_003"
    RATE_LIMIT_EXCEEDED = "SYS_004"
    
    # File & Upload Errors
    FILE_TOO_LARGE = "FILE_001"
    INVALID_FILE_TYPE = "FILE_002"
    FILE_PROCESSING_ERROR = "FILE_003"

class ErrorResponse(BaseModel):
    """Standardized error response model"""
    error: bool = True
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str
    request_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "error_code": "VAL_001",
                "message": "Validation error occurred",
                "details": {"field": "email", "issue": "Invalid email format"},
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_123456"
            }
        }

class ArthaAIException(Exception):
    """Base exception class for Artha AI application"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(ArthaAIException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details
        )

class AuthenticationException(ArthaAIException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401
        )

class AuthorizationException(ArthaAIException):
    """Exception for authorization errors"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403
        )

class ResourceNotFoundException(ArthaAIException):
    """Exception for resource not found errors"""
    
    def __init__(self, resource: str, identifier: str = ""):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=404,
            details={"resource": resource, "identifier": identifier}
        )

class ExternalServiceException(ArthaAIException):
    """Exception for external service errors"""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service} service error: {message}",
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=502,
            details=details or {"service": service}
        )

class RateLimitException(ArthaAIException):
    """Exception for rate limiting"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429
        )

class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def create_error_response(
        error_code: ErrorCode,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create a standardized error response"""
        
        error_response = ErrorResponse(
            error_code=error_code.value,
            message=message,
            details=details,
            timestamp=datetime.utcnow().isoformat() + "Z",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error_response.dict()
        )
    
    @staticmethod
    def log_error(
        error: Exception,
        request: Optional[Request] = None,
        user_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """Log error with context information"""
        
        context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if request:
            context.update({
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            })
        
        if user_id:
            context["user_id"] = user_id
        
        if additional_context:
            context.update(additional_context)
        
        # Log with appropriate level based on error type
        if isinstance(error, (ValidationException, AuthenticationException, AuthorizationException)):
            logger.warning(f"Client error: {context}")
        elif isinstance(error, ResourceNotFoundException):
            logger.info(f"Resource not found: {context}")
        else:
            logger.error(f"Server error: {context}", exc_info=True)
    
    @staticmethod
    def handle_validation_error(error: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors"""
        
        details = []
        for err in error.errors():
            details.append({
                "field": ".".join(str(x) for x in err["loc"]),
                "message": err["msg"],
                "type": err["type"]
            })
        
        return ErrorHandler.create_error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            status_code=422,
            details={"validation_errors": details}
        )
    
    @staticmethod
    def handle_http_exception(error: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        
        # Map common HTTP status codes to error codes
        status_to_error_code = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.RESOURCE_NOT_FOUND,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_SERVER_ERROR,
            502: ErrorCode.EXTERNAL_SERVICE_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE
        }
        
        error_code = status_to_error_code.get(error.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
        
        return ErrorHandler.create_error_response(
            error_code=error_code,
            message=error.detail,
            status_code=error.status_code
        )
    
    @staticmethod
    def handle_generic_exception(error: Exception) -> JSONResponse:
        """Handle generic exceptions"""
        
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        
        return ErrorHandler.create_error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            status_code=500,
            details={"error_type": type(error).__name__} if logger.isEnabledFor(logging.DEBUG) else None
        )

# Global exception handlers for FastAPI
def setup_exception_handlers(app):
    """Setup global exception handlers for the FastAPI app"""
    
    @app.exception_handler(ArthaAIException)
    async def artha_ai_exception_handler(request: Request, exc: ArthaAIException):
        """Handle custom Artha AI exceptions"""
        ErrorHandler.log_error(exc, request)
        
        return ErrorHandler.create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors"""
        ErrorHandler.log_error(exc, request)
        return ErrorHandler.handle_validation_error(exc)
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions"""
        ErrorHandler.log_error(exc, request)
        return ErrorHandler.handle_http_exception(exc)
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        ErrorHandler.log_error(exc, request)
        return ErrorHandler.handle_generic_exception(exc)
    
    logger.info("✅ Global exception handlers configured")

# Utility functions for common error scenarios
def raise_validation_error(message: str, field: str = None, details: Dict[str, Any] = None):
    """Raise a validation error with optional field information"""
    error_details = details or {}
    if field:
        error_details["field"] = field
    
    raise ValidationException(message, error_details)

def raise_not_found(resource: str, identifier: str = ""):
    """Raise a resource not found error"""
    raise ResourceNotFoundException(resource, identifier)

def raise_unauthorized(message: str = "Authentication required"):
    """Raise an authentication error"""
    raise AuthenticationException(message)

def raise_forbidden(message: str = "Insufficient permissions"):
    """Raise an authorization error"""
    raise AuthorizationException(message)

def raise_external_service_error(service: str, message: str, details: Dict[str, Any] = None):
    """Raise an external service error"""
    raise ExternalServiceException(service, message, details)

def raise_rate_limit_error(message: str = "Rate limit exceeded"):
    """Raise a rate limit error"""
    raise RateLimitException(message)