"""
Verify trader unlock information for specific items
"""
import os

# Expected unlocks
EXPECTED_UNLOCKS = {
    "Salt-cured Fish": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Arnor Trader OR Blue Mountains Trader}}",
    "Northern Wool": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Arnor Trader}}",
    "Shell": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Blue Mountains Trader}}",
    "Coastal Marble": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Blue Mountains Trader}}",
    "Elven Silk": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Lothloorien Trader Or Rivendell Trader}}",
    "Drakhbarzin": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Lothloorien Trader}}",
    "Elanor Seed": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Lothloorien Trader}}",
    "Niphredil Seed": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Lothloorien Trader}}",
    "Saffron": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Fireclay Brick": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Red Sandstone": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Pumice": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Crimson Fire Brazier": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Volcanic Glass": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Southern Oil": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gondor Trader}}",
    "Whale Tallow": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gondor Trader}}",
    "White Tree Replica": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gondor Trader}}",
    "Sea Wax": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gundabad Quartermaster}}",
    "Thanazutsam": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Rivendell Trader}}",
    "Ithildin Ingot": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Rivendell Trader}}",
    "Cookware Display": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Shire Trader}}",
    "Pumpkin Seed": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Shire Trader}}",
    "Sweetroot Seed": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Shire Trader}}",
}

def find_wiki_file(item_name):
    """Find wiki file for an item in any output directory."""
    directories = [
        'output/items', 'output/constructions', 'output/consumables',
        'output/ores', 'output/weapons', 'output/armor', 'output/tools'
    ]

    # First pass: exact matches only
    for directory in directories:
        if not os.path.exists(directory):
            continue

        # Try exact match
        filepath = os.path.join(directory, f"{item_name}.wiki")
        if os.path.exists(filepath):
            return filepath, directory.split('/')[-1]

        # Try with trailing space (some items have this)
        filepath_space = os.path.join(directory, f"{item_name} .wiki")
        if os.path.exists(filepath_space):
            return filepath_space, directory.split('/')[-1]

    # Second pass: special case for "Cookware Display" -> "Hanging Cookware"
    if item_name == "Cookware Display":
        for directory in directories:
            if not os.path.exists(directory):
                continue
            filepath = os.path.join(directory, "Hanging Cookware.wiki")
            if os.path.exists(filepath):
                return filepath, directory.split('/')[-1]

    return None, None

def extract_unlock_section(filepath):
    """Extract the unlock section from a wiki file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '== Unlock ==' not in content:
        return None

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
                unlock_lines.append(line.strip())

    return '\n'.join(unlock_lines) if unlock_lines else None

def main():
    print("VERIFICATION REPORT: Trader Unlock Items")
    print("=" * 80)
    print()

    found_count = 0
    correct_count = 0
    incorrect_count = 0
    missing_count = 0

    for item_name, expected_unlock in EXPECTED_UNLOCKS.items():
        filepath, category = find_wiki_file(item_name)

        if filepath is None:
            print(f"[X] {item_name}")
            print(f"   Status: FILE NOT FOUND")
            print(f"   Expected: {expected_unlock}")
            print()
            missing_count += 1
            continue

        found_count += 1
        unlock_section = extract_unlock_section(filepath)

        if unlock_section is None:
            print(f"[X] {item_name} ({category})")
            print(f"   Status: NO UNLOCK SECTION")
            print(f"   Expected: {expected_unlock}")
            print()
            incorrect_count += 1
            continue

        # Check if unlock matches expected
        has_match = expected_unlock.lower() in unlock_section.lower()

        if has_match:
            print(f"[OK] {item_name} ({category})")
            print(f"   Status: CORRECT")
            correct_count += 1
        else:
            print(f"[X] {item_name} ({category})")
            print(f"   Status: INCORRECT UNLOCK")
            print(f"   Expected: {expected_unlock}")
            print(f"   Actual: {unlock_section}")
            incorrect_count += 1
        print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total items to check: {len(EXPECTED_UNLOCKS)}")
    print(f"Files found: {found_count}")
    print(f"Correct unlocks: {correct_count}")
    print(f"Incorrect unlocks: {incorrect_count}")
    print(f"Missing files: {missing_count}")
    print()

    if correct_count == len(EXPECTED_UNLOCKS):
        print("[OK] ALL ITEMS HAVE CORRECT UNLOCKS!")
    else:
        print(f"[!] {len(EXPECTED_UNLOCKS) - correct_count} items need attention")

if __name__ == "__main__":
    main()
