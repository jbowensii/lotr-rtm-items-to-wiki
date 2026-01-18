import json
import os

# Paths - Updated for new datajson structure
OUTPUT_BASE = os.path.join(os.environ.get("APPDATA", ""), "MoriaWikiGenerator", "output")
SOURCE_DIR = os.path.join(OUTPUT_BASE, "datajson", "Moria", "Content", "Tech", "Data")
STRINGS_DIR = os.path.join(SOURCE_DIR, "StringTables")
ORES_FILE = os.path.join(SOURCE_DIR, "Items", "DT_Ores.json")
OUTPUT_DIR = os.path.join(OUTPUT_BASE, "wiki", "ores")

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

# Load unlock overrides from JSON file
def load_unlock_overrides():
    """Load unlock overrides from ore_unlock_overrides.json"""
    override_file = "ore_unlock_overrides.json"
    if os.path.exists(override_file):
        with open(override_file, 'r', encoding='utf-8') as f:
            overrides = json.load(f)
            campaign_overrides = {}
            sandbox_overrides = {}
            for item_name, unlock_data in overrides.items():
                if "campaign" in unlock_data:
                    campaign_overrides[item_name] = unlock_data["campaign"]
                if "sandbox" in unlock_data:
                    sandbox_overrides[item_name] = unlock_data["sandbox"]
            return campaign_overrides, sandbox_overrides
    return {}, {}

# Load overrides at module level
CAMPAIGN_UNLOCK_OVERRIDE, SANDBOX_UNLOCK_OVERRIDE = load_unlock_overrides()


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


