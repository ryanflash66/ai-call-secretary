"""
Temporary LLM module tests without API dependencies.
"""
import pytest
from unittest.mock import patch, MagicMock

from src.llm.ollama_client import OllamaClient
from src.llm.context import ConversationContext


@pytest.mark.asyncio
async def test_ollama_client_initialization():
    """Test OllamaClient initialization."""
    client = OllamaClient(base_url="http://localhost:11434", model="llama2")
    assert client.base_url == "http://localhost:11434"
    assert client.model == "llama2"


@pytest.mark.asyncio
async def test_conversation_context():
    """Test ConversationContext functionality."""
    context = ConversationContext()
    
    # Test adding messages
    context.add_user_message("Hello")
    context.add_assistant_message("Hi there!")
    
    # Check message count
    assert len(context.messages) == 2
    
    # Check message content
    assert context.messages[0]["role"] == "user"
    assert context.messages[0]["content"] == "Hello"
    assert context.messages[1]["role"] == "assistant"
    assert context.messages[1]["content"] == "Hi there!"
    
    # Test clearing context
    context.clear()
    assert len(context.messages) == 0


@pytest.mark.asyncio
async def test_ollama_client_generate(mock_ollama_client):
    """Test OllamaClient generation with mock."""
    response = await mock_ollama_client.generate("Test prompt")
    assert response["response"] == "This is a mock response from the LLM."
    assert response["model"] == "mock-model"
    assert response["done"] is True