"""
Escalation flow for handling escalations to a human operator.
"""
import logging
import re
import time
from typing import Dict, List, Optional, Any, Union, Tuple

from src.workflow.flows.base_flow import BaseFlow

logger = logging.getLogger(__name__)

class EscalationFlow(BaseFlow):
    """
    Flow for escalating calls to a human operator.
    """
    
    # States for the escalation flow
    STATES = {
        'INIT': 'init',
        'COLLECTING_REASON': 'collecting_reason',
        'PREPARING_TRANSFER': 'preparing_transfer',
        'TRANSFERRING': 'transferring',
        'COMPLETED': 'completed',
        'FAILED': 'failed'
    }
    
    # Escalation destinations
    DESTINATIONS = {
        'GENERAL': 'general',
        'SUPPORT': 'support',
        'SALES': 'sales',
        'BILLING': 'billing',
        'EMERGENCY': 'emergency',
        'SPECIFIC': 'specific_person'
    }
    
    def initialize(self, flow_data: Dict[str, Any]) -> None:
        """
        Initialize the escalation flow.
        
        Args:
            flow_data: Initial data for the flow
        """
        super().initialize(flow_data)
        
        # Initialize escalation data if not present
        if 'escalation' not in flow_data:
            flow_data['escalation'] = {
                'reason': None,
                'destination': self.DESTINATIONS['GENERAL'],
                'specific_person': None,
                'transfer_type': 'warm',  # warm or cold
                'attempt_count': 0,
                'state': self.STATES['INIT']
            }
        
        # Set the initial state if not already set
        if 'state' not in flow_data['escalation']:
            flow_data['escalation']['state'] = self.STATES['INIT']
        
        logger.info("Escalation flow initialized")
    
    def process(self, message: str, metadata: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message through the escalation flow.
        
        Args:
            message: The message to process
            metadata: Additional metadata
            flow_data: Current flow data
            
        Returns:
            Updated flow data with processing results
        """
        super().process(message, metadata, flow_data)
        
        # Get the current state
        current_state = flow_data['escalation']['state']
        logger.info(f"Processing message in escalation flow, state: {current_state}")
        
        # Process based on current state
        if current_state == self.STATES['INIT']:
            return self._process_init(message, flow_data)
        elif current_state == self.STATES['COLLECTING_REASON']:
            return self._process_collecting_reason(message, flow_data)
        elif current_state == self.STATES['PREPARING_TRANSFER']:
            return self._process_preparing_transfer(message, flow_data)
        else:
            # For any other state, move to transferring
            return self._process_transferring(message, flow_data)
    
    def _process_init(self, message: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message in the initial state.
        
        Args:
            message: The message to process
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Analyze the escalation intent
        destination, specific_person = self._analyze_escalation_intent(message)
        
        # Update escalation data
        flow_data['escalation']['destination'] = destination
        if specific_person:
            flow_data['escalation']['specific_person'] = specific_person
        
        # Move to collecting reason if not provided
        if len(message.split()) < 5:
            flow_data['escalation']['state'] = self.STATES['COLLECTING_REASON']
        else:
            # Use message as reason
            flow_data['escalation']['reason'] = message
            flow_data['escalation']['state'] = self.STATES['PREPARING_TRANSFER']
        
        return flow_data
    
    def _process_collecting_reason(self, message: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting the reason for escalation.
        
        Args:
            message: The message to process
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Set the reason
        flow_data['escalation']['reason'] = message
        
        # Move to preparing transfer
        flow_data['escalation']['state'] = self.STATES['PREPARING_TRANSFER']
        
        return flow_data
    
    def _process_preparing_transfer(self, message: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when preparing for transfer.
        
        Args:
            message: The message to process
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Determine transfer type (warm or cold)
        if re.search(r'(cold|direct|just transfer|immediately)', message.lower()):
            flow_data['escalation']['transfer_type'] = 'cold'
        else:
            flow_data['escalation']['transfer_type'] = 'warm'
        
        # Move to transferring
        flow_data['escalation']['state'] = self.STATES['TRANSFERRING']
        
        return self._process_transferring(message, flow_data)
    
    def _process_transferring(self, message: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when transferring the call.
        
        Args:
            message: The message to process
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Increment attempt count
        flow_data['escalation']['attempt_count'] += 1
        
        # Execute the transfer action
        destination = self._get_destination(flow_data['escalation'])
        
        action = {
            'type': 'transfer_call',
            'params': {
                'destination': destination,
                'transfer_type': flow_data['escalation']['transfer_type'],
                'reason': flow_data['escalation']['reason'],
                'attempt': flow_data['escalation']['attempt_count']
            }
        }
        
        result = self._execute_action(action)
        flow_data['transfer_result'] = result
        
        # Check result
        if result.get('success', False):
            flow_data['escalation']['state'] = self.STATES['COMPLETED']
        else:
            flow_data['escalation']['state'] = self.STATES['FAILED']
        
        # End the flow
        self.flow_manager.end_flow(flow_data)
        
        return flow_data
    
    def _analyze_escalation_intent(self, message: str) -> Tuple[str, Optional[str]]:
        """
        Analyze the escalation intent from a message.
        
        Args:
            message: The message to analyze
            
        Returns:
            Tuple of (destination, specific_person or None)
        """
        message = message.lower()
        
        # Check for specific person
        person_pattern = r'(?:speak|talk) (?:to|with) ([\w\s]+)'
        person_match = re.search(person_pattern, message)
        if person_match:
            return self.DESTINATIONS['SPECIFIC'], person_match.group(1).strip()
        
        # Check for support/help
        if re.search(r'(support|help|assist|service|technical)', message):
            return self.DESTINATIONS['SUPPORT'], None
        
        # Check for sales
        if re.search(r'(sales|purchase|buy|price|quote|product)', message):
            return self.DESTINATIONS['SALES'], None
        
        # Check for billing
        if re.search(r'(bill|invoice|payment|account|subscription|renewal)', message):
            return self.DESTINATIONS['BILLING'], None
        
        # Check for emergency
        if re.search(r'(emergency|urgent|critical|immediately|right away)', message):
            return self.DESTINATIONS['EMERGENCY'], None
        
        # Default to general
        return self.DESTINATIONS['GENERAL'], None
    
    def _get_destination(self, escalation_data: Dict[str, Any]) -> str:
        """
        Get the transfer destination.
        
        Args:
            escalation_data: Escalation data
            
        Returns:
            Destination string for the transfer
        """
        # If specific person is requested
        if escalation_data['destination'] == self.DESTINATIONS['SPECIFIC'] and escalation_data['specific_person']:
            return f"person:{escalation_data['specific_person']}"
        
        # Otherwise return the destination department
        return f"department:{escalation_data['destination']}"
    
    def cleanup(self, flow_data: Dict[str, Any]) -> None:
        """
        Clean up the escalation flow.
        
        Args:
            flow_data: Current flow data
        """
        super().cleanup(flow_data)
        
        # Add timestamp
        flow_data['escalation']['last_updated'] = time.time()
        
        logger.info("Escalation flow cleaned up")
    
    def resume(self, flow_data: Dict[str, Any]) -> None:
        """
        Resume the escalation flow.
        
        Args:
            flow_data: Updated flow data
        """
        super().resume(flow_data)
        
        # If we were completed or failed, end the flow
        if flow_data['escalation']['state'] in [self.STATES['COMPLETED'], self.STATES['FAILED']]:
            self.flow_manager.end_flow(flow_data)
        
        logger.info("Escalation flow resumed")