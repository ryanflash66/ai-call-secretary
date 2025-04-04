"""
Pydantic schemas for API validation.
"""
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator


class CallStatus(str, Enum):
    """Call status enum."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TRANSFERRED = "transferred"
    VOICEMAIL = "voicemail"


class FlowType(str, Enum):
    """Flow type enum."""
    GENERAL = "general"
    APPOINTMENT = "appointment"
    MESSAGE = "message"
    INFORMATION = "info"
    ESCALATION = "escalation"


class ActionType(str, Enum):
    """Action type enum."""
    SCHEDULE_APPOINTMENT = "schedule_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    TAKE_MESSAGE = "take_message"
    TRANSFER_CALL = "transfer_call"
    LOOKUP_INFO = "lookup_info"
    SAVE_CONTACT = "save_contact"
    SET_REMINDER = "set_reminder"
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"


class CallEventType(str, Enum):
    """Call event type enum."""
    CALL_STARTED = "call_started"
    CALL_CONNECTED = "call_connected"
    USER_SPOKE = "user_spoke"
    ASSISTANT_SPOKE = "assistant_spoke"
    FLOW_CHANGED = "flow_changed"
    ACTION_EXECUTED = "action_executed"
    CALL_ENDED = "call_ended"
    ERROR = "error"


class CallEvent(BaseModel):
    """Call event model."""
    event_type: CallEventType
    timestamp: datetime = Field(default_factory=datetime.now)
    call_id: str
    data: Optional[Dict[str, Any]] = None


class TranscriptItem(BaseModel):
    """Transcript item model."""
    speaker: str  # "user" or "assistant"
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: Optional[float] = None


class CallTranscript(BaseModel):
    """Call transcript model."""
    call_id: str
    items: List[TranscriptItem] = []


class ActionResult(BaseModel):
    """Action result model."""
    action_type: ActionType
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CallDetail(BaseModel):
    """Call detail model."""
    call_id: str
    caller_number: str
    caller_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    status: CallStatus
    current_flow: Optional[FlowType] = None
    actions: List[ActionResult] = []
    transcript: Optional[CallTranscript] = None
    metadata: Optional[Dict[str, Any]] = None


class CallSummary(BaseModel):
    """Call summary model."""
    call_id: str
    caller_number: str
    caller_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    status: CallStatus
    summary: Optional[str] = None


# Request/Response Models

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None


class CallListResponse(BaseModel):
    """Call list response model."""
    calls: List[CallSummary]
    total: int
    page: int
    page_size: int


class CallFilterParams(BaseModel):
    """Call filter parameters model."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[CallStatus] = None
    caller_number: Optional[str] = None
    page: int = 1
    page_size: int = 50


class ActionRequest(BaseModel):
    """Action request model."""
    action_type: ActionType
    params: Dict[str, Any]


class AppointmentRequest(BaseModel):
    """Appointment request model."""
    date: str  # ISO format date
    time: str
    duration: int = 30  # minutes
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None


class MessageRequest(BaseModel):
    """Message request model."""
    message: str
    caller_name: str
    caller_number: Optional[str] = None
    urgency: str = "normal"  # low, normal, high, critical
    callback_requested: bool = False


class SystemStatus(BaseModel):
    """System status model."""
    status: str
    version: str
    uptime: int  # seconds
    active_calls: int
    total_calls_today: int
    components: Dict[str, str]  # component name -> status
