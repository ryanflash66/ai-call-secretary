"""
Security utilities for AI Call Secretary.
Provides security-related helper functions and middleware integration.
"""
import re
import os
import json
import secrets
import string
import logging
import urllib.parse
from typing import Dict, Any, Optional, List, Tuple
from functools import wraps

from fastapi import Request, Response, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from src.security_config import security_config
from src.security.encryption import encryption_service
from src.security.audit_log import (
    audit_log, AuditLogEvent, AuditLogLevel,
    log_login_success, log_login_failure, log_logout, log_access_denied
)
from src.security.intrusion_detection import intrusion_detection
from src.security.data_access import access_control, data_store

# Initialize logging
logger = logging.getLogger(__name__)

# OAuth2 password bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=security_config.jwt.token_url)


class SecurityUtils:
    """Security utility functions."""
    
    @staticmethod
    def generate_password(length: int = 16) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Length of the password
            
        Returns:
            Random password
        """
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        # Ensure at least one of each type
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # Fill remaining length with random chars from all sets
        all_chars = lowercase + uppercase + digits + symbols
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        # Convert to string
        return "".join(password)
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate a secure random token.
        
        Args:
            length: Length of the token in bytes (will produce 2*length hex chars)
            
        Returns:
            Random token
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def is_safe_url(url: str, allowed_hosts: Optional[List[str]] = None) -> bool:
        """
        Check if a URL is safe for redirects.
        
        Args:
            url: URL to check
            allowed_hosts: List of allowed hostnames
            
        Returns:
            True if safe, False otherwise
        """
        if allowed_hosts is None:
            allowed_hosts = []
        
        # Parse URL
        parsed = urllib.parse.urlparse(url)
        
        # Check if it's a relative URL (safe)
        if not parsed.netloc:
            return True
        
        # Check if hostname is in allowed hosts
        return parsed.netloc in allowed_hosts
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_str: String to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove HTML tags
        sanitized = re.sub(r"<[^>]*>", "", input_str)
        
        # Remove script tags and event handlers
        sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r"on\w+\s*=", "", sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password against policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        config = security_config.password
        
        # Check length
        if len(password) < config.min_length:
            return False, f"Password must be at least {config.min_length} characters"
        
        # Check for uppercase
        if config.require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase
        if config.require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for digits
        if config.require_digits and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        # Check for special characters
        if config.require_special and not any(c in config.special_chars for c in password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation: remove common separators and check if it's a valid number
        clean_phone = re.sub(r"[\s\-\(\)\+\.]", "", phone)
        return clean_phone.isdigit() and 7 <= len(clean_phone) <= 15
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic email validation regex
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    @staticmethod
    def mask_pii(text: str) -> str:
        """
        Mask personally identifiable information in text.
        
        Args:
            text: Text to mask
            
        Returns:
            Masked text
        """
        # Mask email addresses
        text = re.sub(
            r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            r"\1@***",
            text
        )
        
        # Mask phone numbers (assuming common formats)
        text = re.sub(
            r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}",
            "PHONE-NUMBER",
            text
        )
        
        # Mask credit card numbers
        text = re.sub(
            r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
            "CREDIT-CARD",
            text
        )
        
        # Mask SSNs
        text = re.sub(
            r"\b\d{3}[\s-]?\d{2}[\s-]?\d{4}\b",
            "SSN",
            text
        )
        
        return text


# Security-related middleware helpers
async def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request, handling proxies.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for X-Forwarded-For header (common in proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # The client IP is the first address in the list
        return forwarded_for.split(",")[0].strip()
    
    # Fall back to direct client address
    client_host = request.client.host if request.client else "unknown"
    return client_host


async def scan_request_security(request: Request) -> None:
    """
    Scan request for security threats.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If a security threat is detected
    """
    # Get client IP and current user
    ip_address = await get_client_ip(request)
    user_id, _ = access_control.get_current_user()
    
    # Get request details for scanning
    method = request.method
    path = request.url.path
    headers = dict(request.headers.items())
    
    # Get query parameters
    query_params = {}
    for key, value in request.query_params.items():
        query_params[key] = value
    
    # Scan request
    is_threat, reason = intrusion_detection.scan_request(
        ip_address=ip_address,
        user=user_id,
        method=method,
        path=path,
        headers=headers,
        query_params=query_params
    )
    
    if is_threat:
        # Log threat
        logger.warning(
            f"Security threat detected: {reason} - "
            f"IP: {ip_address}, User: {user_id or 'anonymous'}, Path: {path}"
        )
        
        # Log to audit log
        audit_log.log_event(
            event_type=AuditLogEvent.SUSPICIOUS_ACTIVITY,
            level=AuditLogLevel.WARNING,
            user=user_id or "anonymous",
            resource_type="security",
            message=f"Security threat: {reason}",
            ip_address=ip_address,
            details={
                "method": method,
                "path": path,
                "query_params": query_params
            }
        )
        
        # Raise exception
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied due to security concerns"
        )


# FastAPI dependency for role-based access control
def require_role(required_roles: List[str]):
    """
    Dependency for requiring specific roles.
    
    Args:
        required_roles: List of allowed roles
        
    Returns:
        Dependency function
    """
    async def dependency(request: Request, token: str = Depends(oauth2_scheme)):
        # Get current user role
        user_id, role = access_control.get_current_user()
        
        # Check if role is allowed
        if not role or role not in required_roles:
            # Log access denied
            log_access_denied(
                user=user_id or "anonymous",
                resource_type="api",
                resource_id=request.url.path,
                ip_address=await get_client_ip(request),
                details={"required_roles": required_roles, "user_role": role}
            )
            
            # Raise exception
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return True
    
    return dependency


# FastAPI dependency for resource permissions
def require_permission(resource_type: str, permission: str):
    """
    Dependency for requiring specific permission on a resource.
    
    Args:
        resource_type: Type of resource
        permission: Required permission
        
    Returns:
        Dependency function
    """
    async def dependency(request: Request, token: str = Depends(oauth2_scheme)):
        # Check permission
        if not access_control.has_permission(resource_type, permission):
            # Get user ID
            user_id, _ = access_control.get_current_user()
            
            # Log access denied
            log_access_denied(
                user=user_id or "anonymous",
                resource_type=resource_type,
                resource_id=request.url.path,
                ip_address=await get_client_ip(request),
                details={"required_permission": permission}
            )
            
            # Raise exception
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {resource_type}"
            )
        
        return True
    
    return dependency


# Create global instance
security_utils = SecurityUtils()