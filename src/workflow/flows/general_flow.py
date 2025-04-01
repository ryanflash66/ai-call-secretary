"""
General conversation flow for basic interactions.
This flow handles general inquiries and routes to more specific flows as needed.
"""
import logging
import re
import time
from typing import Dict, List, Optional, Any, Union, Tuple

from src.workflow.flows.base_flow import BaseFlow

logger = logging.getLogger(__name__)

class GeneralFlow(BaseFlow):
    """
    General conversation flow for basic interactions.
    """
    
    def initialize(self, flow_data: Dict[str, Any]) -> None:
        """
        Initialize the flow with data.
        
        Args:
            flow_data: Initial data for the flow
        """
        super().initialize(flow_data)
        
        # Initialize general flow state
        if 'state' not in flow_data:
            flow_data['state'] = 'greeting'
        
        # Initialize interaction tracking
        if 'interactions' not in flow_data:
            flow_data['interactions'] = []
        
        # Initialize entities
        if 'entities' not in flow_data:
            flow_data['entities'] = {}
        
        logger.info("General flow initialized")
    
    def process(self, message: str, metadata: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message through the general flow.
        
        Args:
            message: The message to process
            metadata: Additional metadata
            flow_data: Current flow data
            
        Returns:
            Updated flow data with processing results
        """
        super().process(message, metadata, flow_data)
        
        # Extract entities from message
        entities = self._extract_entities(message)
        self._update_entities(flow_data, entities)
        
        # Track this interaction
        flow_data['interactions'].append({
            'message': message,
            'timestamp': time.time(),
            'entities': entities
        })
        
        # Analyze intent
        intent = self._analyze_intent(message, flow_data)
        logger.info(f"Detected intent: {intent}")
        
        # Handle the message based on current state and intent
        result = self._handle_message(message, intent, metadata, flow_data)
        
        # Update flow data
        flow_data.update(result)
        
        return flow_data
    
    def _update_entities(self, flow_data: Dict[str, Any], new_entities: Dict[str, Any]) -> None:
        """
        Update the entities in flow data with new entities.
        
        Args:
            flow_data: Current flow data
            new_entities: New entities to add
        """
        for entity_type, entities in new_entities.items():
            if entity_type not in flow_data['entities']:
                flow_data['entities'][entity_type] = []
            
            # Add new entities, avoiding duplicates
            for entity in entities:
                if entity not in flow_data['entities'][entity_type]:
                    flow_data['entities'][entity_type].append(entity)
    
    def _analyze_intent(self, message: str, flow_data: Dict[str, Any]) -> str:
        """
        Analyze the intent of a message.
        
        Args:
            message: The message to analyze
            flow_data: Current flow data
            
        Returns:
            Intent category
        """
        # This is a simple rule-based intent classification
        # In a real implementation, this would use an NLU model or service
        
        message = message.lower()
        
        # Appointment-related
        if re.search(r'(appointment|schedule|book|meeting|consultation|session)', message):
            return 'appointment'
        
        # Message-related
        if re.search(r'(message|tell|let .* know|pass along|relay)', message):
            return 'message'
        
        # Information-related
        if re.search(r'(information|details|tell me about|what is|how do|hours|location|address|phone|website|email)', message):
            return 'information'
        
        # Escalation-related
        if re.search(r'(speak to .* human|speak to .* person|real person|supervisor|manager|speak to someone else|transfer|operator)', message):
            return 'escalation'
        
        # If no specific intent is detected
        return 'general'
    
    def _handle_message(self, message: str, intent: str, metadata: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a message based on intent and current state.
        
        Args:
            message: The message to handle
            intent: The detected intent
            metadata: Additional metadata
            flow_data: Current flow data
            
        Returns:
            Processing results
        """
        current_state = flow_data.get('state', 'greeting')
        
        # If we're in greeting state, update to conversation state
        if current_state == 'greeting':
            flow_data['state'] = 'conversation'
            
        # Handle based on intent - transition to specialized flow if needed
        if intent == 'appointment' and intent != flow_data.get('current_intent'):
            # Transition to appointment flow
            self.flow_manager.start_flow('appointment', flow_data)
            return {'transitioned_to': 'appointment'}
            
        elif intent == 'message' and intent != flow_data.get('current_intent'):
            # Transition to message flow
            self.flow_manager.start_flow('message', flow_data)
            return {'transitioned_to': 'message'}
            
        elif intent == 'information' and intent != flow_data.get('current_intent'):
            # Transition to information flow
            self.flow_manager.start_flow('info', flow_data)
            return {'transitioned_to': 'information'}
            
        elif intent == 'escalation' and intent != flow_data.get('current_intent'):
            # Transition to escalation flow
            self.flow_manager.start_flow('escalation', flow_data)
            return {'transitioned_to': 'escalation'}
        
        # Update current intent
        flow_data['current_intent'] = intent
        
        # For general intent, extract actions if any
        actions = self._extract_actions(message)
        results = []
        
        # Execute actions if any
        if actions:
            for action in actions:
                result = self._execute_action(action)
                results.append(result)
        
        return {
            'processing_results': {
                'intent': intent,
                'actions': results if results else None
            }
        }
    
    def cleanup(self, flow_data: Dict[str, Any]) -> None:
        """
        Clean up the flow.
        
        Args:
            flow_data: Current flow data
        """
        super().cleanup(flow_data)
        
        # Save any necessary data or state before exiting
        flow_data['last_active'] = time.time()
        
        logger.info("General flow cleaned up")
    
    def resume(self, flow_data: Dict[str, Any]) -> None:
        """
        Resume the flow after a nested flow completes.
        
        Args:
            flow_data: Updated flow data
        """
        super().resume(flow_data)
        
        # Reset current intent to allow new intent detection
        flow_data['current_intent'] = 'general'
        
        # Update state
        flow_data['state'] = 'resumed'
        
        logger.info("General flow resumed")