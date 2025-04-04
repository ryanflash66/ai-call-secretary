"""
Voice cloning functionality.
Allows creation of custom voice models for TTS using sample recordings.
"""
import os
import logging
import yaml
import json
import tempfile
import shutil
import subprocess
from typing import Optional, Dict, Any, List, Tuple, Union

logger = logging.getLogger(__name__)

class VoiceCloner:
    """
    Voice cloning functionality to create custom TTS voices.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the voice cloner with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../config/default.yml"
        )
        
        # Default settings
        self.enabled = False
        self.training_samples = 5
        self.training_time = 300  # seconds
        self.voice_dir = os.path.join(os.path.dirname(__file__), "../../data/voices")
        self.temp_dir = os.path.join(os.path.dirname(__file__), "../../data/temp")
        
        # Load configuration
        self._load_config()
        
        # Ensure directories exist
        os.makedirs(self.voice_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        logger.info(f"Voice cloner initialized, enabled: {self.enabled}")
    
    def _load_config(self) -> None:
        """
        Load voice cloning configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'voice' in config and 'voice_clone' in config['voice']:
                vc_config = config['voice']['voice_clone']
                
                if 'enabled' in vc_config:
                    self.enabled = bool(vc_config['enabled'])
                
                if 'training_samples' in vc_config:
                    self.training_samples = int(vc_config['training_samples'])
                
                if 'training_time' in vc_config:
                    self.training_time = int(vc_config['training_time'])
                
                if 'voice_dir' in vc_config:
                    self.voice_dir = vc_config['voice_dir']
                
                if 'temp_dir' in vc_config:
                    self.temp_dir = vc_config['temp_dir']
                
            logger.info(f"Loaded voice cloning configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
    
    def create_voice(self, voice_name: str, audio_samples: List[Union[str, bytes]], 
                    metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Create a new voice model from audio samples.
        
        Args:
            voice_name: Name for the new voice
            audio_samples: List of audio samples (file paths or audio data)
            metadata: Optional metadata for the voice
            
        Returns:
            Tuple of (success, message)
        """
        if not self.enabled:
            logger.warning("Voice cloning is disabled in configuration")
            return False, "Voice cloning is disabled"
        
        if len(audio_samples) < self.training_samples:
            logger.warning(f"Not enough audio samples provided. Need at least {self.training_samples}")
            return False, f"Not enough audio samples. Need at least {self.training_samples}"
        
        try:
            logger.info(f"Creating voice model: {voice_name}")
            
            # Create a unique voice directory
            voice_path = os.path.join(self.voice_dir, voice_name)
            if os.path.exists(voice_path):
                logger.warning(f"Voice '{voice_name}' already exists")
                return False, f"Voice '{voice_name}' already exists"
            
            os.makedirs(voice_path, exist_ok=True)
            
            # Process audio samples
            sample_paths = []
            for i, sample in enumerate(audio_samples):
                sample_path = self._process_audio_sample(sample, voice_name, i)
                if sample_path:
                    sample_paths.append(sample_path)
            
            if len(sample_paths) < self.training_samples:
                logger.warning(f"Not enough valid audio samples after processing")
                shutil.rmtree(voice_path)
                return False, "Not enough valid audio samples after processing"
            
            # Train the voice model
            # In a real implementation, this would call the voice cloning system
            # For this example, we'll simulate the training process
            success, message = self._train_voice_model(voice_name, sample_paths, metadata)
            
            if not success:
                logger.error(f"Voice training failed: {message}")
                shutil.rmtree(voice_path)
                return False, message
            
            logger.info(f"Voice '{voice_name}' created successfully")
            return True, f"Voice '{voice_name}' created successfully"
            
        except Exception as e:
            logger.error(f"Error creating voice: {str(e)}", exc_info=True)
            # Clean up any partial directory
            if os.path.exists(voice_path):
                shutil.rmtree(voice_path)
            return False, f"Error creating voice: {str(e)}"
    
    def _process_audio_sample(self, sample: Union[str, bytes], voice_name: str, index: int) -> Optional[str]:
        """
        Process an audio sample for voice training.
        
        Args:
            sample: The audio sample (file path or audio data)
            voice_name: Name of the voice being created
            index: Sample index
            
        Returns:
            Path to the processed sample or None if processing failed
        """
        try:
            # Create a unique sample name
            sample_name = f"{voice_name}_sample_{index:03d}.wav"
            sample_path = os.path.join(self.voice_dir, voice_name, sample_name)
            
            # Process the sample based on its type
            if isinstance(sample, str) and os.path.exists(sample):
                # It's a file path
                logger.info(f"Processing audio sample from file: {sample}")
                
                # In a real implementation, we would normalize audio, check quality, etc.
                # For now, we'll just copy the file
                shutil.copy2(sample, sample_path)
                
            elif isinstance(sample, bytes):
                # It's audio data
                logger.info(f"Processing audio sample from binary data")
                
                # Save to a temporary file
                with open(sample_path, 'wb') as f:
                    f.write(sample)
                
                # In a real implementation, we would normalize the audio here
            
            logger.info(f"Audio sample processed: {sample_path}")
            return sample_path
            
        except Exception as e:
            logger.error(f"Error processing audio sample: {str(e)}", exc_info=True)
            return None
    
    def _train_voice_model(self, voice_name: str, sample_paths: List[str],
                          metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Train a voice model from processed samples.
        
        Args:
            voice_name: Name of the voice being created
            sample_paths: List of paths to processed audio samples
            metadata: Optional metadata for the voice
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(f"Training voice model '{voice_name}' with {len(sample_paths)} samples")
            
            voice_path = os.path.join(self.voice_dir, voice_name)
            
            # In a real implementation, this would call the voice cloning system
            # We'll simulate the training process with a wait
            logger.info(f"Voice training would take approximately {self.training_time} seconds")
            
            # Create a metadata file
            model_metadata = {
                "name": voice_name,
                "samples": len(sample_paths),
                "created_at": os.path.getmtime(voice_path),
                "training_time": self.training_time
            }
            
            if metadata:
                model_metadata.update(metadata)
            
            # Save metadata
            with open(os.path.join(voice_path, "metadata.json"), 'w') as f:
                json.dump(model_metadata, f, indent=2)
            
            # Create a dummy model file to simulate the trained model
            with open(os.path.join(voice_path, "model.bin"), 'wb') as f:
                f.write(b"SIMULATED_VOICE_MODEL_DATA")
            
            logger.info(f"Voice model '{voice_name}' trained successfully")
            return True, "Voice model trained successfully"
            
        except Exception as e:
            logger.error(f"Error training voice model: {str(e)}", exc_info=True)
            return False, f"Error training voice model: {str(e)}"
    
    def list_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available custom voices.
        
        Returns:
            Dictionary of voice names and their metadata
        """
        voices = {}
        
        try:
            # Check if voice directory exists
            if not os.path.exists(self.voice_dir):
                logger.warning(f"Voice directory does not exist: {self.voice_dir}")
                return voices
            
            # Scan the voice directory for voice models
            for voice_name in os.listdir(self.voice_dir):
                voice_path = os.path.join(self.voice_dir, voice_name)
                
                if os.path.isdir(voice_path):
                    # Check for metadata file
                    metadata_path = os.path.join(voice_path, "metadata.json")
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            try:
                                metadata = json.load(f)
                                voices[voice_name] = metadata
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid metadata for voice: {voice_name}")
                                voices[voice_name] = {"name": voice_name, "error": "Invalid metadata"}
                    else:
                        # Create basic metadata from directory
                        voices[voice_name] = {
                            "name": voice_name,
                            "created_at": os.path.getmtime(voice_path)
                        }
            
            logger.info(f"Found {len(voices)} custom voices")
            return voices
            
        except Exception as e:
            logger.error(f"Error listing voices: {str(e)}", exc_info=True)
            return voices
    
    def delete_voice(self, voice_name: str) -> Tuple[bool, str]:
        """
        Delete a custom voice.
        
        Args:
            voice_name: Name of the voice to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            voice_path = os.path.join(self.voice_dir, voice_name)
            
            if not os.path.exists(voice_path):
                logger.warning(f"Voice '{voice_name}' does not exist")
                return False, f"Voice '{voice_name}' does not exist"
            
            # Remove the voice directory
            shutil.rmtree(voice_path)
            
            logger.info(f"Voice '{voice_name}' deleted successfully")
            return True, f"Voice '{voice_name}' deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting voice: {str(e)}", exc_info=True)
            return False, f"Error deleting voice: {str(e)}"