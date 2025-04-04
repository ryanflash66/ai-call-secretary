"""
Tests for voice functionality.
"""
import os
import unittest
import tempfile
import json
import shutil
from unittest.mock import MagicMock, patch

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice.stt import SpeechToText
from src.voice.tts import TextToSpeech
from src.voice.voice_clone import VoiceCloner

class TestSpeechToText(unittest.TestCase):
    """Test cases for the SpeechToText class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the whisper model and config loading
        self.whisper_patcher = patch('whisper.load_model')
        self.whisper_mock = self.whisper_patcher.start()
        
        # Mock model instance
        self.model_mock = MagicMock()
        self.whisper_mock.return_value = self.model_mock
        
        # Set up test transcription response
        self.model_mock.transcribe.return_value = {"text": "This is a test transcription"}
        
        # Create a stt instance
        self.stt = SpeechToText()
        
        # Force model loading
        self.stt._ensure_model_loaded()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.whisper_patcher.stop()
    
    def test_model_loading(self):
        """Test model loading."""
        self.whisper_mock.assert_called_once()
    
    def test_transcribe_bytes(self):
        """Test transcribing from bytes."""
        result = self.stt.transcribe(b"test audio data")
        
        # Check that a temporary file was created (indirectly by checking the transcribe call)
        args, kwargs = self.model_mock.transcribe.call_args
        self.assertTrue(isinstance(args[0], str))  # Should be a file path
        
        # Check the result
        self.assertEqual(result, "This is a test transcription")
    
    def test_transcribe_file_path(self):
        """Test transcribing from a file path."""
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
            result = self.stt.transcribe(temp_file.name)
            
            # Check that the file path was passed directly
            self.model_mock.transcribe.assert_called_with(temp_file.name, language="en", task="transcribe")
            
            # Check the result
            self.assertEqual(result, "This is a test transcription")
    
    def test_transcribe_error_handling(self):
        """Test error handling during transcription."""
        # Make the model raise an exception
        self.model_mock.transcribe.side_effect = Exception("Test error")
        
        # Should return empty string on error
        result = self.stt.transcribe(b"test audio data")
        self.assertEqual(result, "")


class TestTextToSpeech(unittest.TestCase):
    """Test cases for the TextToSpeech class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a tts instance
        self.tts = TextToSpeech()
        
        # Mock the engine-specific methods
        self.sesame_patcher = patch.object(self.tts, '_synthesize_sesame', return_value=b"SESAME_AUDIO")
        self.pyttsx3_patcher = patch.object(self.tts, '_synthesize_pyttsx3', return_value=b"PYTTSX3_AUDIO")
        self.api_patcher = patch.object(self.tts, '_synthesize_api', return_value=b"API_AUDIO")
        
        self.sesame_mock = self.sesame_patcher.start()
        self.pyttsx3_mock = self.pyttsx3_patcher.start()
        self.api_mock = self.api_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.sesame_patcher.stop()
        self.pyttsx3_patcher.stop()
        self.api_patcher.stop()
    
    def test_synthesize_sesame(self):
        """Test sesame synthesis."""
        self.tts.engine = "sesame"
        result = self.tts.synthesize("Test text")
        
        self.sesame_mock.assert_called_with("Test text", None, None)
        self.assertEqual(result, b"SESAME_AUDIO")
    
    def test_synthesize_pyttsx3(self):
        """Test pyttsx3 synthesis."""
        self.tts.engine = "pyttsx3"
        result = self.tts.synthesize("Test text")
        
        self.pyttsx3_mock.assert_called_with("Test text", None, None)
        self.assertEqual(result, b"PYTTSX3_AUDIO")
    
    def test_synthesize_api(self):
        """Test API synthesis."""
        self.tts.engine = "api"
        result = self.tts.synthesize("Test text")
        
        self.api_mock.assert_called_with("Test text", None, None)
        self.assertEqual(result, b"API_AUDIO")
    
    def test_synthesize_empty_text(self):
        """Test synthesizing empty text."""
        result = self.tts.synthesize("")
        self.assertEqual(result, b"")
    
    def test_synthesize_invalid_engine(self):
        """Test synthesizing with invalid engine."""
        self.tts.engine = "invalid"
        result = self.tts.synthesize("Test text")
        self.assertEqual(result, b"")


