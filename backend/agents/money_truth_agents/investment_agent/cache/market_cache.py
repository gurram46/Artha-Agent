#!/usr/bin/env python3
"""
Market Data Caching System for Investment Agent
Provides fast access to commonly used market data to improve response times
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MarketDataCache:
    """Handles caching of market data to improve agent response times"""
    
    def __init__(self, cache_dir: str = "investment_agent/cache/data"):
        """
        Initialize the market data cache
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache expiry times (in minutes)
        self.cache_expiry = {
            'market_overview': 30,      # Market indices, status
            'top_funds': 60,           # Popular mutual funds
            'top_stocks': 30,          # Popular stocks with prices
            'economic_data': 120,      # Economic indicators
            'sector_analysis': 60,     # Sector performance
            'gold_data': 30,           # Gold prices and ETFs
            'market_news': 15,         # Recent market news
        }
        
        logger.info(f"Market cache initialized at {self.cache_dir}")
    
    def _get_cache_file(self, cache_type: str) -> Path:
        """Get cache file path for given cache type"""
        return self.cache_dir / f"{cache_type}.json"
    
    def _is_cache_valid(self, cache_type: str) -> bool:
        """Check if cache is still valid based on expiry time"""
        cache_file = self._get_cache_file(cache_type)
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            timestamp = data.get('timestamp', 0)
            cache_age_minutes = (time.time() - timestamp) / 60
            max_age = self.cache_expiry.get(cache_type, 30)
            
            is_valid = cache_age_minutes < max_age
            logger.debug(f"Cache {cache_type}: age={cache_age_minutes:.1f}min, max={max_age}min, valid={is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Error checking cache validity for {cache_type}: {e}")
            return False
    
    def get_cached_data(self, cache_type: str) -> Optional[Dict]:
        """
        Get cached data if available and valid
        
        Args:
            cache_type: Type of cache to retrieve
            
        Returns:
            Cached data or None if not available/expired
        """
        if not self._is_cache_valid(cache_type):
            logger.debug(f"Cache miss for {cache_type}")
            return None
        
        try:
            cache_file = self._get_cache_file(cache_type)
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Cache hit for {cache_type}")
            return data.get('data')
            
        except Exception as e:
            logger.error(f"Error reading cache for {cache_type}: {e}")
            return None
    
    def set_cached_data(self, cache_type: str, data: Dict) -> bool:
        """
        Store data in cache with current timestamp
        
        Args:
            cache_type: Type of cache to store
            data: Data to cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_data = {
                'timestamp': time.time(),
                'cache_type': cache_type,
                'expiry_minutes': self.cache_expiry.get(cache_type, 30),
                'data': data
            }
            
            cache_file = self._get_cache_file(cache_type)
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            logger.info(f"Cached data for {cache_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching data for {cache_type}: {e}")
            return False
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """
        Clear cache files
        
        Args:
            cache_type: Specific cache to clear, or None to clear all
        """
        if cache_type:
            cache_file = self._get_cache_file(cache_type)
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"Cleared cache for {cache_type}")
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cleared all cache files")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get status of all cache types"""
        status = {}
        
        for cache_type in self.cache_expiry.keys():
            cache_file = self._get_cache_file(cache_type)
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    
                    timestamp = data.get('timestamp', 0)
                    age_minutes = (time.time() - timestamp) / 60
                    is_valid = self._is_cache_valid(cache_type)
                    
                    status[cache_type] = {
                        'exists': True,
                        'age_minutes': round(age_minutes, 1),
                        'valid': is_valid,
                        'expiry_minutes': self.cache_expiry[cache_type]
                    }
                except:
                    status[cache_type] = {'exists': True, 'error': 'Cannot read cache file'}
            else:
                status[cache_type] = {'exists': False}
        
        return status


# Create default market data templates for common scenarios
def get_default_market_data():
    """Get default market data structure for initial cache population"""
    return {
        'market_overview': {
            'nifty_50': {'value': 24500, 'change': '+0.5%', 'status': 'open'},
            'sensex': {'value': 80500, 'change': '+0.3%', 'status': 'open'},
            'bank_nifty': {'value': 51200, 'change': '+0.8%', 'status': 'open'},
            'market_status': 'open',
            'volatility': 'moderate'
        },
        
        'top_funds': {
            'large_cap': [
                {'name': 'SBI Large Cap Fund', 'nav': 65.23, 'returns_1y': 12.5, 'rating': 4},
                {'name': 'HDFC Top 100 Fund', 'nav': 58.45, 'returns_1y': 11.8, 'rating': 4},
                {'name': 'ICICI Pru Bluechip Fund', 'nav': 52.34, 'returns_1y': 13.2, 'rating': 5}
            ],
            'mid_cap': [
                {'name': 'SBI Mid Cap Fund', 'nav': 45.67, 'returns_1y': 18.5, 'rating': 4},
                {'name': 'HDFC Mid-Cap Fund', 'nav': 67.89, 'returns_1y': 16.8, 'rating': 4}
            ],
            'elss': [
                {'name': 'Axis Long Term Equity Fund', 'nav': 42.34, 'returns_1y': 14.5, 'rating': 5},
                {'name': 'SBI Long Term Equity Fund', 'nav': 38.92, 'returns_1y': 13.8, 'rating': 4}
            ]
        },
        
        'top_stocks': {
            'large_cap': [
                {'symbol': 'RELIANCE', 'price': 2850, 'change': '+1.2%', 'market_cap': 'Large'},
                {'symbol': 'TCS', 'price': 3920, 'change': '+0.8%', 'market_cap': 'Large'},
                {'symbol': 'INFY', 'price': 1850, 'change': '+0.5%', 'market_cap': 'Large'},
                {'symbol': 'HDFCBANK', 'price': 1720, 'change': '+0.3%', 'market_cap': 'Large'},
                {'symbol': 'ICICIBANK', 'price': 1280, 'change': '+0.9%', 'market_cap': 'Large'}
            ],
            'mid_cap': [
                {'symbol': 'LICI', 'price': 920, 'change': '+2.1%', 'market_cap': 'Mid'},
                {'symbol': 'FEDERALBNK', 'price': 185, 'change': '+1.5%', 'market_cap': 'Mid'}
            ]
        },
        
        'gold_data': {
            'spot_price': 72500,
            'change': '+0.3%',
            'etfs': [
                {'name': 'SBI Gold ETF', 'nav': 47.23, 'change': '+0.2%'},
                {'name': 'HDFC Gold ETF', 'nav': 46.89, 'change': '+0.3%'}
            ]
        },
        
        'economic_data': {
            'inflation': 4.8,
            'repo_rate': 6.5,
            'gdp_growth': 7.2,
            'fiscal_deficit': 5.8
        }
    }


# Global cache instance
market_cache = MarketDataCache()