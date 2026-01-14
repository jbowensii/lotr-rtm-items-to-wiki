import json
import os
import re

# Paths
SOURCE_DIR = "source"
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")
ITEMS_FILE = os.path.join(SOURCE_DIR, "DT_Items.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join("output", "items")

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

# Fragment location hints by tier for Campaign mode
CAMPAIGN_FRAGMENT_LOCATION = {
    1: ", Repair [[Damaged Statues]] in [[Westgate]]",
    2: ", Repair [[Damaged Statues]] in the [[Mines of Moria]]",
    3: ", Repair [[Damaged Statues]] in the [[Lower Deeps]]",
    4: ", Repair [[Damaged Statues]] in the [[Desolation]]",
    5: ", Unlock the [[Great Nogrod Forge]]",
    6: ", Speak with [[Aric]] after the end-game credits",
}

# Fragment location hints by tier for Sandbox mode
SANDBOX_FRAGMENT_LOCATION = {
    1: ", Repair [[Damaged Statues]] in the [[Gate]] or [[Elven]] areas",
    2: ", Repair [[Damaged Statues]] in the [[Mines]] areas",
    3: ", Repair [[Damaged Statues]] in the [[Mines]] or [[Deeps]] areas",
    4: ", Repair [[Damaged Statues]] in the [[Halls]], [[Ruins]] or [[Lode]] areas",
    5: ", Repair [[Damaged Statues]] in the [[Halls]], [[Ruins]] or [[Lode]] areas",
    6: ", Repair [[Damaged Statues]] in the [[Halls]], [[Ruins]] or [[Lode]] areas",
}

# Special campaign unlock overrides for items with unique unlock methods
CAMPAIGN_UNLOCK_OVERRIDE = {
    # Add specific overrides here as needed
}

# Special sandbox unlock overrides for items with unique unlock methods
SANDBOX_UNLOCK_OVERRIDE = {
    # Add specific overrides here as needed
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

# Tag to property mappings
TAG_MAPPINGS = {
    "Item.BasicGather": {"gathered": True, "crafting": True, "type": "Material"},
    "Item.Book": {"gathered": True, "crafting": True, "type": "Treasure"},
    "Item.BrewIngredient": {"brewing": True, "type": "Ingredient"},
    "Item.Food.Spice": {"cooking": True, "type": "Ingredient"},
    "Item.Food.Veg.Mushroom": {"type": "Fuel", "gathered": True},
    "Item.Key": {"gathered": True, "type": "Key"},
    "Item.MemorialItem": {"crafting": True, "type": "Treasure"},
    "Item.Mineral.Scrap": {"gathered": True, "type": "Material"},
    "Item.Scroll": {"gathered": True, "crafting": True, "type": "Treasure"},
    "Item.Seed": {"farming": True, "type": "Seed"},
    "Item.Treasure": {"type": "Treasure"},
    "Item.Wood": {"gathered": True, "crafting": True, "building": True, "type": "Material"},
    "UI.Fabric": {"crafting": True, "building": True, "type": "Material"},
    "UI.Figurine": {"type": "Muznakan Carving"},
    "UI.Items": {"gathered": True, "type": "Treasure"},
    "UI.Materials": {"crafting": True, "type": "Material"},
    "UI.Metals": {"crafting": True, "type": "Crafted Material"},
    "UI.Processed": {"type": "Crafted Material", "crafting": True},
    "UI.Purified": {"crafting": True, "type": "Crafted Material"},
    "UI.Seed": {"farming": True, "type": "Seed"},
    "UI.Tool": {"type": "Key"},
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


def load_items_data(filepath):
    """Load DT_Items.json and return the list of item entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items_list = []
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.DataTableExport, UAssetAPI":
            table = export.get("Table", {})
            item_entries = table.get("Data", [])
            items_list.extend(item_entries)

    return items_list


def load_recipe_data(filepath):
    """Load DT_ItemRecipes.json and return a dictionary keyed by item name."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes = {}
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.DataTableExport, UAssetAPI":
            table = export.get("Table", {})
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


def get_display_name(item_data, string_map):
    """Extract display name from item data."""
    for prop in item_data.get("Value", []):
        if prop.get("Name") == "DisplayName":
            table_key = prop.get("Value", "")
            if table_key and isinstance(table_key, str):
                # Try exact match first
                display_name = string_map.get(table_key)
                if display_name:
                    return display_name
                # Try suffix match (e.g., "Items.Items.Scrap.Name" -> "Scrap.Name")
                parts = table_key.split('.')
                if len(parts) >= 2:
                    suffix = '.'.join(parts[-2:])
                    display_name = find_string_by_suffix(string_map, suffix)
                    if display_name:
                        return display_name
    return "Unknown Item"


def get_description(item_data, string_map):
    """Extract description from item data."""
    for prop in item_data.get("Value", []):
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


def get_actor_path(item_data):
    """Extract actor path from item data."""
    for prop in item_data.get("Value", []):
        if prop.get("Name") == "Actor":
            value = prop.get("Value", {})
            if isinstance(value, dict):
                asset_path = value.get("AssetPath", {})
                if isinstance(asset_path, dict):
                    asset_name = asset_path.get("AssetName", "")
                    return asset_name
    return ""


def get_icon_path(item_data):
    """Extract icon path from item data."""
    for prop in item_data.get("Value", []):
        if prop.get("Name") == "Icon":
            value = prop.get("Value", {})
            if isinstance(value, dict):
                asset_path = value.get("AssetPath", {})
                if isinstance(asset_path, dict):
                    asset_name = asset_path.get("AssetName", "")
                    return asset_name
    return ""


def get_max_stack_size(item_data):
    """Extract max stack size from item data."""
    for prop in item_data.get("Value", []):
        if prop.get("Name") == "MaxStackSize":
            return prop.get("Value", 1)
    return 1


def get_slot_size(item_data):
    """Extract slot size from item data."""
    for prop in item_data.get("Value", []):
        if prop.get("Name") == "SlotSize":
            return prop.get("Value", 1)
    return 1


def get_base_trade_value(item_data):
    """Extract base trade value from item data."""
    for prop in item_data.get("Value", []):
        if prop.get("Name") == "BaseTradeValue":
            return prop.get("Value", 0.0)
    return 0.0


def get_portability(item_data):
    """Extract portability from item data."""
    for prop in item_data.get("Value", []):
        if prop.get("Name") == "Portability":
            enum_value = prop.get("Value", "")
            if "::" in enum_value:
                return enum_value.split("::")[-1]
    return "Unknown"


def get_tags(item_data):
    """Extract gameplay tags from item data."""
    tags = []
    for prop in item_data.get("Value", []):
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
        if prop.get("Name") == "CraftingMaterials":
            for mat_struct in prop.get("Value", []):
                if mat_struct.get("$type") == "UAssetAPI.PropertyTypes.Structs.StructPropertyData, UAssetAPI":
                    mat_key = None
                    mat_count = 1
                    for mat_prop in mat_struct.get("Value", []):
                        if mat_prop.get("Name") == "Row":
                            mat_key = mat_prop.get("Value", "")
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
            for station_struct in prop.get("Value", []):
                if station_struct.get("$type") == "UAssetAPI.PropertyTypes.Structs.StructPropertyData, UAssetAPI":
                    station_key = None
                    for station_prop in station_struct.get("Value", []):
                        if station_prop.get("Name") == "Row":
                            station_key = station_prop.get("Value", "")
                    if station_key:
                        display_name = get_station_display_name(station_key, string_map)
                        stations.append(display_name)
    return stations


def parse_crafting_time(recipe_data):
    """Extract crafting time from recipe data."""
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "CraftTime":
            return prop.get("Value", 0.0)
    return 0.0


def parse_unlock_type(recipe_data):
    """Extract unlock type from recipe data."""
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "UnlockType":
            enum_value = prop.get("Value", "")
            if "::" in enum_value:
                return enum_value.split("::")[-1]
    return "Unknown"


def parse_fragments_required(recipe_data):
    """Extract number of fragments required from recipe data."""
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "FragmentsRequired":
            return prop.get("Value", 0)
    return 0


def parse_has_sandbox_unlock_override(recipe_data):
    """Check if recipe has sandbox unlock override flag."""
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "bHasSandboxUnlockOverride":
            return prop.get("Value", True)
    return True


def parse_tier(recipe_data):
    """Extract tier from recipe data."""
    for prop in recipe_data.get("Value", []):
        if prop.get("Name") == "Tier":
            tier_value = prop.get("Value", 0)
            # Strip "Tier" prefix if present and return just the number
            if isinstance(tier_value, str) and tier_value.startswith("Tier"):
                return tier_value[4:]
            return tier_value
    return 0


def format_unlock_text(display_name, unlock_type, fragments_required, tier, is_dlc, dlc_title, has_sandbox_unlock_override, is_campaign_mode):
    """Format the unlock text based on unlock type and other parameters."""
    # Check for override first
    override_map = CAMPAIGN_UNLOCK_OVERRIDE if is_campaign_mode else SANDBOX_UNLOCK_OVERRIDE
    if display_name in override_map:
        return override_map[display_name]

    # Fragment collection unlock
    if unlock_type == "FragmentCollection" and fragments_required > 0:
        fragment_text = f"Collect {fragments_required} fragment" + ("s" if fragments_required > 1 else "")
        location_map = CAMPAIGN_FRAGMENT_LOCATION if is_campaign_mode else SANDBOX_FRAGMENT_LOCATION
        if tier and tier in location_map:
            fragment_text += location_map[tier]
        return fragment_text

    # Manual unlock (usually trader purchases or special unlocks)
    if unlock_type == "Manual":
        if is_dlc and dlc_title:
            return f"Purchase {dlc_title}"
        return "???"

    # Discover dependencies
    if unlock_type == "DiscoverDependencies":
        return "Unlocked by discovering dependencies"

    # DLC unlock
    if is_dlc and dlc_title:
        return f"Purchase {dlc_title}"

    # Default fallback
    return "{{LI|Return to Moria}}"


def process_tags_for_properties(tags):
    """
    Process gameplay tags and extract type and usage flags.
    Returns a dict with 'types' (list) and boolean flags.
    """
    result = {
        "types": [],
        "gathered": False,
        "crafting": False,
        "building": False,
        "brewing": False,
        "cooking": False,
        "farming": False,
    }

    # Ignored tags that don't contribute to properties
    ignored_tags = {
        "Item.Heavy",
        "Item.HeavyCarryTarget",
        "Item.Unstorable.HandsOnly",
        "Item.Unstorable.WorldOnly",
    }

    for tag in tags:
        # Skip ignored tags
        if tag in ignored_tags:
            continue

        # Check if tag is in our mappings
        if tag in TAG_MAPPINGS:
            mapping = TAG_MAPPINGS[tag]

            # Extract type if present
            if "type" in mapping:
                type_value = mapping["type"]
                if type_value not in result["types"]:
                    result["types"].append(type_value)

            # Set boolean flags (if any tag sets it to True, it's True)
            for flag in ["gathered", "crafting", "building", "brewing", "cooking", "farming"]:
                if mapping.get(flag, False):
                    result[flag] = True

    return result


def should_exclude_item(item_name, display_name):
    """Check if item should be excluded from wiki generation."""
    exclusions = [
        "TEST",
        "Test",
        "DEV_",
        "BROKEN",
        "Broken",
        "DISABLED",
        "_Backup",
    ]

    for exclusion in exclusions:
        if exclusion in item_name or exclusion in display_name:
            return True

    return False


def generate_wiki_template(item_model):
    """Generate MediaWiki template for an item."""
    lines = []
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(f" | name          = {item_model['DisplayName']}")

    # Type field - join multiple types with <br>
    type_value = ""
    if item_model.get("ItemTypes"):
        type_value = "<br>".join(item_model["ItemTypes"])
    lines.append(f" | type          = {type_value}")
    lines.append(" | subtype       = ")

    # Properties section (description moved to separate section below)
    if item_model.get("MaxStackSize") and item_model["MaxStackSize"] > 1:
        lines.append(f" | stack         = {item_model['MaxStackSize']}")

    if item_model.get("SlotSize") and item_model["SlotSize"] > 1:
        lines.append(f" | slots         = {item_model['SlotSize']}")

    # Removed: BaseTradeValue display
    # if item_model.get("BaseTradeValue") and item_model["BaseTradeValue"] > 0:
    #     lines.append(f"| value = {item_model['BaseTradeValue']:.1f}")

    if item_model.get("Portability"):
        portability = item_model["Portability"]
        if portability == "HeavyCarry":
            lines.append(" | heavy         = Yes")
        elif portability == "NotPortable":
            lines.append(" | portable      = No")

    # Tags
    if item_model.get("Tags"):
        tags_formatted = ", ".join(item_model["Tags"])
        lines.append(f" | tags          = {tags_formatted}")

    # Reqs field - list all positive flags separated by <br>
    reqs_flags = []
    if item_model.get("Gathered", False):
        reqs_flags.append("Harvestable")
    if item_model.get("Building", False):
        reqs_flags.append("Building")
    if item_model.get("Crafting", False):
        reqs_flags.append("Crafting")
    if item_model.get("Cooking", False):
        reqs_flags.append("Cooking")
    if item_model.get("Farming", False):
        reqs_flags.append("Farming")
    if item_model.get("Brewing", False):
        reqs_flags.append("Brewing")

    if reqs_flags:
        reqs_value = "<br>".join(reqs_flags)
        lines.append(f" | reqs          = {reqs_value}")

    lines.append("}}")

    # Intro line
    lines.append("")
    lines.append("'''{{PAGENAME}}''' are an Ingredient [[item]] in ''[[{{topic}}]]''.")

    # Description section
    if item_model.get("Description"):
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {item_model['Description']}")

    # Crafting section - only show if there's actual crafting data
    if item_model.get("HasRecipe") and (item_model.get("CraftingStations") or item_model.get("CraftingMaterials")):
        lines.append("")
        lines.append("== Crafting ==")

        if item_model.get("CraftingStations"):
            stations = ", ".join([f"{{{{LI|{s}}}}}" for s in item_model["CraftingStations"]])
            lines.append(f"'''Station:''' {stations}")

        if item_model.get("CraftingMaterials"):
            lines.append("'''Materials:'''")
            for count, material in item_model["CraftingMaterials"]:
                lines.append(f"* ({count}) {{{{LI|{material}}}}}")

        if item_model.get("CraftTime") and item_model["CraftTime"] > 0:
            lines.append(f"'''Time:''' {item_model['CraftTime']:.1f}s")

    # Removed: Unlock section
    # lines.append("== Unlock ==")
    # if item_model.get("CampaignUnlock"):
    #     lines.append(f"| campaign = {item_model['CampaignUnlock']}")
    # if item_model.get("SandboxUnlock"):
    #     lines.append(f"| sandbox = {item_model['SandboxUnlock']}")

    return "\n".join(lines)


def process_items(items_data, recipes_data, string_map):
    """Process all items and generate wiki models."""
    print("\nProcessing items...")
    item_models = []
    excluded_items = []

    for item_entry in items_data:
        item_name = item_entry.get("Name", "")

        # Get basic properties
        display_name = get_display_name(item_entry, string_map)

        # Check exclusions
        if should_exclude_item(item_name, display_name):
            excluded_items.append((item_name, display_name))
            continue

        # Get tags
        tags = get_tags(item_entry)

        # Process tags to extract types and usage flags
        tag_properties = process_tags_for_properties(tags)

        # Build item model
        item_model = {
            "Name": item_name,
            "DisplayName": display_name,
            "Description": get_description(item_entry, string_map),
            "ActorPath": get_actor_path(item_entry),
            "IconPath": get_icon_path(item_entry),
            "MaxStackSize": get_max_stack_size(item_entry),
            "SlotSize": get_slot_size(item_entry),
            "BaseTradeValue": get_base_trade_value(item_entry),
            "Portability": get_portability(item_entry),
            "Tags": tags,
            "ItemTypes": tag_properties["types"],
            "Gathered": tag_properties["gathered"],
            "Crafting": tag_properties["crafting"],
            "Building": tag_properties["building"],
            "Brewing": tag_properties["brewing"],
            "Cooking": tag_properties["cooking"],
            "Farming": tag_properties["farming"],
        }

        # Detect DLC
        is_dlc, dlc_title, dlc_name = detect_dlc(item_model["ActorPath"], item_model["IconPath"])
        if is_dlc:
            item_model["DLC"] = True
            item_model["DLCTitle"] = dlc_title
            item_model["DLCName"] = dlc_name
        else:
            item_model["DLC"] = False

        # Parse recipe data if available
        recipe = recipes_data.get(item_name)
        if recipe:
            item_model["HasRecipe"] = True
            item_model["CraftingMaterials"] = parse_recipe_materials(recipe, string_map)
            item_model["CraftingStations"] = parse_crafting_stations(recipe, string_map)
            item_model["CraftTime"] = parse_crafting_time(recipe)
            item_model["UnlockType"] = parse_unlock_type(recipe)
            item_model["FragmentsRequired"] = parse_fragments_required(recipe)
            item_model["Tier"] = parse_tier(recipe)
            item_model["HasSandboxUnlockOverride"] = parse_has_sandbox_unlock_override(recipe)

            # Generate unlock text
            item_model["CampaignUnlock"] = format_unlock_text(
                display_name, item_model["UnlockType"], item_model["FragmentsRequired"],
                item_model["Tier"], is_dlc, dlc_title, item_model["HasSandboxUnlockOverride"], True
            )

            # Sandbox unlock
            if item_model["HasSandboxUnlockOverride"]:
                item_model["SandboxUnlock"] = format_unlock_text(
                    display_name, item_model["UnlockType"], item_model["FragmentsRequired"],
                    item_model["Tier"], is_dlc, dlc_title, item_model["HasSandboxUnlockOverride"], False
                )
            else:
                # Use campaign unlock for sandbox if no override
                item_model["SandboxUnlock"] = item_model["CampaignUnlock"]
        else:
            item_model["HasRecipe"] = False
            # Items without recipes - likely found/gathered items
            if is_dlc:
                item_model["CampaignUnlock"] = f"Purchase {dlc_title}"
                item_model["SandboxUnlock"] = f"Purchase {dlc_title}"
            else:
                item_model["CampaignUnlock"] = "{{LI|Return to Moria}}"
                item_model["SandboxUnlock"] = "{{LI|Return to Moria}}"

        item_models.append(item_model)

    print(f"  Processed {len(item_models)} items")
    print(f"  Excluded {len(excluded_items)} items")
    return item_models, excluded_items


def write_wiki_files(item_models, output_dir):
    """Write wiki template files for each item."""
    print(f"\nWriting wiki files to {output_dir}...")

    os.makedirs(output_dir, exist_ok=True)

    for item in item_models:
        wiki_content = generate_wiki_template(item)
        filename = f"{item['DisplayName']}.wiki"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(item_models)} wiki files")


def write_excluded_log(excluded_items, output_dir):
    """Write log file of excluded items."""
    log_path = os.path.join(output_dir, "excluded_items.log")

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("Excluded Items Log\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total excluded: {len(excluded_items)}\n\n")

        for item_name, display_name in excluded_items:
            f.write(f"{item_name}\n")
            f.write(f"  Display Name: {display_name}\n")
            f.write("\n")

    print(f"  Wrote exclusion log: {log_path}")


def main():
    print("Loading data...")

    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"  Total strings: {len(string_map)}")

    # Load items data
    print("Loading items data...")
    items_data = load_items_data(ITEMS_FILE)
    print(f"  Total items: {len(items_data)}")

    # Load recipes data
    print("Loading recipes data...")
    recipes_data = load_recipe_data(RECIPES_FILE)
    print(f"  Total recipes: {len(recipes_data)}")

    # Process items
    item_models, excluded_items = process_items(items_data, recipes_data, string_map)

    # Write wiki files
    write_wiki_files(item_models, OUTPUT_DIR)

    # Write exclusion log to output root directory
    if excluded_items:
        write_excluded_log(excluded_items, "output")

    print("\nDone!")


if __name__ == "__main__":
    main()
