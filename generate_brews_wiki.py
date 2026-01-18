import json
import os

# Paths - Updated for new datajson structure
OUTPUT_BASE = os.path.join(os.environ.get("APPDATA", ""), "MoriaWikiGenerator", "output")
SOURCE_DIR = os.path.join(OUTPUT_BASE, "datajson", "Moria", "Content", "Tech", "Data")
STRINGS_DIR = os.path.join(SOURCE_DIR, "StringTables")
BREWS_FILE = os.path.join(SOURCE_DIR, "Items", "DT_Brews.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "Items", "DT_ItemRecipes.json")
THRESHOLD_EFFECTS_FILE = os.path.join(SOURCE_DIR, "Items", "DT_ThresholdEffects.json")
OUTPUT_DIR = os.path.join(OUTPUT_BASE, "wiki", "brews")

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

# Effect name overrides for brews that don't have discoverable effect names
EFFECT_NAME_OVERRIDE = {
    "Scour Pilsner": "Fortified",
    "Ironheart Stout": "Stout",
    "Darkeye Stout": "Darkeye",
}

# Effect name to threshold suffix mapping for overridden effects
# Used to look up effect descriptions when effect name is overridden
EFFECT_SUFFIX_OVERRIDE = {
    "Fortified": "Antidote",
    "Stout": "DefensiveBrew",
    "Darkeye": "AntiDarknessBrew",
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
    """Load DT_ItemRecipes.json and return a dict of recipe data by item name."""
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

                # Extract recipe data
                materials = []
                station = None
                craft_time = None
                result_item = None

                for prop in properties:
                    # Get crafting station
                    if prop.get("Name") == "CraftingStations":
                        stations = prop.get("Value", [])
                        if stations:
                            for st in stations[0].get("Value", []):
                                if st.get("Name") == "RowName":
                                    station = st.get("Value")

                    # Get craft time
                    elif prop.get("Name") == "CraftTimeSeconds":
                        craft_time = prop.get("Value")

                    # Get result item
                    elif prop.get("Name") == "ResultItemHandle":
                        for handle_prop in prop.get("Value", []):
                            if handle_prop.get("Name") == "RowName":
                                result_item = handle_prop.get("Value")

                    # Get materials
                    elif prop.get("Name") == "DefaultRequiredMaterials":
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

                if result_item:
                    recipes_dict[recipe_name] = {
                        'materials': materials,
                        'station': station,
                        'craft_time': craft_time,
                        'result_item': result_item
                    }

    return recipes_dict


def load_threshold_effects_data(filepath):
    """Load DT_ThresholdEffects.json and return a dict of effect durations."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    effects_dict = {}
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            effect_entries = table.get("Data", [])
            for effect_entry in effect_entries:
                effect_name = effect_entry.get("Name", "")

                # Only process Brew_XXX entries (these contain duration)
                if effect_name.startswith("Brew_"):
                    properties = effect_entry.get("Value", [])

                    # Find ThresholdTime property
                    for prop in properties:
                        if prop.get("Name") == "ThresholdTime":
                            duration = prop.get("Value", 0)
                            effects_dict[effect_name] = duration
                            break

    return effects_dict


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
    # Handle different prefixes
    if material_key.startswith("Item."):
        suffix = material_key.replace("Item.", "")
    elif material_key.startswith("Consumable."):
        suffix = material_key.replace("Consumable.", "")
    elif '.' in material_key:
        suffix = material_key.split('.')[-1]
    else:
        suffix = material_key

    # For pack-specific items like "EntPack_EntMoss", try removing the pack prefix
    if "_" in suffix and any(pack in suffix for pack in ["EntPack", "BeornPack", "RohanPack", "OrcHunterPack", "HolidayPack"]):
        # Extract the actual item name after the pack prefix
        parts = suffix.split("_", 1)
        if len(parts) > 1:
            suffix = parts[1]

    # Try Items.Items.XXX.Name first
    lookup_key1 = f"Items.Items.{suffix}.Name"
    display_name = string_map.get(lookup_key1)

    # Try Items.XXX.Name as fallback
    if not display_name:
        lookup_key2 = f"Items.{suffix}.Name"
        display_name = string_map.get(lookup_key2)

    # If still not found, try suffix matching
    if not display_name:
        for key, val in string_map.items():
            if key.endswith(f".{suffix}.Name"):
                return val

    # Fall back to the suffix if still not found
    if not display_name:
        return suffix

    return display_name


def find_brew_recipes(brew_name, recipes_dict):
    """Find all three size recipes (Small, Medium, Massive) for a brew.

    Returns a dict with combined recipe information or None if not found.
    """
    # Map recipe name patterns - brew items in DT_Brews use format like "Night_Brew"
    # but recipes can vary:
    # - Night_Brew -> Night_Brew_Small, Night_Brew_Medium, Night_Brew_Massive
    # - AntiDarkness_Brew -> AntiDarknessBrew_Brew_Small, AntiDarknessBrew_Brew_Medium, AntiDarknessBrew_Brew_Massive
    # - BeornPack_Brew -> BeornPack_BeornBrew_Small, BeornPack_BeornBrew_Medium, BeornPack_BeornBrew_Massive

    # Try multiple naming patterns
    base_name = brew_name

    # First, try exact match pattern
    recipes = {
        'Small': recipes_dict.get(f"{base_name}_Small"),
        'Medium': recipes_dict.get(f"{base_name}_Medium"),
        'Massive': recipes_dict.get(f"{base_name}_Massive")
    }

    # If not found, try without underscores and with _Brew suffix
    if not any(recipes.values()):
        # Remove underscores and add _Brew suffix
        alt_name = brew_name.replace("_", "") + "_Brew"
        recipes = {
            'Small': recipes_dict.get(f"{alt_name}_Small"),
            'Medium': recipes_dict.get(f"{alt_name}_Medium"),
            'Massive': recipes_dict.get(f"{alt_name}_Massive")
        }

    # If still not found, try pack-specific naming (e.g., BeornPack_Brew -> BeornPack_BeornBrew)
    if not any(recipes.values()):
        if "_" in brew_name:
            parts = brew_name.split("_")
            if len(parts) == 2:
                pack_name = parts[0]
                brew_suffix = parts[1]
                # Extract just the pack prefix (e.g., "BeornPack" -> "Beorn")
                pack_prefix = pack_name.replace("Pack", "")
                # Try PackName_PackPrefixBrew pattern (e.g., BeornPack_BeornBrew)
                alt_name = f"{pack_name}_{pack_prefix}{brew_suffix}"
                recipes = {
                    'Small': recipes_dict.get(f"{alt_name}_Small"),
                    'Medium': recipes_dict.get(f"{alt_name}_Medium"),
                    'Massive': recipes_dict.get(f"{alt_name}_Massive")
                }

    # If still not found, try fuzzy match by searching for similar names
    if not any(recipes.values()):
        brew_search = brew_name.replace("_", "").lower()
        for recipe_name in recipes_dict.keys():
            recipe_search = recipe_name.replace("_", "").lower()
            if brew_search in recipe_search and ("small" in recipe_search.lower()):
                # Found a potential match, extract base name
                base_match = recipe_name.replace("_Small", "").replace("_small", "")
                recipes = {
                    'Small': recipes_dict.get(f"{base_match}_Small"),
                    'Medium': recipes_dict.get(f"{base_match}_Medium"),
                    'Massive': recipes_dict.get(f"{base_match}_Massive")
                }
                break

    # Check if we have at least one recipe
    if not any(recipes.values()):
        return None

    # Combine materials from all three sizes
    combined_materials = {}
    stations = []
    craft_time = None

    for size, recipe in recipes.items():
        if recipe:
            # Store station
            if recipe.get('station'):
                stations.append(recipe['station'])

            # Get craft time (should be same for all sizes)
            if not craft_time and recipe.get('craft_time'):
                craft_time = recipe['craft_time']

            # Combine materials
            for mat_name, mat_count in recipe.get('materials', []):
                if mat_name not in combined_materials:
                    combined_materials[mat_name] = {}
                combined_materials[mat_name][size] = mat_count

    # Build result
    result = {
        'stations': stations,
        'craft_time': craft_time,
        'materials': combined_materials
    }

    return result


def format_brew_station(stations):
    """Format brewing stations for wiki template."""
    station_map = {
        'Brewery_Small': '[[Brew Kettle]]',
        'Brewery_Base': '[[Brew Tank]]',
        'Brewery_Massive': '[[King\'s Brew Tank]]'
    }

    # Map stations and add Alchemical Still requirement
    formatted = []
    for station in stations:
        if station in station_map:
            formatted.append(station_map[station])

    if formatted:
        return '<br>'.join(formatted) + '<br>with [[Alchemical Still]]'

    return ''


def format_brew_materials(materials_dict, string_map):
    """Format brewing materials in small-medium-massive format."""
    lines = []

    for mat_name, counts in materials_dict.items():
        # Get display name
        display_name = get_material_display_name(mat_name, string_map)

        # Build count string in small-medium-massive format
        small = counts.get('Small', 0)
        medium = counts.get('Medium', 0)
        massive = counts.get('Massive', 0)

        count_str = f"{small}-{medium}-{massive}"
        lines.append(f"{count_str} [[{display_name}]]")

    return '<br> '.join(lines)


def format_brew_time(seconds):
    """Format brew time as seconds and minutes."""
    if not seconds:
        return ''

    minutes = int(seconds / 60)
    return f"{int(seconds):,} seconds<br>({minutes} minutes)"


def get_brew_effect_info(properties, imports, threshold_effects, string_map):
    """Extract brew effect name and duration from UseEffects property.

    Returns a tuple: (effect_name, effect_duration_formatted, threshold_suffix)
    """
    # Find UseEffects property
    use_effects = None
    for prop in properties:
        if prop.get("Name") == "UseEffects":
            use_effects = prop.get("Value", [])
            break

    if not use_effects or not isinstance(use_effects, list) or len(use_effects) == 0:
        return None, None, None

    # Get the first effect reference
    effect_ref = use_effects[0].get("Value", 0)

    # Negative values reference imports
    if effect_ref >= 0:
        return None, None, None

    # Look up the import
    import_idx = abs(effect_ref) - 1
    if import_idx >= len(imports):
        return None, None, None

    effect_class = imports[import_idx].get("ObjectName", "")

    # Map effect class to threshold effect name
    # Pattern: GE_XXXSip_C -> Brew_XXX
    # Examples:
    #   GE_EveningAleSip_C -> Brew_EveningAle
    #   GE_StaminaBrewSip_C -> Brew_StaminaBrew
    #   GE_HealthBrewSip_C -> Brew_HealthBrew

    threshold_name = None
    duration = None

    # Try to match effect class to a threshold effect
    if effect_class.startswith("GE_") and "Sip" in effect_class:
        # Remove GE_ prefix and _C suffix
        base = effect_class.replace("GE_", "").replace("Sip_C", "")

        # Try to find matching threshold effect
        for thresh_name, thresh_duration in threshold_effects.items():
            # Check if the base matches the threshold name
            thresh_base = thresh_name.replace("Brew_", "")

            # Direct match or base match (accounting for "Brew" suffix)
            if base == thresh_base or base.replace("Brew", "") == thresh_base:
                threshold_name = thresh_name
                duration = thresh_duration
                break

    if not threshold_name or duration is None:
        return None, None, None

    # Format duration
    minutes = int(duration / 60)
    duration_str = f"{int(duration)} seconds ({minutes} minutes)"

    # Try to find effect name in string tables
    # Pattern: Survival.Buff.XXX.Name
    threshold_suffix = threshold_name.replace("Brew_", "")

    # Try multiple string key patterns
    effect_name = None
    for key_pattern in [
        f"Survival.Buff.{threshold_suffix}.Name",
        f"Survival.Buff.{threshold_suffix}Brew.Name",
    ]:
        if key_pattern in string_map:
            effect_name = string_map[key_pattern]
            break

    # If we couldn't find the effect name, return just the duration
    if not effect_name:
        return None, duration_str, threshold_suffix

    return effect_name, duration_str, threshold_suffix


def get_effect_description(effect_name, threshold_suffix, string_map):
    """Get effect description from string tables.

    Returns the effect description or None if not found.
    """
    if not effect_name and not threshold_suffix:
        return None

    # Try to find effect description in string tables
    # Pattern: Survival.Buff.XXX.Description
    desc_patterns = []

    if threshold_suffix:
        desc_patterns.extend([
            f"Survival.Buff.{threshold_suffix}.Description",
            f"Survival.Buff.{threshold_suffix}Brew.Description",
        ])

    for key_pattern in desc_patterns:
        if key_pattern in string_map:
            return string_map[key_pattern]

    return None


def generate_wiki_template(brew_model, string_map):
    """Generate MediaWiki template text for a brew."""
    lines = []

    # Item infobox
    lines.append("{{Item")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(" | imagecaption  = ")

    # Type
    lines.append(" | type          = Brew")

    # Subtype
    if brew_model.get("Subtype"):
        lines.append(f" | subtype       = {brew_model['Subtype']}")
    else:
        lines.append(" | subtype       = ")

    # Grip (empty for brews)
    lines.append(" | grip          = ")

    # Tier (empty for brews)
    lines.append(" | tier          = ")

    # Damage type (empty for brews)
    lines.append(" | damage_type   = ")

    # Station (from recipes)
    if brew_model.get("RecipeData"):
        station_str = format_brew_station(brew_model["RecipeData"].get("stations", []))
        if station_str:
            lines.append(f" | station       = {station_str}")

    # Requirements (materials in small-medium-massive format)
    if brew_model.get("RecipeData") and brew_model["RecipeData"].get("materials"):
        reqs_str = format_brew_materials(brew_model["RecipeData"]["materials"], string_map)
        if reqs_str:
            lines.append(f" | reqs          = {reqs_str}")

    # Time (craft time)
    if brew_model.get("RecipeData") and brew_model["RecipeData"].get("craft_time"):
        time_str = format_brew_time(brew_model["RecipeData"]["craft_time"])
        if time_str:
            lines.append(f" | time          = {time_str}")

    # Effect
    if brew_model.get("EffectName"):
        lines.append(f" | effect = [[{brew_model['EffectName']}]]")
    else:
        lines.append(" | effect = ")

    # Effect duration
    if brew_model.get("EffectDuration"):
        lines.append(f" | effect duration = {brew_model['EffectDuration']}")
    else:
        lines.append(" | effect duration = ")

    lines.append("}}")
    lines.append("")
    lines.append("'''{{PAGENAME}}''' is a [[Brew]] in ''[[{{topic}}]]''.")

    # Description section (only if non-empty)
    if brew_model.get("Description") and brew_model["Description"].strip():
        lines.append("")
        lines.append("==Description==")
        lines.append(f"In-game: {brew_model['Description']}")

        # Add effect description if available
        if brew_model.get("EffectDescription"):
            lines.append("")
            effect_name = brew_model.get("EffectName", "Effect")
            lines.append(f"'''{effect_name}''' - {brew_model['EffectDescription']}")

    # Unlocks section (only if unlock overrides exist)
    if brew_model.get("CampaignUnlock") or brew_model.get("SandboxUnlock"):
        lines.append("")
        lines.append("== Unlocks ==")
        lines.append("")
        if brew_model.get("CampaignUnlock"):
            lines.append(f"* Campaign {{{{spoiler|{brew_model['CampaignUnlock']}}}}}")
        if brew_model.get("SandboxUnlock"):
            lines.append(f"* Sandbox  {{{{spoiler|{brew_model['SandboxUnlock']}}}}}")

    # DLC section (if applicable)
    if brew_model.get("DLC"):
        lines.append("")
        lines.append("==Availability==")
        lines.append(f"This item is part of the {brew_model['DLCTitle']}.")

    return "\n".join(lines)


def process_brews(brews_data, string_map, recipes_dict, threshold_effects, imports):
    """Process all brews and generate wiki models."""
    print("\nProcessing brews...")
    brew_models = []

    for brew_entry in brews_data:
        brew_name = brew_entry.get("Name", "")

        # Get properties
        properties = brew_entry.get("Value", [])

        # Extract basic info
        display_name = get_string_property(properties, "DisplayName", string_map)
        description = get_string_property(properties, "Description", string_map)
        icon_path = get_property_value(properties, "Icon")
        actor_path = get_property_value(properties, "Actor")

        # Skip if no display name
        if not display_name:
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

        # Find brew recipes (all three sizes)
        recipe_data = find_brew_recipes(brew_name, recipes_dict)
        if recipe_data:
            brew_model["RecipeData"] = recipe_data

        # Extract effect information
        effect_name, effect_duration, threshold_suffix = get_brew_effect_info(
            properties, imports, threshold_effects, string_map
        )

        # Apply effect name override if available
        if display_name in EFFECT_NAME_OVERRIDE:
            effect_name = EFFECT_NAME_OVERRIDE[display_name]
            # Use the suffix override for looking up descriptions
            if effect_name in EFFECT_SUFFIX_OVERRIDE:
                threshold_suffix = EFFECT_SUFFIX_OVERRIDE[effect_name]

        if effect_name:
            brew_model["EffectName"] = effect_name
        if effect_duration:
            brew_model["EffectDuration"] = effect_duration

        # Get effect description
        effect_desc = get_effect_description(effect_name, threshold_suffix, string_map)
        if effect_desc:
            brew_model["EffectDescription"] = effect_desc

        brew_models.append(brew_model)

    print(f"  Processed {len(brew_models)} brews")
    return brew_models


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

    # Load threshold effects data
    print("Loading threshold effects data...")
    threshold_effects = load_threshold_effects_data(THRESHOLD_EFFECTS_FILE)
    print(f"  Total threshold effects: {len(threshold_effects)}")

    # Load brews data
    print("Loading brews data...")
    with open(BREWS_FILE, 'r', encoding='utf-8') as f:
        brews_json = json.load(f)

    # Extract imports for effect lookups
    imports = brews_json.get("Imports", [])
    print(f"  Total imports: {len(imports)}")

    brews_data = load_brews_data(BREWS_FILE)
    print(f"  Total brews: {len(brews_data)}")

    # Process brews
    brew_models = process_brews(brews_data, string_map, recipes_dict, threshold_effects, imports)

    # Write wiki files
    write_wiki_files(brew_models, OUTPUT_DIR, string_map)

    print("\nDone!")


if __name__ == "__main__":
    main()
