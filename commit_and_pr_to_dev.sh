#!/bin/bash

# Git commit and pull request script for PowerCV refactoring to dev branch

echo "🚀 Starting commit process for PowerCV refactoring..."

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Create and switch to feature branch
echo "🌿 Creating feature branch..."
git checkout -b feature/comprehensive-refactoring

if [ $? -ne 0 ]; then
    echo "❌ Failed to create feature branch"
    exit 1
fi

# Stage all changes
echo "📦 Staging all changes..."
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "❌ No changes to commit"
    exit 1
fi

# Create commit with comprehensive message
echo "📝 Creating commit..."
git commit -m "feat: comprehensive code analysis and refactoring

- Fixed configuration inconsistencies and duplicate field definitions
- Replaced all print() statements with proper logging
- Enhanced error handling with detailed context and user-friendly messages
- Added comprehensive input validation with security checks
- Implemented security headers middleware (XSS protection, HSTS, etc.)
- Created debugging middleware for performance monitoring
- Added structured logging with request IDs and timing
- Enhanced JSON parsing with detailed error handling
- Resolved TODO comments with proper implementations
- Added comprehensive test suite for new components
- Created enhanced validation utilities
- Implemented malicious content detection and sanitization
- Added performance metrics collection and slow request detection
- Enhanced file upload security
- Maintained full backward compatibility

New files:
- app/utils/error_handler.py - Enhanced error handling utilities
- app/utils/validation.py - Comprehensive validation utilities  
- app/middleware/debugging.py - Debugging and performance monitoring middleware
- tests/test_error_handling.py - Test suite for new components
- REFACTORING_SUMMARY.md - Detailed documentation of changes

This refactoring significantly improves reliability, security, maintainability, and debugging capabilities while maintaining backward compatibility."

if [ $? -eq 0 ]; then
    echo "✅ Commit created successfully!"
    
    # Show commit details
    echo "📋 Commit details:"
    git log --oneline -1
    
    echo ""
    echo "🌟 Ready to push and create pull request to dev branch!"
    echo ""
    echo "Next steps:"
    echo "1. Push to your fork:"
    echo "   git push origin feature/comprehensive-refactoring"
    echo ""
    echo "2. Create pull request to dev branch:"
    echo "   - Go to: https://github.com/ILLnar-Nizami/PowerCV"
    echo "   - Click 'Compare & pull request'"
    echo "   - Select base: 'dev' branch"
    echo "   - Select compare: 'feature/comprehensive-refactoring' branch"
    echo "   - Fill in PR details (see PR_TEMPLATE.md)"
    echo ""
    echo "3. Or use GitHub CLI:"
    echo "   gh pr create --base dev --title 'Comprehensive Code Analysis and Refactoring' --body-file PR_TEMPLATE.md"
    echo ""
else
    echo "❌ Failed to create commit"
    exit 1
fi
