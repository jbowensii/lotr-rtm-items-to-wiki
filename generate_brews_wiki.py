import json
import os

# Paths
SOURCE_DIR = "source"
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")
BREWS_FILE = os.path.join(SOURCE_DIR, "DT_Brews.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join("output", "brews")

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


def load_brews_data(filepath):
    """Load DT_Brews.json and return a list of brew entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    brews_list = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            brew_entries = table.get("Data", [])
            brews_list.extend(brew_entries)

    return brews_list


def load_recipes_data(filepath):
    """Load DT_ItemRecipes.json and return a dict of recipe materials by item name."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes_dict = {}
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            recipe_entries = table.get("Data", [])
            for recipe_entry in recipe_entries:
                recipe_name = recipe_entry.get("Name", "")
                properties = recipe_entry.get("Value", [])

                # Extract materials
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

                if materials:
                    recipes_dict[recipe_name] = materials

    return recipes_dict


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


def detect_dlc(actor_path, icon_path):
    """Detect if an item is from a DLC based on asset paths."""
    paths = [actor_path, icon_path]
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


def generate_wiki_template(brew_model, string_map):
    """Generate MediaWiki template text for a brew."""
    lines = []

    # Item infobox
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(f" | name          = {brew_model['DisplayName']}")

    # Type
    lines.append(" | type          = Brew")

    # Subtype
    if brew_model.get("Subtype"):
        lines.append(f" | subtype       = {brew_model['Subtype']}")
    else:
        lines.append(" | subtype       = ")

    # Stack size
    if brew_model.get("MaxStackSize"):
        lines.append(f" | stack         = {brew_model['MaxStackSize']}")

    # Tags
    if brew_model.get("Tags"):
        lines.append(f" | tags          = {', '.join(brew_model['Tags'])}")

    lines.append("}}")
    lines.append("")
    lines.append("'''{{PAGENAME}}''' is a [[Brew]] in ''[[{{topic}}]]''.")

    # Description section (only if non-empty)
    if brew_model.get("Description") and brew_model["Description"].strip():
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {brew_model['Description']}")

    # Unlocks section (only if unlock overrides exist)
    if brew_model.get("CampaignUnlock") or brew_model.get("SandboxUnlock"):
        lines.append("")
        lines.append("== Unlocks ==")
        lines.append("")
        if brew_model.get("CampaignUnlock"):
            lines.append(f"* Campaign {{{{spoiler|{brew_model['CampaignUnlock']}}}}}")
        if brew_model.get("SandboxUnlock"):
            lines.append(f"* Sandbox  {{{{spoiler|{brew_model['SandboxUnlock']}}}}}")

    # Stats section (only if has any positive stats)
    has_stats = (
        (brew_model.get("HungerRestore") and brew_model["HungerRestore"] > 0) or
        (brew_model.get("HealthRestore") and brew_model["HealthRestore"] > 0) or
        (brew_model.get("EnergyRestore") and brew_model["EnergyRestore"] > 0)
    )

    if has_stats:
        lines.append("")
        lines.append("==Stats==")

        if brew_model.get("HungerRestore") and brew_model["HungerRestore"] > 0:
            lines.append(f"* '''Hunger:''' {brew_model['HungerRestore']}")

        if brew_model.get("HealthRestore") and brew_model["HealthRestore"] > 0:
            lines.append(f"* '''Health:''' {brew_model['HealthRestore']}")

        if brew_model.get("EnergyRestore") and brew_model["EnergyRestore"] > 0:
            lines.append(f"* '''Energy:''' {brew_model['EnergyRestore']}")

    # Crafting section (only if materials exist)
    if brew_model.get("CraftingMaterials"):
        lines.append("")
        lines.append("==Crafting==")
        lines.append("Materials:")
        lines.append("")
        for mat_name, mat_count in brew_model["CraftingMaterials"]:
            # Look up display name in string tables
            display_name = get_material_display_name(mat_name, string_map)
            lines.append(f"* ({mat_count}) {{{{LI|{display_name}}}}}")

    # DLC section (if applicable)
    if brew_model.get("DLC"):
        lines.append("")
        lines.append("==Availability==")
        lines.append(f"This item is part of the {brew_model['DLCTitle']}.")

    return "\n".join(lines)


def process_brews(brews_data, string_map, recipes_dict):
    """Process all brews and generate wiki models."""
    print("\nProcessing brews...")
    brew_models = []
    excluded_brews = []

    for brew_entry in brews_data:
        brew_name = brew_entry.get("Name", "")

        # Skip UNSHIPPABLE items
        if "UNSHIPPABLE" in brew_name:
            excluded_brews.append({
                "name": brew_name,
                "reason": "UNSHIPPABLE item"
            })
            continue

        # Get properties
        properties = brew_entry.get("Value", [])

        # Extract basic info
        display_name = get_string_property(properties, "DisplayName", string_map)
        description = get_string_property(properties, "Description", string_map)
        icon_path = get_property_value(properties, "Icon")
        actor_path = get_property_value(properties, "Actor")

        # Skip if no display name
        if not display_name:
            excluded_brews.append({
                "name": brew_name,
                "reason": "No display name"
            })
            continue

        # Skip items with template placeholders in name
        if "{" in display_name or "}" in display_name:
            excluded_brews.append({
                "name": brew_name,
                "reason": "Template placeholder in name"
            })
            continue

        # Extract tags
        tags = get_tags_list(properties)

        # Build brew model
        brew_model = {
            "Name": brew_name,
            "DisplayName": display_name,
            "Description": description or "",
            "Type": "Brew",
            "Subtype": "",
            "IconPath": icon_path or "",
            "ActorPath": actor_path or "",
            "Tags": tags,
            "MaxStackSize": get_property_value(properties, "MaxStackSize"),
            "HungerRestore": get_property_value(properties, "HungerRestore"),
            "HealthRestore": get_property_value(properties, "HealthRestore"),
            "EnergyRestore": get_property_value(properties, "EnergyRestore"),
        }

        # Detect DLC
        is_dlc, dlc_title, dlc_name = detect_dlc(brew_model["ActorPath"], brew_model["IconPath"])
        if is_dlc:
            brew_model["DLC"] = True
            brew_model["DLCTitle"] = dlc_title
            brew_model["DLCName"] = dlc_name
        else:
            brew_model["DLC"] = False

        # Check for unlock overrides
        if display_name in CAMPAIGN_UNLOCK_OVERRIDE:
            brew_model["CampaignUnlock"] = CAMPAIGN_UNLOCK_OVERRIDE[display_name]
        if display_name in SANDBOX_UNLOCK_OVERRIDE:
            brew_model["SandboxUnlock"] = SANDBOX_UNLOCK_OVERRIDE[display_name]

        # Check for crafting recipe
        if brew_name in recipes_dict:
            brew_model["CraftingMaterials"] = recipes_dict[brew_name]

        brew_models.append(brew_model)

    print(f"  Processed {len(brew_models)} brews")
    print(f"  Excluded {len(excluded_brews)} brews")
    return brew_models, excluded_brews


def sanitize_filename(filename):
    """Sanitize a filename by removing invalid characters."""
    # Remove invalid Windows filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename


def write_wiki_files(brew_models, output_dir, string_map):
    """Write wiki files for all brews."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nWriting wiki files to {output_dir}...")
    for brew_model in brew_models:
        display_name = sanitize_filename(brew_model['DisplayName'])
        filename = f"{display_name}.wiki"
        filepath = os.path.join(output_dir, filename)

        wiki_content = generate_wiki_template(brew_model, string_map)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(brew_models)} wiki files")


def write_excluded_log(excluded_brews, output_root):
    """Write a log of excluded brews."""
    if not excluded_brews:
        return

    log_path = os.path.join(output_root, "excluded_brews.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Excluded {len(excluded_brews)} brews:\n\n")
        for item in excluded_brews:
            f.write(f"{item['name']}: {item['reason']}\n")
    print(f"\nWrote exclusion log to {log_path}")


def main():
    print("Loading data...")

    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"  Total strings: {len(string_map)}")

    # Load recipes data
    print("Loading recipes data...")
    recipes_dict = load_recipes_data(RECIPES_FILE)
    print(f"  Total recipes: {len(recipes_dict)}")

    # Load brews data
    print("Loading brews data...")
    brews_data = load_brews_data(BREWS_FILE)
    print(f"  Total brews: {len(brews_data)}")

    # Process brews
    brew_models, excluded_brews = process_brews(brews_data, string_map, recipes_dict)

    # Write wiki files
    write_wiki_files(brew_models, OUTPUT_DIR, string_map)

    # Write exclusion log to output root directory
    if excluded_brews:
        write_excluded_log(excluded_brews, "output")

    print("\nDone!")


if __name__ == "__main__":
    main()
