"""
Security-related API routes for AI Call Secretary.
Handles user management, authentication, password resets, and audit logging.
"""
import os
import time
import secrets
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form, Body, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.security_config import security_config
from src.middleware.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    validate_password_strength, User, mask_sensitive_data
)
from src.api.security_schemas import (
    UserCreate, UserUpdate, UserPublic, PasswordChange, PasswordReset,
    PasswordResetConfirm, LoginRequest, TokenResponse, RefreshTokenRequest,
    LogoutRequest, MfaSetupResponse, MfaVerifyRequest, MfaDisableRequest,
    SecurityQuestionResponse, SecurityQuestionSet, ApiKeyResponse, ApiKeyCreate,
    AuditLogEntry, AuditLogFilter, UserRole, UserStatus
)

# Initialize logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/security",
    tags=["security"],
)

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/security/token")

# In-memory storage (would be replaced with database in production)
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("Admin@123456"),  # Hashed in production
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "mfa_enabled": False,
        "mfa_secret": None,
        "backup_codes": [],
        "security_questions": None,
        "failed_login_attempts": 0,
        "locked_until": None,
    }
}

# Token blacklist for logout
token_blacklist = set()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check if token is blacklisted
        if token in token_blacklist:
            raise credentials_exception
        
        # Decode token
        payload = jwt.decode(
            token,
            security_config.jwt.secret.get_secret_value(),
            algorithms=[security_config.jwt.algorithm]
        )
        
        # Extract data
        username: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        # Validate token type
        if token_type != "access":
            raise credentials_exception
        
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    
    # Check if user is locked
    if user.get("status") == UserStatus.LOCKED:
        locked_until = user.get("locked_until")
        if locked_until and locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Account is locked. Try again after {locked_until.isoformat()}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            # Unlock user if lock period has passed
            user["status"] = UserStatus.ACTIVE
            user["locked_until"] = None
    
    # Check if user is active
    if user.get("status") != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Check if current user is an admin."""
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def add_to_audit_log(
    request: Request,
    user: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Add an entry to the audit log."""
    if security_config.logging.log_security_events:
        # In production, this would be stored in a database
        try:
            # Mask sensitive data
            if details and security_config.logging.mask_sensitive_data:
                details = mask_sensitive_data(details)
            
            # Log entry
            entry = {
                "id": secrets.token_hex(8),
                "timestamp": datetime.utcnow(),
                "user": user,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details,
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("User-Agent", "unknown"),
            }
            
            # In production, this would be stored in a database
            logger.info(f"Audit log: {entry}")
        except Exception as e:
            logger.error(f"Error adding to audit log: {str(e)}", exc_info=True)


