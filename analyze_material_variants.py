"""Analyze material variants and show proposed naming."""

import json
import os
from collections import defaultdict

SOURCE_DIR = "source"
CONSTRUCTIONS_FILE = os.path.join(SOURCE_DIR, "DT_Constructions.json")
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")

def load_all_string_tables(strings_dir):
    """Load all string tables from the strings directory."""
    string_map = {}

    for filename in os.listdir(strings_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(strings_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                exports = data.get("Exports", [])
                for export in exports:
                    table = export.get("Table", {})
                    if table and isinstance(table, dict):
                        entries = table.get("Value", [])
                        if isinstance(entries, list):
                            for entry in entries:
                                if isinstance(entry, list) and len(entry) == 2:
                                    key, value = entry
                                    string_map[key] = value

    return string_map

def get_property_value(properties, prop_name):
    """Extract a property value from the list of properties."""
    for prop in properties:
        if prop.get("Name") == prop_name:
            return prop.get("Value")
    return None

def resolve_string_table_reference(text_property, string_map):
    """Resolve a string table reference to its actual text."""
    if not text_property:
        return None

    if isinstance(text_property, str):
        return string_map.get(text_property)

    if isinstance(text_property, dict) and text_property.get("$type", "").endswith("TextPropertyData, UAssetAPI"):
        key = text_property.get("Value")
        if key and isinstance(key, str):
            return string_map.get(key)

    return None

def resolve_construction_display_name(name, properties, string_map):
    """Resolve construction display name with fallback strategies."""
    display_name_prop = get_property_value(properties, "DisplayName")
    display_name = resolve_string_table_reference(display_name_prop, string_map)

    if not display_name and name.startswith("_"):
        cleaned_name = name[1:]
        for key in [f"{cleaned_name}.Name", f"Constructions.{cleaned_name}.Name"]:
            if key in string_map:
                display_name = string_map[key]
                break

    if not display_name and name.startswith("CraftingStation_"):
        cleaned_name = name.replace("CraftingStation_", "")
        for key in [f"{cleaned_name}.Name", f"Constructions.{cleaned_name}", f"Constructions.{cleaned_name}.Name"]:
            if key in string_map:
                display_name = string_map[key]
                break

    return display_name

def should_exclude_construction(name, display_name):
    """Determine if a construction should be excluded based on naming rules."""
    if name.startswith("["):
        return True
    if name.startswith("_Beorn"):
        return True
    if "Broken" in name or (display_name and "Broken" in display_name):
        return True
    return False

def get_material_suffix(internal_name):
    """Determine material suffix from internal name."""
    if "_RedSandstone" in internal_name or internal_name.endswith("_RedSandstone"):
        return "RedSandstone"
    elif "_WhiteMarble" in internal_name or internal_name.endswith("_WhiteMarble"):
        return "WhiteMarble"
    else:
        return "Base"

def main():
    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)

    # Load constructions
    print("Loading constructions...")
    with open(CONSTRUCTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    constructions = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            constructions = table.get("Data", [])
            break

    # Group by display name
    display_name_groups = defaultdict(list)

    for construction in constructions:
        name = construction.get("Name", "")
        properties = construction.get("Value", [])

        # Check exclusions
        display_name = resolve_construction_display_name(name, properties, string_map)
        if should_exclude_construction(name, display_name):
            continue

        if display_name:
            material = get_material_suffix(name)
            display_name_groups[display_name].append({
                "internal_name": name,
                "display_name": display_name,
                "material": material
            })

    # Find groups with multiple materials
    print("\n" + "="*80)
    print("MATERIAL VARIANT MAPPINGS")
    print("="*80 + "\n")

    material_variants = []

    for display_name, items in sorted(display_name_groups.items()):
        if len(items) > 1:
            # Check if they're material variants
            materials = set(item["material"] for item in items)
            if len(materials) > 1:
                material_variants.append((display_name, items))

    print(f"Found {len(material_variants)} display names with material variants\n")

    # Show mappings
    for display_name, items in material_variants:
        print(f"Display Name: {display_name}")
        print("-" * 40)

        for item in sorted(items, key=lambda x: x["material"]):
            material = item["material"]
            internal = item["internal_name"]

            if material == "RedSandstone":
                proposed_name = f"Crimson {display_name}"
                print(f"  Internal: {internal}")
                print(f"  Material: RedSandstone")
                print(f"  Current:  {display_name}")
                print(f"  Proposed: {proposed_name}")
            elif material == "WhiteMarble":
                proposed_name = f"Fair {display_name}"
                print(f"  Internal: {internal}")
                print(f"  Material: WhiteMarble")
                print(f"  Current:  {display_name}")
                print(f"  Proposed: {proposed_name}")
            else:
                print(f"  Internal: {internal}")
                print(f"  Material: Base")
                print(f"  Current:  {display_name}")
                print(f"  Proposed: {display_name} (unchanged)")

            print()

        print()

if __name__ == "__main__":
    main()
