"""
Simple Cache Service for Artha AI Cache System
Uses direct PostgreSQL connection with proper encryption
"""

import os
import json
import psycopg2
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from utils.encryption import encryption

class SimpleCacheService:
    def __init__(self):
        """Initialize cache service with database connection"""
        self.db_config = {
            'host': 'localhost',
            'port': 5433,
            'database': 'artha_cache_db',
            'user': 'postgres',
            'password': '2003'
        }
        
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def set(self, key: str, data: Any, expiry_hours: int = 24) -> bool:
        """Store data in cache"""
        try:
            # Encrypt the data using database format
            encrypted_data, nonce, auth_tag = encryption.encrypt_for_database(data)
            
            # Create a simple hash for integrity checking
            json_data = json.dumps(data, sort_keys=True)
            data_hash = hashlib.sha256(json_data.encode()).hexdigest()
            
            # Calculate expiry time
            expiry_time = datetime.now() + timedelta(hours=expiry_hours)
            
            # Store in database
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO cache_entries (cache_key, encrypted_data, nonce, auth_tag, data_hash, expires_at, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (cache_key) DO UPDATE SET
                            encrypted_data = EXCLUDED.encrypted_data,
                            nonce = EXCLUDED.nonce,
                            auth_tag = EXCLUDED.auth_tag,
                            data_hash = EXCLUDED.data_hash,
                            expires_at = EXCLUDED.expires_at,
                            updated_at = EXCLUDED.updated_at
                    """, (key, encrypted_data, nonce, auth_tag, data_hash, expiry_time, datetime.now(), datetime.now()))
                    
                    # Update statistics
                    cursor.execute("""
                        UPDATE cache_stats SET 
                            total_entries = (SELECT COUNT(*) FROM cache_entries WHERE expires_at > NOW()),
                            cache_hits = cache_hits + 1,
                            last_updated = %s
                    """, (datetime.now(),))
                    
                conn.commit()
            
            print(f"✅ Cached data with key: {key}")
            return True
            
        except Exception as e:
            print(f"❌ Error caching data: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT encrypted_data, nonce, auth_tag, data_hash, expires_at
                        FROM cache_entries 
                        WHERE cache_key = %s AND expires_at > NOW()
                    """, (key,))
                    
                    result = cursor.fetchone()
                    if not result:
                        print(f"❌ Cache miss for key: {key}")
                        
                        # Update miss statistics
                        cursor.execute("""
                            UPDATE cache_stats SET 
                                cache_misses = cache_misses + 1,
                                last_updated = %s
                        """, (datetime.now(),))
                        conn.commit()
                        return None
                    
                    encrypted_data, nonce, auth_tag, stored_hash, expires_at = result
                    
                    # Decrypt data
                    data = encryption.decrypt_from_database(encrypted_data, nonce, auth_tag)
                    
                    # Verify data integrity
                    json_data = json.dumps(data, sort_keys=True)
                    calculated_hash = hashlib.sha256(json_data.encode()).hexdigest()
                    
                    if calculated_hash != stored_hash:
                        print(f"❌ Data integrity check failed for key: {key}")
                        return None
                    
                    # Update hit statistics
                    cursor.execute("""
                        UPDATE cache_stats SET 
                            cache_hits = cache_hits + 1,
                            last_updated = %s
                    """, (datetime.now(),))
                    conn.commit()
                    
                    print(f"✅ Retrieved cached data with key: {key}")
                    return data
                    
        except Exception as e:
            print(f"❌ Error retrieving data: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete data from cache"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM cache_entries WHERE cache_key = %s", (key,))
                    deleted_count = cursor.rowcount
                    
                    if deleted_count > 0:
                        # Update statistics
                        cursor.execute("""
                            UPDATE cache_stats SET 
                                total_entries = (SELECT COUNT(*) FROM cache_entries WHERE expires_at > NOW()),
                                last_updated = %s
                        """, (datetime.now(),))
                        
                    conn.commit()
                    
            if deleted_count > 0:
                print(f"✅ Deleted cached data with key: {key}")
                return True
            else:
                print(f"❌ No data found with key: {key}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting data: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM cache_entries WHERE expires_at <= NOW()")
                    deleted_count = cursor.rowcount
                    
                    # Update statistics
                    cursor.execute("""
                        UPDATE cache_stats SET 
                            total_entries = (SELECT COUNT(*) FROM cache_entries WHERE expires_at > NOW()),
                            last_updated = %s
                    """, (datetime.now(),))
                    
                conn.commit()
            
            print(f"✅ Cleaned up {deleted_count} expired entries")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error cleaning up expired entries: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM cache_stats")
                    result = cursor.fetchone()
                    
                    if result:
                        return {
                            'total_entries': result[1],
                            'cache_hits': result[2],
                            'cache_misses': result[3],
                            'hit_ratio': result[4],
                            'last_updated': result[5]
                        }
                    else:
                        return {
                            'total_entries': 0,
                            'cache_hits': 0,
                            'cache_misses': 0,
                            'hit_ratio': 0.0,
                            'last_updated': None
                        }
                        
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def list_keys(self) -> list:
        """List all cache keys"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT cache_key FROM cache_entries WHERE expires_at > NOW()")
                    results = cursor.fetchall()
                    return [row[0] for row in results]
                    
        except Exception as e:
            print(f"❌ Error listing keys: {e}")
            return []