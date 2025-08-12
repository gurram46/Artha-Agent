"""
Rate Limiting Middleware for Artha AI Backend
============================================

Comprehensive rate limiting with different tiers for various endpoints.
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
import logging
import os

logger = logging.getLogger(__name__)

class RateLimiter:
    """Thread-safe rate limiter using sliding window algorithm"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, identifier: str) -> Tuple[bool, Optional[float]]:
        """Check if request is allowed, return (allowed, retry_after_seconds)"""
        async with self._lock:
            current_time = time.time()
            window_start = current_time - self.window_seconds
            
            # Clean old requests
            user_requests = self.requests[identifier]
            while user_requests and user_requests[0] < window_start:
                user_requests.popleft()
            
            # Check if under limit
            if len(user_requests) < self.max_requests:
                user_requests.append(current_time)
                return True, None
            
            # Calculate retry after time
            oldest_request = user_requests[0]
            retry_after = oldest_request + self.window_seconds - current_time
            return False, max(0, retry_after)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with different limits for different endpoint types"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Different rate limits for different endpoint types
        self.limiters = {
            # Authentication endpoints - stricter limits
            'auth': RateLimiter(max_requests=10, window_seconds=60),  # 10 requests per minute
            
            # General API endpoints
            'api': RateLimiter(max_requests=100, window_seconds=60),  # 100 requests per minute
            
            # Chat/AI endpoints - moderate limits
            'chat': RateLimiter(max_requests=30, window_seconds=60),  # 30 requests per minute
            
            # File upload endpoints - very strict
            'upload': RateLimiter(max_requests=5, window_seconds=60),  # 5 uploads per minute
            
            # Health/status endpoints - lenient
            'health': RateLimiter(max_requests=200, window_seconds=60),  # 200 requests per minute
        }
        
        # Global rate limiter for overall protection
        self.global_limiter = RateLimiter(max_requests=500, window_seconds=60)  # 500 total requests per minute
        
        # Whitelist for development
        self.whitelist_ips = set(os.getenv("RATE_LIMIT_WHITELIST", "127.0.0.1,::1").split(","))
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get real IP from headers (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # For authenticated requests, use user ID if available
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # Extract user info from token (simplified - in production, decode JWT)
                token = auth_header.split(" ")[1]
                # For now, use token hash as identifier
                import hashlib
                user_id = hashlib.sha256(token.encode()).hexdigest()[:16]
                return f"user:{user_id}"
            except:
                pass
        
        return f"ip:{client_ip}"
    
    def _get_endpoint_category(self, path: str) -> str:
        """Determine endpoint category for rate limiting"""
        if path.startswith("/api/auth/"):
            return "auth"
        elif path.startswith("/api/chat/") or path.startswith("/api/query") or path.startswith("/api/stream"):
            return "chat"
        elif path.startswith("/api/upload/") or "upload" in path:
            return "upload"
        elif path in ["/health", "/status", "/api/status"]:
            return "health"
        elif path.startswith("/api/"):
            return "api"
        else:
            return "api"  # Default category
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for whitelisted IPs in development
        client_ip = request.client.host if request.client else "unknown"
        if client_ip in self.whitelist_ips:
            return await call_next(request)
        
        # Get client identifier and endpoint category
        client_id = self._get_client_identifier(request)
        category = self._get_endpoint_category(request.url.path)
        
        try:
            # Check global rate limit first
            global_allowed, global_retry_after = await self.global_limiter.is_allowed(client_id)
            if not global_allowed:
                logger.warning(f"Global rate limit exceeded for {client_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests globally",
                    headers={"Retry-After": str(int(global_retry_after or 60))}
                )
            
            # Check category-specific rate limit
            limiter = self.limiters.get(category, self.limiters['api'])
            allowed, retry_after = await limiter.is_allowed(f"{client_id}:{category}")
            
            if not allowed:
                logger.warning(f"Rate limit exceeded for {client_id} on {category} endpoints")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests for {category} endpoints",
                    headers={"Retry-After": str(int(retry_after or 60))}
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            remaining = limiter.max_requests - len(limiter.requests[f"{client_id}:{category}"])
            response.headers["X-RateLimit-Limit"] = str(limiter.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + limiter.window_seconds))
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # If rate limiting fails, allow the request to proceed
            return await call_next(request)

# Factory function for easy integration
def create_rate_limit_middleware():
    """Create rate limiting middleware instance"""
    return RateLimitMiddleware