import json
import os

# Paths
SOURCE_DIR = "source"
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")
CONSUMABLES_FILE = os.path.join(SOURCE_DIR, "DT_Consumables.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join("output", "consumables")

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

# Special campaign unlock overrides for items with unique unlock methods
CAMPAIGN_UNLOCK_OVERRIDE = {
    "Salt-cured Fish": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Arnor Trader}} OR {{LI|Blue Mountains Trader}}",
    "Saffron": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Red Mountains Trader}}",
    "Southern Oil": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Gondor Trader}}",
    "Whale Tallow": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Gondor Trader}}",
    "Thanazutsam": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Rivendell Trader}}",
}

# Special sandbox unlock overrides for items with unique unlock methods
SANDBOX_UNLOCK_OVERRIDE = {
    "Salt-cured Fish": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Arnor Trader}} OR {{LI|Blue Mountains Trader}}",
    "Saffron": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Red Mountains Trader}}",
    "Southern Oil": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Gondor Trader}}",
    "Whale Tallow": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Gondor Trader}}",
    "Thanazutsam": "Purchase the {{LI|Durin's Folk}} Expansion, Purchased from the {{LI|Rivendell Trader}}",
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
    # Hearths
    "CraftingStation_Hearth": "Constructions.Hearth_Small.name",
    "CraftingStation_Hearth_SmallHearth": "Constructions.Hearth_Small.name",
    "CraftingStation_Hearth_MiniHearth": "Constructions.Hearth_Mini.Name",
    "CraftingStation_Hearth_MediumHearth": "Constructions.Hearth_MediumFireplace.Name",
    "CraftingStation_Hearth_LargeHearth": "Constructions.Hearth_LargeHearth.Name",
    # Kitchen stations
    "CraftingStation_Kitchen": "Constructions.Kitchen_Stove.Name",
    "CraftingStation_Kitchen_Stove": "Constructions.Kitchen_Stove.Name",
    "CraftingStation_Kitchen_Oven": "Constructions.Kitchen_Oven.Name",
    "CraftingStation_Kitchen_PitBBQ": "Constructions.Kitchen_PitBBQ.Name",
    # Breweries
    "Brewery_Base": "Constructions.BreweryUpgradeStation.Name",
    "Brewery_Small": "Constructions.BreweryUpgradeStation.Name",
    "Brewery_Massive": "Constructions.BreweryUpgradeStation.Name",
    # Campfire
    "CraftingStation_Campfire": "Constructions.Campfire",
    "CraftingStation_Campfire_Sandbox": "Constructions.Campfire",
    # Other stations
    "CraftingStation_Workbench": "Constructions.Workbench",
    "CraftingStation_MealTable": "Constructions.MealTable",
    "CraftingStation_FabricStation": "Constructions.FabricStation.Name",
    "CraftingStation_Mill": "Constructions.Mill.Name",
    "CraftingStation_PurificationStation": "Constructions.PurificationStation.Name",
    "CraftingStation_TintingStation": "Constructions.TintingStation.Name",
}

# Material name mappings for special cases
MATERIAL_KEY_MAP = {
    "Item.Scrap": "Metal Fragments",
}

