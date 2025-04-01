"""
Security module for AI Call Secretary.
Provides comprehensive security features including authentication, authorization,
encryption, audit logging, and intrusion detection.
"""
import os
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

from src.security_config import security_config
from src.middleware.security import (
    AuthMiddleware,
    CsrfMiddleware,
    SecureHeadersMiddleware,
    InputValidationMiddleware,
    SecurityLoggingMiddleware
)
from src.security.audit_log import audit_log, AuditLogEvent, AuditLogLevel
from src.security.intrusion_detection import intrusion_detection
from src.security.encryption import encryption_service
from src.security.data_access import access_control, data_store
from src.security.utils import security_utils, scan_request_security, get_client_ip

# Initialize logging
logger = logging.getLogger(__name__)

class SecurityInitializer:
    """
    Initializes and configures all security components.
    """
    
    @classmethod
    def initialize(cls, app: Optional[FastAPI] = None) -> None:
        """
        Initialize security components.
        
        Args:
            app: FastAPI application to add middleware to
        """
        logger.info("Initializing security components")
        
        # Create required directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("keys", exist_ok=True)
        
        # Initialize audit logging
        logger.info("Initializing audit logging")
        # Already initialized on import
        
        # Initialize intrusion detection
        logger.info("Initializing intrusion detection")
        # Already initialized on import
        
        # Initialize encryption
        logger.info("Initializing encryption")
        # Already initialized on import
        
        # Initialize data access control
        logger.info("Initializing data access control")
        # Already initialized on import
        
        # Add middleware to FastAPI app if provided
        if app:
            cls.add_middleware(app)
        
        # Log initialization complete
        logger.info("Security components initialized")
        
        # Log to audit log
        audit_log.log_event(
            event_type=AuditLogEvent.SYSTEM_START,
            level=AuditLogLevel.INFO,
            user="system",
            resource_type="security",
            message="Security components initialized"
        )
    
    @classmethod
    def add_middleware(cls, app: FastAPI) -> None:
        """
        Add security middleware to FastAPI application.
        
        Args:
            app: FastAPI application
        """
        logger.info("Adding security middleware")
        
        # Add request security scanner middleware
        class SecurityScannerMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # Scan request for security threats
                await scan_request_security(request)
                
                # Continue with request
                return await call_next(request)
        
        # Add middleware in correct order
        
        # 1. Input validation (should run first to reject malformed requests)
        app.add_middleware(InputValidationMiddleware)
        
        # 2. Security scanner (runs early to reject malicious requests)
        app.add_middleware(SecurityScannerMiddleware)
        
        # 3. CSRF protection (must run before authentication)
        if security_config.csrf.enabled:
            app.add_middleware(CsrfMiddleware)
        
        # 4. Authentication (runs after input validation and security scanning)
        if not security_config.development_mode:
            app.add_middleware(
                AuthMiddleware,
                exempt_paths=[
                    "/security/token",
                    "/security/token/refresh",
                    "/security/password/reset",
                    "/security/password/reset/confirm",
                    "/docs",
                    "/redoc",
                    "/openapi.json",
                ],
            )
        
        # 5. Security logging (runs after authentication to log authenticated user)
        app.add_middleware(SecurityLoggingMiddleware)
        
        # 6. Secure headers (runs last to add security headers to all responses)
        app.add_middleware(SecureHeadersMiddleware)
        
        logger.info("Security middleware added")
    
    @classmethod
    def shutdown(cls) -> None:
        """Shutdown security components."""
        logger.info("Shutting down security components")
        
        # Stop intrusion detection
        intrusion_detection.stop()
        
        # Log to audit log
        audit_log.log_event(
            event_type=AuditLogEvent.SYSTEM_STOP,
            level=AuditLogLevel.INFO,
            user="system",
            resource_type="security",
            message="Security components shut down"
        )
        
        logger.info("Security components shut down")


# Export components for easy access
__all__ = [
    "security_config",
    "audit_log",
    "intrusion_detection",
    "encryption_service",
    "access_control",
    "data_store",
    "security_utils",
    "SecurityInitializer",
]