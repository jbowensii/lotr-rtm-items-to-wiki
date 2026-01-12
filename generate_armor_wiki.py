import json
import os
import re

# Paths
SOURCE_DIR = "source"
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")
ARMOR_FILE = os.path.join(SOURCE_DIR, "DT_Armor.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join("output", "armor")

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

# Tinted armor variant suffixes - these unlock when a complete set of original armor is crafted
TINTED_ARMOR_SUFFIXES = ["Amzul", "Masharuz", "Shayar"]
TINTED_ARMOR_UNLOCK_TEXT = "This cosmetic varient unlocks when a complete set of the original armor is crafted"

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

# Mapping for items with "Manual" unlock type - these are purchased from traders
# Maps DisplayName to the unlock text
MANUAL_UNLOCK_MAP = {
    "Innkeeper's Garb": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Shire Trader}}",
    "Keeper's Vest": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Arnor Trader}}",
    "Metalworker's Slouch": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Arnor Trader}}",
    "Mason's Hat": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Blue Mountains Trader}}",
    "Stonemason's Garb": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Blue Mountains Trader}}",
    "Cook's Toque": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Blue Mountains Trader}}",
    "Salvager's Ghillie": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Lothlorien Trader}}",
    "Smith's Apron": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Advanced Miner's Helm": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Red Mountains Trader}}",
    "Merchant's Attire": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gondor Trader}}",
    "Builder's Kettle": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gondor Trader}}",
    "Artisan's Topper": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gondor Trader}}",
    "Blacksmith's Caul": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gundabad Quartermaster}}",
    "Expeditioner's Armor": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gundabad Quartermaster}}",
    "Guard's Helm": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Gundabad Quartermaster}}",
    "Brewmaster's Casque": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Shire Trader}}",
    "Kitchen Apron": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Shire Trader}}",
    "Meat Hat": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Shire Trader}}",
}

# Mapping from CraftingStation keys to Constructions string keys
# This handles inconsistent naming between recipe data and string tables
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


def is_tinted_armor_variant(display_name):
    """Check if the display name is a tinted armor variant (Amzul, Masharuz, or Shayar)."""
    for suffix in TINTED_ARMOR_SUFFIXES:
        if suffix in display_name:
            return True
    return False


def load_string_table(filepath):
    """Load a single string table file and return a key->value dictionary."""
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


def load_all_string_tables(strings_dir):
    """Load all string table files from the strings directory into a single map."""
    combined_map = {}

    # Find all JSON files in the strings directory
    for filename in os.listdir(strings_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(strings_dir, filename)
            print(f"  Loading {filename}...")
            file_map = load_string_table(filepath)
            combined_map.update(file_map)
            print(f"    Found {len(file_map)} strings")

    return combined_map


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
        "Materials": [],  # List of {"Item": key, "Count": n}
        "CampaignUnlockType": "",
        "CampaignUnlockFragments": 0,
        "SandboxUnlockType": "",
        "SandboxUnlockFragments": 0
    }

    for prop in properties:
        prop_name = prop.get("Name", "")
        prop_value = prop.get("Value")

        if prop_name == "ResultItemHandle":
            # Extract RowName from nested structure
            if isinstance(prop_value, list):
                for inner in prop_value:
                    if inner.get("Name") == "RowName":
                        recipe["ResultItemHandle"] = inner.get("Value", "")

        elif prop_name == "ResultItemCount":
            recipe["ResultItemCount"] = prop_value

        elif prop_name == "CraftTimeSeconds":
            recipe["CraftTimeSeconds"] = prop_value

        elif prop_name == "CraftingStations":
            # Extract station RowNames
            stations = []
            if isinstance(prop_value, list):
                for station in prop_value:
                    station_values = station.get("Value", [])
                    for inner in station_values:
                        if inner.get("Name") == "RowName":
                            stations.append(inner.get("Value", ""))
            recipe["CraftingStations"] = stations

        elif prop_name == "DefaultRequiredMaterials":
            # Extract materials with counts
            materials = []
            if isinstance(prop_value, list):
                for mat in prop_value:
                    mat_values = mat.get("Value", [])
                    item_key = ""
                    count = 0
                    for inner in mat_values:
                        if inner.get("Name") == "MaterialHandle":
                            handle_values = inner.get("Value", [])
                            for h in handle_values:
                                if h.get("Name") == "RowName":
                                    item_key = h.get("Value", "")
                        elif inner.get("Name") == "Count":
                            count = inner.get("Value", 0)
                    if item_key:
                        materials.append({"Item": item_key, "Count": count})
            recipe["Materials"] = materials

        elif prop_name == "DefaultUnlocks":
            # Extract campaign unlock info
            if isinstance(prop_value, list):
                for inner in prop_value:
                    if inner.get("Name") == "UnlockType":
                        # Strip enum prefix
                        unlock_type = inner.get("Value", "")
                        if "::" in unlock_type:
                            unlock_type = unlock_type.split("::")[-1]
                        recipe["CampaignUnlockType"] = unlock_type
                    elif inner.get("Name") == "NumFragments":
                        recipe["CampaignUnlockFragments"] = inner.get("Value", 0)

        elif prop_name == "SandboxUnlocks":
            # Extract sandbox unlock info
            if isinstance(prop_value, list):
                for inner in prop_value:
                    if inner.get("Name") == "UnlockType":
                        unlock_type = inner.get("Value", "")
                        if "::" in unlock_type:
                            unlock_type = unlock_type.split("::")[-1]
                        recipe["SandboxUnlockType"] = unlock_type
                    elif inner.get("Name") == "NumFragments":
                        recipe["SandboxUnlockFragments"] = inner.get("Value", 0)

    return recipe


