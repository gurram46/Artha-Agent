"""Enhanced Database Connection Manager with Pooling and Retry Logic

Provides robust database connection management with:
- Advanced connection pooling configuration
- Automatic retry logic with exponential backoff
- Connection health monitoring
- Graceful error handling and recovery
- Performance metrics and monitoring
"""

import os
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, TypeVar, Union
from contextlib import contextmanager, asynccontextmanager
from functools import wraps

from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.exc import (
    SQLAlchemyError, 
    DisconnectionError, 
    OperationalError, 
    TimeoutError as SQLTimeoutError,
    InvalidRequestError
)
# from sqlalchemy.engine.events import PoolEvents  # Not available in current SQLAlchemy version

# Configure logging
logger = logging.getLogger(__name__)

# Type hints
T = TypeVar('T')
RetryableFunc = Callable[..., T]

class DatabaseConnectionManager:
    """Enhanced database connection manager with pooling and retry logic"""
    
    def __init__(self, database_url: str, **kwargs):
        self.database_url = database_url
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'retry_attempts': 0,
            'last_health_check': None,
            'pool_size': 0,
            'checked_out': 0,
            'overflow': 0,
            'invalid': 0
        }
        
        # Configuration with environment variable support
        self.config = {
            'pool_size': kwargs.get('pool_size', int(os.getenv('DB_POOL_SIZE', '20'))),
            'max_overflow': kwargs.get('max_overflow', int(os.getenv('DB_MAX_OVERFLOW', '30'))),
            'pool_timeout': kwargs.get('pool_timeout', int(os.getenv('DB_POOL_TIMEOUT', '30'))),
            'pool_recycle': kwargs.get('pool_recycle', int(os.getenv('DB_POOL_RECYCLE', '3600'))),
            'pool_pre_ping': kwargs.get('pool_pre_ping', os.getenv('DB_POOL_PRE_PING', 'true').lower() == 'true'),
            'connect_timeout': kwargs.get('connect_timeout', int(os.getenv('DB_CONNECT_TIMEOUT', '10'))),
            'max_retries': kwargs.get('max_retries', int(os.getenv('DB_MAX_RETRIES', '3'))),
            'retry_delay': kwargs.get('retry_delay', float(os.getenv('DB_RETRY_DELAY', '1.0'))),
            'retry_backoff': kwargs.get('retry_backoff', float(os.getenv('DB_RETRY_BACKOFF', '2.0'))),
            'retry_max_delay': kwargs.get('retry_max_delay', float(os.getenv('DB_RETRY_MAX_DELAY', '10.0'))),
            'health_check_interval': kwargs.get('health_check_interval', int(os.getenv('DB_HEALTH_CHECK_INTERVAL', '300'))),
            'echo': kwargs.get('echo', os.getenv('DEBUG', 'false').lower() == 'true')
        }
        
        self._initialize_engine()
        self._setup_event_listeners()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with advanced pooling configuration"""
        try:
            # Determine pool class based on database type
            if 'sqlite' in self.database_url.lower():
                poolclass = StaticPool
                pool_kwargs = {
                    'poolclass': poolclass,
                    'connect_args': {'check_same_thread': False}
                }
            else:
                poolclass = QueuePool
                pool_kwargs = {
                    'poolclass': poolclass,
                    'pool_size': self.config['pool_size'],
                    'max_overflow': self.config['max_overflow'],
                    'pool_timeout': self.config['pool_timeout'],
                    'pool_recycle': self.config['pool_recycle'],
                }
            
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=self.config['pool_pre_ping'],
                echo=self.config['echo'],
                future=True,
                connect_args={
                    'connect_timeout': self.config['connect_timeout']
                },
                **pool_kwargs
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            logger.info(f"✅ Database engine initialized with {poolclass.__name__}")
            logger.info(f"📊 Pool configuration: size={self.config['pool_size']}, overflow={self.config['max_overflow']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database engine: {e}")
            raise
    
    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for monitoring"""
        if not self.engine:
            return
        
        @event.listens_for(self.engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            self.connection_stats['total_connections'] += 1
            logger.debug("🔗 New database connection established")
        
        @event.listens_for(self.engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            self.connection_stats['active_connections'] += 1
        
        @event.listens_for(self.engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            self.connection_stats['active_connections'] = max(0, self.connection_stats['active_connections'] - 1)
        
        @event.listens_for(self.engine, "invalidate")
        def on_invalidate(dbapi_connection, connection_record, exception):
            self.connection_stats['failed_connections'] += 1
            logger.warning(f"⚠️ Database connection invalidated: {exception}")
    
    def with_retry(self, max_retries: Optional[int] = None, delay: Optional[float] = None):
        """Decorator for adding retry logic to database operations"""
        max_retries = max_retries or self.config['max_retries']
        delay = delay or self.config['retry_delay']
        
        def decorator(func: RetryableFunc) -> RetryableFunc:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except (DisconnectionError, OperationalError, SQLTimeoutError) as e:
                        last_exception = e
                        self.connection_stats['retry_attempts'] += 1
                        
                        if attempt < max_retries:
                            # Exponential backoff with configurable parameters
                            retry_delay = min(
                                delay * (self.config['retry_backoff'] ** attempt),
                                self.config['retry_max_delay']
                            )
                            logger.warning(
                                f"⚠️ Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                            )
                            logger.info(f"🔄 Retrying in {retry_delay:.2f} seconds...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"❌ Database operation failed after {max_retries + 1} attempts: {e}")
                    except Exception as e:
                        # Non-retryable exceptions
                        logger.error(f"❌ Non-retryable database error: {e}")
                        raise
                
                raise last_exception
            return wrapper
        return decorator
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup and error handling"""
        if not self.session_factory:
            raise RuntimeError("Database connection manager not initialized")
        
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Database session error: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session (if using async SQLAlchemy)"""
        # Note: This would require async SQLAlchemy setup
        # For now, we'll use the sync version in a thread pool
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def get_sync_session():
            return self.get_session()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            session_context = await loop.run_in_executor(executor, get_sync_session)
            try:
                yield session_context
            finally:
                pass  # Context manager handles cleanup
    
    def execute_with_retry(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a query with retry logic"""
        @self.with_retry()
        def _execute():
            with self.get_session() as session:
                if params:
                    return session.execute(text(query), params).fetchall()
                else:
                    return session.execute(text(query)).fetchall()
        
        return _execute()
    
    def test_connection(self) -> bool:
        """Test database connection with retry logic"""
        @self.with_retry(max_retries=1)
        def _test():
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return True
        
        try:
            result = _test()
            self.connection_stats['last_health_check'] = datetime.utcnow()
            logger.info("✅ Database connection test successful")
            return result
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status"""
        if not self.engine or not hasattr(self.engine.pool, 'size'):
            return {'error': 'Pool information not available'}
        
        pool = self.engine.pool
        return {
            'pool_size': getattr(pool, 'size', lambda: 0)(),
            'checked_out': getattr(pool, 'checkedout', lambda: 0)(),
            'overflow': getattr(pool, 'overflow', lambda: 0)(),
            'checked_in': getattr(pool, 'checkedin', lambda: 0)(),
            'invalid': getattr(pool, 'invalid', lambda: 0)(),
            'total_connections': self.connection_stats['total_connections'],
            'active_connections': self.connection_stats['active_connections'],
            'failed_connections': self.connection_stats['failed_connections'],
            'retry_attempts': self.connection_stats['retry_attempts'],
            'last_health_check': self.connection_stats['last_health_check']
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            'healthy': False,
            'timestamp': datetime.utcnow().isoformat(),
            'connection_test': False,
            'pool_status': {},
            'errors': []
        }
        
        try:
            # Test connection
            health_status['connection_test'] = self.test_connection()
            
            # Get pool status
            health_status['pool_status'] = self.get_pool_status()
            
            # Check for issues
            pool_status = health_status['pool_status']
            if isinstance(pool_status, dict):
                if pool_status.get('failed_connections', 0) > 10:
                    health_status['errors'].append('High number of failed connections')
                
                if pool_status.get('retry_attempts', 0) > 50:
                    health_status['errors'].append('High number of retry attempts')
            
            health_status['healthy'] = (
                health_status['connection_test'] and 
                len(health_status['errors']) == 0
            )
            
        except Exception as e:
            health_status['errors'].append(f'Health check failed: {str(e)}')
            logger.error(f"❌ Database health check failed: {e}")
        
        return health_status
    
    def close(self):
        """Close database connections and cleanup resources"""
        if self.engine:
            try:
                self.engine.dispose()
                logger.info("✅ Database connections closed")
            except Exception as e:
                logger.error(f"❌ Error closing database connections: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Global connection manager instance
_connection_manager: Optional[DatabaseConnectionManager] = None

def get_connection_manager(database_url: Optional[str] = None) -> DatabaseConnectionManager:
    """Get or create global connection manager instance"""
    global _connection_manager
    
    if _connection_manager is None:
        if not database_url:
            # Import here to avoid circular imports
            from .config import get_database_url
            database_url = get_database_url()
        
        _connection_manager = DatabaseConnectionManager(database_url)
    
    return _connection_manager

def close_connection_manager():
    """Close global connection manager"""
    global _connection_manager
    if _connection_manager:
        _connection_manager.close()
        _connection_manager = None

# Convenience functions for backward compatibility
def get_db_session():
    """Get database session using connection manager"""
    manager = get_connection_manager()
    return manager.get_session()

def execute_with_retry(query: str, params: Optional[Dict] = None):
    """Execute query with retry logic"""
    manager = get_connection_manager()
    return manager.execute_with_retry(query, params)

def test_db_connection() -> bool:
    """Test database connection"""
    manager = get_connection_manager()
    return manager.test_connection()

def get_db_health() -> Dict[str, Any]:
    """Get database health status"""
    manager = get_connection_manager()
    return manager.health_check()