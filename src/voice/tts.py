"""
Text-to-Speech module using Sesame CSM.
Converts text to speech with configurable voice models.
"""
import os
import logging
import tempfile
import yaml
import json
import subprocess
import requests
from typing import Optional, Dict, Any, Union, Tuple

logger = logging.getLogger(__name__)

class TextToSpeech:
    """
    Text-to-speech conversion using Sesame CSM or alternative engines.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the TTS engine with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../config/default.yml"
        )
        
        # Default settings
        self.engine = "sesame"
        self.voice = "default"
        self.rate = 1.0
        self.pitch = 1.0
        self.audio_format = "wav"
        self.api_url = "http://localhost:8080/api/tts"
        
        # Load configuration
        self._load_config()
        
        # Cache for voice models
        self.voice_models = {}
        
        logger.info(f"TTS initialized with engine: {self.engine}, voice: {self.voice}")
    
    def _load_config(self) -> None:
        """
        Load TTS configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'voice' in config and 'tts' in config['voice']:
                tts_config = config['voice']['tts']
                
                if 'engine' in tts_config:
                    self.engine = tts_config['engine']
                
                if 'voice' in tts_config:
                    self.voice = tts_config['voice']
                
                if 'rate' in tts_config:
                    self.rate = float(tts_config['rate'])
                
                if 'pitch' in tts_config:
                    self.pitch = float(tts_config['pitch'])
                
                if 'audio_format' in tts_config:
                    self.audio_format = tts_config['audio_format']
                
                if 'api_url' in tts_config:
                    self.api_url = tts_config['api_url']
                
            logger.info(f"Loaded TTS configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
    
    def synthesize(self, text: str, voice: Optional[str] = None, 
                  options: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Convert text to speech.
        
        Args:
            text: The text to convert to speech
            voice: Override the default voice
            options: Additional options for synthesis
            
        Returns:
            Audio data as bytes
        """
        if not text:
            logger.warning("Empty text provided for synthesis, returning empty audio")
            return b""
        
        # Select the appropriate engine
        if self.engine == "sesame":
            return self._synthesize_sesame(text, voice, options)
        elif self.engine == "pyttsx3":
            return self._synthesize_pyttsx3(text, voice, options)
        elif self.engine == "api":
            return self._synthesize_api(text, voice, options)
        else:
            logger.error(f"Unsupported TTS engine: {self.engine}")
            return b""
    
    def _synthesize_sesame(self, text: str, voice: Optional[str] = None, 
                          options: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Synthesize speech using Sesame CSM.
        
        Args:
            text: The text to convert to speech
            voice: Override the default voice
            options: Additional options for synthesis
            
        Returns:
            Audio data as bytes
        """
        try:
            # In a real implementation, this would use the Sesame CSM API
            # For now, we'll simulate the output
            
            voice_to_use = voice or self.voice
            logger.info(f"Synthesizing with Sesame CSM, voice: {voice_to_use}")
            
            # Simulated audio data
            # In a real implementation, this would be actual audio data returned from Sesame CSM
            return b"SIMULATED_AUDIO_DATA_FROM_SESAME"
            
        except Exception as e:
            logger.error(f"Error in Sesame synthesis: {str(e)}", exc_info=True)
            return b""
    
    def _synthesize_pyttsx3(self, text: str, voice: Optional[str] = None, 
                           options: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Synthesize speech using pyttsx3 (offline TTS).
        
        Args:
            text: The text to convert to speech
            voice: Override the default voice
            options: Additional options for synthesis
            
        Returns:
            Audio data as bytes
        """
        try:
            # This is a placeholder for the pyttsx3 implementation
            # In a real implementation, this would use pyttsx3 API
            import pyttsx3
            
            voice_to_use = voice or self.voice
            logger.info(f"Synthesizing with pyttsx3, voice: {voice_to_use}")
            
            # Create a temporary file for the audio output
            with tempfile.NamedTemporaryFile(suffix=f".{self.audio_format}", delete=False) as temp_file:
                output_path = temp_file.name
            
            # Initialize the TTS engine
            engine = pyttsx3.init()
            
            # Set voice properties
            voices = engine.getProperty('voices')
            for v in voices:
                if voice_to_use in v.id or voice_to_use in v.name:
                    engine.setProperty('voice', v.id)
                    break
            
            # Set rate and pitch
            engine.setProperty('rate', int(self.rate * 200))  # Default is 200
            # pyttsx3 doesn't directly support pitch, would need to use additional processing
            
            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            # Read the file back as bytes
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(output_path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error in pyttsx3 synthesis: {str(e)}", exc_info=True)
            return b""
    
    def _synthesize_api(self, text: str, voice: Optional[str] = None, 
                       options: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Synthesize speech using an external API.
        
        Args:
            text: The text to convert to speech
            voice: Override the default voice
            options: Additional options for synthesis
            
        Returns:
            Audio data as bytes
        """
        try:
            voice_to_use = voice or self.voice
            logger.info(f"Synthesizing with API, voice: {voice_to_use}")
            
            # Prepare request data
            request_data = {
                "text": text,
                "voice": voice_to_use,
                "rate": self.rate,
                "pitch": self.pitch,
                "format": self.audio_format
            }
            
            # Add any additional options
            if options:
                request_data.update(options)
            
            # Make API request
            response = requests.post(
                self.api_url,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return b""
            
        except Exception as e:
            logger.error(f"Error in API synthesis: {str(e)}", exc_info=True)
            return b""
    
    def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a list of available voices.
        
        Returns:
            Dictionary of available voices and their properties
        """
        available_voices = {}
        
        try:
            if self.engine == "sesame":
                # In a real implementation, this would retrieve available voices from Sesame
                available_voices = {
                    "default": {"gender": "female", "language": "en-US"},
                    "male1": {"gender": "male", "language": "en-US"},
                    "female1": {"gender": "female", "language": "en-US"}
                }
            elif self.engine == "pyttsx3":
                import pyttsx3
                engine = pyttsx3.init()
                for voice in engine.getProperty('voices'):
                    available_voices[voice.id] = {
                        "name": voice.name,
                        "language": voice.languages[0] if voice.languages else "unknown",
                        "gender": "unknown"
                    }
            elif self.engine == "api":
                # Get voices from API
                response = requests.get(
                    f"{self.api_url}/voices",
                    timeout=10
                )
                if response.status_code == 200:
                    available_voices = response.json()
                else:
                    logger.error(f"Failed to get voices from API: {response.status_code}")
            
            logger.info(f"Retrieved {len(available_voices)} available voices")
            return available_voices
            
        except Exception as e:
            logger.error(f"Error getting available voices: {str(e)}", exc_info=True)
            return available_voices