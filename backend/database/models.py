"""
Database Models for Artha AI Secure Caching System
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timedelta
from database.config import Base
import uuid

class CachedFinancialData(Base):
    """
    Model for storing encrypted financial data with 24-hour expiration
    """
    __tablename__ = "cached_financial_data"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User identification (hashed email)
    user_id = Column(String, nullable=False, index=True)
    
    # Encrypted financial data (JSONB for efficient querying)
    encrypted_data = Column(JSONB, nullable=False)
    
    # Metadata
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Data source and version tracking
    data_source = Column(String, default="fi_mcp", nullable=False)
    data_version = Column(String, default="1.0", nullable=False)
    
    # Security and audit fields
    encryption_version = Column(String, default="aes256", nullable=False)
    access_count = Column(String, default="0", nullable=False)  # Encrypted access count
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            # Set expiration to 24 hours from now
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def is_data_expired(self) -> bool:
        """Check if the cached data has expired"""
        return datetime.utcnow() > self.expires_at
    
    def mark_as_expired(self):
        """Mark the data as expired"""
        self.is_expired = True
        self.is_active = False
    
    def update_access(self):
        """Update last accessed timestamp"""
        self.last_accessed = datetime.utcnow()
    
    def __repr__(self):
        return f"<CachedFinancialData(id={self.id}, user_id={self.user_id[:8]}..., cached_at={self.cached_at})>"

class UserSession(Base):
    """
    Model for tracking user sessions and cache status
    """
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User identification
    user_id = Column(String, nullable=False, index=True)
    
    # Session tracking
    session_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Cache status
    has_cached_data = Column(Boolean, default=False, nullable=False)
    cache_expires_at = Column(DateTime, nullable=True)
    
    # MCP connection status
    mcp_connected = Column(Boolean, default=False, nullable=False)
    mcp_last_sync = Column(DateTime, nullable=True)
    
    # Session metadata
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)  # Encrypted
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def set_cache_status(self, has_cache: bool, expires_at: datetime = None):
        """Update cache status"""
        self.has_cached_data = has_cache
        self.cache_expires_at = expires_at
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id[:8]}..., session_start={self.session_start})>"

class CacheAuditLog(Base):
    """
    Model for auditing cache operations (security and compliance)
    """
    __tablename__ = "cache_audit_log"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User and operation tracking
    user_id = Column(String, nullable=False, index=True)
    operation = Column(String, nullable=False)  # CREATE, READ, UPDATE, DELETE, EXPIRE
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Operation details
    cache_id = Column(String, nullable=True)  # Reference to cached data
    operation_details = Column(JSONB, nullable=True)  # Additional operation metadata
    
    # Security context
    ip_address = Column(String, nullable=True)  # Encrypted
    user_agent = Column(String, nullable=True)
    
    # Result
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<CacheAuditLog(id={self.id}, operation={self.operation}, timestamp={self.timestamp})>"

# Create indexes for performance
Index('idx_cached_data_user_active', CachedFinancialData.user_id, CachedFinancialData.is_active)
Index('idx_cached_data_expires', CachedFinancialData.expires_at, CachedFinancialData.is_expired)
Index('idx_user_sessions_user_activity', UserSession.user_id, UserSession.last_activity)
Index('idx_audit_log_user_timestamp', CacheAuditLog.user_id, CacheAuditLog.timestamp)