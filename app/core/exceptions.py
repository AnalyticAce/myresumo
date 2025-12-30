"""Centralized exception handling for PowerCV application.

This module defines custom exceptions and global exception handlers
to provide consistent error responses across the application.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PowerCVException(Exception):
    """Base exception for PowerCV application errors.
    
    Attributes:
        message (str): Human-readable error message
        status_code (int): HTTP status code (default: 500)
        error_code (str): Application-specific error code
        details (Dict[str, Any]): Additional error details
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(PowerCVException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details={"field": field, **(details or {})}
        )


class AuthenticationError(PowerCVException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(PowerCVException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )


class ResourceNotFoundError(PowerCVException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class AIServiceError(PowerCVException):
    """Raised when AI service operations fail."""
    
    def __init__(self, message: str, service_name: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="AI_SERVICE_ERROR",
            details={"service": service_name, **(details or {})}
        )


class DatabaseError(PowerCVException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details={"operation": operation, **(details or {})}
        )


class RateLimitError(PowerCVException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after}
        )


class FileProcessingError(PowerCVException):
    """Raised when file processing operations fail."""
    
    def __init__(self, message: str, file_name: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="FILE_PROCESSING_ERROR",
            details={"file_name": file_name, **(details or {})}
        )


# Global exception handlers

async def powercv_exception_handler(request: Request, exc: PowerCVException):
    """Global handler for PowerCV custom exceptions."""
    logger.error(
        f"PowerCVException: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "request_path": request.url.path,
            "request_method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "type": exc.__class__.__name__,
                "details": exc.details
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Enhanced handler for FastAPI HTTP exceptions."""
    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "request_path": request.url.path,
            "request_method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "code": f"HTTP_{exc.status_code}",
                "type": "HTTPException"
            }
        }
    )


async def validation_exception_handler(request: Request, exc):
    """Handler for Pydantic validation errors."""
    logger.warning(
        f"ValidationError: {exc.errors()}",
        extra={
            "validation_errors": exc.errors(),
            "request_path": request.url.path,
            "request_method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation failed",
                "code": "VALIDATION_ERROR",
                "type": "ValidationError",
                "details": {"validation_errors": exc.errors()}
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Fallback handler for unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "exception_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError"
            }
        }
    )
