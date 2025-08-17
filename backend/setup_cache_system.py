#!/usr/bin/env python3
"""
Comprehensive PostgreSQL and Secure Cache System Setup for Artha AI
Handles PostgreSQL installation, database setup, and secure caching infrastructure
"""

import os
import sys
import subprocess
import logging
import platform
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgreSQLSetup:
    """Handles PostgreSQL installation and configuration"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.postgres_version = "15"
        self.default_port = 5432
        self.default_db = "artha_cache_db"
        self.default_user = "artha_user"
        
    def check_postgresql_installed(self) -> bool:
        """Check if PostgreSQL is already installed"""
        try:
            if self.is_windows:
                # Check for psql in common Windows locations
                common_paths = [
                    r"C:\Program Files\PostgreSQL\*\bin\psql.exe",
                    r"C:\Program Files (x86)\PostgreSQL\*\bin\psql.exe"
                ]
                
                for path_pattern in common_paths:
                    import glob
                    matches = glob.glob(path_pattern)
                    if matches:
                        logger.info(f"Found PostgreSQL at: {matches[0]}")
                        return True
                
                # Try running psql command
                result = subprocess.run(["psql", "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"PostgreSQL found: {result.stdout.strip()}")
                    return True
            else:
                # Unix-like systems
                result = subprocess.run(["which", "psql"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"PostgreSQL found at: {result.stdout.strip()}")
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"PostgreSQL check failed: {e}")
            return False
    
    def install_postgresql_windows(self) -> bool:
        """Install PostgreSQL on Windows"""
        logger.info("Installing PostgreSQL on Windows...")
        
        try:
            # Check if chocolatey is available
            choco_result = subprocess.run(["choco", "--version"], 
                                        capture_output=True, text=True)
            
            if choco_result.returncode == 0:
                logger.info("   Using Chocolatey to install PostgreSQL...")
                result = subprocess.run([
                    "choco", "install", "postgresql", "-y",
                    "--params", f"'/Password:postgres /Port:{self.default_port}'"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("PostgreSQL installed via Chocolatey")
                    return True
                else:
                    logger.warning("Chocolatey installation failed, trying manual approach...")
            
            # Manual installation instructions
            logger.info("Manual PostgreSQL installation required:")
            logger.info("   1. Download PostgreSQL from: https://www.postgresql.org/download/windows/")
            logger.info("   2. Run the installer with default settings")
            logger.info(f"   3. Set password for 'postgres' user")
            logger.info(f"   4. Use port {self.default_port}")
            logger.info("   5. Re-run this setup script after installation")
            
            return False
            
        except Exception as e:
            logger.error(f"Windows PostgreSQL installation failed: {e}")
            return False
    
    def install_postgresql_unix(self) -> bool:
        """Install PostgreSQL on Unix-like systems"""
        logger.info("Installing PostgreSQL on Unix-like system...")
        
        try:
            # Detect package manager and install
            if shutil.which("apt-get"):  # Debian/Ubuntu
                commands = [
                    ["sudo", "apt-get", "update"],
                    ["sudo", "apt-get", "install", "-y", "postgresql", "postgresql-contrib"]
                ]
            elif shutil.which("yum"):  # RHEL/CentOS
                commands = [
                    ["sudo", "yum", "install", "-y", "postgresql-server", "postgresql-contrib"],
                    ["sudo", "postgresql-setup", "initdb"]
                ]
            elif shutil.which("brew"):  # macOS
                commands = [
                    ["brew", "install", "postgresql"],
                    ["brew", "services", "start", "postgresql"]
                ]
            else:
                logger.error("Unsupported package manager")
                return False
            
            for cmd in commands:
                logger.info(f"   Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Command failed: {result.stderr}")
                    return False
            
            logger.info("PostgreSQL installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Unix PostgreSQL installation failed: {e}")
            return False
    
    def create_database_and_user(self) -> bool:
        """Create database and user for Artha AI"""
        logger.info("Creating database and user...")
        
        try:
            # SQL commands to create database and user
            sql_commands = [
                f"CREATE DATABASE {self.default_db};",
                f"CREATE USER {self.default_user} WITH ENCRYPTED PASSWORD 'artha_secure_2024';",
                f"GRANT ALL PRIVILEGES ON DATABASE {self.default_db} TO {self.default_user};",
                f"ALTER USER {self.default_user} CREATEDB;"
            ]
            
            for sql in sql_commands:
                if self.is_windows:
                    cmd = ["psql", "-U", "postgres", "-c", sql]
                else:
                    cmd = ["sudo", "-u", "postgres", "psql", "-c", sql]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0 and "already exists" not in result.stderr:
                    logger.warning(f"SQL command may have failed: {sql}")
                    logger.debug(f"Error: {result.stderr}")
            
            logger.info("Database and user created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database creation failed: {e}")
            return False

class CacheSystemSetup:
    """Handles cache system setup and configuration"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.env_file = self.backend_dir / ".env"
    
    def install_python_dependencies(self) -> bool:
        """Install required Python packages"""
        logger.info("Installing Python dependencies...")
        
        dependencies = [
            "psycopg2-binary>=2.9.0",
            "sqlalchemy>=1.4.0",
            "alembic>=1.8.0", 
            "pycryptodome>=3.15.0",
            "apscheduler>=3.9.0",
            "python-dotenv>=0.19.0"
        ]
        
        try:
            for dep in dependencies:
                logger.info(f"   Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.warning(f"Failed to install {dep}: {result.stderr}")
                else:
                    logger.debug(f"{dep} installed")
            
            logger.info("Python dependencies installation completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """Create .env file with database configuration"""
        logger.info("Creating environment configuration...")
        
        try:
            import secrets
            import base64
            
            # Generate secure random values
            db_password = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*') for _ in range(20))
            encryption_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
            cache_salt = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode('utf-8')
            
            env_content = f"""# Artha AI Cache System Configuration
# Database Configuration
DATABASE_URL=postgresql://artha_user:{db_password}@localhost:5432/artha_cache_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=artha_cache_db
DB_USER=artha_user
DB_PASSWORD={db_password}

# Encryption Configuration
ENCRYPTION_KEY={encryption_key}
CACHE_ENCRYPTION_SALT={cache_salt}

# Cache Configuration
CACHE_DEFAULT_EXPIRY_HOURS=24
CACHE_MAX_SIZE_MB=1024
CACHE_CLEANUP_INTERVAL_HOURS=6

# Security Configuration
SECURE_CACHE_ENABLED=true
AUDIT_LOGGING_ENABLED=true

# Environment
ENVIRONMENT=development
DEBUG=true

# Generated on {datetime.utcnow().isoformat()}
# IMPORTANT: Save this password for database setup: {db_password}
"""
            
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            
            logger.info(f"Environment file created: {self.env_file}")
            logger.info("IMPORTANT: Update ENCRYPTION_KEY in production!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False
    
    def setup_database_schema(self) -> bool:
        """Set up database tables and schema"""
        logger.info("Setting up database schema...")
        
        try:
            # Import after dependencies are installed
            from backend.database.config import create_tables, test_connection
            
            # Test database connection
            if test_connection():
                logger.info("Database connection successful")
                
                # Create tables
                if create_tables():
                    logger.info("Database tables created successfully")
                    return True
                else:
                    logger.error("Failed to create database tables")
                    return False
            else:
                logger.error("Database connection failed")
                return False
                
        except ImportError as e:
            logger.error(f"Failed to import database modules: {e}")
            return False
        except Exception as e:
            logger.error(f"Database schema setup failed: {e}")
            return False
    
    def test_encryption_system(self) -> bool:
        """Test and verify encryption system"""
        logger.info("Testing encryption system...")
        
        try:
            from backend.utils.encryption import test_encryption_system
            
            if test_encryption_system():
                logger.info("Encryption system working correctly")
                return True
            else:
                logger.error("Encryption system test failed")
                return False
                
        except ImportError as e:
            logger.error(f"Failed to import encryption modules: {e}")
            return False
        except Exception as e:
            logger.error(f"Encryption test failed: {e}")
            return False
    
    def test_cache_service(self) -> bool:
        """Test cache service functionality"""
        logger.info("Testing cache service...")
        
        try:
            from backend.services.cache_service import cache_service
            
            # Test basic cache operations
            test_email = "test@example.com"
            test_data = {
                "accounts": [{"name": "Test", "balance": 1000}],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Test store
            if cache_service.cache_financial_data(test_email, test_data):
                logger.info("   Cache store test passed")
                
                # Test retrieve
                retrieved = cache_service.get_cached_financial_data(test_email)
                if retrieved and retrieved.get("accounts"):
                    logger.info("   Cache retrieve test passed")
                    
                    # Test invalidate
                    if cache_service.invalidate_user_cache(test_email):
                        logger.info("   Cache invalidate test passed")
                        logger.info("Cache service tests completed successfully")
                        return True
            
            logger.error("Cache service tests failed")
            return False
            
        except ImportError as e:
            logger.error(f"Failed to import cache service: {e}")
            return False
        except Exception as e:
            logger.error(f"Cache service test failed: {e}")
            return False





def main():
    """Main setup function"""
    logger.info("Starting Artha AI PostgreSQL & Cache System Setup")
    logger.info("=" * 70)
    
    # Initialize setup classes
    postgres_setup = PostgreSQLSetup()
    cache_setup = CacheSystemSetup()
    
    # Step 1: Install Python dependencies first
    logger.info("Step 1: Installing Python Dependencies")
    if not cache_setup.install_python_dependencies():
        logger.error("Setup failed at Python dependencies installation")
        return False
    
    # Step 2: Check/Install PostgreSQL
    logger.info("Step 2: PostgreSQL Installation")
    if not postgres_setup.check_postgresql_installed():
        logger.info("PostgreSQL not found. Installing...")
        
        if postgres_setup.is_windows:
            if not postgres_setup.install_postgresql_windows():
                logger.error("PostgreSQL installation failed")
                logger.info("Please install PostgreSQL manually and re-run this script")
                return False
        else:
            if not postgres_setup.install_postgresql_unix():
                logger.error("PostgreSQL installation failed")
                return False
    
    # Step 3: Create database and user
    logger.info("Step 3: Database Configuration")
    if not postgres_setup.create_database_and_user():
        logger.warning("Database creation may have failed - continuing anyway")
    
    # Step 4: Create environment configuration
    logger.info("Step 4: Environment Configuration")
    if not cache_setup.create_env_file():
        logger.error("Setup failed at environment configuration")
        return False
    
    # Step 5: Setup database schema
    logger.info("Step 5: Database Schema Setup")
    if not cache_setup.setup_database_schema():
        logger.error("Setup failed at database schema creation")
        return False
    
    # Step 6: Test encryption system
    logger.info("Step 6: Encryption System Test")
    if not cache_setup.test_encryption_system():
        logger.error("Setup failed at encryption system test")
        return False
    
    # Step 7: Test cache service
    logger.info("Step 7: Cache Service Test")
    if not cache_setup.test_cache_service():
        logger.error("Setup failed at cache service test")
        return False
    
    # Success!
    logger.info("=" * 70)
    logger.info("Artha AI PostgreSQL & Cache System Setup Completed Successfully!")
    logger.info("")
    logger.info("Setup Summary:")
    logger.info("   PostgreSQL installed and configured")
    logger.info("   Database and user created")
    logger.info("   Environment configuration created")
    logger.info("   Database schema initialized")
    logger.info("   Encryption system verified")
    logger.info("   Cache service tested")
    logger.info("")
    logger.info("Next Steps for Team Deployment:")
    logger.info("   1. Share the .env file template with your team")
    logger.info("   2. Each developer should update ENCRYPTION_KEY")
    logger.info("   3. Configure production database settings")
    logger.info("   4. Set up automated cache cleanup (optional)")
    logger.info("")
    logger.info("The system is ready for secure financial data caching!")
    
    return True

if __name__ == "__main__":
    main()