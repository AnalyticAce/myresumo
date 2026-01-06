#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import pytest


def test_imports():
    """Test all new modules can be imported."""
    # Import should succeed, otherwise pytest will fail this test.
    from app.utils.error_handler import ErrorHandler, DetailedError
    from app.utils.validation import ValidationHelper
    from app.middleware.debugging import DebuggingMiddleware
    
    # Basic sanity checks so linters don't flag unused imports
    assert ErrorHandler is not None
    assert DetailedError is not None
    assert ValidationHelper is not None
    assert DebuggingMiddleware is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
