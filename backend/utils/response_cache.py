"""
Simple response caching for faster LLM responses
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional
from config.settings import config

class ResponseCache:
    """Simple in-memory cache for LLM responses"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, query: str, financial_context: str) -> str:
        """Generate cache key from query and context"""
        content = f"{query}_{financial_context}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, query: str, financial_context: str = "") -> Optional[str]:
        """Get cached response if available and not expired"""
        if not config.ENABLE_RESPONSE_CACHING:
            return None
            
        key = self._generate_key(query, financial_context)
        
        if key in self._cache:
            cache_entry = self._cache[key]
            if time.time() - cache_entry['timestamp'] < config.CACHE_TTL_SECONDS:
                return cache_entry['response']
            else:
                # Remove expired entry
                del self._cache[key]
        
        return None
    
    def set(self, query: str, response: str, financial_context: str = ""):
        """Cache response"""
        if not config.ENABLE_RESPONSE_CACHING:
            return
            
        key = self._generate_key(query, financial_context)
        self._cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def clear(self):
        """Clear all cached responses"""
        self._cache.clear()
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time - entry['timestamp'] >= config.CACHE_TTL_SECONDS
        ]
        
        for key in expired_keys:
            del self._cache[key]

# Global cache instance
response_cache = ResponseCache()