"""
Chat Database Initialization Script
===================================

Creates the necessary database tables for chat functionality.
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

def create_chat_tables():
    """
    Create all chat-related database tables
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
        
        # Create chat_conversations table
        logger.info("📝 Creating chat_conversations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id VARCHAR(36) PRIMARY KEY,
                user_id_hash VARCHAR(64) NOT NULL,
                title VARCHAR(255),
                agent_mode VARCHAR(50) NOT NULL DEFAULT 'quick',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_archived BOOLEAN DEFAULT FALSE,
                is_favorite BOOLEAN DEFAULT FALSE,
                message_count INTEGER DEFAULT 0,
                total_tokens_used INTEGER DEFAULT 0,
                summary TEXT,
                tags TEXT[],
                financial_context_encrypted BYTEA,
                financial_context_nonce BYTEA,
                financial_context_auth_tag BYTEA
            );
        """)
        
        # Create indexes for chat_conversations
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id_hash 
            ON chat_conversations(user_id_hash);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_created_at 
            ON chat_conversations(created_at DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_last_message_at 
            ON chat_conversations(last_message_at DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_is_active 
            ON chat_conversations(is_active);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_is_archived 
            ON chat_conversations(is_archived);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_conversations_is_favorite 
            ON chat_conversations(is_favorite);
        """)
        
        logger.info("✅ chat_conversations table created successfully")
        
        # Create chat_messages table
        logger.info("📝 Creating chat_messages table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id VARCHAR(36) PRIMARY KEY,
                conversation_id VARCHAR(36) NOT NULL,
                message_type VARCHAR(20) NOT NULL,
                content_encrypted BYTEA NOT NULL,
                content_nonce BYTEA NOT NULL,
                content_auth_tag BYTEA NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                agent_mode VARCHAR(50),
                tokens_used INTEGER DEFAULT 0,
                processing_time FLOAT DEFAULT 0.0,
                metadata JSONB,
                is_deleted BOOLEAN DEFAULT FALSE,
                is_edited BOOLEAN DEFAULT FALSE,
                financial_snapshot_encrypted BYTEA,
                financial_snapshot_nonce BYTEA,
                financial_snapshot_auth_tag BYTEA,
                FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE
            );
        """)
        
        # Create indexes for chat_messages
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id 
            ON chat_messages(conversation_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at 
            ON chat_messages(created_at DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_message_type 
            ON chat_messages(message_type);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_is_deleted 
            ON chat_messages(is_deleted);
        """)
        
        logger.info("✅ chat_messages table created successfully")
        
        # Create chat_analytics table
        logger.info("📝 Creating chat_analytics table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_analytics (
                id SERIAL PRIMARY KEY,
                user_id_hash VARCHAR(64) NOT NULL,
                date DATE NOT NULL,
                conversations_created INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                total_tokens_used INTEGER DEFAULT 0,
                avg_processing_time FLOAT DEFAULT 0.0,
                agent_modes_used JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id_hash, date)
            );
        """)
        
        # Create indexes for chat_analytics
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_analytics_user_id_hash 
            ON chat_analytics(user_id_hash);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_analytics_date 
            ON chat_analytics(date DESC);
        """)
        
        logger.info("✅ chat_analytics table created successfully")
        
        # Create chat_feedback table
        logger.info("📝 Creating chat_feedback table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_feedback (
                id VARCHAR(36) PRIMARY KEY,
                user_id_hash VARCHAR(64) NOT NULL,
                message_id VARCHAR(36) NOT NULL,
                feedback_type VARCHAR(20) NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                feedback_text_encrypted BYTEA,
                feedback_text_nonce BYTEA,
                feedback_text_auth_tag BYTEA,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE
            );
        """)
        
        # Create indexes for chat_feedback
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_feedback_user_id_hash 
            ON chat_feedback(user_id_hash);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_feedback_message_id 
            ON chat_feedback(message_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_feedback_feedback_type 
            ON chat_feedback(feedback_type);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_feedback_created_at 
            ON chat_feedback(created_at DESC);
        """)
        
        logger.info("✅ chat_feedback table created successfully")
        
        # Create triggers for updating timestamps
        logger.info("📝 Creating triggers...")
        
        # Trigger for updating updated_at in chat_conversations
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_conversation_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp 
            ON chat_conversations;
        """)
        
        cursor.execute("""
            CREATE TRIGGER trigger_update_conversation_timestamp
                BEFORE UPDATE ON chat_conversations
                FOR EACH ROW
                EXECUTE FUNCTION update_conversation_timestamp();
        """)
        
        # Trigger for updating last_message_at when messages are added
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_last_message_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE chat_conversations 
                SET last_message_at = NEW.created_at,
                    message_count = message_count + 1,
                    total_tokens_used = total_tokens_used + NEW.tokens_used
                WHERE id = NEW.conversation_id;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_last_message_timestamp 
            ON chat_messages;
        """)
        
        cursor.execute("""
            CREATE TRIGGER trigger_update_last_message_timestamp
                AFTER INSERT ON chat_messages
                FOR EACH ROW
                EXECUTE FUNCTION update_last_message_timestamp();
        """)
        
        logger.info("✅ Triggers created successfully")
        
        # Display table structures
        logger.info("\n" + "="*60)
        logger.info("📊 CHAT DATABASE SCHEMA CREATED SUCCESSFULLY")
        logger.info("="*60)
        
        # Show chat_conversations structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'chat_conversations'
            ORDER BY ordinal_position;
        """)
        
        logger.info("\n🗂️  chat_conversations table structure:")
        for row in cursor.fetchall():
            logger.info(f"   {row[0]:<25} | {row[1]:<20} | Nullable: {row[2]:<3} | Default: {row[3] or 'None'}")
        
        # Show chat_messages structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'chat_messages'
            ORDER BY ordinal_position;
        """)
        
        logger.info("\n💬 chat_messages table structure:")
        for row in cursor.fetchall():
            logger.info(f"   {row[0]:<25} | {row[1]:<20} | Nullable: {row[2]:<3} | Default: {row[3] or 'None'}")
        
        # Show chat_analytics structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'chat_analytics'
            ORDER BY ordinal_position;
        """)
        
        logger.info("\n📈 chat_analytics table structure:")
        for row in cursor.fetchall():
            logger.info(f"   {row[0]:<25} | {row[1]:<20} | Nullable: {row[2]:<3} | Default: {row[3] or 'None'}")
        
        # Show chat_feedback structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'chat_feedback'
            ORDER BY ordinal_position;
        """)
        
        logger.info("\n👍 chat_feedback table structure:")
        for row in cursor.fetchall():
            logger.info(f"   {row[0]:<25} | {row[1]:<20} | Nullable: {row[2]:<3} | Default: {row[3] or 'None'}")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 CHAT SYSTEM DATABASE INITIALIZATION COMPLETE!")
        logger.info("="*60)
        
        # Close connections
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create chat tables: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting chat database initialization...")
    
    success = create_chat_tables()
    
    if success:
        logger.info("✅ Chat database initialization completed successfully!")
    else:
        logger.error("❌ Chat database initialization failed!")
        sys.exit(1)