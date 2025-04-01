"""
Tests for workflow components and flows.
"""
import os
import pytest
import time
from unittest.mock import patch, MagicMock

from src.workflow.actions import ActionHandler, ActionExecutor, extract_entities_from_text
from src.workflow.flows.flow_manager import FlowManager
from src.workflow.flows.base_flow import BaseFlow
from src.workflow.flows import (
    GeneralFlow,
    AppointmentFlow,
    MessageFlow,
    InformationFlow,
    EscalationFlow
)

# Test data
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/default.yml')


class TestWorkflowActions:
    """Tests for action handling."""
    
    def test_extract_entities(self):
        """Test entity extraction."""
        # Test extracting phone numbers
        text = "My phone number is 555-123-4567 and my other number is (123) 456-7890."
        entities = extract_entities_from_text(text)
        assert 'phone_numbers' in entities
        assert len(entities['phone_numbers']) == 2
        
        # Test extracting email addresses
        text = "Contact me at john.doe@example.com or jane@test.org."
        entities = extract_entities_from_text(text)
        assert 'emails' in entities
        assert len(entities['emails']) == 2
        assert "john.doe@example.com" in entities['emails']
        
        # Test extracting dates
        text = "The meeting is on 2023-12-15 and the appointment is on Jan 20, 2024."
        entities = extract_entities_from_text(text)
        assert 'dates' in entities
        assert len(entities['dates']) == 2
        
        # Test extracting times
        text = "Let's meet at 10:30 AM or 3:45 PM."
        entities = extract_entities_from_text(text)
        assert 'times' in entities
        assert len(entities['times']) == 2
    
    def test_action_extraction(self):
        """Test extracting actions from text."""
        handler = ActionHandler(CONFIG_PATH)
        
        # Test bracket notation
        text = "I'll schedule that for you. [ACTION:schedule_appointment{date: 2023-12-15, time: 14:30, duration: 60}]"
        actions = handler.extract_actions(text)
        assert len(actions) == 1
        assert actions[0]['type'] == 'schedule_appointment'
        assert actions[0]['params']['date'] == '2023-12-15'
        assert actions[0]['params']['time'] == '14:30'
        
        # Test JSON notation
        text = """I'll take that message.
```action
{
  "type": "take_message",
  "params": {
    "message": "Call back regarding the proposal",
    "caller_name": "John Smith",
    "urgency": "high"
  }
}
```
"""
        actions = handler.extract_actions(text)
        assert len(actions) == 1
        assert actions[0]['type'] == 'take_message'
        assert actions[0]['params']['message'] == 'Call back regarding the proposal'
        assert actions[0]['params']['caller_name'] == 'John Smith'
    
    @patch('src.workflow.actions.ActionHandler._action_schedule_appointment')
    def test_execute_action(self, mock_schedule):
        """Test executing an action."""
        mock_schedule.return_value = {
            'success': True,
            'appointment_id': 'test_id',
            'message': 'Appointment scheduled successfully'
        }
        
        handler = ActionHandler(CONFIG_PATH)
        action = {
            'type': 'schedule_appointment',
            'params': {
                'date': '2023-12-15',
                'time': '14:30',
                'duration': 60
            }
        }
        
        result = handler.execute_action(action)
        assert result['success'] is True
        assert 'appointment_id' in result
        mock_schedule.assert_called_once_with(action['params'])
    
    def test_action_executor(self):
        """Test the action executor."""
        handler = MagicMock()
        handler.execute_action.return_value = {'success': True}
        
        executor = ActionExecutor(handler)
        actions = [
            {'type': 'action1', 'params': {}},
            {'type': 'action2', 'params': {}}
        ]
        
        results = executor.execute_actions(actions)
        assert len(results) == 2
        assert len(executor.get_executed_actions()) == 2
        
        executor.clear_executed_actions()
        assert len(executor.get_executed_actions()) == 0


