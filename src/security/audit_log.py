"""
Security audit logging module for AI Call Secretary.
Provides functionality for recording and querying security-related events.
"""
import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4

from src.security_config import security_config

# Initialize logging
logger = logging.getLogger(__name__)

# Define audit log levels
class AuditLogLevel:
    """Audit log severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditLogEvent:
    """Audit log event types."""
    # Authentication events
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET_REQUEST = "PASSWORD_RESET_REQUEST"
    PASSWORD_RESET_COMPLETE = "PASSWORD_RESET_COMPLETE"
    MFA_ENABLE = "MFA_ENABLE"
    MFA_DISABLE = "MFA_DISABLE"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    
    # Access control events
    ACCESS_DENIED = "ACCESS_DENIED"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"
    
    # Data access events
    DATA_ACCESS = "DATA_ACCESS"
    DATA_MODIFICATION = "DATA_MODIFICATION"
    DATA_DELETION = "DATA_DELETION"
    
    # User management events
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    USER_LOCK = "USER_LOCK"
    USER_UNLOCK = "USER_UNLOCK"
    
    # System events
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    
    # Security events
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    BRUTE_FORCE_ATTEMPT = "BRUTE_FORCE_ATTEMPT"
    INPUT_VALIDATION_FAILURE = "INPUT_VALIDATION_FAILURE"

class AuditLog:
    """
    Security audit log manager.
    Provides functionality for recording and querying security-related events.
    """
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize the audit log manager.
        
        Args:
            log_path: Path to the audit log file. If None, will use 'logs/audit_log.jsonl'
        """
        self.log_path = log_path or os.path.join("logs", "audit_log.jsonl")
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        # Configure sensitive fields for masking
        self.sensitive_fields = security_config.logging.sensitive_fields
        
        # Log retention period in days
        self.retention_days = 90
        
        logger.info(f"Audit log initialized with path: {self.log_path}")
        
        # Log system start event
        self.log_event(
            event_type=AuditLogEvent.SYSTEM_START,
            level=AuditLogLevel.INFO,
            user="system",
            resource_type="system",
            message="System started",
        )
    
    def log_event(
        self,
        event_type: str,
        level: str,
        user: str,
        resource_type: str,
        message: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Log a security event to the audit log.
        
        Args:
            event_type: Type of event (see AuditLogEvent)
            level: Severity level (see AuditLogLevel)
            user: Username or identifier of the user performing the action
            resource_type: Type of resource being accessed or modified
            message: Human-readable description of the event
            resource_id: Identifier of the specific resource
            ip_address: IP address of the user
            user_agent: User agent of the client
            details: Additional details about the event
            
        Returns:
            The audit log entry
        """
        # Create event ID
        event_id = str(uuid4())
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Mask sensitive data in details
        if details and security_config.logging.mask_sensitive_data:
            details = self._mask_sensitive_data(details)
        
        # Create log entry
        log_entry = {
            "id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "level": level,
            "user": user,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "message": message,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
        }
        
        # Write to log file
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Error writing to audit log: {str(e)}", exc_info=True)
        
        # Also log to application logs for critical events
        if level in (AuditLogLevel.ERROR, AuditLogLevel.CRITICAL):
            log_message = f"SECURITY: {event_type} - {message} - User: {user}"
            if level == AuditLogLevel.CRITICAL:
                logger.critical(log_message)
            else:
                logger.error(log_message)
        
        return log_entry
    
    def query_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        level: Optional[str] = None,
        user: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Query the audit log for specific events.
        
        Args:
            start_date: Filter events after this date
            end_date: Filter events before this date
            event_type: Filter by event type
            level: Filter by severity level
            user: Filter by username
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            ip_address: Filter by IP address
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of audit log entries matching the criteria
        """
        if not os.path.exists(self.log_path):
            return []
        
        try:
            # Read log file
            with open(self.log_path, "r") as f:
                logs = [json.loads(line) for line in f]
            
            # Apply filters
            filtered_logs = []
            for log in logs:
                # Parse timestamp
                log_timestamp = datetime.fromisoformat(log["timestamp"])
                
                # Apply date filters
                if start_date and log_timestamp < start_date:
                    continue
                if end_date and log_timestamp > end_date:
                    continue
                
                # Apply other filters
                if event_type and log["event_type"] != event_type:
                    continue
                if level and log["level"] != level:
                    continue
                if user and log["user"] != user:
                    continue
                if resource_type and log["resource_type"] != resource_type:
                    continue
                if resource_id and log["resource_id"] != resource_id:
                    continue
                if ip_address and log["ip_address"] != ip_address:
                    continue
                
                filtered_logs.append(log)
            
            # Apply limit and offset
            paginated_logs = filtered_logs[offset:offset + limit]
            
            return paginated_logs
        except Exception as e:
            logger.error(f"Error querying audit log: {str(e)}", exc_info=True)
            return []
    
    def get_recent_activity(self, user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent activity for a specific user.
        
        Args:
            user: Username to filter by
            limit: Maximum number of results
            
        Returns:
            List of recent audit log entries for the user
        """
        return self.query_logs(user=user, limit=limit, offset=0)
    
    def get_login_failures(
        self, user: Optional[str] = None, hours: int = 24, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent login failures.
        
        Args:
            user: Username to filter by (optional)
            hours: Number of hours to look back
            limit: Maximum number of results
            
        Returns:
            List of login failure events
        """
        start_date = datetime.utcnow() - timedelta(hours=hours)
        return self.query_logs(
            start_date=start_date,
            event_type=AuditLogEvent.LOGIN_FAILURE,
            user=user,
            limit=limit,
        )
    
    def get_suspicious_activity(
        self, hours: int = 24, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent suspicious activity.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of results
            
        Returns:
            List of suspicious activity events
        """
        start_date = datetime.utcnow() - timedelta(hours=hours)
        
        # Get all logs in timeframe
        all_logs = self.query_logs(
            start_date=start_date,
            limit=10000,  # High limit to get all logs in period
        )
        
        # Find suspicious events (login failures, access denied, rate limit exceeded, etc.)
        suspicious_events = [
            log for log in all_logs
            if log["event_type"] in (
                AuditLogEvent.LOGIN_FAILURE,
                AuditLogEvent.ACCESS_DENIED,
                AuditLogEvent.RATE_LIMIT_EXCEEDED,
                AuditLogEvent.SUSPICIOUS_ACTIVITY,
                AuditLogEvent.BRUTE_FORCE_ATTEMPT,
                AuditLogEvent.INPUT_VALIDATION_FAILURE,
            )
        ]
        
        # Sort by timestamp (newest first) and apply limit
        suspicious_events.sort(
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        return suspicious_events[:limit]
    
    def rotate_logs(self) -> bool:
        """
        Rotate audit logs, removing entries older than the retention period.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.log_path):
                return True
            
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Read all logs
            with open(self.log_path, "r") as f:
                logs = [json.loads(line) for line in f]
            
            # Filter out old logs
            current_logs = []
            for log in logs:
                log_timestamp = datetime.fromisoformat(log["timestamp"])
                if log_timestamp >= cutoff_date:
                    current_logs.append(log)
            
            # Write back current logs
            with open(self.log_path, "w") as f:
                for log in current_logs:
                    f.write(json.dumps(log) + "\n")
            
            logger.info(
                f"Rotated audit logs: removed {len(logs) - len(current_logs)} entries "
                f"older than {self.retention_days} days"
            )
            
            return True
        except Exception as e:
            logger.error(f"Error rotating audit logs: {str(e)}", exc_info=True)
            return False
    
    def _mask_sensitive_data(self, data: Union[Dict[str, Any], List, str]) -> Union[Dict[str, Any], List, str]:
        """
        Mask sensitive data in log details.
        
        Args:
            data: Data to mask
            
        Returns:
            Masked data
        """
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if key.lower() in [field.lower() for field in self.sensitive_fields]:
                    masked_data[key] = "****MASKED****"
                elif isinstance(value, (dict, list)):
                    masked_data[key] = self._mask_sensitive_data(value)
                else:
                    masked_data[key] = value
            return masked_data
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Check if string contains any sensitive field names
            if any(field.lower() in data.lower() for field in self.sensitive_fields):
                return "****POTENTIAL-SENSITIVE-DATA****"
            return data
        else:
            return data


# Create global audit log instance
audit_log = AuditLog()

# Helper functions for common audit logging actions

def log_login_success(
    user: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Log successful login."""
    audit_log.log_event(
        event_type=AuditLogEvent.LOGIN_SUCCESS,
        level=AuditLogLevel.INFO,
        user=user,
        resource_type="authentication",
        message=f"Successful login for user: {user}",
        ip_address=ip_address,
        user_agent=user_agent,
    )

def log_login_failure(
    user: str,
    reason: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Log failed login."""
    audit_log.log_event(
        event_type=AuditLogEvent.LOGIN_FAILURE,
        level=AuditLogLevel.WARNING,
        user=user,
        resource_type="authentication",
        message=f"Failed login for user: {user} - Reason: {reason}",
        ip_address=ip_address,
        user_agent=user_agent,
        details={"reason": reason},
    )

def log_logout(
    user: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Log user logout."""
    audit_log.log_event(
        event_type=AuditLogEvent.LOGOUT,
        level=AuditLogLevel.INFO,
        user=user,
        resource_type="authentication",
        message=f"User logout: {user}",
        ip_address=ip_address,
        user_agent=user_agent,
    )

def log_access_denied(
    user: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log access denied event."""
    resource_str = f"{resource_type}"
    if resource_id:
        resource_str += f": {resource_id}"
    
    audit_log.log_event(
        event_type=AuditLogEvent.ACCESS_DENIED,
        level=AuditLogLevel.WARNING,
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        message=f"Access denied to {resource_str} for user: {user}",
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )

def log_user_action(
    user: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log user action."""
    resource_str = f"{resource_type}"
    if resource_id:
        resource_str += f": {resource_id}"
    
    audit_log.log_event(
        event_type=action,
        level=AuditLogLevel.INFO,
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        message=f"User {user} performed {action} on {resource_str}",
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )

def log_suspicious_activity(
    user: str,
    activity_type: str,
    message: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log suspicious activity."""
    audit_log.log_event(
        event_type=AuditLogEvent.SUSPICIOUS_ACTIVITY,
        level=AuditLogLevel.WARNING,
        user=user,
        resource_type="security",
        message=message,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )