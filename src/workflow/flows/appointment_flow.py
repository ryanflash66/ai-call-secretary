"""
Appointment flow for scheduling and managing appointments.
"""
import logging
import re
import time
import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

from src.workflow.flows.base_flow import BaseFlow

logger = logging.getLogger(__name__)

class AppointmentFlow(BaseFlow):
    """
    Flow for handling appointment scheduling and management.
    """
    
    # States for the appointment flow
    STATES = {
        'INIT': 'init',
        'COLLECTING_DATE': 'collecting_date',
        'COLLECTING_TIME': 'collecting_time',
        'COLLECTING_DURATION': 'collecting_duration',
        'COLLECTING_NAME': 'collecting_name',
        'COLLECTING_PURPOSE': 'collecting_purpose',
        'CONFIRMING': 'confirming',
        'COMPLETED': 'completed',
        'CANCELLED': 'cancelled',
        'RESCHEDULING': 'rescheduling'
    }
    
    def initialize(self, flow_data: Dict[str, Any]) -> None:
        """
        Initialize the appointment flow.
        
        Args:
            flow_data: Initial data for the flow
        """
        super().initialize(flow_data)
        
        # Initialize appointment data if not present
        if 'appointment' not in flow_data:
            flow_data['appointment'] = {
                'date': None,
                'time': None,
                'duration': 30,  # Default 30 minutes
                'name': flow_data.get('caller_name', None),
                'phone': flow_data.get('caller_number', None),
                'purpose': None,
                'notes': None,
                'state': self.STATES['INIT']
            }
        
        # Set the initial state if not already set
        if 'state' not in flow_data['appointment']:
            flow_data['appointment']['state'] = self.STATES['INIT']
        
        logger.info("Appointment flow initialized")
    
    def process(self, message: str, metadata: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message through the appointment flow.
        
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
        current_state = flow_data['appointment']['state']
        logger.info(f"Processing message in appointment flow, state: {current_state}")
        
        # Process based on current state
        if current_state == self.STATES['INIT']:
            return self._process_init(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_DATE']:
            return self._process_collecting_date(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_TIME']:
            return self._process_collecting_time(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_DURATION']:
            return self._process_collecting_duration(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_NAME']:
            return self._process_collecting_name(message, entities, flow_data)
        elif current_state == self.STATES['COLLECTING_PURPOSE']:
            return self._process_collecting_purpose(message, entities, flow_data)
        elif current_state == self.STATES['CONFIRMING']:
            return self._process_confirming(message, entities, flow_data)
        elif current_state == self.STATES['RESCHEDULING']:
            return self._process_rescheduling(message, entities, flow_data)
        else:
            # Unknown state, reset to initial
            flow_data['appointment']['state'] = self.STATES['INIT']
            logger.warning(f"Unknown appointment state: {current_state}, resetting to INIT")
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
        # Look for appointment intent
        intent = self._analyze_appointment_intent(message)
        
        if intent == 'schedule':
            # Extract date if present
            if 'dates' in entities and entities['dates']:
                flow_data['appointment']['date'] = entities['dates'][0]
                flow_data['appointment']['state'] = self.STATES['COLLECTING_TIME']
                return flow_data
            
            # Extract time if present
            if 'times' in entities and entities['times']:
                flow_data['appointment']['time'] = entities['times'][0]
                if flow_data['appointment']['date'] is None:
                    flow_data['appointment']['state'] = self.STATES['COLLECTING_DATE']
                else:
                    flow_data['appointment']['state'] = self.STATES['COLLECTING_DURATION']
                return flow_data
            
            # No date or time, start collecting
            flow_data['appointment']['state'] = self.STATES['COLLECTING_DATE']
            return flow_data
            
        elif intent == 'cancel':
            # Handle cancellation
            # For now, just end the flow
            flow_data['appointment']['state'] = self.STATES['CANCELLED']
            self.flow_manager.end_flow(flow_data)
            return flow_data
            
        elif intent == 'reschedule':
            # Handle rescheduling
            flow_data['appointment']['state'] = self.STATES['RESCHEDULING']
            return flow_data
            
        else:
            # Default to scheduling
            flow_data['appointment']['state'] = self.STATES['COLLECTING_DATE']
            return flow_data
    
    def _process_collecting_date(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting date.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Check for date in entities
        if 'dates' in entities and entities['dates']:
            date_str = entities['dates'][0]
            # In a real implementation, validate and normalize the date
            flow_data['appointment']['date'] = date_str
            
            # If we have the time, move to duration
            if flow_data['appointment']['time'] is not None:
                flow_data['appointment']['state'] = self.STATES['COLLECTING_DURATION']
            else:
                flow_data['appointment']['state'] = self.STATES['COLLECTING_TIME']
                
            return flow_data
        
        # No date found, stay in same state
        return flow_data
    
    def _process_collecting_time(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting time.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Check for time in entities
        if 'times' in entities and entities['times']:
            time_str = entities['times'][0]
            # In a real implementation, validate and normalize the time
            flow_data['appointment']['time'] = time_str
            flow_data['appointment']['state'] = self.STATES['COLLECTING_DURATION']
            return flow_data
        
        # No time found, stay in same state
        return flow_data
    
    def _process_collecting_duration(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting duration.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Try to extract duration
        duration = self._extract_duration(message)
        if duration:
            flow_data['appointment']['duration'] = duration
        
        # Move to next state regardless (use default duration if not specified)
        if flow_data['appointment']['name'] is None:
            flow_data['appointment']['state'] = self.STATES['COLLECTING_NAME']
        else:
            flow_data['appointment']['state'] = self.STATES['COLLECTING_PURPOSE']
        
        return flow_data
    
    def _process_collecting_name(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting name.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Check for name in entities
        if 'names' in entities and entities['names']:
            flow_data['appointment']['name'] = entities['names'][0]
        else:
            # Use message as name if no entity detected
            flow_data['appointment']['name'] = message.strip()
        
        # Move to purpose
        flow_data['appointment']['state'] = self.STATES['COLLECTING_PURPOSE']
        return flow_data
    
    def _process_collecting_purpose(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when collecting purpose.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Use message as purpose
        flow_data['appointment']['purpose'] = message.strip()
        
        # Move to confirmation
        flow_data['appointment']['state'] = self.STATES['CONFIRMING']
        return flow_data
    
    def _process_confirming(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when confirming appointment.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Check for confirmation or denial
        if self._is_confirmation(message):
            # Schedule the appointment via action
            action = {
                'type': 'schedule_appointment',
                'params': {
                    'date': flow_data['appointment']['date'],
                    'time': flow_data['appointment']['time'],
                    'duration': flow_data['appointment']['duration'],
                    'name': flow_data['appointment']['name'],
                    'phone': flow_data['appointment']['phone'],
                    'purpose': flow_data['appointment']['purpose']
                }
            }
            
            result = self._execute_action(action)
            flow_data['appointment_result'] = result
            
            # Mark as completed
            flow_data['appointment']['state'] = self.STATES['COMPLETED']
            
            # End the flow
            self.flow_manager.end_flow(flow_data)
            
        elif self._is_denial(message):
            # Cancel the appointment process
            flow_data['appointment']['state'] = self.STATES['CANCELLED']
            self.flow_manager.end_flow(flow_data)
            
        # Otherwise stay in confirming state
        return flow_data
    
    def _process_rescheduling(self, message: str, entities: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process message when rescheduling.
        
        Args:
            message: The message to process
            entities: Extracted entities
            flow_data: Current flow data
            
        Returns:
            Updated flow data
        """
        # Check for date and time
        if 'dates' in entities and entities['dates']:
            flow_data['appointment']['date'] = entities['dates'][0]
        
        if 'times' in entities and entities['times']:
            flow_data['appointment']['time'] = entities['times'][0]
        
        # If we have both date and time, move to confirmation
        if flow_data['appointment']['date'] and flow_data['appointment']['time']:
            flow_data['appointment']['state'] = self.STATES['CONFIRMING']
            return flow_data
        
        # If we only have date, collect time
        if flow_data['appointment']['date'] and not flow_data['appointment']['time']:
            flow_data['appointment']['state'] = self.STATES['COLLECTING_TIME']
            return flow_data
        
        # If we only have time, collect date
        if not flow_data['appointment']['date'] and flow_data['appointment']['time']:
            flow_data['appointment']['state'] = self.STATES['COLLECTING_DATE']
            return flow_data
        
        # No date or time, collect date
        flow_data['appointment']['state'] = self.STATES['COLLECTING_DATE']
        return flow_data
    
    def _analyze_appointment_intent(self, message: str) -> str:
        """
        Analyze the appointment-related intent.
        
        Args:
            message: The message to analyze
            
        Returns:
            Intent: 'schedule', 'cancel', 'reschedule', or 'inquire'
        """
        message = message.lower()
        
        # Check for cancellation
        if re.search(r'(cancel|remove|delete|forget|never mind)', message):
            return 'cancel'
        
        # Check for rescheduling
        if re.search(r'(reschedule|change|move|different time|different day)', message):
            return 'reschedule'
        
        # Check for inquiry
        if re.search(r'(check|find out|when is|do I have|confirm)', message):
            return 'inquire'
        
        # Default to scheduling
        return 'schedule'
    
    def _extract_duration(self, message: str) -> Optional[int]:
        """
        Extract appointment duration from message.
        
        Args:
            message: The message to analyze
            
        Returns:
            Duration in minutes or None if not found
        """
        message = message.lower()
        
        # Look for duration patterns
        patterns = [
            r'(\d+)\s*(?:minute|min|minutes|mins)',
            r'(\d+)\s*(?:hour|hours|hr|hrs)',
            r'half\s*(?:an|hour|a)',
            r'quarter\s*(?:hour|of an hour)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                if 'minute' in pattern or 'min' in pattern:
                    return int(match.group(1))
                elif 'hour' in pattern or 'hr' in pattern:
                    return int(match.group(1)) * 60
                elif 'half' in pattern:
                    return 30
                elif 'quarter' in pattern:
                    return 15
        
        return None
    
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
            r'\b(book it|schedule it|make it|do it|proceed|go ahead)\b'
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
        Clean up the appointment flow.
        
        Args:
            flow_data: Current flow data
        """
        super().cleanup(flow_data)
        
        # Add timestamp
        flow_data['appointment']['last_updated'] = time.time()
        
        logger.info("Appointment flow cleaned up")
    
    def resume(self, flow_data: Dict[str, Any]) -> None:
        """
        Resume the appointment flow.
        
        Args:
            flow_data: Updated flow data
        """
        super().resume(flow_data)
        
        # If we were completed or cancelled, end the flow
        if flow_data['appointment']['state'] in [self.STATES['COMPLETED'], self.STATES['CANCELLED']]:
            self.flow_manager.end_flow(flow_data)
        
        logger.info("Appointment flow resumed")