"""
Conversation flows package.
Contains flow implementations for managing different types of conversations.
"""
from src.workflow.flows.general_flow import GeneralFlow
from src.workflow.flows.appointment_flow import AppointmentFlow
from src.workflow.flows.message_flow import MessageFlow
from src.workflow.flows.information_flow import InformationFlow
from src.workflow.flows.escalation_flow import EscalationFlow

__all__ = [
    'GeneralFlow',
    'AppointmentFlow',
    'MessageFlow',
    'InformationFlow',
    'EscalationFlow'
]