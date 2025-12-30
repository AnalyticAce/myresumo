#!/bin/bash
# Remove em dashes from codebase

find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.js" -o -name "*.ts" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/.pytest_cache/*" \
  -exec sed -i 's/—/-/g' {} +

echo "Em dashes replaced with regular dashes"
