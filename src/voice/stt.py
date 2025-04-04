"""
Speech-to-Text module using Whisper.
Converts audio to text using the Whisper ASR model.
"""
import os
import logging
import tempfile
import yaml
import numpy as np
from typing import Optional, Dict, Any, Union
import whisper

logger = logging.getLogger(__name__)

class SpeechToText:
    """
    Speech-to-text conversion using Whisper ASR.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the STT engine with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../config/default.yml"
        )
        
        # Default settings
        self.model_name = "tiny"
        self.language = "en"
        self.device = "cpu"
        self.compute_type = "int8"
        
        # Load configuration
        self._load_config()
        
        # Load model - defer until first use to save memory
        self.model = None
        
        logger.info(f"STT initialized with model: {self.model_name}, language: {self.language}")
    
    def _load_config(self) -> None:
        """
        Load STT configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'voice' in config and 'stt' in config['voice']:
                stt_config = config['voice']['stt']
                
                if 'model' in stt_config:
                    self.model_name = stt_config['model']
                
                if 'language' in stt_config:
                    self.language = stt_config['language']
                
                if 'device' in stt_config:
                    self.device = stt_config['device']
                
                if 'compute_type' in stt_config:
                    self.compute_type = stt_config['compute_type']
                
            logger.info(f"Loaded STT configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
    
    def _ensure_model_loaded(self) -> None:
        """
        Ensure the Whisper model is loaded.
        """
        if self.model is None:
            try:
                logger.info(f"Loading Whisper model: {self.model_name}")
                self.model = whisper.load_model(
                    self.model_name,
                    device=self.device,
                    compute_type=self.compute_type
                )
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {str(e)}", exc_info=True)
                raise RuntimeError(f"Failed to load Whisper model: {str(e)}")
    
    def transcribe(self, audio_data: Union[bytes, str, np.ndarray], 
                  options: Optional[Dict[str, Any]] = None) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: The audio data to transcribe. Can be:
                - bytes: Raw audio data (will be saved to temporary file)
                - str: Path to an audio file
                - np.ndarray: Audio waveform data
            options: Additional options for the transcription
            
        Returns:
            Transcription text
        """
        try:
            # Ensure model is loaded
            self._ensure_model_loaded()
            
            # Set default options
            transcribe_options = {
                "language": self.language,
                "task": "transcribe"
            }
            
            # Update with any user-provided options
            if options:
                transcribe_options.update(options)
            
            # Handle different types of audio input
            audio_input = audio_data
            temp_file = None
            
            if isinstance(audio_data, bytes):
                # Save bytes to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                temp_file.write(audio_data)
                temp_file.close()
                audio_input = temp_file.name
            
            # Transcribe the audio
            result = self.model.transcribe(audio_input, **transcribe_options)
            transcription = result.get("text", "").strip()
            
            # Clean up the temporary file if created
            if temp_file:
                os.unlink(temp_file.name)
            
            logger.info(f"Transcribed audio: {transcription[:50]}{'...' if len(transcription) > 50 else ''}")
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
            return ""
    
    def stream_transcribe(self, audio_stream, chunk_duration_ms: int = 1000,
                         options: Optional[Dict[str, Any]] = None) -> str:
        """
        Transcribe streaming audio in chunks.
        
        Args:
            audio_stream: A stream of audio data
            chunk_duration_ms: Duration of each chunk in milliseconds
            options: Additional options for the transcription
            
        Returns:
            Transcription text
        """
        # NOTE: This is a simplified streaming transcription implementation
        # In a production system, this would be more sophisticated, handling
        # partial results, timeouts, etc.
        try:
            # Ensure model is loaded
            self._ensure_model_loaded()
            
            # In a real implementation, we would accumulate audio and transcribe in chunks
            # For now, we'll just assume the audio_stream has a read() method to get all data
            audio_data = audio_stream.read()
            return self.transcribe(audio_data, options)
            
        except Exception as e:
            logger.error(f"Error in streaming transcription: {str(e)}", exc_info=True)
            return ""