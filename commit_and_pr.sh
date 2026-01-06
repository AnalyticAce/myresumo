#!/bin/bash

# Git commit and pull request script for PowerCV refactoring

echo "🚀 Starting commit process for PowerCV refactoring..."

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
git commit -F COMMIT_MESSAGE.md

if [ $? -eq 0 ]; then
    echo "✅ Commit created successfully!"
    
    # Show commit details
    echo "📋 Commit details:"
    git log --oneline -1
    
    echo ""
    echo "🌟 Ready to create pull request!"
    echo ""
    echo "To create a pull request, run these commands:"
    echo ""
    echo "1. Push to your fork:"
    echo "   git push origin feature/comprehensive-refactoring"
    echo ""
    echo "2. Create pull request on GitHub:"
    echo "   - Go to: https://github.com/ILLnar-Nizami/PowerCV"
    echo "   - Click 'Compare & pull request'"
    echo "   - Select your feature branch"
    echo "   - Fill in PR details (see PR_TEMPLATE.md)"
    echo ""
    echo "3. Or use GitHub CLI:"
    echo "   gh pr create --title 'Comprehensive Code Analysis and Refactoring' --body-file PR_TEMPLATE.md"
    echo ""
else
    echo "❌ Failed to create commit"
    exit 1
fi
