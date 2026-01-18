import json
import os

# Paths - Updated for new datajson structure
OUTPUT_BASE = os.path.join(os.environ.get("APPDATA", ""), "MoriaWikiGenerator", "output")
SOURCE_DIR = os.path.join(OUTPUT_BASE, "datajson", "Moria", "Content", "Tech", "Data")
STRINGS_DIR = os.path.join(SOURCE_DIR, "StringTables")
TRADEGOODS_FILE = os.path.join(SOURCE_DIR, "Economy", "DT_TradeGoods.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "Items", "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join(OUTPUT_BASE, "wiki", "tradegoods")

# Mapping from DLC path names to DLC titles
DLC_TITLE_MAP = {
    "BeornPack": "{{LI|The Beorn's Lodge Pack}}",
    "DurinsFolk": "{{LI|Durin's Folk Expansion}}",
    "Elven": "{{LI|Durin's Folk Expansion}}",
    "EntPack": "{{LI|The Ent-craft Pack}}",
    "Holiday2025": "{{LI|The Yule-tide Pack}}",
    "HolidayPack": "{{LI|The Yule-tide Pack}}",
    "LordOfMoria": "{{LI|End Game Award}}",
    "OrcHunterPack": "{{LI|The Orc Hunter Pack}}",
    "OriginCosmetics": "{{LI|Return to Moria}}",
    "RohanPack": "{{LI|The Rohan Pack}}",
}

# Mapping from CraftingStation keys to Constructions string keys
STATION_KEY_MAP = {
    # Forges
    "CraftingStation_BasicForge": "Constructions.BasicForge",
    "CraftingStation_AdvancedForge": "Constructions.ForgeAdvanced",
    "CraftingStation_FloodedForge": "Constructions.FloodedForge",
    "CraftingStation_DurinForge": "Constructions.DurinForge",
    "CraftingStation_MithrilForge": "Constructions.MithrilForge",
    "CraftingStation_NogrodForge": "Constructions.NogrodForge",
    "CraftingStation_LegendayElvishForge": "Constructions.LegendayElvishForge",
    "CraftingStation_ForgeUpgrade": "Constructions.ForgeUpgrade",
    # Furnaces
    "CraftingStation_BasicFurnace": "Constructions.BasicFurnace",
    "CraftingStation_AdvancedFurnace": "Constructions.FurnaceAdvanced",
    "CraftingStation_FloodedFurnace": "Constructions.FloodedFurnace.Name",
    "CraftingStation_LegendaryDurinsFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_LegendaryFloodedFurnace": "Constructions.FloodedFurnace.Name",
    "CraftingStation_LegendaryMithrilFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_LegendaryNogrodFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_LegendayElvishFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_FurnaceUpgrade": "Constructions.ForgeUpgrade",
    # Other stations
    "CraftingStation_Workbench": "Constructions.Workbench",
    "CraftingStation_Campfire": "Constructions.Campfire",
    "CraftingStation_MealTable": "Constructions.MealTable",
    "CraftingStation_FabricStation": "Constructions.FabricStation.Name",
    "CraftingStation_Hearth": "Constructions.Hearth_Small.name",
    "CraftingStation_Kitchen": "Constructions.Kitchen_Stove.Name",
    "CraftingStation_Mill": "Constructions.Mill.Name",
    "CraftingStation_PurificationStation": "Constructions.PurificationStation.Name",
    "CraftingStation_TintingStation": "Constructions.TintingStation.Name",
}

# Material name mappings for special cases
MATERIAL_KEY_MAP = {
    "Item.Scrap": "Metal Fragments",
}

# Tag to property mappings for trade goods
TAG_MAPPINGS = {
    "Item.TradeGood.Artisan": {"type": "Artisan"},
    "Item.TradeGood.Blacksmith": {"type": "Blacksmith"},
    "Item.TradeGood.Brewer": {"type": "Brewer"},
    "Item.TradeGood.Metalworker": {"type": "Metalworker"},
    "UI.Trading": {},  # General trading tag, no specific type
}


def load_string_table(filepath):
    """Load a single string table file and return a key->value dictionary."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    string_map = {}
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


def load_all_string_tables(strings_dir):
    """Load all string table files from the strings directory."""
    combined_map = {}
    for filename in os.listdir(strings_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(strings_dir, filename)
            print(f"  Loading {filename}...")
            table_map = load_string_table(filepath)
            print(f"    Found {len(table_map)} strings")
            combined_map.update(table_map)
    return combined_map


def load_tradegoods_data(filepath):
    """Load DT_TradeGoods.json and return the list of trade good entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tradegoods_list = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            tradegood_entries = table.get("Data", [])
            tradegoods_list.extend(tradegood_entries)

    return tradegoods_list


def load_recipe_data(filepath):
    """Load DT_ItemRecipes.json and return a dictionary keyed by item name."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes = {}
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            recipe_entries = table.get("Data", [])
            for recipe in recipe_entries:
                name = recipe.get("Name")
                if name:
                    recipes[name] = recipe

    return recipes


def find_string_by_suffix(string_map, suffix):
    """
    Find a string value by matching the suffix of the key.
    This helps handle variations in key naming conventions.
    """
    for key, value in string_map.items():
        if key.endswith(suffix):
            return value
    return None


def get_display_name(tradegood_data, string_map):
    """Extract display name from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "DisplayName":
            table_key = prop.get("Value", "")
            if table_key and isinstance(table_key, str):
                # Try exact match first
                display_name = string_map.get(table_key)
                if display_name:
                    return display_name
                # Try suffix match
                parts = table_key.split('.')
                if len(parts) >= 2:
                    suffix = '.'.join(parts[-2:])
                    display_name = find_string_by_suffix(string_map, suffix)
                    if display_name:
                        return display_name
    return "Unknown Trade Good"


def get_description(tradegood_data, string_map):
    """Extract description from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "Description":
            table_key = prop.get("Value", "")
            if table_key and isinstance(table_key, str):
                # Try exact match first
                description = string_map.get(table_key)
                if description:
                    return description
                # Try suffix match
                parts = table_key.split('.')
                if len(parts) >= 2:
                    suffix = '.'.join(parts[-2:])
                    description = find_string_by_suffix(string_map, suffix)
                    if description:
                        return description
    return ""


def get_actor_path(tradegood_data):
    """Extract actor path from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "Actor":
            value = prop.get("Value", {})
            if isinstance(value, dict):
                asset_path = value.get("AssetPath", {})
                if isinstance(asset_path, dict):
                    asset_name = asset_path.get("AssetName", "")
                    return asset_name
    return ""


def get_icon_path(tradegood_data):
    """Extract icon path from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "Icon":
            value = prop.get("Value", {})
            if isinstance(value, dict):
                asset_path = value.get("AssetPath", {})
                if isinstance(asset_path, dict):
                    asset_name = asset_path.get("AssetName", "")
                    return asset_name
    return ""


def get_max_stack_size(tradegood_data):
    """Extract max stack size from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "MaxStackSize":
            return prop.get("Value", 1)
    return 1


def get_slot_size(tradegood_data):
    """Extract slot size from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "SlotSize":
            return prop.get("Value", 1)
    return 1


def get_base_trade_value(tradegood_data):
    """Extract base trade value from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "BaseTradeValue":
            return prop.get("Value", 0.0)
    return 0.0


def get_portability(tradegood_data):
    """Extract portability from trade good data."""
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "Portability":
            enum_value = prop.get("Value", "")
            if "::" in enum_value:
                return enum_value.split("::")[-1]
    return "Unknown"


def get_tags(tradegood_data):
    """Extract gameplay tags from trade good data."""
    tags = []
    for prop in tradegood_data.get("Value", []):
        if prop.get("Name") == "Tags":
            struct_values = prop.get("Value", [])
            for struct_val in struct_values:
                if struct_val.get("$type") == "UAssetAPI.PropertyTypes.Structs.GameplayTagContainerPropertyData, UAssetAPI":
                    tag_list = struct_val.get("Value", [])
                    tags.extend(tag_list)
    return tags


def detect_dlc(actor_path, icon_path):
    """Detect DLC information from actor or icon path."""
    paths_to_check = [actor_path, icon_path]
    for path in paths_to_check:
        if "/DLC/" in path:
            # Extract DLC name from path (e.g., /Game/DLC/OrcHunterPack/...)
            parts = path.split("/DLC/")
            if len(parts) > 1:
                dlc_name = parts[1].split("/")[0]
                dlc_title = DLC_TITLE_MAP.get(dlc_name, f"{{{{LI|{dlc_name}}}}}")
                return True, dlc_title, dlc_name
    return False, None, None


def get_material_display_name(material_key, string_map):
    """Get display name for a crafting material."""
    # Check special material mappings first
    if material_key in MATERIAL_KEY_MAP:
        return MATERIAL_KEY_MAP[material_key]

    # Try multiple lookup patterns
    lookup_patterns = [
        f"Items.Items.{material_key}.Name",
        f"Items.Ores.{material_key}.Name",
        f"Consumable.{material_key}.Name",
        f"Category.Item.{material_key}",
        f"Item.{material_key}.Name",
        material_key,
    ]

    for pattern in lookup_patterns:
        display_name = string_map.get(pattern)
        if display_name:
            return display_name

    # Try suffix matching
    for pattern in lookup_patterns:
        parts = pattern.split('.')
        if len(parts) >= 2:
            suffix = '.'.join(parts[-2:])
            display_name = find_string_by_suffix(string_map, suffix)
            if display_name:
                return display_name

    # Fallback to the key itself
    return material_key


def get_station_display_name(station_key, string_map):
    """Get display name for a crafting station."""
    mapped_key = STATION_KEY_MAP.get(station_key, station_key)
    station_name = string_map.get(mapped_key, station_key)
    return station_name


def parse_recipe_materials(recipe_data, string_map):
    """Extract crafting materials from recipe data."""
    materials = []
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "DefaultRequiredMaterials":
            # DefaultRequiredMaterials is a list - each item represents one material entry
            for mat_entry in prop.get("Value", []):
                mat_key = None
                mat_count = 1
                # The mat_entry itself has MaterialHandle and Count as direct properties
                for mat_prop in mat_entry.get("Value", []):
                    if mat_prop.get("Name") == "MaterialHandle":
                        # MaterialHandle contains RowName
                        for handle_prop in mat_prop.get("Value", []):
                            if handle_prop.get("Name") == "RowName":
                                mat_key = handle_prop.get("Value", "")
                    elif mat_prop.get("Name") == "Count":
                        mat_count = mat_prop.get("Value", 1)
                if mat_key:
                    display_name = get_material_display_name(mat_key, string_map)
                    materials.append((mat_count, display_name))
    return materials


def parse_crafting_stations(recipe_data, string_map):
    """Extract crafting stations from recipe data."""
    stations = []
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "CraftingStations":
            # CraftingStations is a list - each item represents one station entry
            for station_entry in prop.get("Value", []):
                station_key = None
                # The station_entry has RowName as a direct property
                for station_prop in station_entry.get("Value", []):
                    if station_prop.get("Name") == "RowName":
                        station_key = station_prop.get("Value", "")
                if station_key:
                    display_name = get_station_display_name(station_key, string_map)
                    stations.append(display_name)
    return stations


def parse_crafting_time(recipe_data):
    """Extract crafting time from recipe data."""
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "CraftTimeSeconds":
            return prop.get("Value", 0.0)
    return 0.0


def process_tags_for_properties(tags):
    """
    Process gameplay tags and extract type.
    Returns a dict with 'types' (list).
    """
    result = {
        "types": [],
    }

    for tag in tags:
        # Check if tag is in our mappings
        if tag in TAG_MAPPINGS:
            mapping = TAG_MAPPINGS[tag]

            # Extract type if present
            if "type" in mapping:
                type_value = mapping["type"]
                if type_value not in result["types"]:
                    result["types"].append(type_value)

    return result




def generate_wiki_template(tradegood_model):
    """Generate MediaWiki template for a trade good."""
    lines = []
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(f" | name          = {tradegood_model['DisplayName']}")

    # Type field - join multiple types with <br>
    type_value = ""
    if tradegood_model.get("TradeGoodTypes"):
        type_value = "<br>".join(tradegood_model["TradeGoodTypes"])
    lines.append(f" | type          = {type_value}")
    lines.append(" | subtype       = ")

    # Properties section
    if tradegood_model.get("MaxStackSize") and tradegood_model["MaxStackSize"] > 1:
        lines.append(f" | stack         = {tradegood_model['MaxStackSize']}")

    if tradegood_model.get("SlotSize") and tradegood_model["SlotSize"] > 1:
        lines.append(f" | slots         = {tradegood_model['SlotSize']}")

    if tradegood_model.get("Portability"):
        portability = tradegood_model["Portability"]
        if portability == "HeavyCarry":
            lines.append(" | heavy         = Yes")
        elif portability == "NotPortable":
            lines.append(" | portable      = No")

    # Base trade value
    if tradegood_model.get("BaseTradeValue") and tradegood_model["BaseTradeValue"] > 0:
        lines.append(f" | value         = {tradegood_model['BaseTradeValue']:.1f}")

    # Tags
    if tradegood_model.get("Tags"):
        tags_formatted = ", ".join(tradegood_model["Tags"])
        lines.append(f" | tags          = {tags_formatted}")

    lines.append("}}")

    # Intro line
    lines.append("")
    lines.append("'''{{PAGENAME}}''' are a [[Trade Good]] in ''[[{{topic}}]]''.")

    # Description section
    if tradegood_model.get("Description"):
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {tradegood_model['Description']}")

    # Crafting section
    if tradegood_model.get("HasRecipe") and (tradegood_model.get("CraftingStations") or tradegood_model.get("CraftingMaterials")):
        lines.append("")
        lines.append("== Crafting ==")
        lines.append("")

        # Crafting time
        if tradegood_model.get("CraftTime") and tradegood_model["CraftTime"] > 0:
            craft_time = tradegood_model["CraftTime"]
            # Format time as integer if it's a whole number, otherwise show decimal
            if craft_time == int(craft_time):
                lines.append(f"Time: {int(craft_time)} seconds")
            else:
                lines.append(f"Time: {craft_time} seconds")
            lines.append("")

        # Stations
        if tradegood_model.get("CraftingStations"):
            lines.append("Station:")
            lines.append("")
            for station in tradegood_model["CraftingStations"]:
                lines.append(f"* {{{{LI|{station}}}}}")
            lines.append("")

        # Materials
        if tradegood_model.get("CraftingMaterials"):
            lines.append("Materials:")
            lines.append("")
            for count, material in tradegood_model["CraftingMaterials"]:
                lines.append(f"* ({count}) {{{{LI|{material}}}}}")

    return "\n".join(lines)


def process_tradegoods(tradegoods_data, recipes_data, string_map):
    """Process all trade goods and generate wiki models."""
    print("\nProcessing trade goods...")
    tradegood_models = []

    for tradegood_entry in tradegoods_data:
        tradegood_name = tradegood_entry.get("Name", "")

        # Get basic properties
        display_name = get_display_name(tradegood_entry, string_map)

        # Skip if no display name
        if not display_name or display_name == "Unknown Trade Good":
            continue

        # Get tags
        tags = get_tags(tradegood_entry)

        # Process tags to extract types
        tag_properties = process_tags_for_properties(tags)

        # Build trade good model
        tradegood_model = {
            "Name": tradegood_name,
            "DisplayName": display_name,
            "Description": get_description(tradegood_entry, string_map),
            "ActorPath": get_actor_path(tradegood_entry),
            "IconPath": get_icon_path(tradegood_entry),
            "MaxStackSize": get_max_stack_size(tradegood_entry),
            "SlotSize": get_slot_size(tradegood_entry),
            "BaseTradeValue": get_base_trade_value(tradegood_entry),
            "Portability": get_portability(tradegood_entry),
            "Tags": tags,
            "TradeGoodTypes": tag_properties["types"],
        }

        # Detect DLC
        is_dlc, dlc_title, dlc_name = detect_dlc(tradegood_model["ActorPath"], tradegood_model["IconPath"])
        if is_dlc:
            tradegood_model["DLC"] = True
            tradegood_model["DLCTitle"] = dlc_title
            tradegood_model["DLCName"] = dlc_name
        else:
            tradegood_model["DLC"] = False

        # Parse recipe data if available
        recipe = recipes_data.get(tradegood_name)
        if recipe:
            tradegood_model["HasRecipe"] = True
            tradegood_model["CraftingMaterials"] = parse_recipe_materials(recipe, string_map)
            tradegood_model["CraftingStations"] = parse_crafting_stations(recipe, string_map)
            tradegood_model["CraftTime"] = parse_crafting_time(recipe)
        else:
            tradegood_model["HasRecipe"] = False

        tradegood_models.append(tradegood_model)

    print(f"  Processed {len(tradegood_models)} trade goods")
    return tradegood_models


def write_wiki_files(tradegood_models, output_dir):
    """Write wiki template files for each trade good."""
    print(f"\nWriting wiki files to {output_dir}...")

    os.makedirs(output_dir, exist_ok=True)

    for tradegood in tradegood_models:
        wiki_content = generate_wiki_template(tradegood)
        filename = f"{tradegood['DisplayName']}.wiki"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(tradegood_models)} wiki files")




def main():
    print("Loading data...")

    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"  Total strings: {len(string_map)}")

    # Load trade goods data
    print("Loading trade goods data...")
    tradegoods_data = load_tradegoods_data(TRADEGOODS_FILE)
    print(f"  Total trade goods: {len(tradegoods_data)}")

    # Load recipes data
    print("Loading recipes data...")
    recipes_data = load_recipe_data(RECIPES_FILE)
    print(f"  Total recipes: {len(recipes_data)}")

    # Process trade goods
    tradegood_models = process_tradegoods(tradegoods_data, recipes_data, string_map)

    # Write wiki files
    write_wiki_files(tradegood_models, OUTPUT_DIR)

    print("\nDone!")


if __name__ == "__main__":
    main()
