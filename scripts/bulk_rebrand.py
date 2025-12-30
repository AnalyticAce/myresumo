import os
import re


def replace_in_file(filepath, old_text, new_text):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_text in content:
            new_content = content.replace(old_text, new_text)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False


def main():
    root_dir = '/home/illnar/Projects/PowerCV'
    old_text = 'MyResumo'
    new_text = 'PowerCV'

    exclude_dirs = {'.git', '.venv', '.pytest_cache',
                    '__pycache__', 'node_modules', '.qodo'}
    exclude_files = {'bulk_rebrand.py'}

    count = 0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file in exclude_files:
                continue

            filepath = os.path.join(root, file)
            if replace_in_file(filepath, old_text, new_text):
                print(f"Updated: {filepath}")
                count += 1

    print(f"Rebranded {count} files.")


if __name__ == "__main__":
    main()
