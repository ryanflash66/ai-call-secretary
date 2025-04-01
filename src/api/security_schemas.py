"""
Security-related schemas for the AI Call Secretary API.
Includes user models, authentication requests/responses, and password reset models.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, SecretStr, validator
from enum import Enum


class UserRole(str, Enum):
    """User role enum."""
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"


class UserCreate(BaseModel):
    """User creation request model."""
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.OPERATOR
    
    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v
    
    @validator("password")
    def password_min_length(cls, v):
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    """User update request model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserPublic(BaseModel):
    """Public user information model."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None


class PasswordChange(BaseModel):
    """Password change request model."""
    current_password: str
    new_password: str
    
    @validator("new_password")
    def password_min_length(cls, v):
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class PasswordReset(BaseModel):
    """Password reset request model."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    token: str
    new_password: str
    
    @validator("new_password")
    def password_min_length(cls, v):
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request model."""
    refresh_token: Optional[str] = None  # If None, only the access token is invalidated


class MfaSetupResponse(BaseModel):
    """MFA setup response model."""
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class MfaVerifyRequest(BaseModel):
    """MFA verification request model."""
    code: str


class MfaDisableRequest(BaseModel):
    """MFA disable request model."""
    current_password: str


class SecurityQuestionResponse(BaseModel):
    """Security question response model."""
    questions: List[str]


class SecurityQuestionSet(BaseModel):
    """Security question set model."""
    question1: str
    answer1: str
    question2: str
    answer2: str
    question3: str
    answer3: str


class ApiKeyResponse(BaseModel):
    """API key response model."""
    key: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    permissions: List[str]


class ApiKeyCreate(BaseModel):
    """API key creation request model."""
    name: str
    expires_in_days: Optional[int] = None  # None means no expiration
    permissions: List[str]


class AuditLogEntry(BaseModel):
    """Audit log entry model."""
    id: str
    timestamp: datetime
    user: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: str
    user_agent: str


class AuditLogFilter(BaseModel):
    """Audit log filter model."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    page: int = 1
    page_size: int = 50