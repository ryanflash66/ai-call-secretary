"""
Base flow class for all conversation flows.
Provides common functionality for all flows.
"""
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

logger = logging.getLogger(__name__)

class BaseFlow:
    """
    Base class for all conversation flows.
    """
    
    def __init__(self, flow_manager):
        """
        Initialize the flow with the flow manager.
        
        Args:
            flow_manager: The flow manager instance
        """
        self.flow_manager = flow_manager
        self.flow_id = self.__class__.__name__.lower().replace('flow', '')
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def initialize(self, flow_data: Dict[str, Any]) -> None:
        """
        Initialize the flow with data.
        
        Args:
            flow_data: Initial data for the flow
        """
        logger.info(f"Initializing {self.__class__.__name__}")
    
    def process(self, message: str, metadata: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message.
        
        Args:
            message: The message to process
            metadata: Additional metadata
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        logger.info(f"Processing message in {self.__class__.__name__}")
        return flow_data
    
    def cleanup(self, flow_data: Dict[str, Any]) -> None:
        """
        Clean up the flow.
        
        Args:
            flow_data: Current flow data
        """
        logger.info(f"Cleaning up {self.__class__.__name__}")
    
    def resume(self, flow_data: Dict[str, Any]) -> None:
        """
        Resume the flow after a nested flow completes.
        
        Args:
            flow_data: Updated flow data
        """
        logger.info(f"Resuming {self.__class__.__name__}")
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract entities from a message.
        
        Args:
            message: The message to extract entities from
            
        Returns:
            Dictionary of extracted entities
        """
        # This is a placeholder. In a real implementation, this would use more sophisticated
        # entity extraction techniques or call into an NLU service.
        from src.workflow.actions import extract_entities_from_text
        return extract_entities_from_text(message)
    
    def _extract_actions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract actions from text.
        
        Args:
            text: The text to extract actions from
            
        Returns:
            List of action dictionaries
        """
        from src.workflow.actions import ActionHandler
        action_handler = ActionHandler()
        return action_handler.extract_actions(text)
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the action
        """
        from src.workflow.actions import ActionHandler
        action_handler = ActionHandler()
        return action_handler.execute_action(action)