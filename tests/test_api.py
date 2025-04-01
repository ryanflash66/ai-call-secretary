"""
Tests for the API layer.
"""
import os
import json
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt

from src.api.routes import app, JWT_SECRET, JWT_ALGORITHM


# Test data
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/default.yml')
test_client = TestClient(app)


def get_test_token():
    """Generate a test token."""
    expiration = datetime.utcnow() + timedelta(hours=1)
    token_data = {
        "sub": "admin",
        "exp": expiration
    }
    return jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)


class TestAuth:
    """Tests for authentication."""
    
    def test_login_success(self):
        """Test successful login."""
        response = test_client.post(
            "/token",
            data={"username": "admin", "password": "password"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_failure(self):
        """Test failed login."""
        response = test_client.post(
            "/token",
            data={"username": "admin", "password": "wrong_password"}
        )
        assert response.status_code == 401
        
        response = test_client.post(
            "/token",
            data={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == 401


class TestSystemRoutes:
    """Tests for system routes."""
    
    def test_root(self):
        """Test root route."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_status_unauthorized(self):
        """Test status route without authentication."""
        response = test_client.get("/status")
        assert response.status_code == 401
    
    def test_status_authorized(self):
        """Test status route with authentication."""
        token = get_test_token()
        response = test_client.get(
            "/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime" in data
        assert "components" in data


class TestCallRoutes:
    """Tests for call routes."""
    
    def test_list_calls_empty(self):
        """Test listing calls when none exist."""
        token = get_test_token()
        response = test_client.get(
            "/calls",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["calls"]) == 0
    
    def test_get_call_not_found(self):
        """Test getting a non-existent call."""
        token = get_test_token()
        response = test_client.get(
            "/calls/nonexistent",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404


class TestActionRoutes:
    """Tests for action routes."""
    
    def test_execute_action_unauthorized(self):
        """Test executing an action without authentication."""
        response = test_client.post(
            "/actions",
            json={
                "action_type": "schedule_appointment",
                "params": {
                    "date": "2023-12-15",
                    "time": "14:30",
                    "duration": 60,
                    "name": "John Doe"
                }
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.skip(reason="Requires mock of ActionHandler")
    def test_execute_action_authorized(self):
        """Test executing an action with authentication."""
        token = get_test_token()
        response = test_client.post(
            "/actions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action_type": "schedule_appointment",
                "params": {
                    "date": "2023-12-15",
                    "time": "14:30",
                    "duration": 60,
                    "name": "John Doe"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action_type"] == "schedule_appointment"
        assert data["success"] is True
    
    @pytest.mark.skip(reason="Requires mock of ActionHandler")
    def test_create_appointment(self):
        """Test creating an appointment."""
        token = get_test_token()
        response = test_client.post(
            "/appointments",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "date": "2023-12-15",
                "time": "14:30",
                "duration": 60,
                "name": "John Doe"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action_type"] == "schedule_appointment"
        assert data["success"] is True
    
    @pytest.mark.skip(reason="Requires mock of ActionHandler")
    def test_create_message(self):
        """Test creating a message."""
        token = get_test_token()
        response = test_client.post(
            "/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Please call me back",
                "caller_name": "John Doe",
                "urgency": "high",
                "callback_requested": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action_type"] == "take_message"
        assert data["success"] is True