"""
Tests for LLM functionality.
"""
import os
import unittest
import tempfile
import json
import yaml
from unittest.mock import MagicMock, patch, Mock

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.ollama_client import OllamaClient
from src.llm.context import ConversationContext
from src.llm.prompts import get_prompt_template, format_prompt, create_custom_prompt

class TestOllamaClient(unittest.TestCase):
    """Test cases for the OllamaClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the requests module
        self.requests_patcher = patch('requests.post')
        self.requests_get_patcher = patch('requests.get')
        
        self.mock_post = self.requests_patcher.start()
        self.mock_get = self.requests_get_patcher.start()
        
        # Set up mock responses
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "message": {"content": "This is a test response"}
        }
        self.mock_post.return_value = self.mock_response
        
        self.mock_get_response = Mock()
        self.mock_get_response.status_code = 200
        self.mock_get_response.json.return_value = {
            "models": [
                {"name": "mistral"},
                {"name": "llama2"}
            ]
        }
        self.mock_get.return_value = self.mock_get_response
        
        # Create a config file
        self.config_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yml')
        with open(self.config_file.name, 'w') as f:
            yaml.dump({
                'llm': {
                    'model': 'mistral',
                    'temperature': 0.7,
                    'system_prompt': 'You are a helpful assistant.',
                    'max_tokens': 500,
                    'timeout': 15
                }
            }, f)
        
        # Create a client instance
        self.client = OllamaClient(self.config_file.name)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.requests_patcher.stop()
        self.requests_get_patcher.stop()
        os.unlink(self.config_file.name)
    
    def test_model_availability_check(self):
        """Test checking model availability."""
        # Test when model is available
        result = self.client._check_model_availability()
        self.assertTrue(result)
        
        # Test when model is not available
        self.mock_get_response.json.return_value = {"models": [{"name": "llama2"}]}
        result = self.client._check_model_availability()
        self.assertFalse(result)
    
    def test_generate_response(self):
        """Test generating a response."""
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        response = self.client.generate_response(messages)
        self.assertEqual(response, "This is a test response")
        
        # Check that the POST request was made correctly
        args, kwargs = self.mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/chat")
        self.assertEqual(kwargs['json']['model'], "mistral")
        self.assertEqual(kwargs['json']['messages'][0]['role'], "system")
        self.assertEqual(kwargs['json']['messages'][1]['role'], "user")
        self.assertEqual(kwargs['json']['messages'][1]['content'], "Hello, how are you?")
    
    def test_generate_response_with_error(self):
        """Test generating a response when an error occurs."""
        # Set up mock to raise an exception
        self.mock_post.side_effect = Exception("Test error")
        
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        response = self.client.generate_response(messages)
        self.assertIsNone(response)
    
    def test_embed_text(self):
        """Test embedding text."""
        # Set up mock response for embeddings
        self.mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        embeddings = self.client.embed_text("Test text")
        self.assertEqual(embeddings, [0.1, 0.2, 0.3, 0.4, 0.5])
        
        # Check that the POST request was made correctly
        args, kwargs = self.mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/embeddings")
        self.assertEqual(kwargs['json']['model'], "mistral")
        self.assertEqual(kwargs['json']['prompt'], "Test text")


class TestConversationContext(unittest.TestCase):
    """Test cases for the ConversationContext class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the prompts module
        self.prompts_patcher = patch('src.llm.context.get_prompt_template')
        self.mock_get_prompt = self.prompts_patcher.start()
        self.mock_get_prompt.return_value = "You are a test assistant."
        
        # Create a config file
        self.config_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yml')
        with open(self.config_file.name, 'w') as f:
            yaml.dump({
                'llm': {
                    'context': {
                        'max_history': 10,
                        'token_limit': 2000,
                        'context_type': 'test'
                    }
                }
            }, f)
        
        # Create a context instance
        self.context = ConversationContext(self.config_file.name)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.prompts_patcher.stop()
        os.unlink(self.config_file.name)
    
    def test_init_conversation(self):
        """Test initializing a conversation."""
        self.context.init_conversation(conversation_id="test-123", caller_name="Test User")
        
        # Check that metadata was set correctly
        self.assertEqual(self.context.metadata['conversation_id'], "test-123")
        self.assertEqual(self.context.metadata['caller_name'], "Test User")
        
        # Check that system message was added
        self.assertEqual(len(self.context.messages), 1)
        self.assertEqual(self.context.messages[0]['role'], "system")
        self.assertEqual(self.context.messages[0]['content'], "You are a test assistant.")
    
    def test_add_messages(self):
        """Test adding messages to the conversation."""
        self.context.init_conversation()
        
        # Add user message
        self.context.add_user_message("Hello!")
        self.assertEqual(len(self.context.messages), 2)
        self.assertEqual(self.context.messages[1]['role'], "user")
        self.assertEqual(self.context.messages[1]['content'], "Hello!")
        
        # Add assistant message
        self.context.add_assistant_message("Hi there!")
        self.assertEqual(len(self.context.messages), 3)
        self.assertEqual(self.context.messages[2]['role'], "assistant")
        self.assertEqual(self.context.messages[2]['content'], "Hi there!")
        
        # Add system message
        self.context.add_system_message("System notification")
        self.assertEqual(len(self.context.messages), 4)
        self.assertEqual(self.context.messages[3]['role'], "system")
        self.assertEqual(self.context.messages[3]['content'], "System notification")
    
    def test_get_messages(self):
        """Test getting messages from the conversation."""
        self.context.init_conversation()
        self.context.add_user_message("User message 1")
        self.context.add_assistant_message("Assistant message 1")
        self.context.add_user_message("User message 2")
        
        # Test get_context
        context = self.context.get_context()
        self.assertEqual(len(context), 4)  # System + 3 messages
        
        # Test get_user_messages
        user_messages = self.context.get_user_messages()
        self.assertEqual(len(user_messages), 2)
        self.assertEqual(user_messages[0]['content'], "User message 1")
        self.assertEqual(user_messages[1]['content'], "User message 2")
        
        # Test get_assistant_messages
        assistant_messages = self.context.get_assistant_messages()
        self.assertEqual(len(assistant_messages), 1)
        self.assertEqual(assistant_messages[0]['content'], "Assistant message 1")
        
        # Test get_latest_message
        latest = self.context.get_latest_message()
        self.assertEqual(latest['content'], "User message 2")
        
        latest_user = self.context.get_latest_message(role="user")
        self.assertEqual(latest_user['content'], "User message 2")
        
        latest_assistant = self.context.get_latest_message(role="assistant")
        self.assertEqual(latest_assistant['content'], "Assistant message 1")
    
    def test_entities(self):
        """Test entity management."""
        self.context.init_conversation()
        
        # Set and get entities
        self.context.set_entity("name", "Test User")
        self.context.set_entity("phone", "555-1234")
        
        self.assertEqual(self.context.get_entity("name"), "Test User")
        self.assertEqual(self.context.get_entity("phone"), "555-1234")
        self.assertIsNone(self.context.get_entity("email"))
    
    def test_trim_history(self):
        """Test history trimming."""
        # Set a small max_history
        self.context.max_history = 5
        self.context.init_conversation()
        
        # Add system message (should be preserved)
        self.context.add_system_message("Important system message")
        
        # Add more messages than the max
        for i in range(6):
            self.context.add_user_message(f"User message {i}")
            self.context.add_assistant_message(f"Assistant message {i}")
        
        # Check that history was trimmed
        self.assertLessEqual(len(self.context.messages), 5)
        
        # System messages should be preserved
        system_messages = [msg for msg in self.context.messages if msg['role'] == 'system']
        self.assertEqual(len(system_messages), 2)  # Initial + added
    
    def test_save_and_load(self):
        """Test saving and loading conversation state."""
        self.context.init_conversation(conversation_id="test-save-load")
        self.context.add_user_message("Test message")
        self.context.add_assistant_message("Test response")
        self.context.set_entity("test_entity", "test_value")
        
        # Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        success = self.context.save_to_file(temp_file.name)
        self.assertTrue(success)
        
        # Create a new context and load from file
        new_context = ConversationContext(self.config_file.name)
        success = new_context.load_from_file(temp_file.name)
        self.assertTrue(success)
        
        # Check that state was loaded correctly
        self.assertEqual(new_context.metadata['conversation_id'], "test-save-load")
        self.assertEqual(len(new_context.messages), 3)
        self.assertEqual(new_context.get_entity("test_entity"), "test_value")
        
        # Clean up
        os.unlink(temp_file.name)


