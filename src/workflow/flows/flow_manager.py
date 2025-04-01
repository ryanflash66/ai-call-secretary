"""
Flow manager for conversation flows.
Manages different flows and transitions between them.
"""
import os
import logging
import yaml
import importlib
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Callable

logger = logging.getLogger(__name__)

class FlowManager:
    """
    Manages conversation flows and transitions between them.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the flow manager with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            "../../../config/default.yml"
        )
        
        # Load configuration
        self._load_config()
        
        # Initialize flow registry
        self.flow_registry = {}
        self._register_flows()
        
        # Initialize flow state
        self.current_flow = None
        self.flow_stack = []  # For nested flows
        self.flow_data = {}   # Shared data between flows
        
        logger.info("Flow manager initialized")
    
    def _load_config(self) -> None:
        """
        Load configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load workflow configuration
            self.config = config.get('workflow', {}).get('flows', {})
            
            # Set default flow
            self.default_flow = self.config.get('default_flow', 'general')
            
            logger.info(f"Loaded flow configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
            self.config = {}
            self.default_flow = 'general'
    
    def _register_flows(self) -> None:
        """
        Register available flows from configuration.
        """
        # Register built-in flows
        self.flow_registry['general'] = {
            'name': 'General Flow',
            'description': 'General conversation flow for basic interactions',
            'class': 'GeneralFlow'
        }
        
        self.flow_registry['appointment'] = {
            'name': 'Appointment Flow',
            'description': 'Flow for scheduling and managing appointments',
            'class': 'AppointmentFlow'
        }
        
        self.flow_registry['message'] = {
            'name': 'Message Flow',
            'description': 'Flow for taking and managing messages',
            'class': 'MessageFlow'
        }
        
        self.flow_registry['info'] = {
            'name': 'Information Flow',
            'description': 'Flow for providing information and answering questions',
            'class': 'InformationFlow'
        }
        
        self.flow_registry['escalation'] = {
            'name': 'Escalation Flow',
            'description': 'Flow for escalating calls to a human operator',
            'class': 'EscalationFlow'
        }
        
        # Register custom flows from configuration
        custom_flows = self.config.get('custom_flows', {})
        for flow_id, flow_config in custom_flows.items():
            self.flow_registry[flow_id] = {
                'name': flow_config.get('name', flow_id),
                'description': flow_config.get('description', ''),
                'class': flow_config.get('class', '')
            }
        
        logger.info(f"Registered {len(self.flow_registry)} flows")
    
    def get_flow_instance(self, flow_id: str) -> Optional[Any]:
        """
        Get an instance of a flow by ID.
        
        Args:
            flow_id: ID of the flow to instantiate
            
        Returns:
            Flow instance or None if flow doesn't exist
        """
        if flow_id not in self.flow_registry:
            logger.warning(f"Flow {flow_id} not found in registry")
            return None
        
        try:
            flow_info = self.flow_registry[flow_id]
            class_name = flow_info['class']
            
            # Try to import the flow module
            module_name = f"src.workflow.flows.{flow_id}_flow"
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                # Try with a different pattern if the first fails
                module_name = f"src.workflow.flows.flow_{flow_id}"
                try:
                    module = importlib.import_module(module_name)
                except ImportError:
                    logger.error(f"Could not import flow module for {flow_id}")
                    return None
            
            # Get the flow class
            flow_class = getattr(module, class_name)
            
            # Instantiate the flow
            flow_instance = flow_class(self)
            
            logger.info(f"Created flow instance: {flow_id}")
            return flow_instance
            
        except Exception as e:
            logger.error(f"Error creating flow instance: {str(e)}", exc_info=True)
            return None
    
    def start_flow(self, flow_id: str, input_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Start a new flow.
        
        Args:
            flow_id: ID of the flow to start
            input_data: Initial data for the flow
            
        Returns:
            True if flow started successfully, False otherwise
        """
        # If a flow is already running, push it onto the stack
        if self.current_flow is not None:
            self.flow_stack.append({
                'flow': self.current_flow,
                'data': self.flow_data
            })
        
        # Start the new flow
        flow_instance = self.get_flow_instance(flow_id)
        if flow_instance is None:
            if self.flow_stack:
                # Restore previous flow
                prev_flow = self.flow_stack.pop()
                self.current_flow = prev_flow['flow']
                self.flow_data = prev_flow['data']
            return False
        
        # Initialize the flow data
        self.current_flow = flow_instance
        self.flow_data = input_data or {}
        
        # Call flow initialization
        if hasattr(self.current_flow, 'initialize'):
            self.current_flow.initialize(self.flow_data)
        
        logger.info(f"Started flow: {flow_id}")
        return True
    
    def end_flow(self, output_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        End the current flow and return to the previous flow if any.
        
        Args:
            output_data: Output data from the ending flow
            
        Returns:
            Flow data for the resumed flow, or None if no flow was resumed
        """
        if self.current_flow is None:
            logger.warning("No active flow to end")
            return None
        
        # Call flow cleanup
        if hasattr(self.current_flow, 'cleanup'):
            self.current_flow.cleanup(self.flow_data)
        
        logger.info(f"Ended flow: {self.current_flow.__class__.__name__}")
        
        # Return to previous flow if any
        if self.flow_stack:
            prev_flow = self.flow_stack.pop()
            self.current_flow = prev_flow['flow']
            self.flow_data = prev_flow['data']
            
            # Update flow data with output from ended flow
            if output_data:
                self.flow_data.update(output_data)
            
            # Call flow resume
            if hasattr(self.current_flow, 'resume'):
                self.current_flow.resume(self.flow_data)
            
            logger.info(f"Resumed flow: {self.current_flow.__class__.__name__}")
            return self.flow_data
        else:
            # No previous flow
            self.current_flow = None
            self.flow_data = {}
            return None
    
    def process_message(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Process a message through the current flow.
        
        Args:
            message: The message to process
            metadata: Additional metadata for processing
            
        Returns:
            Flow processing result or None if no flow is active
        """
        if self.current_flow is None:
            # Start default flow if no flow is active
            if not self.start_flow(self.default_flow):
                logger.error("Failed to start default flow")
                return None
        
        # Process the message through the current flow
        if hasattr(self.current_flow, 'process'):
            try:
                result = self.current_flow.process(message, metadata or {}, self.flow_data)
                logger.info(f"Processed message through {self.current_flow.__class__.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                return {
                    'error': str(e),
                    'flow': self.current_flow.__class__.__name__
                }
        else:
            logger.warning(f"Current flow {self.current_flow.__class__.__name__} does not have a process method")
            return None
    
    def get_active_flow(self) -> Tuple[Optional[Any], Dict[str, Any]]:
        """
        Get the currently active flow and its data.
        
        Returns:
            Tuple of (active flow instance, flow data) or (None, {}) if no flow is active
        """
        return self.current_flow, self.flow_data
    
    def get_flow_stack(self) -> List[Dict[str, Any]]:
        """
        Get the current flow stack.
        
        Returns:
            List of flow stack entries
        """
        return self.flow_stack
    
    def clear_flows(self) -> None:
        """
        Clear all flows and reset the flow manager.
        """
        # Clean up current flow if any
        if self.current_flow is not None and hasattr(self.current_flow, 'cleanup'):
            try:
                self.current_flow.cleanup(self.flow_data)
            except Exception as e:
                logger.error(f"Error cleaning up flow: {str(e)}", exc_info=True)
        
        # Reset flow state
        self.current_flow = None
        self.flow_stack = []
        self.flow_data = {}
        
        logger.info("Cleared all flows")
    
    def get_available_flows(self) -> Dict[str, Dict[str, str]]:
        """
        Get a list of available flows.
        
        Returns:
            Dictionary mapping flow IDs to flow information
        """
        return self.flow_registry