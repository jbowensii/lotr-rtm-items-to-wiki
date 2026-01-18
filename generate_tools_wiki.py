import json
import os
import re

# Paths - Updated for new datajson structure
OUTPUT_BASE = os.path.join(os.environ.get("APPDATA", ""), "MoriaWikiGenerator", "output")
SOURCE_DIR = os.path.join(OUTPUT_BASE, "datajson", "Moria", "Content", "Tech", "Data")
STRINGS_DIR = os.path.join(SOURCE_DIR, "StringTables")
TOOLS_FILE = os.path.join(SOURCE_DIR, "Items", "DT_Tools.json")
THROWLIGHTS_FILE = os.path.join(SOURCE_DIR, "Items", "DT_ThrowLights.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "Items", "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join(OUTPUT_BASE, "wiki", "tools")

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
    "Durin's Axe": "Find the 5 fragments as part of the adventure",
    "Torch": "Obtain [[Wood Scraps]]",
    "Simple Pickaxe": "Obtain {{LI|Metal Fragments}}",
    "Steel Pickaxe": "Repair the [[Great Forge of Narvi]]",
    "First Age Pickaxe": "Obtain a {{LI|Black Diamond}}",
    "Ironwood Pickaxe": "Obtain a {{LI|Shanôr Ingot}}",
    "Quarrymaster": "Craft a {{LI|First Age Pickaxe}}",
    "Zarôk Torch": "Obtaining {{LI|True-quartz}}",
    "Iron Hammer": "Repair an abandoned {{LI|Forge}}",
    "Steel Hammer": "Repair the [[Great Forge of Narvi]]",
    "Shanôr Hammer": "Achieve the Goal of restoring the [[Library of Kibil-nâla]] in the [[Lower Deeps]]",
    "Star-metal Hammer": "Obtain {{LI|Star-metal Ore}}",
    "Adamant Hammer": "Talking to {{LI|Aric}} after defeating [[Narag-Shazon]]",
    "Wood Flare": "Build or repair a {{LI|Stone Hearth}}",
    "Crystal Flare": "Obtaining {{LI|True-quartz}}",
    # NPC Tools (all from Durin's Folk Expansion)
    "Metalworker's Stoking Rod": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Brewmaster's Paddle": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Artisan's Adze": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Blacksmith's Mallet": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Builder's Mallet": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Cook's Frying Pan": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Salvager's Creel": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Grocer's Staff": "Purchase the {{LI|Durin's Folk}} Expansion",
}

# Special sandbox unlock overrides for items with unique unlock methods
SANDBOX_UNLOCK_OVERRIDE = {
    "Durin's Axe": "Retrieve 4 fragments from Orc Warchiefs",
    "Torch": "Obtain [[Wood Scraps]]",
    "Simple Pickaxe": "Obtain {{LI|Metal Fragments}}",
    "Steel Pickaxe": "Obtain a {{LI|Steel Ingot}}",
    "First Age Pickaxe": "Build or repair a {{LI|Gem Cutter}}",
    "Ironwood Pickaxe": "Obtain a {{LI|Shanôr Ingot}}",
    "Quarrymaster": "Repair the {{LI|Great Belegost Forge}}",
    "Zarôk Torch": "Obtaining {{LI|True-quartz}}",
    "Iron Hammer": "Build a {{LI|Forge}}",
    "Steel Hammer": "Obtain a {{LI|Steel Ingot}}",
    "Shanôr Hammer": "Repair the [[Great Belegost Forge]]",
    "Star-metal Hammer": "Obtain {{LI|Star-metal Ore}}",
    "Adamant Hammer": "Repair the {{LI|Great Mithril Forge}}",
    "Wood Flare": "Build or repair a {{LI|Stone Hearth}}",
    "Crystal Flare": "Obtaining {{LI|True-quartz}}",
    # NPC Tools (all from Durin's Folk Expansion)
    "Metalworker's Stoking Rod": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Brewmaster's Paddle": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Artisan's Adze": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Blacksmith's Mallet": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Builder's Mallet": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Cook's Frying Pan": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Salvager's Creel": "Purchase the {{LI|Durin's Folk}} Expansion",
    "Grocer's Staff": "Purchase the {{LI|Durin's Folk}} Expansion",
}

