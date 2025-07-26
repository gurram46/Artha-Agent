"""
Investment Agent Cache Module

Provides fast market data caching to improve response times from 4+ minutes to under 2 minutes.
"""

from .market_cache import market_cache, MarketDataCache
from .cache_manager import (
    cache_manager, 
    CacheManager,
    get_cached_market_summary,
    get_cached_funds,
    get_cached_stocks,
    warm_up_cache
)

__all__ = [
    'market_cache',
    'MarketDataCache', 
    'cache_manager',
    'CacheManager',
    'get_cached_market_summary',
    'get_cached_funds', 
    'get_cached_stocks',
    'warm_up_cache'
]