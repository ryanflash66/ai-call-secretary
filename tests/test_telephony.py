"""
Tests for telephony functionality.
"""
import os
import unittest
import time
from unittest.mock import MagicMock, patch
import yaml

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.telephony.call_router import CallRouter
from src.telephony.call_handler import CallHandler

class TestCallRouter(unittest.TestCase):
    """Test cases for the CallRouter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.test_config = {
            'telephony': {
                'routing_rules': [
                    {
                        'name': 'Test Rule',
                        'number_pattern': '^1555123.*$',
                        'action': 'test_action',
                        'params': {'test': 'value'}
                    }
                ],
                'blacklist': ['^1555999.*$'],
                'whitelist': ['^1555111.*$'],
                'business_hours': {
                    'start': '09:00',
                    'end': '17:00'
                }
            }
        }
        
        # Mock the config loading
        self.config_patcher = patch('yaml.safe_load')
        self.mock_yaml_load = self.config_patcher.start()
        self.mock_yaml_load.return_value = self.test_config
        
        # Create a router instance with mocked config
        self.router = CallRouter()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.config_patcher.stop()
    
    def test_blacklisted_number(self):
        """Test routing for blacklisted numbers."""
        call_metadata = {
            'caller_number': '15559991234',
            'caller_name': 'Test Caller',
            'timestamp': time.time()
        }
        action, params = self.router.route_call(call_metadata)
        self.assertEqual(action, 'reject')
        self.assertEqual(params['reason'], 'blacklisted')
    
    def test_whitelisted_number(self):
        """Test routing for whitelisted numbers."""
        call_metadata = {
            'caller_number': '15551119876',
            'caller_name': 'VIP Caller',
            'timestamp': time.time()
        }
        action, params = self.router.route_call(call_metadata)
        self.assertEqual(action, 'priority')
        self.assertEqual(params['level'], 'high')
    
    def test_rule_matching(self):
        """Test rule matching functionality."""
        call_metadata = {
            'caller_number': '15551234567',
            'caller_name': 'Regular Caller',
            'timestamp': time.time()
        }
        action, params = self.router.route_call(call_metadata)
        self.assertEqual(action, 'test_action')
        self.assertEqual(params['test'], 'value')
    
    def test_business_hours(self):
        """Test business hours functionality."""
        # Set up a mock time that's within business hours (11 AM)
        mock_time = time.mktime(time.strptime("2023-01-01 11:00:00", "%Y-%m-%d %H:%M:%S"))
        
        call_metadata = {
            'caller_number': '12223334444',  # Number that doesn't match any specific rules
            'caller_name': 'Test Caller',
            'timestamp': mock_time
        }
        
        # First, test within business hours
        is_business_hours = self.router._is_business_hours(mock_time)
        self.assertTrue(is_business_hours)
        
        # Now test outside business hours (3 AM)
        mock_time_outside = time.mktime(time.strptime("2023-01-01 03:00:00", "%Y-%m-%d %H:%M:%S"))
        is_outside_hours = not self.router._is_business_hours(mock_time_outside)
        self.assertTrue(is_outside_hours)


class TestCallHandler(unittest.TestCase):
    """Test cases for the CallHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock components
        self.mock_stt = MagicMock()
        self.mock_tts = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_context = MagicMock()
        self.mock_action_handler = MagicMock()
        
        # Create a test call metadata
        self.test_call_metadata = {
            'call_id': 'test-call-123',
            'caller_number': '15551234567',
            'caller_name': 'Test Caller',
            'timestamp': time.time()
        }
        
        # Patch the imports
        self.patches = [
            patch('src.telephony.call_handler.SpeechToText', return_value=self.mock_stt),
            patch('src.telephony.call_handler.TextToSpeech', return_value=self.mock_tts),
            patch('src.telephony.call_handler.OllamaClient', return_value=self.mock_llm),
            patch('src.telephony.call_handler.ConversationContext', return_value=self.mock_context),
            patch('src.telephony.call_handler.ActionHandler', return_value=self.mock_action_handler),
        ]
        
        for p in self.patches:
            p.start()
        
        # Create handler instance
        self.handler = CallHandler(self.test_call_metadata)
        
        # Mock session
        self.mock_session = MagicMock()
    
    def tearDown(self):
        """Tear down test fixtures."""
        for p in self.patches:
            p.stop()
    
    def test_initialization(self):
        """Test handler initialization."""
        self.assertEqual(self.handler.call_id, self.test_call_metadata['call_id'])
        self.assertEqual(self.handler.caller_number, self.test_call_metadata['caller_number'])
        self.assertEqual(self.handler.caller_name, self.test_call_metadata['caller_name'])
    
    def test_should_end_call(self):
        """Test detection of call-ending phrases."""
        end_phrases = [
            "goodbye", "bye", "hang up", "end call",
            "thank you goodbye", "that's all", "disconnect"
        ]
        
        for phrase in end_phrases:
            self.assertTrue(self.handler._should_end_call(phrase), f"Failed for '{phrase}'")
        
        non_end_phrases = [
            "hello", "yes", "no", "maybe", "tell me more",
            "what time is it", "can you help me"
        ]
        
        for phrase in non_end_phrases:
            self.assertFalse(self.handler._should_end_call(phrase), f"Failed for '{phrase}'")
    
    def test_conversation_flow(self):
        """Test the basic conversation flow."""
        # Setup mocks
        self.mock_stt.transcribe.return_value = "This is a test message"
        self.mock_llm.generate_response.return_value = "This is the AI response"
        self.mock_action_handler.extract_actions.return_value = []
        
        # Call process_call with patched _capture_audio and _should_end_call
        with patch.object(self.handler, '_capture_audio') as mock_capture:
            with patch.object(self.handler, '_should_end_call') as mock_end:
                # First audio capture returns message, second simulates end of call
                mock_capture.side_effect = [b"AUDIO_DATA", None]
                mock_end.return_value = False
                
                self.handler.process_call(self.mock_session)
        
        # Verify the conversation flow
        self.mock_context.init_conversation.assert_called_once()
        self.mock_stt.transcribe.assert_called_once()
        self.mock_context.add_user_message.assert_called_once_with("This is a test message")
        self.mock_llm.generate_response.assert_called_once()
        self.mock_context.add_assistant_message.assert_called_once_with("This is the AI response")
        self.mock_action_handler.extract_actions.assert_called_once_with("This is the AI response")
        

if __name__ == '__main__':
    unittest.main()