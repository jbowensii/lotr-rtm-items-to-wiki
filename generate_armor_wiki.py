import json
import os
import re

# Paths
SOURCE_DIR = "source"
STRINGS_FILE = os.path.join(SOURCE_DIR, "strings", "items.json")
ARMOR_FILE = os.path.join(SOURCE_DIR, "DT_Armor.json")
OUTPUT_DIR = os.path.join("output", "armor")


def load_string_table(filepath):
    """Load the items.json string table and return a key->value dictionary."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    string_map = {}
    # Navigate to Exports[0].Table.Value which contains the string pairs
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.StringTableExport, UAssetAPI":
            table = export.get("Table", {})
            values = table.get("Value", [])
            for pair in values:
                if isinstance(pair, list) and len(pair) == 2:
                    key, value = pair
                    string_map[key] = value

    return string_map


def load_armor_data(filepath):
    """Load DT_Armor.json and return the list of armor entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    armor_list = []
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.DataTableExport, UAssetAPI":
            table = export.get("Table", {})
            armor_entries = table.get("Data", [])
            armor_list.extend(armor_entries)

    return armor_list


def get_property_value(properties, prop_name):
    """Get a property value from a list of property objects."""
    for prop in properties:
        if prop.get("Name") == prop_name:
            return prop.get("Value")
    return None


def extract_armor_model(armor_entry, string_map):
    """Extract our data model from an armor entry."""
    game_name = armor_entry.get("Name", "")
    properties = armor_entry.get("Value", [])

    model = {
        "GameName": game_name,
        "Durability": 0,
        "DamageReduction": 0.0,
        "DamageProtection": 0.0,
        "DisplayNameKey": "",
        "DisplayName": "",
        "DescriptionKey": "",
        "Description": "",
        "DamageModifiers": "",
        "SkillsGranted": "",
        "SkillsRequired": "",
        "Type": "",
        "SubType": "",
        "Tier": "",
        "Icon": "",
        "RepairCost": 0
    }

    for prop in properties:
        prop_name = prop.get("Name", "")
        prop_value = prop.get("Value")

        if prop_name == "Durability":
            model["Durability"] = prop_value

        elif prop_name == "DamageReduction":
            model["DamageReduction"] = prop_value

        elif prop_name == "DamageProtection":
            model["DamageProtection"] = prop_value

        elif prop_name == "DisplayName":
            model["DisplayNameKey"] = prop_value
            model["DisplayName"] = string_map.get(prop_value, prop_value)

        elif prop_name == "Description":
            model["DescriptionKey"] = prop_value
            model["Description"] = string_map.get(prop_value, prop_value)

        elif prop_name == "DamageModifiers":
            # Extract RowName values from the array
            modifiers = []
            if isinstance(prop_value, list):
                for item in prop_value:
                    inner_values = item.get("Value", [])
                    for inner in inner_values:
                        if inner.get("Name") == "RowName":
                            modifiers.append(inner.get("Value", ""))
            model["DamageModifiers"] = ", ".join(modifiers)

        elif prop_name == "SkillsGranted":
            # Extract from GameplayTagContainer
            skills = []
            if isinstance(prop_value, list):
                for item in prop_value:
                    if item.get("Name") == "SkillsGranted":
                        skills.extend(item.get("Value", []))
            model["SkillsGranted"] = ", ".join(skills)

        elif prop_name == "SkillsRequired":
            # Extract from GameplayTagContainer
            skills = []
            if isinstance(prop_value, list):
                for item in prop_value:
                    if item.get("Name") == "SkillsRequired":
                        skills.extend(item.get("Value", []))
            model["SkillsRequired"] = ", ".join(skills)

        elif prop_name == "Tags":
            # Parse tags: UI.Armor.Torso.Tier3 -> Type=Armor, SubType=Torso, Tier=Tier3
            if isinstance(prop_value, list):
                for item in prop_value:
                    if item.get("Name") == "Tags":
                        tags = item.get("Value", [])
                        for tag in tags:
                            parts = tag.split(".")
                            # Remove "UI" prefix if present
                            if parts and parts[0] == "UI":
                                parts = parts[1:]
                            if len(parts) >= 1:
                                model["Type"] = parts[0]
                            if len(parts) >= 2:
                                model["SubType"] = parts[1]
                            if len(parts) >= 3:
                                model["Tier"] = parts[2]

        elif prop_name == "Icon":
            # Extract asset path
            if isinstance(prop_value, dict):
                asset_path = prop_value.get("AssetPath", {})
                model["Icon"] = asset_path.get("AssetName", "")

        elif prop_name == "InitialRepairCost":
            # Extract Count from the nested structure
            if isinstance(prop_value, list):
                for item in prop_value:
                    inner_values = item.get("Value", [])
                    for inner in inner_values:
                        if inner.get("Name") == "Count":
                            model["RepairCost"] = inner.get("Value", 0)

    return model


