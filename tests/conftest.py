"""
Configuration file for pytest containing fixtures and setup/teardown functions.
"""
import os
import sys
import json
import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any, AsyncGenerator

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api import create_app
from api.routes import get_settings
from telephony.call_handler import CallHandler
from llm.ollama_client import OllamaClient


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def api_client() -> AsyncGenerator:
    """
    Create a test client for the FastAPI application.
    """
    from fastapi.testclient import TestClient
    
    app = create_app("test")
    async with TestClient(app) as client:
        yield client


@pytest.fixture
async def auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for API requests.
    """
    from fastapi.testclient import TestClient
    from api.routes import create_access_token
    
    app = create_app("test")
    settings = get_settings()
    
    # Create a test token
    access_token = create_access_token(
        data={"sub": "test_user"}, 
        secret_key=settings.secret_key,
        expires_minutes=30
    )
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_call_data() -> Dict[str, Any]:
    """
    Provide test call data.
    """
    return {
        "call_id": "test-call-123",
        "caller_number": "+15555555555",
        "caller_name": "Test Caller",
        "start_time": "2023-01-01T12:00:00Z",
        "duration": 120,
        "status": "completed",
        "notes": "This is a test call",
        "transcript": {
            "items": [
                {
                    "speaker": "user",
                    "text": "Hello, I would like to schedule an appointment.",
                    "timestamp": "2023-01-01T12:00:05Z"
                },
                {
                    "speaker": "assistant",
                    "text": "I'd be happy to help you schedule an appointment. What day works best for you?",
                    "timestamp": "2023-01-01T12:00:10Z"
                }
            ]
        },
        "actions": [
            {
                "action_type": "schedule_appointment",
                "timestamp": "2023-01-01T12:00:15Z",
                "success": True,
                "details": {
                    "date": "2023-01-05",
                    "time": "14:00",
                    "purpose": "Consultation"
                }
            }
        ]
    }


@pytest.fixture
def test_message_data() -> Dict[str, Any]:
    """
    Provide test message data.
    """
    return {
        "message_id": "test-message-123",
        "sender": "Test Sender",
        "recipient": "Test Recipient",
        "subject": "Test Message",
        "content": "This is a test message content.",
        "timestamp": "2023-01-01T12:00:00Z",
        "urgency": "normal",
        "read": False,
        "call_id": "test-call-123"
    }


@pytest.fixture
def test_appointment_data() -> Dict[str, Any]:
    """
    Provide test appointment data.
    """
    return {
        "appointment_id": "test-appointment-123",
        "title": "Test Appointment",
        "contact": "Test Contact",
        "date": "2023-01-05",
        "start_time": "14:00:00",
        "end_time": "15:00:00",
        "status": "scheduled",
        "notes": "This is a test appointment",
        "call_id": "test-call-123"
    }


@pytest.fixture
async def mock_ollama_client() -> OllamaClient:
    """
    Provide a mock Ollama client for LLM testing.
    """
    class MockOllamaClient(OllamaClient):
        async def generate(self, prompt: str, system_prompt: str = None):
            return {
                "response": "This is a mock response from the LLM.",
                "model": "mock-model",
                "done": True
            }
    
    return MockOllamaClient(base_url="http://localhost:11434", model="mock-model")


@pytest.fixture
async def mock_call_handler() -> CallHandler:
    """
    Provide a mock call handler for telephony testing.
    """
    class MockCallHandler(CallHandler):
        async def answer_call(self, call_id: str):
            return True
            
        async def end_call(self, call_id: str):
            return True
            
        async def say(self, call_id: str, text: str):
            return True
            
        async def listen(self, call_id: str, timeout: int = 30):
            return "This is mock speech recognition result."
    
    return MockCallHandler()


@pytest.fixture
def mock_database():
    """
    Provide a mock database for testing.
    """
    class MockDB:
        def __init__(self):
            self.calls = {}
            self.messages = {}
            self.appointments = {}
            
        async def get_calls(self, limit=10, offset=0, **filters):
            return list(self.calls.values())[:limit]
            
        async def get_call(self, call_id):
            return self.calls.get(call_id)
            
        async def create_call(self, call_data):
            self.calls[call_data["call_id"]] = call_data
            return call_data
            
        async def update_call(self, call_id, call_data):
            if call_id in self.calls:
                self.calls[call_id].update(call_data)
                return self.calls[call_id]
            return None
            
        async def delete_call(self, call_id):
            if call_id in self.calls:
                del self.calls[call_id]
                return True
            return False
    
    return MockDB()