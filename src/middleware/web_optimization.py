"""
Web optimization middleware for the AI Call Secretary FastAPI application.
"""
import re
import gzip
import brotli
import hashlib
from typing import Dict, List, Set, Callable, Any, Awaitable, Optional
from pathlib import Path
from fastapi import Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..performance_config import get_performance_config


class OptimizedStaticFiles(StaticFiles):
    """Enhanced static files handler with optimization features."""
    
    def __init__(
        self,
        *args,
        compression_enabled: bool = True,
        cache_control_max_age: int = 86400,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.compression_enabled = compression_enabled
        self.cache_control_max_age = cache_control_max_age
        self.etag_cache: Dict[str, str] = {}
        self.precompressed_files: Dict[str, Dict[str, Path]] = {}
        
        # Initialize precompressed files if enabled
        if compression_enabled and self.directory is not None:
            self._precompress_files()
    
    async def __call__(self, scope, receive, send) -> None:
        """Handle static file requests with optimization."""
        if scope["type"] != "http":
            return await super().__call__(scope, receive, send)
        
        # Create response and request wrappers
        request = Request(scope, receive=receive)
        path = request.url.path
        
        # Check if this is a static file request
        if not self._is_static_file(path):
            return await super().__call__(scope, receive, send)
        
        # Modify response before sending
        original_send = send
        
        async def optimized_send(message):
            if message["type"] == "http.response.start":
                # Add cache control headers
                headers = dict(message.get("headers", []))
                headers_list = list(headers.items())
                
                # Add Cache-Control header if not present
                if b"cache-control" not in headers:
                    headers_list.append((
                        b"cache-control", 
                        f"public, max-age={self.cache_control_max_age}".encode()
                    ))
                
                # Add ETag header if not present
                if b"etag" not in headers and path in self.etag_cache:
                    headers_list.append((
                        b"etag", 
                        f'"{self.etag_cache[path]}"'.encode()
                    ))
                
                # Update headers in the message
                message["headers"] = headers_list
            
            await original_send(message)
        
        # Handle compressed files if supported
        if self.compression_enabled:
            accept_encoding = request.headers.get("accept-encoding", "")
            
            # Check for brotli support
            if "br" in accept_encoding and self._has_precompressed(path, "br"):
                # Modify scope to serve the brotli file
                scope["path"] = self._get_precompressed_path(path, "br")
                scope["headers"].append((b"accept-encoding", b"br"))
            
            # Check for gzip support
            elif "gzip" in accept_encoding and self._has_precompressed(path, "gzip"):
                # Modify scope to serve the gzip file
                scope["path"] = self._get_precompressed_path(path, "gzip")
                scope["headers"].append((b"accept-encoding", b"gzip"))
        
        # Handle If-None-Match header for 304 responses
        if_none_match = request.headers.get("if-none-match")
        if if_none_match and path in self.etag_cache:
            etag = f'"{self.etag_cache[path]}"'
            if etag == if_none_match:
                # Return 304 Not Modified
                await optimized_send({
                    "type": "http.response.start",
                    "status": 304,
                    "headers": [
                        (b"cache-control", f"public, max-age={self.cache_control_max_age}".encode()),
                        (b"etag", etag.encode()),
                    ]
                })
                await optimized_send({
                    "type": "http.response.body",
                    "body": b"",
                })
                return
        
        # Process the request with our modified send
        await super().__call__(scope, receive, optimized_send)
    
    def _is_static_file(self, path: str) -> bool:
        """Check if the path is a static file."""
        if not path.startswith(self.config.prefix):
            return False
        
        path = path[len(self.config.prefix):]
        full_path = self.directory / path
        
        return full_path.is_file()
    
    def _precompress_files(self) -> None:
        """Precompress static files and generate ETags."""
        if not self.directory:
            return
        
        # Get a list of all static files
        for file_path in self.directory.glob("**/*"):
            if not file_path.is_file():
                continue
            
            # Skip already compressed files
            if file_path.suffix in {".gz", ".br", ".zip", ".jpg", ".png", ".webp", ".gif"}:
                continue
            
            # Get the relative path
            rel_path = str(file_path.relative_to(self.directory))
            
            # Generate ETag for the file
            self.etag_cache[f"{self.config.prefix}/{rel_path}"] = self._generate_etag(file_path)
            
            # Generate compressed versions
            self._compress_file(file_path, rel_path)
    
    def _compress_file(self, file_path: Path, rel_path: str) -> None:
        """Compress a file using gzip and brotli."""
        # Read the file content
        try:
            with open(file_path, "rb") as f:
                content = f.read()
        except Exception:
            return
        
        # Skip small files
        if len(content) < 1024:  # 1KB
            return
        
        # Create the compressed paths
        gzip_path = file_path.with_suffix(f"{file_path.suffix}.gz")
        brotli_path = file_path.with_suffix(f"{file_path.suffix}.br")
        
        # Compress with gzip
        try:
            with open(gzip_path, "wb") as f:
                f.write(gzip.compress(content, compresslevel=9))
            
            # Store the compressed path
            key = f"{self.config.prefix}/{rel_path}"
            if key not in self.precompressed_files:
                self.precompressed_files[key] = {}
            self.precompressed_files[key]["gzip"] = gzip_path
        except Exception:
            pass
        
        # Compress with brotli
        try:
            with open(brotli_path, "wb") as f:
                f.write(brotli.compress(content, quality=11))
            
            # Store the compressed path
            key = f"{self.config.prefix}/{rel_path}"
            if key not in self.precompressed_files:
                self.precompressed_files[key] = {}
            self.precompressed_files[key]["br"] = brotli_path
        except Exception:
            pass
    
    def _has_precompressed(self, path: str, compression: str) -> bool:
        """Check if a precompressed version exists."""
        return path in self.precompressed_files and compression in self.precompressed_files[path]
    
    def _get_precompressed_path(self, path: str, compression: str) -> str:
        """Get the path to the precompressed file."""
        if not self._has_precompressed(path, compression):
            return path
        
        # Get the compressed file path relative to the directory
        compressed_path = self.precompressed_files[path][compression]
        rel_path = compressed_path.relative_to(self.directory)
        
        return f"{self.config.prefix}/{rel_path}"
    
    def _generate_etag(self, file_path: Path) -> str:
        """Generate ETag for a file based on its content."""
        try:
            stat = file_path.stat()
            etag_base = f"{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(etag_base.encode()).hexdigest()
        except Exception:
            return ""


class WebOptimizationMiddleware(BaseHTTPMiddleware):
    """Middleware for optimizing web responses."""
    
    def __init__(
        self, 
        app: ASGIApp,
        environment: str = "development"
    ):
        super().__init__(app)
        self.config = get_performance_config(environment).web
        self.html_minifier = None
        self.css_minifier = None
        self.js_minifier = None
        
        # Load minifiers if enabled
        if self.config.html_minify:
            try:
                from htmlmin import minify as html_minify
                self.html_minifier = html_minify
            except ImportError:
                pass
        
        if self.config.css_minify:
            try:
                from rcssmin import cssmin
                self.css_minifier = cssmin
            except ImportError:
                pass
        
        if self.config.js_minify:
            try:
                from rjsmin import jsmin
                self.js_minifier = jsmin
            except ImportError:
                pass
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request and optimize the response."""
        # Process the request
        response = await call_next(request)
        
        # Skip optimization for certain responses
        if (
            not response.headers.get("content-type") or
            response.status_code >= 400
        ):
            return response
        
        # Set cache control header
        if self.config.cache_control_max_age > 0:
            if "cache-control" not in response.headers:
                response.headers["cache-control"] = f"public, max-age={self.config.cache_control_max_age}"
        
        # Add HTTP/2 server push headers
        if self.config.http2_push and request.headers.get("accept").startswith("text/html"):
            push_headers = []
            for asset in self.config.push_assets:
                push_headers.append(f"<{asset}>; rel=preload; as={self._get_asset_type(asset)}")
            
            if push_headers:
                response.headers["link"] = ", ".join(push_headers)
        
        # Check if compression is supported
        accept_encoding = request.headers.get("accept-encoding", "")
        supports_brotli = "br" in accept_encoding
        supports_gzip = "gzip" in accept_encoding
        
        # Minify content if needed
        content_type = response.headers.get("content-type", "")
        
        if self.config.compression_enabled:
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Minify content based on content type
            if "text/html" in content_type and self.html_minifier:
                try:
                    body = self.html_minifier(
                        body.decode("utf-8"),
                        remove_comments=True,
                        remove_empty_space=True
                    ).encode("utf-8")
                except Exception:
                    pass
            elif "text/css" in content_type and self.css_minifier:
                try:
                    body = self.css_minifier(body.decode("utf-8")).encode("utf-8")
                except Exception:
                    pass
            elif "application/javascript" in content_type and self.js_minifier:
                try:
                    body = self.js_minifier(body.decode("utf-8")).encode("utf-8")
                except Exception:
                    pass
            
            # Compress content if enabled and supported
            if supports_brotli:
                try:
                    compressed_body = brotli.compress(body, quality=4)
                    if len(compressed_body) < len(body):
                        body = compressed_body
                        response.headers["content-encoding"] = "br"
                except Exception:
                    pass
            elif supports_gzip:
                try:
                    compressed_body = gzip.compress(body, compresslevel=6)
                    if len(compressed_body) < len(body):
                        body = compressed_body
                        response.headers["content-encoding"] = "gzip"
                except Exception:
                    pass
            
            # Update content length
            response.headers["content-length"] = str(len(body))
            
            # Create new response with the modified body
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        return response
    
    def _get_asset_type(self, asset: str) -> str:
        """Determine the asset type for preload hints."""
        if asset.endswith(".js"):
            return "script"
        elif asset.endswith(".css"):
            return "style"
        elif asset.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            return "image"
        elif asset.endswith((".woff", ".woff2", ".ttf", ".otf")):
            return "font"
        else:
            return "resource"


# Factory function for creating optimized static files handler
def create_optimized_static_files(
    directory: str,
    environment: str = "development"
) -> OptimizedStaticFiles:
    """Create an optimized static files handler."""
    config = get_performance_config(environment).web
    return OptimizedStaticFiles(
        directory=directory,
        compression_enabled=config.compression_enabled,
        cache_control_max_age=config.cache_control_max_age
    )


# Factory function for creating web optimization middleware
def create_web_optimization_middleware(
    app: ASGIApp, 
    environment: str = "development"
) -> WebOptimizationMiddleware:
    """Create a new web optimization middleware instance."""
    return WebOptimizationMiddleware(app, environment)