# Tag to property mappings for consumables
TAG_MAPPINGS = {
    # Food tags
    "Item.Food.Cheese": {"type": "Food", "subtype": "Cheese"},
    "Item.Food.Eggs": {"type": "Food", "subtype": "Eggs"},
    "Item.Food.Fruit": {"type": "Food", "subtype": "Fruit", "notes": ["Farming: Need Light"]},
    "Item.Food.Honey": {"type": "Food", "subtype": "Honey"},
    "Item.Food.Meat": {"type": "Food", "subtype": "Meat"},
    "Item.Food.Spice": {"type": "Food", "subtype": "Spices"},
    "Item.Food.Veg.Flower": {"type": "Food", "subtype": "Flower", "notes": ["Farming: Need Light"]},
    "Item.Food.Veg.Grain": {"type": "Food", "subtype": "Grain", "notes": ["Farming: Need Light"]},
    "Item.Food.Veg.Herb": {"type": "Food", "subtype": "Herbs", "notes": ["Farming: Need Light"]},
    "Item.Food.Veg.Mushroom": {"type": "Food", "subtype": "Mushrooms", "notes": ["Farming: Need Darkness"]},
    "Item.Food.Veg": {"type": "Food", "subtype": "Vegetables", "notes": ["Farming: Need Light"]},
    "Item.Food": {"type": "Food"},

    # Mineral tags
    "Item.Mineral.Ore": {"type": "Ore"},

    # Brewing ingredient
    "Item.BrewIngredient": {"stats": ["Brewing Ingredient"]},

    # Meal complexity and time tags
    "UI.BreakfastMeal.Complex": {"type": "Meal", "subtype": "Breakfast", "notes": ["Complexity: Complex", "Meal Time: Breakfast"]},
    "UI.BreakfastMeal.Reasonable": {"type": "Meal", "subtype": "Breakfast", "notes": ["Complexity: Reasonable", "Meal Time: Breakfast"]},
    "UI.BreakfastMeal.Simple": {"type": "Meal", "subtype": "Breakfast", "notes": ["Complexity: Simple", "Meal Time: Breakfast"]},
    "UI.LunchMeal.Complex": {"type": "Meal", "subtype": "Lunch", "notes": ["Complexity: Complex", "Meal Time: Lunch"]},
    "UI.LunchMeal.Reasonable": {"type": "Meal", "subtype": "Lunch", "notes": ["Complexity: Reasonable", "Meal Time: Lunch"]},
    "UI.LunchMeal.Simple": {"type": "Meal", "subtype": "Lunch", "notes": ["Complexity: Simple", "Meal Time: Lunch"]},
    "UI.DinnerMeal.Complex": {"type": "Meal", "subtype": "Dinner", "notes": ["Complexity: Complex", "Meal Time: Dinner"]},
    "UI.DinnerMeal.Reasonable": {"type": "Meal", "subtype": "Dinner", "notes": ["Complexity: Reasonable", "Meal Time: Dinner"]},
    "UI.DinnerMeal.Simple": {"type": "Meal", "subtype": "Dinner", "notes": ["Complexity: Simple", "Meal Time: Dinner"]},

    # Ration tags
    "UI.Ration.Complex": {"type": "Ration", "notes": ["Complexity: Complex"]},
    "UI.Ration.Reasonable": {"type": "Ration", "notes": ["Complexity: Reasonable"]},
    "UI.Ration.Simple": {"type": "Ration", "notes": ["Complexity: Simple"]},

    # Special types
    "UI.Abahk": {"type": "Âbakh"},
    "UI.Processed": {"subtype": "Crafted"},

    # Ignore tags
    "UI.Lore.Consumables": {},
    "UI.Premium": {},
    "UI.Tinted": {},

    # Legacy fallback
    "Item.Consumable.Meal": {"type": "Meal"},
    "Item.Consumable.Ration": {"type": "Ration"},
    "Item.Consumable.Potion": {"type": "Potion"},
    "Item.Consumable.Ingredient": {"type": "Ingredient"},
    "Item.Consumable": {"type": "Consumable"},
}


