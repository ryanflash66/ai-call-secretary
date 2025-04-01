# AI Call Secretary Security Module

This module provides comprehensive security features for the AI Call Secretary system.

## Overview

The security module implements multiple layers of protection:

1. **Authentication and Authorization**: JWT-based authentication with role-based access control
2. **Data Protection**: Encryption for sensitive data at rest and in transit
3. **Input Validation**: Protection against malicious input
4. **Intrusion Detection**: Detection and prevention of attack patterns
5. **Audit Logging**: Complete audit trail of security events
6. **Secure Communications**: HTTPS enforcement and security headers

## Components

### 1. Security Configuration (`security_config.py`)

Central configuration for all security settings, including:

- JWT settings
- Password policy
- CORS settings
- CSRF protection
- Content Security Policy
- Rate limiting
- Input validation
- Session management
- TLS configuration
- Security logging

### 2. Security Middleware (`middleware/security.py`)

FastAPI middleware for enforcing security:

- `AuthMiddleware`: JWT authentication
- `CsrfMiddleware`: CSRF protection
- `SecureHeadersMiddleware`: Security headers
- `InputValidationMiddleware`: Input validation
- `SecurityLoggingMiddleware`: Security event logging

### 3. Audit Logging (`security/audit_log.py`)

Comprehensive logging of security events:

- Login/logout events
- Access control events
- Data access events
- System events
- Security alerts

### 4. Intrusion Detection (`security/intrusion_detection.py`)

Detection and prevention of attack patterns:

- SQL injection detection
- XSS detection
- Path traversal detection
- Brute force detection
- Distributed attack detection
- IP and user blacklisting

### 5. Encryption (`security/encryption.py`)

Encryption utilities for sensitive data:

- Symmetric encryption (Fernet)
- Asymmetric encryption (RSA)
- Password hashing (PBKDF2)
- Field-level encryption

### 6. Data Access Control (`security/data_access.py`)

Secure data access with:

- Role-based access control
- Field sensitivity levels
- Data masking
- Access logging

### 7. Security Utilities (`security/utils.py`)

Helper functions for security features:

- Password generation/validation
- URL validation
- Input sanitization
- PII masking
- Request scanning

## Usage

### Initialization

Initialize security components at application startup:

```python
from src.security import SecurityInitializer

# Initialize security components
SecurityInitializer.initialize(app)
```

### Authentication

```python
from src.security.middleware.security import verify_password, get_password_hash

# Hash a password
hashed_password = get_password_hash("password123")

# Verify a password
is_valid = verify_password("password123", hashed_password)
```

### Authorization

```python
from src.security.data_access import access_control

# Set current user context
access_control.set_current_user(user_id="user123", role="admin")

# Check permission
has_permission = access_control.has_permission(
    resource_type="calls", 
    permission="write"
)
```

### Data Encryption

```python
from src.security.encryption import encryption_service

# Encrypt data
encrypted = encryption_service.encrypt_symmetric("sensitive data")

# Decrypt data
decrypted = encryption_service.decrypt_symmetric(encrypted)
```

### Secure Data Access

```python
from src.security.data_access import data_store

# Get a resource
resource = data_store.get_resource(
    resource_type="calls", 
    resource_id="call123"
)

# List resources
resources = data_store.list_resources(resource_type="calls")

# Create a resource
success = data_store.create_resource(
    resource_type="calls",
    resource_id="call123",
    resource={"caller_number": "1234567890"}
)
```

### Audit Logging

```python
from src.security.audit_log import audit_log, AuditLogEvent, AuditLogLevel

# Log a security event
audit_log.log_event(
    event_type=AuditLogEvent.DATA_ACCESS,
    level=AuditLogLevel.INFO,
    user="user123",
    resource_type="calls",
    resource_id="call123",
    message="User accessed call record"
)
```

### Intrusion Detection

```python
from src.security.intrusion_detection import intrusion_detection

# Record a login failure
intrusion_detection.record_login_failure(
    ip_address="192.168.1.1",
    user="user123",
    reason="Invalid password"
)

# Check if IP is blacklisted
is_blacklisted = intrusion_detection.is_blacklisted_ip("192.168.1.1")
```

## Development vs. Production

The security system supports different modes:

- **Development Mode**: Relaxes certain security restrictions for development
- **Production Mode**: Enforces all security measures

To enable development mode:

```python
import os
from src.security_config import security_config

# Set environment variable
os.environ["DEVELOPMENT_MODE"] = "true"

# Or set directly
security_config.development_mode = True
```

## Configuration

Security settings can be configured in the following ways:

1. **Configuration File**: `config/default.yml` and `config/production.yml`
2. **Environment Variables**: Override settings via environment variables
3. **Direct Configuration**: Update `security_config` object directly

## Best Practices

1. **Always set a strong JWT secret** in production
2. **Use the data access control system** for accessing data
3. **Log security events** using the audit log
4. **Follow the principle of least privilege** when assigning roles
5. **Encrypt sensitive data** using the encryption service