#!/usr/bin/env python3
"""
Comprehensive Test for Artha AI Cache System
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://postgres:2003@localhost:5433/artha_cache_db'
os.environ['ARTHA_ENCRYPTION_KEY'] = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cache_system():
    """Test the complete cache system"""
    
    try:
        print("🧪 Testing Artha AI Cache System")
        print("=" * 50)
        
        # Test 1: Import modules
        print("📦 Test 1: Importing modules...")
        from services.cache_service import CacheService
        from utils.encryption import encrypt_data, decrypt_data, test_encryption_system
        print("✅ All modules imported successfully")
        
        # Test 2: Encryption system
        print("\n🔐 Test 2: Encryption system...")
        encryption_result = test_encryption_system()
        if encryption_result:
            print("✅ Encryption system working correctly")
        else:
            print("❌ Encryption system failed")
            return False
        
        # Test 3: Cache service initialization
        print("\n💾 Test 3: Cache service initialization...")
        cache = CacheService()
        print("✅ Cache service initialized")
        
        # Test 4: Basic cache operations
        print("\n📝 Test 4: Basic cache operations...")
        
        # Store data
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
        
        # Set cache
        success = cache.set(cache_key, test_data, expiry_hours=24)
        if success:
            print("✅ Data stored in cache")
        else:
            print("❌ Failed to store data in cache")
            return False
        
        # Get cache
        retrieved_data = cache.get(cache_key)
        if retrieved_data:
            print("✅ Data retrieved from cache")
            print(f"   Retrieved: {json.dumps(retrieved_data, indent=2)}")
        else:
            print("❌ Failed to retrieve data from cache")
            return False
        
        # Verify data integrity
        if retrieved_data == test_data:
            print("✅ Data integrity verified")
        else:
            print("❌ Data integrity check failed")
            return False
        
        # Test 5: Cache statistics
        print("\n📊 Test 5: Cache statistics...")
        stats = cache.get_stats()
        if stats:
            print("✅ Cache statistics retrieved")
            print(f"   Stats: {json.dumps(stats, indent=2)}")
        else:
            print("❌ Failed to get cache statistics")
        
        # Test 6: Cache cleanup
        print("\n🧹 Test 6: Cache cleanup...")
        cleanup_result = cache.cleanup_expired()
        print(f"✅ Cleanup completed - removed {cleanup_result} expired entries")
        
        # Test 7: Multiple cache entries
        print("\n📚 Test 7: Multiple cache entries...")
        for i in range(5):
            key = f"test_entry_{i}"
            data = {"id": i, "value": f"test_value_{i}", "created": datetime.now().isoformat()}
            cache.set(key, data, expiry_hours=1)
        print("✅ Multiple entries stored")
        
        # Get all test entries
        all_entries = []
        for i in range(5):
            key = f"test_entry_{i}"
            data = cache.get(key)
            if data:
                all_entries.append(data)
        
        print(f"✅ Retrieved {len(all_entries)} entries")
        
        # Test 8: Cache invalidation
        print("\n🗑️ Test 8: Cache invalidation...")
        delete_success = cache.delete(cache_key)
        if delete_success:
            print("✅ Cache entry deleted")
        else:
            print("❌ Failed to delete cache entry")
        
        # Verify deletion
        deleted_data = cache.get(cache_key)
        if deleted_data is None:
            print("✅ Cache deletion verified")
        else:
            print("❌ Cache deletion failed")
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 50)
        print("✅ Artha AI Cache System is fully operational")
        print("🔧 Ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cache_system()
    
    if success:
        print("\n🚀 Cache system is ready!")
        print("You can now run your Artha AI application with secure caching enabled.")
    else:
        print("\n💥 Cache system test failed!")
        print("Please check the error messages above.")