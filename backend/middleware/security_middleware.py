"""
Comprehensive Security Middleware for Artha AI
==============================================

This middleware implements multiple security layers to protect against common vulnerabilities.
"""

import os
import re
import time
import hashlib
import logging
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration settings"""
    
    def __init__(self):
        # Rate limiting configuration
        self.rate_limits = {
            'auth': {'requests': 10, 'window': 60},  # 10 requests per minute for auth
            'api': {'requests': 100, 'window': 60},   # 100 requests per minute for API
            'chat': {'requests': 30, 'window': 60},   # 30 requests per minute for chat
            'upload': {'requests': 5, 'window': 60},  # 5 requests per minute for uploads
            'global': {'requests': 500, 'window': 60} # 500 total requests per minute
        }
        
        # Security headers - Modified for frontend compatibility
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',  # Changed from DENY to SAMEORIGIN for better compatibility
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            # More permissive CSP for development - allows localStorage, eval, and inline scripts
            'Content-Security-Policy': "default-src 'self' 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval' localhost:* 127.0.0.1:*; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https: blob:; font-src 'self' https: data:; connect-src 'self' https: ws: wss: localhost:* 127.0.0.1:*; frame-ancestors 'self';",
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        # Input validation patterns
        self.malicious_patterns = [
            # SQL Injection patterns
            r"(?i)(union\s+select|select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from)",
            r"(?i)(drop\s+table|alter\s+table|create\s+table|truncate\s+table)",
            r"(?i)(\'\s*or\s+\'\d+\'\s*=\s*\'\d+|\'\s*or\s+\d+\s*=\s*\d+)",
            r"(?i)(exec\s*\(|execute\s*\(|sp_executesql)",
            
            # XSS patterns
            r"(?i)(<script[^>]*>|</script>|javascript:|vbscript:|onload=|onerror=)",
            r"(?i)(alert\s*\(|confirm\s*\(|prompt\s*\(|eval\s*\()",
            r"(?i)(<iframe|<object|<embed|<applet)",
            
            # Command injection patterns
            r"(?i)(;\s*rm\s+|;\s*cat\s+|;\s*ls\s+|;\s*pwd|;\s*whoami)",
            r"(?i)(\|\s*nc\s+|\|\s*netcat\s+|\|\s*wget\s+|\|\s*curl\s+)",
            r"(?i)(&&\s*rm\s+|&&\s*cat\s+|&&\s*ls\s+)",
            
            # Path traversal patterns
            r"(?i)(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
            r"(?i)(\/etc\/passwd|\/etc\/shadow|\/proc\/|\/sys\/)",
            
            # LDAP injection patterns
            r"(?i)(\*\)\(|\)\(.*\*|\(\||\)\&)",
            
            # NoSQL injection patterns
            r"(?i)(\$where|\$ne|\$gt|\$lt|\$regex|\$or|\$and)",
        ]
        
        self.compiled_patterns = [re.compile(pattern) for pattern in self.malicious_patterns]
        
        # Blocked user agents (bots, scanners)
        self.blocked_user_agents = [
            r"(?i)(sqlmap|nikto|nmap|masscan|zap|burp|acunetix)",
            r"(?i)(nessus|openvas|w3af|skipfish|wpscan)",
            r"(?i)(python-requests|curl|wget|libwww|lwp-trivial)",
        ]
        
        self.compiled_user_agents = [re.compile(pattern) for pattern in self.blocked_user_agents]

class RateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.requests: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_ips: Set[str] = set()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP with proxy support"""
        # Check for forwarded headers (in order of preference)
        forwarded_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'CF-Connecting-IP',  # Cloudflare
            'X-Client-IP',
            'X-Forwarded'
        ]
        
        for header in forwarded_headers:
            if header in request.headers:
                ip = request.headers[header].split(',')[0].strip()
                if self._is_valid_ip(ip):
                    return ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Determine rate limit category based on endpoint"""
        path = request.url.path.lower()
        
        if any(auth_path in path for auth_path in ['/auth/', '/login', '/register', '/token']):
            return 'auth'
        elif any(upload_path in path for upload_path in ['/upload', '/file']):
            return 'upload'
        elif any(chat_path in path for chat_path in ['/chat', '/stream', '/ai']):
            return 'chat'
        else:
            return 'api'
    
    def is_rate_limited(self, request: Request) -> tuple[bool, Optional[str]]:
        """Check if request should be rate limited"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Check if IP is temporarily blocked
        if client_ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[client_ip]:
                return True, f"IP {client_ip} is temporarily blocked"
            else:
                del self.blocked_ips[client_ip]
        
        # Get rate limit category
        category = self._get_rate_limit_key(request)
        limit_config = self.config.rate_limits[category]
        
        # Clean old requests
        cutoff_time = current_time - limit_config['window']
        request_times = self.requests[client_ip][category]
        
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Check category-specific limit
        if len(request_times) >= limit_config['requests']:
            self._mark_suspicious(client_ip)
            return True, f"Rate limit exceeded for {category}: {limit_config['requests']} requests per {limit_config['window']} seconds"
        
        # Check global limit
        global_config = self.config.rate_limits['global']
        global_cutoff = current_time - global_config['window']
        total_requests = 0
        
        for cat_requests in self.requests[client_ip].values():
            total_requests += sum(1 for req_time in cat_requests if req_time > global_cutoff)
        
        if total_requests >= global_config['requests']:
            self._mark_suspicious(client_ip)
            return True, f"Global rate limit exceeded: {global_config['requests']} requests per {global_config['window']} seconds"
        
        # Record this request
        request_times.append(current_time)
        return False, None
    
    def _mark_suspicious(self, ip: str):
        """Mark IP as suspicious and potentially block it"""
        self.suspicious_ips.add(ip)
        
        # Block IP for repeated violations
        violation_count = sum(1 for cat_requests in self.requests[ip].values() 
                            for req_time in cat_requests 
                            if time.time() - req_time < 300)  # Last 5 minutes
        
        if violation_count > 50:  # More than 50 requests in 5 minutes
            self.blocked_ips[ip] = datetime.now() + timedelta(minutes=30)
            logger.warning(f"Blocked IP {ip} for 30 minutes due to excessive requests")

