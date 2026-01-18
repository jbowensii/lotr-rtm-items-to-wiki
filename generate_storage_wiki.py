import json
import os

# Paths - Updated for new datajson structure
OUTPUT_BASE = os.path.join(os.environ.get("APPDATA", ""), "MoriaWikiGenerator", "output")
SOURCE_DIR = os.path.join(OUTPUT_BASE, "datajson", "Moria", "Content", "Tech", "Data")
STRINGS_DIR = os.path.join(SOURCE_DIR, "StringTables")
STORAGE_FILE = os.path.join(SOURCE_DIR, "Items", "DT_Storage.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "Items", "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join(OUTPUT_BASE, "wiki", "storage")

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


def load_storage_data(filepath):
    """Load DT_Storage.json and return a list of storage entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    storage_list = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            storage_entries = table.get("Data", [])
            storage_list.extend(storage_entries)

    return storage_list


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


def determine_storage_type(storage_name, is_portable):
    """Determine the type of storage based on name and properties."""
    storage_type = "Storage"

    name_lower = storage_name.lower()

    if is_portable:
        storage_type = "Container"
    elif "chest" in name_lower:
        storage_type = "Chest"
    elif "brewery" in name_lower or "brewskin" in name_lower:
        storage_type = "Storage"

    return storage_type


def generate_wiki_template(storage_model, string_map):
    """Generate MediaWiki template text for a storage item."""
    lines = []

    # Item infobox
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(f" | name          = {storage_model['DisplayName']}")

    # Type
    if storage_model.get("Type"):
        lines.append(f" | type          = {storage_model['Type']}")
    else:
        lines.append(" | type          = ")

    # Subtype
    if storage_model.get("Subtype"):
        lines.append(f" | subtype       = {storage_model['Subtype']}")
    else:
        lines.append(" | subtype       = ")

    lines.append("}}")
    lines.append("")
    lines.append(f"'''{{{{PAGENAME}}}}''' is a [[{storage_model['Type']}]] in ''[[{{{{topic}}}}]]''.")

    # Description section (only if non-empty)
    if storage_model.get("Description") and storage_model["Description"].strip():
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {storage_model['Description']}")

    # Unlocks section (only if unlock overrides exist)
    if storage_model.get("CampaignUnlock") or storage_model.get("SandboxUnlock"):
        lines.append("")
        lines.append("== Unlocks ==")
        lines.append("")
        if storage_model.get("CampaignUnlock"):
            lines.append(f"* Campaign {{{{spoiler|{storage_model['CampaignUnlock']}}}}}")
        if storage_model.get("SandboxUnlock"):
            lines.append(f"* Sandbox  {{{{spoiler|{storage_model['SandboxUnlock']}}}}}")

    # Stats section
    lines.append("")
    lines.append("==Stats==")

    if storage_model.get("InventoryWidth") and storage_model.get("InventoryHeight"):
        lines.append(f"* '''Inventory Size:''' {storage_model['InventoryWidth']} x {storage_model['InventoryHeight']}")

    if storage_model.get("IsPortable") is not None:
        portable_text = "Yes" if storage_model["IsPortable"] else "No"
        lines.append(f"* '''Portable:''' {portable_text}")

    if storage_model.get("Durability") and storage_model["Durability"] > 0:
        lines.append(f"* '''Durability:''' {storage_model['Durability']}")

    # Crafting section (only if materials exist)
    if storage_model.get("CraftingMaterials"):
        lines.append("")
        lines.append("==Crafting==")
        lines.append("Materials:")
        lines.append("")
        for mat_name, mat_count in storage_model["CraftingMaterials"]:
            # Look up display name in string tables
            # Materials are stored as "Item.XXX", but string keys are "Items.Items.XXX.Name" or "Items.XXX.Name"
            display_name = None

            if mat_name.startswith("Item."):
                item_suffix = mat_name.replace("Item.", "")
                # Try Items.Items.XXX.Name first
                lookup_key1 = f"Items.Items.{item_suffix}.Name"
                display_name = string_map.get(lookup_key1)

                # Try Items.XXX.Name as fallback
                if not display_name:
                    lookup_key2 = f"Items.{item_suffix}.Name"
                    display_name = string_map.get(lookup_key2)

            # If still not found, try suffix matching
            if not display_name:
                suffix = mat_name.split('.')[-1] if '.' in mat_name else mat_name
                for key, val in string_map.items():
                    if key.endswith(f".{suffix}.Name"):
                        display_name = val
                        break

            # Fall back to removing "Item." prefix if still not found
            if not display_name:
                display_name = mat_name.replace("Item.", "")

            lines.append(f"* ({mat_count}) {{{{LI|{display_name}}}}}")

    # DLC section (if applicable)
    if storage_model.get("DLC"):
        lines.append("")
        lines.append("==Availability==")
        lines.append(f"This item is part of the {storage_model['DLCTitle']}.")

    return "\n".join(lines)


def process_storage(storage_data, string_map, recipes_dict):
    """Process all storage items and generate wiki models."""
    print("\nProcessing storage items...")
    storage_models = []

    for storage_entry in storage_data:
        storage_name = storage_entry.get("Name", "")

        # Get properties
        properties = storage_entry.get("Value", [])

        # Extract basic info
        display_name = get_string_property(properties, "Name", string_map)
        description = get_string_property(properties, "Description", string_map)

        # Skip if no display name
        if not display_name:
            continue

        # Extract storage-specific properties
        inventory_width = get_property_value(properties, "InventoryWidth")
        inventory_height = get_property_value(properties, "InventoryHeight")
        is_portable = get_property_value(properties, "bPortable")
        durability = get_property_value(properties, "Durability")

        # Determine type
        storage_type = determine_storage_type(storage_name, is_portable)

        # Build storage model
        storage_model = {
            "Name": storage_name,
            "DisplayName": display_name,
            "Description": description or "",
            "Type": storage_type,
            "Subtype": "",
            "InventoryWidth": inventory_width,
            "InventoryHeight": inventory_height,
            "IsPortable": is_portable,
            "Durability": durability,
        }

        # Note: Storage items don't typically have Actor/Icon paths in the same way
        # as other items, so DLC detection may not work the same way

        # Check for unlock overrides
        if display_name in CAMPAIGN_UNLOCK_OVERRIDE:
            storage_model["CampaignUnlock"] = CAMPAIGN_UNLOCK_OVERRIDE[display_name]
        if display_name in SANDBOX_UNLOCK_OVERRIDE:
            storage_model["SandboxUnlock"] = SANDBOX_UNLOCK_OVERRIDE[display_name]

        # Check for crafting recipe
        if storage_name in recipes_dict:
            storage_model["CraftingMaterials"] = recipes_dict[storage_name]

        storage_models.append(storage_model)

    print(f"  Processed {len(storage_models)} storage items")
    return storage_models


def write_wiki_files(storage_models, output_dir, string_map):
    """Write wiki files for all storage items."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nWriting wiki files to {output_dir}...")
    for storage_model in storage_models:
        filename = f"{storage_model['DisplayName']}.wiki"
        filepath = os.path.join(output_dir, filename)

        wiki_content = generate_wiki_template(storage_model, string_map)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(storage_models)} wiki files")




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

    # Load storage data
    print("Loading storage data...")
    storage_data = load_storage_data(STORAGE_FILE)
    print(f"  Total storage items: {len(storage_data)}")

    # Process storage
    storage_models = process_storage(storage_data, string_map, recipes_dict)

    # Write wiki files
    write_wiki_files(storage_models, OUTPUT_DIR, string_map)

    print("\nDone!")


if __name__ == "__main__":
    main()
