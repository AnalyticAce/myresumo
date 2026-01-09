"""Enhanced error handling and debugging utilities for PowerCV."""

import logging
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Dict

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class DetailedError(Exception):
    """Enhanced exception with detailed context for debugging."""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        context: Dict[str, Any] = None,
        cause: Exception = None,
        user_friendly_message: str = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        self.cause = cause
        self.user_friendly_message = user_friendly_message or message
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/API responses."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_friendly_message": self.user_friendly_message,
            "context": self.context,
            "timestamp": self.timestamp,
            "cause_type": type(self.cause).__name__ if self.cause else None,
            "cause_message": str(self.cause) if self.cause else None
        }


class ErrorHandler:
    """Centralized error handling and logging utility."""
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Dict[str, Any] = None,
        include_traceback: bool = True
    ) -> Dict[str, Any]:
        """Log error with detailed context and return error details."""
        error_details = {
            "error_type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        }
        
        if include_traceback:
            error_details["traceback"] = traceback.format_exc()
        
        # Log with appropriate level
        if isinstance(error, (ValueError, KeyError, AttributeError)):
            logger.warning(f"Application error: {error_details}")
        else:
            logger.error(f"Critical error: {error_details}")
        
        return error_details
    
    @staticmethod
    def create_http_exception(
        error: Exception,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        user_message: str = None,
        include_context: bool = False
    ) -> HTTPException:
        """Create HTTP exception with proper error details."""
        error_details = ErrorHandler.log_error(error)
        
        response_data = {
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": error_details["timestamp"]
        }
        
        if user_message:
            response_data["detail"] = user_message
        
        # Include context in development mode
        if include_context and error_details.get("context"):
            response_data["context"] = error_details["context"]
        
        return HTTPException(
            status_code=status_code,
            detail=response_data
        )
    
    @staticmethod
    def handle_ai_api_error(
        error: Exception,
        provider: str,
        operation: str,
        context: Dict[str, Any] = None
    ) -> HTTPException:
        """Handle AI API errors with specific context."""
        error_context = {
            "provider": provider,
            "operation": operation,
            "error_type": type(error).__name__,
            **(context or {})
        }
        
        ErrorHandler.log_error(error, error_context)
        
        # Determine appropriate status code based on error type
        if "timeout" in str(error).lower():
            status_code = status.HTTP_408_REQUEST_TIMEOUT
            user_message = f"The {provider} service is taking too long to respond. Please try again."
        elif "connection" in str(error).lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            user_message = f"Unable to connect to {provider} service. Please try again later."
        elif "authentication" in str(error).lower() or "unauthorized" in str(error).lower():
            status_code = status.HTTP_401_UNAUTHORIZED
            user_message = f"Authentication with {provider} failed. Please check your API configuration."
        elif "rate limit" in str(error).lower():
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            user_message = f"Rate limit exceeded for {provider}. Please try again later."
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            user_message = f"An error occurred with the {provider} service. Please try again."
        
        return HTTPException(
            status_code=status_code,
            detail={
                "error": "AI Service Error",
                "provider": provider,
                "operation": operation,
                "detail": user_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


def debug_endpoint(func):
    """Decorator to add debugging information to endpoint responses."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        
        try:
            result = await func(*args, **kwargs)
            
            # Add debug info to response if it's a dict
            if isinstance(result, dict):
                debug_info = {
                    "debug": {
                        "execution_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                        "timestamp": start_time.isoformat(),
                        "function": func.__name__
                    }
                }
                # Merge debug info without overwriting existing keys
                result.update(debug_info)
            
            return result
            
        except Exception as e:
            # Log the error with execution context
            ErrorHandler.log_error(e, {
                "function": func.__name__,
                "execution_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            })
            raise
    
    return wrapper


class ValidationError(DetailedError):
    """Enhanced validation error with field-specific details."""
    
    def __init__(
        self,
        message: str,
        field: str = None,
        value: Any = None,
        validation_rule: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if field:
            context['field'] = field
        if value is not None:
            context['value'] = str(value)[:100]  # Limit value length for security
        if validation_rule:
            context['validation_rule'] = validation_rule
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context,
            **kwargs
        )


class ConfigurationError(DetailedError):
    """Enhanced configuration error with specific details."""
    
    def __init__(
        self,
        message: str,
        config_key: str = None,
        expected_type: str = None,
        provider: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if config_key:
            context['config_key'] = config_key
        if expected_type:
            context['expected_type'] = expected_type
        if provider:
            context['provider'] = provider
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context=context,
            **kwargs
        )


def create_error_response(
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "error": True,
        "error_code": error_code,
        "message": message,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }


def log_performance(operation: str, duration_ms: float, context: Dict[str, Any] = None):
    """Log performance metrics."""
    logger.info(f"Performance: {operation} completed in {duration_ms:.2f}ms", extra={
        "operation": operation,
        "duration_ms": duration_ms,
        "context": context or {}
    })


class ErrorContext:
    """Context manager for error handling and logging."""
    
    def __init__(self, operation: str, context: Dict[str, Any] = None):
        self.operation = operation
        self.context = context or {}
        self.start_time = datetime.utcnow()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        
        if exc_type is None:
            # Operation completed successfully
            log_performance(self.operation, duration_ms, self.context)
        else:
            # Operation failed
            error_context = {
                "operation": self.operation,
                "duration_ms": duration_ms,
                **self.context
            }
            ErrorHandler.log_error(exc_val, error_context)
        
        return False  # Don't suppress exceptions
