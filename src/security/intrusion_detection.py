"""
Intrusion Detection System (IDS) for AI Call Secretary.
Monitors for suspicious activities and potential security threats.
"""
import time
import ipaddress
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, deque

from src.security_config import security_config
from src.security.audit_log import (
    audit_log, AuditLogEvent, AuditLogLevel,
    log_suspicious_activity
)

# Initialize logging
logger = logging.getLogger(__name__)

class SecurityEvent:
    """Security event with timestamp and details."""
    def __init__(self, event_type: str, details: Dict[str, Any]):
        self.timestamp = datetime.utcnow()
        self.event_type = event_type
        self.details = details


class IntrusionDetectionSystem:
    """
    Intrusion Detection System for monitoring security events
    and detecting potential attacks or suspicious activities.
    """
    
    def __init__(self):
        """Initialize the intrusion detection system."""
        # Time windows for different checks (in seconds)
        self.windows = {
            "login_failure": 300,  # 5 minutes
            "brute_force": 600,  # 10 minutes
            "port_scan": 120,  # 2 minutes
            "path_traversal": 300,  # 5 minutes
            "sql_injection": 300,  # 5 minutes
            "xss": 300,  # 5 minutes
            "rate_limit": 60  # 1 minute
        }
        
        # Thresholds for alerts
        self.thresholds = {
            "login_failure": 5,  # Alert after 5 failed logins
            "brute_force": 10,  # Alert after 10 login attempts
            "port_scan": 15,  # Alert after 15 different ports
            "path_traversal": 3,  # Alert after 3 path traversal attempts
            "sql_injection": 3,  # Alert after 3 SQL injection attempts
            "xss": 3,  # Alert after 3 XSS attempts
            "rate_limit": 20  # Alert after 20 rate limit violations
        }
        
        # Event counters by IP and user
        self.ip_events = defaultdict(lambda: defaultdict(list))
        self.user_events = defaultdict(lambda: defaultdict(list))
        
        # Blacklisted IPs and users
        self.blacklisted_ips = set()
        self.blacklisted_users = set()
        
        # Known crawler user agents
        self.crawler_user_agents = {
            "googlebot", "bingbot", "yandexbot", "slurp", "duckduckbot",
            "baiduspider", "twitterbot", "facebookexternalhit", "linkedinbot",
            "applebot", "pinterestbot", "skypeuripreview"
        }
        
        # Known attack signatures
        self.sql_injection_patterns = {
            "union select", "1=1", "1 = 1", "or 1=1", "or 1 = 1",
            "' or '1'='1", "' or 1 = 1 --", "admin'--", "drop table",
            "information_schema", "exec(", "execute(", "eval(", "xp_cmdshell"
        }
        
        self.xss_patterns = {
            "<script>", "</script>", "javascript:", "onerror=", "onload=",
            "eval(", "document.cookie", "alert(", "onmouseover=", "onfocus=",
            "onclick=", "onmouseout=", "onkeypress=", "onchange="
        }
        
        self.path_traversal_patterns = {
            "../", "..%2f", "%2e%2e%2f", "..\\", "%2e%2e\\", 
            "/etc/passwd", "c:\\windows\\", "boot.ini", "/proc/self/",
            "file:///", "php://", "data://", "ftp://"
        }
        
        # Initialize monitoring thread
        self.running = False
        self.monitor_thread = None
        
        logger.info("Intrusion Detection System initialized")
    
    def start(self):
        """Start the intrusion detection system."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Intrusion Detection System monitoring started")
    
    def stop(self):
        """Stop the intrusion detection system."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        logger.info("Intrusion Detection System stopped")
    
    def _monitoring_loop(self):
        """Background thread for periodic monitoring and cleanup."""
        cleanup_interval = 60  # Clean up every minute
        
        while self.running:
            try:
                # Sleep first to allow some data to accumulate on startup
                time.sleep(cleanup_interval)
                
                # Clean up old events
                self._cleanup_old_events()
                
                # Analyze aggregate patterns
                self._analyze_aggregate_patterns()
            except Exception as e:
                logger.error(f"Error in IDS monitoring loop: {str(e)}", exc_info=True)
    
    def _cleanup_old_events(self):
        """Remove events older than the largest window."""
        # Find the largest window
        max_window = max(self.windows.values())
        cutoff_time = datetime.utcnow() - timedelta(seconds=max_window)
        
        # Cleanup IP events
        for ip in list(self.ip_events.keys()):
            for event_type in list(self.ip_events[ip].keys()):
                self.ip_events[ip][event_type] = [
                    event for event in self.ip_events[ip][event_type]
                    if event.timestamp > cutoff_time
                ]
                
                # Remove empty event types
                if not self.ip_events[ip][event_type]:
                    del self.ip_events[ip][event_type]
            
            # Remove empty IPs
            if not self.ip_events[ip]:
                del self.ip_events[ip]
        
        # Cleanup user events
        for user in list(self.user_events.keys()):
            for event_type in list(self.user_events[user].keys()):
                self.user_events[user][event_type] = [
                    event for event in self.user_events[user][event_type]
                    if event.timestamp > cutoff_time
                ]
                
                # Remove empty event types
                if not self.user_events[user][event_type]:
                    del self.user_events[user][event_type]
            
            # Remove empty users
            if not self.user_events[user]:
                del self.user_events[user]
    
    def _analyze_aggregate_patterns(self):
        """
        Analyze patterns across multiple users and IPs to 
        detect distributed attacks.
        """
        # Analyze login failures across IPs
        ip_login_failures = {}
        for ip, events in self.ip_events.items():
            if "login_failure" in events:
                ip_login_failures[ip] = len(events["login_failure"])
        
        # Check for distributed brute force attack (many IPs, few attempts each)
        if len(ip_login_failures) > 5:
            total_failures = sum(ip_login_failures.values())
            avg_failures = total_failures / len(ip_login_failures)
            
            if total_failures > 20 and avg_failures < 3:
                logger.warning(
                    f"Possible distributed brute force attack detected: "
                    f"{len(ip_login_failures)} IPs with {total_failures} total login failures"
                )
                # Log to audit log
                log_suspicious_activity(
                    user="system",
                    activity_type="DISTRIBUTED_BRUTE_FORCE",
                    message="Possible distributed brute force attack detected",
                    details={
                        "ip_count": len(ip_login_failures),
                        "total_failures": total_failures,
                        "avg_failures_per_ip": avg_failures
                    }
                )
    
    def record_event(
        self,
        event_type: str,
        ip_address: Optional[str] = None,
        user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a security event.
        
        Args:
            event_type: Type of security event
            ip_address: IP address of the client
            user: Username (if authenticated)
            details: Additional details about the event
        """
        # Create event
        event = SecurityEvent(event_type, details or {})
        
        # Record by IP address
        if ip_address:
            self.ip_events[ip_address][event_type].append(event)
            
            # Check IP-based thresholds
            self._check_ip_thresholds(ip_address)
        
        # Record by user
        if user:
            self.user_events[user][event_type].append(event)
            
            # Check user-based thresholds
            self._check_user_thresholds(user)
    
    def _check_ip_thresholds(self, ip_address: str) -> None:
        """Check if any thresholds have been exceeded for an IP address."""
        for event_type, window in self.windows.items():
            if event_type not in self.ip_events[ip_address]:
                continue
            
            # Get events within the time window
            cutoff_time = datetime.utcnow() - timedelta(seconds=window)
            recent_events = [
                event for event in self.ip_events[ip_address][event_type]
                if event.timestamp > cutoff_time
            ]
            
            # Check threshold
            threshold = self.thresholds[event_type]
            if len(recent_events) >= threshold:
                # Log alert
                logger.warning(
                    f"IP address {ip_address} exceeded {event_type} threshold "
                    f"with {len(recent_events)} events in {window} seconds"
                )
                
                # Blacklist IP if severe
                if event_type in ("brute_force", "sql_injection", "xss", "path_traversal"):
                    self._blacklist_ip(ip_address, event_type)
                
                # Log to audit log
                log_suspicious_activity(
                    user="system",
                    activity_type=f"IP_{event_type.upper()}_THRESHOLD",
                    message=f"IP address {ip_address} exceeded {event_type} threshold",
                    ip_address=ip_address,
                    details={
                        "event_count": len(recent_events),
                        "window_seconds": window,
                        "threshold": threshold
                    }
                )
    
    def _check_user_thresholds(self, user: str) -> None:
        """Check if any thresholds have been exceeded for a user."""
        for event_type, window in self.windows.items():
            if event_type not in self.user_events[user]:
                continue
            
            # Get events within the time window
            cutoff_time = datetime.utcnow() - timedelta(seconds=window)
            recent_events = [
                event for event in self.user_events[user][event_type]
                if event.timestamp > cutoff_time
            ]
            
            # Check threshold
            threshold = self.thresholds[event_type]
            if len(recent_events) >= threshold:
                # Log alert
                logger.warning(
                    f"User {user} exceeded {event_type} threshold "
                    f"with {len(recent_events)} events in {window} seconds"
                )
                
                # Blacklist user if severe
                if event_type in ("brute_force", "sql_injection", "xss", "path_traversal"):
                    self._blacklist_user(user, event_type)
                
                # Log to audit log
                log_suspicious_activity(
                    user=user,
                    activity_type=f"USER_{event_type.upper()}_THRESHOLD",
                    message=f"User {user} exceeded {event_type} threshold",
                    details={
                        "event_count": len(recent_events),
                        "window_seconds": window,
                        "threshold": threshold
                    }
                )
    
    def _blacklist_ip(self, ip_address: str, reason: str) -> None:
        """
        Blacklist an IP address.
        
        Args:
            ip_address: IP address to blacklist
            reason: Reason for blacklisting
        """
        if ip_address in self.blacklisted_ips:
            return
        
        logger.warning(f"Blacklisting IP address {ip_address} due to {reason}")
        self.blacklisted_ips.add(ip_address)
        
        # Log to audit log
        audit_log.log_event(
            event_type="IP_BLACKLISTED",
            level=AuditLogLevel.WARNING,
            user="system",
            resource_type="security",
            message=f"IP address {ip_address} blacklisted",
            ip_address=ip_address,
            details={"reason": reason}
        )
    
    def _blacklist_user(self, user: str, reason: str) -> None:
        """
        Blacklist a user.
        
        Args:
            user: Username to blacklist
            reason: Reason for blacklisting
        """
        if user in self.blacklisted_users:
            return
        
        logger.warning(f"Blacklisting user {user} due to {reason}")
        self.blacklisted_users.add(user)
        
        # Log to audit log
        audit_log.log_event(
            event_type="USER_BLACKLISTED",
            level=AuditLogLevel.WARNING,
            user=user,
            resource_type="security",
            message=f"User {user} blacklisted",
            details={"reason": reason}
        )
    
    def is_blacklisted_ip(self, ip_address: str) -> bool:
        """
        Check if an IP address is blacklisted.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            True if blacklisted, False otherwise
        """
        return ip_address in self.blacklisted_ips
    
    def is_blacklisted_user(self, user: str) -> bool:
        """
        Check if a user is blacklisted.
        
        Args:
            user: Username to check
            
        Returns:
            True if blacklisted, False otherwise
        """
        return user in self.blacklisted_users
    
    def scan_request(
        self,
        ip_address: str,
        user: Optional[str],
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
        body: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Scan an HTTP request for potential security threats.
        
        Args:
            ip_address: Client IP address
            user: Username if authenticated
            method: HTTP method
            path: Request path
            headers: HTTP headers
            query_params: Query parameters
            body: Request body
            
        Returns:
            Tuple of (is_threat, reason)
        """
        # Check if IP or user is already blacklisted
        if self.is_blacklisted_ip(ip_address):
            return True, f"IP address {ip_address} is blacklisted"
        
        if user and self.is_blacklisted_user(user):
            return True, f"User {user} is blacklisted"
        
        # Check for path traversal attacks
        if self._check_path_traversal(path, query_params):
            self.record_event("path_traversal", ip_address, user, {
                "method": method,
                "path": path,
                "query_params": query_params
            })
            return True, "Path traversal attempt detected"
        
        # Check for SQL injection attacks
        if self._check_sql_injection(query_params, body):
            self.record_event("sql_injection", ip_address, user, {
                "method": method,
                "path": path,
                "query_params": query_params
            })
            return True, "SQL injection attempt detected"
        
        # Check for XSS attacks
        if self._check_xss(query_params, body):
            self.record_event("xss", ip_address, user, {
                "method": method,
                "path": path,
                "query_params": query_params
            })
            return True, "XSS attempt detected"
        
        # No threats detected
        return False, None
    
    def _check_path_traversal(self, path: str, query_params: Dict[str, str]) -> bool:
        """
        Check for path traversal attack indicators.
        
        Args:
            path: Request path
            query_params: Query parameters
            
        Returns:
            True if attack detected, False otherwise
        """
        # Check path
        for pattern in self.path_traversal_patterns:
            if pattern in path:
                return True
        
        # Check query parameters
        for param, value in query_params.items():
            for pattern in self.path_traversal_patterns:
                if pattern in value:
                    return True
        
        return False
    
    def _check_sql_injection(
        self,
        query_params: Dict[str, str],
        body: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check for SQL injection attack indicators.
        
        Args:
            query_params: Query parameters
            body: Request body
            
        Returns:
            True if attack detected, False otherwise
        """
        # Check query parameters
        for param, value in query_params.items():
            value_lower = value.lower()
            for pattern in self.sql_injection_patterns:
                if pattern in value_lower:
                    return True
        
        # Check body parameters if present
        if body:
            for key, value in body.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    for pattern in self.sql_injection_patterns:
                        if pattern in value_lower:
                            return True
        
        return False
    
    def _check_xss(
        self,
        query_params: Dict[str, str],
        body: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check for XSS attack indicators.
        
        Args:
            query_params: Query parameters
            body: Request body
            
        Returns:
            True if attack detected, False otherwise
        """
        # Check query parameters
        for param, value in query_params.items():
            value_lower = value.lower()
            for pattern in self.xss_patterns:
                if pattern in value_lower:
                    return True
        
        # Check body parameters if present
        if body:
            for key, value in body.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    for pattern in self.xss_patterns:
                        if pattern in value_lower:
                            return True
        
        return False
    
    def record_login_failure(
        self,
        ip_address: str,
        user: str,
        reason: str
    ) -> None:
        """
        Record a failed login attempt.
        
        Args:
            ip_address: Client IP address
            user: Username
            reason: Reason for failure
        """
        self.record_event("login_failure", ip_address, user, {"reason": reason})
        
        # Also check for brute force
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.windows["brute_force"])
        
        # Count recent login failures for this user
        user_failures = 0
        if "login_failure" in self.user_events[user]:
            user_failures = sum(
                1 for event in self.user_events[user]["login_failure"]
                if event.timestamp > cutoff_time
            )
        
        # Count recent login failures from this IP
        ip_failures = 0
        if "login_failure" in self.ip_events[ip_address]:
            ip_failures = sum(
                1 for event in self.ip_events[ip_address]["login_failure"]
                if event.timestamp > cutoff_time
            )
        
        # Record brute force if threshold exceeded
        if user_failures >= self.thresholds["brute_force"] or ip_failures >= self.thresholds["brute_force"]:
            self.record_event("brute_force", ip_address, user, {
                "user_failures": user_failures,
                "ip_failures": ip_failures
            })
    
    def record_rate_limit_exceeded(
        self,
        ip_address: str,
        user: Optional[str],
        endpoint: str,
        limit: int
    ) -> None:
        """
        Record a rate limit exceeded event.
        
        Args:
            ip_address: Client IP address
            user: Username if authenticated
            endpoint: API endpoint
            limit: Rate limit that was exceeded
        """
        self.record_event("rate_limit", ip_address, user, {
            "endpoint": endpoint,
            "limit": limit
        })


# Create global IDS instance
intrusion_detection = IntrusionDetectionSystem()

# Start monitoring on import
intrusion_detection.start()