# Authentication routes
@router.post("/token", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    """Login and get access token."""
    # Get user from database
    user = users_db.get(form_data.username)
    
    # Check if user exists
    if not user:
        # Use the same error message to prevent username enumeration
        logger.warning(f"Login attempt for non-existent user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is locked
    if user.get("status") == UserStatus.LOCKED:
        locked_until = user.get("locked_until")
        if locked_until and locked_until > datetime.utcnow():
            logger.warning(f"Login attempt for locked account: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Account is locked. Try again after {locked_until.isoformat()}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            # Unlock user if lock period has passed
            user["status"] = UserStatus.ACTIVE
            user["locked_until"] = None
    
    # Check if user is active
    if user.get("status") != UserStatus.ACTIVE:
        logger.warning(f"Login attempt for inactive account: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        # Increment failed login attempts
        user["failed_login_attempts"] += 1
        
        # Check if account should be locked
        if user["failed_login_attempts"] >= security_config.password.max_failed_attempts:
            # Lock account
            user["status"] = UserStatus.LOCKED
            user["locked_until"] = datetime.utcnow() + timedelta(minutes=security_config.password.lockout_minutes)
            logger.warning(f"Account locked due to too many failed login attempts: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Account locked due to too many failed login attempts. Try again after {user['locked_until'].isoformat()}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.warning(f"Failed login attempt for user {form_data.username} ({user['failed_login_attempts']}/{security_config.password.max_failed_attempts})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Reset failed login attempts
    user["failed_login_attempts"] = 0
    
    # Update last login
    user["last_login"] = datetime.utcnow()
    
    # Create token data
    access_token_expires = timedelta(minutes=security_config.jwt.access_token_expire_minutes)
    token_data = {"sub": user["username"]}
    
    # Create tokens
    access_token = create_access_token(token_data, access_token_expires)
    refresh_token = create_refresh_token(token_data)
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=user["username"],
        action="login",
        resource_type="user",
        resource_id=user["username"],
    )
    
    # Return tokens
    user_data = UserPublic(
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        role=user["role"],
        status=user["status"],
        created_at=user["created_at"],
        last_login=user["last_login"],
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=access_token_expires.seconds,
        user=user_data
    )


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
) -> TokenResponse:
    """Refresh access token."""
    # Check if token is blacklisted
    if refresh_request.refresh_token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode token
        payload = jwt.decode(
            refresh_request.refresh_token,
            security_config.jwt.secret.get_secret_value(),
            algorithms=[security_config.jwt.algorithm]
        )
        
        # Extract data
        username: str = payload.get("sub")
        token_type: str = payload.get("type", "refresh")
        
        # Validate token type
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = users_db.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.get("status") != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token data
    access_token_expires = timedelta(minutes=security_config.jwt.access_token_expire_minutes)
    token_data = {"sub": user["username"]}
    
    # Create new tokens
    access_token = create_access_token(token_data, access_token_expires)
    new_refresh_token = create_refresh_token(token_data)
    
    # Blacklist old refresh token
    token_blacklist.add(refresh_request.refresh_token)
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=user["username"],
        action="refresh_token",
        resource_type="user",
        resource_id=user["username"],
    )
    
    # Return tokens
    user_data = UserPublic(
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        role=user["role"],
        status=user["status"],
        created_at=user["created_at"],
        last_login=user["last_login"],
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=access_token_expires.seconds,
        user=user_data
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    logout_request: LogoutRequest,
    current_user: dict = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
) -> Response:
    """Logout user."""
    # Blacklist access token
    token_blacklist.add(token)
    
    # Blacklist refresh token if provided
    if logout_request.refresh_token:
        token_blacklist.add(logout_request.refresh_token)
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="logout",
        resource_type="user",
        resource_id=current_user["username"],
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# User management routes
@router.post("/users", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_create: UserCreate,
    current_user: dict = Depends(get_current_active_admin),
) -> UserPublic:
    """Create a new user."""
    # Check if username already exists
    if user_create.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Create user
    hashed_password = get_password_hash(user_create.password)
    
    new_user = {
        "username": user_create.username,
        "hashed_password": hashed_password,
        "email": user_create.email,
        "full_name": user_create.full_name,
        "role": user_create.role,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "mfa_enabled": False,
        "mfa_secret": None,
        "backup_codes": [],
        "security_questions": None,
        "failed_login_attempts": 0,
        "locked_until": None,
    }
    
    # Add user to database
    users_db[user_create.username] = new_user
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="create_user",
        resource_type="user",
        resource_id=user_create.username,
        details={"email": user_create.email, "role": user_create.role},
    )
    
    # Return user data
    return UserPublic(
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user.get("full_name"),
        role=new_user["role"],
        status=new_user["status"],
        created_at=new_user["created_at"],
        last_login=new_user["last_login"],
    )


@router.get("/users", response_model=List[UserPublic])
async def list_users(
    current_user: dict = Depends(get_current_active_admin),
) -> List[UserPublic]:
    """List all users."""
    # Convert to UserPublic model
    return [
        UserPublic(
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            role=user["role"],
            status=user["status"],
            created_at=user["created_at"],
            last_login=user["last_login"],
        )
        for user in users_db.values()
    ]


@router.get("/users/{username}", response_model=UserPublic)
async def get_user(
    username: str,
    current_user: dict = Depends(get_current_user),
) -> UserPublic:
    """Get user details."""
    # Check if current user is admin or the requested user
    if current_user["role"] != UserRole.ADMIN and current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get user from database
    user = users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Return user data
    return UserPublic(
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        role=user["role"],
        status=user["status"],
        created_at=user["created_at"],
        last_login=user["last_login"],
    )


@router.put("/users/{username}", response_model=UserPublic)
async def update_user(
    request: Request,
    username: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
) -> UserPublic:
    """Update user details."""
    # Check if current user is admin or the requested user
    if current_user["role"] != UserRole.ADMIN and current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get user from database
    user = users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Only admin can change role and status
    if current_user["role"] != UserRole.ADMIN:
        if user_update.role is not None or user_update.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to change role or status",
            )
    
    # Update user
    if user_update.email is not None:
        user["email"] = user_update.email
    
    if user_update.full_name is not None:
        user["full_name"] = user_update.full_name
    
    if user_update.role is not None and current_user["role"] == UserRole.ADMIN:
        user["role"] = user_update.role
    
    if user_update.status is not None and current_user["role"] == UserRole.ADMIN:
        user["status"] = user_update.status
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="update_user",
        resource_type="user",
        resource_id=username,
        details={k: v for k, v in user_update.dict().items() if v is not None},
    )
    
    # Return updated user
    return UserPublic(
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        role=user["role"],
        status=user["status"],
        created_at=user["created_at"],
        last_login=user["last_login"],
    )


