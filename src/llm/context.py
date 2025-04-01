"""
Context management for LLM conversations.
Manages conversation state and context for LLM interactions.
"""
import os
import logging
import json
import yaml
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from collections import deque

from src.llm.prompts import get_prompt_template

logger = logging.getLogger(__name__)

class ConversationContext:
    """
    Manages conversation context for LLM interactions.
    Handles message history, conversation state, and context management.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the conversation context manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../config/default.yml"
        )
        
        # Default settings
        self.max_history = 20
        self.token_limit = 4000
        self.context_type = "call_answering"
        
        # Load configuration
        self._load_config()
        
        # Initialize context
        self.messages = []
        self.metadata = {}
        self.context_variables = {}
        self.last_updated = time.time()
        
        # Initialize memory for tracking entities and actions
        self.entities = {}
        self.actions = []
        
        logger.info("Conversation context initialized")
    
    def _load_config(self) -> None:
        """
        Load configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'llm' in config:
                llm_config = config['llm']
                
                if 'context' in llm_config:
                    context_config = llm_config['context']
                    
                    if 'max_history' in context_config:
                        self.max_history = int(context_config['max_history'])
                    
                    if 'token_limit' in context_config:
                        self.token_limit = int(context_config['token_limit'])
                    
                    if 'context_type' in context_config:
                        self.context_type = context_config['context_type']
                
            logger.info(f"Loaded context configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
    
    def init_conversation(self, conversation_id: Optional[str] = None, 
                         context_type: Optional[str] = None,
                         **metadata) -> None:
        """
        Initialize a new conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            context_type: Type of conversation context to use
            **metadata: Additional metadata for the conversation
        """
        # Reset the context
        self.messages = []
        self.entities = {}
        self.actions = []
        
        # Set the conversation type
        if context_type:
            self.context_type = context_type
        
        # Set metadata
        self.metadata = {
            "conversation_id": conversation_id or f"conv_{int(time.time())}",
            "start_time": time.time(),
            "context_type": self.context_type
        }
        
        # Add any additional metadata
        self.metadata.update(metadata)
        
        # Add the initial system message
        system_prompt = get_prompt_template(self.context_type)
        
        # Format the system prompt with metadata
        try:
            system_prompt = system_prompt.format(**self.metadata)
        except KeyError as e:
            logger.warning(f"Missing metadata key in prompt template: {e}")
        
        self.messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        self.last_updated = time.time()
        logger.info(f"Initialized conversation: {self.metadata['conversation_id']}")
    
    def add_user_message(self, content: str, **metadata) -> None:
        """
        Add a user message to the conversation.
        
        Args:
            content: The message content
            **metadata: Additional metadata for the message
        """
        if not content:
            logger.warning("Attempted to add empty user message, ignoring")
            return
        
        # Create the message
        message = {
            "role": "user",
            "content": content,
            "timestamp": time.time()
        }
        
        # Add any additional metadata
        if metadata:
            message.update(metadata)
        
        # Add to message history
        self.messages.append(message)
        
        # Update entities based on message content
        # In a real implementation, we would extract entities here
        self._extract_entities(content)
        
        # Trim history if needed
        self._trim_history()
        
        self.last_updated = time.time()
        logger.info(f"Added user message: {content[:50]}{'...' if len(content) > 50 else ''}")
    
    def add_assistant_message(self, content: str, **metadata) -> None:
        """
        Add an assistant message to the conversation.
        
        Args:
            content: The message content
            **metadata: Additional metadata for the message
        """
        if not content:
            logger.warning("Attempted to add empty assistant message, ignoring")
            return
        
        # Create the message
        message = {
            "role": "assistant",
            "content": content,
            "timestamp": time.time()
        }
        
        # Add any additional metadata
        if metadata:
            message.update(metadata)
        
        # Add to message history
        self.messages.append(message)
        
        # Extract potential actions from the assistant's response
        self._extract_actions(content)
        
        # Trim history if needed
        self._trim_history()
        
        self.last_updated = time.time()
        logger.info(f"Added assistant message: {content[:50]}{'...' if len(content) > 50 else ''}")
    
    def add_system_message(self, content: str) -> None:
        """
        Add a system message to the conversation.
        
        Args:
            content: The message content
        """
        if not content:
            logger.warning("Attempted to add empty system message, ignoring")
            return
        
        # Create the message
        message = {
            "role": "system",
            "content": content,
            "timestamp": time.time()
        }
        
        # Add to message history
        self.messages.append(message)
        
        self.last_updated = time.time()
        logger.info(f"Added system message: {content[:50]}{'...' if len(content) > 50 else ''}")
    
    def add_action_result(self, action: Dict[str, Any], result: Any) -> None:
        """
        Add the result of an action to the conversation.
        
        Args:
            action: The action that was performed
            result: The result of the action
        """
        # Format the result as a system message
        action_type = action.get('type', 'unknown')
        action_params = action.get('params', {})
        
        # Create a human-readable description of the action
        action_desc = f"Action '{action_type}' was performed"
        if action_params:
            param_strs = [f"{k}='{v}'" for k, v in action_params.items()]
            action_desc += f" with parameters: {', '.join(param_strs)}"
        
        # Format the result
        if isinstance(result, dict):
            result_str = json.dumps(result, indent=2)
        elif isinstance(result, (list, tuple)):
            result_str = "\n".join(str(item) for item in result)
        else:
            result_str = str(result)
        
        # Combine into a system message
        system_message = f"{action_desc}. Result: {result_str}"
        
        # Add to conversation
        self.add_system_message(system_message)
        
        # Add to actions list
        self.actions.append({
            "type": action_type,
            "params": action_params,
            "result": result,
            "timestamp": time.time()
        })
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        Get the current conversation context for the LLM.
        
        Returns:
            List of message dictionaries for the LLM
        """
        return self.messages
    
    def get_user_messages(self) -> List[Dict[str, Any]]:
        """
        Get all user messages in the conversation.
        
        Returns:
            List of user message dictionaries
        """
        return [msg for msg in self.messages if msg.get('role') == 'user']
    
    def get_assistant_messages(self) -> List[Dict[str, Any]]:
        """
        Get all assistant messages in the conversation.
        
        Returns:
            List of assistant message dictionaries
        """
        return [msg for msg in self.messages if msg.get('role') == 'assistant']
    
    def get_latest_message(self, role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the latest message, optionally filtering by role.
        
        Args:
            role: Optional role to filter by ('user', 'assistant', 'system')
            
        Returns:
            Latest message dictionary or None if no messages match
        """
        if role:
            messages = [msg for msg in self.messages if msg.get('role') == role]
        else:
            messages = self.messages
        
        if not messages:
            return None
        
        return messages[-1]
    
    def get_conversation_duration(self) -> float:
        """
        Get the duration of the conversation in seconds.
        
        Returns:
            Duration in seconds
        """
        start_time = self.metadata.get('start_time', 0)
        return time.time() - start_time
    
    def get_entity(self, entity_name: str) -> Any:
        """
        Get an entity value from the conversation.
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            Entity value or None if not found
        """
        return self.entities.get(entity_name)
    
    def set_entity(self, entity_name: str, value: Any) -> None:
        """
        Set an entity value in the conversation.
        
        Args:
            entity_name: Name of the entity
            value: Value to set
        """
        self.entities[entity_name] = value
    
    def clear(self) -> None:
        """
        Clear the conversation context.
        """
        self.messages = []
        self.entities = {}
        self.actions = []
        self.metadata = {}
        self.last_updated = time.time()
        logger.info("Cleared conversation context")
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save the conversation context to a file.
        
        Args:
            file_path: Path to save the conversation
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create the data structure
            data = {
                "metadata": self.metadata,
                "messages": self.messages,
                "entities": self.entities,
                "actions": self.actions,
                "saved_at": time.time()
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved conversation to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}", exc_info=True)
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load conversation context from a file.
        
        Args:
            file_path: Path to the conversation file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Load from file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Restore the data
            self.metadata = data.get('metadata', {})
            self.messages = data.get('messages', [])
            self.entities = data.get('entities', {})
            self.actions = data.get('actions', [])
            self.last_updated = time.time()
            
            logger.info(f"Loaded conversation from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}", exc_info=True)
            return False
    
    def _trim_history(self) -> None:
        """
        Trim conversation history to stay within limits.
        """
        # First, check if we're beyond the max number of messages
        if len(self.messages) <= self.max_history:
            return
        
        # Keep the system messages and the most recent messages
        system_messages = [msg for msg in self.messages if msg.get('role') == 'system']
        non_system_messages = [msg for msg in self.messages if msg.get('role') != 'system']
        
        # Sort non-system messages by timestamp (newest first)
        non_system_messages.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # Keep only the most recent messages up to the limit
        keep_count = min(self.max_history - len(system_messages), len(non_system_messages))
        kept_messages = non_system_messages[:keep_count]
        
        # Sort kept messages back to chronological order
        kept_messages.sort(key=lambda x: x.get('timestamp', 0))
        
        # Rebuild the messages list
        self.messages = system_messages + kept_messages
        
        logger.info(f"Trimmed conversation history to {len(self.messages)} messages")
    
    def _extract_entities(self, text: str) -> None:
        """
        Extract entities from user message.
        In a real implementation, this would use NLP techniques.
        
        Args:
            text: The message text to extract entities from
        """
        # Placeholder for entity extraction
        # In a real implementation, this would use NLP or regex patterns
        pass
    
    def _extract_actions(self, text: str) -> None:
        """
        Extract actions from assistant message.
        In a real implementation, this would detect action patterns.
        
        Args:
            text: The message text to extract actions from
        """
        # Placeholder for action extraction
        # In a real implementation, this would detect action keywords or structured formats
        pass