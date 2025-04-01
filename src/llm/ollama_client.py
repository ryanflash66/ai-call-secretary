"""
Ollama client for LLM integration.
Provides a client for interacting with locally hosted Ollama models.
"""
import os
import logging
import json
import yaml
import requests
import time
from typing import Dict, List, Optional, Any, Union, Tuple

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Client for interacting with Ollama LLM API.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Ollama client with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../config/default.yml"
        )
        
        # Default settings
        self.api_url = "http://localhost:11434/api"
        self.model = "mistral"
        self.temperature = 0.7
        self.system_prompt = "You are an AI assistant for a call answering service. Your job is to professionally greet callers, understand their requests, and take appropriate actions."
        self.max_tokens = 500
        self.timeout = 15
        
        # Load configuration
        self._load_config()
        
        logger.info(f"Ollama client initialized with model: {self.model}")
    
    def _load_config(self) -> None:
        """
        Load configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'llm' in config:
                llm_config = config['llm']
                
                if 'model' in llm_config:
                    self.model = llm_config['model']
                
                if 'temperature' in llm_config:
                    self.temperature = float(llm_config['temperature'])
                
                if 'system_prompt' in llm_config:
                    self.system_prompt = llm_config['system_prompt']
                
                if 'max_tokens' in llm_config:
                    self.max_tokens = int(llm_config['max_tokens'])
                
                if 'timeout' in llm_config:
                    self.timeout = int(llm_config['timeout'])
                
                if 'api_url' in llm_config:
                    self.api_url = llm_config['api_url']
                
            logger.info(f"Loaded LLM configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
    
    def _check_model_availability(self) -> bool:
        """
        Check if the specified model is available in Ollama.
        
        Returns:
            True if the model is available, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == self.model for model in models)
            else:
                logger.warning(f"Failed to get models from Ollama: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking model availability: {str(e)}", exc_info=True)
            return False
    
    def _pull_model_if_needed(self) -> bool:
        """
        Pull the model if it's not available locally.
        
        Returns:
            True if the model is available (either already or after pulling),
            False if the model couldn't be pulled
        """
        if self._check_model_availability():
            return True
        
        logger.info(f"Model {self.model} not found locally, attempting to pull")
        
        try:
            # Pull the model
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": self.model},
                timeout=600  # Longer timeout for model pulling
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully pulled model {self.model}")
                return True
            else:
                logger.error(f"Failed to pull model {self.model}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}", exc_info=True)
            return False
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate a response using the Ollama API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            options: Additional options for the generation
            
        Returns:
            Generated response text or None if generation failed
        """
        try:
            # Ensure model is available
            if not self._pull_model_if_needed():
                logger.error(f"Model {self.model} is not available")
                return None
            
            # Parse messages to ensure they have the correct format
            formatted_messages = []
            
            # Always start with system message if not already included
            has_system = any(msg.get('role') == 'system' for msg in messages)
            if not has_system and self.system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": self.system_prompt
                })
            
            # Add the rest of the messages
            for msg in messages:
                role = msg.get('role', '').lower()
                content = msg.get('content', '')
                
                if role in ['system', 'user', 'assistant'] and content:
                    formatted_messages.append({
                        "role": role,
                        "content": content
                    })
            
            # Default options
            request_options = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "num_predict": self.max_tokens
            }
            
            # Update with any user-provided options
            if options:
                request_options.update(options)
            
            # Prepare the request
            request_data = {
                "model": self.model,
                "messages": formatted_messages,
                "options": request_options,
                "stream": False
            }
            
            # Make the request
            response = requests.post(
                f"{self.api_url}/chat",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('message', {}).get('content', '')
                
                if generated_text:
                    logger.info(f"Generated response of {len(generated_text)} characters")
                    return generated_text
                else:
                    logger.warning("Empty response from Ollama API")
                    return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return None
    
    def stream_response(self, messages: List[Dict[str, str]], 
                       callback: callable,
                       options: Optional[Dict[str, Any]] = None) -> bool:
        """
        Stream a response from the Ollama API with a callback for each chunk.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            callback: Callback function that receives each text chunk
            options: Additional options for the generation
            
        Returns:
            True if streaming completed successfully, False otherwise
        """
        try:
            # Ensure model is available
            if not self._pull_model_if_needed():
                logger.error(f"Model {self.model} is not available")
                return False
            
            # Parse messages (same as in generate_response)
            formatted_messages = []
            
            has_system = any(msg.get('role') == 'system' for msg in messages)
            if not has_system and self.system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": self.system_prompt
                })
            
            for msg in messages:
                role = msg.get('role', '').lower()
                content = msg.get('content', '')
                
                if role in ['system', 'user', 'assistant'] and content:
                    formatted_messages.append({
                        "role": role,
                        "content": content
                    })
            
            # Default options
            request_options = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "num_predict": self.max_tokens
            }
            
            # Update with any user-provided options
            if options:
                request_options.update(options)
            
            # Prepare the request
            request_data = {
                "model": self.model,
                "messages": formatted_messages,
                "options": request_options,
                "stream": True
            }
            
            # Make the streaming request
            with requests.post(
                f"{self.api_url}/chat",
                json=request_data,
                timeout=self.timeout,
                stream=True
            ) as response:
                if response.status_code != 200:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    return False
                
                full_response = ""
                
                # Process each chunk in the stream
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            chunk_text = chunk.get('message', {}).get('content', '')
                            
                            if chunk_text:
                                full_response += chunk_text
                                callback(chunk_text)
                            
                            # Check for done flag
                            if chunk.get('done', False):
                                logger.info(f"Streaming complete, total length: {len(full_response)}")
                                break
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse chunk: {line}")
                            continue
                
                return True
                
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}", exc_info=True)
            return False
    
    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embeddings for the given text using Ollama.
        
        Args:
            text: The text to embed
            
        Returns:
            List of embedding values or None if embedding failed
        """
        try:
            # Embeddings endpoint
            response = requests.post(
                f"{self.api_url}/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                embeddings = result.get('embedding', [])
                logger.info(f"Generated embeddings with dimension {len(embeddings)}")
                return embeddings
            else:
                logger.error(f"Embedding request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}", exc_info=True)
            return None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from Ollama.
        
        Returns:
            List of available models and their metadata
        """
        try:
            response = requests.get(
                f"{self.api_url}/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json().get('models', [])
            else:
                logger.error(f"Failed to get models: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}", exc_info=True)
            return []