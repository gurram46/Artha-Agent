#!/usr/bin/env python3
"""
Complete Artha AI System Setup Script
====================================

Sets up the complete user management and authentication system with all required database tables.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description="Running command"):
    """Execute a command and return success status"""
    try:
        logger.info(f"🔄 {description}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ {description} completed successfully")
            if result.stdout:
                logger.info(f"Output: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description} failed")
            if result.stderr:
                logger.error(f"Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {description} failed with exception: {e}")
        return False

def setup_database_tables():
    """Set up all required database tables"""
    logger.info("🗄️ Setting up database tables...")
    
    scripts = [
        ("create_tables.py", "Creating cache system tables"),
        ("database/init_chat_tables.py", "Creating chat system tables"),
        ("database/init_user_tables.py", "Creating user management tables")
    ]
    
    success_count = 0
    for script, description in scripts:
        script_path = os.path.join(os.path.dirname(__file__), script)
        if os.path.exists(script_path):
            if run_command(f"python \"{script_path}\"", description):
                success_count += 1
        else:
            logger.warning(f"⚠️ Script not found: {script_path}")
    
    return success_count == len(scripts)

def install_dependencies():
    """Install required Python packages"""
    logger.info("📦 Installing Python dependencies...")
    
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        return run_command(f"pip install -r \"{requirements_path}\"", "Installing dependencies")
    else:
        logger.error("❌ requirements.txt not found")
        return False

def test_services():
    """Test that all services can be imported and initialized"""
    logger.info("🧪 Testing service imports...")
    
    try:
        # Test authentication service
        sys.path.append(os.path.dirname(__file__))
        from services.auth_service import get_auth_service
        auth_service = get_auth_service()
        logger.info("✅ Authentication service imported successfully")
        
        # Test user service
        from services.user_service import get_user_service
        user_service = get_user_service()
        logger.info("✅ User service imported successfully")
        
        # Test portfolio service
        from services.portfolio_service import get_portfolio_service
        portfolio_service = get_portfolio_service()
        logger.info("✅ Portfolio service imported successfully")
        
        # Test API endpoints
        from api.auth_endpoints import router as auth_router
        from api.user_endpoints import router as user_router
        from api.portfolio_endpoints import router as portfolio_router
        logger.info("✅ All API endpoints imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service import failed: {e}")
        return False

def create_env_template():
    """Create .env file with default configurations"""
    import secrets
    import base64
    
    logger.info("📝 Checking environment configuration...")
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        logger.info("📝 Creating .env template...")
        
        # Generate secure random keys
        encryption_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
        jwt_secret = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode('utf-8')
        
        env_template = f'''# Artha AI Backend Configuration
# Database Configuration
DATABASE_URL=postgresql://artha_user:CHANGE_THIS_PASSWORD@localhost:5432/artha_ai

# Security Configuration - CHANGE THESE IN PRODUCTION
ENCRYPTION_KEY={encryption_key}
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# External API Keys - ADD YOUR ACTUAL KEYS
GOOGLE_API_KEY=your-google-api-key-here
FI_MCP_AUTH_TOKEN=your-fi-mcp-auth-token-here

# CORS Configuration - ADD YOUR PRODUCTION DOMAINS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting Configuration
RATE_LIMIT_WHITELIST=127.0.0.1,::1

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL_HOURS=24

# Development Settings
DEBUG=false
LOG_LEVEL=INFO

# HTTPS Configuration (for production)
FORCE_HTTPS=true

# Generated on {datetime.now().isoformat()}
'''
        
        with open(env_path, 'w') as f:
            f.write(env_template)
        
        logger.info("✅ .env template created")
        return True
    else:
        logger.info("✅ .env file already exists")
        return True

def main():
    """Main setup function"""
    logger.info("🚀 Starting Artha AI Complete System Setup")
    logger.info("=" * 60)
    
    # Step 1: Create environment template
    if not create_env_template():
        logger.error("❌ Failed to create environment template")
        return False
    
    # Step 2: Install dependencies
    if not install_dependencies():
        logger.error("❌ Failed to install dependencies")
        return False
    
    # Step 3: Set up database tables
    if not setup_database_tables():
        logger.error("❌ Failed to set up database tables")
        return False
    
    # Step 4: Test services
    if not test_services():
        logger.error("❌ Failed to test services")
        return False
    
    # Success message
    logger.info("\n" + "=" * 60)
    logger.info("🎉 ARTHA AI COMPLETE SYSTEM SETUP SUCCESSFUL!")
    logger.info("=" * 60)
    
    logger.info("\n✅ System Components Installed:")
    logger.info("   • User Authentication System with JWT")
    logger.info("   • Persistent User Profile Management")
    logger.info("   • Investment Preferences & Goals Tracking")
    logger.info("   • Portfolio Analytics with Historical Data")
    logger.info("   • Comprehensive Data Export (JSON/CSV)")
    logger.info("   • Enterprise-level Security & Encryption")
    logger.info("   • Chat History with Full Encryption")
    logger.info("   • 24-hour Financial Data Caching")
    
    logger.info("\n🔗 API Endpoints Available:")
    logger.info("   • /api/auth/* - Authentication & JWT management")
    logger.info("   • /api/user/* - User profiles & preferences")
    logger.info("   • /api/portfolio/* - Portfolio analytics & export")
    logger.info("   • /api/chat/* - Chat conversations & history")
    logger.info("   • /api/cache/* - Financial data caching")
    
    logger.info("\n🔧 Next Steps:")
    logger.info("   1. Update .env file with your actual configuration")
    logger.info("   2. Ensure PostgreSQL is running on port 5433")
    logger.info("   3. Start the backend server: python api_server.py")
    logger.info("   4. Test endpoints at http://localhost:8000/docs")
    logger.info("   5. Integrate with frontend authentication")
    
    logger.info(f"\n📊 Setup completed at: {datetime.now().isoformat()}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)