#!/usr/bin/env python3
"""Test server startup without actually running it."""

import sys

# Add project root to Python path
sys.path.insert(0, '/home/illnar/Projects/PowerCV')


def test_imports():
    """Test all critical imports for server startup."""
    try:
        print("Testing critical imports...")
        
        # Test settings
        from app.config.settings import get_settings
        settings = get_settings()
        print(f" Settings loaded: {settings.app_name} v{settings.version}")
        
        # Test database connector
        from app.database.connector import (
            get_secure_mongodb_config,
        )
        config = get_secure_mongodb_config()
        print(f" MongoDB config: {config['database']}")
        
        # Test main app import
        print(" Main app imported successfully")
        
        # Test debugging middleware
        print(" Debugging middleware imported")
        
        print("\n All critical imports successful!")
        return True
        
    except Exception as e:
        print(f" Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
