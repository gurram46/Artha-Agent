"""
Setup script for Artha AI Secure Caching System
Helps configure PostgreSQL and environment variables
"""

import os
import sys
import subprocess
import base64
from pathlib import Path
from Crypto.Random import get_random_bytes

def generate_encryption_key():
    """Generate a new AES-256 encryption key"""
    key = get_random_bytes(32)
    return base64.b64encode(key).decode('utf-8')

def create_env_file():
    """Create .env file with required configuration"""
    env_path = Path(".env")
    
    # Generate encryption key
    encryption_key = generate_encryption_key()
    
    env_content = f"""# Artha AI Secure Caching Configuration

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/artha_cache

# Encryption Key (AES-256) - KEEP THIS SECRET!
ARTHA_ENCRYPTION_KEY={encryption_key}

# Cache Settings
CACHE_CLEANUP_INTERVAL_HOURS=1
CACHE_EXPIRATION_HOURS=24

# Security Settings
ENABLE_SECURE_CACHE=true
LOG_CACHE_OPERATIONS=true
"""
    
    if env_path.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled")
            return False
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully")
    print(f"🔑 Generated encryption key: {encryption_key[:16]}...")
    return True

def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "psycopg2-binary", "sqlalchemy", "alembic", 
            "pycryptodome", "apscheduler"
        ], check=True, capture_output=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_postgresql():
    """Check if PostgreSQL is installed and running"""
    print("🔍 Checking PostgreSQL installation...")
    
    try:
        # Try to connect to PostgreSQL
        result = subprocess.run([
            "psql", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found")
            return False
            
    except FileNotFoundError:
        print("❌ PostgreSQL not found in PATH")
        return False

def create_database():
    """Create the Artha cache database"""
    print("🗄️  Creating Artha cache database...")
    
    try:
        # Try to create database
        subprocess.run([
            "createdb", "-h", "localhost", "-U", "postgres", "artha_cache"
        ], check=True, capture_output=True)
        
        print("✅ Database 'artha_cache' created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e.stderr):
            print("ℹ️  Database 'artha_cache' already exists")
            return True
        else:
            print(f"❌ Failed to create database: {e}")
            return False

def test_database_connection():
    """Test database connection"""
    print("🔗 Testing database connection...")
    
    try:
        from database.config import test_connection
        if test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_encryption():
    """Test encryption system"""
    print("🔐 Testing encryption system...")
    
    try:
        from utils.encryption import encryption
        if encryption.test_encryption():
            print("✅ Encryption system working correctly")
            return True
        else:
            print("❌ Encryption system failed")
            return False
            
    except Exception as e:
        print(f"❌ Encryption test error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Artha AI Secure Caching Setup")
    print("=" * 40)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Step 2: Create .env file
    if not create_env_file():
        print("❌ Setup failed at .env creation")
        return
    
    # Step 3: Check PostgreSQL
    if not check_postgresql():
        print("\n📋 PostgreSQL Installation Instructions:")
        print("1. Download PostgreSQL from: https://www.postgresql.org/download/")
        print("2. Install with default settings")
        print("3. Remember your postgres user password")
        print("4. Update DATABASE_URL in .env file with your password")
        print("5. Run this setup script again")
        return
    
    # Step 4: Create database
    if not create_database():
        print("⚠️  Database creation failed - you may need to create it manually")
        print("Run: createdb -h localhost -U postgres artha_cache")
    
    # Step 5: Test connections
    print("\n🧪 Running tests...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    db_success = test_database_connection()
    encryption_success = test_encryption()
    
    if db_success and encryption_success:
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start your Artha AI backend server")
        print("2. The secure caching system will initialize automatically")
        print("3. User data will be cached for 24 hours with AES-256 encryption")
        print("4. Automatic cleanup runs every hour")
        
        print("\n🔧 Configuration:")
        print(f"- Database: {os.getenv('DATABASE_URL', 'Not configured')}")
        print(f"- Encryption: AES-256 enabled")
        print(f"- Cache expiration: 24 hours")
        print(f"- Cleanup interval: 1 hour")
        
    else:
        print("\n❌ Setup completed with errors")
        print("Please check the error messages above and fix any issues")

if __name__ == "__main__":
    main()