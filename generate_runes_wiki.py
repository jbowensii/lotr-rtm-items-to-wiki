import json
import os

# Paths
SOURCE_DIR = "source"
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")
RUNES_FILE = os.path.join(SOURCE_DIR, "DT_Runes.json")
OUTPUT_DIR = os.path.join("output", "runes")

# DLC detection patterns
DLC_PATH_PATTERNS = {
    "BeornPack": "The Beorn's Lodge Pack",
    "DurinsFolk": "Durin's Folk Expansion",
    "Elven": "Durin's Folk Expansion",
    "EntPack": "The Ent-craft Pack",
    "Holiday2025": "The Yule-tide Pack",
    "HolidayPack": "The Yule-tide Pack",
    "LordOfMoria": "End Game Award",
    "OrcHunterPack": "The Orc Hunter Pack",
    "OriginCosmetics": "Return to Moria",
    "RohanPack": "The Rohan Pack",
}

# Special campaign unlock overrides for items with unique unlock methods
CAMPAIGN_UNLOCK_OVERRIDE = {
}

# Special sandbox unlock overrides for items with unique unlock methods
SANDBOX_UNLOCK_OVERRIDE = {
}


def load_all_string_tables(strings_dir):
    """Load all string tables from the strings directory."""
    string_map = {}

    for filename in os.listdir(strings_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(strings_dir, filename)
            print(f"  Loading {filename}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Parse UAssetAPI string table format
                exports = data.get("Exports", [])
                file_string_count = 0

                for export in exports:
                    table = export.get("Table", {})
                    if table and isinstance(table, dict):
                        # The table has a 'Value' which is a list of [key, value] pairs
                        entries = table.get("Value", [])
                        if isinstance(entries, list):
                            for entry in entries:
                                if isinstance(entry, list) and len(entry) == 2:
                                    key, value = entry
                                    string_map[key] = value
                                    file_string_count += 1

                print(f"    Found {file_string_count} strings")

    return string_map


def load_runes_data(filepath):
    """Load DT_Runes.json and return a list of rune entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    runes_list = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            rune_entries = table.get("Data", [])
            runes_list.extend(rune_entries)

    return runes_list


def get_property_value(properties, prop_name):
    """Extract a property value from the list of properties."""
    for prop in properties:
        if prop.get("Name") == prop_name:
            return prop.get("Value")
    return None


def get_string_property(properties, prop_name, string_map):
    """Get a string property and look it up in the string map."""
    # Find the property
    prop = None
    for p in properties:
        if p.get("Name") == prop_name:
            prop = p
            break

    if not prop:
        return None

    # Check HistoryType to determine how to extract the string
    history_type = prop.get("HistoryType")

    # If HistoryType is "Base", use CultureInvariantString
    if history_type == "Base":
        culture_string = prop.get("CultureInvariantString")
        if culture_string:
            return culture_string

    # For TextPropertyData with StringTableEntry, get the Value which contains the string table key
    value = prop.get("Value")
    if not value:
        return None

    # If it's a string (not a GUID), try to look it up in the string table
    if isinstance(value, str):
        # Try direct lookup
        display_value = string_map.get(value)
        if display_value:
            return display_value

        # Try suffix matching
        suffix = value.split('.')[-1] if '.' in value else value
        for key, val in string_map.items():
            if key.endswith(f".{suffix}"):
                return val

    return value


def get_tags_list(properties):
    """Extract tags array from properties."""
    tags_prop = get_property_value(properties, "Tags")
    if not tags_prop or not isinstance(tags_prop, list):
        return []

    tags = []
    for tag_container in tags_prop:
        tag_values = tag_container.get("Value")
        if tag_values and isinstance(tag_values, list):
            tags.extend(tag_values)

    return tags


def get_crafting_materials(properties):
    """Extract crafting materials from DefaultRequiredMaterials property."""
    materials = []
    for prop in properties:
        if prop.get("Name") == "DefaultRequiredMaterials":
            material_list = prop.get("Value", [])
            for mat_struct in material_list:
                mat_props = mat_struct.get("Value", [])
                mat_name = None
                mat_count = None
                for mat_prop in mat_props:
                    if mat_prop.get("Name") == "MaterialHandle":
                        handle_props = mat_prop.get("Value", [])
                        for handle_prop in handle_props:
                            if handle_prop.get("Name") == "RowName":
                                mat_name = handle_prop.get("Value")
                    elif mat_prop.get("Name") == "Count":
                        mat_count = mat_prop.get("Value")
                if mat_name:
                    materials.append((mat_name, mat_count))
    return materials


def detect_dlc(icon_path):
    """Detect if an item is from a DLC based on asset paths."""
    if icon_path and isinstance(icon_path, int):
        # Icon path is an index reference, can't detect DLC from it
        return False, None, None

    paths = [icon_path]
    for path in paths:
        if path and isinstance(path, dict):
            asset_path_obj = path.get("AssetPath")
            if asset_path_obj and isinstance(asset_path_obj, dict):
                asset_name = asset_path_obj.get("AssetName", "")
                if isinstance(asset_name, str):
                    for dlc_key, dlc_name in DLC_PATH_PATTERNS.items():
                        if dlc_key in asset_name:
                            return True, f"{{{{LI|{dlc_name}}}}}", dlc_name
    return False, None, None


def get_material_display_name(material_key, string_map):
    """Get display name for a crafting material using string table lookup patterns."""
    # Try multiple lookup patterns (similar to storage_wiki.py)
    if material_key.startswith("Item."):
        item_suffix = material_key.replace("Item.", "")
        # Try Items.Items.XXX.Name first
        lookup_key1 = f"Items.Items.{item_suffix}.Name"
        display_name = string_map.get(lookup_key1)

        # Try Items.XXX.Name as fallback
        if not display_name:
            lookup_key2 = f"Items.{item_suffix}.Name"
            display_name = string_map.get(lookup_key2)

        if display_name:
            return display_name

    # If still not found, try suffix matching
    suffix = material_key.split('.')[-1] if '.' in material_key else material_key
    for key, val in string_map.items():
        if key.endswith(f".{suffix}.Name"):
            return val

    # Fall back to removing "Item." prefix if still not found
    if material_key.startswith("Item."):
        return material_key.replace("Item.", "")

    return material_key


def determine_rune_subtype(tags, display_name):
    """Determine the subtype of rune based on tags and name."""
    subtype = ""

    # Check for damage type tags
    if "Damage.Fire" in tags:
        subtype = "Fire"
    elif "Damage.Cold" in tags:
        subtype = "Ice"
    elif "Damage.Thunder" in tags:
        subtype = "Thunder"
    elif "Damage.Light" in tags:
        subtype = "Light"
    elif "Damage.Shadow" in tags:
        subtype = "Shadow"
    elif "Damage.Poison" in tags:
        subtype = "Poison"
    elif "Damage.AntiDragon" in tags:
        subtype = "Dragonbane"
    elif "Damage.AntiOrc" in tags:
        subtype = "Orc Slayer"
    elif "Damage.Hunters" in tags:
        subtype = "Hunter"
    elif "Damage.Whisperwood" in tags:
        subtype = "Whisperwood"

    return subtype


def generate_wiki_template(rune_model, string_map):
    """Generate MediaWiki template text for a rune."""
    lines = []

    # Item infobox
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(f" | name          = {rune_model['DisplayName']}")

    # Type
    lines.append(" | type          = Rune")

    # Subtype
    if rune_model.get("Subtype"):
        lines.append(f" | subtype       = {rune_model['Subtype']}")
    else:
        lines.append(" | subtype       = ")

    # Tags
    if rune_model.get("Tags"):
        lines.append(f" | tags          = {', '.join(rune_model['Tags'])}")

    lines.append("}}")
    lines.append("")
    lines.append("'''{{PAGENAME}}''' is a [[Rune]] in ''[[{{topic}}]]''.")

    # Description section (only if non-empty)
    if rune_model.get("Description") and rune_model["Description"].strip():
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {rune_model['Description']}")

    # Item Prefix section (only if non-empty)
    if rune_model.get("ItemPrefix") and rune_model["ItemPrefix"].strip():
        lines.append("")
        lines.append("==Prefix==")
        lines.append(f"When inscribed on a weapon, this rune grants the prefix: '''{rune_model['ItemPrefix']}'''")

    # Unlocks section (only if unlock overrides exist)
    if rune_model.get("CampaignUnlock") or rune_model.get("SandboxUnlock"):
        lines.append("")
        lines.append("== Unlocks ==")
        lines.append("")
        if rune_model.get("CampaignUnlock"):
            lines.append(f"* Campaign {{{{spoiler|{rune_model['CampaignUnlock']}}}}}")
        if rune_model.get("SandboxUnlock"):
            lines.append(f"* Sandbox  {{{{spoiler|{rune_model['SandboxUnlock']}}}}}")

    # Crafting section (only if materials exist)
    if rune_model.get("CraftingMaterials"):
        lines.append("")
        lines.append("==Crafting==")
        lines.append("Materials:")
        lines.append("")
        for mat_name, mat_count in rune_model["CraftingMaterials"]:
            # Look up display name in string tables
            display_name = get_material_display_name(mat_name, string_map)
            lines.append(f"* ({mat_count}) {{{{LI|{display_name}}}}}")

    # DLC section (if applicable)
    if rune_model.get("DLC"):
        lines.append("")
        lines.append("==Availability==")
        lines.append(f"This item is part of the {rune_model['DLCTitle']}.")

    return "\n".join(lines)


def process_runes(runes_data, string_map):
    """Process all runes and generate wiki models."""
    print("\nProcessing runes...")
    rune_models = []
    excluded_runes = []

    for rune_entry in runes_data:
        rune_name = rune_entry.get("Name", "")

        # Skip UNSHIPPABLE items
        if "UNSHIPPABLE" in rune_name:
            excluded_runes.append({
                "name": rune_name,
                "reason": "UNSHIPPABLE item"
            })
            continue

        # Get properties
        properties = rune_entry.get("Value", [])

        # Extract basic info
        display_name = get_string_property(properties, "DisplayName", string_map)
        description = get_string_property(properties, "Description", string_map)
        item_prefix = get_string_property(properties, "ItemPrefix", string_map)
        icon_path = get_property_value(properties, "Icon")

        # Skip if no display name
        if not display_name:
            excluded_runes.append({
                "name": rune_name,
                "reason": "No display name"
            })
            continue

        # Skip items with template placeholders in name
        if "{" in display_name or "}" in display_name:
            excluded_runes.append({
                "name": rune_name,
                "reason": "Template placeholder in name"
            })
            continue

        # Extract tags
        tags = get_tags_list(properties)

        # Extract crafting materials
        crafting_materials = get_crafting_materials(properties)

        # Determine subtype
        subtype = determine_rune_subtype(tags, display_name)

        # Build rune model
        rune_model = {
            "Name": rune_name,
            "DisplayName": display_name,
            "Description": description or "",
            "ItemPrefix": item_prefix or "",
            "Type": "Rune",
            "Subtype": subtype,
            "IconPath": icon_path or "",
            "Tags": tags,
            "CraftingMaterials": crafting_materials,
        }

        # Detect DLC
        is_dlc, dlc_title, dlc_name = detect_dlc(rune_model["IconPath"])
        if is_dlc:
            rune_model["DLC"] = True
            rune_model["DLCTitle"] = dlc_title
            rune_model["DLCName"] = dlc_name
        else:
            rune_model["DLC"] = False

        # Check for unlock overrides
        if display_name in CAMPAIGN_UNLOCK_OVERRIDE:
            rune_model["CampaignUnlock"] = CAMPAIGN_UNLOCK_OVERRIDE[display_name]
        if display_name in SANDBOX_UNLOCK_OVERRIDE:
            rune_model["SandboxUnlock"] = SANDBOX_UNLOCK_OVERRIDE[display_name]

        rune_models.append(rune_model)

    print(f"  Processed {len(rune_models)} runes")
    print(f"  Excluded {len(excluded_runes)} runes")
    return rune_models, excluded_runes


def sanitize_filename(filename):
    """Sanitize a filename by removing invalid characters."""
    # Remove invalid Windows filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename


def write_wiki_files(rune_models, output_dir, string_map):
    """Write wiki files for all runes."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nWriting wiki files to {output_dir}...")
    for rune_model in rune_models:
        display_name = sanitize_filename(rune_model['DisplayName'])
        filename = f"{display_name}.wiki"
        filepath = os.path.join(output_dir, filename)

        wiki_content = generate_wiki_template(rune_model, string_map)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(rune_models)} wiki files")


def write_excluded_log(excluded_runes, output_root):
    """Write a log of excluded runes."""
    if not excluded_runes:
        return

    log_path = os.path.join(output_root, "excluded_runes.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Excluded {len(excluded_runes)} runes:\n\n")
        for item in excluded_runes:
            f.write(f"{item['name']}: {item['reason']}\n")
    print(f"\nWrote exclusion log to {log_path}")


def main():
    print("Loading data...")

    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"  Total strings: {len(string_map)}")

    # Load runes data
    print("Loading runes data...")
    runes_data = load_runes_data(RUNES_FILE)
    print(f"  Total runes: {len(runes_data)}")

    # Process runes
    rune_models, excluded_runes = process_runes(runes_data, string_map)

    # Write wiki files
    write_wiki_files(rune_models, OUTPUT_DIR, string_map)

    # Write exclusion log to output root directory
    if excluded_runes:
        write_excluded_log(excluded_runes, "output")

    print("\nDone!")


if __name__ == "__main__":
    main()