class TestVoiceCloner(unittest.TestCase):
    """Test cases for the VoiceCloner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for voice models
        self.temp_dir = tempfile.mkdtemp()
        self.voice_dir = os.path.join(self.temp_dir, "voices")
        self.temp_sample_dir = os.path.join(self.temp_dir, "samples")
        
        os.makedirs(self.voice_dir, exist_ok=True)
        os.makedirs(self.temp_sample_dir, exist_ok=True)
        
        # Create some test audio files
        self.audio_samples = []
        for i in range(5):
            sample_path = os.path.join(self.temp_sample_dir, f"sample_{i}.wav")
            with open(sample_path, 'wb') as f:
                f.write(b"FAKE_AUDIO_DATA")
            self.audio_samples.append(sample_path)
        
        # Create a mock config
        self.config_path = os.path.join(self.temp_dir, "config.yml")
        with open(self.config_path, 'w') as f:
            f.write(f"""
voice:
  voice_clone:
    enabled: true
    training_samples: 3
    training_time: 5
    voice_dir: {self.voice_dir}
    temp_dir: {self.temp_dir}
""")
        
        # Create a voice cloner instance
        self.voice_cloner = VoiceCloner(self.config_path)
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_voice(self):
        """Test creating a voice."""
        success, message = self.voice_cloner.create_voice("test_voice", self.audio_samples)
        
        self.assertTrue(success)
        self.assertTrue("created successfully" in message)
        
        # Check that the voice directory was created
        voice_path = os.path.join(self.voice_dir, "test_voice")
        self.assertTrue(os.path.exists(voice_path))
        
        # Check that metadata was created
        metadata_path = os.path.join(voice_path, "metadata.json")
        self.assertTrue(os.path.exists(metadata_path))
        
        # Check that the model file was created
        model_path = os.path.join(voice_path, "model.bin")
        self.assertTrue(os.path.exists(model_path))
    
    def test_create_voice_with_metadata(self):
        """Test creating a voice with metadata."""
        metadata = {
            "description": "Test voice",
            "gender": "female",
            "language": "en-US"
        }
        
        success, message = self.voice_cloner.create_voice("test_voice_meta", self.audio_samples, metadata)
        
        self.assertTrue(success)
        
        # Check the metadata was saved correctly
        metadata_path = os.path.join(self.voice_dir, "test_voice_meta", "metadata.json")
        with open(metadata_path, 'r') as f:
            saved_metadata = json.load(f)
        
        # The metadata should include both the provided values and auto-generated ones
        self.assertEqual(saved_metadata["description"], "Test voice")
        self.assertEqual(saved_metadata["gender"], "female")
        self.assertEqual(saved_metadata["language"], "en-US")
        self.assertEqual(saved_metadata["name"], "test_voice_meta")
    
    def test_list_voices(self):
        """Test listing voices."""
        # Create a couple of voices
        self.voice_cloner.create_voice("voice1", self.audio_samples)
        self.voice_cloner.create_voice("voice2", self.audio_samples)
        
        voices = self.voice_cloner.list_voices()
        
        self.assertEqual(len(voices), 2)
        self.assertIn("voice1", voices)
        self.assertIn("voice2", voices)
    
    def test_delete_voice(self):
        """Test deleting a voice."""
        # Create a voice
        self.voice_cloner.create_voice("voice_to_delete", self.audio_samples)
        
        # Verify it exists
        voice_path = os.path.join(self.voice_dir, "voice_to_delete")
        self.assertTrue(os.path.exists(voice_path))
        
        # Delete it
        success, message = self.voice_cloner.delete_voice("voice_to_delete")
        
        self.assertTrue(success)
        self.assertTrue("deleted successfully" in message)
        
        # Verify it was deleted
        self.assertFalse(os.path.exists(voice_path))
    
    def test_delete_nonexistent_voice(self):
        """Test deleting a nonexistent voice."""
        success, message = self.voice_cloner.delete_voice("nonexistent_voice")
        
        self.assertFalse(success)
        self.assertTrue("does not exist" in message)


if __name__ == '__main__':
    unittest.main()