@router.delete("/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    username: str,
    current_user: dict = Depends(get_current_active_admin),
) -> Response:
    """Delete a user."""
    # Check if user exists
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if user is trying to delete themselves
    if current_user["username"] == username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    # Delete user
    del users_db[username]
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="delete_user",
        resource_type="user",
        resource_id=username,
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Password management routes
@router.post("/users/{username}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: Request,
    username: str,
    password_change: PasswordChange,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """Change user password."""
    # Check if current user is the requested user
    if current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Verify current password
    if not verify_password(password_change.current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    # Validate password strength
    if not validate_password_strength(password_change.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet requirements",
        )
    
    # Hash new password
    hashed_password = get_password_hash(password_change.new_password)
    
    # Update password
    current_user["hashed_password"] = hashed_password
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="change_password",
        resource_type="user",
        resource_id=username,
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/password/reset", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    request: Request,
    password_reset: PasswordReset,
) -> Response:
    """Request password reset."""
    # Find user by email
    user = None
    for u in users_db.values():
        if u["email"] == password_reset.email:
            user = u
            break
    
    # Always return success to prevent email enumeration
    if not user:
        logger.info(f"Password reset requested for non-existent email: {password_reset.email}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    # In production, send password reset email with token
    reset_token = secrets.token_hex(32)
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=user["username"],
        action="request_password_reset",
        resource_type="user",
        resource_id=user["username"],
    )
    
    # Log token for testing (would be sent via email in production)
    logger.info(f"Password reset token for {user['username']}: {reset_token}")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/password/reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(
    request: Request,
    password_reset: PasswordResetConfirm,
) -> Response:
    """Confirm password reset."""
    # In production, validate token and find user
    # For now, just log it
    logger.info(f"Password reset confirmation with token: {password_reset.token}")
    
    # Validate password strength
    if not validate_password_strength(password_reset.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet requirements",
        )
    
    # In production, update user password
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# MFA routes
@router.post("/users/{username}/mfa/setup", response_model=MfaSetupResponse)
async def setup_mfa(
    request: Request,
    username: str,
    current_user: dict = Depends(get_current_user),
) -> MfaSetupResponse:
    """Set up MFA for user."""
    # Check if current user is the requested user
    if current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # In production, generate TOTP secret and QR code
    secret = "TESTSECRETFORTOTPAUTH"
    qr_code_url = "https://example.com/qr-code"
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    
    # Update user
    current_user["mfa_secret"] = secret
    current_user["backup_codes"] = backup_codes
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="setup_mfa",
        resource_type="user",
        resource_id=username,
    )
    
    return MfaSetupResponse(
        secret=secret,
        qr_code_url=qr_code_url,
        backup_codes=backup_codes,
    )