def strip_rich_text(text):
    """Remove in-game rich text markup like <Inventory.Regular.White>...</>"""
    # Pattern matches <SomeTag>content</> and replaces with just content
    pattern = r'<[^>]+>([^<]*)</>'
    result = re.sub(pattern, r'\1', text)
    return result


def format_tier(tier):
    """Convert Tier3 to 3, etc."""
    if tier.startswith("Tier"):
        return tier[4:]
    return tier


def generate_wiki_template(model):
    """Generate MediaWiki template from the data model."""

    # Clean up description
    description = strip_rich_text(model["Description"])

    # Format tier
    tier = format_tier(model["Tier"])

    # Build damage modifiers line if present
    damage_modifiers_line = ""
    if model["DamageModifiers"]:
        damage_modifiers_line = f"\nDamage Modifiers: {model['DamageModifiers']}\n"

    template = f"""{{{{Item
 | title         = {{{{PAGENAME}}}}
 | image         = {{{{PAGENAME}}}}.webp
 | imagecaption  =
 | type          = {model['Type']}
 | subtype       = {model['SubType']}
 | tier          = {tier}
}}}}
'''{{{{PAGENAME}}}}''' is a {model['SubType']} {model['Type']} [[item]] in ''[[{{{{topic}}}}]]''.

==Description==

In-game: ''{description}''

== Unlocks ==

* Campaign {{{{spoiler|???}}}}
* Sandbox  {{{{spoiler|???}}}}

== Stats ==

Durability: {model['Durability']}

Armor Protection: {model['DamageProtection']}

Armor Effectiveness: {model['DamageReduction']}
{damage_modifiers_line}
Max Repair Cost: {model['RepairCost']} {{{{LI|Scrap}}}}

== Crafting ==

Time: ??? seconds

Station:

* {{{{LI|???}}}}

Materials:

* {{{{LI|???}}}}

{{{{Navbox items}}}}
[[Category:Tier {tier} Items]]
[[Category:{model['SubType']}s]]
"""

    return template


def sanitize_filename(name):
    """Sanitize a string to be used as a filename."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name


def should_exclude(model):
    """Check if an item should be excluded. Returns (exclude: bool, reason: str)."""
    display_name = model.get("DisplayName", "")

    # No display name
    if not display_name:
        return True, "No display name"

    # Name doesn't start with a letter
    if not display_name[0].isalpha():
        return True, f"Name begins with non-letter: '{display_name[0]}'"

    return False, ""


def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    print("Loading string table...")
    string_map = load_string_table(STRINGS_FILE)
    print(f"Loaded {len(string_map)} strings")

    print("Loading armor data...")
    armor_list = load_armor_data(ARMOR_FILE)
    print(f"Loaded {len(armor_list)} armor entries")

    # Process each armor entry
    count = 0
    excluded = []

    for armor_entry in armor_list:
        model = extract_armor_model(armor_entry, string_map)

        # Check exclusion rules
        exclude, reason = should_exclude(model)
        if exclude:
            excluded.append({
                "GameName": model["GameName"],
                "DisplayName": model.get("DisplayName", ""),
                "Reason": reason
            })
            print(f"Excluding {model['GameName']} - {reason}")
            continue

        # Generate wiki template
        wiki_content = generate_wiki_template(model)

        # Write to file using DisplayName as filename
        filename = sanitize_filename(model["DisplayName"]) + ".wiki"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

        count += 1
        print(f"Generated: {filename}")

    # Write exclusion log
    if excluded:
        log_path = os.path.join("output", "excluded_armor.log")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Excluded Armor Items ({len(excluded)} total)\n")
            f.write("=" * 50 + "\n\n")
            for item in excluded:
                f.write(f"GameName: {item['GameName']}\n")
                f.write(f"DisplayName: {item['DisplayName']}\n")
                f.write(f"Reason: {item['Reason']}\n")
                f.write("-" * 30 + "\n")
        print(f"\nExclusion log written to {log_path}")

    print(f"\nDone! Generated {count} wiki templates in {OUTPUT_DIR}")
    print(f"Excluded {len(excluded)} items")


if __name__ == "__main__":
    main()
