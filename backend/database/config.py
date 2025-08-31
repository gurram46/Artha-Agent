"""
Artha AI - Database Configuration
================================

SQLAlchemy models and database configuration for the secure cache system.
Supports PostgreSQL with encrypted data storage and automatic cleanup.
"""

import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from typing import Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class SecureCache(Base):
    """
    Secure cache table for storing encrypted financial data
    
    Features:
    - AES-256 encrypted data storage
    - Automatic expiration tracking
    - User-based data isolation
    - Performance optimized with indexes
    """
    __tablename__ = 'secure_cache'
    
    # Primary key: user email (hashed for privacy)
    user_email_hash = Column(String(64), primary_key=True, index=True)
    
    # Encrypted financial data (JSONB equivalent as Text)
    encrypted_data = Column(Text, nullable=False)
    
    # Encryption metadata
    encryption_nonce = Column(String(32), nullable=False)
    encryption_tag = Column(String(32), nullable=False)
    
    # Timestamps
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Cache metadata
    data_size_bytes = Column(String(20), nullable=True)  # Store as string to avoid integer overflow
    cache_version = Column(String(10), default='1.0', nullable=False)
    
    # Performance indexes
    __table_args__ = (
        Index('idx_expires_at', 'expires_at'),
        Index('idx_cached_at', 'cached_at'),
        Index('idx_user_expires', 'user_email_hash', 'expires_at'),
    )
    
    def is_expired(self):
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at
    
    def time_until_expiry(self):
        """Get time remaining until expiry"""
        if self.is_expired():
            return timedelta(0)
        return self.expires_at - datetime.utcnow()
    
    def __repr__(self):
        return f"<SecureCache(user_hash={self.user_email_hash[:8]}..., expires={self.expires_at})>"

class CacheAuditLog(Base):
    """
    Audit log for cache operations
    
    Tracks all cache operations for security and debugging
    """
    __tablename__ = 'cache_audit_log'
    
    # Auto-incrementing ID
    id = Column(String(36), primary_key=True)  # UUID
    
    # User and operation details
    user_email_hash = Column(String(64), nullable=False, index=True)
    operation = Column(String(20), nullable=False)  # 'store', 'retrieve', 'delete', 'cleanup'
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Operation metadata
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    data_size_bytes = Column(String(20), nullable=True)
    
    # Performance indexes
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_user_operation', 'user_email_hash', 'operation'),
        Index('idx_operation_timestamp', 'operation', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<CacheAuditLog(operation={self.operation}, user_hash={self.user_email_hash[:8]}..., timestamp={self.timestamp})>"

# Database configuration
def get_database_url():
    """Get database URL from environment variables"""
    # Try new environment variables first
    host = os.getenv('CACHE_DB_HOST', 'localhost')
    port = os.getenv('CACHE_DB_PORT', '5432')
    name = os.getenv('CACHE_DB_NAME', 'artha_cache')
    user = os.getenv('CACHE_DB_USER', 'postgres')
    password = os.getenv('CACHE_DB_PASSWORD', '')
    
    if password:
        new_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    else:
        new_url = f"postgresql://{user}@{host}:{port}/{name}"
    
    # Fallback to old DATABASE_URL if new variables not set
    return os.getenv('DATABASE_URL', new_url)

# Import enhanced connection manager
from .connection_manager import get_connection_manager, get_db_session, test_db_connection as test_conn_manager

# Create SQLAlchemy engine with connection pooling (legacy support)
def create_engine_instance():
    """Create SQLAlchemy engine with optimized settings (legacy)"""
    database_url = get_database_url()
    
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,  # Set to True for SQL debugging
        future=True
    )

# Enhanced connection manager (recommended)
connection_manager = get_connection_manager()
engine = connection_manager.engine

# Create SessionLocal class (legacy support)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Database dependency for FastAPI with enhanced connection management
    """
    with connection_manager.get_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"❌ Database session error in FastAPI dependency: {e}")
            raise

def get_session():
    """Get database session with enhanced connection management"""
    return connection_manager.get_session()

def test_connection() -> bool:
    """
    Test database connection with retry logic
    """
    return connection_manager.test_connection()

def create_tables():
    """
    Create all database tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        logger.info(f"   📊 Tables: {', '.join(Base.metadata.tables.keys())}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        return False

@connection_manager.with_retry()
def cleanup_expired_cache():
    """Clean up expired cache entries with retry logic"""
    try:
        with connection_manager.get_session() as session:
            # Find expired entries
            expired_entries = session.query(SecureCache).filter(
                SecureCache.expires_at < datetime.utcnow()
            ).all()
            
            count = len(expired_entries)
            
            if count > 0:
                # Delete expired entries
                session.query(SecureCache).filter(
                    SecureCache.expires_at < datetime.utcnow()
                ).delete()
                
                logger.info(f"🧹 Cleaned up {count} expired cache entries")
            else:
                logger.info("🧹 No expired cache entries to clean up")
            
            return count
        
    except Exception as e:
        logger.error(f"❌ Cache cleanup failed: {e}")
        return 0

@connection_manager.with_retry()
def get_cache_stats():
    """Get cache system statistics with retry logic"""
    try:
        with connection_manager.get_session() as session:
            # Total cached users
            total_users = session.query(SecureCache).count()
            
            # Active (non-expired) users
            active_users = session.query(SecureCache).filter(
                SecureCache.expires_at > datetime.utcnow()
            ).count()
            
            # Expired users
            expired_users = total_users - active_users
            
            # Recent activity (last 24 hours)
            recent_activity = session.query(CacheAuditLog).filter(
                CacheAuditLog.timestamp > datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            # Get connection pool stats
            pool_stats = connection_manager.get_pool_status()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'expired_users': expired_users,
                'recent_activity_24h': recent_activity,
                'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
                'connection_pool': pool_stats
            }
        
    except Exception as e:
        logger.error(f"❌ Failed to get cache stats: {e}")
        return {
            'total_users': 0,
            'active_users': 0,
            'expired_users': 0,
            'recent_activity_24h': 0,
            'cache_enabled': False,
            'connection_pool': {},
            'error': str(e)
        }

# Initialize database on import (for production)
if __name__ != "__main__":
    try:
        # Only test connection, don't create tables automatically
        test_connection()
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")

if __name__ == "__main__":
    # Direct execution for testing
    print("🔧 Testing database configuration...")
    
    if test_connection():
        print("✅ Database connection successful")
        
        if create_tables():
            print("✅ Tables created successfully")
            
            # Test cache stats
            stats = get_cache_stats()
            print(f"📊 Cache stats: {stats}")
        else:
            print("❌ Failed to create tables")
    else:
        print("❌ Database connection failed")