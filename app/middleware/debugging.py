"""Debugging middleware for PowerCV application."""

import logging
import os
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class DebuggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add debugging information to requests and responses."""
    
    def __init__(self, app, enable_debug: bool = False):
        super().__init__(app)
        self.enable_debug = enable_debug and os.getenv("ENVIRONMENT", "development") == "development"
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and add debugging information."""
        # Skip debugging in production
        if not self.enable_debug:
            return await call_next(request)
            
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request details
        logger.info(f"Request started: {request.method} {request.url.path}", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": request.client.host if request.client else None
        })
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Add debug headers to response
            response.headers["X-Request-ID"] = request_id
            if self.enable_debug:
                response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"
                response.headers["X-Debug-Enabled"] = "true"
            
            # Log response details
            logger.info(f"Request completed: {request.method} {request.url.path} - {response.status_code}", extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time_ms": processing_time
            })
            
            return response
            
        except Exception as e:
            # Calculate processing time for failed requests
            processing_time = (time.time() - start_time) * 1000
            
            # Log error details
            logger.error(f"Request failed: {request.method} {request.url.path}", extra={
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "processing_time_ms": processing_time
            }, exc_info=True)
            
            # Re-raise the exception
            raise


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor performance metrics."""
    
    def __init__(self, app, slow_request_threshold_ms: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold_ms = slow_request_threshold_ms
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Monitor request performance."""
        start_time = time.time()
        
        response = await call_next(request)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Log slow requests
        if processing_time > self.slow_request_threshold_ms:
            logger.warning(f"Slow request detected: {request.method} {request.url.path} took {processing_time:.2f}ms", extra={
                "method": request.method,
                "path": request.url.path,
                "processing_time_ms": processing_time,
                "threshold_ms": self.slow_request_threshold_ms
            })
        
        # Add performance header
        response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add HSTS header in production
        if not request.url.path.startswith("/docs"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request logging."""
    
    def __init__(self, app, log_body: bool = False, max_body_size: int = 1000):
        super().__init__(app)
        self.log_body = log_body
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Log detailed request information."""
        start_time = time.time()
        
        # Prepare log data
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Add request body if enabled (for debugging only)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8', errors='ignore')
                    if len(body_str) > self.max_body_size:
                        body_str = body_str[:self.max_body_size] + "... [truncated]"
                    log_data["body"] = body_str
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")
        
        logger.info(f"Incoming request: {request.method} {request.url.path}", extra=log_data)
        
        # Process request
        response = await call_next(request)
        
        # Log response
        processing_time = (time.time() - start_time) * 1000
        log_data.update({
            "status_code": response.status_code,
            "processing_time_ms": processing_time
        })
        
        logger.info(f"Response: {request.method} {request.url.path} - {response.status_code}", extra=log_data)
        
        return response


def setup_debugging_middleware(app, enable_debug: bool = False):
    """Setup all debugging middleware for the application."""
    # Get environment from environment variable
    environment = os.getenv("ENVIRONMENT", "development")
    is_development = environment == "development"
    
    # Add security headers (always enabled)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add performance monitoring (always enabled)
    app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold_ms=1000.0)
    
    # Add debugging middleware (development only)
    if is_development and enable_debug:
        app.add_middleware(RequestLoggingMiddleware, log_body=True, max_body_size=500)
        app.add_middleware(DebuggingMiddleware, enable_debug=True)
    else:
        app.add_middleware(DebuggingMiddleware, enable_debug=False)
