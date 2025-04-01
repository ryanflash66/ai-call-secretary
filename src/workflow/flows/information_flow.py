"""
Information flow for providing information and answering questions.
"""
import logging
import re
import time
from typing import Dict, List, Optional, Any, Union, Tuple

from src.workflow.flows.base_flow import BaseFlow

logger = logging.getLogger(__name__)

class InformationFlow(BaseFlow):
    """
    Flow for providing information and answering questions.
    """
    
    # Categories of information
    INFO_CATEGORIES = {
        'HOURS': 'hours',
        'LOCATION': 'location',
        'SERVICES': 'services',
        'PRICING': 'pricing',
        'CONTACT': 'contact',
        'STAFF': 'staff',
        'POLICIES': 'policies',
        'GENERAL': 'general'
    }
    
    def initialize(self, flow_data: Dict[str, Any]) -> None:
        """
        Initialize the information flow.
        
        Args:
            flow_data: Initial data for the flow
        """
        super().initialize(flow_data)
        
        # Initialize information data if not present
        if 'info_data' not in flow_data:
            flow_data['info_data'] = {
                'query': None,
                'category': self.INFO_CATEGORIES['GENERAL'],
                'resolved': False,
                'followup_queries': []
            }
        
        logger.info("Information flow initialized")
    
    def process(self, message: str, metadata: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message through the information flow.
        
        Args:
            message: The message to process
            metadata: Additional metadata
            flow_data: Current flow data
            
        Returns:
            Updated flow data with processing results
        """
        super().process(message, metadata, flow_data)
        
        # Track the query
        if flow_data['info_data']['query'] is None:
            flow_data['info_data']['query'] = message
        else:
            flow_data['info_data']['followup_queries'].append(message)
        
        # Determine the information category
        category = self._determine_info_category(message)
        if category != self.INFO_CATEGORIES['GENERAL']:
            flow_data['info_data']['category'] = category
        
        # Look up the information
        info_result = self._lookup_information(message, flow_data['info_data']['category'])
        
        # Store the result
        if 'info_results' not in flow_data:
            flow_data['info_results'] = []
        
        flow_data['info_results'].append({
            'query': message,
            'category': flow_data['info_data']['category'],
            'result': info_result,
            'timestamp': time.time()
        })
        
        # Check if the query is resolved
        if self._is_resolved(message, info_result):
            flow_data['info_data']['resolved'] = True
            
            # If resolved and no indication of more questions, end the flow
            if not self._has_followup_questions(message):
                self.flow_manager.end_flow(flow_data)
        
        return flow_data
    
    def _determine_info_category(self, message: str) -> str:
        """
        Determine the category of information being requested.
        
        Args:
            message: The message to analyze
            
        Returns:
            Category of information
        """
        message = message.lower()
        
        # Check for hours
        if re.search(r'(hours|open|close|time|schedule|when|day)', message):
            return self.INFO_CATEGORIES['HOURS']
        
        # Check for location
        if re.search(r'(location|address|where|place|direction|map|find you)', message):
            return self.INFO_CATEGORIES['LOCATION']
        
        # Check for services
        if re.search(r'(service|offer|provide|do you|can you|what.*do|available)', message):
            return self.INFO_CATEGORIES['SERVICES']
        
        # Check for pricing
        if re.search(r'(price|cost|fee|rate|charge|how much|payment)', message):
            return self.INFO_CATEGORIES['PRICING']
        
        # Check for contact
        if re.search(r'(contact|email|phone|call|number|reach)', message):
            return self.INFO_CATEGORIES['CONTACT']
        
        # Check for staff
        if re.search(r'(staff|employee|person|people|team|expert|specialist|doctor|provider)', message):
            return self.INFO_CATEGORIES['STAFF']
        
        # Check for policies
        if re.search(r'(policy|rule|guideline|requirement|cancel|reschedule|insurance)', message):
            return self.INFO_CATEGORIES['POLICIES']
        
        # Default to general
        return self.INFO_CATEGORIES['GENERAL']
    
    def _lookup_information(self, query: str, category: str) -> Dict[str, Any]:
        """
        Look up information based on the query and category.
        
        Args:
            query: The query to look up
            category: The category of information
            
        Returns:
            Information lookup result
        """
        # Create an action to look up information
        action = {
            'type': 'lookup_info',
            'params': {
                'query': query,
                'category': category
            }
        }
        
        # Execute the action
        return self._execute_action(action)
    
    def _is_resolved(self, message: str, result: Dict[str, Any]) -> bool:
        """
        Determine if a query has been resolved.
        
        Args:
            message: The original query
            result: The result of the information lookup
            
        Returns:
            True if the query is resolved, False otherwise
        """
        # Check if result indicates success
        if not result.get('success', False):
            return False
        
        # Check if detailed info is provided
        if 'details' not in result or 'info' not in result['details']:
            return False
        
        # If the info is "No specific information found", it's not resolved
        if result['details']['info'] == "No specific information found for this query.":
            return False
        
        return True
    
    def _has_followup_questions(self, message: str) -> bool:
        """
        Determine if a message indicates more questions are coming.
        
        Args:
            message: The message to analyze
            
        Returns:
            True if followup questions are indicated, False otherwise
        """
        message = message.lower()
        
        # Check for indications of more questions
        followup_patterns = [
            r'(also|another question|one more thing|follow up|followup|additionally|next|more)',
            r'(what about|how about|tell me about)',
            r'(and|plus)'
        ]
        
        for pattern in followup_patterns:
            if re.search(pattern, message):
                return True
        
        return False
    
    def cleanup(self, flow_data: Dict[str, Any]) -> None:
        """
        Clean up the information flow.
        
        Args:
            flow_data: Current flow data
        """
        super().cleanup(flow_data)
        
        # Add timestamp
        flow_data['info_data']['last_updated'] = time.time()
        
        logger.info("Information flow cleaned up")
    
    def resume(self, flow_data: Dict[str, Any]) -> None:
        """
        Resume the information flow.
        
        Args:
            flow_data: Updated flow data
        """
        super().resume(flow_data)
        
        # Reset resolved flag to allow new queries
        flow_data['info_data']['resolved'] = False
        
        logger.info("Information flow resumed")