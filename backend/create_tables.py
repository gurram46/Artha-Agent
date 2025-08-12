#!/usr/bin/env python3
"""
Database Schema Setup for Artha AI Cache System
"""

import psycopg2
import os
from datetime import datetime
from urllib.parse import urlparse

def create_tables():
    """Create the necessary database tables"""
    
    # Get database URL from environment variable
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse DATABASE_URL
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
    else:
        # Fallback to individual environment variables
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'artha_cache_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD')
        )
    
    cursor = conn.cursor()
    
    try:
        print("🗄️ Creating database tables...")
        
        # Cache entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                id SERIAL PRIMARY KEY,
                cache_key VARCHAR(255) UNIQUE NOT NULL,
                encrypted_data TEXT NOT NULL,
                data_hash VARCHAR(64) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB DEFAULT '{}'::jsonb
            );
        """)
        print("✅ Created cache_entries table")
        
        # Cache statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_stats (
                id SERIAL PRIMARY KEY,
                date DATE DEFAULT CURRENT_DATE,
                total_entries INTEGER DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                cache_misses INTEGER DEFAULT 0,
                total_size_bytes BIGINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created cache_stats table")
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                operation VARCHAR(50) NOT NULL,
                cache_key VARCHAR(255),
                user_id VARCHAR(100),
                ip_address INET,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details JSONB DEFAULT '{}'::jsonb
            );
        """)
        print("✅ Created audit_log table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(cache_key);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON cache_entries(created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_log(operation);")
        print("✅ Created database indexes")
        
        # Insert initial cache stats record
        cursor.execute("""
            INSERT INTO cache_stats (date, total_entries, cache_hits, cache_misses, total_size_bytes)
            VALUES (CURRENT_DATE, 0, 0, 0, 0)
            ON CONFLICT DO NOTHING;
        """)
        print("✅ Initialized cache statistics")
        
        conn.commit()
        print("🎉 Database schema setup completed successfully!")
        
        # Test the tables
        cursor.execute("SELECT COUNT(*) FROM cache_entries;")
        cache_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cache_stats;")
        stats_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM audit_log;")
        audit_count = cursor.fetchone()[0]
        
        print(f"📊 Database Status:")
        print(f"   - Cache entries: {cache_count}")
        print(f"   - Cache stats records: {stats_count}")
        print(f"   - Audit log entries: {audit_count}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Artha AI Database Schema Setup")
    print("=" * 40)
    
    success = create_tables()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("🔧 Next steps:")
        print("1. Test the cache system")
        print("2. Run your Artha AI application")
    else:
        print("\n❌ Setup failed!")