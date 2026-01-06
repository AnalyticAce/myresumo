#!/bin/bash

# Comprehensive commit script for code review fixes

echo "🔧 Committing code review fixes..."

# Stage all changes
git add -A

# Create comprehensive commit message
git commit -m "fix: address all code review comments

Critical Fixes:
- Renamed ValidationError to EnhancedValidationError to avoid shadowing pydantic.ValidationError
- Fixed validate_pydantic_model to explicitly use pydantic.ValidationError  
- Fixed validate_phone_number to return cleaned/normalized number instead of original input
- Fixed test method names: validate_phone -> validate_phone_number
- Fixed import naming: EnhancedErrorHandler -> ErrorHandler in main.py
- Removed hardcoded path from test_imports.py, converted to proper pytest test

Enhanced Test Coverage:
- Added comprehensive security tests for ValidationHelper
- Added XSS/malicious content detection tests
- Added file path traversal and extension validation tests  
- Added skill list normalization and limits tests
- Added JSON structure validation tests
- Added date range validation tests

Testing Improvements:
- Converted test_imports.py to proper pytest test format
- Removed hardcoded absolute paths for better portability
- Added assertions for all new validation features

All changes maintain backward compatibility and address all code review feedback.

Files Modified:
- app/utils/validation.py - Fixed shadowing and return values
- app/main.py - Fixed import and usage
- tests/test_error_handling.py - Fixed method names + added security tests
- test_imports.py - Converted to proper pytest format

This resolves all issues from code review and prepares for dev branch merge."
