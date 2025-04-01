"""
Caching middleware for the AI Call Secretary FastAPI application.
"""
import time
import hashlib
import json
from typing import Dict, Optional, Callable, Any, Union, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis.asyncio as redis

from ..performance_config import get_performance_config


class MemoryCache:
    """Simple in-memory LRU cache implementation."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        
        # Check if the item has expired
        if time.time() > item["expires"]:
            del self.cache[key]
            return None
        
        # Update access time for LRU
        item["last_access"] = time.time()
        return item["value"]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        # If cache is full, remove least recently used item
        if len(self.cache) >= self.max_size:
            # Find the item with the oldest last_access time
            oldest_key = min(self.cache, key=lambda k: self.cache[k]["last_access"])
            del self.cache[oldest_key]
        
        ttl = ttl if ttl is not None else self.default_ttl
        self.cache[key] = {
            "value": value,
            "expires": time.time() + ttl,
            "last_access": time.time()
        }
    
    async def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        if key in self.cache:
            del self.cache[key]
    
    async def clear(self) -> None:
        """Clear the entire cache."""
        self.cache.clear()


class RedisCache:
    """Redis-based cache implementation."""
    
    def __init__(self, redis_url: str, default_ttl: int = 300):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        value = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        ttl = ttl if ttl is not None else self.default_ttl
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        await self.redis.delete(key)
    
    async def clear(self) -> None:
        """Clear the entire cache."""
        # Be careful! This clears all keys matching the pattern.
        # In a shared Redis instance, you might want to use a prefix.
        keys = await self.redis.keys("*")
        if keys:
            await self.redis.delete(*keys)


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for caching API responses."""
    
    def __init__(
        self, 
        app: ASGIApp,
        environment: str = "development",
        cache_instance: Optional[Union[MemoryCache, RedisCache]] = None
    ):
        super().__init__(app)
        self.config = get_performance_config(environment).cache
        
        # Skip initialization if caching is disabled
        if not self.config.enabled:
            self.cache = None
            return
        
        # Use provided cache instance or create a new one
        if cache_instance:
            self.cache = cache_instance
        elif self.config.backend == "redis" and self.config.redis_url:
            self.cache = RedisCache(
                redis_url=self.config.redis_url,
                default_ttl=self.config.default_ttl
            )
        else:
            self.cache = MemoryCache(
                max_size=self.config.max_size,
                default_ttl=self.config.default_ttl
            )
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request and apply caching logic."""
        # Skip caching if disabled or for non-GET requests
        if not self.config.enabled or request.method != "GET":
            return await call_next(request)
        
        # Skip caching for excluded paths
        for path in self.config.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Generate cache key from request details
        cache_key = self._generate_cache_key(request)
        
        # Try to get response from cache
        if self.cache:
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                # Recreate response from cached data
                response = Response(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers=dict(cached_response["headers"]),
                    media_type=cached_response["media_type"]
                )
                response.headers["X-Cache"] = "HIT"
                return response
        
        # Execute the request
        response = await call_next(request)
        
        # Cache the response if it's successful
        if self.cache and 200 <= response.status_code < 400:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Create a new response
            cached_data = {
                "content": response_body,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type
            }
            
            # Store in cache
            await self.cache.set(cache_key, cached_data)
            
            # Recreate response since we consumed the original
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            response.headers["X-Cache"] = "MISS"
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate a unique cache key for the request."""
        # Include path, query parameters, and auth status in key
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items())),
            str(bool(request.headers.get("Authorization")))
        ]
        
        # Get the appropriate prefix for this endpoint
        prefix = "default:"
        for path_type, path_prefix in self.config.prefixes.items():
            if path_type in request.url.path:
                prefix = path_prefix
                break
        
        # Create the key
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}{key_hash}"


# Factory function for creating cache middleware
def create_cache_middleware(
    app: ASGIApp, 
    environment: str = "development"
) -> CacheMiddleware:
    """Create a new cache middleware instance."""
    return CacheMiddleware(app, environment)