# Mapping from CraftingStation keys to Constructions string keys
STATION_KEY_MAP = {
    # Forges
    "CraftingStation_BasicForge": "Constructions.BasicForge",
    "CraftingStation_AdvancedForge": "Constructions.ForgeAdvanced",
    "CraftingStation_FloodedForge": "Constructions.FloodedForge",
    "CraftingStation_GreatForge": "Constructions.GreatForge",
    "CraftingStation_MithrilForge": "Constructions.MithrilForge",
    "CraftingStation_NogrodForge": "Constructions.NogrodForge",
    "CraftingStation_BelegostForge": "Constructions.BelegostForge",
    "CraftingStation_ElvenForge": "Constructions.ElvenForge",
    # Crafting stations
    "CraftingStation_Workbench": "Constructions.Workbench",
    "CraftingStation_Loom": "Constructions.Loom.Name",
    "CraftingStation_StoneCutter": "Constructions.Stonecutter.Name",
    "CraftingStation_GemCutter": "Constructions.Gemcutter.Name",
    "CraftingStation_MapTable": "Constructions.MapTable",
    # Food stations
    "CraftingStation_Hearth": "Constructions.Hearth_Small.name",
    "CraftingStation_Kitchen": "Constructions.Kitchen_Stove.Name",
    "CraftingStation_Mill": "Constructions.Mill.Name",
    "CraftingStation_PurificationStation": "Constructions.PurificationStation.Name",
    "CraftingStation_TintingStation": "Constructions.TintingStation.Name",
}

# Tool type tag to display name mapping
TOOL_TYPE_MAP = {
    "Item.Tool.Pickaxe": "Pickaxe",
    "Item.Tool.Pickaxe.2H": "Pickaxe",
    "Item.Tool.Torch": "Torch",
    "Item.Tool.RestorationHammer": "Restoration Hammer",
    "Item.Tool.Basket": "Basket",
    "Item.Tool.BlacksmithHammer": "Blacksmith Hammer",
    "Item.Tool.Chisel": "Chisel",
    "Item.Tool.FryingPan": "Frying Pan",
    "Item.Tool.GrocerStaff": "Grocer Staff",
    "Item.Tool.Loupe": "Loupe",
    "Item.Tool.MashPaddle": "Mash Paddle",
    "Item.Tool.Scissors": "Scissors",
    "Item.Tool.Spanner": "Spanner",
    "Item.Tool.Tong": "Tongs",
}

