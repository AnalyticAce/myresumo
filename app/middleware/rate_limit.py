"""Rate limiting middleware for PowerCV."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from typing import Callable
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global rate limiter
limiter = Limiter(key_func=get_remote_address)

# Stricter limiter for expensive operations
expensive_limiter = Limiter(key_func=get_remote_address)

# User-based limiter (when auth is implemented)
def get_user_identifier(request: Request) -> str:
    """Get user identifier for rate limiting.

    For now, uses IP address. Later will use user ID when auth is implemented.
    """
    # Try to get from headers (when auth is implemented)
    # For now, fall back to IP
    return get_remote_address(request)

user_limiter = Limiter(key_func=get_user_identifier)


def init_rate_limiting(app):
    """Initialize rate limiting for the FastAPI app."""

    # Add rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Store limiter in app state
    app.state.limiter = limiter
    app.state.expensive_limiter = expensive_limiter
    app.state.user_limiter = user_limiter

    logger.info("Rate limiting initialized")


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""

    logger.warning(
        f"Rate limit exceeded for {request.url.path} from {get_remote_address(request)}"
    )

    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.retry_after
        },
        headers={"Retry-After": str(exc.retry_after)}
    )


# Rate limit decorators for different endpoints
def light_limit():
    """Rate limit for light operations (60/minute)."""
    return limiter.limit(f"{settings.rate_limit_per_minute}/minute")


def heavy_limit():
    """Rate limit for heavy operations (5/minute)."""
    return expensive_limiter.limit("5/minute")


def auth_limit():
    """Rate limit for authenticated operations (higher limits)."""
    return user_limiter.limit(f"{settings.rate_limit_per_hour}/hour")