class TestPrompts(unittest.TestCase):
    """Test cases for prompts functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a config file with custom prompts
        self.config_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yml')
        with open(self.config_file.name, 'w') as f:
            yaml.dump({
                'prompts': {
                    'custom_prompt': 'This is a custom prompt for {business_name}.'
                }
            }, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        os.unlink(self.config_file.name)
    
    def test_get_default_prompt(self):
        """Test getting a default prompt template."""
        prompt = get_prompt_template("call_answering")
        self.assertIn("You are an AI call secretary", prompt)
        
        # Test fallback for unknown prompt type
        prompt = get_prompt_template("nonexistent_type")
        self.assertIn("You are an AI call secretary", prompt)  # Falls back to call_answering
    
    def test_get_custom_prompt(self):
        """Test getting a custom prompt template."""
        prompt = get_prompt_template("custom_prompt", self.config_file.name)
        self.assertEqual(prompt, 'This is a custom prompt for {business_name}.')
        
        # Test fallback to default when prompt not in config
        prompt = get_prompt_template("call_answering", self.config_file.name)
        self.assertIn("You are an AI call secretary", prompt)
    
    def test_format_prompt(self):
        """Test formatting a prompt template."""
        template = "Hello, {name}! Welcome to {business_name}."
        variables = {
            "name": "Test User",
            "business_name": "Test Company"
        }
        
        result = format_prompt(template, variables)
        self.assertEqual(result, "Hello, Test User! Welcome to Test Company.")
        
        # Test with missing variables (should use defaults)
        template = "Hello, {caller_name}! Welcome to {business_name}."
        result = format_prompt(template, {})
        self.assertEqual(result, "Hello, the caller! Welcome to the business.")
        
        # Test with partial variables
        template = "Hello, {name}! Your number is {phone}."
        result = format_prompt(template, {"name": "Test"})
        self.assertIn("Hello, Test!", result)
    
    def test_create_custom_prompt(self):
        """Test creating a custom prompt."""
        result = create_custom_prompt(
            "test_prompt", 
            "This is a test prompt for {name}.",
            self.config_file.name
        )
        self.assertTrue(result)
        
        # Check that the prompt was saved
        with open(self.config_file.name, 'r') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('test_prompt', config['prompts'])
        self.assertEqual(config['prompts']['test_prompt'], "This is a test prompt for {name}.")
        
        # Test that the prompt can be retrieved
        prompt = get_prompt_template("test_prompt", self.config_file.name)
        self.assertEqual(prompt, "This is a test prompt for {name}.")


if __name__ == '__main__':
    unittest.main()