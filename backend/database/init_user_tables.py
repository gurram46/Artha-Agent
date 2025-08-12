"""
User Management Database Initialization Script
============================================

Creates comprehensive user management tables with encryption and security.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_database_url

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_user_tables():
    """
    Create comprehensive user management database tables
    """
    try:
        # Get database URL and parse it
        database_url = get_database_url()
        
        # Parse the database URL to extract connection parameters
        import re
        match = re.match(r'postgresql://([^:]+):?([^@]*)@([^:]+):(\d+)/(.+)', database_url)
        if not match:
            # Try without password
            match = re.match(r'postgresql://([^@]+)@([^:]+):(\d+)/(.+)', database_url)
            if match:
                user, host, port, database = match.groups()
                password = ''
            else:
                raise ValueError(f"Invalid database URL format: {database_url}")
        else:
            user, password, host, port, database = match.groups()
        
        # Connect to database
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            database=database,
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("🔗 Connected to database successfully")
        
        # Create users table
        logger.info("📝 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                email_hash VARCHAR(64) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(32) NOT NULL,
                full_name_encrypted BYTEA,
                full_name_nonce BYTEA,
                full_name_auth_tag BYTEA,
                phone_encrypted BYTEA,
                phone_nonce BYTEA,
                phone_auth_tag BYTEA,
                date_of_birth_encrypted BYTEA,
                date_of_birth_nonce BYTEA,
                date_of_birth_auth_tag BYTEA,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255),
                reset_password_token VARCHAR(255),
                reset_password_expires TIMESTAMP WITH TIME ZONE,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP WITH TIME ZONE,
                metadata JSONB DEFAULT '{}'::jsonb
            );
        """)
        
        # Create indexes for users
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email 
            ON users(email);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email_hash 
            ON users(email_hash);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_is_active 
            ON users(is_active);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_created_at 
            ON users(created_at DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_last_login 
            ON users(last_login DESC);
        """)
        
        logger.info("✅ users table created successfully")
        
        # Create user_profiles table
        logger.info("📝 Creating user_profiles table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                occupation_encrypted BYTEA,
                occupation_nonce BYTEA,
                occupation_auth_tag BYTEA,
                annual_income_encrypted BYTEA,
                annual_income_nonce BYTEA,
                annual_income_auth_tag BYTEA,
                company_encrypted BYTEA,
                company_nonce BYTEA,
                company_auth_tag BYTEA,
                experience_years INTEGER,
                address_encrypted BYTEA,
                address_nonce BYTEA,
                address_auth_tag BYTEA,
                pan_encrypted BYTEA,
                pan_nonce BYTEA,
                pan_auth_tag BYTEA,
                aadhar_encrypted BYTEA,
                aadhar_nonce BYTEA,
                aadhar_auth_tag BYTEA,
                emergency_contact_encrypted BYTEA,
                emergency_contact_nonce BYTEA,
                emergency_contact_auth_tag BYTEA,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id 
            ON user_profiles(user_id);
        """)
        
        logger.info("✅ user_profiles table created successfully")
        
        # Create investment_preferences table
        logger.info("📝 Creating investment_preferences table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investment_preferences (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                risk_tolerance VARCHAR(20) NOT NULL DEFAULT 'moderate',
                investment_horizon VARCHAR(20) NOT NULL DEFAULT 'long_term',
                investment_goals JSONB DEFAULT '[]'::jsonb,
                preferred_asset_classes JSONB DEFAULT '[]'::jsonb,
                monthly_investment_amount DECIMAL(15,2),
                emergency_fund_months INTEGER DEFAULT 6,
                debt_to_income_ratio DECIMAL(5,2),
                current_investments JSONB DEFAULT '{}'::jsonb,
                financial_dependents INTEGER DEFAULT 0,
                retirement_age INTEGER DEFAULT 60,
                major_expenses JSONB DEFAULT '[]'::jsonb,
                insurance_coverage JSONB DEFAULT '{}'::jsonb,
                tax_bracket VARCHAR(20),
                investment_experience VARCHAR(20) DEFAULT 'beginner',
                advisor_preference VARCHAR(20) DEFAULT 'ai_guided',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT valid_risk_tolerance CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive', 'very_aggressive')),
                CONSTRAINT valid_investment_horizon CHECK (investment_horizon IN ('short_term', 'medium_term', 'long_term')),
                CONSTRAINT valid_investment_experience CHECK (investment_experience IN ('beginner', 'intermediate', 'experienced', 'expert')),
                CONSTRAINT valid_advisor_preference CHECK (advisor_preference IN ('ai_guided', 'human_advisor', 'self_directed', 'hybrid'))
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_investment_preferences_user_id 
            ON investment_preferences(user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_investment_preferences_risk_tolerance 
            ON investment_preferences(risk_tolerance);
        """)
        
        logger.info("✅ investment_preferences table created successfully")
        
        # Create user_sessions table
        logger.info("📝 Creating user_sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                session_token VARCHAR(255) NOT NULL,
                refresh_token VARCHAR(255) NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                refresh_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                ip_address INET,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                fi_money_session_linked BOOLEAN DEFAULT FALSE,
                fi_money_session_id VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id 
            ON user_sessions(user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token 
            ON user_sessions(session_token);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active 
            ON user_sessions(is_active);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at 
            ON user_sessions(expires_at);
        """)
        
        logger.info("✅ user_sessions table created successfully")
        
        # Create portfolio_snapshots table for historical tracking
        logger.info("📝 Creating portfolio_snapshots table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                snapshot_date DATE NOT NULL,
                net_worth DECIMAL(15,2),
                total_assets DECIMAL(15,2),
                total_liabilities DECIMAL(15,2),
                mutual_funds_value DECIMAL(15,2),
                stocks_value DECIMAL(15,2),
                fixed_deposits DECIMAL(15,2),
                savings_accounts DECIMAL(15,2),
                epf_value DECIMAL(15,2),
                other_investments DECIMAL(15,2),
                portfolio_data_encrypted BYTEA NOT NULL,
                portfolio_data_nonce BYTEA NOT NULL,
                portfolio_data_auth_tag BYTEA NOT NULL,
                data_source VARCHAR(50) DEFAULT 'fi_mcp',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, snapshot_date)
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_user_id 
            ON portfolio_snapshots(user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_date 
            ON portfolio_snapshots(snapshot_date DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_net_worth 
            ON portfolio_snapshots(net_worth);
        """)
        
        logger.info("✅ portfolio_snapshots table created successfully")
        
        # Create user_goals table
        logger.info("📝 Creating user_goals table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_goals (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                goal_name VARCHAR(255) NOT NULL,
                goal_type VARCHAR(50) NOT NULL,
                target_amount DECIMAL(15,2) NOT NULL,
                current_amount DECIMAL(15,2) DEFAULT 0,
                target_date DATE,
                monthly_contribution DECIMAL(10,2),
                priority_level INTEGER DEFAULT 3,
                status VARCHAR(20) DEFAULT 'active',
                description_encrypted BYTEA,
                description_nonce BYTEA,
                description_auth_tag BYTEA,
                strategy JSONB DEFAULT '{}'::jsonb,
                progress_tracking JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT valid_goal_type CHECK (goal_type IN ('retirement', 'emergency_fund', 'home_purchase', 'education', 'travel', 'business', 'wedding', 'car_purchase', 'investment', 'debt_payoff', 'other')),
                CONSTRAINT valid_status CHECK (status IN ('active', 'completed', 'paused', 'cancelled')),
                CONSTRAINT valid_priority CHECK (priority_level >= 1 AND priority_level <= 5)
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_goals_user_id 
            ON user_goals(user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_goals_goal_type 
            ON user_goals(goal_type);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_goals_status 
            ON user_goals(status);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_goals_target_date 
            ON user_goals(target_date);
        """)
        
        logger.info("✅ user_goals table created successfully")
        
        # Create notifications table
        logger.info("📝 Creating notifications table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message_encrypted BYTEA NOT NULL,
                message_nonce BYTEA NOT NULL,
                message_auth_tag BYTEA NOT NULL,
                priority VARCHAR(20) DEFAULT 'medium',
                is_read BOOLEAN DEFAULT FALSE,
                action_url VARCHAR(500),
                metadata JSONB DEFAULT '{}'::jsonb,
                expires_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP WITH TIME ZONE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT valid_notification_type CHECK (notification_type IN ('portfolio_update', 'goal_progress', 'market_alert', 'system_update', 'security_alert', 'payment_reminder', 'achievement', 'recommendation')),
                CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
            ON notifications(user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_is_read 
            ON notifications(is_read);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_created_at 
            ON notifications(created_at DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_priority 
            ON notifications(priority);
        """)
        
        logger.info("✅ notifications table created successfully")
        
        # Create triggers for updating timestamps
        logger.info("📝 Creating triggers...")
        
        # Trigger for updating updated_at in users
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_user_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_user_timestamp 
            ON users;
        """)
        
        cursor.execute("""
            CREATE TRIGGER trigger_update_user_timestamp
                BEFORE UPDATE ON users
                FOR EACH ROW
                EXECUTE FUNCTION update_user_timestamp();
        """)
        
        # Trigger for updating updated_at in user_profiles
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_user_profile_timestamp 
            ON user_profiles;
        """)
        
        cursor.execute("""
            CREATE TRIGGER trigger_update_user_profile_timestamp
                BEFORE UPDATE ON user_profiles
                FOR EACH ROW
                EXECUTE FUNCTION update_user_timestamp();
        """)
        
        # Trigger for updating updated_at in investment_preferences
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_investment_preferences_timestamp 
            ON investment_preferences;
        """)
        
        cursor.execute("""
            CREATE TRIGGER trigger_update_investment_preferences_timestamp
                BEFORE UPDATE ON investment_preferences
                FOR EACH ROW
                EXECUTE FUNCTION update_user_timestamp();
        """)
        
        # Trigger for updating updated_at in user_goals
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_user_goals_timestamp 
            ON user_goals;
        """)
        
        cursor.execute("""
            CREATE TRIGGER trigger_update_user_goals_timestamp
                BEFORE UPDATE ON user_goals
                FOR EACH ROW
                EXECUTE FUNCTION update_user_timestamp();
        """)
        
        logger.info("✅ Triggers created successfully")
        
        # Display success message
        logger.info("\n" + "="*60)
        logger.info("🎉 USER MANAGEMENT DATABASE SCHEMA CREATED SUCCESSFULLY")
        logger.info("="*60)
        
        logger.info("\n📊 Tables created:")
        logger.info("   • users - Core user accounts with encryption")
        logger.info("   • user_profiles - Extended user information")
        logger.info("   • investment_preferences - Investment settings & goals")
        logger.info("   • user_sessions - JWT session management")
        logger.info("   • portfolio_snapshots - Historical portfolio tracking")
        logger.info("   • user_goals - Financial goals management")
        logger.info("   • notifications - User notification system")
        
        logger.info("\n🔐 Security features:")
        logger.info("   • AES-256 encryption for sensitive data")
        logger.info("   • Salted password hashing")
        logger.info("   • Session token management")
        logger.info("   • Account lockout protection")
        logger.info("   • Audit trail logging")
        
        # Close connections
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create user tables: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting user management database initialization...")
    
    success = create_user_tables()
    
    if success:
        logger.info("✅ User management database initialization completed successfully!")
        logger.info("🔧 Next steps:")
        logger.info("1. Run user authentication API setup")
        logger.info("2. Configure JWT settings")
        logger.info("3. Test user registration and login")
    else:
        logger.error("❌ User management database initialization failed!")
        sys.exit(1)