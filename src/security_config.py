"""
Security configuration for the AI Call Secretary system.
This module contains all security-related settings, including authentication, authorization,
input validation, CORS settings, content security policy, and more.
"""
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator, SecretStr


class JwtConfig(BaseModel):
    """JWT configuration settings."""
    secret: SecretStr = Field(
        SecretStr(""),
        description="Secret key for JWT token signing and validation"
    )
    algorithm: str = Field("HS256", description="Algorithm used for JWT token signing")
    access_token_expire_minutes: int = Field(
        1440,  # 24 hours
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        30,
        description="Refresh token expiration time in days"
    )
    token_url: str = Field("/token", description="URL for token endpoint")
    refresh_url: str = Field("/token/refresh", description="URL for token refresh endpoint")
    
    @validator("secret", pre=True)
    def set_default_secret(cls, v):
        """Set a secure default secret when none is provided."""
        if not v:
            # In production, this will come from environment variable
            return SecretStr(os.environ.get("JWT_SECRET", "your-secret-key-replace-in-production"))
        return v


class PasswordConfig(BaseModel):
    """Password policy configuration."""
    min_length: int = Field(10, description="Minimum password length")
    require_uppercase: bool = Field(True, description="Require uppercase characters")
    require_lowercase: bool = Field(True, description="Require lowercase characters")
    require_digits: bool = Field(True, description="Require numeric digits")
    require_special: bool = Field(True, description="Require special characters")
    special_chars: str = Field("!@#$%^&*()-_=+[]{}|;:,.<>?", description="Special characters")
    max_failed_attempts: int = Field(5, description="Maximum failed login attempts before lockout")
    lockout_minutes: int = Field(30, description="Account lockout duration in minutes")
    password_history: int = Field(5, description="Number of previous passwords to remember")
    password_expiry_days: int = Field(90, description="Password expiration in days")


class CorsConfig(BaseModel):
    """CORS configuration."""
    allowed_origins: List[str] = Field(
        ["http://localhost:8080", "http://localhost:3000", "https://example.com"],
        description="Allowed origins for CORS"
    )
    allow_credentials: bool = Field(True, description="Allow credentials for CORS")
    allowed_methods: List[str] = Field(["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"], description="Allowed methods")
    allowed_headers: List[str] = Field(["*"], description="Allowed headers")
    expose_headers: List[str] = Field(
        ["Content-Length", "Content-Type", "X-Request-ID"],
        description="Headers exposed to the browser"
    )
    max_age: int = Field(600, description="Maximum cache age for preflight requests in seconds")


class CsrfConfig(BaseModel):
    """CSRF protection configuration."""
    enabled: bool = Field(True, description="Enable CSRF protection")
    cookie_name: str = Field("csrf_token", description="CSRF cookie name")
    header_name: str = Field("X-CSRF-Token", description="CSRF header name")
    cookie_secure: bool = Field(True, description="Only send cookie over HTTPS")
    cookie_http_only: bool = Field(True, description="Prevent JavaScript access to CSRF cookie")
    cookie_same_site: str = Field("lax", description="SameSite cookie policy")
    expiry_hours: int = Field(24, description="CSRF token expiration in hours")


class ContentSecurityPolicyConfig(BaseModel):
    """Content Security Policy (CSP) configuration."""
    enabled: bool = Field(True, description="Enable Content Security Policy")
    default_src: List[str] = Field(["'self'"], description="Default source directive")
    script_src: List[str] = Field(["'self'"], description="Script source directive")
    style_src: List[str] = Field(["'self'"], description="Style source directive")
    img_src: List[str] = Field(["'self'", "data:"], description="Image source directive")
    font_src: List[str] = Field(["'self'"], description="Font source directive")
    connect_src: List[str] = Field(["'self'"], description="Connection source directive")
    frame_src: List[str] = Field(["'none'"], description="Frame source directive")
    report_uri: Optional[str] = Field(None, description="URI for CSP violation reporting")
    report_only: bool = Field(False, description="Report only mode (no enforcing)")


class SecureHeadersConfig(BaseModel):
    """Secure HTTP headers configuration."""
    strict_transport_security: bool = Field(True, description="Enable HSTS")
    hsts_max_age: int = Field(31536000, description="HSTS max age in seconds")
    hsts_include_subdomains: bool = Field(True, description="Include subdomains in HSTS")
    hsts_preload: bool = Field(False, description="Preload HSTS")
    x_frame_options: str = Field("DENY", description="X-Frame-Options header")
    x_content_type_options: bool = Field(True, description="Enable X-Content-Type-Options")
    referrer_policy: str = Field("strict-origin-when-cross-origin", description="Referrer Policy")
    permissions_policy: Dict[str, str] = Field(
        {
            "geolocation": "'self'",
            "microphone": "'self'",
            "camera": "'self'",
            "payment": "'self'",
            "usb": "'none'",
        },
        description="Permissions Policy directives"
    )


