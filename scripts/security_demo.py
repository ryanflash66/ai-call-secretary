#!/usr/bin/env python3
"""
Security demonstration script for AI Call Secretary.
Demonstrates key security features: authentication, encryption, access control, etc.
"""
import os
import sys
import time
import logging
import argparse
import json
from datetime import datetime
from pprint import pprint

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import security components
from src.security_config import security_config
from src.security.encryption import encryption_service
from src.security.audit_log import audit_log, AuditLogEvent, AuditLogLevel
from src.security.intrusion_detection import intrusion_detection
from src.security.data_access import access_control, data_store
from src.security.utils import security_utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def demo_encryption():
    """Demonstrate encryption features."""
    print_section("Encryption Demo")
    
    # Symmetric encryption
    print("1. Symmetric Encryption (Fernet)")
    data = "This is sensitive user data including credit card: 4111-1111-1111-1111"
    print(f"Original: {data}")
    
    encrypted = encryption_service.encrypt_symmetric(data)
    print(f"Encrypted: {encrypted}")
    
    decrypted = encryption_service.decrypt_symmetric(encrypted).decode()
    print(f"Decrypted: {decrypted}")
    print("")
    
    # Asymmetric encryption
    print("2. Asymmetric Encryption (RSA)")
    data = "This is data that will be encrypted with RSA"
    print(f"Original: {data}")
    
    encrypted = encryption_service.encrypt_asymmetric(data)
    print(f"Encrypted: {encrypted}")
    
    decrypted = encryption_service.decrypt_asymmetric(encrypted).decode()
    print(f"Decrypted: {decrypted}")
    print("")
    
    # Field-level encryption
    print("3. Field-level Encryption")
    data = {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "secretpassword123",
        "credit_card": "4111-1111-1111-1111",
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zip": "10001"
        }
    }
    print("Original data:")
    pprint(data)
    
    encrypted_data = encryption_service.encrypt_dict(data)
    print("\nEncrypted data:")
    pprint(encrypted_data)
    
    decrypted_data = encryption_service.decrypt_dict(encrypted_data)
    print("\nDecrypted data:")
    pprint(decrypted_data)
    print("")
    
    # Password hashing
    print("4. Password Hashing (PBKDF2)")
    password = "MySecurePassword123!"
    print(f"Original password: {password}")
    
    hashed, salt = encryption_service.hash_password(password)
    print(f"Hashed password: {hashed.hex()}")
    print(f"Salt: {salt.hex()}")
    
    is_valid = encryption_service.verify_password(password, hashed, salt)
    print(f"Password valid: {is_valid}")
    
    is_invalid = encryption_service.verify_password("WrongPassword", hashed, salt)
    print(f"Wrong password valid: {is_invalid}")


def demo_access_control():
    """Demonstrate access control features."""
    print_section("Access Control Demo")
    
    # Create test data
    test_data = {
        "call123": {
            "call_id": "call123",
            "caller_number": "1234567890",
            "caller_name": "John Doe",
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
            "duration": None,
            "status": "active",
            "transcript": "Hello, this is a test call",
            "credit_card_info": "4111-1111-1111-1111",
            "ssn": "123-45-6789"
        }
    }
    
    # Save test data
    data_store.save_data("calls", test_data)
    print("Created test call data")
    
    # Access with different roles
    roles = ["admin", "manager", "operator", "viewer"]
    
    for role in roles:
        print(f"\nAccessing data as {role}:")
        
        # Set user context
        access_control.set_current_user(user_id=f"user_{role}", role=role)
        
        # Get permissions
        has_read = access_control.has_permission("calls", "read")
        has_write = access_control.has_permission("calls", "write")
        has_delete = access_control.has_permission("calls", "delete")
        
        print(f"Permissions - Read: {has_read}, Write: {has_write}, Delete: {has_delete}")
        
        # Try to access data
        if has_read:
            resource = data_store.get_resource("calls", "call123")
            print("Visible fields:")
            pprint(resource)
        else:
            print("No read permission - access denied")
    
    # Clear user context
    access_control.clear_current_user()


def demo_intrusion_detection():
    """Demonstrate intrusion detection features."""
    print_section("Intrusion Detection Demo")
    
    # Simulate login failures
    print("1. Login Failure Detection")
    print("Simulating multiple login failures...")
    
    for i in range(6):
        intrusion_detection.record_login_failure(
            ip_address="192.168.1.1",
            user="testuser",
            reason="Invalid password"
        )
        print(f"Recorded login failure {i+1}/6")
        time.sleep(0.1)
    
    # Check if IP is blacklisted
    is_blacklisted = intrusion_detection.is_blacklisted_ip("192.168.1.1")
    print(f"IP blacklisted: {is_blacklisted}")
    
    # Simulate SQL injection attack
    print("\n2. SQL Injection Detection")
    
    # These would normally come from a request
    path = "/api/users"
    headers = {"User-Agent": "Mozilla/5.0"}
    query_params = {"name": "' OR 1=1 --"}
    
    is_threat, reason = intrusion_detection.scan_request(
        ip_address="192.168.1.2",
        user="testuser",
        method="GET",
        path=path,
        headers=headers,
        query_params=query_params
    )
    
    print(f"Threat detected: {is_threat}")
    print(f"Reason: {reason}")
    
    # Simulate XSS attack
    print("\n3. XSS Attack Detection")
    
    query_params = {"comment": "<script>alert('XSS')</script>"}
    
    is_threat, reason = intrusion_detection.scan_request(
        ip_address="192.168.1.3",
        user="testuser",
        method="POST",
        path="/api/comments",
        headers=headers,
        query_params=query_params
    )
    
    print(f"Threat detected: {is_threat}")
    print(f"Reason: {reason}")