def get_material_display_name(item_key, string_map):
    """Convert item key like 'Item.GunMetalIngot' to display name via string lookup."""
    # Item.GunMetalIngot -> try Items.Items.GunMetalIngot.Name, then Items.GunMetalIngot.Name
    if item_key.startswith("Item."):
        item_name = item_key[5:]  # Remove "Item." prefix
        # Try Items.Items.X.Name first
        string_key = f"Items.Items.{item_name}.Name"
        result = string_map.get(string_key)
        if result:
            return result
        # Fallback: try Items.X.Name
        string_key = f"Items.{item_name}.Name"
        result = string_map.get(string_key)
        if result:
            return result
        # Fallback: try Item.X.Name (original key format, e.g., Item.Wool.Name)
        string_key = f"{item_key}.Name"
        result = string_map.get(string_key)
        if result:
            return result
        return item_name
    # Ore.MoonStone -> Items.Ores.MoonStone.Name
    if item_key.startswith("Ore."):
        ore_name = item_key[4:]  # Remove "Ore." prefix
        string_key = f"Items.Ores.{ore_name}.Name"
        return string_map.get(string_key, ore_name)
    # Consumable.Meat -> Items.Consumables.Meat.Name
    if item_key.startswith("Consumable."):
        consumable_name = item_key[11:]  # Remove "Consumable." prefix
        string_key = f"Items.Consumables.{consumable_name}.Name"
        result = string_map.get(string_key)
        if result:
            return result
        # Fallback: try Consumable.X.Name pattern
        string_key = f"{item_key}.Name"
        return string_map.get(string_key, consumable_name)
    # No prefix - try Items.X.Name pattern (e.g., TrackingDevice -> Items.TrackingDevice.Name)
    string_key = f"Items.{item_key}.Name"
    result = string_map.get(string_key)
    if result:
        return result
    return item_key


def get_repair_material_display_name(item_key, string_map):
    """Convert repair material key like 'Item.Scrap' to display name via Category lookup."""
    # Item.Scrap -> Category.Item.Scrap
    if item_key.startswith("Item."):
        string_key = f"Category.{item_key}"
        return string_map.get(string_key, item_key)
    return item_key


