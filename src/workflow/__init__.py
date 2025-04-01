"""
Workflow package.
Contains components for managing conversation flows and executing actions.
"""
from src.workflow.actions import ActionHandler, ActionExecutor, extract_entities_from_text
from src.workflow.flows.flow_manager import FlowManager
from src.workflow.flows import (
    GeneralFlow,
    AppointmentFlow,
    MessageFlow,
    InformationFlow,
    EscalationFlow
)

__all__ = [
    'ActionHandler',
    'ActionExecutor',
    'extract_entities_from_text',
    'FlowManager',
    'GeneralFlow',
    'AppointmentFlow',
    'MessageFlow',
    'InformationFlow',
    'EscalationFlow'
]