def demo_audit_logging():
    """Demonstrate audit logging features."""
    print_section("Audit Logging Demo")
    
    # Log various events
    print("1. Logging Security Events")
    
    event_types = [
        (AuditLogEvent.LOGIN_SUCCESS, AuditLogLevel.INFO),
        (AuditLogEvent.LOGIN_FAILURE, AuditLogLevel.WARNING),
        (AuditLogEvent.ACCESS_DENIED, AuditLogLevel.WARNING),
        (AuditLogEvent.DATA_ACCESS, AuditLogLevel.INFO),
        (AuditLogEvent.DATA_MODIFICATION, AuditLogLevel.INFO),
        (AuditLogEvent.SUSPICIOUS_ACTIVITY, AuditLogLevel.WARNING)
    ]
    
    for event_type, level in event_types:
        audit_log.log_event(
            event_type=event_type,
            level=level,
            user="testuser",
            resource_type="calls",
            resource_id="call123",
            message=f"Test {event_type} event",
            ip_address="192.168.1.1",
            details={"test": True, "timestamp": datetime.utcnow().isoformat()}
        )
        print(f"Logged {event_type} event")
    
    # Query logs
    print("\n2. Querying Audit Logs")
    
    # Query all logs
    logs = audit_log.query_logs(limit=10)
    print(f"Found {len(logs)} audit log entries")
    
    if logs:
        print("\nLatest log entry:")
        pprint(logs[0])
    
    # Query by event type
    warning_logs = audit_log.query_logs(level=AuditLogLevel.WARNING, limit=10)
    print(f"\nFound {len(warning_logs)} warning-level events")
    
    # Query suspicious activity
    suspicious = audit_log.get_suspicious_activity(hours=1)
    print(f"\nFound {len(suspicious)} suspicious activities in the last hour")


def demo_security_utils():
    """Demonstrate security utility functions."""
    print_section("Security Utilities Demo")
    
    # Password generation
    print("1. Secure Password Generation")
    password = security_utils.generate_password()
    print(f"Generated password: {password}")
    
    # Password validation
    print("\n2. Password Validation")
    passwords = [
        "short",
        "nouppercase123!",
        "NOLOWERCASE123!",
        "NoDigits!",
        "NoSpecial123",
        "Secure123!"
    ]
    
    for pwd in passwords:
        valid, reason = security_utils.validate_password_strength(pwd)
        print(f"Password: {pwd}")
        print(f"Valid: {valid}")
        if not valid:
            print(f"Reason: {reason}")
        print("")
    
    # PII masking
    print("3. PII Masking")
    text = """
    Contact John Doe at john@example.com or 123-456-7890.
    His credit card is 4111-1111-1111-1111 and SSN is 123-45-6789.
    """
    print(f"Original text:\n{text}")
    
    masked = security_utils.mask_pii(text)
    print(f"\nMasked text:\n{masked}")
    
    # Input sanitization
    print("\n4. Input Sanitization")
    inputs = [
        "Normal text",
        "<script>alert('XSS')</script>",
        "Text with javascript:alert('XSS')",
        "Text with onclick=alert('XSS')"
    ]
    
    for input_text in inputs:
        sanitized = security_utils.sanitize_input(input_text)
        print(f"Original: {input_text}")
        print(f"Sanitized: {sanitized}")
        print("")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Call Secretary Security Demo")
    
    parser.add_argument(
        "--features",
        type=str,
        choices=["encryption", "access-control", "intrusion-detection", "audit-logging", "utils", "all"],
        default="all",
        help="Which security features to demonstrate"
    )
    
    args = parser.parse_args()
    
    print("\nAI Call Secretary Security Demo")
    print("================================\n")
    
    # Run demos based on command line arguments
    if args.features == "encryption" or args.features == "all":
        demo_encryption()
    
    if args.features == "access-control" or args.features == "all":
        demo_access_control()
    
    if args.features == "intrusion-detection" or args.features == "all":
        demo_intrusion_detection()
    
    if args.features == "audit-logging" or args.features == "all":
        demo_audit_logging()
    
    if args.features == "utils" or args.features == "all":
        demo_security_utils()
    
    print("\nSecurity Demo Complete\n")


if __name__ == "__main__":
    main()