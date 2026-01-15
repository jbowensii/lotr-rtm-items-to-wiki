"""
Verify unlock information for items across all wiki files (items, constructions, consumables)
"""
import os
import json

def check_wiki_file(directory, filename):
    """Check if a wiki file exists and extract its unlock section."""
    filepath = os.path.join(directory, filename)
    if not os.path.exists(filepath):
        return None, "File not found"

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '== Unlock ==' not in content:
        return None, "No unlock section"

    # Extract unlock lines
    lines = content.split('\n')
    unlock_lines = []
    in_unlock = False
    for line in lines:
        if '== Unlock ==' in line:
            in_unlock = True
            continue
        if in_unlock:
            if line.startswith('=='):
                break
            if line.strip():
                unlock_lines.append(line)

    return '\n'.join(unlock_lines), "Found"

def main():
    # Items to check - paste the list from user here
    items_to_check = []

    print("Please provide the list of items to check.")
    print("Expected format: Display Name -> unlock description")
    print("\nWaiting for input...")

    # For now, just show the function is ready
    print("\nReady to check items. Please provide the list in your next message.")

if __name__ == "__main__":
    main()
