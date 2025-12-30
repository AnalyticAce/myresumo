#!/bin/bash
# setup_dev.sh - Development environment setup script for ATS Resume Optimizer

set -e  # Exit on error

echo "Setting up development environment..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Installing dependencies..."
pip install --upgrade pip --break-system-packages
pip install -r requirements.txt --break-system-packages

if [ -f ".pre-commit-config.yaml" ]; then
    echo "Installing pre-commit hooks..."
    pip install pre-commit --break-system-packages
    pre-commit install
fi

echo "Development environment setup complete!"
echo "---------------------------------------"
echo "To activate the virtual environment, run:"
echo "    source venv/bin/activate"
echo ""
echo "After activation, you can run the application with: python main.py"