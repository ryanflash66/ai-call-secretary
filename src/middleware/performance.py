"""
Performance monitoring middleware for the AI Call Secretary FastAPI application.
"""
import time
import logging
import tracemalloc
import functools
import asyncio
from typing import Callable, Dict, Any, List, Optional, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..performance_config import get_performance_config


# Set up logging
logger = logging.getLogger("ai_call_secretary.performance")


class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring request performance."""
    
    def __init__(
        self, 
        app: ASGIApp,
        environment: str = "development"
    ):
        super().__init__(app)
        self.config = get_performance_config(environment)
        
        # Set up logging according to configuration
        if self.config.monitoring_enabled:
            logger.setLevel(getattr(logging, self.config.log_level.upper()))
            
            # Enable memory tracking if monitoring is enabled
            if not tracemalloc.is_tracing():
                tracemalloc.start()
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request and gather performance metrics."""
        # Skip monitoring if disabled
        if not self.config.monitoring_enabled:
            return await call_next(request)
        
        # Start performance tracking
        start_time = time.time()
        mem_snapshot = tracemalloc.take_snapshot() if tracemalloc.is_tracing() else None
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000  # ms
            
            # Get memory usage
            mem_current = tracemalloc.get_traced_memory()[0] / (1024 * 1024) if tracemalloc.is_tracing() else 0
            mem_diff = 0
            if mem_snapshot:
                current_snapshot = tracemalloc.take_snapshot()
                mem_diff = self._calculate_memory_diff(mem_snapshot, current_snapshot)
            
            # Add performance headers
            response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"
            
            # Log performance data
            self._log_performance(request, response, execution_time, mem_current, mem_diff)
            
            # Check for slow execution
            if execution_time > self.config.slow_execution_threshold:
                self._log_slow_execution(request, execution_time)
            
            # Check for memory usage threshold
            if mem_current > self.config.memory_threshold:
                self._log_memory_usage(mem_current)
                
                # Force garbage collection if adaptive tuning is enabled
                if self.config.adaptive_tuning:
                    self._force_garbage_collection()
            
            return response
        except Exception as e:
            # Log errors but don't stop processing
            logger.error(f"Performance monitoring error: {e}")
            raise
    
    def _log_performance(
        self,
        request: Request,
        response: Response,
        execution_time: float,
        memory_usage: float,
        memory_diff: float
    ) -> None:
        """Log performance data."""
        if logger.level <= logging.INFO:
            logger.info(
                f"Request: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Time: {execution_time:.2f}ms | "
                f"Memory: {memory_usage:.2f}MB (Δ{memory_diff:+.2f}MB)"
            )
    
    def _log_slow_execution(self, request: Request, execution_time: float) -> None:
        """Log slow execution warnings."""
        logger.warning(
            f"SLOW EXECUTION: {request.method} {request.url.path} | "
            f"Time: {execution_time:.2f}ms | "
            f"Threshold: {self.config.slow_execution_threshold}ms"
        )
    
    def _log_memory_usage(self, memory_usage: float) -> None:
        """Log high memory usage warnings."""
        logger.warning(
            f"HIGH MEMORY USAGE: {memory_usage:.2f}MB | "
            f"Threshold: {self.config.memory_threshold}MB"
        )
    
    def _calculate_memory_diff(self, old_snapshot, new_snapshot) -> float:
        """Calculate memory difference between snapshots in MB."""
        stats = new_snapshot.compare_to(old_snapshot, 'lineno')
        return sum(stat.size_diff for stat in stats) / (1024 * 1024)
    
    def _force_garbage_collection(self) -> None:
        """Force Python garbage collection."""
        import gc
        gc.collect()
        logger.info("Forced garbage collection")


# Function decorator for performance monitoring
def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor performance of individual functions."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        config = get_performance_config()
        
        # Skip monitoring if disabled
        if not config.monitoring_enabled:
            return await func(*args, **kwargs)
        
        # Start performance tracking
        start_time = time.time()
        mem_before = tracemalloc.get_traced_memory()[0] if tracemalloc.is_tracing() else 0
        
        try:
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000  # ms
            
            # Get memory usage
            mem_after = tracemalloc.get_traced_memory()[0] if tracemalloc.is_tracing() else 0
            mem_diff = (mem_after - mem_before) / (1024 * 1024)  # MB
            
            # Log performance data
            if logger.level <= logging.DEBUG:
                logger.debug(
                    f"Function: {func.__module__}.{func.__name__} | "
                    f"Time: {execution_time:.2f}ms | "
                    f"Memory: Δ{mem_diff:+.2f}MB"
                )
            
            # Check for slow execution
            if execution_time > config.slow_execution_threshold:
                logger.warning(
                    f"SLOW FUNCTION: {func.__module__}.{func.__name__} | "
                    f"Time: {execution_time:.2f}ms | "
                    f"Threshold: {config.slow_execution_threshold}ms"
                )
            
            return result
        except Exception as e:
            # Log errors but don't stop processing
            logger.error(f"Function monitoring error in {func.__name__}: {e}")
            raise
    
    return wrapper


# Async function to periodically check system performance
async def monitor_system_performance(interval: int = 300) -> None:
    """
    Periodically check system performance and log metrics.
    
    Args:
        interval: Interval between checks in seconds (default: 5 minutes)
    """
    config = get_performance_config()
    
    while True:
        try:
            # Skip monitoring if disabled
            if not config.monitoring_enabled:
                await asyncio.sleep(interval)
                continue
            
            # Get memory usage
            mem_current, mem_peak = tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)
            mem_current_mb = mem_current / (1024 * 1024)
            mem_peak_mb = mem_peak / (1024 * 1024)
            
            # Log system metrics
            logger.info(
                f"SYSTEM METRICS | "
                f"Memory Current: {mem_current_mb:.2f}MB | "
                f"Memory Peak: {mem_peak_mb:.2f}MB"
            )
            
            # Check for memory threshold
            if mem_current_mb > config.memory_threshold * 0.8:  # 80% of threshold as early warning
                logger.warning(
                    f"APPROACHING MEMORY THRESHOLD: {mem_current_mb:.2f}MB | "
                    f"Threshold: {config.memory_threshold}MB"
                )
                
                # Force garbage collection if adaptive tuning is enabled and close to threshold
                if config.adaptive_tuning and mem_current_mb > config.memory_threshold * 0.9:
                    import gc
                    gc.collect()
                    logger.info("Forced garbage collection from system monitor")
            
            await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"System monitoring error: {e}")
            await asyncio.sleep(interval)


# Factory function for creating performance monitoring middleware
def create_performance_middleware(
    app: ASGIApp, 
    environment: str = "development"
) -> PerformanceMonitorMiddleware:
    """Create a new performance monitoring middleware instance."""
    return PerformanceMonitorMiddleware(app, environment)