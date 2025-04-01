"""
Call routing rules and logic.
Determines how incoming calls are handled based on caller ID, time of day, etc.
"""
import logging
import re
import time
import yaml
import os
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class CallRouter:
    """
    Routes incoming calls based on rules and configuration.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the call router with configuration.
        
        Args:
            config_path: Path to the routing configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../config/default.yml"
        )
        self.routing_rules = []
        self.blacklist = []
        self.whitelist = []
        self.business_hours = {
            "start": dt_time(9, 0),  # 9:00 AM
            "end": dt_time(17, 0)    # 5:00 PM
        }
        
        self._load_config()
        logger.info("Call router initialized")
    
    def _load_config(self) -> None:
        """
        Load routing configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config or 'telephony' not in config:
                logger.warning(f"Invalid configuration in {self.config_path}")
                return
            
            telephony_config = config['telephony']
            
            # Load routing rules
            if 'routing_rules' in telephony_config:
                self.routing_rules = telephony_config['routing_rules']
            
            # Load blacklist/whitelist
            if 'blacklist' in telephony_config:
                self.blacklist = telephony_config['blacklist']
            
            if 'whitelist' in telephony_config:
                self.whitelist = telephony_config['whitelist']
            
            # Load business hours
            if 'business_hours' in telephony_config:
                hours = telephony_config['business_hours']
                if 'start' in hours:
                    start_parts = hours['start'].split(':')
                    self.business_hours['start'] = dt_time(int(start_parts[0]), int(start_parts[1]))
                
                if 'end' in hours:
                    end_parts = hours['end'].split(':')
                    self.business_hours['end'] = dt_time(int(end_parts[0]), int(end_parts[1]))
            
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
    
    def route_call(self, call_metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Route an incoming call based on configured rules.
        
        Args:
            call_metadata: Dictionary containing call information
            
        Returns:
            Tuple of (routing_action, action_params)
        """
        caller_number = call_metadata.get('caller_number', '')
        caller_name = call_metadata.get('caller_name', 'Unknown')
        timestamp = call_metadata.get('timestamp', time.time())
        
        # Check blacklist
        if self._is_blacklisted(caller_number):
            logger.info(f"Blacklisted caller: {caller_number}")
            return "reject", {"reason": "blacklisted"}
        
        # Check whitelist (priority handling)
        if self._is_whitelisted(caller_number):
            logger.info(f"Whitelisted caller: {caller_number} ({caller_name})")
            return "priority", {"level": "high"}
        
        # Check business hours
        if not self._is_business_hours(timestamp):
            logger.info(f"Call outside business hours from {caller_number}")
            return "voicemail", {"greeting": "outside_hours"}
        
        # Apply specific routing rules
        for rule in self.routing_rules:
            if self._rule_matches(rule, call_metadata):
                action = rule.get('action', 'default')
                params = rule.get('params', {})
                logger.info(f"Applied rule {rule.get('name', 'unnamed')} to call from {caller_number}")
                return action, params
        
        # Default handling
        logger.info(f"Default handling for call from {caller_number} ({caller_name})")
        return "default", {"ai_model": "default"}
    
    def _is_blacklisted(self, number: str) -> bool:
        """
        Check if a number is blacklisted.
        
        Args:
            number: The caller's phone number
            
        Returns:
            True if blacklisted, False otherwise
        """
        for pattern in self.blacklist:
            if re.search(pattern, number):
                return True
        return False
    
    def _is_whitelisted(self, number: str) -> bool:
        """
        Check if a number is whitelisted.
        
        Args:
            number: The caller's phone number
            
        Returns:
            True if whitelisted, False otherwise
        """
        for pattern in self.whitelist:
            if re.search(pattern, number):
                return True
        return False
    
    def _is_business_hours(self, timestamp: float) -> bool:
        """
        Check if the call is during business hours.
        
        Args:
            timestamp: The call timestamp as a Unix timestamp
            
        Returns:
            True if during business hours, False otherwise
        """
        call_time = datetime.fromtimestamp(timestamp).time()
        
        # If business hours span across midnight
        if self.business_hours['start'] > self.business_hours['end']:
            return call_time >= self.business_hours['start'] or call_time < self.business_hours['end']
        else:
            return call_time >= self.business_hours['start'] and call_time < self.business_hours['end']
    
    def _rule_matches(self, rule: Dict[str, Any], call_metadata: Dict[str, Any]) -> bool:
        """
        Check if a routing rule matches the call metadata.
        
        Args:
            rule: The routing rule to check
            call_metadata: The call metadata
            
        Returns:
            True if the rule matches, False otherwise
        """
        # Number pattern matching
        if 'number_pattern' in rule:
            caller_number = call_metadata.get('caller_number', '')
            if not re.search(rule['number_pattern'], caller_number):
                return False
        
        # Name pattern matching
        if 'name_pattern' in rule:
            caller_name = call_metadata.get('caller_name', '')
            if not re.search(rule['name_pattern'], caller_name):
                return False
        
        # Time range matching
        if 'time_range' in rule:
            timestamp = call_metadata.get('timestamp', time.time())
            call_dt = datetime.fromtimestamp(timestamp)
            
            time_range = rule['time_range']
            if 'days' in time_range:
                if call_dt.strftime('%A').lower() not in [d.lower() for d in time_range['days']]:
                    return False
            
            if 'start_time' in time_range and 'end_time' in time_range:
                start_parts = time_range['start_time'].split(':')
                end_parts = time_range['end_time'].split(':')
                
                start_time = dt_time(int(start_parts[0]), int(start_parts[1]))
                end_time = dt_time(int(end_parts[0]), int(end_parts[1]))
                
                call_time = call_dt.time()
                
                # If time range spans across midnight
                if start_time > end_time:
                    if call_time < start_time and call_time >= end_time:
                        return False
                else:
                    if call_time < start_time or call_time >= end_time:
                        return False
        
        # Custom condition matching
        if 'condition' in rule:
            condition = rule['condition']
            if condition == 'repeat_caller':
                # This would check if this caller has called before
                # In a real implementation, this would check a database
                pass
            elif condition == 'high_priority':
                # This would check if this caller is flagged as high priority
                # In a real implementation, this would check a database or CRM
                pass
        
        # If we've passed all checks, the rule matches
        return True