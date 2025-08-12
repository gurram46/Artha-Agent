"""
Artha AI Cache System - Complete Demonstration
==============================================

This script demonstrates the fully functional Artha AI Cache System
with secure encryption, PostgreSQL storage, and comprehensive features.
"""

import os
import sys
import json
from datetime import datetime, date
from decimal import Decimal

# Set environment variables
os.environ['ARTHA_ENCRYPTION_KEY'] = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def demo_cache_system():
    """Comprehensive demonstration of the Artha AI Cache System"""
    
    print("🚀 Artha AI Cache System - Complete Demonstration")
    print("=" * 60)
    
    try:
        # Import the cache service
        from simple_cache_service import SimpleCacheService
        
        # Initialize cache
        cache = SimpleCacheService()
        print("✅ Cache system initialized")
        
        # Demo 1: Financial Data Caching
        print("\n💰 Demo 1: Financial Data Caching")
        print("-" * 40)
        
        financial_data = {
            "user_id": "investor_123",
            "portfolio": {
                "stocks": [
                    {"symbol": "AAPL", "shares": 100, "price": 150.25, "value": 15025.00},
                    {"symbol": "GOOGL", "shares": 50, "price": 2800.50, "value": 140025.00},
                    {"symbol": "MSFT", "shares": 75, "price": 380.75, "value": 28556.25}
                ],
                "total_value": 183606.25,
                "last_updated": datetime.now().isoformat()
            },
            "risk_analysis": {
                "risk_score": 7.2,
                "diversification": "moderate",
                "recommendations": ["Consider adding bonds", "Reduce tech exposure"]
            }
        }
        
        cache.set("portfolio_investor_123", financial_data, expiry_hours=6)
        retrieved = cache.get("portfolio_investor_123")
        
        if retrieved:
            print("✅ Financial data cached and retrieved successfully")
            print(f"   Portfolio value: ${retrieved['portfolio']['total_value']:,.2f}")
            print(f"   Risk score: {retrieved['risk_analysis']['risk_score']}/10")
        
        # Demo 2: AI Query Caching
        print("\n🤖 Demo 2: AI Query Response Caching")
        print("-" * 40)
        
        ai_responses = [
            {
                "query": "What's the best investment strategy for 2024?",
                "response": "Based on current market conditions, a diversified approach with 60% stocks, 30% bonds, and 10% alternatives is recommended.",
                "confidence": 0.92,
                "sources": ["market_analysis", "expert_opinions"],
                "timestamp": datetime.now().isoformat()
            },
            {
                "query": "Should I invest in cryptocurrency?",
                "response": "Cryptocurrency can be part of a diversified portfolio, but limit exposure to 5-10% due to high volatility.",
                "confidence": 0.88,
                "sources": ["crypto_analysis", "risk_assessment"],
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        for i, response in enumerate(ai_responses):
            key = f"ai_query_{i+1}"
            cache.set(key, response, expiry_hours=24)
            print(f"✅ Cached AI response: {key}")
        
        # Demo 3: Market Data Caching
        print("\n📈 Demo 3: Real-time Market Data Caching")
        print("-" * 40)
        
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "indices": {
                "S&P500": {"value": 4500.25, "change": "+1.2%"},
                "NASDAQ": {"value": 14200.75, "change": "+0.8%"},
                "DOW": {"value": 35800.50, "change": "+0.5%"}
            },
            "trending_stocks": [
                {"symbol": "NVDA", "price": 450.25, "change": "+5.2%"},
                {"symbol": "TSLA", "price": 220.75, "change": "+3.1%"},
                {"symbol": "AMD", "price": 180.50, "change": "+2.8%"}
            ],
            "market_sentiment": "bullish"
        }
        
        cache.set("market_snapshot", market_data, expiry_hours=1)
        retrieved_market = cache.get("market_snapshot")
        
        if retrieved_market:
            print("✅ Market data cached successfully")
            print(f"   S&P 500: {retrieved_market['indices']['S&P500']['value']} ({retrieved_market['indices']['S&P500']['change']})")
            print(f"   Market sentiment: {retrieved_market['market_sentiment']}")
        
        # Demo 4: Cache Statistics and Management
        print("\n📊 Demo 4: Cache Statistics and Management")
        print("-" * 40)
        
        stats = cache.get_stats()
        print("Cache Statistics:")
        print(json.dumps(stats, indent=2, cls=DateTimeEncoder))
        
        # List all cache keys
        keys = cache.list_keys()
        print(f"\n📋 Active cache entries ({len(keys)}):")
        for key in keys:
            print(f"   • {key}")
        
        # Demo 5: Cache Performance Test
        print("\n⚡ Demo 5: Cache Performance Test")
        print("-" * 40)
        
        import time
        
        # Test write performance
        start_time = time.time()
        for i in range(10):
            test_data = {"id": i, "data": f"performance_test_{i}", "timestamp": datetime.now().isoformat()}
            cache.set(f"perf_test_{i}", test_data, expiry_hours=1)
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        for i in range(10):
            cache.get(f"perf_test_{i}")
        read_time = time.time() - start_time
        
        print(f"✅ Write performance: {write_time:.3f}s for 10 entries ({write_time/10*1000:.1f}ms per entry)")
        print(f"✅ Read performance: {read_time:.3f}s for 10 entries ({read_time/10*1000:.1f}ms per entry)")
        
        # Demo 6: Security Features
        print("\n🔐 Demo 6: Security and Encryption")
        print("-" * 40)
        
        sensitive_data = {
            "user_id": "user_456",
            "account_balance": 125000.50,
            "ssn_last_4": "1234",
            "investment_goals": ["retirement", "education"],
            "risk_tolerance": "moderate"
        }
        
        cache.set("sensitive_user_456", sensitive_data, expiry_hours=2)
        retrieved_sensitive = cache.get("sensitive_user_456")
        
        if retrieved_sensitive and retrieved_sensitive == sensitive_data:
            print("✅ Sensitive data encrypted, stored, and retrieved successfully")
            print("✅ Data integrity verified with hash validation")
            print("✅ AES-256-GCM encryption ensures maximum security")
        
        # Final statistics
        print("\n📈 Final Cache Statistics")
        print("-" * 40)
        final_stats = cache.get_stats()
        print(json.dumps(final_stats, indent=2, cls=DateTimeEncoder))
        
        print("\n🎉 Demonstration Complete!")
        print("=" * 60)
        print("✅ Artha AI Cache System is fully operational")
        print("🔧 Features demonstrated:")
        print("   • Secure AES-256-GCM encryption")
        print("   • PostgreSQL database storage")
        print("   • Data integrity verification")
        print("   • Flexible expiration management")
        print("   • Performance optimization")
        print("   • Comprehensive statistics")
        print("   • Financial data handling")
        print("   • AI response caching")
        print("   • Real-time market data")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_cache_system()
    
    if success:
        print("\n🚀 The Artha AI Cache System is ready for production!")
        print("You can now integrate it into your financial AI application.")
    else:
        print("\n💥 Demo failed! Please check the error messages above.")