# Unlock type mapping for user-friendly display
UNLOCK_TYPE_DISPLAY = {
    "DiscoverDependencies": "Unlocked by discovering dependencies",
    "Manual": "Manual unlock",
    "Unknown": "Unknown",
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


def load_tools_data(filepath):
    """Load DT_Tools.json and return the list of tool entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tools_list = []
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.DataTableExport, UAssetAPI":
            table = export.get("Table", {})
            tool_entries = table.get("Data", [])
            tools_list.extend(tool_entries)

    return tools_list


def load_throwlights_data(filepath):
    """Load DT_ThrowLights.json and return the list of throw light entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    throwlights_list = []
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.DataTableExport, UAssetAPI":
            table = export.get("Table", {})
            throwlight_entries = table.get("Data", [])
            throwlights_list.extend(throwlight_entries)

    return throwlights_list


def load_recipe_data(filepath):
    """Load DT_ItemRecipes.json and return a dictionary keyed by result item handle."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipe_map = {}
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.DataTableExport, UAssetAPI":
            table = export.get("Table", {})
            recipe_entries = table.get("Data", [])
            for entry in recipe_entries:
                recipe = extract_recipe(entry)
                if recipe and recipe.get("ResultItemHandle"):
                    recipe_map[recipe["ResultItemHandle"]] = recipe

    return recipe_map


def extract_recipe(recipe_entry):
    """Extract recipe data from a recipe entry."""
    properties = recipe_entry.get("Value", [])

    recipe = {
        "RecipeName": recipe_entry.get("Name", ""),
        "ResultItemHandle": "",
        "ResultItemCount": 1,
        "CraftTimeSeconds": 0.0,
        "CraftingStations": [],
        "Materials": [],
        "CampaignUnlockType": "",
        "CampaignUnlockFragments": 0,
        "SandboxUnlockType": "",
        "SandboxUnlockFragments": 0,
        "bHasSandboxUnlockOverride": False,
    }

    for prop in properties:
        prop_name = prop.get("Name", "")
        prop_value = prop.get("Value")

        if prop_name == "ResultItemHandle":
            # Extract RowName from the nested structure
            if isinstance(prop_value, list):
                for item in prop_value:
                    if item.get("Name") == "RowName":
                        recipe["ResultItemHandle"] = item.get("Value", "")

        elif prop_name == "ResultItemCount":
            recipe["ResultItemCount"] = prop_value if prop_value else 1

        elif prop_name == "CraftTimeSeconds":
            recipe["CraftTimeSeconds"] = prop_value if prop_value else 0.0

        elif prop_name in ("CraftingStations", "DefaultRequiredConstructions"):
            # Extract crafting stations - each is a MorConstructionRowHandle struct
            if isinstance(prop_value, list):
                stations = []
                for station_struct in prop_value:
                    station_data = station_struct.get("Value", [])
                    if isinstance(station_data, list):
                        for item in station_data:
                            if item.get("Name") == "RowName":
                                station_name = item.get("Value", "")
                                if station_name and station_name != "None":
                                    stations.append(station_name)
                recipe["CraftingStations"] = stations

        elif prop_name in ("RequiredMaterials", "DefaultRequiredMaterials"):
            # Extract materials list (supports both property names)
            if isinstance(prop_value, list):
                for material_entry in prop_value:
                    material_data = material_entry.get("Value", [])
                    material = {"Handle": "", "Count": 0}
                    for mat_prop in material_data:
                        mat_name = mat_prop.get("Name", "")
                        mat_value = mat_prop.get("Value")
                        if mat_name == "MaterialHandle":
                            # Extract RowName from MaterialHandle
                            if isinstance(mat_value, list):
                                for item in mat_value:
                                    if item.get("Name") == "RowName":
                                        material["Handle"] = item.get("Value", "")
                        elif mat_name == "Count":
                            material["Count"] = mat_value if mat_value else 0
                    if material["Handle"]:
                        recipe["Materials"].append(material)

        elif prop_name == "CampaignUnlock":
            # Extract unlock type
            if isinstance(prop_value, list):
                for item in prop_value:
                    if item.get("Name") == "UnlockType":
                        unlock_val = item.get("Value", "")
                        if "::" in unlock_val:
                            recipe["CampaignUnlockType"] = unlock_val.split("::")[-1]
                        else:
                            recipe["CampaignUnlockType"] = unlock_val
                    elif item.get("Name") == "CollectFragmentCount":
                        recipe["CampaignUnlockFragments"] = item.get("Value", 0)

        elif prop_name == "SandboxUnlock":
            # Extract sandbox unlock type
            if isinstance(prop_value, list):
                for item in prop_value:
                    if item.get("Name") == "UnlockType":
                        unlock_val = item.get("Value", "")
                        if "::" in unlock_val:
                            recipe["SandboxUnlockType"] = unlock_val.split("::")[-1]
                        else:
                            recipe["SandboxUnlockType"] = unlock_val
                    elif item.get("Name") == "CollectFragmentCount":
                        recipe["SandboxUnlockFragments"] = item.get("Value", 0)

        elif prop_name == "bHasSandboxUnlockOverride":
            recipe["bHasSandboxUnlockOverride"] = prop_value if prop_value else False

    return recipe


def find_string_by_suffix(item_key, string_map, suffix=".Name"):
    """Search string table for any key ending with .{item_key}{suffix}."""
    # Look for any key that ends with .{item_key}.Name (case-insensitive match on item_key)
    search_suffix = f".{item_key}{suffix}"
    search_suffix_lower = search_suffix.lower()

    for key in string_map:
        if key.lower().endswith(search_suffix_lower):
            return string_map[key]

    return None


# Special mapping for materials with non-standard naming (item handle -> string table key)
MATERIAL_KEY_MAP = {
    "Item.Scrap": "ScrapMetal",  # Item.Scrap maps to ScrapMetal in string tables
}


def get_material_display_name(material_handle, string_map):
    """Convert a material handle to its display name."""
    # Check special mapping first
    if material_handle in MATERIAL_KEY_MAP:
        item_key = MATERIAL_KEY_MAP[material_handle]
    elif "." in material_handle:
        item_key = material_handle.split(".")[-1]
    else:
        item_key = material_handle

    # Search for any string table key ending with .{item_key}.Name
    result = find_string_by_suffix(item_key, string_map, ".Name")
    if result:
        return result

    # Fallback: clean up the handle itself
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', item_key)
    return name


def get_station_display_name(station_tag, string_map):
    """Convert a crafting station tag to its display name."""
    # Station tags look like "CraftingStation_BasicForge"
    # Convert to key and look up in string map

    # Handle if station_tag is not a string
    if not isinstance(station_tag, str):
        return str(station_tag)

    # The station_tag is already in format "CraftingStation_BasicForge"
    station_key = station_tag

    if station_key in STATION_KEY_MAP:
        string_key = STATION_KEY_MAP[station_key]
        if string_key in string_map:
            return string_map[string_key]

    # Fallback: clean up the tag
    name = station_tag.replace("CraftingStation_", "")
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    return name


def get_repair_material_display_name(material_key, string_map):
    """Get display name for a repair material."""
    # Use the same logic as get_material_display_name
    return get_material_display_name(material_key, string_map)


def extract_tool_model(tool_entry, string_map, recipe_map):
    """Extract and transform tool entry into a data model."""
    game_name = tool_entry.get("Name", "")
    properties = tool_entry.get("Value", [])

    model = {
        "GameName": game_name,
        "DisplayName": "",
        "DisplayNameKey": "",
        "Description": "",
        "Tier": "",
        "SubType": "Tool",
        "Durability": 0,
        "StaminaCost": 0,
        "EnergyCost": 0,
        "CarveHits": 0,
        "MaxStackSize": 1,
        "MaxRepairCost": 0,
        "RepairMaterial": "",
        "RepairMaterialKey": "",
        "DLCPath": "",
        "DLCTitle": "",
        "CampaignUnlockType": "",
        "CampaignUnlockFragments": 0,
        "SandboxUnlockType": "",
        "SandboxUnlockFragments": 0,
        "HasRecipe": False,
        "EnabledState": "Enabled",
        "Tags": [],
        "IsThrowLight": False,
        "DurationSeconds": 0,
    }

    for prop in properties:
        prop_name = prop.get("Name", "")
        prop_value = prop.get("Value")

        if prop_name == "DisplayName":
            model["DisplayNameKey"] = prop_value if prop_value else ""
            # Look up in string table
            if prop_value and prop_value in string_map:
                model["DisplayName"] = string_map[prop_value]
            else:
                model["DisplayName"] = prop_value if prop_value else ""

        elif prop_name == "Description":
            if prop_value and prop_value in string_map:
                model["Description"] = string_map[prop_value]
            else:
                model["Description"] = prop_value if prop_value else ""

        elif prop_name == "Durability":
            model["Durability"] = prop_value if prop_value else 0

        elif prop_name == "StaminaCost":
            if prop_value and prop_value != "+0":
                try:
                    model["StaminaCost"] = float(prop_value.replace("+", ""))
                except (ValueError, AttributeError):
                    model["StaminaCost"] = prop_value

        elif prop_name == "EnergyCost":
            if prop_value and prop_value != "+0":
                try:
                    model["EnergyCost"] = float(prop_value.replace("+", ""))
                except (ValueError, AttributeError):
                    model["EnergyCost"] = prop_value

        elif prop_name == "CarveHits":
            model["CarveHits"] = prop_value if prop_value else 0

        elif prop_name == "MaxStackSize":
            model["MaxStackSize"] = prop_value if prop_value else 1

        elif prop_name == "DurationSeconds":
            model["DurationSeconds"] = prop_value if prop_value else 0
            model["IsThrowLight"] = True

        elif prop_name == "Tags":
            # Extract tags from gameplay tag container
            if isinstance(prop_value, list) and prop_value:
                tags = prop_value[0].get("Value", [])
                model["Tags"] = tags if isinstance(tags, list) else []

        elif prop_name == "InitialRepairCost":
            # Extract repair material and cost
            if isinstance(prop_value, list):
                for repair_item in prop_value:
                    repair_data = repair_item.get("Value", [])
                    for repair_prop in repair_data:
                        rp_name = repair_prop.get("Name", "")
                        rp_value = repair_prop.get("Value")
                        if rp_name == "MaterialHandle":
                            if isinstance(rp_value, list):
                                for item in rp_value:
                                    if item.get("Name") == "RowName":
                                        material_key = item.get("Value", "")
                                        if material_key and material_key != "None":
                                            model["RepairMaterialKey"] = material_key
                                            model["RepairMaterial"] = get_repair_material_display_name(
                                                material_key, string_map
                                            )
                        elif rp_name == "Count":
                            model["MaxRepairCost"] = rp_value if rp_value else 0

        elif prop_name == "EnabledState":
            # Extract enabled state (Enabled/Disabled)
            if isinstance(prop_value, str) and "::" in prop_value:
                model["EnabledState"] = prop_value.split("::")[-1]
            else:
                model["EnabledState"] = str(prop_value) if prop_value else "Enabled"

        elif prop_name == "Icon":
            # Check for DLC path in icon
            if isinstance(prop_value, dict):
                asset_path = prop_value.get("AssetPath", {})
                package_name = asset_path.get("PackageName", "") or ""
                if package_name and "/DLC/" in package_name:
                    model["DLCPath"] = package_name
                    # Extract DLC name
                    for dlc_key, dlc_title in DLC_TITLE_MAP.items():
                        if dlc_key in package_name:
                            model["DLCTitle"] = dlc_title
                            break

    # Extract tier from tags
    for tag in model["Tags"]:
        if "Tier1" in tag:
            model["Tier"] = "1"
        elif "Tier2" in tag:
            model["Tier"] = "2"
        elif "Tier3" in tag:
            model["Tier"] = "3"
        elif "Tier4" in tag:
            model["Tier"] = "4"
        elif "Masterwork" in tag:
            model["Tier"] = "5"
        elif "Item.EpicItem" in tag and not model["Tier"]:
            model["Tier"] = "5"

    # Extract tool subtype from tags
    for tag in model["Tags"]:
        if tag in TOOL_TYPE_MAP:
            model["SubType"] = TOOL_TYPE_MAP[tag]
            break

    # Special cases for subtypes
    if "Torch" in game_name and not model["SubType"]:
        model["SubType"] = "Torch"
    if "Restoration" in game_name or "Restoration" in model["DisplayName"]:
        model["SubType"] = "Restoration Hammer"
    if "Pickaxe" in game_name or "Pickaxe" in model["DisplayName"]:
        model["SubType"] = "Pickaxe"
    if "Rope" in game_name:
        model["SubType"] = "Rope"
    if "WarHorn" in game_name:
        model["SubType"] = "War Horn"

    # Look up recipe data using "Tool.{GameName}" as the key
    recipe_key = f"Tool.{game_name}"
    recipe = recipe_map.get(recipe_key)
    if recipe:
        model["HasRecipe"] = True
        model["CraftTime"] = recipe.get("CraftTimeSeconds", 0)
        model["CraftingStations"] = [
            get_station_display_name(s, string_map)
            for s in recipe.get("CraftingStations", [])
        ]
        model["CraftMaterials"] = [
            {
                "Name": get_material_display_name(m["Handle"], string_map),
                "Count": m["Count"]
            }
            for m in recipe.get("Materials", [])
        ]
        model["ResultCount"] = recipe.get("ResultItemCount", 1)

        # Use recipe unlock info if not overridden
        if recipe.get("bHasSandboxUnlockOverride"):
            model["CampaignUnlockType"] = recipe.get("CampaignUnlockType", "")
            model["CampaignUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)
            model["SandboxUnlockType"] = recipe.get("SandboxUnlockType", "")
            model["SandboxUnlockFragments"] = recipe.get("SandboxUnlockFragments", 0)
        else:
            # Same unlock for both modes
            model["CampaignUnlockType"] = recipe.get("CampaignUnlockType", "")
            model["CampaignUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)
            model["SandboxUnlockType"] = recipe.get("CampaignUnlockType", "")
            model["SandboxUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)

    return model


def extract_throwlight_model(throwlight_entry, string_map, recipe_map):
    """Extract and transform throw light entry into a data model."""
    game_name = throwlight_entry.get("Name", "")
    properties = throwlight_entry.get("Value", [])

    model = {
        "GameName": game_name,
        "DisplayName": "",
        "DisplayNameKey": "",
        "Description": "",
        "Tier": "",
        "SubType": "Throw Light",
        "Durability": -1,  # Expended on use
        "MaxStackSize": 1,
        "DurationSeconds": 0,
        "DLCPath": "",
        "DLCTitle": "",
        "CampaignUnlockType": "",
        "CampaignUnlockFragments": 0,
        "SandboxUnlockType": "",
        "SandboxUnlockFragments": 0,
        "HasRecipe": False,
        "EnabledState": "Enabled",
        "Tags": [],
        "IsThrowLight": True,
    }

    for prop in properties:
        prop_name = prop.get("Name", "")
        prop_value = prop.get("Value")

        if prop_name == "DisplayName":
            model["DisplayNameKey"] = prop_value if prop_value else ""
            if prop_value and prop_value in string_map:
                model["DisplayName"] = string_map[prop_value]
            else:
                model["DisplayName"] = prop_value if prop_value else ""

        elif prop_name == "Description":
            if prop_value and prop_value in string_map:
                model["Description"] = string_map[prop_value]
            else:
                model["Description"] = prop_value if prop_value else ""

        elif prop_name == "DurationSeconds":
            model["DurationSeconds"] = prop_value if prop_value else 0

        elif prop_name == "MaxStackSize":
            model["MaxStackSize"] = prop_value if prop_value else 1

        elif prop_name == "Tags":
            if isinstance(prop_value, list) and prop_value:
                tags = prop_value[0].get("Value", [])
                model["Tags"] = tags if isinstance(tags, list) else []

        elif prop_name == "EnabledState":
            if isinstance(prop_value, str) and "::" in prop_value:
                model["EnabledState"] = prop_value.split("::")[-1]
            else:
                model["EnabledState"] = str(prop_value) if prop_value else "Enabled"

        elif prop_name == "Icon":
            if isinstance(prop_value, dict):
                asset_path = prop_value.get("AssetPath", {})
                package_name = asset_path.get("PackageName", "") or ""
                if package_name and "/DLC/" in package_name:
                    model["DLCPath"] = package_name
                    for dlc_key, dlc_title in DLC_TITLE_MAP.items():
                        if dlc_key in package_name:
                            model["DLCTitle"] = dlc_title
                            break

    # Look up recipe data using "ThrowLight.{GameName}" as the key
    recipe_key = f"ThrowLight.{game_name}"
    recipe = recipe_map.get(recipe_key)
    if recipe:
        model["HasRecipe"] = True
        model["CraftTime"] = recipe.get("CraftTimeSeconds", 0)
        model["CraftingStations"] = [
            get_station_display_name(s, string_map)
            for s in recipe.get("CraftingStations", [])
        ]
        model["CraftMaterials"] = [
            {
                "Name": get_material_display_name(m["Handle"], string_map),
                "Count": m["Count"]
            }
            for m in recipe.get("Materials", [])
        ]
        model["ResultCount"] = recipe.get("ResultItemCount", 1)

        if recipe.get("bHasSandboxUnlockOverride"):
            model["CampaignUnlockType"] = recipe.get("CampaignUnlockType", "")
            model["CampaignUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)
            model["SandboxUnlockType"] = recipe.get("SandboxUnlockType", "")
            model["SandboxUnlockFragments"] = recipe.get("SandboxUnlockFragments", 0)
        else:
            model["CampaignUnlockType"] = recipe.get("CampaignUnlockType", "")
            model["CampaignUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)
            model["SandboxUnlockType"] = recipe.get("CampaignUnlockType", "")
            model["SandboxUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)

    return model


def strip_rich_text(text):
    """Remove in-game rich text markup like <Inventory.Regular.White>...</>"""
    pattern = r'<[^>]+>([^<]*)</>'
    result = re.sub(pattern, r'\1', text)
    return result


def format_float(value):
    """Format a float value for display, removing unnecessary precision."""
    if value == 0:
        return "0"
    if isinstance(value, str):
        if value == "+0":
            return "0"
        return value
    formatted = f"{value:.2f}".rstrip('0').rstrip('.')
    return formatted


def get_unlock_display(unlock_type):
    """Convert unlock type to user-friendly display text."""
    if unlock_type in UNLOCK_TYPE_DISPLAY:
        return UNLOCK_TYPE_DISPLAY[unlock_type]
    return unlock_type


def get_article(word):
    """Return 'a' or 'an' depending on whether word starts with a vowel sound."""
    if not word:
        return "a"
    word_lower = word.lower().strip()
    if word_lower.startswith("one") or word_lower.startswith("uni"):
        return "a"
    first_letter = word_lower[0]
    if first_letter in 'aeiou':
        return "an"
    return "a"


def generate_wiki_template(model):
    """Generate MediaWiki template from the data model."""

    description = strip_rich_text(model["Description"])
    tier = model["Tier"] if model["Tier"] else "1"
    subtype = model["SubType"] if model["SubType"] else "Tool"

    # Get tier as integer for fragment location lookup
    tier_int = 0
    try:
        tier_int = int(tier)
    except (ValueError, TypeError):
        pass

    # Determine unlock text
    campaign_unlock = "???"
    if model["DisplayName"] in CAMPAIGN_UNLOCK_OVERRIDE:
        campaign_unlock = CAMPAIGN_UNLOCK_OVERRIDE[model["DisplayName"]]
    elif model["CampaignUnlockType"] == "CollectFragments":
        campaign_unlock = f"Collect {model['CampaignUnlockFragments']} fragments"
        if tier_int in CAMPAIGN_FRAGMENT_LOCATION:
            campaign_unlock += CAMPAIGN_FRAGMENT_LOCATION[tier_int]
    elif model["CampaignUnlockType"] in ("Unknown", "") and model.get("DLCTitle"):
        campaign_unlock = f"Purchase {model['DLCTitle']}"
    elif model["CampaignUnlockType"]:
        campaign_unlock = get_unlock_display(model["CampaignUnlockType"])

    sandbox_unlock = "???"
    if model["DisplayName"] in SANDBOX_UNLOCK_OVERRIDE:
        sandbox_unlock = SANDBOX_UNLOCK_OVERRIDE[model["DisplayName"]]
    elif model["SandboxUnlockType"] == "CollectFragments":
        sandbox_unlock = f"Collect {model['SandboxUnlockFragments']} fragments"
        if tier_int in SANDBOX_FRAGMENT_LOCATION:
            sandbox_unlock += SANDBOX_FRAGMENT_LOCATION[tier_int]
    elif model["SandboxUnlockType"] in ("Unknown", "") and model.get("DLCTitle"):
        sandbox_unlock = f"Purchase {model['DLCTitle']}"
    elif model["SandboxUnlockType"]:
        sandbox_unlock = get_unlock_display(model["SandboxUnlockType"])

    # Final fallback
    if campaign_unlock == "???":
        campaign_unlock = "{{LI|Return to Moria}}"
    if sandbox_unlock == "???":
        sandbox_unlock = "{{LI|Return to Moria}}"

    # Build stats section
    stats_lines = ["== Stats ==", ""]

    # Durability (-1 means expended on use)
    if model.get('Durability') == -1 or model.get('IsThrowLight'):
        stats_lines.append("Durability: Expended on use")
        stats_lines.append("")
    elif model.get('Durability', 0) > 0:
        stats_lines.append(f"Durability: {model['Durability']}")
        stats_lines.append("")

    # Duration (for throw lights)
    if model.get('DurationSeconds', 0) > 0:
        stats_lines.append(f"Duration: {format_float(model['DurationSeconds'])} seconds")
        stats_lines.append("")

    # Carve Hits (for pickaxes)
    if model.get('CarveHits', 0) > 0:
        stats_lines.append(f"Carve Hits: {model['CarveHits']}")
        stats_lines.append("")

    # Energy Cost (only show if non-zero)
    energy_val = model.get('EnergyCost', 0)
    if energy_val and float(energy_val) != 0:
        stats_lines.append(f"Energy Cost: {format_float(energy_val)}")
        stats_lines.append("")

    # Stamina Cost (only show if non-zero)
    stamina_val = model.get('StaminaCost', 0)
    if stamina_val and float(stamina_val) != 0:
        stats_lines.append(f"Stamina Cost: {format_float(stamina_val)}")
        stats_lines.append("")

    # Max Stack Size (only show if > 1)
    if model.get('MaxStackSize', 1) > 1:
        stats_lines.append(f"Max Stack Size: {model['MaxStackSize']}")
        stats_lines.append("")

    # Max Repair Cost (only show if > 0 and has material)
    if model.get('MaxRepairCost', 0) > 0 and model.get('RepairMaterial'):
        stats_lines.append(f"Max Repair Cost: {model['MaxRepairCost']} {{{{LI|{model['RepairMaterial']}}}}}")
        stats_lines.append("")

    stats_section = "\n".join(stats_lines) + "\n"

    # Build crafting section
    if model.get("HasRecipe"):
        craft_time = model.get("CraftTime", 0)
        craft_time_str = f"{int(craft_time)}" if craft_time else "???"

        stations_lines = ""
        if model.get("CraftingStations"):
            stations_lines = "Station:\n\n"
            for station in model["CraftingStations"]:
                stations_lines += f"* {{{{LI|{station}}}}}\n"

        materials_lines = ""
        if model.get("CraftMaterials"):
            materials_lines = "Materials:\n\n"
            for mat in model["CraftMaterials"]:
                materials_lines += f"* ({mat['Count']}) {{{{LI|{mat['Name']}}}}}\n"

        # Add yield info if > 1
        yield_info = ""
        result_count = model.get("ResultCount", 1)
        if result_count > 1:
            yield_info = f"\nYields: {result_count}\n"

        crafting_section = f"""== Crafting ==

Time: {craft_time_str} seconds

{stations_lines}
{materials_lines}{yield_info}"""
    else:
        crafting_section = ""

    # Build categories
    categories = []
    if tier:
        categories.append(f"[[Category:Tier {tier} Items]]")
    categories.append(f"[[Category:{subtype}s]]")
    categories.append("[[Category:Tools]]")

    categories_str = "\n".join(categories)

    template = f"""{{{{Item
 | title         = {{{{PAGENAME}}}}
 | image         = {{{{PAGENAME}}}}.webp
 | imagecaption  =
 | type          = Tool
 | subtype       = {subtype}
 | tier          = {tier}
}}}}
'''{{{{PAGENAME}}}}''' is {get_article(subtype)} {subtype} [[tool]] in ''[[{{{{topic}}}}]]''.

==Description==

In-game: ''{description}''

== Unlocks ==

* Campaign {{{{spoiler|{campaign_unlock}}}}}
* Sandbox  {{{{spoiler|{sandbox_unlock}}}}}

{stats_section}
{crafting_section}
{{{{Navbox items}}}}
{categories_str}
"""

    return template


def sanitize_filename(name):
    """Remove or replace characters that are invalid in filenames."""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name




def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    print("Loading all string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"Loaded {len(string_map)} total strings")

    print("Loading tools data...")
    tools_list = load_tools_data(TOOLS_FILE)
    print(f"Loaded {len(tools_list)} tool entries")

    print("Loading throw lights data...")
    throwlights_list = load_throwlights_data(THROWLIGHTS_FILE)
    print(f"Loaded {len(throwlights_list)} throw light entries")

    print("Loading recipe data...")
    recipe_map = load_recipe_data(RECIPES_FILE)
    print(f"Loaded {len(recipe_map)} recipes")

    # Process each tool entry
    generated = 0

    for tool_entry in tools_list:
        model = extract_tool_model(tool_entry, string_map, recipe_map)

        # Skip if no display name
        if not model.get("DisplayName"):
            continue

        # Generate wiki template
        template = generate_wiki_template(model)

        # Write to file
        filename = sanitize_filename(model["DisplayName"]) + ".wiki"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"Generated: {filename}")
        generated += 1

    # Process each throw light entry
    for throwlight_entry in throwlights_list:
        model = extract_throwlight_model(throwlight_entry, string_map, recipe_map)

        # Skip if no display name
        if not model.get("DisplayName"):
            continue

        # Generate wiki template
        template = generate_wiki_template(model)

        # Write to file
        filename = sanitize_filename(model["DisplayName"]) + ".wiki"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"Generated: {filename}")
        generated += 1

    print(f"\nDone! Generated {generated} wiki templates in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