def get_damage_modifier_display_name(modifier_key, string_map):
    """Convert damage modifier key like 'CorrosiveDamage' to display name via Stat lookup."""
    # CorrosiveDamage -> strip "Damage" -> Corrosive -> Stat.DamageResist.Corrosive
    if modifier_key.endswith("Damage"):
        damage_type = modifier_key[:-6]  # Remove "Damage" suffix
        string_key = f"Stat.DamageResist.{damage_type}"
        return string_map.get(string_key, modifier_key)
    return modifier_key


def get_station_display_name(station_key, string_map):
    """Convert crafting station key to display name via string lookup."""
    # Use the mapping to find the string key
    string_key = STATION_KEY_MAP.get(station_key)
    if string_key:
        return string_map.get(string_key, station_key)
    # Fallback: try to derive a readable name
    name = station_key.replace("CraftingStation_", "")
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    return name


def get_property_value(properties, prop_name):
    """Get a property value from a list of property objects."""
    for prop in properties:
        if prop.get("Name") == prop_name:
            return prop.get("Value")
    return None


def extract_armor_model(armor_entry, string_map, recipe_map):
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
        "ActorPath": "",
        "DLC": "",
        "DLCTitle": "",
        "MaxRepairCost": 0,
        "RepairMaterialKey": "",
        "RepairMaterial": "",
        # Recipe data
        "CraftTime": 0.0,
        "CraftingStations": [],
        "Materials": [],  # List of {"Name": display_name, "Count": n}
        "CampaignUnlockType": "",
        "CampaignUnlockFragments": 0,
        "SandboxUnlockType": "",
        "SandboxUnlockFragments": 0,
        "Cosmetic": False
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
            # Extract RowName values from the array and resolve display names
            modifiers = []
            if isinstance(prop_value, list):
                for item in prop_value:
                    inner_values = item.get("Value", [])
                    for inner in inner_values:
                        if inner.get("Name") == "RowName":
                            modifier_key = inner.get("Value", "")
                            display_name = get_damage_modifier_display_name(
                                modifier_key, string_map
                            )
                            modifiers.append(display_name)
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
                                # Extract just the numeric tier, stripping "Tier" prefix
                                tier_raw = parts[2]
                                if tier_raw.startswith("Tier"):
                                    model["Tier"] = tier_raw[4:].strip()
                                else:
                                    model["Tier"] = tier_raw.strip()

        elif prop_name == "Icon":
            # Extract asset path
            if isinstance(prop_value, dict):
                asset_path = prop_value.get("AssetPath", {})
                icon_path = asset_path.get("AssetName", "")
                model["Icon"] = icon_path
                # Fallback: Extract DLC name from Icon path if not already set
                if not model["DLC"] and "/DLC/" in icon_path:
                    parts = icon_path.split("/")
                    try:
                        dlc_index = parts.index("DLC")
                        if dlc_index + 1 < len(parts):
                            model["DLC"] = parts[dlc_index + 1]
                            model["DLCTitle"] = DLC_TITLE_MAP.get(model["DLC"], "")
                    except ValueError:
                        pass

        elif prop_name == "Actor":
            # Extract actor path (used to identify DLC content)
            if isinstance(prop_value, dict):
                asset_path = prop_value.get("AssetPath", {})
                actor_path = asset_path.get("AssetName", "")
                model["ActorPath"] = actor_path
                # Extract DLC name if path contains /DLC/
                # e.g., /Game/DLC/RohanPack/Armor/... -> RohanPack
                if "/DLC/" in actor_path:
                    parts = actor_path.split("/")
                    try:
                        dlc_index = parts.index("DLC")
                        if dlc_index + 1 < len(parts):
                            model["DLC"] = parts[dlc_index + 1]
                            # Look up the DLC title from the map
                            model["DLCTitle"] = DLC_TITLE_MAP.get(model["DLC"], "")
                    except ValueError:
                        pass

        elif prop_name == "InitialRepairCost":
            # Extract Count and MaterialHandle from the nested structure
            if isinstance(prop_value, list):
                for item in prop_value:
                    inner_values = item.get("Value", [])
                    for inner in inner_values:
                        if inner.get("Name") == "Count":
                            model["MaxRepairCost"] = inner.get("Value", 0)
                        elif inner.get("Name") == "MaterialHandle":
                            # Extract RowName from MaterialHandle
                            handle_values = inner.get("Value", [])
                            for h in handle_values:
                                if h.get("Name") == "RowName":
                                    material_key = h.get("Value", "")
                                    model["RepairMaterialKey"] = material_key
                                    model["RepairMaterial"] = get_repair_material_display_name(
                                        material_key, string_map
                                    )

    # Look up recipe data using "Armor.{GameName}" as the key
    recipe_key = f"Armor.{game_name}"
    recipe = recipe_map.get(recipe_key)
    if recipe:
        model["CraftTime"] = recipe.get("CraftTimeSeconds", 0.0)
        model["CampaignUnlockType"] = recipe.get("CampaignUnlockType", "")
        model["CampaignUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)
        model["SandboxUnlockType"] = recipe.get("SandboxUnlockType", "")
        model["SandboxUnlockFragments"] = recipe.get("SandboxUnlockFragments", 0)

        # If SandboxUnlockType is Unknown but CampaignUnlockType is known, copy from Campaign
        if model["SandboxUnlockType"] == "Unknown" and model["CampaignUnlockType"] != "Unknown":
            model["SandboxUnlockType"] = model["CampaignUnlockType"]
            model["SandboxUnlockFragments"] = model["CampaignUnlockFragments"]

        # Convert crafting station keys to display names
        stations = []
        for station_key in recipe.get("CraftingStations", []):
            display_name = get_station_display_name(station_key, string_map)
            stations.append(display_name)
        model["CraftingStations"] = stations

        # Convert material keys to display names
        materials = []
        for mat in recipe.get("Materials", []):
            display_name = get_material_display_name(mat["Item"], string_map)
            materials.append({"Name": display_name, "Count": mat["Count"]})
        model["Materials"] = materials
    else:
        # No recipe found - this is a cosmetic item
        model["Cosmetic"] = True

    return model


def strip_rich_text(text):
    """Remove in-game rich text markup like <Inventory.Regular.White>...</>"""
    # Pattern matches <SomeTag>content</> and replaces with just content
    pattern = r'<[^>]+>([^<]*)</>'
    result = re.sub(pattern, r'\1', text)
    return result


def generate_wiki_template(model):
    """Generate MediaWiki template from the data model."""

    # Clean up description
    description = strip_rich_text(model["Description"])

    # Tier is already just the number (e.g., "3" not "Tier3")
    tier = model["Tier"]

    # Build damage modifiers line if present
    damage_modifiers_line = ""
    if model["DamageModifiers"]:
        damage_modifiers_line = f"\nDamage Modifiers: {model['DamageModifiers']}\n"

    # Get tier as integer for fragment location lookup
    tier_int = 0
    try:
        tier_int = int(tier)
    except (ValueError, TypeError):
        pass

    # Build unlock lines
    campaign_unlock = "???"
    if model["CampaignUnlockType"] == "CollectFragments":
        campaign_unlock = f"Collect {model['CampaignUnlockFragments']} fragments"
        # Append tier-based location hint
        if tier_int in CAMPAIGN_FRAGMENT_LOCATION:
            campaign_unlock += CAMPAIGN_FRAGMENT_LOCATION[tier_int]
    elif model["CampaignUnlockType"] == "Manual" and model["DisplayName"] in MANUAL_UNLOCK_MAP:
        # Manual unlock items are purchased from traders
        campaign_unlock = MANUAL_UNLOCK_MAP[model["DisplayName"]]
    elif model["CampaignUnlockType"] == "Manual" and is_tinted_armor_variant(model["DisplayName"]):
        # Tinted armor variants unlock when a complete set of original armor is crafted
        campaign_unlock = TINTED_ARMOR_UNLOCK_TEXT
    elif model["CampaignUnlockType"] == "Manual" and model["SandboxUnlockType"] != "Manual":
        # Manual in one mode but not the other means unavailable in this mode
        campaign_unlock = "Unavailable"
    elif model["CampaignUnlockType"] in ("Unknown", "") and model["DLCTitle"]:
        # DLC items with Unknown or empty unlock type require purchasing the DLC
        campaign_unlock = f"Purchase {model['DLCTitle']}"
    elif model["CampaignUnlockType"]:
        campaign_unlock = model["CampaignUnlockType"]

    sandbox_unlock = "???"
    if model["SandboxUnlockType"] == "CollectFragments":
        sandbox_unlock = f"Collect {model['SandboxUnlockFragments']} fragments"
        # Append tier-based location hint
        if tier_int in SANDBOX_FRAGMENT_LOCATION:
            sandbox_unlock += SANDBOX_FRAGMENT_LOCATION[tier_int]
    elif model["SandboxUnlockType"] == "Manual" and model["DisplayName"] in MANUAL_UNLOCK_MAP:
        # Manual unlock items are purchased from traders
        sandbox_unlock = MANUAL_UNLOCK_MAP[model["DisplayName"]]
    elif model["SandboxUnlockType"] == "Manual" and is_tinted_armor_variant(model["DisplayName"]):
        # Tinted armor variants unlock when a complete set of original armor is crafted
        sandbox_unlock = TINTED_ARMOR_UNLOCK_TEXT
    elif model["SandboxUnlockType"] == "Manual" and model["CampaignUnlockType"] != "Manual":
        # Manual in one mode but not the other means unavailable in this mode
        sandbox_unlock = "Unavailable"
    elif model["SandboxUnlockType"] in ("Unknown", "") and model["DLCTitle"]:
        # DLC items with Unknown or empty unlock type require purchasing the DLC
        sandbox_unlock = f"Purchase {model['DLCTitle']}"
    elif model["SandboxUnlockType"]:
        sandbox_unlock = model["SandboxUnlockType"]

    # Build stats and crafting/cosmetic sections based on Cosmetic flag
    if model["Cosmetic"]:
        # Cosmetic items don't have stats or crafting info
        stats_section = ""
        crafting_or_cosmetic_section = """== Cosmetic ==

This is a cosmetic piece of armor and does not effect the stats of the armor you are wearing only the look.
"""
    else:
        # Build stats section
        stats_section = f"""== Stats ==

Durability: {model['Durability']}

Armor Protection: {model['DamageProtection']}

Armor Effectiveness: {model['DamageReduction']}
{damage_modifiers_line}
Max Repair Cost: {model['MaxRepairCost']} {{{{LI|{model['RepairMaterial']}}}}}

"""
        # Build craft time
        craft_time = model.get("CraftTime", 0)
        craft_time_str = f"{int(craft_time)}" if craft_time else "???"

        # Build stations list (already resolved to display names)
        stations_lines = ""
        if model["CraftingStations"]:
            for station_name in model["CraftingStations"]:
                stations_lines += f"* {{{{LI|{station_name}}}}}\n"
        else:
            stations_lines = "* {{LI|???}}\n"

        # Build materials list
        materials_lines = ""
        if model["Materials"]:
            for mat in model["Materials"]:
                materials_lines += f"* ({mat['Count']}) {{{{LI|{mat['Name']}}}}}\n"
        else:
            materials_lines = "* {{LI|???}}\n"

        crafting_or_cosmetic_section = f"""== Crafting ==

Time: {craft_time_str} seconds

Station:

{stations_lines}
Materials:

{materials_lines}"""

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

* Campaign {{{{spoiler|{campaign_unlock}}}}}
* Sandbox  {{{{spoiler|{sandbox_unlock}}}}}

{stats_section}{crafting_or_cosmetic_section}
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
    print("Loading all string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"Loaded {len(string_map)} total strings")

    print("Loading armor data...")
    armor_list = load_armor_data(ARMOR_FILE)
    print(f"Loaded {len(armor_list)} armor entries")

    print("Loading recipe data...")
    recipe_map = load_recipe_data(RECIPES_FILE)
    print(f"Loaded {len(recipe_map)} recipes")

    # Process each armor entry
    count = 0
    excluded = []

    for armor_entry in armor_list:
        model = extract_armor_model(armor_entry, string_map, recipe_map)

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
