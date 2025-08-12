import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

class TestSessionEndpoints:
    """Test cases for session management endpoints."""

    def test_set_session_data_success(self, client, mock_session_service):
        """Test successful session data setting."""
        mock_session_service.set_session_data.return_value = True
        
        response = client.post(
            "/api/session/set",
            json={"key": "userData", "value": {"id": "123", "name": "Test User"}},
            cookies={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_session_service.set_session_data.assert_called_once()

    def test_set_session_data_creates_new_session(self, client, mock_session_service):
        """Test session data setting creates new session when none exists."""
        mock_session_service.create_session.return_value = "new-session-123"
        mock_session_service.set_session_data.return_value = True
        
        response = client.post(
            "/api/session/set",
            json={"key": "userData", "value": {"id": "123", "name": "Test User"}}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_session_service.create_session.assert_called_once()
        mock_session_service.set_session_data.assert_called_once()

    def test_set_session_data_invalid_payload(self, client):
        """Test session data setting with invalid payload."""
        response = client.post(
            "/api/session/set",
            json={"key": "userData"}  # Missing 'value'
        )
        
        assert response.status_code == 422

    def test_get_session_data_success(self, client, mock_session_service):
        """Test successful session data retrieval."""
        mock_data = {"id": "123", "name": "Test User"}
        mock_session_service.get_session_data.return_value = mock_data
        
        response = client.get(
            "/api/session/get?key=userData",
            cookies={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 200
        assert response.json()["value"] == mock_data
        mock_session_service.get_session_data.assert_called_once_with("test-session-123", "userData")

    def test_get_session_data_not_found(self, client, mock_session_service):
        """Test session data retrieval when data not found."""
        mock_session_service.get_session_data.return_value = None
        
        response = client.get(
            "/api/session/get?key=nonexistent",
            cookies={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_session_data_no_session(self, client):
        """Test session data retrieval without session."""
        response = client.get("/api/session/get?key=userData")
        
        assert response.status_code == 401
        assert "No session found" in response.json()["detail"]

    def test_remove_session_data_success(self, client, mock_session_service):
        """Test successful session data removal."""
        mock_session_service.remove_session_data.return_value = True
        
        response = client.delete(
            "/api/session/remove",
            json={"key": "userData"},
            cookies={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_session_service.remove_session_data.assert_called_once_with("test-session-123", "userData")

    def test_remove_session_data_no_session(self, client):
        """Test session data removal without session."""
        response = client.delete(
            "/api/session/remove",
            json={"key": "userData"}
        )
        
        assert response.status_code == 401
        assert "No session found" in response.json()["detail"]

    def test_clear_session_data_success(self, client, mock_session_service):
        """Test successful session data clearing."""
        mock_session_service.clear_session_data.return_value = True
        
        response = client.delete(
            "/api/session/clear",
            cookies={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_session_service.clear_session_data.assert_called_once_with("test-session-123")

    def test_clear_session_data_no_session(self, client):
        """Test session data clearing without session."""
        response = client.delete("/api/session/clear")
        
        assert response.status_code == 401
        assert "No session found" in response.json()["detail"]

    def test_session_service_error_handling(self, client, mock_session_service):
        """Test error handling when session service fails."""
        mock_session_service.set_session_data.side_effect = Exception("Database error")
        
        response = client.post(
            "/api/session/set",
            json={"key": "userData", "value": {"id": "123"}},
            cookies={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 500
        assert "Failed to set session data" in response.json()["detail"]

    def test_session_cookie_security(self, client, mock_session_service):
        """Test that session cookies are set with security flags."""
        mock_session_service.create_session.return_value = "new-session-123"
        mock_session_service.set_session_data.return_value = True
        
        response = client.post(
            "/api/session/set",
            json={"key": "userData", "value": {"id": "123"}}
        )
        
        assert response.status_code == 200
        
        # Check that session cookie is set
        set_cookie_header = response.headers.get("set-cookie")
        if set_cookie_header:
            assert "session_id=" in set_cookie_header
            assert "HttpOnly" in set_cookie_header
            assert "SameSite=Strict" in set_cookie_header

    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self, client, mock_session_service):
        """Test concurrent session operations."""
        import asyncio
        
        mock_session_service.set_session_data.return_value = True
        mock_session_service.get_session_data.return_value = {"id": "123"}
        
        async def set_data():
            return client.post(
                "/api/session/set",
                json={"key": "userData", "value": {"id": "123"}},
                cookies={"session_id": "test-session-123"}
            )
        
        async def get_data():
            return client.get(
                "/api/session/get?key=userData",
                cookies={"session_id": "test-session-123"}
            )
        
        # Run operations concurrently
        set_response, get_response = await asyncio.gather(
            asyncio.to_thread(set_data),
            asyncio.to_thread(get_data)
        )
        
        assert set_response.status_code == 200
        assert get_response.status_code == 200

    def test_session_data_validation(self, client, mock_session_service):
        """Test session data validation."""
        # Test with various data types
        test_cases = [
            {"key": "string_data", "value": "test_string"},
            {"key": "number_data", "value": 123},
            {"key": "boolean_data", "value": True},
            {"key": "object_data", "value": {"nested": {"data": "value"}}},
            {"key": "array_data", "value": [1, 2, 3, "test"]},
        ]
        
        mock_session_service.set_session_data.return_value = True
        
        for test_case in test_cases:
            response = client.post(
                "/api/session/set",
                json=test_case,
                cookies={"session_id": "test-session-123"}
            )
            assert response.status_code == 200, f"Failed for {test_case}"

    def test_session_key_validation(self, client):
        """Test session key validation."""
        invalid_keys = ["", " ", None, 123, [], {}]
        
        for invalid_key in invalid_keys:
            if invalid_key is None:
                continue  # Skip None as it would be missing from JSON
                
            response = client.post(
                "/api/session/set",
                json={"key": invalid_key, "value": "test"},
                cookies={"session_id": "test-session-123"}
            )
            # Should return 422 for validation error
            assert response.status_code in [400, 422], f"Should reject invalid key: {invalid_key}"