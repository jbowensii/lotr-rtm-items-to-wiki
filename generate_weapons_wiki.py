import json
import os
import re

# Paths
SOURCE_DIR = "source"
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")
WEAPONS_FILE = os.path.join(SOURCE_DIR, "DT_Weapons.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "DT_ItemRecipes.json")
OUTPUT_DIR = os.path.join("output", "weapons")

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

# Load unlock overrides from JSON file and merge with defaults
def load_unlock_overrides():
    """Load unlock overrides from weapon_unlock_overrides.json and merge with defaults"""
    # Default overrides
    campaign_defaults = {
    "Arrows": "Build a {{LI|Workbench}}",
    "Barôkamlut": "Unavailable",
    "Belegost Halberd": "Repair the {{LI|Great Belegost Forge}}",
    "Dimrill Spear": "Build the {{LI|Khuzdul Forge}}",
    "Drakhbarzin": "Purchase the {{LI|Durin's Folk}} Expansion, then Purchased from the {{LI|Lothloorien Trader}}",
    "Elven Arrows": "Collect 2 fragments, Repair [[Damaged Statues]] in the [[Elven Quarter]]",
    "Ent-craft Shield": "Purchase the [[Ent-craft Pack]] DLC",
    "Eregion Spear": "Repair the {{LI|Great Forge of Narvi}}",
    "First Age Bolts": "Craft a {{LI|First Age Crossbow}}",
    "First Age Crossbow": "Collect 3 fragments, Repair [[Damaged Statues]] in the [[Lower Deeps]]",
    "First Age Greatsword": "Collect 2 fragments, Repair [[Damaged Statues]] in the [[Lower Deeps]]",
    "First Age Sword": "Build a {{LI|Gem Cutter}}",
    "Frightener's Battleaxe": "Purchase the {{LI|Orc Hunter Pack}} DLC",
    "Gimli's Fourth Age Axe": "Purchase the {{LI|Durin's Folk}} Expansion, then complete the storyline.",
    "Improvised Axe": "Obtain {{LI|Wood Scraps}}, {{LI|Cloth Scraps}}, and {{LI|Metal Fragments}}",
    "Iron Hills Shield": "Repair an abandoned {{LI|Forge}}",
    "Iron Sword": "Repair an abandoned {{LI|Forge}}",
    "Iron War Axe": "Collect 2 fragments, Repair [[Damaged Statues]] in [[Westgate]]",
    "Ironbough Greatsword": "Obtain the {{LI|Ent-craft Pack}} DLC",
    "Khazâd Arrows": "Obtain {{LI|Ironwood}}",
    "Khazâd Bolts": "Obtain {{LI|Ironwood}}",
    "Khazâd Maul": "Collect 3 fragments, Repair [[Damaged Statues]] in the [[Eastern Bastion]] and [[Upper City]]",
    "Khazâd War Axe": "Collect 3 fragments, Repair [[Damaged Statues]] in the [[Eastern Bastion]] and [[Upper City]]",
    "Khazâd War Mattock": "Collect 3 fragments, Repair [[Damaged Statues]] in the [[Eastern Bastion]] and [[Upper City]]",
    "Khushnabrak": "Speak with {{LI|Aric}} after the end-game credits.",
    "Lafarnîzîn": "Speak with {{LI|Aric}} after the end-game credits.",
    "Mithril Shield": "Speak with {{LI|Aric}} after the end-game credits.",
    "Muasgadnûr": "Speak with {{LI|Aric}} after the end-game credits.",
    "Nogrod Bolts": "Obtain a {{LI|Nogrod Steel Ingot}}",
    "Oakenshield": "Obtain {{LI|Ironwood}}",
    "Red Axe of Nogrod": "Repair the {{LI|Great Nogrod Forge}}",
    "Red Sword of Nogrod": "Repair the {{LI|Great Nogrod Forge}}",
    "Rohirrim Shield": "Purchase the {{LI|Rohan Pack}} DLC",
    "Rohirrim Spear": "Purchase the {{LI|Rohan Pack}} DLC",
    "Rukhnaman": "Speak with {{LI|Aric}} after the end-game credits.",
    "Sagrûrisâbun": "Speak with {{LI|Aric}} after the end-game credits.",
    "Shaz'akhnaman": "Repair the {{LI|Great Mithril Forge}}",
    "Shieldwall": "Repair the {{LI|Great Forge of Narvi}}",
    "Steel Battleaxe": "Collect 3 fragments, Repair [[Damaged Statues]] in the [[Mines of Moria]]",
    "Steel Sword": "Collect 2 fragments, Repair [[Damaged Statues]] in the [[Mines of Moria]]",
    "Thanazbad": "Speak with {{LI|Aric}} after the end-game credits.",
    }

    sandbox_defaults = {
    "Arrows": "Build a {{LI|Workbench}}",
    "Barôkamlut": "Repair the {{LI|Great Mithril Forge}}",
    "Belegost Halberd": "Repair the {{LI|Great Belegost Forge}}",
    "Dimrill Spear": "Build the {{LI|Khuzdul Forge}}",
    "Drakhbarzin": "Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|Lothloorien Trader}}",
    "Elven Arrows": "Repair the {{LI|Great Forge of Narvi}}",
    "Ent-craft Shield": "Purchase the [[Ent-craft Pack]] DLC",
    "Eregion Spear": "Repair the {{LI|Great Forge of Narvi}}",
    "First Age Bolts": "Craft a {{LI|First Age Crossbow}}",
    "First Age Crossbow": "Build a {{LI|Gem Cutter}}",
    "First Age Greatsword": "Build a {{LI|Gem Cutter}}",
    "First Age Sword": "Build a {{LI|Gem Cutter}}",
    "Frightener's Battleaxe": "Purchase the {{LI|Orc Hunter Pack}} DLC",
    "Gimli's Fourth Age Axe": "Purchase the {{LI|Durin's Folk}} Expansion, then complete the storyline.",
    "Improvised Axe": "Obtain {{LI|Wood Scraps}}, {{LI|Cloth Scraps}}, and {{LI|Metal Fragments}}",
    "Iron Hills Shield": "Collect 3 fragments, Repair [[Damaged Statues]] in the [[Gate]] or [[Elven]] areas",
    "Iron Sword": "Build a {{LI|Forge}}",
    "Iron War Axe": "Build a {{LI|Forge}}",
    "Ironbough Greatsword": "Obtain the {{LI|Ent-craft Pack}} DLC",
    "Khazâd Arrows": "Build a {{LI|Khuzdul Forge}}",
    "Khazâd Bolts": "Build a {{LI|Khuzdul Forge}}",
    "Khazâd Maul": "Build a {{LI|Khuzdul Forge}}",
    "Khazâd War Axe": "Build a {{LI|Khuzdul Forge}}",
    "Khazâd War Mattock": "Build a {{LI|Khuzdul Forge}}",
    "Khushnabrak": "Repair the {{LI|Great Mithril Forge}}",
    "Lafarnîzîn": "Repair the {{LI|Great Mithril Forge}}",
    "Last Alliance Maul": "Repair the {{LI|Great Forge of Narvi}}",
    "Mithril Shield": "Repair the {{LI|Great Mithril Forge}}",
    "Muasgadnûr": "Repair the {{LI|Great Mithril Forge}}",
    "Nogrod Bolts": "Obtain a {{LI|Nogrod Steel Ingot}}",
    "Oakenshield": "Obtain {{LI|Wood Scraps}}",
    "Red Axe of Nogrod": "Repair the {{LI|Great Nogrod Forge}}",
    "Red Sword of Nogrod": "Repair the {{LI|Great Nogrod Forge}}",
    "Rohirrim Shield": "Purchase the {{LI|Rohan Pack}} DLC",
    "Rohirrim Spear": "Purchase the {{LI|Rohan Pack}} DLC",
    "Rukhnaman": "Repair the {{LI|Great Mithril Forge}}",
    "Sagrûrisâbun": "Repair the {{LI|Great Mithril Forge}}",
    "Shaz'akhnaman": "Repair the {{LI|Great Mithril Forge}}",
    "Shieldwall": "Repair the {{LI|Great Forge of Narvi}}",
    "Steel Battleaxe": "Build a {{LI|Bellows}}",
    "Steel Sword": "Build a {{LI|Bellows}}",
    "Thanazbad": "Repair the {{LI|Great Mithril Forge}}",
    }

    # Load overrides from JSON file
    override_file = "weapon_unlock_overrides.json"
    if os.path.exists(override_file):
        with open(override_file, 'r', encoding='utf-8') as f:
            overrides = json.load(f)
            for item_name, unlock_data in overrides.items():
                if "campaign" in unlock_data:
                    campaign_defaults[item_name] = unlock_data["campaign"]
                if "sandbox" in unlock_data:
                    sandbox_defaults[item_name] = unlock_data["sandbox"]

    return campaign_defaults, sandbox_defaults

# Load overrides at module level
CAMPAIGN_UNLOCK_OVERRIDE, SANDBOX_UNLOCK_OVERRIDE = load_unlock_overrides()

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

# Damage type tag to display name mapping
# These tags can have hand type suffix like .1h or .2h
DAMAGE_TYPE_MAP = {
    # Piercing
    "Damage.Piercing.Spear": "Piercing (Spear)",
    "Damage.Piercing.Spear.1h": "Piercing (Spear)",
    "Damage.Piercing.Arrow": "Piercing (Arrow)",
    "Damage.Piercing.Bolt": "Piercing (Bolt)",
    # Slashing
    "Damage.Slashing.Sword": "Slashing (Sword)",
    "Damage.Slashing.Sword.1h": "Slashing (Sword)",
    "Damage.Slashing.Sword.2h": "Slashing (Greatsword)",
    "Damage.Slashing.Axe": "Slashing (Axe)",
    "Damage.Slashing.Axe.1h": "Slashing (War Axe)",
    "Damage.Slashing.Axe.2h": "Slashing (Battleaxe)",
    "Damage.Slashing.Halberd": "Slashing (Halberd)",
    # Bludgeoning
    "Damage.Bludgeoning.Hammer": "Bludgeoning (Hammer)",
    "Damage.Bludgeoning.Hammer.2h": "Bludgeoning (War Mattock)",
    "Damage.Bludgeoning.Mattock": "Bludgeoning (Mattock)",
    "Damage.Bludgeoning.Mattock.1h": "Bludgeoning (Maul)",
    "Damage.Bludgeoning.Club": "Bludgeoning (Club)",
    "Damage.Bludgeoning.Club.1h": "Bludgeoning (Club)",
    "Damage.Bludgeoning.Club.2h": "Bludgeoning (Greatclub)",
    "Damage.Bludgeoning.Shield": "Bludgeoning (Shield)",
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
    """Load all string table files from the strings directory into a single map."""
    combined_map = {}

    for filename in os.listdir(strings_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(strings_dir, filename)
            print(f"  Loading {filename}...")
            file_map = load_string_table(filepath)
            combined_map.update(file_map)
            print(f"    Found {len(file_map)} strings")

    return combined_map


def load_weapons_data(filepath):
    """Load DT_Weapons.json and return the list of weapon entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    weapons_list = []
    exports = data.get("Exports", [])
    for export in exports:
        if export.get("$type") == "UAssetAPI.ExportTypes.DataTableExport, UAssetAPI":
            table = export.get("Table", {})
            weapon_entries = table.get("Data", [])
            weapons_list.extend(weapon_entries)

    return weapons_list


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
        "HasSandboxUnlockOverride": False
    }

    for prop in properties:
        prop_name = prop.get("Name", "")
        prop_value = prop.get("Value")

        if prop_name == "ResultItemHandle":
            if isinstance(prop_value, list):
                for inner in prop_value:
                    if inner.get("Name") == "RowName":
                        recipe["ResultItemHandle"] = inner.get("Value", "")

        elif prop_name == "ResultItemCount":
            recipe["ResultItemCount"] = prop_value

        elif prop_name == "CraftTimeSeconds":
            recipe["CraftTimeSeconds"] = prop_value

        elif prop_name == "CraftingStations":
            stations = []
            if isinstance(prop_value, list):
                for station in prop_value:
                    station_values = station.get("Value", [])
                    for inner in station_values:
                        if inner.get("Name") == "RowName":
                            stations.append(inner.get("Value", ""))
            recipe["CraftingStations"] = stations

        elif prop_name == "DefaultRequiredMaterials":
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
            if isinstance(prop_value, list):
                for inner in prop_value:
                    if inner.get("Name") == "UnlockType":
                        unlock_type = inner.get("Value", "")
                        if "::" in unlock_type:
                            unlock_type = unlock_type.split("::")[-1]
                        recipe["CampaignUnlockType"] = unlock_type
                    elif inner.get("Name") == "NumFragments":
                        recipe["CampaignUnlockFragments"] = inner.get("Value", 0)

        elif prop_name == "bHasSandboxUnlockOverride":
            recipe["HasSandboxUnlockOverride"] = prop_value

        elif prop_name == "SandboxUnlocks":
            if isinstance(prop_value, list):
                for inner in prop_value:
                    if inner.get("Name") == "UnlockType":
                        unlock_type = inner.get("Value", "")
                        if "::" in unlock_type:
                            unlock_type = unlock_type.split("::")[-1]
                        recipe["SandboxUnlockType"] = unlock_type
                    elif inner.get("Name") == "NumFragments":
                        recipe["SandboxUnlockFragments"] = inner.get("Value", 0)

    # If no sandbox override, use campaign unlock for sandbox
    if not recipe["HasSandboxUnlockOverride"] and recipe["CampaignUnlockType"]:
        recipe["SandboxUnlockType"] = recipe["CampaignUnlockType"]
        recipe["SandboxUnlockFragments"] = recipe["CampaignUnlockFragments"]

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


def get_material_display_name(item_key, string_map):
    """Convert item key like 'Item.GunMetalIngot' to display name via string lookup."""
    # Check special mapping first
    if item_key in MATERIAL_KEY_MAP:
        base_key = MATERIAL_KEY_MAP[item_key]
    elif "." in item_key:
        base_key = item_key.split(".")[-1]
    else:
        base_key = item_key

    # Use flexible string table lookup
    result = find_string_by_suffix(base_key, string_map, ".Name")
    if result:
        return result

    # Fallback: clean up the key
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', base_key)
    return name


def get_repair_material_display_name(item_key, string_map):
    """Convert repair material key like 'Item.Scrap' to display name."""
    # Use the same logic as get_material_display_name
    return get_material_display_name(item_key, string_map)


def get_station_display_name(station_key, string_map):
    """Convert crafting station key to display name via string lookup."""
    string_key = STATION_KEY_MAP.get(station_key)
    if string_key:
        return string_map.get(string_key, station_key)
    name = station_key.replace("CraftingStation_", "")
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    return name


def get_damage_type_display(damage_type_tag):
    """Convert damage type tag to display name."""
    if damage_type_tag in DAMAGE_TYPE_MAP:
        return DAMAGE_TYPE_MAP[damage_type_tag]
    # Fallback: extract from tag like "Damage.Piercing.Spear" -> "Piercing"
    parts = damage_type_tag.split(".")
    if len(parts) >= 2:
        return parts[1]
    return damage_type_tag


def extract_weapon_model(weapon_entry, string_map, recipe_map):
    """Extract our data model from a weapon entry."""
    game_name = weapon_entry.get("Name", "")
    properties = weapon_entry.get("Value", [])

    model = {
        "GameName": game_name,
        "DisplayNameKey": "",
        "DisplayName": "",
        "DescriptionKey": "",
        "Description": "",
        "DamageType": "",
        "DamageTypeDisplay": "",
        "Durability": 0,
        "Tier": "",
        "Damage": 0,
        "Speed": 1.0,
        "ArmorPenetration": 0.0,
        "StaminaCost": 0.0,
        "EnergyCost": 0.0,
        "BlockDamageReduction": 0.0,
        "Type": "Weapon",
        "SubType": "",  # e.g., Spear, Sword, Axe
        "HandType": "",  # e.g., 1h, 2h
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
        "Materials": [],
        "CampaignUnlockType": "",
        "CampaignUnlockFragments": 0,
        "SandboxUnlockType": "",
        "SandboxUnlockFragments": 0,
        "HasRecipe": False,
        "EnabledState": "Enabled"
    }

    for prop in properties:
        prop_name = prop.get("Name", "")
        prop_value = prop.get("Value")

        if prop_name == "DamageType":
            # Extract from GameplayTag structure
            if isinstance(prop_value, list):
                for inner in prop_value:
                    if inner.get("Name") == "TagName":
                        damage_tag = inner.get("Value", "")
                        model["DamageType"] = damage_tag
                        model["DamageTypeDisplay"] = get_damage_type_display(damage_tag)

        elif prop_name == "Durability":
            model["Durability"] = prop_value

        elif prop_name == "Tier":
            model["Tier"] = str(prop_value)

        elif prop_name == "Damage":
            model["Damage"] = prop_value

        elif prop_name == "Speed":
            model["Speed"] = prop_value

        elif prop_name == "ArmorPenetration":
            model["ArmorPenetration"] = prop_value

        elif prop_name == "StaminaCost":
            model["StaminaCost"] = prop_value

        elif prop_name == "EnergyCost":
            model["EnergyCost"] = prop_value

        elif prop_name == "BlockDamageReduction":
            model["BlockDamageReduction"] = prop_value

        elif prop_name == "DisplayName":
            model["DisplayNameKey"] = prop_value
            model["DisplayName"] = string_map.get(prop_value, prop_value)

        elif prop_name == "Description":
            model["DescriptionKey"] = prop_value
            model["Description"] = string_map.get(prop_value, prop_value)

        elif prop_name == "Tags":
            # Parse tags: UI.Weapon.1h, Item.Weapon.Spear
            if isinstance(prop_value, list):
                for item in prop_value:
                    if item.get("Name") == "Tags":
                        tags = item.get("Value", [])
                        for tag in tags:
                            parts = tag.split(".")
                            if parts[0] == "UI" and len(parts) >= 3:
                                # UI.Weapon.1h or UI.Weapon.2h
                                model["HandType"] = parts[2]
                            elif parts[0] == "Item" and len(parts) >= 3:
                                # Item.Weapon.Spear -> SubType = Spear
                                model["SubType"] = parts[2]

        elif prop_name == "Icon":
            if isinstance(prop_value, dict):
                asset_path = prop_value.get("AssetPath", {})
                icon_path = asset_path.get("AssetName", "")
                model["Icon"] = icon_path
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
            if isinstance(prop_value, dict):
                asset_path = prop_value.get("AssetPath", {})
                actor_path = asset_path.get("AssetName", "")
                model["ActorPath"] = actor_path
                if "/DLC/" in actor_path:
                    parts = actor_path.split("/")
                    try:
                        dlc_index = parts.index("DLC")
                        if dlc_index + 1 < len(parts):
                            model["DLC"] = parts[dlc_index + 1]
                            model["DLCTitle"] = DLC_TITLE_MAP.get(model["DLC"], "")
                    except ValueError:
                        pass

        elif prop_name == "InitialRepairCost":
            if isinstance(prop_value, list):
                for item in prop_value:
                    inner_values = item.get("Value", [])
                    for inner in inner_values:
                        if inner.get("Name") == "Count":
                            model["MaxRepairCost"] = inner.get("Value", 0)
                        elif inner.get("Name") == "MaterialHandle":
                            handle_values = inner.get("Value", [])
                            for h in handle_values:
                                if h.get("Name") == "RowName":
                                    material_key = h.get("Value", "")
                                    model["RepairMaterialKey"] = material_key
                                    model["RepairMaterial"] = get_repair_material_display_name(
                                        material_key, string_map
                                    )

        elif prop_name == "EnabledState":
            # Extract enabled state (Enabled/Disabled)
            if isinstance(prop_value, str) and "::" in prop_value:
                model["EnabledState"] = prop_value.split("::")[-1]
            else:
                model["EnabledState"] = str(prop_value) if prop_value else "Enabled"

    # Look up recipe data using "Weapon.{GameName}" as the key
    recipe_key = f"Weapon.{game_name}"
    recipe = recipe_map.get(recipe_key)
    if recipe:
        model["HasRecipe"] = True
        model["CraftTime"] = recipe.get("CraftTimeSeconds", 0.0)
        model["CampaignUnlockType"] = recipe.get("CampaignUnlockType", "")
        model["CampaignUnlockFragments"] = recipe.get("CampaignUnlockFragments", 0)
        model["SandboxUnlockType"] = recipe.get("SandboxUnlockType", "")
        model["SandboxUnlockFragments"] = recipe.get("SandboxUnlockFragments", 0)

        # If SandboxUnlockType is Unknown but CampaignUnlockType is known, copy from Campaign
        if model["SandboxUnlockType"] == "Unknown" and model["CampaignUnlockType"] != "Unknown":
            model["SandboxUnlockType"] = model["CampaignUnlockType"]
            model["SandboxUnlockFragments"] = model["CampaignUnlockFragments"]

        stations = []
        for station_key in recipe.get("CraftingStations", []):
            display_name = get_station_display_name(station_key, string_map)
            stations.append(display_name)
        model["CraftingStations"] = stations

        materials = []
        for mat in recipe.get("Materials", []):
            display_name = get_material_display_name(mat["Item"], string_map)
            materials.append({"Name": display_name, "Count": mat["Count"]})
        model["Materials"] = materials

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
    # Handle "+0" style strings
    if isinstance(value, str):
        if value == "+0":
            return "0"
        return value
    # Round to 2 decimal places and strip trailing zeros
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
    # Special cases that start with vowel letters but consonant sounds
    if word_lower.startswith("one") or word_lower.startswith("uni"):
        return "a"
    # Check first letter for vowel
    first_letter = word_lower[0]
    if first_letter in 'aeiou':
        return "an"
    return "a"


def generate_wiki_template(model):
    """Generate MediaWiki template from the data model."""

    description = strip_rich_text(model["Description"])
    tier = model["Tier"]

    # Get tier as integer for fragment location lookup
    tier_int = 0
    try:
        tier_int = int(tier)
    except (ValueError, TypeError):
        pass

    # Build unlock lines
    campaign_unlock = "???"
    if model["DisplayName"] in CAMPAIGN_UNLOCK_OVERRIDE:
        campaign_unlock = CAMPAIGN_UNLOCK_OVERRIDE[model["DisplayName"]]
    elif model["CampaignUnlockType"] == "CollectFragments":
        campaign_unlock = f"Collect {model['CampaignUnlockFragments']} fragments"
        if tier_int in CAMPAIGN_FRAGMENT_LOCATION:
            campaign_unlock += CAMPAIGN_FRAGMENT_LOCATION[tier_int]
    elif model["CampaignUnlockType"] in ("Unknown", "") and model["DLCTitle"]:
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
    elif model["SandboxUnlockType"] in ("Unknown", "") and model["DLCTitle"]:
        sandbox_unlock = f"Purchase {model['DLCTitle']}"
    elif model["SandboxUnlockType"]:
        sandbox_unlock = get_unlock_display(model["SandboxUnlockType"])

    # Final fallback
    if campaign_unlock == "???":
        campaign_unlock = "{{LI|Return to Moria}}"
    if sandbox_unlock == "???":
        sandbox_unlock = "{{LI|Return to Moria}}"

    # Determine weapon subtype for display
    subtype = model["SubType"] if model["SubType"] else "Weapon"
    hand_type = model["HandType"]
    if hand_type == "1h":
        hand_display = "One-Handed "
    elif hand_type == "2h":
        hand_display = "Two-Handed "
    else:
        hand_display = ""

    # Build stats section with formatted float values, omitting zero values
    stats_lines = ["== Stats ==", ""]

    # Durability (-1 means expended on use, 0 is not meaningful)
    if model['Durability'] == -1:
        stats_lines.append("Durability: Expended on use")
        stats_lines.append("")
    elif model['Durability'] > 0:
        stats_lines.append(f"Durability: {model['Durability']}")
        stats_lines.append("")

    # Damage (always show if > 0)
    if model['Damage'] > 0:
        stats_lines.append(f"Damage: {model['Damage']}")
        stats_lines.append("")

    # Damage Type (always show if present)
    if model['DamageTypeDisplay']:
        stats_lines.append(f"Damage Type: {model['DamageTypeDisplay']}")
        stats_lines.append("")

    # Speed (show if not 0)
    speed_val = model['Speed']
    if speed_val and speed_val != 0:
        stats_lines.append(f"Speed: {format_float(speed_val)}")
        stats_lines.append("")

    # Armor Penetration (only show if non-zero)
    ap_val = model['ArmorPenetration']
    if ap_val and ap_val != 0 and str(ap_val) != "+0":
        stats_lines.append(f"Armor Penetration: {format_float(ap_val)}")
        stats_lines.append("")

    # Stamina Cost (only show if non-zero)
    stamina_val = model['StaminaCost']
    if stamina_val and stamina_val != 0 and str(stamina_val) != "+0":
        stats_lines.append(f"Stamina Cost: {format_float(stamina_val)}")
        stats_lines.append("")

    # Energy Cost (only show if non-zero)
    energy_val = model['EnergyCost']
    if energy_val is not None and float(energy_val) != 0:
        stats_lines.append(f"Energy Cost: {format_float(energy_val)}")
        stats_lines.append("")

    # Block Damage Reduction (only show if non-zero)
    block_val = model['BlockDamageReduction']
    if block_val and block_val != 0 and str(block_val) != "+0":
        stats_lines.append(f"Block Damage Reduction: {format_float(block_val)}")
        stats_lines.append("")

    # Max Repair Cost (only show if > 0 and has material)
    if model['MaxRepairCost'] > 0 and model['RepairMaterial']:
        stats_lines.append(f"Max Repair Cost: {model['MaxRepairCost']} {{{{LI|{model['RepairMaterial']}}}}}")
        stats_lines.append("")

    stats_section = "\n".join(stats_lines) + "\n"

    # Build crafting section
    if model["HasRecipe"]:
        craft_time = model.get("CraftTime", 0)
        craft_time_str = f"{int(craft_time)}" if craft_time else "???"

        stations_lines = ""
        if model["CraftingStations"]:
            for station_name in model["CraftingStations"]:
                stations_lines += f"* {{{{LI|{station_name}}}}}\n"
        else:
            stations_lines = "* {{LI|???}}\n"

        materials_lines = ""
        if model["Materials"]:
            for mat in model["Materials"]:
                materials_lines += f"* ({mat['Count']}) {{{{LI|{mat['Name']}}}}}\n"
        else:
            materials_lines = "* {{LI|???}}\n"

        crafting_section = f"""== Crafting ==

Time: {craft_time_str} seconds

Station:

{stations_lines}
Materials:

{materials_lines}"""
    else:
        crafting_section = """== Acquisition ==

This weapon cannot be crafted and must be obtained through other means.
"""

    template = f"""{{{{Item
 | title         = {{{{PAGENAME}}}}
 | image         = {{{{PAGENAME}}}}.webp
 | imagecaption  =
 | type          = Weapon
 | subtype       = {subtype}
 | tier          = {tier}
}}}}
'''{{{{PAGENAME}}}}''' is {get_article(hand_display if hand_display else subtype)} {hand_display}{subtype} [[weapon]] in ''[[{{{{topic}}}}]]''.

==Description==

In-game: ''{description}''

== Unlock ==
'''Campaign:''' {campaign_unlock}
'''Sandbox:''' {sandbox_unlock}

{stats_section}{crafting_section}
{{{{Navbox items}}}}
[[Category:Tier {tier} Items]]
[[Category:{subtype}s]]
[[Category:Weapons]]
"""

    return template


def sanitize_filename(name):
    """Sanitize a string to be used as a filename."""
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

    # DEV items are internal/test items
    if display_name.startswith("DEV - "):
        return True, "DEV item"

    # TEST items are internal/test items
    if display_name.startswith("TEST"):
        return True, "TEST item"

    # Unresolved string table references (display name still shows key)
    if display_name.startswith("Weapons."):
        return True, "Unresolved string table reference"

    # Broken weapons (these are repair states, not separate items)
    if "Broken" in model.get("GameName", ""):
        return True, "Broken weapon variant"

    # Disabled items
    if model.get("EnabledState") == "Disabled":
        return True, "Disabled item"

    return False, ""


def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    print("Loading all string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"Loaded {len(string_map)} total strings")

    print("Loading weapons data...")
    weapons_list = load_weapons_data(WEAPONS_FILE)
    print(f"Loaded {len(weapons_list)} weapon entries")

    print("Loading recipe data...")
    recipe_map = load_recipe_data(RECIPES_FILE)
    print(f"Loaded {len(recipe_map)} recipes")

    # Process each weapon entry
    count = 0
    excluded = []

    for weapon_entry in weapons_list:
        model = extract_weapon_model(weapon_entry, string_map, recipe_map)

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
        log_path = os.path.join("output", "excluded_weapons.log")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Excluded Weapon Items ({len(excluded)} total)\n")
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