@router.post("/users/{username}/mfa/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify_mfa(
    request: Request,
    username: str,
    mfa_verify: MfaVerifyRequest,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """Verify MFA code and enable MFA."""
    # Check if current user is the requested user
    if current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # In production, verify TOTP code
    # For now, just check if code is "123456"
    if mfa_verify.code != "123456" and mfa_verify.code not in current_user.get("backup_codes", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code",
        )
    
    # Enable MFA
    current_user["mfa_enabled"] = True
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="enable_mfa",
        resource_type="user",
        resource_id=username,
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/{username}/mfa/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_mfa(
    request: Request,
    username: str,
    mfa_disable: MfaDisableRequest,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """Disable MFA."""
    # Check if current user is the requested user
    if current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Verify password
    if not verify_password(mfa_disable.current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    # Disable MFA
    current_user["mfa_enabled"] = False
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="disable_mfa",
        resource_type="user",
        resource_id=username,
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Security questions routes
@router.get("/security-questions", response_model=SecurityQuestionResponse)
async def get_security_questions() -> SecurityQuestionResponse:
    """Get available security questions."""
    # In production, fetch from database
    questions = [
        "What was the name of your first pet?",
        "What is your mother's maiden name?",
        "What was the name of your first school?",
        "In what city were you born?",
        "What is the name of your favorite teacher?",
        "What was your childhood nickname?",
        "What is your favorite book?",
        "What was the make of your first car?",
        "What is your favorite movie?",
        "What is the name of the street you grew up on?",
    ]
    
    return SecurityQuestionResponse(questions=questions)


@router.post("/users/{username}/security-questions", status_code=status.HTTP_204_NO_CONTENT)
async def set_security_questions(
    request: Request,
    username: str,
    security_questions: SecurityQuestionSet,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """Set security questions for user."""
    # Check if current user is the requested user
    if current_user["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update security questions
    current_user["security_questions"] = {
        "question1": security_questions.question1,
        "answer1": get_password_hash(security_questions.answer1.lower()),
        "question2": security_questions.question2,
        "answer2": get_password_hash(security_questions.answer2.lower()),
        "question3": security_questions.question3,
        "answer3": get_password_hash(security_questions.answer3.lower()),
    }
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="set_security_questions",
        resource_type="user",
        resource_id=username,
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# API key routes
@router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: Request,
    api_key_create: ApiKeyCreate,
    current_user: dict = Depends(get_current_active_admin),
) -> ApiKeyResponse:
    """Create API key."""
    # Generate API key
    api_key = f"aics_{secrets.token_hex(32)}"
    
    # Set expiration
    expires_at = None
    if api_key_create.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_create.expires_in_days)
    
    # In production, store in database
    
    # Add to audit log
    add_to_audit_log(
        request=request,
        user=current_user["username"],
        action="create_api_key",
        resource_type="api_key",
        resource_id=api_key_create.name,
        details={"permissions": api_key_create.permissions},
    )
    
    return ApiKeyResponse(
        key=api_key,
        name=api_key_create.name,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        permissions=api_key_create.permissions,
    )


# Audit log routes
@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    request: Request,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    current_user: dict = Depends(get_current_active_admin),
) -> List[AuditLogEntry]:
    """Get audit logs."""
    # In production, fetch from database
    # For now, return empty list
    return []