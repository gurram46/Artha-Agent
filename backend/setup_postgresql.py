#!/usr/bin/env python3
"""
PostgreSQL setup script for Artha Agent
This script will:
1. Reset artha_user password
2. Grant proper permissions
3. Clean up existing tables
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass
import sys
import os
import secrets
import string

def generate_secure_password(length=16):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def setup_postgresql():
    # Get database connection details from environment or prompt
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_name = os.getenv('DB_NAME', 'artha_cache_db')
    
    # Get postgres password from environment or prompt
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    if not postgres_password:
        postgres_password = getpass.getpass("Enter postgres user password: ")
    
    # Generate or get artha_user password
    artha_password = os.getenv('DB_PASSWORD')
    if not artha_password:
        artha_password = generate_secure_password()
        print(f"Generated secure password for artha_user: {artha_password}")
        print("IMPORTANT: Save this password in your .env file as DB_PASSWORD")
    
    try:
        # Connect to database as postgres user
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user="postgres",
            password=postgres_password,
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL as postgres user")
        
        # Reset artha_user password
        print("Setting artha_user password...")
        cursor.execute("ALTER USER artha_user WITH PASSWORD %s;", (artha_password,))
        print("Password set for artha_user")
        
        # Grant all necessary privileges
        cursor.execute("GRANT ALL PRIVILEGES ON SCHEMA public TO artha_user;")
        cursor.execute("GRANT CREATE ON SCHEMA public TO artha_user;")
        cursor.execute("GRANT USAGE ON SCHEMA public TO artha_user;")
        print("Granted schema privileges")
        
        # Drop existing tables to clean up
        print("Cleaning up existing tables...")
        tables_to_drop = [
            'secure_cache',
            'chat_sessions', 
            'chat_messages',
            'user_feedback',
            'popular_topics'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                print(f"Dropped table {table}")
            except Exception as e:
                print(f"Note: Could not drop {table}: {e}")
        
        # Drop indexes if they exist
        indexes_to_drop = [
            'idx_expires_at',
            'idx_session_id',
            'idx_user_id',
            'idx_timestamp'
        ]
        
        for index in indexes_to_drop:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index};")
                print(f"Dropped index {index}")
            except Exception as e:
                print(f"Note: Could not drop {index}: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ PostgreSQL setup completed successfully!")
        print("✅ artha_user password reset")
        print("✅ Database tables cleaned up")
        print("\nTesting connection as artha_user...")
        
        # Test connection as artha_user
        test_conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user="artha_user",
            password=artha_password,
            database=db_name
        )
        test_conn.close()
        print("✅ Connection test successful!")
        print("\nYou can now start the backend server.")
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_postgresql()