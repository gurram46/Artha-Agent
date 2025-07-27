#!/usr/bin/env python3
"""
Cache Manager for Investment Agent
Provides high-level cache management and data population functions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .market_cache import market_cache, get_default_market_data

logger = logging.getLogger(__name__)

class CacheManager:
    """High-level cache management for investment agent"""
    
    def __init__(self):
        """Initialize cache manager"""
        self.cache = market_cache
        logger.info("Cache manager initialized")
    
    def populate_default_cache(self):
        """Populate cache with default market data for fast startup"""
        try:
            default_data = get_default_market_data()
            
            for cache_type, data in default_data.items():
                self.cache.set_cached_data(cache_type, data)
                logger.info(f"Populated default cache for {cache_type}")
            
            logger.info("Default cache population completed")
            return True
            
        except Exception as e:
            logger.error(f"Error populating default cache: {e}")
            return False
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview with fallback to defaults"""
        cached_data = self.cache.get_cached_data('market_overview')
        
        if cached_data:
            return cached_data
        
        # Fallback to default data
        logger.warning("Using default market overview data")
        default_data = get_default_market_data()['market_overview']
        self.cache.set_cached_data('market_overview', default_data)
        return default_data
    
    def get_top_funds(self, fund_type: Optional[str] = None) -> Dict[str, List]:
        """Get top funds data with optional filtering"""
        cached_data = self.cache.get_cached_data('top_funds')
        
        if not cached_data:
            logger.warning("Using default funds data")
            default_data = get_default_market_data()['top_funds']
            self.cache.set_cached_data('top_funds', default_data)
            cached_data = default_data
        
        if fund_type and fund_type in cached_data:
            return {fund_type: cached_data[fund_type]}
        
        return cached_data
    
    def get_top_stocks(self, stock_type: Optional[str] = None) -> Dict[str, List]:
        """Get top stocks data with optional filtering"""
        cached_data = self.cache.get_cached_data('top_stocks')
        
        if not cached_data:
            logger.warning("Using default stocks data")
            default_data = get_default_market_data()['top_stocks']
            self.cache.set_cached_data('top_stocks', default_data)
            cached_data = default_data
        
        if stock_type and stock_type in cached_data:
            return {stock_type: cached_data[stock_type]}
        
        return cached_data
    
    def get_gold_data(self) -> Dict[str, Any]:
        """Get gold market data"""
        cached_data = self.cache.get_cached_data('gold_data')
        
        if not cached_data:
            logger.warning("Using default gold data")
            default_data = get_default_market_data()['gold_data']
            self.cache.set_cached_data('gold_data', default_data)
            cached_data = default_data
        
        return cached_data
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """Get economic indicators data"""
        cached_data = self.cache.get_cached_data('economic_data')
        
        if not cached_data:
            logger.warning("Using default economic data")
            default_data = get_default_market_data()['economic_data']
            self.cache.set_cached_data('economic_data', default_data)
            cached_data = default_data
        
        return cached_data
    
    def generate_market_summary(self) -> str:
        """Generate a comprehensive market summary from cached data"""
        try:
            market_overview = self.get_market_overview()
            top_funds = self.get_top_funds()
            top_stocks = self.get_top_stocks()
            gold_data = self.get_gold_data()
            economic_data = self.get_economic_indicators()
            
            summary = f"""
## Market Overview (Cached Data - {datetime.now().strftime('%Y-%m-%d %H:%M')})

### Current Market Status
- **Nifty 50**: {market_overview['nifty_50']['value']} ({market_overview['nifty_50']['change']})
- **Sensex**: {market_overview['sensex']['value']} ({market_overview['sensex']['change']})
- **Bank Nifty**: {market_overview['bank_nifty']['value']} ({market_overview['bank_nifty']['change']})
- **Market Status**: {market_overview['market_status']}

### Top Performing Funds
**Large Cap Funds:**
"""
            
            for fund in top_funds.get('large_cap', [])[:3]:
                summary += f"- {fund['name']}: NAV ₹{fund['nav']}, 1Y Return: {fund['returns_1y']}%\n"
            
            summary += "\n**Mid Cap Funds:**\n"
            for fund in top_funds.get('mid_cap', [])[:2]:
                summary += f"- {fund['name']}: NAV ₹{fund['nav']}, 1Y Return: {fund['returns_1y']}%\n"
            
            summary += "\n**ELSS Funds (Tax Saving):**\n"
            for fund in top_funds.get('elss', [])[:2]:
                summary += f"- {fund['name']}: NAV ₹{fund['nav']}, 1Y Return: {fund['returns_1y']}%\n"
            
            summary += f"""
### Top Stocks
**Large Cap Stocks:**
"""
            for stock in top_stocks.get('large_cap', [])[:5]:
                summary += f"- {stock['symbol']}: ₹{stock['price']} ({stock['change']})\n"
            
            summary += f"""
### Gold Investment
- **Spot Price**: ₹{gold_data['spot_price']} per 10g ({gold_data['change']})
- **Top Gold ETFs**:
"""
            for etf in gold_data.get('etfs', []):
                summary += f"  - {etf['name']}: NAV ₹{etf['nav']} ({etf['change']})\n"
            
            summary += f"""
### Economic Indicators
- **Inflation**: {economic_data['inflation']}%
- **Repo Rate**: {economic_data['repo_rate']}%
- **GDP Growth**: {economic_data['gdp_growth']}%
- **Fiscal Deficit**: {economic_data['fiscal_deficit']}%

*Data cached for fast response. Live data integration available through Angel One APIs.*
"""
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return "Error generating market summary from cached data."
    
    def update_cache_from_api(self, api_data: Dict[str, Any]):
        """Update cache with fresh API data"""
        try:
            # Map API data to cache structure
            if 'market_data' in api_data:
                self.cache.set_cached_data('market_overview', api_data['market_data'])
            
            if 'funds_data' in api_data:
                self.cache.set_cached_data('top_funds', api_data['funds_data'])
            
            if 'stocks_data' in api_data:
                self.cache.set_cached_data('top_stocks', api_data['stocks_data'])
            
            if 'gold_data' in api_data:
                self.cache.set_cached_data('gold_data', api_data['gold_data'])
            
            logger.info("Cache updated with fresh API data")
            return True
            
        except Exception as e:
            logger.error(f"Error updating cache from API: {e}")
            return False
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status for all cache types"""
        return self.cache.get_cache_status()
        
    def get_cache_status_report(self) -> str:
        """Generate a human-readable cache status report"""
        status = self.cache.get_cache_status()
        
        report = "## Market Data Cache Status\n\n"
        
        for cache_type, info in status.items():
            if info.get('exists'):
                if info.get('valid'):
                    report += f"✅ **{cache_type}**: Valid ({info['age_minutes']}min old)\n"
                else:
                    report += f"⚠️ **{cache_type}**: Expired ({info['age_minutes']}min old)\n"
            else:
                report += f"❌ **{cache_type}**: Not cached\n"
        
        report += f"\n*Cache checked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        return report
    
    def clear_all_cache(self):
        """Clear all cached data"""
        self.cache.clear_cache()
        logger.info("All cache cleared")
    
    def warm_up_cache(self):
        """Warm up cache with default data for immediate availability"""
        if not any(self.cache.get_cache_status().values()):
            logger.info("Cache empty, warming up with default data")
            self.populate_default_cache()
        else:
            logger.info("Cache already contains data")


# Global cache manager instance
cache_manager = CacheManager()

# Convenience functions for easy import
def get_cached_market_summary() -> str:
    """Get cached market summary - main function for agents to use"""
    return cache_manager.generate_market_summary()

def get_cached_funds(fund_type: str = None) -> Dict:
    """Get cached funds data"""
    return cache_manager.get_top_funds(fund_type)

def get_cached_stocks(stock_type: str = None) -> Dict:
    """Get cached stocks data"""
    return cache_manager.get_top_stocks(stock_type)

def warm_up_cache():
    """Warm up cache for immediate use"""
    cache_manager.warm_up_cache()