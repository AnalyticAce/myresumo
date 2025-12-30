"""Rate limiting middleware for PowerCV API.

This module provides rate limiting functionality to protect against
abuse and ensure fair usage of API resources.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
from typing import Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Global limiter instance
limiter = Limiter(key_func=get_remote_address)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Remove server header for security
        response.headers.pop("server", None)
        
        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Limit request size to prevent DoS attacks."""
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content length for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    if int(content_length) > self.max_size:
                        logger.warning(
                            f"Request size exceeded: {content_length} bytes",
                            extra={
                                "client_ip": request.client.host,
                                "method": request.method,
                                "path": request.url.path,
                                "content_length": content_length
                            }
                        )
                        return Response(
                            content=json.dumps({
                                "error": {
                                    "message": "Request too large",
                                    "code": "REQUEST_TOO_LARGE"
                                }
                            }),
                            status_code=413,
                            media_type="application/json"
                        )
                except ValueError:
                    # Invalid content-length header
                    pass
        
        return await call_next(request)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Optional IP whitelist for admin endpoints."""
    
    def __init__(self, app, whitelist: list = None):
        super().__init__(app)
        self.whitelist = whitelist or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only check for admin endpoints
        if request.url.path.startswith("/admin") or request.url.path.startswith("/api/admin"):
            client_ip = self._get_client_ip(request)
            if self.whitelist and client_ip not in self.whitelist:
                logger.warning(
                    f"Blocked access from non-whitelisted IP: {client_ip}",
                    extra={"client_ip": client_ip, "path": request.url.path}
                )
                return Response(
                    content=json.dumps({
                        "error": {
                            "message": "Access denied",
                            "code": "ACCESS_DENIED"
                        }
                    }),
                    status_code=403,
                    media_type="application/json"
                )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host


class CORSMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware with security considerations."""
    
    def __init__(
        self, 
        app, 
        allowed_origins: list = None,
        allowed_methods: list = None,
        allowed_headers: list = None,
        allow_credentials: bool = True,
        max_age: int = 86400  # 24 hours
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3000", "http://localhost:8080"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allowed_headers = allowed_headers or [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-API-Key"
        ]
        self.allow_credentials = allow_credentials
        self.max_age = max_age
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Handle preflight requests
        if request.method == "OPTIONS":
            origin = request.headers.get("origin")
            
            if origin and self._is_origin_allowed(origin):
                response = Response()
                self._set_cors_headers(response, origin)
                return response
        
        response = await call_next(request)
        
        # Add CORS headers to response
        origin = request.headers.get("origin")
        if origin and self._is_origin_allowed(origin):
            self._set_cors_headers(response, origin)
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        # Allow localhost and exact matches
        if origin in self.allowed_origins:
            return True
        
        # Allow subdomains of allowed origins
        for allowed_origin in self.allowed_origins:
            if allowed_origin.startswith("http://localhost") or allowed_origin.startswith("https://localhost"):
                if origin.startswith("http://localhost") or origin.startswith("https://localhost"):
                    return True
        
        return False
    
    def _set_cors_headers(self, response: Response, origin: str):
        """Set CORS headers on response."""
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
        response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        # Expose headers that might be useful for frontend
        response.headers["Access-Control-Expose-Headers"] = "X-Request-ID, X-Response-Time"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced request logging middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Generate request ID for tracing
        request_id = f"{int(start_time * 1000000)}-{hash(str(request.url)) % 10000:04d}"
        request.state.request_id = request_id
        
        # Log request start
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log request completion
            logger.info(
                f"Request completed: {response.status_code} ({process_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": process_time,
                    "method": request.method,
                    "path": request.url.path
                }
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{process_time:.3f}s"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed: {str(e)} ({process_time:.3f}s)",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "response_time": process_time,
                    "method": request.method,
                    "path": request.url.path
                }
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host


# Rate limit decorators for specific endpoints
def rate_limit_auth():
    """Rate limit for authentication endpoints."""
    return limiter.limit("5/minute")


def rate_limit_api():
    """Rate limit for general API endpoints."""
    return limiter.limit("100/minute")


def rate_limit_ai():
    """Rate limit for AI processing endpoints."""
    return limiter.limit("10/minute")


def rate_limit_upload():
    """Rate limit for file upload endpoints."""
    return limiter.limit("20/hour")


# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    retry_after = getattr(exc, 'retry_after', None)
    
    logger.warning(
        f"Rate limit exceeded for {request.client.host}",
        extra={
            "client_ip": request.client.host,
            "path": request.url.path,
            "method": request.method,
            "retry_after": retry_after
        }
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "message": "Rate limit exceeded. Please try again later.",
                "code": "RATE_LIMIT_EXCEEDED",
                "type": "RateLimitError",
                "details": {"retry_after": retry_after}
            }
        },
        headers={"Retry-After": str(retry_after)} if retry_after else None
    )