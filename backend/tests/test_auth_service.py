import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import bcrypt

class TestAuthService:
    """Test cases for authentication service."""

    @pytest.fixture
    def auth_service(self, mock_database):
        """Create auth service instance with mocked database."""
        with patch('services.auth_service.get_db_connection', return_value=mock_database):
            from services.auth_service import AuthService
            return AuthService()

    def test_hash_password(self, auth_service):
        """Test password hashing."""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(wrong_password, hashed) is False

    def test_create_user_success(self, auth_service, mock_database):
        """Test successful user creation."""
        mock_database.fetchone.return_value = None  # User doesn't exist
        mock_database.lastrowid = 123
        
        user_data = {
            "email": "test@example.com",
            "password": "secure_password_123",
            "name": "Test User"
        }
        
        result = auth_service.create_user(user_data)
        
        assert result["id"] == 123
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert "password" not in result
        mock_database.execute.assert_called()
        mock_database.commit.assert_called()

    def test_create_user_duplicate_email(self, auth_service, mock_database):
        """Test user creation with duplicate email."""
        mock_database.fetchone.return_value = {"id": 1, "email": "test@example.com"}
        
        user_data = {
            "email": "test@example.com",
            "password": "secure_password_123",
            "name": "Test User"
        }
        
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.create_user(user_data)

    def test_authenticate_user_success(self, auth_service, mock_database):
        """Test successful user authentication."""
        password = "test_password_123"
        hashed_password = auth_service.hash_password(password)
        
        mock_user = {
            "id": 123,
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": hashed_password,
            "is_active": True,
            "login_attempts": 0,
            "locked_until": None
        }
        mock_database.fetchone.return_value = mock_user
        
        result = auth_service.authenticate_user("test@example.com", password)
        
        assert result["id"] == 123
        assert result["email"] == "test@example.com"
        assert "hashed_password" not in result

    def test_authenticate_user_wrong_password(self, auth_service, mock_database):
        """Test authentication with wrong password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed_password = auth_service.hash_password(password)
        
        mock_user = {
            "id": 123,
            "email": "test@example.com",
            "hashed_password": hashed_password,
            "is_active": True,
            "login_attempts": 2,
            "locked_until": None
        }
        mock_database.fetchone.return_value = mock_user
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.authenticate_user("test@example.com", wrong_password)
        
        # Should increment login attempts
        mock_database.execute.assert_called()

    def test_authenticate_user_account_locked(self, auth_service, mock_database):
        """Test authentication with locked account."""
        future_time = datetime.utcnow() + timedelta(minutes=30)
        
        mock_user = {
            "id": 123,
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "is_active": True,
            "login_attempts": 5,
            "locked_until": future_time.isoformat()
        }
        mock_database.fetchone.return_value = mock_user
        
        with pytest.raises(ValueError, match="Account is locked"):
            auth_service.authenticate_user("test@example.com", "any_password")

    def test_authenticate_user_not_found(self, auth_service, mock_database):
        """Test authentication with non-existent user."""
        mock_database.fetchone.return_value = None
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.authenticate_user("nonexistent@example.com", "password")

    def test_authenticate_user_inactive(self, auth_service, mock_database):
        """Test authentication with inactive user."""
        mock_user = {
            "id": 123,
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "is_active": False,
            "login_attempts": 0,
            "locked_until": None
        }
        mock_database.fetchone.return_value = mock_user
        
        with pytest.raises(ValueError, match="Account is disabled"):
            auth_service.authenticate_user("test@example.com", "password")

    def test_create_access_token(self, auth_service):
        """Test JWT token creation."""
        user_data = {"id": 123, "email": "test@example.com"}
        
        token = auth_service.create_access_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT format

    def test_verify_token_valid(self, auth_service):
        """Test JWT token verification with valid token."""
        user_data = {"id": 123, "email": "test@example.com"}
        token = auth_service.create_access_token(user_data)
        
        decoded = auth_service.verify_token(token)
        
        assert decoded["user_id"] == 123
        assert decoded["email"] == "test@example.com"

    def test_verify_token_invalid(self, auth_service):
        """Test JWT token verification with invalid token."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.verify_token(invalid_token)

    def test_verify_token_expired(self, auth_service):
        """Test JWT token verification with expired token."""
        user_data = {"id": 123, "email": "test@example.com"}
        
        # Create token with very short expiration
        with patch('services.auth_service.datetime') as mock_datetime:
            # Mock current time
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
            token = auth_service.create_access_token(user_data, expires_delta=timedelta(seconds=1))
            
            # Mock time after expiration
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 2)
            
            with pytest.raises(ValueError, match="Token has expired"):
                auth_service.verify_token(token)

    def test_reset_login_attempts(self, auth_service, mock_database):
        """Test resetting login attempts after successful login."""
        password = "test_password_123"
        hashed_password = auth_service.hash_password(password)
        
        mock_user = {
            "id": 123,
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": hashed_password,
            "is_active": True,
            "login_attempts": 3,
            "locked_until": None
        }
        mock_database.fetchone.return_value = mock_user
        
        auth_service.authenticate_user("test@example.com", password)
        
        # Should reset login attempts
        calls = mock_database.execute.call_args_list
        reset_call = any("login_attempts = 0" in str(call) for call in calls)
        assert reset_call

    def test_account_lockout_after_max_attempts(self, auth_service, mock_database):
        """Test account lockout after maximum failed attempts."""
        mock_user = {
            "id": 123,
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "is_active": True,
            "login_attempts": 4,  # One less than max
            "locked_until": None
        }
        mock_database.fetchone.return_value = mock_user
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.authenticate_user("test@example.com", "wrong_password")
        
        # Should set locked_until timestamp
        calls = mock_database.execute.call_args_list
        lock_call = any("locked_until" in str(call) for call in calls)
        assert lock_call

    def test_unlock_expired_account(self, auth_service, mock_database):
        """Test unlocking account when lock period has expired."""
        password = "test_password_123"
        hashed_password = auth_service.hash_password(password)
        past_time = datetime.utcnow() - timedelta(minutes=30)
        
        mock_user = {
            "id": 123,
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": hashed_password,
            "is_active": True,
            "login_attempts": 5,
            "locked_until": past_time.isoformat()
        }
        mock_database.fetchone.return_value = mock_user
        
        result = auth_service.authenticate_user("test@example.com", password)
        
        assert result["id"] == 123
        # Should reset login attempts and clear lock
        calls = mock_database.execute.call_args_list
        reset_call = any("login_attempts = 0" in str(call) for call in calls)
        unlock_call = any("locked_until = NULL" in str(call) for call in calls)
        assert reset_call
        assert unlock_call

    def test_password_strength_validation(self, auth_service):
        """Test password strength validation."""
        weak_passwords = [
            "123",
            "password",
            "12345678",
            "abcdefgh",
            "PASSWORD",
        ]
        
        for weak_password in weak_passwords:
            with pytest.raises(ValueError, match="Password does not meet security requirements"):
                auth_service._validate_password_strength(weak_password)
        
        # Strong password should pass
        strong_password = "SecureP@ssw0rd123"
        auth_service._validate_password_strength(strong_password)  # Should not raise

    def test_email_validation(self, auth_service):
        """Test email validation."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user..name@example.com",
            "user@.com",
        ]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                auth_service._validate_email(invalid_email)
        
        # Valid email should pass
        valid_email = "user@example.com"
        auth_service._validate_email(valid_email)  # Should not raise