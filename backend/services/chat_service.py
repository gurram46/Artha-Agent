"""
Chat Service for Artha AI
=========================

Service for managing chat conversations, messages, and analytics.
Provides secure storage and retrieval of user chat history.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc, func, and_, or_
import logging
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import our models
from database.chat_models import ChatConversation, ChatMessage, ChatAnalytics, ChatFeedback
from database.config import get_database_url
from utils.encryption import encryption

logger = logging.getLogger(__name__)

class ChatService:
    """
    Enhanced chat service with encryption, analytics, conversation management, and caching
    """
    
    def __init__(self):
        """Initialize the chat service"""
        self.db_url = get_database_url()
        self.engine = create_engine(self.db_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        self._create_tables()
        
        # Initialize caching and performance optimizations
        self._conversation_cache = {}
        self._user_conversations_cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("✅ Chat service initialized with database connection and caching")
    
    def _create_tables(self):
        """Create chat tables if they don't exist"""
        try:
            from database.chat_models import Base
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Chat tables created/verified")
        except Exception as e:
            logger.error(f"❌ Failed to create chat tables: {e}")
            raise
    
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy"""
        return hashlib.sha256(user_id.encode()).hexdigest()
    
    def _encrypt_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt financial data for storage"""
        if not data:
            return None
        
        try:
            json_data = json.dumps(data)
            encrypted_data = encryption.encrypt_for_database(json_data)
            return encrypted_data
        except Exception as e:
            logger.error(f"❌ Failed to encrypt financial data: {e}")
            return None
    
    def _decrypt_financial_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt financial data from storage"""
        if not encrypted_data:
            return None
        
        try:
            decrypted_json = encryption.decrypt_from_database(encrypted_data)
            return json.loads(decrypted_json)
        except Exception as e:
            logger.error(f"❌ Failed to decrypt financial data: {e}")
            return None
    
    def create_conversation(self, user_id: str, agent_mode: str = 'quick', 
                          financial_context: Dict[str, Any] = None) -> str:
        """
        Create a new chat conversation
        
        Args:
            user_id: User identifier
            agent_mode: Agent mode (quick, comprehensive, research, investment, etc.)
            financial_context: User's financial context
            
        Returns:
            Conversation ID
        """
        try:
            hashed_user_id = self._hash_user_id(user_id)
            encrypted_context = self._encrypt_financial_data(financial_context)
            
            with self.SessionLocal() as session:
                conversation = ChatConversation(
                    user_id=hashed_user_id,
                    agent_mode=agent_mode,
                    financial_context=encrypted_context
                )
                
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                
                logger.info(f"✅ Created conversation {conversation.id} for user {user_id[:8]}...")
                return conversation.id
                
        except Exception as e:
            logger.error(f"❌ Failed to create conversation: {e}")
            raise
    
    def add_message(self, conversation_id: str, message_type: str, content: str,
                   agent_mode: str = None, tokens_used: int = 0, 
                   processing_time: float = 0.0, metadata: Dict[str, Any] = None,
                   financial_snapshot: Dict[str, Any] = None) -> str:
        """
        Add a message to a conversation with cache invalidation
        
        Args:
            conversation_id: Conversation ID
            message_type: 'user', 'assistant', or 'system'
            content: Message content
            agent_mode: Agent mode used
            tokens_used: Number of tokens used
            processing_time: Response processing time
            metadata: Additional message metadata
            financial_snapshot: Financial data snapshot at message time
            
        Returns:
            Message ID
        """
        try:
            encrypted_snapshot = self._encrypt_financial_data(financial_snapshot)
            
            with self.SessionLocal() as session:
                # Get conversation to update it
                conversation = session.query(ChatConversation).filter_by(id=conversation_id).first()
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found")
                
                # Create message
                message = ChatMessage(
                    conversation_id=conversation_id,
                    message_type=message_type,
                    content=content,
                    agent_mode=agent_mode,
                    tokens_used=tokens_used,
                    processing_time=processing_time,
                    metadata=metadata,
                    financial_snapshot=encrypted_snapshot
                )
                
                session.add(message)
                
                # Update conversation
                conversation.update_last_message()
                conversation.total_tokens_used += tokens_used
                
                # Auto-generate title from first user message
                if not conversation.title and message_type == 'user' and conversation.message_count == 1:
                    conversation.title = conversation.generate_title(content)
                
                session.commit()
                session.refresh(message)
                
                # Invalidate cache for this conversation and user
                self._invalidate_conversation_cache(conversation_id)
                self.invalidate_user_cache(conversation.user_id)
                
                logger.info(f"✅ Added {message_type} message to conversation {conversation_id}")
                return message.id
                
        except Exception as e:
            logger.error(f"❌ Failed to add message: {e}")
            raise
    
    def _invalidate_conversation_cache(self, conversation_id: str):
        """Invalidate cache for a specific conversation"""
        cache_key = f"conv_{conversation_id}"
        if cache_key in self._conversation_cache:
            del self._conversation_cache[cache_key]
            logger.debug(f"✅ Invalidated cache for conversation {conversation_id}")
    
    def get_user_conversations(self, user_id: str, limit: int = 50, 
                              include_archived: bool = False) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
            include_archived: Whether to include archived conversations
            
        Returns:
            List of conversation dictionaries
        """
        try:
            hashed_user_id = self._hash_user_id(user_id)
            
            with self.SessionLocal() as session:
                query = session.query(ChatConversation).filter_by(user_id=hashed_user_id)
                
                if not include_archived:
                    query = query.filter_by(is_archived=False)
                
                conversations = query.order_by(desc(ChatConversation.updated_at)).limit(limit).all()
                
                result = []
                for conv in conversations:
                    result.append({
                        "id": conv.id,
                        "title": conv.title,
                        "agent_mode": conv.agent_mode,
                        "created_at": conv.created_at.isoformat(),
                        "updated_at": conv.updated_at.isoformat(),
                        "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                        "is_active": conv.is_active,
                        "is_archived": conv.is_archived,
                        "is_favorite": conv.is_favorite,
                        "message_count": conv.message_count,
                        "total_tokens_used": conv.total_tokens_used,
                        "summary": conv.summary,
                        "tags": conv.tags
                    })
                
                logger.info(f"✅ Retrieved {len(result)} conversations for user {user_id[:8]}...")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get user conversations: {e}")
            raise
    
    def get_conversation_history(self, user_id: str, conversation_id: str, 
                               include_deleted: bool = False) -> Dict[str, Any]:
        """
        Get conversation history with all messages
        
        Args:
            user_id: User identifier
            conversation_id: Conversation ID
            include_deleted: Whether to include deleted messages
            
        Returns:
            Dictionary with conversation and messages
        """
        try:
            hashed_user_id = self._hash_user_id(user_id)
            
            with self.SessionLocal() as session:
                # Get conversation
                conversation = session.query(ChatConversation).filter_by(
                    id=conversation_id, 
                    user_id=hashed_user_id
                ).first()
                
                if not conversation:
                    return None
                
                # Get messages
                query = session.query(ChatMessage).filter_by(conversation_id=conversation_id)
                
                if not include_deleted:
                    query = query.filter_by(is_deleted=False)
                
                messages = query.order_by(ChatMessage.created_at).all()
                
                # Format conversation
                conv_data = {
                    "id": conversation.id,
                    "title": conversation.title,
                    "agent_mode": conversation.agent_mode,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                    "last_message_at": conversation.last_message_at.isoformat() if conversation.last_message_at else None,
                    "is_active": conversation.is_active,
                    "is_archived": conversation.is_archived,
                    "is_favorite": conversation.is_favorite,
                    "message_count": conversation.message_count,
                    "total_tokens_used": conversation.total_tokens_used,
                    "summary": conversation.summary,
                    "tags": conversation.tags
                }
                
                # Format messages
                message_data = []
                for msg in messages:
                    message_data.append({
                        "id": msg.id,
                        "type": msg.message_type,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat(),
                        "agent_mode": msg.agent_mode,
                        "tokens_used": msg.tokens_used,
                        "processing_time": msg.processing_time,
                        "metadata": msg.metadata,
                        "is_edited": msg.is_edited
                    })
                
                # Decrypt financial context
                financial_context = self._decrypt_financial_data(conversation.financial_context)
                
                result = {
                    "conversation": conv_data,
                    "messages": message_data,
                    "financial_context": financial_context
                }
                
                logger.info(f"✅ Retrieved conversation {conversation_id} with {len(message_data)} messages")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to get conversation history: {e}")
            raise
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid based on TTL"""
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
        
        cache_age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        return cache_age < self._cache_ttl
    
    def _get_cached_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation from cache if valid"""
        cache_key = f"conv_{conversation_id}"
        if cache_key in self._conversation_cache:
            cache_entry = self._conversation_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(f"✅ Cache hit for conversation {conversation_id}")
                return cache_entry['data']
            else:
                # Remove expired cache entry
                del self._conversation_cache[cache_key]
        return None
    
    def _cache_conversation(self, conversation_id: str, data: Dict[str, Any]):
        """Cache conversation data with timestamp"""
        cache_key = f"conv_{conversation_id}"
        self._conversation_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        logger.debug(f"✅ Cached conversation {conversation_id}")
    
    def _get_cached_user_conversations(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get user conversations from cache if valid"""
        cache_key = f"user_{user_id}_convs"
        if cache_key in self._user_conversations_cache:
            cache_entry = self._user_conversations_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(f"✅ Cache hit for user {user_id} conversations")
                return cache_entry['data']
            else:
                # Remove expired cache entry
                del self._user_conversations_cache[cache_key]
        return None
    
    def _cache_user_conversations(self, user_id: str, data: List[Dict[str, Any]]):
        """Cache user conversations data with timestamp"""
        cache_key = f"user_{user_id}_convs"
        self._user_conversations_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        logger.debug(f"✅ Cached conversations for user {user_id}")
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a specific user"""
        # Remove user conversations cache
        cache_key = f"user_{user_id}_convs"
        if cache_key in self._user_conversations_cache:
            del self._user_conversations_cache[cache_key]
        
        # Remove conversation caches for this user
        keys_to_remove = []
        for key in self._conversation_cache.keys():
            if key.startswith(f"conv_"):
                # Check if conversation belongs to this user (would need DB lookup)
                # For now, we'll implement a simple cleanup
                keys_to_remove.append(key)
        
        for key in keys_to_remove[:10]:  # Limit cleanup to avoid performance issues
            del self._conversation_cache[key]
        
        logger.info(f"✅ Invalidated cache for user {user_id}")
    
    def clear_expired_cache(self):
        """Clear all expired cache entries"""
        current_time = datetime.now()
        
        # Clear expired conversation cache
        expired_conv_keys = []
        for key, entry in self._conversation_cache.items():
            if (current_time - entry['timestamp']).total_seconds() > self._cache_ttl:
                expired_conv_keys.append(key)
        
        for key in expired_conv_keys:
            del self._conversation_cache[key]
        
        # Clear expired user conversations cache
        expired_user_keys = []
        for key, entry in self._user_conversations_cache.items():
            if (current_time - entry['timestamp']).total_seconds() > self._cache_ttl:
                expired_user_keys.append(key)
        
        for key in expired_user_keys:
            del self._user_conversations_cache[key]
        
        if expired_conv_keys or expired_user_keys:
            logger.info(f"✅ Cleared {len(expired_conv_keys)} conversation and {len(expired_user_keys)} user cache entries")
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """Get a specific conversation by ID - required by API endpoints"""
        try:
            return await self.get_conversation_history_async(user_id, conversation_id)
        except Exception as e:
            logger.error(f"❌ Failed to get conversation {conversation_id}: {e}")
            return None

    async def get_conversation_history_async(self, user_id: str, conversation_id: str, 
                                           include_deleted: bool = False) -> Dict[str, Any]:
        """Async version of get_conversation_history with caching"""
        # Check cache first
        cached_data = self._get_cached_conversation(conversation_id)
        if cached_data:
            return cached_data
        
        # Run sync method in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            self.get_conversation_history,
            user_id,
            conversation_id,
            include_deleted
        )
        
        # Cache the result
        if result:
            self._cache_conversation(conversation_id, result)
        
        return result
    
    async def get_user_conversations_async(self, user_id: str, limit: int = 50, 
                                         include_archived: bool = False) -> List[Dict[str, Any]]:
        """Async version of get_user_conversations with caching"""
        # Check cache first
        cached_data = self._get_cached_user_conversations(user_id)
        if cached_data:
            return cached_data[:limit]  # Apply limit to cached data
        
        # Run database query in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            self.get_user_conversations,
            user_id,
            limit,
            include_archived
        )
        
        # Cache the result
        if result:
            self._cache_user_conversations(user_id, result)
        
        return result
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            'conversation_cache_size': len(self._conversation_cache),
            'user_conversations_cache_size': len(self._user_conversations_cache),
            'cache_ttl_seconds': self._cache_ttl,
            'executor_threads': self._executor._max_workers
        }