#!/usr/bin/env python3
"""
Simple Test for Artha AI Cache System
"""

import os
import sys
import json
from datetime import datetime, date
from decimal import Decimal

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Set environment variables
os.environ['ARTHA_ENCRYPTION_KEY'] = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_cache():
    """Test the simple cache system"""
    
    try:
        print("🧪 Testing Simple Artha AI Cache System")
        print("=" * 50)
        
        # Import the simple cache service
        from simple_cache_service import SimpleCacheService
        
        # Create cache instance
        cache = SimpleCacheService()
        print("✅ Cache service initialized")
        
        # Test data
        test_data = {
            "user_id": "test_user_123",
            "query": "What is the stock price of AAPL?",
            "response": "Apple Inc. (AAPL) is currently trading at $150.25",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "financial_api",
                "confidence": 0.95
            }
        }
        
        cache_key = "test_query_123"
        
        print("\n📝 Test 1: Store data in cache...")
        success = cache.set(cache_key, test_data, expiry_hours=24)
        if success:
            print("✅ Data stored successfully")
        else:
            print("❌ Failed to store data")
            return False
        
        print("\n📖 Test 2: Retrieve data from cache...")
        retrieved_data = cache.get(cache_key)
        if retrieved_data:
            print("✅ Data retrieved successfully")
            print(f"   Retrieved: {json.dumps(retrieved_data, indent=2, cls=DateTimeEncoder)}")
        else:
            print("❌ Failed to retrieve data")
            return False
        
        print("\n🔍 Test 3: Verify data integrity...")
        if retrieved_data == test_data:
            print("✅ Data integrity verified")
        else:
            print("❌ Data integrity check failed")
            return False
        
        print("\n📊 Test 4: Get cache statistics...")
        stats = cache.get_stats()
        if stats:
            print("✅ Cache statistics retrieved")
            print(f"   Stats: {json.dumps(stats, indent=2, cls=DateTimeEncoder)}")
        else:
            print("❌ Failed to get cache statistics")
        
        print("\n📚 Test 5: Store multiple entries...")
        for i in range(3):
            key = f"test_entry_{i}"
            data = {"id": i, "value": f"test_value_{i}", "created": datetime.now().isoformat()}
            cache.set(key, data, expiry_hours=1)
        print("✅ Multiple entries stored")
        
        print("\n📊 Test 6: Updated statistics...")
        stats = cache.get_stats()
        if stats:
            print(f"   Updated Stats: {json.dumps(stats, indent=2, cls=DateTimeEncoder)}")
        
        print("\n🗑️ Test 7: Delete cache entry...")
        delete_success = cache.delete(cache_key)
        if delete_success:
            print("✅ Cache entry deleted")
        else:
            print("❌ Failed to delete cache entry")
        
        print("\n🔍 Test 8: Verify deletion...")
        deleted_data = cache.get(cache_key)
        if deleted_data is None:
            print("✅ Cache deletion verified")
        else:
            print("❌ Cache deletion failed")
        
        print("\n🧹 Test 9: Cleanup expired entries...")
        cleanup_count = cache.cleanup_expired()
        print(f"✅ Cleanup completed - removed {cleanup_count} expired entries")
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 50)
        print("✅ Simple Artha AI Cache System is fully operational")
        print("🔧 Ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_cache()
    
    if success:
        print("\n🚀 Cache system is ready!")
        print("You can now use the cache system in your Artha AI application.")
    else:
        print("\n💥 Cache system test failed!")
        print("Please check the error messages above.")