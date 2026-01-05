"""Configuration package for PowerCV."""

from .settings import get_settings, Settings
from .logging_config import logger, setup_secure_logging

# Backward compatibility - provide computed_settings like the old config.py
computed_settings = get_settings()

__all__ = ["get_settings", "Settings", "logger", "setup_secure_logging", "computed_settings"]