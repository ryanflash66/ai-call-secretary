"""
Workflow actions for automation.
Defines actions that can be performed based on conversation analysis.
"""
import os
import logging
import json
import re
import time
import yaml
import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

logger = logging.getLogger(__name__)

class ActionHandler:
    """
    Handles extracting and executing actions from LLM responses.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the action handler with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../config/default.yml"
        )
        
        # Load configuration
        self._load_config()
        
        # Initialize action registry
        self.action_registry = {
            "schedule_appointment": self._action_schedule_appointment,
            "cancel_appointment": self._action_cancel_appointment,
            "take_message": self._action_take_message,
            "transfer_call": self._action_transfer_call,
            "lookup_info": self._action_lookup_info,
            "save_contact": self._action_save_contact,
            "set_reminder": self._action_set_reminder,
            "send_email": self._action_send_email,
            "send_sms": self._action_send_sms
        }
        
        logger.info("Action handler initialized")
    
    def _load_config(self) -> None:
        """
        Load configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Any specific configuration can be loaded here
            self.config = config.get('workflow', {}).get('actions', {})
            
            logger.info(f"Loaded action configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
            self.config = {}
    
    def extract_actions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract actions from text.
        
        Args:
            text: Text to extract actions from (typically LLM response)
            
        Returns:
            List of action dictionaries with 'type' and 'params' keys
        """
        actions = []
        
        # Look for patterns like [ACTION:action_type{param1:value1,param2:value2}]
        action_pattern = r'\[ACTION:(\w+)\{([^}]*)\}\]'
        matches = re.finditer(action_pattern, text)
        
        for match in matches:
            action_type = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
            params = {}
            for param in params_str.split(','):
                if ':' in param:
                    key, value = param.split(':', 1)
                    params[key.strip()] = value.strip()
            
            actions.append({
                'type': action_type,
                'params': params
            })
        
        # Also look for JSON-like action blocks
        json_pattern = r'```action\s*\n(.*?)\n```'
        matches = re.finditer(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                action_json = json.loads(match.group(1))
                if isinstance(action_json, dict) and 'type' in action_json:
                    actions.append(action_json)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse action JSON: {match.group(1)}")
        
        logger.info(f"Extracted {len(actions)} actions from text")
        return actions
    
    def execute_action(self, action: Dict[str, Any]) -> Any:
        """
        Execute an action.
        
        Args:
            action: Action dictionary with 'type' and 'params' keys
            
        Returns:
            Result of the action execution
        """
        action_type = action.get('type')
        params = action.get('params', {})
        
        if action_type not in self.action_registry:
            logger.warning(f"Unknown action type: {action_type}")
            return {"error": f"Unknown action type: {action_type}"}
        
        try:
            logger.info(f"Executing action: {action_type}")
            result = self.action_registry[action_type](params)
            logger.info(f"Action {action_type} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def _action_schedule_appointment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule an appointment.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        required_params = ['date', 'time', 'duration']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        
        # In a real implementation, this would interface with a calendar system
        # For now, we'll just simulate the appointment creation
        appointment_id = f"apt_{int(time.time())}"
        
        # Format date and time
        try:
            date_obj = datetime.datetime.strptime(params['date'], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
        except ValueError:
            formatted_date = params['date']  # Use as-is if not in expected format
        
        appointment = {
            'id': appointment_id,
            'date': params['date'],
            'formatted_date': formatted_date,
            'time': params['time'],
            'duration': params['duration'],
            'name': params.get('name', 'Unknown'),
            'phone': params.get('phone', 'Unknown'),
            'purpose': params.get('purpose', ''),
            'notes': params.get('notes', ''),
            'status': 'scheduled',
            'created_at': time.time()
        }
        
        # In a real implementation, save to database
        logger.info(f"Scheduled appointment: {appointment_id}")
        
        return {
            'success': True,
            'appointment_id': appointment_id,
            'details': appointment,
            'message': f"Appointment scheduled for {formatted_date} at {params['time']} for {params['duration']} minutes."
        }
    
    def _action_cancel_appointment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancel an appointment.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        if 'appointment_id' not in params and 'date' not in params:
            raise ValueError("Missing required parameter: either appointment_id or date is required")
        
        # In a real implementation, this would interface with a calendar system
        # For now, we'll just simulate the appointment cancellation
        appointment_id = params.get('appointment_id', f"apt_{params.get('date')}")
        
        # In a real implementation, check if appointment exists
        appointment_exists = True  # Simulated
        
        if not appointment_exists:
            return {
                'success': False,
                'message': f"Appointment {appointment_id} not found."
            }
        
        logger.info(f"Cancelled appointment: {appointment_id}")
        
        return {
            'success': True,
            'appointment_id': appointment_id,
            'message': f"Appointment {appointment_id} has been cancelled."
        }
    
    def _action_take_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take a message.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        required_params = ['message']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        
        # In a real implementation, this would save to a database or send notifications
        message_id = f"msg_{int(time.time())}"
        
        message = {
            'id': message_id,
            'caller_name': params.get('caller_name', 'Unknown'),
            'caller_number': params.get('caller_number', 'Unknown'),
            'message': params['message'],
            'urgency': params.get('urgency', 'normal'),
            'callback_requested': params.get('callback_requested', False),
            'timestamp': time.time()
        }
        
        # In a real implementation, save to database or send notification
        logger.info(f"Took message: {message_id}")
        
        return {
            'success': True,
            'message_id': message_id,
            'details': message,
            'message': f"Message recorded. ID: {message_id}"
        }
    
    def _action_transfer_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transfer a call.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        if 'destination' not in params:
            raise ValueError("Missing required parameter: destination")
        
        # In a real implementation, this would interface with the telephony system
        destination = params['destination']
        transfer_type = params.get('transfer_type', 'warm')  # warm or cold
        
        # Simulate the transfer
        logger.info(f"Transferring call to {destination} ({transfer_type} transfer)")
        
        return {
            'success': True,
            'destination': destination,
            'transfer_type': transfer_type,
            'message': f"Call transferred to {destination}."
        }
    
    def _action_lookup_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Look up information.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        if 'query' not in params:
            raise ValueError("Missing required parameter: query")
        
        # In a real implementation, this would search a knowledge base or CRM
        query = params['query']
        category = params.get('category', 'general')
        
        # Simulate information lookup
        result = {
            'query': query,
            'category': category,
            'timestamp': time.time()
        }
        
        # Dummy responses based on categories
        if category == 'hours':
            result['info'] = "Monday-Friday: 9 AM - 5 PM, Saturday: 10 AM - 2 PM, Sunday: Closed"
        elif category == 'location':
            result['info'] = "123 Main Street, Anytown, USA 12345"
        elif category == 'contact':
            result['info'] = "Phone: (555) 123-4567, Email: info@example.com"
        else:
            result['info'] = "No specific information found for this query."
        
        logger.info(f"Looked up information: {query} ({category})")
        
        return {
            'success': True,
            'details': result,
            'message': f"Information lookup for '{query}' complete."
        }
    
    def _action_save_contact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save contact information.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        required_params = ['name']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        
        # In a real implementation, this would save to a CRM or contacts database
        contact_id = f"contact_{int(time.time())}"
        
        contact = {
            'id': contact_id,
            'name': params['name'],
            'phone': params.get('phone', ''),
            'email': params.get('email', ''),
            'company': params.get('company', ''),
            'notes': params.get('notes', ''),
            'created_at': time.time()
        }
        
        # In a real implementation, save to database
        logger.info(f"Saved contact: {contact_id} ({params['name']})")
        
        return {
            'success': True,
            'contact_id': contact_id,
            'details': contact,
            'message': f"Contact information for {params['name']} saved."
        }
    
    def _action_set_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set a reminder.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        required_params = ['date', 'time', 'description']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        
        # In a real implementation, this would interface with a calendar or task system
        reminder_id = f"reminder_{int(time.time())}"
        
        reminder = {
            'id': reminder_id,
            'date': params['date'],
            'time': params['time'],
            'description': params['description'],
            'for_user': params.get('for_user', 'staff'),
            'priority': params.get('priority', 'normal'),
            'created_at': time.time()
        }
        
        # In a real implementation, save to database or calendar
        logger.info(f"Set reminder: {reminder_id}")
        
        return {
            'success': True,
            'reminder_id': reminder_id,
            'details': reminder,
            'message': f"Reminder set for {params['date']} at {params['time']}."
        }
    
    def _action_send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        required_params = ['to', 'subject', 'body']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        
        # In a real implementation, this would use an email service
        email_id = f"email_{int(time.time())}"
        
        email = {
            'id': email_id,
            'to': params['to'],
            'subject': params['subject'],
            'body': params['body'],
            'cc': params.get('cc', ''),
            'bcc': params.get('bcc', ''),
            'from': params.get('from', 'system@example.com'),
            'timestamp': time.time()
        }
        
        # In a real implementation, send via email API
        logger.info(f"Sent email: {email_id} to {params['to']}")
        
        return {
            'success': True,
            'email_id': email_id,
            'details': email,
            'message': f"Email sent to {params['to']} with subject '{params['subject']}'."
        }
    
    def _action_send_sms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an SMS.
        
        Args:
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        required_params = ['to', 'message']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        
        # In a real implementation, this would use an SMS service
        sms_id = f"sms_{int(time.time())}"
        
        sms = {
            'id': sms_id,
            'to': params['to'],
            'message': params['message'],
            'from': params.get('from', 'system'),
            'timestamp': time.time()
        }
        
        # In a real implementation, send via SMS API
        logger.info(f"Sent SMS: {sms_id} to {params['to']}")
        
        return {
            'success': True,
            'sms_id': sms_id,
            'details': sms,
            'message': f"SMS sent to {params['to']}."
        }


class ActionExecutor:
    """
    Responsible for executing action sequences based on conversation analysis.
    """
    
    def __init__(self, handler: Optional[ActionHandler] = None):
        """
        Initialize the action executor.
        
        Args:
            handler: Action handler instance
        """
        self.handler = handler or ActionHandler()
        self.executed_actions = []
        
        logger.info("Action executor initialized")
    
    def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a sequence of actions.
        
        Args:
            actions: List of action dictionaries
            
        Returns:
            List of action results
        """
        results = []
        
        for action in actions:
            result = self.handler.execute_action(action)
            results.append(result)
            
            # Record the executed action and its result
            self.executed_actions.append({
                'action': action,
                'result': result,
                'timestamp': time.time()
            })
        
        return results
    
    def get_executed_actions(self) -> List[Dict[str, Any]]:
        """
        Get the list of executed actions.
        
        Returns:
            List of executed actions with results
        """
        return self.executed_actions
    
    def clear_executed_actions(self) -> None:
        """
        Clear the list of executed actions.
        """
        self.executed_actions = []
        logger.info("Cleared executed actions history")


# Action extraction utility functions

def extract_entities_from_text(text: str) -> Dict[str, Any]:
    """
    Extract entities from text using pattern matching.
    
    Args:
        text: Text to extract entities from
        
    Returns:
        Dictionary of extracted entities
    """
    entities = {}
    
    # Extract phone numbers
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
    phone_matches = re.finditer(phone_pattern, text)
    phones = [match.group(0) for match in phone_matches]
    if phones:
        entities['phone_numbers'] = phones
    
    # Extract email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_matches = re.finditer(email_pattern, text)
    emails = [match.group(0) for match in email_matches]
    if emails:
        entities['emails'] = emails
    
    # Extract dates
    date_patterns = [
        r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',  # MM/DD/YYYY or DD/MM/YYYY
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})\b',  # Month DD, YYYY
        r'\b(\d{1,2})(?:st|nd|rd|th)? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,? (\d{4})\b',  # DD Month, YYYY
    ]
    
    dates = []
    for pattern in date_patterns:
        date_matches = re.finditer(pattern, text, re.IGNORECASE)
        dates.extend([match.group(0) for match in date_matches])
    
    if dates:
        entities['dates'] = dates
    
    # Extract times
    time_pattern = r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(am|pm|AM|PM)?\b'
    time_matches = re.finditer(time_pattern, text)
    times = [match.group(0) for match in time_matches]
    if times:
        entities['times'] = times
    
    # Extract names (this is a simple heuristic and would be much more advanced in a real system)
    name_pattern = r'(?:(?:my|his|her|their) name is |I am |I\'m |This is )([A-Z][a-z]+ [A-Z][a-z]+)'
    name_matches = re.finditer(name_pattern, text)
    names = [match.group(1) for match in name_matches]
    if names:
        entities['names'] = names
    
    return entities