def load_consumables_data(filepath):
    """Load DT_Consumables.json and return a list of consumable entries and imports."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tradegoods_list = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            tradegood_entries = table.get("Data", [])
            tradegoods_list.extend(tradegood_entries)

    imports = data.get("Imports", [])
    return tradegoods_list, imports


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


def load_all_string_tables(strings_dir):
    """Load all string table JSON files and merge them into a single map."""
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
        if path and "/DLC/" in path:
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


def parse_use_effects(properties, imports):
    """Extract UseEffects from properties and resolve them using imports."""
    effects = []

    for prop in properties:
        if prop.get("Name") == "UseEffects":
            effect_refs = prop.get("Value", [])
            for effect_ref in effect_refs:
                idx = effect_ref.get("Value")
                if idx and idx < 0:
                    # Negative index means it's an import reference
                    import_idx = abs(idx) - 1
                    if import_idx < len(imports):
                        imp = imports[import_idx]
                        effect_name = imp.get("ObjectName", "")
                        if effect_name:
                            # Clean up the effect name
                            # Remove _C suffix and GE_ prefix
                            clean_name = effect_name.replace("_C", "").replace("GE_", "")
                            # Replace underscores with spaces and title case
                            clean_name = clean_name.replace("_", " ").title()
                            effects.append(clean_name)

    return effects


def process_tags_for_properties(tags):
    """
    Process gameplay tags and extract type, subtype, notes, and stats.
    Returns a dict with 'types', 'subtypes', 'notes', and 'stats' (all lists, no duplicates).
    """
    result = {
        "types": [],
        "subtypes": [],
        "notes": [],
        "stats": [],
    }

    for tag in tags:
        if tag in TAG_MAPPINGS:
            mapping = TAG_MAPPINGS[tag]

            # Add type if present and not duplicate
            if "type" in mapping and mapping["type"] not in result["types"]:
                result["types"].append(mapping["type"])

            # Add subtype if present and not duplicate
            if "subtype" in mapping and mapping["subtype"] not in result["subtypes"]:
                result["subtypes"].append(mapping["subtype"])

            # Add notes if present (each note checked for duplicates)
            if "notes" in mapping:
                for note in mapping["notes"]:
                    if note not in result["notes"]:
                        result["notes"].append(note)

            # Add stats if present (each stat checked for duplicates)
            if "stats" in mapping:
                for stat in mapping["stats"]:
                    if stat not in result["stats"]:
                        result["stats"].append(stat)

    return result


def generate_wiki_template(consumable_model):
    """Generate MediaWiki template text for a consumable."""
    lines = []

    # Item infobox
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(f" | name          = {consumable_model['DisplayName']}")

    # Type
    if consumable_model.get("Type"):
        lines.append(f" | type          = {consumable_model['Type']}")
    else:
        lines.append(" | type          = ")

    # Subtype (from tags)
    if consumable_model.get("Subtypes"):
        subtype_str = "<br>".join(consumable_model["Subtypes"])
        lines.append(f" | subtype       = {subtype_str}")
    else:
        lines.append(" | subtype       = ")

    # Stack size
    if consumable_model.get("MaxStackSize"):
        lines.append(f" | stack         = {consumable_model['MaxStackSize']}")

    # Tags
    if consumable_model.get("Tags"):
        lines.append(f" | tags          = {', '.join(consumable_model['Tags'])}")

    lines.append("}}")
    lines.append("")
    lines.append("'''{{PAGENAME}}''' is a [[Consumable]] in ''[[{{topic}}]]''.")

    # Description section (only if non-empty)
    if consumable_model.get("Description") and consumable_model["Description"].strip():
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {consumable_model['Description']}")

    # Unlocks section (only if unlock overrides exist)
    if consumable_model.get("CampaignUnlock") or consumable_model.get("SandboxUnlock"):
        lines.append("")
        lines.append("== Unlocks ==")
        lines.append("")
        if consumable_model.get("CampaignUnlock"):
            lines.append(f"* Campaign {{{{spoiler|{consumable_model['CampaignUnlock']}}}}}")
        if consumable_model.get("SandboxUnlock"):
            lines.append(f"* Sandbox  {{{{spoiler|{consumable_model['SandboxUnlock']}}}}}")

    # Stats section
    has_stats = (
        (consumable_model.get("HungerRestore") and consumable_model["HungerRestore"] > 0) or
        (consumable_model.get("HealthRestore") and consumable_model["HealthRestore"] > 0) or
        (consumable_model.get("EnergyRestore") and consumable_model["EnergyRestore"] > 0) or
        (consumable_model.get("TagStats") and len(consumable_model["TagStats"]) > 0)
    )

    if has_stats:
        lines.append("")
        lines.append("==Stats==")

        if consumable_model.get("HungerRestore") and consumable_model["HungerRestore"] > 0:
            lines.append(f"* '''Hunger:''' {consumable_model['HungerRestore']}")

        if consumable_model.get("HealthRestore") and consumable_model["HealthRestore"] > 0:
            lines.append(f"* '''Health:''' {consumable_model['HealthRestore']}")

        if consumable_model.get("EnergyRestore") and consumable_model["EnergyRestore"] > 0:
            lines.append(f"* '''Energy:''' {consumable_model['EnergyRestore']}")

        # Add tag-derived stats
        if consumable_model.get("TagStats"):
            for tag_stat in consumable_model["TagStats"]:
                lines.append(f"* {tag_stat}")

    # Use section (effects) - only if non-empty
    if consumable_model.get("UseEffects") and len(consumable_model["UseEffects"]) > 0:
        lines.append("")
        lines.append("==Use==")
        for effect in consumable_model["UseEffects"]:
            lines.append(f"* {effect}")

    # Crafting section
    if consumable_model.get("HasRecipe") and (consumable_model.get("CraftingStations") or consumable_model.get("CraftingMaterials")):
        lines.append("")
        lines.append("== Crafting ==")
        lines.append("")

        # Crafting time
        craft_time = consumable_model.get("CraftTime")
        if craft_time:
            try:
                craft_time = float(craft_time) if isinstance(craft_time, str) else craft_time
                if craft_time > 0:
                    # Format time as integer if it's a whole number, otherwise show decimal
                    if craft_time == int(craft_time):
                        lines.append(f"Time: {int(craft_time)} seconds")
                    else:
                        lines.append(f"Time: {craft_time} seconds")
                    lines.append("")
            except (ValueError, TypeError):
                pass

        # Stations
        if consumable_model.get("CraftingStations"):
            lines.append("Station:")
            lines.append("")
            for station in consumable_model["CraftingStations"]:
                lines.append(f"* {{{{LI|{station}}}}}")
            lines.append("")

        # Materials
        if consumable_model.get("CraftingMaterials"):
            lines.append("Materials:")
            lines.append("")
            for count, material in consumable_model["CraftingMaterials"]:
                lines.append(f"* ({count}) {{{{LI|{material}}}}}")

    # Notes section - only if there are notes to add
    if consumable_model.get("TagNotes") and len(consumable_model["TagNotes"]) > 0:
        lines.append("")
        lines.append("==Notes==")
        for tag_note in consumable_model["TagNotes"]:
            lines.append(f"* {tag_note}")

    return "\n".join(lines)


def process_consumables(consumables_data, recipes_data, string_map, imports):
    """Process all consumables and generate wiki models."""
    print("\nProcessing consumables...")
    consumable_models = []
    excluded_consumables = []

    for consumable_entry in consumables_data:
        consumable_name = consumable_entry.get("Name", "")

        # Skip UNSHIPPABLE items
        if "UNSHIPPABLE" in consumable_name:
            excluded_consumables.append({
                "name": consumable_name,
                "reason": "UNSHIPPABLE item"
            })
            continue

        # Get properties
        properties = consumable_entry.get("Value", [])

        # Extract basic info
        display_name = get_string_property(properties, "DisplayName", string_map)
        description = get_string_property(properties, "Description", string_map)
        icon_path = get_property_value(properties, "Icon")
        actor_path = get_property_value(properties, "Actor")

        # Skip if no display name
        if not display_name:
            excluded_consumables.append({
                "name": consumable_name,
                "reason": "No display name"
            })
            continue

        # Extract tags
        tags = get_tags_list(properties)
        tag_properties = process_tags_for_properties(tags)

        # Determine type
        item_type = tag_properties["types"][0] if tag_properties["types"] else "Consumable"

        # Parse UseEffects
        use_effects = parse_use_effects(properties, imports)

        # Build consumable model
        consumable_model = {
            "Name": consumable_name,
            "DisplayName": display_name,
            "Description": description or "",
            "Type": item_type,
            "Subtypes": tag_properties["subtypes"],
            "TagNotes": tag_properties["notes"],
            "TagStats": tag_properties["stats"],
            "IconPath": icon_path or "",
            "ActorPath": actor_path or "",
            "Tags": tags,
            "MaxStackSize": get_property_value(properties, "MaxStackSize"),
            "HungerRestore": get_property_value(properties, "HungerRestore"),
            "HealthRestore": get_property_value(properties, "HealthRestore"),
            "EnergyRestore": get_property_value(properties, "EnergyRestore"),
            "UseEffects": use_effects,
        }

        # Detect DLC
        is_dlc, dlc_title, dlc_name = detect_dlc(consumable_model["ActorPath"], consumable_model["IconPath"])
        if is_dlc:
            consumable_model["DLC"] = True
            consumable_model["DLCTitle"] = dlc_title
            consumable_model["DLCName"] = dlc_name
        else:
            consumable_model["DLC"] = False

        # Parse recipe data if available
        recipe = recipes_data.get(consumable_name)
        if recipe:
            consumable_model["HasRecipe"] = True
            consumable_model["CraftingMaterials"] = parse_recipe_materials(recipe, string_map)
            consumable_model["CraftingStations"] = parse_crafting_stations(recipe, string_map)
            consumable_model["CraftTime"] = parse_crafting_time(recipe)
        else:
            consumable_model["HasRecipe"] = False

        # Check for unlock overrides
        if display_name in CAMPAIGN_UNLOCK_OVERRIDE:
            consumable_model["CampaignUnlock"] = CAMPAIGN_UNLOCK_OVERRIDE[display_name]
        if display_name in SANDBOX_UNLOCK_OVERRIDE:
            consumable_model["SandboxUnlock"] = SANDBOX_UNLOCK_OVERRIDE[display_name]

        consumable_models.append(consumable_model)

    print(f"  Processed {len(consumable_models)} consumables")
    print(f"  Excluded {len(excluded_consumables)} consumables")
    return consumable_models, excluded_consumables


def write_wiki_files(consumable_models, output_dir):
    """Write wiki files for all consumables."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nWriting wiki files to {output_dir}...")
    for consumable_model in consumable_models:
        filename = f"{consumable_model['DisplayName']}.wiki"
        filepath = os.path.join(output_dir, filename)

        wiki_content = generate_wiki_template(consumable_model)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(consumable_models)} wiki files")


def write_excluded_log(excluded_consumables, output_root):
    """Write a log of excluded consumables."""
    if not excluded_consumables:
        return

    log_path = os.path.join(output_root, "excluded_consumables.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Excluded {len(excluded_consumables)} consumables:\n\n")
        for item in excluded_consumables:
            f.write(f"{item['name']}: {item['reason']}\n")
    print(f"\nWrote exclusion log to {log_path}")


def main():
    print("Loading data...")

    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"  Total strings: {len(string_map)}")

    # Load consumables data
    print("Loading consumables data...")
    consumables_data, imports = load_consumables_data(CONSUMABLES_FILE)
    print(f"  Total consumables: {len(consumables_data)}")

    # Load recipes data
    print("Loading recipes data...")
    recipes_data = load_recipe_data(RECIPES_FILE)
    print(f"  Total recipes: {len(recipes_data)}")

    # Process consumables
    consumable_models, excluded_consumables = process_consumables(consumables_data, recipes_data, string_map, imports)

    # Write wiki files
    write_wiki_files(consumable_models, OUTPUT_DIR)

    # Write exclusion log to output root directory
    if excluded_consumables:
        write_excluded_log(excluded_consumables, "output")

    print("\nDone!")


if __name__ == "__main__":
    main()
