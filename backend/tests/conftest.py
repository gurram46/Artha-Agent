import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_env():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'DATABASE_URL': 'sqlite:///test.db',
        'REDIS_URL': 'redis://localhost:6379/1',
        'ALLOWED_ORIGINS': 'http://localhost:3000,http://localhost:3001',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'RATE_LIMIT_REQUESTS': '100',
        'RATE_LIMIT_WINDOW': '60',
    }):
        yield

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.exists.return_value = False
    mock_redis.expire.return_value = True
    return mock_redis

@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    mock_db = Mock()
    mock_db.execute.return_value = Mock()
    mock_db.fetchone.return_value = None
    mock_db.fetchall.return_value = []
    mock_db.commit.return_value = None
    return mock_db

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "hashed_password": "$2b$12$test.hashed.password",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "login_attempts": 0,
        "locked_until": None
    }

@pytest.fixture
def test_session_data():
    """Sample session data for testing."""
    return {
        "session_id": "test-session-123",
        "user_id": "test-user-123",
        "data": {"key": "value"},
        "expires_at": "2024-12-31T23:59:59Z"
    }

@pytest.fixture
def mock_auth_service():
    """Mock authentication service for testing."""
    with patch('services.auth_service.AuthService') as mock:
        mock_instance = Mock()
        mock_instance.authenticate_user.return_value = {"id": "test-user-123", "email": "test@example.com"}
        mock_instance.create_access_token.return_value = "test-jwt-token"
        mock_instance.verify_token.return_value = {"user_id": "test-user-123"}
        mock_instance.hash_password.return_value = "$2b$12$test.hashed.password"
        mock_instance.verify_password.return_value = True
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_session_service():
    """Mock session service for testing."""
    with patch('services.session_service.SessionService') as mock:
        mock_instance = Mock()
        mock_instance.create_session.return_value = "test-session-123"
        mock_instance.get_session_data.return_value = {"key": "value"}
        mock_instance.update_session_data.return_value = True
        mock_instance.delete_session.return_value = True
        mock_instance.cleanup_expired_sessions.return_value = 5
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def client(mock_env):
    """Create a test client for the FastAPI application."""
    # Import here to ensure environment variables are set
    from api_server import app
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def authenticated_headers():
    """Headers for authenticated requests."""
    return {
        "Authorization": "Bearer test-jwt-token",
        "Content-Type": "application/json"
    }

@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing."""
    with patch('middleware.rate_limiter.RateLimiter') as mock:
        mock_instance = Mock()
        mock_instance.is_allowed.return_value = True
        mock_instance.get_remaining_requests.return_value = 99
        mock.return_value = mock_instance
        yield mock_instance