class InputValidationConfig(BaseModel):
    """Input validation and sanitization configuration."""
    enabled: bool = Field(True, description="Enable input validation and sanitization")
    max_content_length: int = Field(10 * 1024 * 1024, description="Maximum allowed content length in bytes")
    allowed_content_types: List[str] = Field(
        ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"],
        description="Allowed content types"
    )
    sanitize_html: bool = Field(True, description="Sanitize HTML input")
    validate_utf8: bool = Field(True, description="Validate UTF-8 encoding")
    file_upload_limits: Dict[str, int] = Field(
        {
            "max_files": 5,
            "max_file_size": 5 * 1024 * 1024,  # 5 MB
            "allowed_extensions": ["jpg", "jpeg", "png", "pdf", "txt", "csv"]
        },
        description="File upload limits"
    )


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = Field(True, description="Enable rate limiting")
    default_rate: int = Field(100, description="Default rate limit per minute")
    login_rate: int = Field(5, description="Login attempt rate limit per minute")
    token_rate: int = Field(10, description="Token request rate limit per minute")
    api_rates: Dict[str, int] = Field(
        {
            "/api/v1/calls": 60,
            "/api/v1/actions": 30,
            "/api/v1/messages": 30,
            "/api/v1/appointments": 30,
        },
        description="API endpoint specific rate limits per minute"
    )
    by_ip: bool = Field(True, description="Enable rate limiting by IP address")
    by_user: bool = Field(True, description="Enable rate limiting by user ID")
    storage: str = Field("memory", description="Rate limit storage backend (memory or redis)")
    redis_url: Optional[str] = Field(None, description="Redis URL for rate limit storage")
    response_code: int = Field(429, description="HTTP response code when rate limited")


class SessionConfig(BaseModel):
    """Session configuration."""
    enabled: bool = Field(True, description="Enable session management")
    cookie_name: str = Field("session", description="Session cookie name")
    cookie_secure: bool = Field(True, description="Only send cookie over HTTPS")
    cookie_http_only: bool = Field(True, description="Prevent JavaScript access to session cookie")
    cookie_same_site: str = Field("lax", description="SameSite cookie policy")
    expiry_hours: int = Field(24, description="Session expiration in hours")
    storage: str = Field("memory", description="Session storage backend (memory or redis)")
    redis_url: Optional[str] = Field(None, description="Redis URL for session storage")
    rotate_on_login: bool = Field(True, description="Rotate session on login")
    regenerate_every: int = Field(60, description="Regenerate session every N minutes")


class TlsConfig(BaseModel):
    """TLS configuration."""
    enabled: bool = Field(True, description="Enable TLS")
    min_version: str = Field("TLSv1.2", description="Minimum TLS version")
    prefer_server_cipher_suites: bool = Field(True, description="Prefer server cipher suites")
    cipher_suites: List[str] = Field(
        [
            "TLS_AES_128_GCM_SHA256",
            "TLS_AES_256_GCM_SHA384",
            "TLS_CHACHA20_POLY1305_SHA256",
            "ECDHE-RSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES256-GCM-SHA384",
            "ECDHE-RSA-CHACHA20-POLY1305",
        ],
        description="Allowed cipher suites"
    )
    cert_file: Optional[str] = Field(None, description="Certificate file path")
    key_file: Optional[str] = Field(None, description="Private key file path")


class LoggingSecurityConfig(BaseModel):
    """Security-related logging configuration."""
    log_security_events: bool = Field(True, description="Log security events")
    log_login_attempts: bool = Field(True, description="Log login attempts")
    log_authentication_failures: bool = Field(True, description="Log authentication failures")
    log_authorization_failures: bool = Field(True, description="Log authorization failures")
    log_rate_limit_hits: bool = Field(True, description="Log rate limit hits")
    log_input_validation_failures: bool = Field(True, description="Log input validation failures")
    log_suspicious_activities: bool = Field(True, description="Log suspicious activities")
    mask_sensitive_data: bool = Field(True, description="Mask sensitive data in logs")
    sensitive_fields: List[str] = Field(
        ["password", "token", "secret", "credit_card", "ssn", "social_security"],
        description="Sensitive fields to mask in logs"
    )


class SecurityConfig(BaseModel):
    """Main security configuration container."""
    # Authentication
    jwt: JwtConfig = Field(default_factory=JwtConfig, description="JWT configuration")
    password: PasswordConfig = Field(default_factory=PasswordConfig, description="Password policy")
    
    # Request protection
    cors: CorsConfig = Field(default_factory=CorsConfig, description="CORS configuration")
    csrf: CsrfConfig = Field(default_factory=CsrfConfig, description="CSRF protection")
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig, description="Rate limiting")
    input_validation: InputValidationConfig = Field(
        default_factory=InputValidationConfig,
        description="Input validation"
    )
    
    # Response protection
    content_security: ContentSecurityPolicyConfig = Field(
        default_factory=ContentSecurityPolicyConfig,
        description="Content Security Policy"
    )
    secure_headers: SecureHeadersConfig = Field(
        default_factory=SecureHeadersConfig,
        description="Secure HTTP headers"
    )
    
    # Session management
    session: SessionConfig = Field(default_factory=SessionConfig, description="Session management")
    
    # Transport security
    tls: TlsConfig = Field(default_factory=TlsConfig, description="TLS configuration")
    
    # Logging and monitoring
    logging: LoggingSecurityConfig = Field(
        default_factory=LoggingSecurityConfig,
        description="Security logging"
    )
    
    # Mode
    development_mode: bool = Field(False, description="Development mode (relaxes certain security settings)")
    
    def get_environment_config(self) -> 'SecurityConfig':
        """
        Load configuration from environment variables, overriding defaults.
        Environment variables take precedence over configuration file.
        """
        # Create a copy of the current config
        config = self.copy(deep=True)
        
        # Override with environment variables
        if os.environ.get("JWT_SECRET"):
            config.jwt.secret = SecretStr(os.environ.get("JWT_SECRET"))
        
        if os.environ.get("DEVELOPMENT_MODE") in ["1", "true", "True", "yes", "Yes"]:
            config.development_mode = True
            # Relax security settings for development
            if config.development_mode:
                config.cors.allowed_origins = ["*"]
                config.tls.enabled = False
                config.csrf.cookie_secure = False
                config.session.cookie_secure = False
                config.secure_headers.strict_transport_security = False
        
        return config


# Create default configuration
default_security_config = SecurityConfig()

# Load environment-specific configuration
security_config = default_security_config.get_environment_config()