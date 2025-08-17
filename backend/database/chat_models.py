"""
Chat Conversation Models for Artha AI
=====================================

Database models for storing user chat conversations, messages, and chat analytics.
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database.config import Base
import uuid

class ChatConversation(Base):
    """
    Model for storing chat conversations/sessions
    """
    __tablename__ = "chat_conversations"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User identification (hashed email or user ID)
    user_id = Column(String, nullable=False, index=True)
    
    # Conversation metadata
    title = Column(String, nullable=True)  # Auto-generated or user-defined title
    agent_mode = Column(String, nullable=False, default='quick')  # quick, comprehensive, research, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Conversation status
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    
    # Analytics
    message_count = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    
    # Financial context (encrypted)
    financial_context = Column(JSON, nullable=True)  # Encrypted financial data snapshot
    
    # Conversation summary (AI-generated)
    summary = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags for categorization
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def update_last_message(self):
        """Update last message timestamp and increment message count"""
        self.last_message_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.message_count += 1
    
    def archive_conversation(self):
        """Archive the conversation"""
        self.is_archived = True
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        self.is_favorite = not self.is_favorite
        self.updated_at = datetime.utcnow()
    
    def generate_title(self, first_message: str) -> str:
        """Generate a title from the first message"""
        if len(first_message) > 50:
            return first_message[:47] + "..."
        return first_message
    
    def __repr__(self):
        return f"<ChatConversation(id={self.id}, user_id={self.user_id[:8]}..., title={self.title})>"

class ChatMessage(Base):
    """
    Model for storing individual chat messages
    """
    __tablename__ = "chat_messages"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to conversation
    conversation_id = Column(String, ForeignKey('chat_conversations.id'), nullable=False, index=True)
    
    # Message metadata
    message_type = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Message context
    agent_mode = Column(String, nullable=True)  # Which agent mode was used
    tokens_used = Column(Integer, default=0, nullable=False)
    processing_time = Column(Float, default=0.0, nullable=False)  # Response time in seconds
    
    # Message metadata
    message_metadata = Column(JSON, nullable=True)  # Additional message data (sources, confidence, etc.)
    
    # Financial context at time of message
    financial_snapshot = Column(JSON, nullable=True)  # Encrypted financial data at message time
    
    # Message status
    is_edited = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")
    
    def mark_as_edited(self):
        """Mark message as edited"""
        self.is_edited = True
    
    def soft_delete(self):
        """Soft delete the message"""
        self.is_deleted = True
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, type={self.message_type}, conversation_id={self.conversation_id})>"

class ChatAnalytics(Base):
    """
    Model for storing chat analytics and usage statistics
    """
    __tablename__ = "chat_analytics"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User identification
    user_id = Column(String, nullable=False, index=True)
    
    # Date for analytics (daily aggregation)
    date = Column(DateTime, nullable=False, index=True)
    
    # Usage statistics
    conversations_started = Column(Integer, default=0, nullable=False)
    messages_sent = Column(Integer, default=0, nullable=False)
    messages_received = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    
    # Agent mode usage
    quick_mode_usage = Column(Integer, default=0, nullable=False)
    comprehensive_mode_usage = Column(Integer, default=0, nullable=False)
    research_mode_usage = Column(Integer, default=0, nullable=False)
    
    # Response times
    avg_response_time = Column(Float, default=0.0, nullable=False)
    max_response_time = Column(Float, default=0.0, nullable=False)
    
    # Popular topics/tags
    popular_topics = Column(JSON, nullable=True)
    
    # Session data
    total_session_time = Column(Float, default=0.0, nullable=False)  # Total time spent in chat
    
    def __repr__(self):
        return f"<ChatAnalytics(user_id={self.user_id[:8]}..., date={self.date.date()})>"

class ChatFeedback(Base):
    """
    Model for storing user feedback on chat responses
    """
    __tablename__ = "chat_feedback"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to message
    message_id = Column(String, ForeignKey('chat_messages.id'), nullable=False, index=True)
    
    # User identification
    user_id = Column(String, nullable=False, index=True)
    
    # Feedback data
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    feedback_type = Column(String, nullable=False)  # 'helpful', 'not_helpful', 'incorrect', 'excellent'
    feedback_text = Column(Text, nullable=True)  # Optional detailed feedback
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadata
    feedback_metadata = Column(JSON, nullable=True)  # Additional feedback context
    
    def __repr__(self):
        return f"<ChatFeedback(id={self.id}, message_id={self.message_id}, rating={self.rating})>"

# Create indexes for performance optimization
Index('idx_conversations_user_active', ChatConversation.user_id, ChatConversation.is_active)
Index('idx_conversations_user_updated', ChatConversation.user_id, ChatConversation.updated_at.desc())
Index('idx_conversations_user_favorite', ChatConversation.user_id, ChatConversation.is_favorite)

Index('idx_messages_conversation_created', ChatMessage.conversation_id, ChatMessage.created_at)
Index('idx_messages_user_type', ChatMessage.message_type, ChatMessage.created_at)

Index('idx_analytics_user_date', ChatAnalytics.user_id, ChatAnalytics.date)
Index('idx_feedback_message_user', ChatFeedback.message_id, ChatFeedback.user_id)