def load_ores_data(filepath):
    """Load DT_Ores.json and return a list of ore entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ores_list = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            ore_entries = table.get("Data", [])
            ores_list.extend(ore_entries)

    return ores_list


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


def determine_ore_type(tags, display_name):
    """Determine the type and subtype of ore based on tags and name."""
    ore_type = "Ore"
    subtype = ""

    # Check tags for specific types
    if "Item.Mineral.Ore" in tags:
        ore_type = "Ore"
    if "Item.Mineral.Gem" in tags:
        ore_type = "Gem"
    if "Item.Mineral.Stone" in tags:
        ore_type = "Stone"

    # Determine subtype from name or tags
    gem_keywords = ["Diamond", "Ruby", "Emerald", "Sapphire", "Amethyst", "Topaz",
                    "Citrine", "Garnet", "Jade", "Onyx", "Opal", "Beryl", "Iolite",
                    "Quartz", "Lapis"]

    stone_keywords = ["Granite", "Marble", "Obsidian", "Sandstone", "Pumice"]

    for gem in gem_keywords:
        if gem.lower() in display_name.lower():
            ore_type = "Gem"
            break

    for stone in stone_keywords:
        if stone.lower() in display_name.lower():
            ore_type = "Stone"
            break

    return ore_type, subtype


def generate_wiki_template(ore_model):
    """Generate MediaWiki template text for an ore."""
    lines = []

    # Item infobox
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(f" | name          = {ore_model['DisplayName']}")

    # Type
    if ore_model.get("Type"):
        lines.append(f" | type          = {ore_model['Type']}")
    else:
        lines.append(" | type          = ")

    # Subtype
    if ore_model.get("Subtype"):
        lines.append(f" | subtype       = {ore_model['Subtype']}")
    else:
        lines.append(" | subtype       = ")

    # Stack size
    if ore_model.get("MaxStackSize"):
        lines.append(f" | stack         = {ore_model['MaxStackSize']}")

    # Value
    if ore_model.get("BaseTradeValue"):
        lines.append(f" | value         = {ore_model['BaseTradeValue']}")

    # Tags
    if ore_model.get("Tags"):
        lines.append(f" | tags          = {', '.join(ore_model['Tags'])}")

    # Requirements
    lines.append(" | reqs          = Harvestable")

    lines.append("}}")
    lines.append("")
    lines.append(f"'''{{{{PAGENAME}}}}''' is a [[{ore_model['Type']}]] in ''[[{{{{topic}}}}]]''.")

    # Description section (only if non-empty)
    if ore_model.get("Description") and ore_model["Description"].strip():
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {ore_model['Description']}")

    # Unlocks section (only if unlock overrides exist)
    if ore_model.get("CampaignUnlock") or ore_model.get("SandboxUnlock"):
        lines.append("")
        lines.append("== Unlock ==")
        if ore_model.get("CampaignUnlock"):
            lines.append(f"'''Campaign:''' {ore_model['CampaignUnlock']}")
        if ore_model.get("SandboxUnlock"):
            lines.append(f"'''Sandbox:''' {ore_model['SandboxUnlock']}")

    # DLC section (if applicable)
    if ore_model.get("DLC"):
        lines.append("")
        lines.append("==Availability==")
        lines.append(f"This item is part of the {ore_model['DLCTitle']}.")

    return "\n".join(lines)


def process_ores(ores_data, string_map):
    """Process all ores and generate wiki models."""
    print("\nProcessing ores...")
    ore_models = []
    excluded_ores = []

    for ore_entry in ores_data:
        ore_name = ore_entry.get("Name", "")

        # Skip UNSHIPPABLE items
        if "UNSHIPPABLE" in ore_name:
            excluded_ores.append({
                "name": ore_name,
                "reason": "UNSHIPPABLE item"
            })
            continue

        # Get properties
        properties = ore_entry.get("Value", [])

        # Extract basic info
        display_name = get_string_property(properties, "DisplayName", string_map)
        description = get_string_property(properties, "Description", string_map)
        icon_path = get_property_value(properties, "Icon")
        actor_path = get_property_value(properties, "Actor")

        # Skip if no display name
        if not display_name:
            excluded_ores.append({
                "name": ore_name,
                "reason": "No display name"
            })
            continue

        # Skip items with template placeholders in name
        if "{" in display_name or "}" in display_name:
            excluded_ores.append({
                "name": ore_name,
                "reason": "Template placeholder in name"
            })
            continue

        # Extract tags
        tags = get_tags_list(properties)

        # Determine type and subtype
        ore_type, subtype = determine_ore_type(tags, display_name)

        # Build ore model
        ore_model = {
            "Name": ore_name,
            "DisplayName": display_name,
            "Description": description or "",
            "Type": ore_type,
            "Subtype": subtype,
            "IconPath": icon_path or "",
            "ActorPath": actor_path or "",
            "Tags": tags,
            "MaxStackSize": get_property_value(properties, "MaxStackSize"),
            "BaseTradeValue": get_property_value(properties, "BaseTradeValue"),
        }

        # Detect DLC
        is_dlc, dlc_title, dlc_name = detect_dlc(ore_model["ActorPath"], ore_model["IconPath"])
        if is_dlc:
            ore_model["DLC"] = True
            ore_model["DLCTitle"] = dlc_title
            ore_model["DLCName"] = dlc_name
        else:
            ore_model["DLC"] = False

        # Check for unlock overrides
        if display_name in CAMPAIGN_UNLOCK_OVERRIDE:
            ore_model["CampaignUnlock"] = CAMPAIGN_UNLOCK_OVERRIDE[display_name]
        if display_name in SANDBOX_UNLOCK_OVERRIDE:
            ore_model["SandboxUnlock"] = SANDBOX_UNLOCK_OVERRIDE[display_name]

        ore_models.append(ore_model)

    print(f"  Processed {len(ore_models)} ores")
    print(f"  Excluded {len(excluded_ores)} ores")
    return ore_models, excluded_ores


def write_wiki_files(ore_models, output_dir):
    """Write wiki files for all ores."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nWriting wiki files to {output_dir}...")
    for ore_model in ore_models:
        filename = f"{ore_model['DisplayName']}.wiki"
        filepath = os.path.join(output_dir, filename)

        wiki_content = generate_wiki_template(ore_model)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(ore_models)} wiki files")


def write_excluded_log(excluded_ores, output_root):
    """Write a log of excluded ores."""
    if not excluded_ores:
        return

    log_path = os.path.join(output_root, "excluded_ores.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Excluded {len(excluded_ores)} ores:\n\n")
        for item in excluded_ores:
            f.write(f"{item['name']}: {item['reason']}\n")
    print(f"\nWrote exclusion log to {log_path}")


def main():
    print("Loading data...")

    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"  Total strings: {len(string_map)}")

    # Load ores data
    print("Loading ores data...")
    ores_data = load_ores_data(ORES_FILE)
    print(f"  Total ores: {len(ores_data)}")

    # Process ores
    ore_models, excluded_ores = process_ores(ores_data, string_map)

    # Write wiki files
    write_wiki_files(ore_models, OUTPUT_DIR)

    # Write exclusion log to output root directory
    if excluded_ores:
        write_excluded_log(excluded_ores, "output")

    print("\nDone!")


if __name__ == "__main__":
    main()
