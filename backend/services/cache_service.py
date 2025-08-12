"""
Secure Cache Service for Artha AI Financial Data
Handles 24-hour data caching with AES-256-GCM encryption and PostgreSQL
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging
import json
import uuid

from database.config import get_session, SecureCache, CacheAuditLog
from utils.encryption import encryption

logger = logging.getLogger(__name__)

class CacheService:
    """
    Service for managing secure financial data caching with PostgreSQL and AES-256-GCM
    """
    
    def __init__(self):
        self.cache_duration_hours = 24
        self.max_access_count = 1000  # Prevent abuse
        self.encryption_manager = encryption
    
    def _create_user_hash(self, email: str) -> str:
        """Create consistent user hash from email using the encryption manager"""
        return self.encryption_manager.hash_user_email(email)
    
    def _log_operation(self, session: Optional[Session], user_hash: str, operation: str, 
                      success: bool = True, details: str = None):
        """Log cache operation for audit trail"""
        try:
            audit_log = CacheAuditLog(
                id=str(uuid.uuid4()),
                user_email_hash=user_hash,
                operation=operation,
                success=success,
                error_message=details,
                timestamp=datetime.utcnow()
            )
            
            if session:
                session.add(audit_log)
                # Don't commit here - let the caller handle it
            else:
                with get_session() as new_session:
                    new_session.add(audit_log)
                    new_session.commit()
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")
    
    def cache_financial_data(self, email: str, financial_data: Dict[str, Any], 
                           data_source: str = "fi_mcp") -> bool:
        """
        Cache financial data for 24 hours with AES-256-GCM encryption
        
        Args:
            email: User email
            financial_data: Complete financial data object from MCP
            data_source: Source of the data (default: fi_mcp)
            
        Returns:
            True if caching successful, False otherwise
        """
        try:
            user_hash = self._create_user_hash(email)
            
            # Prepare data for caching
            cache_data = {
                "financial_data": financial_data,
                "cached_at": datetime.utcnow().isoformat(),
                "data_source": data_source,
                "user_email": email  # For verification
            }
            
            # Encrypt the data using GCM
            encrypted_data, nonce, auth_tag = self.encryption_manager.encrypt_for_database(cache_data)
            
            # Calculate expiry time
            expiry_time = datetime.utcnow() + timedelta(hours=self.cache_duration_hours)
            
            with get_session() as session:
                # Remove existing cache for this user
                session.query(SecureCache).filter(
                    SecureCache.user_email_hash == user_hash
                ).delete()
                
                # Create new cache entry
                cache_entry = SecureCache(
                    user_email_hash=user_hash,
                    encrypted_data=encrypted_data,
                    encryption_nonce=nonce,
                    encryption_tag=auth_tag,
                    cached_at=datetime.utcnow(),
                    expires_at=expiry_time,
                    data_size_bytes=str(len(json.dumps(financial_data)))
                )
                
                session.add(cache_entry)
                session.commit()
                
                # Log successful operation
                self._log_operation(session, user_hash, "STORE", True, 
                                  f"Data size: {len(json.dumps(financial_data))} bytes")
                
                logger.info(f"✅ Financial data cached for user (expires: {expiry_time})")
                return True
            
        except Exception as e:
            logger.error(f"Failed to cache financial data: {e}")
            self._log_operation(None, user_hash if 'user_hash' in locals() else "unknown", 
                              "STORE", False, str(e))
            return False
    
    def get_cached_financial_data(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached financial data if available and not expired
        
        Args:
            email: User email
            
        Returns:
            Financial data if available, None if expired or not found
        """
        try:
            user_hash = self._create_user_hash(email)
            
            with get_session() as session:
                # Find active, non-expired cache
                cache_entry = session.query(SecureCache).filter(
                    and_(
                        SecureCache.user_email_hash == user_hash,
                        SecureCache.expires_at > datetime.utcnow()
                    )
                ).first()
                
                if not cache_entry:
                    self._log_operation(session, user_hash, "RETRIEVE", False, 
                                      "No valid cache found")
                    return None
                
                # Decrypt data using GCM
                decrypted_data = self.encryption_manager.decrypt_from_database(
                    cache_entry.encrypted_data,
                    cache_entry.encryption_nonce,
                    cache_entry.encryption_tag
                )
                
                # Update access time
                cache_entry.last_accessed = datetime.utcnow()
                session.commit()
                
                # Log successful access
                self._log_operation(session, user_hash, "RETRIEVE", True)
                
                logger.info(f"✅ Retrieved cached data for user")
                return decrypted_data.get("financial_data")
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached data: {e}")
            self._log_operation(None, user_hash if 'user_hash' in locals() else "unknown", 
                              "RETRIEVE", False, str(e))
            return None
    
    def is_cache_available(self, email: str) -> Dict[str, Any]:
        """
        Check if user has valid cached data
        
        Args:
            email: User email
            
        Returns:
            Dict with cache status information
        """
        try:
            user_hash = self._create_user_hash(email)
            
            with get_session() as session:
                cache_entry = session.query(SecureCache).filter(
                    SecureCache.user_email_hash == user_hash
                ).first()
                
                if not cache_entry:
                    return {
                        "has_cache": False,
                        "cached": False,
                        "expired": False,
                        "expires_at": None,
                        "time_remaining": None,
                        "created_at": None,
                        "last_accessed": None,
                        "data_size": 0
                    }
                
                now = datetime.utcnow()
                is_expired = cache_entry.expires_at <= now
                time_remaining = None if is_expired else cache_entry.expires_at - now
                
                return {
                    "has_cache": not is_expired,
                    "cached": True,
                    "expired": is_expired,
                    "expires_at": cache_entry.expires_at.isoformat(),
                    "time_remaining": str(time_remaining) if time_remaining else None,
                    "created_at": cache_entry.cached_at.isoformat(),
                    "last_accessed": cache_entry.last_accessed.isoformat() if cache_entry.last_accessed else None,
                    "data_size": cache_entry.data_size_bytes
                }
            
        except Exception as e:
            logger.error(f"Failed to check cache status: {e}")
            return {"has_cache": False, "cached": False, "expired": False, "error": str(e)}
    
    def invalidate_user_cache(self, email: str) -> bool:
        """
        Manually invalidate user's cached data
        
        Args:
            email: User email
            
        Returns:
            True if invalidation successful
        """
        try:
            user_hash = self._create_user_hash(email)
            
            with get_session() as session:
                # Delete all cache entries for this user
                deleted_count = session.query(SecureCache).filter(
                    SecureCache.user_email_hash == user_hash
                ).delete()
                
                session.commit()
                
                # Log the operation
                self._log_operation(session, user_hash, "INVALIDATE", True, 
                                  f"Deleted {deleted_count} cache entries")
                
                if deleted_count > 0:
                    logger.info(f"✅ Invalidated {deleted_count} cache entries for user")
                else:
                    logger.info(f"📭 No cache found to invalidate for user")
                
                return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            self._log_operation(None, user_hash if 'user_hash' in locals() else "unknown", 
                              "INVALIDATE", False, str(e))
            return False
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired cached data (run periodically)
        
        Returns:
            Dict with cleanup statistics
        """
        try:
            with get_session() as session:
                now = datetime.utcnow()
                
                # Count expired entries
                expired_count = session.query(func.count(SecureCache.user_email_hash)).filter(
                    SecureCache.expires_at <= now
                ).scalar() or 0
                
                if expired_count == 0:
                    logger.info("🧹 No expired cache entries to clean up")
                    return {
                        "expired_entries": 0,
                        "deleted_entries": 0,
                        "deleted_logs": 0,
                        "cleanup_time": now.isoformat()
                    }
                
                # Delete expired entries
                deleted_count = session.query(SecureCache).filter(
                    SecureCache.expires_at <= now
                ).delete()
                
                # Clean up old audit logs (keep 30 days)
                old_logs_count = session.query(func.count(CacheAuditLog.id)).filter(
                    CacheAuditLog.timestamp < now - timedelta(days=30)
                ).scalar() or 0
                
                logs_deleted = session.query(CacheAuditLog).filter(
                    CacheAuditLog.timestamp < now - timedelta(days=30)
                ).delete()
                
                session.commit()
                
                # Log cleanup operation
                self._log_operation(session, 'system', 'CLEANUP', True, 
                                  f'Cleaned {deleted_count} cache entries, {logs_deleted} audit logs')
                
                stats = {
                    "expired_entries": expired_count,
                    "deleted_entries": deleted_count,
                    "deleted_logs": logs_deleted,
                    "cleanup_time": now.isoformat()
                }
                
                logger.info(f"🧹 Cleanup completed: {stats}")
                return stats
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            self._log_operation(None, 'system', 'CLEANUP', False, str(e))
            return {"error": str(e)}
    
    def get_system_cache_stats(self) -> Dict[str, Any]:
        """
        Get system-wide cache statistics
        
        Returns:
            Dict with system cache statistics
        """
        try:
            with get_session() as session:
                now = datetime.utcnow()
                
                # Total cached users
                total_users = session.query(func.count(SecureCache.user_email_hash)).scalar() or 0
                
                # Active (non-expired) cached users
                active_users = session.query(func.count(SecureCache.user_email_hash)).filter(
                    SecureCache.expires_at > now
                ).scalar() or 0
                
                # Expired cached users
                expired_users = total_users - active_users
                
                # Total data size
                total_size = session.query(func.sum(SecureCache.data_size_bytes)).scalar() or 0
                
                # Recent activity (last 24 hours)
                recent_activity = session.query(func.count(CacheAuditLog.id)).filter(
                    CacheAuditLog.timestamp > now - timedelta(hours=24)
                ).scalar() or 0
                
                # Last cleanup time
                last_cleanup = session.query(func.max(CacheAuditLog.timestamp)).filter(
                    CacheAuditLog.operation == 'CLEANUP'
                ).scalar()
                
                return {
                    'total_cached_users': total_users,
                    'active_cached_users': active_users,
                    'expired_cached_users': expired_users,
                    'total_data_size_bytes': total_size,
                    'recent_activity_24h': recent_activity,
                    'last_cleanup': last_cleanup.isoformat() if last_cleanup else None,
                    'cache_enabled': True,
                    'encryption_enabled': True
                }
                
        except Exception as e:
            logger.error(f"Failed to get system cache stats: {e}")
            return {
                'total_cached_users': 0,
                'active_cached_users': 0,
                'expired_cached_users': 0,
                'error': str(e)
            }

# Global cache service instance
cache_service = CacheService()