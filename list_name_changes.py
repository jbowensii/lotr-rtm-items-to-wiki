"""Generate explicit list of all name changes for material variants."""

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
    string_map = load_all_string_tables(STRINGS_DIR)

    # Load constructions
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
    material_variants = []

    for display_name, items in sorted(display_name_groups.items()):
        if len(items) > 1:
            materials = set(item["material"] for item in items)
            if len(materials) > 1:
                material_variants.append((display_name, items))

    print("="*80)
    print("EXPLICIT NAME CHANGES FOR MATERIAL VARIANTS")
    print("="*80)
    print()
    print(f"Total items being renamed: {sum(1 for _, items in material_variants for item in items if item['material'] != 'Base')}")
    print()

    # Collect all changes
    changes = []

    for display_name, items in material_variants:
        for item in sorted(items, key=lambda x: x["material"]):
            material = item["material"]
            internal = item["internal_name"]

            if material == "RedSandstone":
                new_name = f"Crimson {display_name}"
                changes.append((internal, display_name, new_name))
            elif material == "WhiteMarble":
                new_name = f"Fair {display_name}"
                changes.append((internal, display_name, new_name))

    # Sort and print changes
    print("RedSandstone variants (Crimson prefix):")
    print("-" * 80)
    crimson_changes = [c for c in changes if c[2].startswith("Crimson")]
    for internal, old_name, new_name in sorted(crimson_changes, key=lambda x: x[2]):
        print(f"{old_name} -> {new_name}")
        print(f"  (Internal: {internal})")
        print()

    print()
    print("="*80)
    print()

    print("WhiteMarble variants (Fair prefix):")
    print("-" * 80)
    fair_changes = [c for c in changes if c[2].startswith("Fair")]
    for internal, old_name, new_name in sorted(fair_changes, key=lambda x: x[2]):
        print(f"{old_name} -> {new_name}")
        print(f"  (Internal: {internal})")
        print()

    print()
    print("="*80)
    print(f"Total Crimson variants: {len(crimson_changes)}")
    print(f"Total Fair variants: {len(fair_changes)}")
    print(f"Total renamed: {len(changes)}")

if __name__ == "__main__":
    main()
