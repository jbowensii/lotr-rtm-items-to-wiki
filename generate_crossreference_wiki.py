"""Generate cross-reference tables for consumables, items, and ores.

Searches all wiki files to find where materials are used in recipes,
then updates the source wiki files with "Used In" tables.
"""

import os
import re
from collections import defaultdict


# Base path for wiki output files in %APPDATA%
OUTPUT_BASE = os.path.join(os.environ.get("APPDATA", ""), "MoriaWikiGenerator", "output")
WIKI_DIR = os.path.join(OUTPUT_BASE, "wiki")

# Directories to search for recipe usage
SEARCH_DIRS = [
    os.path.join(WIKI_DIR, "weapons"),
    os.path.join(WIKI_DIR, "tools"),
    os.path.join(WIKI_DIR, "constructions"),
    os.path.join(WIKI_DIR, "brews"),
    os.path.join(WIKI_DIR, "armor"),
    os.path.join(WIKI_DIR, "tradegoods"),
    os.path.join(WIKI_DIR, "consumables"),  # Consumables can craft other consumables
]

# Directories containing items to add cross-references to
TARGET_DIRS = [
    os.path.join(WIKI_DIR, "consumables"),
    os.path.join(WIKI_DIR, "items"),
    os.path.join(WIKI_DIR, "ores"),
]


