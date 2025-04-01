"""
Security middleware for the AI Call Secretary system.
This module contains middleware components for authentication, authorization, CSRF protection,
secure headers, rate limiting, and input validation.
"""
import os
import time
import logging
import secrets
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Callable, Awaitable, Any, Union

import jwt
from fastapi import Request, Response, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.base import BaseHTTPMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from src.security_config import security_config

# Initialize logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=security_config.jwt.token_url)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication and authorization."""
    
    def __init__(self, app, exempt_paths: List[str] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            security_config.jwt.token_url,
            security_config.jwt.refresh_url,
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.config = security_config.jwt
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Check if path is exempt from authentication
        for path in self.exempt_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # No token provided
            logger.warning(f"Authentication failure: No token provided for {request.url.path}")
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if header has correct format
        if not auth_header.startswith("Bearer "):
            logger.warning(f"Authentication failure: Invalid token format for {request.url.path}")
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.config.secret.get_secret_value(),
                algorithms=[self.config.algorithm]
            )
            
            # Check if token is expired
            if datetime.fromtimestamp(payload.get("exp", 0)) < datetime.utcnow():
                logger.warning(f"Authentication failure: Token expired for {request.url.path}")
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Add user information to request state
            request.state.user = payload
            request.state.authenticated = True
            
            # Continue processing the request
            return await call_next(request)
            
        except jwt.PyJWTError as e:
            # Invalid token
            logger.warning(f"Authentication failure: {str(e)} for {request.url.path}")
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            # Unexpected error
            logger.error(f"Authentication error: {str(e)} for {request.url.path}", exc_info=True)
            return Response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content="Authentication error",
            )


