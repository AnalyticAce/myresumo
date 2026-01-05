"""Secure logging configuration for PowerCV."""
import logging
import re
from typing import Optional


class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from logs."""

    PATTERNS = [
        # API keys (Deepseek, OpenAI, etc.)
        (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9\-_]{20,})'), r'\1***REDACTED***'),
        # MongoDB connection strings
        (re.compile(r'(mongodb.*://[^:]+:)([^@]+)(@)'), r'\1***REDACTED***\3'),
        # Generic API keys (sk-, pk-, etc.)
        (re.compile(r'(sk-[a-zA-Z0-9]{20,})'), r'***API_KEY_REDACTED***'),
        (re.compile(r'(pk_[a-zA-Z0-9]{20,})'), r'***API_KEY_REDACTED***'),
        # Passwords
        (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\']+)'), r'\1***REDACTED***'),
        # JWT tokens
        (re.compile(r'(Bearer\s+)([a-zA-Z0-9\-_\.]{50,})'), r'\1***JWT_REDACTED***'),
    ]

    def filter(self, record):
        """Filter sensitive data from log records."""
        message = record.getMessage()

        for pattern, replacement in self.PATTERNS:
            message = pattern.sub(replacement, message)

        record.msg = message
        record.args = ()
        return True


def setup_secure_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """Set up secure logging configuration.

    Args:
        level: Logging level
        log_file: Optional log file path
        format_string: Log format string

    Returns:
        Root logger with secure filtering
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    # Create file handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(SensitiveDataFilter())
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            # Log to console if file logging fails (but don't expose sensitive data)
            logger.warning(f"Failed to set up file logging: {type(e).__name__}")

    return logger


# Global logger instance
logger = setup_secure_logging()