def extract_item_name_from_wiki_link(link):
    """Extract item name from wiki link format: {{LI|Item Name}}"""
    match = re.search(r'\{\{LI\|([^}]+)\}\}', link)
    if match:
        return match.group(1)

    # Also handle plain [[Item Name]] format
    match = re.search(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', link)
    if match:
        return match.group(1)

    return None


def extract_all_stations_from_infobox(station_text):
    """Extract all station names from brew infobox station field.

    Returns list of station names.
    """
    stations = []

    # Split by <br> or newline
    parts = re.split(r'<br>|\n', station_text)

    for part in parts:
        # Extract station name from [[Station]] format
        station_name = extract_item_name_from_wiki_link(part)
        if station_name:
            stations.append(station_name)

    return stations


def parse_wiki_file(filepath):
    """Parse a wiki file and extract recipe information.

    Returns:
        dict with keys: 'display_name', 'stations', 'materials', 'is_brew'
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract display name from title or PAGENAME
    display_name = os.path.splitext(os.path.basename(filepath))[0]

    # Determine if this is a brew (check for brews directory or Brew type)
    is_brew = os.path.join('wiki', 'brews') in filepath or 'brews' in filepath.replace('\\', '/').lower() or 'type          = Brew' in content

    # Extract crafting station(s)
    stations = []

    # Method 1: From "Station:" section (weapons, tools, consumables)
    station_match = re.search(r'Station:\s*\n\s*\*\s*(.+)', content)
    if station_match:
        station_name = extract_item_name_from_wiki_link(station_match.group(1))
        if station_name:
            stations.append(station_name)

    # Method 2: From infobox "station" field (brews) - extract ALL stations
    if not stations:
        station_infobox = re.search(r'\|\s*station\s*=\s*(.+?)(?=\n\s*\||\n\}\})', content, re.DOTALL)
        if station_infobox:
            station_text = station_infobox.group(1)
            stations = extract_all_stations_from_infobox(station_text)

    # For constructions, station might not be listed but implied
    if not stations and 'Building object' in content:
        # Constructions are built at various hearths/forges
        stations.append("Hearth/Forge")

    # Extract materials from either "Materials:" or "reqs" field
    materials = []

    # Method 1: Parse from Crafting section (weapons, tools, armor, consumables)
    materials_section = re.search(r'Materials:\s*\n((?:\s*\*.*\n)*)', content)
    if materials_section:
        material_lines = materials_section.group(1).strip().split('\n')
        for line in material_lines:
            # Parse: * (15) {{LI|Wood Scraps}}
            count_match = re.search(r'\((\d+)\)', line)
            item_name = extract_item_name_from_wiki_link(line)
            if item_name:
                count = int(count_match.group(1)) if count_match else 1
                materials.append({
                    'name': item_name,
                    'count': count,
                    'is_range': False
                })

    # Method 2: Parse from infobox reqs field (constructions and brews)
    if not materials:
        reqs_match = re.search(r'\|\s*reqs\s*=\s*(.+?)(?=\n\s*\||\n\}\})', content, re.DOTALL)
        if reqs_match:
            reqs_text = reqs_match.group(1)
            # Parse: 1 [[Red Sandstone]]<br>3 [[Wood]]
            # Or brew format: 3-6-9 [[Grabapple]]
            # Split by <br> or newline
            for part in re.split(r'<br>|\n', reqs_text):
                part = part.strip()
                if not part:
                    continue

                # Check for brew-style ranges (e.g., "3-6-9")
                range_match = re.search(r'(\d+(?:-\d+)+)\s+\[\[', part)
                if range_match:
                    # This is a brew range
                    numbers = range_match.group(1).split('-')
                    if len(numbers) == 3:
                        small, medium, large = int(numbers[0]), int(numbers[1]), int(numbers[2])
                    else:
                        # Fallback for unexpected format
                        small = medium = large = int(numbers[-1])

                    item_name = extract_item_name_from_wiki_link(part)
                    if item_name:
                        materials.append({
                            'name': item_name,
                            'small': small,
                            'medium': medium,
                            'large': large,
                            'is_range': True
                        })
                else:
                    # Regular single number
                    count_match = re.search(r'(\d+)\s+', part)
                    count = int(count_match.group(1)) if count_match else 1

                    item_name = extract_item_name_from_wiki_link(part)
                    if item_name:
                        materials.append({
                            'name': item_name,
                            'count': count,
                            'is_range': False
                        })

    return {
        'display_name': display_name,
        'stations': stations,
        'materials': materials,
        'is_brew': is_brew
    }


def find_material_usage(material_name, search_dirs):
    """Find all recipes that use a given material.

    Args:
        material_name: Name of the material to search for
        search_dirs: List of directories to search

    Returns:
        List of dicts with keys: 'recipe_name', 'stations', 'all_materials', 'is_brew', 'category'
    """
    usage_list = []

    for directory in search_dirs:
        if not os.path.exists(directory):
            continue

        # Determine category from directory name
        category = os.path.basename(directory).title()
        if category == "Consumables":
            category = "Consumable"
        elif category == "Tradegoods":
            category = "Special"

        for filename in os.listdir(directory):
            if not filename.endswith('.wiki'):
                continue

            filepath = os.path.join(directory, filename)
            recipe_info = parse_wiki_file(filepath)

            # Skip self-references (item used to craft itself)
            if recipe_info['display_name'] == material_name:
                continue

            # Check if this recipe uses the material
            uses_material = False
            for material in recipe_info['materials']:
                if material['name'] == material_name:
                    uses_material = True
                    break

            if uses_material:
                usage_list.append({
                    'recipe_name': recipe_info['display_name'],
                    'stations': recipe_info['stations'],
                    'all_materials': recipe_info['materials'],
                    'is_brew': recipe_info['is_brew'],
                    'category': category
                })

    return usage_list


def format_recipe_column(recipe_name):
    """Format recipe name with icon image."""
    return f"[[File:{recipe_name}.webp|x32px|link={recipe_name}]] [[{recipe_name}]]"


def format_station_column(stations, is_brew=False):
    """Format station(s) with icon images.

    For brews with multiple stations, show them with 'or' between them.
    """
    if not stations:
        return "N/A"

    if len(stations) == 0:
        return "N/A"

    # Special handling for brews with Alchemical Still
    # Check if last station is "Alchemical Still" and others are brew stations
    if is_brew and len(stations) > 1 and stations[-1] == "Alchemical Still":
        # Format as: "Alchemical Still with: Station1 or Station2 or Station3"
        still = stations[-1]
        brew_stations = stations[:-1]

        station_links = []
        for station in brew_stations:
            # Handle special case for King's Brew Tank which uses .png
            if station == "King's Brew Tank":
                station_links.append(f"[[File:{station}.png|32px|link={station}]] [[{station}]]")
            else:
                station_links.append(f"[[File:{station}.webp|32px|link={station}]] [[{station}]]")

        stations_text = " or<br>".join(station_links)
        return f"[[File:{still}.webp|32px|link={still}]] [[{still}]] with:<br>{stations_text}"
    else:
        # Regular format: Station1 or Station2
        station_links = []
        for station in stations:
            # Handle special case for King's Brew Tank which uses .png
            if station == "King's Brew Tank":
                station_links.append(f"[[File:{station}.png|32px|link={station}]] [[{station}]]")
            else:
                station_links.append(f"[[File:{station}.webp|32px|link={station}]] [[{station}]]")

        return " or<br>".join(station_links)


def format_materials_column(materials):
    """Format materials with icon images and quantities."""
    if not materials:
        return "N/A"

    formatted_lines = []
    for material in materials:
        name = material['name']

        if material['is_range']:
            # Brew format: Name (small/medium/large)
            small = material['small']
            medium = material['medium']
            large = material['large']
            formatted_lines.append(
                f"[[File:{name}.webp|32px|link={name}]] [[{name}]] ({small}/{medium}/{large})"
            )
        else:
            # Regular format: Name (count)
            count = material['count']
            formatted_lines.append(
                f"[[File:{name}.webp|32px|link={name}]] [[{name}]] ({count})"
            )

    return "<br>".join(formatted_lines)


def generate_used_in_section_simple(usage_list):
    """Generate the 'Used In' wiki section for items/ores (simple format).

    Args:
        usage_list: List of dicts with recipe usage information

    Returns:
        str: Formatted wiki text for the Used In section
    """
    if not usage_list:
        return ""

    lines = []
    lines.append("")
    lines.append("==Used In==")
    lines.append("")
    lines.append("{{PAGENAME}} is used in the following crafting recipes:")
    lines.append("")

    # Group recipes by category
    categories = defaultdict(list)
    for usage in usage_list:
        categories[usage['category']].append(usage['recipe_name'])

    # Sort categories and recipes within each category
    for category in sorted(categories.keys()):
        lines.append(f"* {category}")
        for recipe_name in sorted(categories[category]):
            lines.append(f"** {{{{LI|{recipe_name}}}}}")

    return "\n".join(lines)


def generate_used_in_section_detailed(usage_list):
    """Generate the 'Used In' wiki section for consumables (detailed table format).

    Args:
        usage_list: List of dicts with recipe usage information

    Returns:
        str: Formatted wiki text for the Used In section
    """
    if not usage_list:
        return ""

    lines = []
    lines.append("")
    lines.append("==Used In==")
    lines.append("")
    lines.append('{| class="wikitable sortable"')
    lines.append('! Recipe !! Crafting Station !! Materials')

    for usage in sorted(usage_list, key=lambda x: x['recipe_name']):
        recipe_name = usage['recipe_name']
        stations = usage['stations']
        materials = usage['all_materials']
        is_brew = usage['is_brew']

        recipe_col = format_recipe_column(recipe_name)
        station_col = format_station_column(stations, is_brew)
        materials_col = format_materials_column(materials)

        lines.append('|-')
        lines.append(f'| {recipe_col}')
        lines.append(f'| {station_col}')
        lines.append(f'| {materials_col}')

    lines.append('|}')

    return "\n".join(lines)


def update_wiki_file_with_crossref(filepath, used_in_section):
    """Update a wiki file by adding or replacing the Used In section.

    Args:
        filepath: Path to the wiki file
        used_in_section: Formatted Used In section text
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if Used In section already exists
    if '==Used In==' in content:
        # Replace existing section
        # Find the section and replace it up to the next section or end
        pattern = r'==Used In==.*?(?=\n==|\n\{\{Navbox|$)'
        content = re.sub(pattern, used_in_section.strip(), content, flags=re.DOTALL)
    else:
        # Add new section before the navbox
        navbox_pattern = r'(\{\{Navbox [^}]+\}\})'
        navbox_match = re.search(navbox_pattern, content)

        if navbox_match:
            # Insert before navbox
            insert_pos = navbox_match.start()
            content = content[:insert_pos] + used_in_section + "\n\n" + content[insert_pos:]
        else:
            # Append at end
            content = content.rstrip() + "\n" + used_in_section + "\n"

    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """Main processing function."""
    print("Cross-Reference Wiki Generator")
    print("=" * 80)
    print()

    # Build list of all target items
    target_items = []
    for directory in TARGET_DIRS:
        if not os.path.exists(directory):
            print(f"Warning: Directory not found: {directory}")
            continue

        for filename in os.listdir(directory):
            if not filename.endswith('.wiki'):
                continue

            filepath = os.path.join(directory, filename)
            item_name = os.path.splitext(filename)[0]
            target_items.append((item_name, filepath))

    print(f"Found {len(target_items)} target items to process")
    print()

    # Process each target item
    updated_count = 0
    skipped_count = 0

    for item_name, filepath in target_items:
        print(f"Processing: {item_name}...")

        # Find where this item is used
        usage_list = find_material_usage(item_name, SEARCH_DIRS)

        if usage_list:
            print(f"  Found {len(usage_list)} recipes using this item")

            # Determine which format to use based on directory
            # Consumables use detailed table format, items/ores use simple list format
            if "output/consumables" in filepath.replace("\\", "/"):
                used_in_section = generate_used_in_section_detailed(usage_list)
            else:
                used_in_section = generate_used_in_section_simple(usage_list)

            # Update wiki file
            update_wiki_file_with_crossref(filepath, used_in_section)
            updated_count += 1
        else:
            print(f"  No recipes found using this item")
            skipped_count += 1

    print()
    print("=" * 80)
    print(f"Processing complete!")
    print(f"  Updated: {updated_count} files")
    print(f"  Skipped (no usage): {skipped_count} files")
    print(f"  Total processed: {len(target_items)} files")


if __name__ == "__main__":
    main()
