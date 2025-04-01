"""
API package for the AI Call Secretary.
"""
from src.api.routes import app as api_app
from src.api.schemas import (
    CallDetail, CallSummary, CallListResponse, ActionRequest, ActionResult,
    AppointmentRequest, MessageRequest, CallFilterParams, SystemStatus,
    TokenResponse, ErrorResponse, CallEvent, CallEventType
)

__all__ = [
    'api_app',
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