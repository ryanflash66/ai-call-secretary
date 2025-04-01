"""
API application for AI Call Secretary.
Configures the FastAPI application with middleware, routes, and error handlers.
"""
import os
import logging
import yaml
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.security_config import security_config
from src.middleware.security import (
    AuthMiddleware,
    CsrfMiddleware,
    SecureHeadersMiddleware,
    InputValidationMiddleware,
    SecurityLoggingMiddleware
)
from src.middleware.cache import CacheMiddleware
from src.middleware.rate_limit import RateLimitMiddleware
from src.middleware.performance import PerformanceMonitorMiddleware
from src.middleware.web_optimization import WebOptimizationMiddleware
from src.api.routes import router as main_router
from src.api.security_routes import router as security_router

# Initialize logging
logger = logging.getLogger(__name__)

# Load configuration
config_path = os.environ.get("CONFIG_PATH", "config/default.yml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Create FastAPI application
app = FastAPI(
    title="AI Call Secretary API",
    description="API for the AI Call Secretary system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.cors.allowed_origins,
    allow_credentials=security_config.cors.allow_credentials,
    allow_methods=security_config.cors.allowed_methods,
    allow_headers=security_config.cors.allowed_headers,
    expose_headers=security_config.cors.expose_headers,
    max_age=security_config.cors.max_age,
)

# Add security middleware
if security_config.csrf.enabled:
    app.add_middleware(CsrfMiddleware)

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

app.add_middleware(SecureHeadersMiddleware)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(SecurityLoggingMiddleware)

# Add performance middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CacheMiddleware)
app.add_middleware(PerformanceMonitorMiddleware)
app.add_middleware(WebOptimizationMiddleware)

# Add routes
app.include_router(main_router)
app.include_router(security_router)

# Add exception handlers
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc: Exception) -> Response:
    """Handle 404 errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "detail": "The requested resource was not found."},
    )


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def server_error_handler(request: Request, exc: Exception) -> Response:
    """Handle 500 errors."""
    # Log the error
    logger.error(f"Internal server error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred."},
    )


# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Handle application startup."""
    logger.info("API server starting")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Handle application shutdown."""
    logger.info("API server shutting down")