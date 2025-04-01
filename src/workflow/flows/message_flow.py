"""
Message flow for taking and managing messages.
"""
import logging
import re
import time
from typing import Dict, List, Optional, Any, Union, Tuple

from src.workflow.flows.base_flow import BaseFlow

logger = logging.getLogger(__name__)

class MessageFlow(BaseFlow):
    """
    Flow for taking and managing messages.
    """
    
    # States for the message flow
    STATES = {
        'INIT': 'init',
        'COLLECTING_MESSAGE': 'collecting_message',
        'COLLECTING_CALLER_INFO': 'collecting_caller_info',
        'COLLECTING_URGENCY': 'collecting_urgency',
        'COLLECTING_CALLBACK': 'collecting_callback',
        'CONFIRMING': 'confirming',
        'COMPLETED': 'completed',
        'CANCELLED': 'cancelled'
    }
    
    def initialize(self, flow_data: Dict[str, Any]) -> None:
        """
        Initialize the message flow.
        
        Args:
            flow_data: Initial data for the flow
        """
        super().initialize(flow_data)
        
        # Initialize message data if not present
        if 'message_data' not in flow_data:
            flow_data['message_data'] = {
                'message': None,
                'caller_name': flow_data.get('caller_name', None),
                'caller_number': flow_data.get('caller_number', None),
                'urgency': 'normal',
                'callback_requested': False,
                'state': self.STATES['INIT']
            }
        
        # Set the initial state if not already set
        if 'state' not in flow_data['message_data']:
            flow_data['message_data']['state'] = self.STATES['INIT']
        
        logger.info("Message flow initialized")
    
    def process(self, message: str, metadata: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message through the message flow.
        
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
        
        # Current state
        current_state = flow_data['message_data']['state']
        logger.info(f"Processing message in message flow, state: {current_state}")
        
        # Process based on current state
        if current_state == self.STATES['INIT']:
            return self._process_init(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_MESSAGE']:
            return self._process_collecting_message(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_CALLER_INFO']:
            return self._process_collecting_caller_info(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_URGENCY']:
            return self._process_collecting_urgency(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_CALLBACK']:
            return self._process_collecting_callback(message, entities, flow_data)
        elif current_state == self.STATES['CONFIRMING']:
            return self._process_confirming(message, entities, flow_data)
        else:
            # Unknown state, reset to initial
            flow_data['message_data']['state'] = self.STATES['INIT']
            logger.warning(f"Unknown message state: {current_state}, resetting to INIT")
            return self._process_init(message, entities, flow_data)
    
    def _process_init(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message in the initial state.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # If the message is short, assume it's not the full message
        if len(message.split()) < 5:
            flow_data['message_data']['state'] = self.STATES['COLLECTING_MESSAGE']
        else:
            # Assume this is the message
            flow_data['message_data']['message'] = message
            
            # If we don't have caller info, collect it next
            if not flow_data['message_data']['caller_name']:
                flow_data['message_data']['state'] = self.STATES['COLLECTING_CALLER_INFO']
            else:
                flow_data['message_data']['state'] = self.STATES['COLLECTING_URGENCY']
        
        return flow_data
    
    def _process_collecting_message(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting the message content.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        flow_data['message_data']['message'] = message
        
        # If we don't have caller info, collect it next
        if not flow_data['message_data']['caller_name']:
            flow_data['message_data']['state'] = self.STATES['COLLECTING_CALLER_INFO']
        else:
            flow_data['message_data']['state'] = self.STATES['COLLECTING_URGENCY']
        
        return flow_data
    
    def _process_collecting_caller_info(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting caller information.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Check for name in entities
        if 'names' in entities and entities['names']:
            flow_data['message_data']['caller_name'] = entities['names'][0]
        else:
            # If no name entity, use the message as the name
            flow_data['message_data']['caller_name'] = message
        
        # Check for phone number
        if 'phone_numbers' in entities and entities['phone_numbers']:
            flow_data['message_data']['caller_number'] = entities['phone_numbers'][0]
        
        # Move to next state
        flow_data['message_data']['state'] = self.STATES['COLLECTING_URGENCY']
        return flow_data
    
    def _process_collecting_urgency(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting urgency level.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        urgency = self._determine_urgency(message)
        flow_data['message_data']['urgency'] = urgency
        
        # Move to callback
        flow_data['message_data']['state'] = self.STATES['COLLECTING_CALLBACK']
        return flow_data
    
    def _process_collecting_callback(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting callback preference.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        callback_requested = self._determine_callback_preference(message)
        flow_data['message_data']['callback_requested'] = callback_requested
        
        # Move to confirmation
        flow_data['message_data']['state'] = self.STATES['CONFIRMING']
        return flow_data
    
    def _process_confirming(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when confirming the message.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Check for confirmation or denial
        if self._is_confirmation(message):
            # Save the message via action
            action = {
                'type': 'take_message',
                'params': {
                    'message': flow_data['message_data']['message'],
                    'caller_name': flow_data['message_data']['caller_name'],
                    'caller_number': flow_data['message_data']['caller_number'],
                    'urgency': flow_data['message_data']['urgency'],
                    'callback_requested': flow_data['message_data']['callback_requested']
                }
            }
            
            result = self._execute_action(action)
            flow_data['message_result'] = result
            
            # Mark as completed
            flow_data['message_data']['state'] = self.STATES['COMPLETED']
            
            # End the flow
            self.flow_manager.end_flow(flow_data)
            
        elif self._is_denial(message):
            # Cancel the message process
            flow_data['message_data']['state'] = self.STATES['CANCELLED']
            self.flow_manager.end_flow(flow_data)
        
        # Otherwise stay in confirming state
        return flow_data
    
    def _determine_urgency(self, message: str) -> str:
        """
        Determine the urgency level from a message.
        
        Args:
            message: The message to analyze
            
        Returns:
            Urgency level: 'low', 'normal', 'high', or 'critical'
        """
        message = message.lower()
        
        # Check for critical urgency
        if re.search(r'(emergency|urgent|critical|asap|immediately|right away|life or death|crisis)', message):
            return 'critical'
        
        # Check for high urgency
        if re.search(r'(important|priority|pressing|significant|soon|quickly)', message):
            return 'high'
        
        # Check for low urgency
        if re.search(r'(whenever|no rush|low priority|not urgent|can wait|eventually|not important)', message):
            return 'low'
        
        # Default to normal
        return 'normal'
    
    def _determine_callback_preference(self, message: str) -> bool:
        """
        Determine if a callback is requested.
        
        Args:
            message: The message to analyze
            
        Returns:
            True if callback is requested, False otherwise
        """
        message = message.lower()
        
        # Check for callback request
        if re.search(r'(call back|callback|return call|call me|reach me|get back to me|reach out|contact me)', message):
            return True
        
        # Check for no callback
        if re.search(r'(no need to call|don\'t call|do not call|won\'t be available|not necessary to call)', message):
            return False
        
        # Look for affirmative responses
        if self._is_confirmation(message):
            return True
        
        # Look for negative responses
        if self._is_denial(message):
            return False
        
        # Default based on context - if they provided a phone number, assume callback
        return False
    
    def _is_confirmation(self, message: str) -> bool:
        """
        Check if a message is a confirmation.
        
        Args:
            message: The message to check
            
        Returns:
            True if it's a confirmation, False otherwise
        """
        message = message.lower()
        confirmation_patterns = [
            r'\b(yes|yeah|sure|confirm|correct|right|ok|okay|fine|good|perfect|sounds good|that works)\b',
            r'\b(save it|send it|deliver it|record it|take it|proceed|go ahead)\b'
        ]
        
        for pattern in confirmation_patterns:
            if re.search(pattern, message):
                return True
        
        return False
    
    def _is_denial(self, message: str) -> bool:
        """
        Check if a message is a denial.
        
        Args:
            message: The message to check
            
        Returns:
            True if it's a denial, False otherwise
        """
        message = message.lower()
        denial_patterns = [
            r'\b(no|nope|not|don\'t|do not|cancel|stop|forget|won\'t|will not|never mind)\b',
            r'\b(incorrect|wrong|bad|invalid|mistaken|error|mistake)\b'
        ]
        
        for pattern in denial_patterns:
            if re.search(pattern, message):
                return True
        
        return False
    
    def cleanup(self, flow_data: Dict[str, Any]) -> None:
        """
        Clean up the message flow.
        
        Args:
            flow_data: Current flow data
        """
        super().cleanup(flow_data)
        
        # Add timestamp
        flow_data['message_data']['last_updated'] = time.time()
        
        logger.info("Message flow cleaned up")
    
    def resume(self, flow_data: Dict[str, Any]) -> None:
        """
        Resume the message flow.
        
        Args:
            flow_data: Updated flow data
        """
        super().resume(flow_data)
        
        # If we were completed or cancelled, end the flow
        if flow_data['message_data']['state'] in [self.STATES['COMPLETED'], self.STATES['CANCELLED']]:
            self.flow_manager.end_flow(flow_data)
        
        logger.info("Message flow resumed")