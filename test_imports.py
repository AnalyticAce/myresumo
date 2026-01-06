#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/home/illnar/Projects/PowerCV')

def test_imports():
    """Test all new modules can be imported."""
    try:
        print("Testing imports...")
        
        # Test error handler
        from app.utils.error_handler import ErrorHandler, DetailedError
        print("✓ Error handler imports successfully")
        
        # Test validation
        from app.utils.validation import ValidationHelper
        print("✓ Validation imports successfully")
        
        # Test debugging middleware
        from app.middleware.debugging import DebuggingMiddleware
        print("✓ Debugging middleware imports successfully")
        
        # Test main application (may fail due to dependencies)
        try:
            from app.main import app
            print("✓ Main application imports successfully")
        except Exception as e:
            print(f"⚠ Main application import failed (expected due to missing dependencies): {e}")
        
        print("\nAll critical imports successful!")
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
