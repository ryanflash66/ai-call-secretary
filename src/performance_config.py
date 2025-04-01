"""
Performance optimization configuration for the AI Call Secretary.
This module configures caching, rate limiting, and performance settings.
"""
import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class CacheConfig(BaseModel):
    """Cache configuration settings."""
    # Enable/disable caching
    enabled: bool = True
    
    # Default TTL in seconds for cached items
    default_ttl: int = 300  # 5 minutes
    
    # Cache backend (memory, redis)
    backend: str = "memory"
    
    # Redis connection string (if using redis backend)
    redis_url: Optional[str] = None
    
    # Maximum cache size for memory cache (items)
    max_size: int = 1000
    
    # Cache key prefixes for different data types
    prefixes: Dict[str, str] = {
        "call": "call:",
        "message": "msg:",
        "appointment": "appt:",
        "status": "status:",
        "user": "user:"
    }
    
    # Endpoints to exclude from caching
    exclude_paths: List[str] = [
        "/token",
        "/webhooks"
    ]


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    # Enable/disable rate limiting
    enabled: bool = True
    
    # Default rate limit (requests per minute)
    default_rate: int = 60
    
    # Rate limits for specific endpoints
    endpoint_rates: Dict[str, int] = {
        "/token": 5,         # 5 login attempts per minute
        "/calls": 30,        # 30 call operations per minute
        "/messages": 60,     # 60 message operations per minute
        "/appointments": 30, # 30 appointment operations per minute
        "/actions": 20       # 20 action executions per minute
    }
    
    # Increase limit factor for authenticated users
    auth_multiplier: float = 2.0
    
    # Window size in seconds
    window_size: int = 60


class DatabaseOptimizationConfig(BaseModel):
    """Database optimization configuration."""
    # Enable/disable connection pooling
    pooling_enabled: bool = True
    
    # Minimum pool size
    min_pool_size: int = 5
    
    # Maximum pool size
    max_pool_size: int = 20
    
    # Connection timeout in seconds
    connection_timeout: float = 5.0
    
    # Maximum query execution time (seconds)
    max_query_time: float = 10.0
    
    # Enable query result caching
    query_cache_enabled: bool = True
    
    # Query cache TTL in seconds
    query_cache_ttl: int = 60


class LlmOptimizationConfig(BaseModel):
    """LLM optimization configuration."""
    # Enable response caching for common queries
    cache_enabled: bool = True
    
    # Cache TTL for LLM responses in seconds
    cache_ttl: int = 3600  # 1 hour
    
    # Maximum tokens per request
    max_tokens: int = 1024
    
    # Timeout for LLM requests in seconds
    timeout: float = 30.0
    
    # Enable batching of multiple LLM requests
    batching_enabled: bool = True
    
    # Maximum batch size
    max_batch_size: int = 5
    
    # Maximum waiting time for batch completion in seconds
    max_batch_wait: float = 0.5


class WebOptimizationConfig(BaseModel):
    """Web interface optimization configuration."""
    # Enable static asset compression
    compression_enabled: bool = True
    
    # Enable HTML minification
    html_minify: bool = True
    
    # Enable CSS minification
    css_minify: bool = True
    
    # Enable JS minification
    js_minify: bool = True
    
    # Enable HTTP/2 server push
    http2_push: bool = True
    
    # Assets to push with HTTP/2
    push_assets: List[str] = [
        "/js/main.js",
        "/css/style.css",
        "/css/charts.css"
    ]
    
    # Cache control max-age in seconds
    cache_control_max_age: int = 86400  # 24 hours
    
    # Enable lazy loading of images
    lazy_loading: bool = True


class PerformanceConfig(BaseModel):
    """Main performance configuration container."""
    # Cache configuration
    cache: CacheConfig = CacheConfig()
    
    # Rate limiting configuration
    rate_limit: RateLimitConfig = RateLimitConfig()
    
    # Database optimization configuration
    database: DatabaseOptimizationConfig = DatabaseOptimizationConfig()
    
    # LLM optimization configuration
    llm: LlmOptimizationConfig = LlmOptimizationConfig()
    
    # Web optimization configuration
    web: WebOptimizationConfig = WebOptimizationConfig()
    
    # Enable/disable performance monitoring
    monitoring_enabled: bool = True
    
    # Performance log level (debug, info, warning, error)
    log_level: str = "info"
    
    # Execution time threshold for performance alerts (ms)
    slow_execution_threshold: int = 500
    
    # Maximum memory usage in MB before garbage collection is forced
    memory_threshold: int = 512
    
    # Enable adaptive performance tuning
    adaptive_tuning: bool = True


# Create default configuration
default_config = PerformanceConfig()

# Create production configuration
production_config = PerformanceConfig(
    cache=CacheConfig(
        backend="redis",
        redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        default_ttl=600  # 10 minutes
    ),
    rate_limit=RateLimitConfig(
        default_rate=100,
        window_size=120  # 2 minutes
    ),
    database=DatabaseOptimizationConfig(
        max_pool_size=50,
        query_cache_ttl=120
    ),
    llm=LlmOptimizationConfig(
        cache_ttl=7200,  # 2 hours
        max_tokens=2048
    ),
    web=WebOptimizationConfig(
        cache_control_max_age=604800  # 7 days
    ),
    memory_threshold=1024  # 1 GB
)


def get_performance_config(environment: str = "development") -> PerformanceConfig:
    """
    Get the performance configuration for the specified environment.
    
    Args:
        environment: The environment to get the configuration for
            (development, production, test)
            
    Returns:
        The performance configuration for the specified environment
    """
    if environment == "production":
        return production_config
    elif environment == "test":
        # Use default config with caching disabled for tests
        test_config = default_config.copy()
        test_config.cache.enabled = False
        test_config.monitoring_enabled = False
        return test_config
    else:
        return default_config