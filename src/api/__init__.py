"""
API package for the AI Call Secretary.
"""
from src.api.app import app
from src.api.schemas import (
    CallDetail, CallSummary, CallListResponse, ActionRequest, ActionResult,
    AppointmentRequest, MessageRequest, CallFilterParams, SystemStatus,
    TokenResponse, ErrorResponse, CallEvent, CallEventType
)

__all__ = [
    'app',
    'CallDetail',
    'CallSummary',
    'CallListResponse',
    'ActionRequest',
    'ActionResult',
    'AppointmentRequest',
    'MessageRequest',
    'CallFilterParams',
    'SystemStatus',
    'TokenResponse',
    'ErrorResponse',
    'CallEvent',
    'CallEventType'
]