class CsrfMiddleware(BaseHTTPMiddleware):
    """Middleware for CSRF protection."""
    
    def __init__(self, app, exempt_paths: List[str] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.config = security_config.csrf
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip if CSRF protection is disabled
        if not self.config.enabled:
            return await call_next(request)
        
        # Check if path is exempt from CSRF protection
        for path in self.exempt_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Only apply CSRF protection to state-changing methods
        if request.method not in ["POST", "PUT", "DELETE", "PATCH"]:
            response = await call_next(request)
            
            # Set CSRF token in cookie if it doesn't exist
            if not request.cookies.get(self.config.cookie_name):
                csrf_token = secrets.token_hex(32)
                response.set_cookie(
                    key=self.config.cookie_name,
                    value=csrf_token,
                    max_age=self.config.expiry_hours * 3600,
                    httponly=self.config.cookie_http_only,
                    secure=self.config.cookie_secure,
                    samesite=self.config.cookie_same_site,
                )
            
            return response
        
        # Get CSRF token from cookie
        csrf_cookie = request.cookies.get(self.config.cookie_name)
        if not csrf_cookie:
            logger.warning(f"CSRF failure: No CSRF token in cookies for {request.url.path}")
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                content="CSRF token missing",
            )
        
        # Get CSRF token from header
        csrf_header = request.headers.get(self.config.header_name)
        if not csrf_header:
            logger.warning(f"CSRF failure: No CSRF token in header for {request.url.path}")
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                content="CSRF token missing",
            )
        
        # Validate token
        if not secrets.compare_digest(csrf_cookie, csrf_header):
            logger.warning(f"CSRF failure: Token mismatch for {request.url.path}")
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                content="CSRF token invalid",
            )
        
        # Continue processing the request
        return await call_next(request)


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security-related HTTP headers."""
    
    def __init__(self, app):
        super().__init__(app)
        self.config = security_config.secure_headers
        self.csp_config = security_config.content_security
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        
        # X-Content-Type-Options
        if self.config.x_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        if self.config.x_frame_options:
            response.headers["X-Frame-Options"] = self.config.x_frame_options
        
        # Referrer-Policy
        if self.config.referrer_policy:
            response.headers["Referrer-Policy"] = self.config.referrer_policy
        
        # Strict-Transport-Security (HSTS)
        if self.config.strict_transport_security:
            hsts_value = f"max-age={self.config.hsts_max_age}"
            if self.config.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.config.hsts_preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value
        
        # Permissions-Policy
        if self.config.permissions_policy:
            policy_directives = []
            for feature, allowed in self.config.permissions_policy.items():
                policy_directives.append(f"{feature}={allowed}")
            response.headers["Permissions-Policy"] = ", ".join(policy_directives)
        
        # Content-Security-Policy
        if self.csp_config.enabled:
            csp_directives = []
            
            # Add CSP directives
            if self.csp_config.default_src:
                csp_directives.append(f"default-src {' '.join(self.csp_config.default_src)}")
            if self.csp_config.script_src:
                csp_directives.append(f"script-src {' '.join(self.csp_config.script_src)}")
            if self.csp_config.style_src:
                csp_directives.append(f"style-src {' '.join(self.csp_config.style_src)}")
            if self.csp_config.img_src:
                csp_directives.append(f"img-src {' '.join(self.csp_config.img_src)}")
            if self.csp_config.font_src:
                csp_directives.append(f"font-src {' '.join(self.csp_config.font_src)}")
            if self.csp_config.connect_src:
                csp_directives.append(f"connect-src {' '.join(self.csp_config.connect_src)}")
            if self.csp_config.frame_src:
                csp_directives.append(f"frame-src {' '.join(self.csp_config.frame_src)}")
            
            # Add report URI if configured
            if self.csp_config.report_uri:
                csp_directives.append(f"report-uri {self.csp_config.report_uri}")
            
            # Set the header
            header_name = "Content-Security-Policy-Report-Only" if self.csp_config.report_only else "Content-Security-Policy"
            response.headers[header_name] = "; ".join(csp_directives)
        
        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization."""
    
    def __init__(self, app):
        super().__init__(app)
        self.config = security_config.input_validation
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip if input validation is disabled
        if not self.config.enabled:
            return await call_next(request)
        
        # Check content type
        content_type = request.headers.get("Content-Type", "")
        if content_type and not any(allowed in content_type for allowed in self.config.allowed_content_types):
            logger.warning(f"Input validation failure: Unsupported content type {content_type} for {request.url.path}")
            return Response(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content=f"Unsupported content type: {content_type}",
            )
        
        # Check content length
        content_length = request.headers.get("Content-Length", "0")
        try:
            if int(content_length) > self.config.max_content_length:
                logger.warning(f"Input validation failure: Content too large ({content_length} bytes) for {request.url.path}")
                return Response(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content="Content too large",
                )
        except ValueError:
            pass
        
        # Continue processing the request
        return await call_next(request)


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging security-related events."""
    
    def __init__(self, app):
        super().__init__(app)
        self.config = security_config.logging
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip if security logging is disabled
        if not self.config.log_security_events:
            return await call_next(request)
        
        # Process the request and capture response
        response = await call_next(request)
        
        # Log authentication failures
        if (
            self.config.log_authentication_failures 
            and response.status_code == status.HTTP_401_UNAUTHORIZED
        ):
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "unknown")
            logger.warning(
                f"Authentication failure: IP={client_ip}, UA={user_agent}, Path={request.url.path}"
            )
        
        # Log authorization failures
        if (
            self.config.log_authorization_failures 
            and response.status_code == status.HTTP_403_FORBIDDEN
        ):
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "unknown")
            user_id = getattr(request.state, "user", {}).get("sub", "unknown")
            logger.warning(
                f"Authorization failure: User={user_id}, IP={client_ip}, UA={user_agent}, Path={request.url.path}"
            )
        
        # Log input validation failures
        if (
            self.config.log_input_validation_failures 
            and response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
        ):
            client_ip = request.client.host if request.client else "unknown"
            user_id = getattr(request.state, "user", {}).get("sub", "unknown")
            logger.warning(
                f"Input validation failure: User={user_id}, IP={client_ip}, Path={request.url.path}, Method={request.method}"
            )
        
        # Log rate limit hits
        if (
            self.config.log_rate_limit_hits 
            and response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        ):
            client_ip = request.client.host if request.client else "unknown"
            user_id = getattr(request.state, "user", {}).get("sub", "unknown")
            logger.warning(
                f"Rate limit exceeded: User={user_id}, IP={client_ip}, Path={request.url.path}, Method={request.method}"
            )
        
        return response


# Authentication and authorization utilities
class User(BaseModel):
    """User model for authentication."""
    username: str
    hashed_password: str
    disabled: bool = False
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_admin: bool = False
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None


class TokenData(BaseModel):
    """Token data model."""
    sub: str
    exp: datetime
    jti: str
    is_admin: bool = False
    type: str = "access"


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> bool:
    """Validate password strength against policy."""
    config = security_config.password
    
    # Check length
    if len(password) < config.min_length:
        return False
    
    # Check for uppercase
    if config.require_uppercase and not any(c.isupper() for c in password):
        return False
    
    # Check for lowercase
    if config.require_lowercase and not any(c.islower() for c in password):
        return False
    
    # Check for digits
    if config.require_digits and not any(c.isdigit() for c in password):
        return False
    
    # Check for special characters
    if config.require_special and not any(c in config.special_chars for c in password):
        return False
    
    return True


# Token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=security_config.jwt.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "jti": secrets.token_hex(8),
        "type": "access"
    })
    
    return jwt.encode(
        to_encode,
        security_config.jwt.secret.get_secret_value(),
        algorithm=security_config.jwt.algorithm
    )


def create_refresh_token(data: dict) -> str:
    """Create a new JWT refresh token."""
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=security_config.jwt.refresh_token_expire_days)
    
    to_encode.update({
        "exp": expire,
        "jti": secrets.token_hex(8),
        "type": "refresh"
    })
    
    return jwt.encode(
        to_encode,
        security_config.jwt.secret.get_secret_value(),
        algorithm=security_config.jwt.algorithm
    )


# Sanitization utilities
def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.
    This is a simple example and should be expanded based on the application needs.
    """
    # Remove HTML tags
    if security_config.input_validation.sanitize_html:
        input_string = re.sub(r"<[^>]*>", "", input_string)
    
    return input_string


# Masking utilities for logging
def mask_sensitive_data(data: Union[dict, str], sensitive_fields: List[str] = None) -> Union[dict, str]:
    """Mask sensitive data in logs."""
    if not security_config.logging.mask_sensitive_data:
        return data
    
    if sensitive_fields is None:
        sensitive_fields = security_config.logging.sensitive_fields
    
    if isinstance(data, dict):
        masked_data = {}
        for key, value in data.items():
            if key.lower() in [f.lower() for f in sensitive_fields]:
                masked_data[key] = "****MASKED****"
            elif isinstance(value, dict):
                masked_data[key] = mask_sensitive_data(value, sensitive_fields)
            elif isinstance(value, str) and any(f.lower() in key.lower() for f in sensitive_fields):
                masked_data[key] = "****MASKED****"
            else:
                masked_data[key] = value
        return masked_data
    elif isinstance(data, str):
        # For string data, just check if it contains any sensitive field names
        for field in sensitive_fields:
            if field.lower() in data.lower():
                return "****CONTAINS-SENSITIVE-DATA****"
        return data
    else:
        return data