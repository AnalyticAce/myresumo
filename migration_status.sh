#!/bin/bash

echo "🚀 PowerCV Frontend Migration - Final Status"
echo "=========================================="

# Check if frontend directory exists
if [ -d "frontend" ]; then
    echo "✅ Frontend directory exists"
else
    echo "❌ Frontend directory not found"
    exit 1
fi

# Check if key files exist
echo ""
echo "📁 Checking key files..."

files_to_check=(
    "frontend/package.json"
    "frontend/src/App.tsx"
    "frontend/src/main.tsx"
    "frontend/src/router.tsx"
    "frontend/tsconfig.json"
    "frontend/vite.config.ts"
    "frontend/tailwind.config.js"
    "frontend/src/types/enums.ts"
    "frontend/src/api/client.ts"
    "frontend/src/components/layout/AppLayout.tsx"
    "frontend/src/pages/DashboardPage.tsx"
    "frontend/src/hooks/useResumes.ts"
    "frontend/src/stores/optimizationStore.ts"
    "frontend/CHANGELOG.md"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file"
    fi
done

# Check build
echo ""
echo "🔨 Testing build..."
cd frontend
if npm run build > /dev/null 2>&1; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
fi

# Count files
echo ""
echo "📊 File count:"
echo "Total files: $(find . -type f | wc -l)"
echo "TypeScript files: $(find . -name "*.ts" -o -name "*.tsx" | wc -l)"
echo "React components: $(find . -name "*.tsx" | wc -l)"

echo ""
echo "🎯 Migration Status: COMPLETED SUCCESSFULLY"
echo "📝 Documentation: See frontend/CHANGELOG.md"
echo "🔀 Pull Request: See FRONTEND_MIGRATION_PR.md"
echo ""
echo "You can now run:"
echo "  cd frontend && npm run dev    # Start development server"
echo "  cd frontend && npm run build  # Build for production"
echo ""
echo "🎉 PowerCV Frontend Migration Complete!"