class TestFlowManager:
    """Tests for flow management."""
    
    def test_flow_initialization(self):
        """Test flow manager initialization."""
        manager = FlowManager(CONFIG_PATH)
        assert manager.default_flow == 'general'
        assert len(manager.flow_registry) >= 5  # At least the built-in flows
    
    @patch('src.workflow.flows.general_flow.GeneralFlow')
    def test_start_flow(self, mock_flow):
        """Test starting a flow."""
        instance = mock_flow.return_value
        instance.__class__.__name__ = 'GeneralFlow'
        
        manager = FlowManager(CONFIG_PATH)
        # Mock the get_flow_instance method
        manager.get_flow_instance = MagicMock(return_value=instance)
        
        # Start a flow
        result = manager.start_flow('general')
        assert result is True
        assert manager.current_flow == instance
        
        # Verify initialize was called
        instance.initialize.assert_called_once()
    
    def test_end_flow(self):
        """Test ending a flow."""
        manager = FlowManager(CONFIG_PATH)
        
        # Mock flows
        main_flow = MagicMock()
        main_flow.__class__.__name__ = 'GeneralFlow'
        nested_flow = MagicMock()
        nested_flow.__class__.__name__ = 'AppointmentFlow'
        
        # Set up the flow stack
        manager.current_flow = nested_flow
        manager.flow_data = {'key': 'value'}
        manager.flow_stack = [{
            'flow': main_flow,
            'data': {'previous': 'data'}
        }]
        
        # End the flow
        output_data = {'result': 'success'}
        result = manager.end_flow(output_data)
        
        # Check cleanup was called
        nested_flow.cleanup.assert_called_once()
        
        # Check we returned to the previous flow
        assert manager.current_flow == main_flow
        assert 'previous' in manager.flow_data
        assert 'result' in manager.flow_data
        
        # Check resume was called
        main_flow.resume.assert_called_once()
    
    @patch('src.workflow.flows.general_flow.GeneralFlow')
    def test_process_message(self, mock_flow):
        """Test processing a message."""
        instance = mock_flow.return_value
        instance.__class__.__name__ = 'GeneralFlow'
        instance.process.return_value = {'result': 'processed'}
        
        manager = FlowManager(CONFIG_PATH)
        # Mock the get_flow_instance method
        manager.get_flow_instance = MagicMock(return_value=instance)
        manager.start_flow('general')
        
        # Process a message
        result = manager.process_message("Hello, I need help")
        assert result == {'result': 'processed'}
        
        # Verify process was called
        instance.process.assert_called_once()
    
    def test_clear_flows(self):
        """Test clearing all flows."""
        manager = FlowManager(CONFIG_PATH)
        
        # Mock flow
        flow = MagicMock()
        manager.current_flow = flow
        manager.flow_data = {'key': 'value'}
        manager.flow_stack = [{'flow': MagicMock(), 'data': {}}]
        
        # Clear flows
        manager.clear_flows()
        
        # Verify state reset
        flow.cleanup.assert_called_once()
        assert manager.current_flow is None
        assert manager.flow_stack == []
        assert manager.flow_data == {}


class TestFlows:
    """Tests for specific flow implementations."""
    
    def setup_method(self):
        """Set up test data."""
        self.flow_manager = MagicMock()
    
    def test_base_flow(self):
        """Test the base flow class."""
        flow = BaseFlow(self.flow_manager)
        
        # Test initialization
        assert flow.flow_manager == self.flow_manager
        
        # Test basic methods
        flow_data = {}
        flow.initialize(flow_data)
        result = flow.process("Hello", {}, flow_data)
        assert result == flow_data
        flow.cleanup(flow_data)
        flow.resume(flow_data)
    
    def test_general_flow(self):
        """Test the general flow."""
        flow = GeneralFlow(self.flow_manager)
        
        # Test initialization
        flow_data = {}
        flow.initialize(flow_data)
        assert 'state' in flow_data
        assert 'interactions' in flow_data
        assert 'entities' in flow_data
        
        # Test process with appointment intent
        message = "I need to schedule an appointment"
        flow._analyze_intent = MagicMock(return_value='appointment')
        self.flow_manager.start_flow = MagicMock(return_value=True)
        
        result = flow.process(message, {}, flow_data)
        self.flow_manager.start_flow.assert_called_once_with('appointment', flow_data)
        assert 'transitioned_to' in result
        assert result['transitioned_to'] == 'appointment'
    
    def test_appointment_flow(self):
        """Test the appointment flow."""
        flow = AppointmentFlow(self.flow_manager)
        
        # Test initialization
        flow_data = {}
        flow.initialize(flow_data)
        assert 'appointment' in flow_data
        assert flow_data['appointment']['state'] == flow.STATES['INIT']
        
        # Test process in initial state with date entity
        message = "I want to book for January 15th"
        flow._extract_entities = MagicMock(return_value={'dates': ['January 15th']})
        
        result = flow.process(message, {}, flow_data)
        assert flow_data['appointment']['date'] == 'January 15th'
        assert flow_data['appointment']['state'] == flow.STATES['COLLECTING_TIME']
    
    def test_message_flow(self):
        """Test the message flow."""
        flow = MessageFlow(self.flow_manager)
        
        # Test initialization
        flow_data = {}
        flow.initialize(flow_data)
        assert 'message_data' in flow_data
        assert flow_data['message_data']['state'] == flow.STATES['INIT']
        
        # Test process in initial state with a full message
        message = "Please tell them I'll be late for the meeting tomorrow."
        
        result = flow.process(message, {}, flow_data)
        assert flow_data['message_data']['message'] == message
    
    def test_information_flow(self):
        """Test the information flow."""
        flow = InformationFlow(self.flow_manager)
        
        # Test initialization
        flow_data = {}
        flow.initialize(flow_data)
        assert 'info_data' in flow_data
        
        # Test category determination
        assert flow._determine_info_category("What are your office hours?") == flow.INFO_CATEGORIES['HOURS']
        assert flow._determine_info_category("Where are you located?") == flow.INFO_CATEGORIES['LOCATION']
        assert flow._determine_info_category("How much does it cost?") == flow.INFO_CATEGORIES['PRICING']
    
    def test_escalation_flow(self):
        """Test the escalation flow."""
        flow = EscalationFlow(self.flow_manager)
        
        # Test initialization
        flow_data = {}
        flow.initialize(flow_data)
        assert 'escalation' in flow_data
        assert flow_data['escalation']['state'] == flow.STATES['INIT']
        
        # Test intent analysis
        destination, person = flow._analyze_escalation_intent("I need to speak to technical support")
        assert destination == flow.DESTINATIONS['SUPPORT']
        assert person is None
        
        destination, person = flow._analyze_escalation_intent("I want to talk to John Smith please")
        assert destination == flow.DESTINATIONS['SPECIFIC']
        assert person == "John Smith"