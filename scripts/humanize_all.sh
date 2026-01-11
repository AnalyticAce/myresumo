#!/bin/bash
# Run all humanization scripts

echo "Starting codebase humanization..."
echo

echo "1. Removing em dashes..."
bash scripts/remove_em_dashes.sh

echo
echo "2. Removing emojis..."
python3 scripts/remove_emojis.py

echo
echo "3. Removing AI language patterns..."
python3 scripts/humanize_text.py

echo
echo "Humanization complete!"
echo
echo "Please review changes with: git diff"
