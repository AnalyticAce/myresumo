#!/usr/bin/env python3
"""Remove AI-typical language patterns from text files."""
import re
import sys
from pathlib import Path

# Patterns to remove or replace
PATTERNS = {
    # Remove enthusiastic markers
    r'!\s*\n': '.\n',  # Replace ! at end of lines with .
    r'!!+': '!',  # Multiple exclamation marks

    # Remove marketing speak
    r'\b(Simply|Just|Easily|Quickly|Seamlessly)\b': '',

    # Remove AI phrases
    r"Let's\s+": '',
    r"We'll\s+": '',
    r"Here's\s+": '',

    # Remove excessive emphasis
    r'\*\*\*([^*]+)\*\*\*': r'\1',  # Triple emphasis
    r'`([^`]+)`': r'\1',  # Remove inline code that isn't actually code

    # Clean up excessive formatting
    r'\n\n\n+': '\n\n',  # Multiple blank lines
    r'#+\s*\n': '',  # Empty headers

    # Remove bullet points with emojis (already removed emoji, clean up spacing)
    r'^\s*[-*]\s+\s+': '- ',

    # Remove "Pro tip", "Note:", etc.
    r'\*\*Pro tip:\*\*\s*': '',
    r'\*\*Note:\*\*\s*': 'Note: ',
    r'\*\*Important:\*\*\s*': 'Important: ',
}

# Phrases to replace with neutral alternatives
REPLACEMENTS = {
    'super easy': 'straightforward',
    'really powerful': 'useful',
    'amazing': 'effective',
    'awesome': 'good',
    'incredible': 'notable',
    'perfect': 'suitable',
    'beautiful': 'clean',
    'elegant': 'simple',
    'robust': 'reliable',
    'cutting-edge': 'modern',
    'state-of-the-art': 'current',
    'blazing fast': 'fast',
    'lightning fast': 'fast',
    'game-changer': 'improvement',
    'game changer': 'improvement',
}


def humanize_content(content):
    """Apply humanization patterns to content."""
    # Apply regex patterns
    for pattern, replacement in PATTERNS.items():
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)

    # Apply word replacements
    for phrase, replacement in REPLACEMENTS.items():
        content = re.sub(r'\b' + re.escape(phrase) + r'\b', replacement, content, flags=re.IGNORECASE)

    # Clean up multiple spaces
    content = re.sub(r'  +', ' ', content)

    # Clean up whitespace around punctuation
    content = re.sub(r'\s+([.,;:])', r'\1', content)

    return content


def process_file(filepath):
    """Process a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()

        humanized = humanize_content(original)

        if humanized != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(humanized)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False


def main():
    """Process all markdown and text files."""
    extensions = {'.md', '.txt', '.rst'}
    exclude_dirs = {'node_modules', '.git', 'venv', '__pycache__', '.venv'}

    modified_count = 0
    processed_count = 0

    root = Path('.')

    for filepath in root.rglob('*'):
        if filepath.is_dir():
            continue
        if any(excluded in filepath.parts for excluded in exclude_dirs):
            continue
        if filepath.suffix not in extensions:
            continue

        processed_count += 1
        if process_file(filepath):
            modified_count += 1
            print(f"Modified: {filepath}")

    print(f"\nProcessed {processed_count} files")
    print(f"Modified {modified_count} files")


if __name__ == '__main__':
    main()
