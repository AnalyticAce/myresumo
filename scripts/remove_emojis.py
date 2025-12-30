#!/usr/bin/env python3
"""Remove emojis from codebase files."""
import re
import sys
from pathlib import Path

# Emoji regex pattern
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA70-\U0001FAFF"
    "]+",
    flags=re.UNICODE
)

def remove_emojis_from_file(filepath):
    """Remove emojis from a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        content = EMOJI_PATTERN.sub('', content)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Process all relevant files in the repository."""
    extensions = {'.py', '.md', '.txt', '.js', '.ts', '.jsx', '.tsx', '.json'}
    exclude_dirs = {'node_modules', '.git', 'venv', '__pycache__', '.venv', 'dist', 'build'}

    modified_count = 0
    processed_count = 0

    root = Path('.')

    for filepath in root.rglob('*'):
        # Skip directories and excluded paths
        if filepath.is_dir():
            continue
        if any(excluded in filepath.parts for excluded in exclude_dirs):
            continue
        if filepath.suffix not in extensions:
            continue

        processed_count += 1
        if remove_emojis_from_file(filepath):
            modified_count += 1
            print(f"Modified: {filepath}")

    print(f"\nProcessed {processed_count} files")
    print(f"Modified {modified_count} files")

if __name__ == '__main__':
    main()
