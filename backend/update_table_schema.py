"""
Update database schema to support GCM encryption
Adds nonce and auth_tag columns to cache_entries table
"""

import psycopg2
from datetime import datetime

def update_schema():
    """Add missing columns for GCM encryption"""
    db_config = {
        'host': 'localhost',
        'port': 5433,
        'database': 'artha_cache_db',
        'user': 'postgres',
        'password': '2003'
    }
    
    try:
        print("🔧 Updating database schema for GCM encryption...")
        
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True  # Enable autocommit to handle DDL statements
        cursor = conn.cursor()
        
        # Add nonce column
        try:
            cursor.execute("ALTER TABLE cache_entries ADD COLUMN nonce TEXT")
            print("✅ Added nonce column")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ nonce column already exists")
        
        # Add auth_tag column
        try:
            cursor.execute("ALTER TABLE cache_entries ADD COLUMN auth_tag TEXT")
            print("✅ Added auth_tag column")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ auth_tag column already exists")
        
        # Add updated_at column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE cache_entries ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added updated_at column")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ updated_at column already exists")
                
        # Update existing entries to have default values
        cursor.execute("""
            UPDATE cache_entries 
            SET nonce = '', auth_tag = '', updated_at = CURRENT_TIMESTAMP 
            WHERE nonce IS NULL OR auth_tag IS NULL
        """)
        
        print("✅ Schema update completed successfully!")
        
        # Update cache_stats table
        print("\n🔧 Updating cache_stats table...")
        
        # Add missing columns to cache_stats
        try:
            cursor.execute("ALTER TABLE cache_stats ADD COLUMN cache_misses INTEGER DEFAULT 0")
            print("✅ Added cache_misses column")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ cache_misses column already exists")
        
        try:
            cursor.execute("ALTER TABLE cache_stats ADD COLUMN hit_ratio DECIMAL(5,4) DEFAULT 0.0")
            print("✅ Added hit_ratio column")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ hit_ratio column already exists")
        
        try:
            cursor.execute("ALTER TABLE cache_stats ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added last_updated column")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ last_updated column already exists")
        
        # Update existing cache_stats entries
        cursor.execute("""
            UPDATE cache_stats 
            SET cache_misses = 0, hit_ratio = 0.0, last_updated = CURRENT_TIMESTAMP 
            WHERE cache_misses IS NULL OR hit_ratio IS NULL OR last_updated IS NULL
        """)
        
        # Show updated table structures
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'cache_entries' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Updated cache_entries table structure:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
        
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'cache_stats' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Updated cache_stats table structure:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
        
        cursor.close()
        conn.close()
                
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    update_schema()