class InputValidator:
    """Advanced input validation and sanitization"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def validate_request(self, request: Request, body: bytes = None) -> tuple[bool, Optional[str]]:
        """Validate entire request for malicious content"""
        # Validate URL parameters
        for param, value in request.query_params.items():
            if self._contains_malicious_content(str(value)):
                return False, f"Malicious content detected in parameter: {param}"
        
        # Validate headers
        for header, value in request.headers.items():
            if self._contains_malicious_content(str(value)):
                return False, f"Malicious content detected in header: {header}"
        
        # Validate request body if present
        if body:
            try:
                body_str = body.decode('utf-8', errors='ignore')
                if self._contains_malicious_content(body_str):
                    return False, "Malicious content detected in request body"
            except Exception:
                pass  # Skip validation for non-text content
        
        return True, None
    
    def _contains_malicious_content(self, content: str) -> bool:
        """Check if content contains malicious patterns"""
        if not content or len(content) > 10000:  # Skip very large content
            return False
        
        for pattern in self.config.compiled_patterns:
            if pattern.search(content):
                return True
        
        return False
    
    def sanitize_input(self, data: str) -> str:
        """Sanitize input data"""
        if not isinstance(data, str):
            return data
        
        # Remove null bytes
        data = data.replace('\x00', '')
        
        # Limit length
        if len(data) > 10000:
            data = data[:10000]
        
        # Basic HTML entity encoding for display
        data = data.replace('&', '&amp;')
        data = data.replace('<', '&lt;')
        data = data.replace('>', '&gt;')
        data = data.replace('"', '&quot;')
        data = data.replace("'", '&#x27;')
        
        return data

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    def __init__(self, app, config: Optional[SecurityConfig] = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.input_validator = InputValidator(self.config)
        
        # JWT configuration
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'artha_ai_jwt_secret_2024_secure')
        self.security_bearer = HTTPBearer(auto_error=False)
    
    async def dispatch(self, request: Request, call_next):
        """Main security middleware dispatch"""
        start_time = time.time()
        
        try:
            # 1. Check user agent
            user_agent = request.headers.get('user-agent', '')
            if self._is_blocked_user_agent(user_agent):
                logger.warning(f"Blocked request from suspicious user agent: {user_agent}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            
            # 2. Rate limiting
            is_limited, limit_message = self.rate_limiter.is_rate_limited(request)
            if is_limited:
                logger.warning(f"Rate limit exceeded: {limit_message}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # 3. Input validation
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                body = await request.body()
                # Reset body for downstream processing
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            
            is_valid, validation_message = self.input_validator.validate_request(request, body)
            if not is_valid:
                logger.warning(f"Input validation failed: {validation_message}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            # 4. Process request
            response = await call_next(request)
            
            # 5. Add security headers
            for header, value in self.config.security_headers.items():
                response.headers[header] = value
            
            # 6. Add timing header for monitoring
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def _is_blocked_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is blocked"""
        for pattern in self.config.compiled_user_agents:
            if pattern.search(user_agent):
                return True
        return False
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None

# Utility functions for manual security checks
def check_sql_injection(query: str) -> bool:
    """Check if query contains SQL injection patterns"""
    config = SecurityConfig()
    validator = InputValidator(config)
    return validator._contains_malicious_content(query)

def sanitize_user_input(data: str) -> str:
    """Sanitize user input"""
    config = SecurityConfig()
    validator = InputValidator(config)
    return validator.sanitize_input(data)

def get_client_ip_from_request(request: Request) -> str:
    """Extract client IP from request"""
    config = SecurityConfig()
    limiter = RateLimiter(config)
    return limiter._get_client_ip(request)