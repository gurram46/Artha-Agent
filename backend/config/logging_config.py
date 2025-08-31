"""Structured Logging Configuration for Artha AI Backend

Provides comprehensive logging setup with:
- Structured JSON logging
- Multiple log levels and handlers
- Request/response logging
- Performance monitoring
- Error tracking and alerting
- Log rotation and archival
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Third-party imports for enhanced logging
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    
try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging without external dependencies"""
    
    def format(self, record):
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class RequestResponseFilter(logging.Filter):
    """Filter to add request/response context to logs"""
    
    def filter(self, record):
        # Add request context if available
        if hasattr(record, 'request_id'):
            return True
        return True

class PerformanceLogger:
    """Performance monitoring logger"""
    
    def __init__(self, logger_name: str = 'artha.performance'):
        self.logger = logging.getLogger(logger_name)
    
    def log_request_time(self, endpoint: str, method: str, duration: float, status_code: int):
        """Log API request performance"""
        self.logger.info(
            "API request completed",
            extra={
                'event_type': 'api_request',
                'endpoint': endpoint,
                'method': method,
                'duration_ms': round(duration * 1000, 2),
                'status_code': status_code,
                'performance_category': self._categorize_performance(duration)
            }
        )
    
    def log_database_query(self, query_type: str, duration: float, success: bool):
        """Log database query performance"""
        self.logger.info(
            "Database query completed",
            extra={
                'event_type': 'database_query',
                'query_type': query_type,
                'duration_ms': round(duration * 1000, 2),
                'success': success,
                'performance_category': self._categorize_performance(duration)
            }
        )
    
    def log_ai_request(self, model: str, tokens: int, duration: float, success: bool):
        """Log AI model request performance"""
        self.logger.info(
            "AI request completed",
            extra={
                'event_type': 'ai_request',
                'model': model,
                'tokens': tokens,
                'duration_ms': round(duration * 1000, 2),
                'success': success,
                'tokens_per_second': round(tokens / duration, 2) if duration > 0 else 0
            }
        )
    
    def _categorize_performance(self, duration: float) -> str:
        """Categorize performance based on duration"""
        if duration < 0.1:  # < 100ms
            return 'excellent'
        elif duration < 0.5:  # < 500ms
            return 'good'
        elif duration < 1.0:  # < 1s
            return 'acceptable'
        elif duration < 3.0:  # < 3s
            return 'slow'
        else:
            return 'very_slow'

class SecurityLogger:
    """Security event logger"""
    
    def __init__(self, logger_name: str = 'artha.security'):
        self.logger = logging.getLogger(logger_name)
    
    def log_authentication_attempt(self, user_id: str, success: bool, ip_address: str, user_agent: str):
        """Log authentication attempts"""
        self.logger.info(
            "Authentication attempt",
            extra={
                'event_type': 'authentication',
                'user_id': user_id,
                'success': success,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'security_level': 'high' if not success else 'normal'
            }
        )
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str, limit: int):
        """Log rate limit violations"""
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                'event_type': 'rate_limit_exceeded',
                'ip_address': ip_address,
                'endpoint': endpoint,
                'limit': limit,
                'security_level': 'medium'
            }
        )
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious security events"""
        self.logger.warning(
            f"Suspicious activity detected: {activity_type}",
            extra={
                'event_type': 'suspicious_activity',
                'activity_type': activity_type,
                'security_level': 'high',
                **details
            }
        )

def setup_logging(config: Optional[Dict[str, Any]] = None) -> Dict[str, logging.Logger]:
    """Setup comprehensive logging configuration
    
    Args:
        config: Optional logging configuration override
    
    Returns:
        Dictionary of configured loggers
    """
    
    # Default configuration
    default_config = {
        'log_level': os.getenv('LOG_LEVEL', 'INFO').upper(),
        'log_format': os.getenv('LOG_FORMAT', 'structured'),
        'log_file': os.getenv('LOG_FILE', 'logs/artha_backend.log'),
        'max_file_size': int(os.getenv('LOG_MAX_SIZE', '10485760')),  # 10MB
        'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5')),
        'enable_console': os.getenv('LOG_ENABLE_CONSOLE', 'true').lower() == 'true',
        'enable_file': os.getenv('LOG_ENABLE_FILE', 'true').lower() == 'true',
        'enable_json': os.getenv('LOG_ENABLE_JSON', 'true').lower() == 'true',
    }
    
    if config:
        default_config.update(config)
    
    # Create logs directory
    log_file_path = Path(default_config['log_file'])
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, default_config['log_level']))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Setup formatters
    if default_config['log_format'] == 'structured' and default_config['enable_json']:
        if JSON_LOGGER_AVAILABLE:
            formatter = jsonlogger.JsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S'
            )
        else:
            formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    if default_config['enable_console']:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(RequestResponseFilter())
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if default_config['enable_file']:
        file_handler = logging.handlers.RotatingFileHandler(
            default_config['log_file'],
            maxBytes=default_config['max_file_size'],
            backupCount=default_config['backup_count']
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestResponseFilter())
        root_logger.addHandler(file_handler)
    
    # Setup specialized loggers
    loggers = {
        'main': logging.getLogger('artha.main'),
        'api': logging.getLogger('artha.api'),
        'database': logging.getLogger('artha.database'),
        'auth': logging.getLogger('artha.auth'),
        'chat': logging.getLogger('artha.chat'),
        'ai': logging.getLogger('artha.ai'),
        'performance': logging.getLogger('artha.performance'),
        'security': logging.getLogger('artha.security'),
        'cache': logging.getLogger('artha.cache'),
        'websocket': logging.getLogger('artha.websocket')
    }
    
    # Set specific log levels for different components
    loggers['performance'].setLevel(logging.INFO)
    loggers['security'].setLevel(logging.WARNING)
    loggers['database'].setLevel(logging.INFO)
    
    # Log successful setup
    loggers['main'].info(
        "Logging system initialized",
        extra={
            'event_type': 'system_startup',
            'log_level': default_config['log_level'],
            'log_format': default_config['log_format'],
            'handlers': len(root_logger.handlers)
        }
    )
    
    return loggers

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f'artha.{name}')

def log_startup_info():
    """Log system startup information"""
    logger = get_logger('main')
    
    startup_info = {
        'event_type': 'system_startup',
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': os.getcwd(),
        'process_id': os.getpid(),
        'environment': os.getenv('NODE_ENV', 'development'),
        'debug_mode': os.getenv('DEBUG', 'false').lower() == 'true'
    }
    
    logger.info("Artha AI Backend starting up", extra=startup_info)

# Initialize performance and security loggers
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()

# Export commonly used loggers
__all__ = [
    'setup_logging',
    'get_logger',
    'log_startup_info',
    'performance_logger',
    'security_logger',
    'StructuredFormatter',
    'RequestResponseFilter',
    'PerformanceLogger',
    'SecurityLogger'
]