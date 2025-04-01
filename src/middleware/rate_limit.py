"""
Rate limiting middleware for the AI Call Secretary FastAPI application.
"""
import time
from typing import Dict, List, Tuple, Optional, Callable, Any, Awaitable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis.asyncio as redis

from ..performance_config import get_performance_config


class MemoryRateLimiter:
    """Simple in-memory rate limiter implementation."""
    
    def __init__(self, window_size: int = 60):
        # Structure: {ip: {endpoint: [(timestamp, count)]}}
        self.requests: Dict[str, Dict[str, List[Tuple[float, int]]]] = {}
        self.window_size = window_size
    
    async def is_rate_limited(
        self, key: str, endpoint: str, limit: int
    ) -> Tuple[bool, int, int]:
        """
        Check if a request is rate limited.
        
        Args:
            key: The client identifier (usually IP)
            endpoint: The API endpoint being accessed
            limit: The maximum number of requests allowed
            
        Returns:
            Tuple of (is_limited, current_count, reset_time)
        """
        now = time.time()
        
        # Initialize request tracking for this key and endpoint if needed
        if key not in self.requests:
            self.requests[key] = {}
        
        if endpoint not in self.requests[key]:
            self.requests[key][endpoint] = []
        
        # Remove expired entries
        cutoff = now - self.window_size
        self.requests[key][endpoint] = [
            r for r in self.requests[key][endpoint] if r[0] > cutoff
        ]
        
        # Count recent requests
        count = sum(r[1] for r in self.requests[key][endpoint])
        
        # Calculate when the rate limit will reset
        reset_at = (
            self.requests[key][endpoint][0][0] + self.window_size
            if self.requests[key][endpoint]
            else now + self.window_size
        )
        
        # Check if limit is exceeded
        if count >= limit:
            return True, count, int(reset_at)
        
        # Add the current request
        self.requests[key][endpoint].append((now, 1))
        
        return False, count + 1, int(reset_at)
    
    async def get_limits(
        self, key: str, endpoint: str
    ) -> Tuple[int, int, int]:
        """
        Get current request count and limits.
        
        Args:
            key: The client identifier (usually IP)
            endpoint: The API endpoint being accessed
            
        Returns:
            Tuple of (current_count, reset_time)
        """
        now = time.time()
        
        # If no data for this key/endpoint, return zeros
        if (
            key not in self.requests or
            endpoint not in self.requests[key]
        ):
            return 0, int(now + self.window_size)
        
        # Remove expired entries
        cutoff = now - self.window_size
        self.requests[key][endpoint] = [
            r for r in self.requests[key][endpoint] if r[0] > cutoff
        ]
        
        # Count recent requests
        count = sum(r[1] for r in self.requests[key][endpoint])
        
        # Calculate when the rate limit will reset
        reset_at = (
            self.requests[key][endpoint][0][0] + self.window_size
            if self.requests[key][endpoint]
            else now + self.window_size
        )
        
        return count, int(reset_at)


class RedisRateLimiter:
    """Redis-based rate limiter implementation."""
    
    def __init__(self, redis_url: str, window_size: int = 60):
        self.redis = redis.from_url(redis_url)
        self.window_size = window_size
    
    async def is_rate_limited(
        self, key: str, endpoint: str, limit: int
    ) -> Tuple[bool, int, int]:
        """
        Check if a request is rate limited.
        
        Args:
            key: The client identifier (usually IP)
            endpoint: The API endpoint being accessed
            limit: The maximum number of requests allowed
            
        Returns:
            Tuple of (is_limited, current_count, reset_time)
        """
        # Create a Redis key for this client and endpoint
        redis_key = f"rate_limit:{key}:{endpoint}"
        pipeline = self.redis.pipeline()
        
        now = int(time.time())
        window_start = now - self.window_size
        
        # Remove requests older than the window
        await pipeline.zremrangebyscore(redis_key, 0, window_start)
        
        # Add the current request
        await pipeline.zadd(redis_key, {str(now): now})
        
        # Get the current count
        await pipeline.zcard(redis_key)
        
        # Set TTL to ensure cleanup
        await pipeline.expire(redis_key, self.window_size * 2)
        
        # Execute all commands
        _, _, count, _ = await pipeline.execute()
        
        # Check if limit is exceeded
        if count > limit:
            # Get the reset time (when the oldest request expires)
            oldest = await self.redis.zrange(redis_key, 0, 0, withscores=True)
            reset_at = int(oldest[0][1]) + self.window_size if oldest else now + self.window_size
            return True, count, reset_at
        
        return False, count, now + self.window_size
    
    async def get_limits(
        self, key: str, endpoint: str
    ) -> Tuple[int, int]:
        """
        Get current request count and reset time.
        
        Args:
            key: The client identifier (usually IP)
            endpoint: The API endpoint being accessed
            
        Returns:
            Tuple of (current_count, reset_time)
        """
        # Create a Redis key for this client and endpoint
        redis_key = f"rate_limit:{key}:{endpoint}"
        
        now = int(time.time())
        window_start = now - self.window_size
        
        # Remove requests older than the window
        await self.redis.zremrangebyscore(redis_key, 0, window_start)
        
        # Get the current count
        count = await self.redis.zcard(redis_key)
        
        # Get the reset time (when the oldest request expires)
        oldest = await self.redis.zrange(redis_key, 0, 0, withscores=True)
        reset_at = int(oldest[0][1]) + self.window_size if oldest else now + self.window_size
        
        return count, reset_at


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(
        self, 
        app: ASGIApp,
        environment: str = "development",
        limiter_instance: Optional[Any] = None
    ):
        super().__init__(app)
        self.config = get_performance_config(environment).rate_limit
        
        # Skip initialization if rate limiting is disabled
        if not self.config.enabled:
            self.limiter = None
            return
        
        # Use provided limiter instance or create a new one
        if limiter_instance:
            self.limiter = limiter_instance
        else:
            cache_config = get_performance_config(environment).cache
            if (
                cache_config.backend == "redis" and 
                cache_config.redis_url and
                cache_config.enabled
            ):
                self.limiter = RedisRateLimiter(
                    redis_url=cache_config.redis_url,
                    window_size=self.config.window_size
                )
            else:
                self.limiter = MemoryRateLimiter(
                    window_size=self.config.window_size
                )
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request and apply rate limiting logic."""
        # Skip rate limiting if disabled
        if not self.config.enabled or not self.limiter:
            return await call_next(request)
        
        # Determine the client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Normalize the endpoint to match our configuration
        endpoint = request.url.path
        for path in self.config.endpoint_rates.keys():
            if endpoint.startswith(path):
                endpoint = path
                break
        
        # Determine the rate limit for this endpoint
        limit = self.config.endpoint_rates.get(endpoint, self.config.default_rate)
        
        # Increase limit for authenticated users
        if request.headers.get("Authorization"):
            limit = int(limit * self.config.auth_multiplier)
        
        # Check if the request is rate limited
        is_limited, current, reset_at = await self.limiter.is_rate_limited(
            client_ip, endpoint, limit
        )
        
        # If rate limited, return 429 Too Many Requests
        if is_limited:
            remaining = 0
            retry_after = reset_at - int(time.time())
            
            # Return a 429 response
            return Response(
                content={"detail": "Rate limit exceeded"},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(retry_after)
                },
                media_type="application/json"
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = max(0, limit - current)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        
        return response


# Factory function for creating rate limit middleware
def create_rate_limit_middleware(
    app: ASGIApp, 
    environment: str = "development"
) -> RateLimitMiddleware:
    """Create a new rate limit middleware instance."""
    return RateLimitMiddleware(app, environment)