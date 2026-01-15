import json
import os

# Paths
SOURCE_DIR = "source"
STRINGS_DIR = os.path.join(SOURCE_DIR, "strings")
CONSTRUCTIONS_FILE = os.path.join(SOURCE_DIR, "DT_Constructions.json")
RECIPES_FILE = os.path.join(SOURCE_DIR, "DT_ConstructionRecipes.json")
ENTITLEMENTS_FILE = os.path.join(SOURCE_DIR, "DT_Entitlements.json")
UNLOCK_OVERRIDES_FILE = "construction_unlock_overrides.json"
OUTPUT_DIR = os.path.join("output", "constructions")

# DLC display name mappings
DLC_DISPLAY_NAMES = {
    "Beorn": "The Beorn's Lodge Pack",
    "OrcHunter": "The Orc Hunter Pack",
    "Ent": "The Ent-craft Pack",
    "Rohan": "The Rohirrim Pack",
    "Holiday": "Yule-tide Pack",
    "DurinsFolk": "Durin's Folk Expansion",
}

# DLC path patterns (for fallback detection from actor paths)
DLC_PATH_PATTERNS = {
    "BeornPack": "The Beorn's Lodge Pack",
    "DurinsFolk": "Durin's Folk Expansion",
    "Elven": "Durin's Folk Expansion",
    "EntPack": "The Ent-craft Pack",
    "HobbitPack": "The Hobbit's Bounty Pack",
    "OrcHunterPack": "The Orc Hunter Pack",
    "HolidayPack": "Yule-tide Pack",
    "RohanPack": "The Rohirrim Pack",
}

# Map path patterns to short DLC names (for unlock detection)
PATH_TO_SHORT_DLC = {
    "BeornPack": "Beorn",
    "DurinsFolk": "DurinsFolk",
    "Elven": "DurinsFolk",
    "EntPack": "Ent",
    "HobbitPack": "Hobbit",
    "OrcHunterPack": "OrcHunter",
    "HolidayPack": "Holiday",
    "RohanPack": "Rohan",
}

# Set detection rules
SET_RULES = [
    # Coastal Marble Set - contains "Fair" in display name (check first, higher priority)
    {"name": "Coastal Marble Set", "pattern": "Fair", "exclude_patterns": []},
    # Red Sandstone Set - contains "Crimson" in display name (check first, higher priority)
    {"name": "Red Sandstone Set", "pattern": "Crimson", "exclude_patterns": []},
    # Ancient Set - contains "Ancient" in display name but NOT Fair/Crimson (which are variants)
    {"name": "Ancient Set", "pattern": "Ancient", "exclude_patterns": ["Fair", "Crimson"]},
    # Imladris Furnishings Set - contains "Imladris" in display name
    {"name": "Imladris Furnishings Set", "pattern": "Imladris", "exclude_patterns": []},
    # Lodge Set - Beorn DLC items
    {"name": "Lodge Set", "dlc": "Beorn", "exclude_patterns": []},
    # Ent-craft Set - Ent DLC items
    {"name": "Ent-craft Set", "dlc": "Ent", "exclude_patterns": []},
    # Orc Hunter Set - OrcHunter DLC items
    {"name": "Orc Hunter Set", "dlc": "OrcHunter", "exclude_patterns": []},
    # Rohirrim Set - Rohan DLC items
    {"name": "Rohirrim Set", "dlc": "Rohan", "exclude_patterns": []},
    # Yule-tide Set - Holiday DLC items
    {"name": "Yule-tide Set", "dlc": "Holiday", "exclude_patterns": []},
]


def load_unlock_overrides(filepath):
    """Load construction unlock overrides from JSON file.

    Returns:
        dict: Maps display name -> {"campaign": text, "sandbox": text}
    """
    if not os.path.exists(filepath):
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_entitlements(filepath):
    """Load DT_Entitlements.json and return a dict mapping construction names to DLC names.

    Returns:
        dict: Maps construction internal name -> DLC short name (e.g., "Beorn", "OrcHunter")
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    construction_to_dlc = {}

    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            table_data = table.get("Data", [])
            for dlc_entry in table_data:
                dlc_name = dlc_entry.get("Name", "")

                # Get the Constructions array
                props = dlc_entry.get("Value", [])
                for prop in props:
                    if prop.get("Name") == "Constructions":
                        constructions_list = prop.get("Value", [])

                        # Each construction is a struct with RowName property
                        for construction_struct in constructions_list:
                            if isinstance(construction_struct, dict):
                                struct_value = construction_struct.get("Value", [])
                                for item in struct_value:
                                    if isinstance(item, dict) and item.get("Name") == "RowName":
                                        construction_name = item.get("Value")
                                        if construction_name:
                                            construction_to_dlc[construction_name] = dlc_name

    return construction_to_dlc


def determine_set(construction_name, display_name, dlc_name):
    """Determine which set a construction belongs to based on name patterns and DLC.

    Args:
        construction_name: Internal name of the construction
        display_name: Display name of the construction
        dlc_name: DLC short name (e.g., "Beorn", "OrcHunter") or None

    Returns:
        str or None: Set name if matched, None otherwise
    """
    for rule in SET_RULES:
        # Check if this rule matches
        matched = False

        # Pattern-based matching (check both internal and display names)
        if "pattern" in rule:
            pattern = rule["pattern"]
            if pattern in construction_name or (display_name and pattern in display_name):
                # Check exclusions
                excluded = False
                for exclude_pattern in rule.get("exclude_patterns", []):
                    if exclude_pattern in construction_name or (display_name and exclude_pattern in display_name):
                        excluded = True
                        break

                if not excluded:
                    matched = True

        # DLC-based matching
        if "dlc" in rule and dlc_name == rule["dlc"]:
            matched = True

        if matched:
            return rule["name"]

    return None


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


def get_property_value(properties, prop_name):
    """Extract a property value from the list of properties."""
    for prop in properties:
        if prop.get("Name") == prop_name:
            return prop.get("Value")
    return None


def get_property(properties, prop_name):
    """Extract a full property dict from the list of properties."""
    for prop in properties:
        if prop.get("Name") == prop_name:
            return prop
    return None


def resolve_string_table_reference(text_property, string_map):
    """Resolve a string table reference to its actual text.

    Args:
        text_property: Either a full property dict or a string key
        string_map: Dictionary mapping string table keys to values
    """
    if not text_property:
        return None

    # If it's already a string, look it up directly
    if isinstance(text_property, str):
        return string_map.get(text_property)

    # Check if it's a TextPropertyData with string table reference
    if isinstance(text_property, dict) and text_property.get("$type", "").endswith("TextPropertyData, UAssetAPI"):
        # The Value field contains the string table key
        key = text_property.get("Value")
        if key and isinstance(key, str):
            return string_map.get(key)

    return None


def get_tags(properties):
    """Extract gameplay tags from the Tags property."""
    tags = []
    for prop in properties:
        if prop.get("Name") == "Tags":
            tag_value = prop.get("Value", [])
            if tag_value and len(tag_value) > 0:
                # Extract GameplayTagContainer value
                for tag_prop in tag_value:
                    if tag_prop.get("Name") == "Tags":
                        tags = tag_prop.get("Value", [])
                        break
    return tags


def detect_dlc_from_path(actor_path):
    """Detect DLC from actor path."""
    if not actor_path:
        return None, None

    for pattern, dlc_name in DLC_PATH_PATTERNS.items():
        if pattern in actor_path:
            return pattern, dlc_name

    return None, None


def load_constructions_data(filepath):
    """Load DT_Constructions.json and return list of construction entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    constructions = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            constructions_data = table.get("Data", [])
            for construction in constructions_data:
                constructions.append(construction)

    return constructions


def load_recipes_data(filepath):
    """Load DT_ConstructionRecipes.json and return a dict keyed by construction name.

    Maps construction names to their recipes. Handles cases where recipe name differs
    from the construction it builds (e.g., Beorn_Roof_* recipes build BP_Beorn_RoofTile_*).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes_dict = {}
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            recipes_data = table.get("Data", [])
            for recipe in recipes_data:
                recipe_name = recipe.get("Name", "")
                if not recipe_name:
                    continue

                # Find what construction this recipe builds
                construction_name = recipe_name  # Default: recipe name = construction name
                props = recipe.get("Value", [])
                for prop in props:
                    if prop.get("Name") == "ResultConstructionHandle":
                        # This property contains the actual construction being built
                        handle_value = prop.get("Value")
                        if isinstance(handle_value, list):
                            for item in handle_value:
                                if isinstance(item, dict) and item.get("Name") == "RowName":
                                    construction_name = item.get("Value", recipe_name)
                                    break

                # Index by the construction name that gets built
                # Store both original case and lowercase for case-insensitive lookup
                recipes_dict[construction_name] = recipe
                recipes_dict[construction_name.lower()] = recipe

    return recipes_dict


def should_exclude_construction(name, display_name):
    """Determine if a construction should be excluded based on naming rules."""
    # Exclude internal names starting with [
    if name.startswith("["):
        return True, "Internal name starts with ["

    # Exclude display names starting with [
    if display_name and display_name.startswith("["):
        return True, "Display name starts with ["

    # Exclude internal names starting with _Beorn
    if name.startswith("_Beorn"):
        return True, "Internal name starts with _Beorn"

    # Exclude display names starting with _ or *
    if display_name and (display_name.startswith("_") or display_name.startswith("*")):
        return True, "Display name starts with _ or *"

    # Exclude anything with "Broken" in internal or display name
    if "Broken" in name or (display_name and "Broken" in display_name):
        return True, "Contains 'Broken'"

    return False, None


def get_material_variant(internal_name):
    """Determine material variant from internal name.

    Returns: "RedSandstone", "WhiteMarble", or None for base material
    """
    if "_RedSandstone" in internal_name or internal_name.endswith("_RedSandstone"):
        return "RedSandstone"
    elif "_WhiteMarble" in internal_name or internal_name.endswith("_WhiteMarble"):
        return "WhiteMarble"
    else:
        return None


def apply_material_prefix(display_name, material_variant):
    """Apply Crimson or Fair prefix for material variants.

    Args:
        display_name: Original display name
        material_variant: "RedSandstone", "WhiteMarble", or None

    Returns: Modified display name with prefix, or original if no variant
    """
    if material_variant == "RedSandstone":
        # Check if "Crimson" is already in the name
        if "Crimson" in display_name or "crimson" in display_name:
            return display_name  # Already has the material indicator
        return f"Crimson {display_name}"
    elif material_variant == "WhiteMarble":
        # Check if "Fair" is already in the name
        if "Fair" in display_name or "fair" in display_name:
            return display_name  # Already has the material indicator
        return f"Fair {display_name}"
    else:
        return display_name


def resolve_construction_display_name(name, properties, string_map):
    """Resolve construction display name with fallback strategies."""
    display_name_prop = get_property_value(properties, "DisplayName")
    display_name = resolve_string_table_reference(display_name_prop, string_map)

    # If not found and name starts with _, try without the underscore
    if not display_name and name.startswith("_"):
        cleaned_name = name[1:]  # Remove leading underscore
        # Try to find the display name with cleaned internal name
        for key in [f"{cleaned_name}.Name", f"Constructions.{cleaned_name}.Name"]:
            if key in string_map:
                display_name = string_map[key]
                break

    # If not found and name starts with CraftingStation_, try without that prefix
    if not display_name and name.startswith("CraftingStation_"):
        cleaned_name = name.replace("CraftingStation_", "")
        # Try to find the display name with cleaned internal name
        for key in [f"{cleaned_name}.Name", f"Constructions.{cleaned_name}", f"Constructions.{cleaned_name}.Name"]:
            if key in string_map:
                display_name = string_map[key]
                break

    # Apply material variant prefix if applicable
    # Skip material prefix for items starting with [ or _ (these will be excluded anyway)
    if display_name and not name.startswith("[") and not name.startswith("_"):
        material_variant = get_material_variant(name)
        display_name = apply_material_prefix(display_name, material_variant)

    return display_name


def analyze_construction(construction, recipe, string_map, dlc_map):
    """Analyze a single construction and return data model.

    Args:
        construction: Construction data from DT_Constructions.json
        recipe: Recipe data from DT_ConstructionRecipes.json
        string_map: String table mappings
        dlc_map: Dict mapping construction names to DLC short names

    Returns:
        dict: Construction data model
    """
    name = construction.get("Name", "")
    properties = construction.get("Value", [])

    # Basic info - use enhanced display name resolution
    display_name = resolve_construction_display_name(name, properties, string_map)

    description_prop = get_property_value(properties, "Description")
    description = resolve_string_table_reference(description_prop, string_map)

    # Actor path (for backward compatibility DLC detection)
    actor_prop = get_property_value(properties, "Actor")
    actor_path = None
    if actor_prop and isinstance(actor_prop, dict):
        asset_path = actor_prop.get("AssetPath", {})
        if isinstance(asset_path, dict):
            actor_path = asset_path.get("AssetName", "")

    # Tags
    tags = get_tags(properties)

    # DLC detection from entitlements file (preferred) or actor path (fallback)
    dlc_short_name = dlc_map.get(name)  # e.g., "Beorn", "OrcHunter"
    dlc_display_name = DLC_DISPLAY_NAMES.get(dlc_short_name) if dlc_short_name else None

    # Fallback to old path-based detection if not in entitlements
    if not dlc_short_name:
        dlc_path_pattern, dlc_name = detect_dlc_from_path(actor_path)
        dlc_display_name = dlc_name
        # Normalize path pattern to short DLC name for unlock detection
        dlc_key = PATH_TO_SHORT_DLC.get(dlc_path_pattern) if dlc_path_pattern else None
    else:
        dlc_key = dlc_short_name

    # Determine set membership
    set_name = determine_set(name, display_name, dlc_short_name)

    model = {
        "InternalName": name,
        "DisplayName": display_name,
        "Description": description,
        "ActorPath": actor_path,
        "Tags": tags,
        "DLC": dlc_key,
        "DLCTitle": f"{{{{LI|{dlc_display_name}}}}}" if dlc_display_name else None,
        "DLCDisplayName": dlc_display_name,
        "Set": set_name,
    }

    # Recipe info
    if recipe:
        recipe_props = recipe.get("Value", [])

        # Build process
        build_process_prop = get_property_value(recipe_props, "BuildProcess")
        model["BuildProcess"] = build_process_prop

        # Location requirement
        location_req_prop = get_property_value(recipe_props, "LocationRequirement")
        model["LocationRequirement"] = location_req_prop

        # Placement type
        placement_type_prop = get_property_value(recipe_props, "PlacementType")
        model["PlacementType"] = placement_type_prop

        # Placement flags
        model["bOnWall"] = get_property_value(recipe_props, "bOnWall")
        model["bOnFloor"] = get_property_value(recipe_props, "bOnFloor")
        model["bOnWater"] = get_property_value(recipe_props, "bPlaceOnWater")

        # Monument type
        monument_type_prop = get_property_value(recipe_props, "MonumentType")
        model["MonumentType"] = monument_type_prop

        # Materials (DefaultRequiredMaterials)
        materials = []
        default_materials = get_property_value(recipe_props, "DefaultRequiredMaterials")
        if default_materials and isinstance(default_materials, list):
            for mat in default_materials:
                mat_props = mat.get("Value", [])
                mat_handle = get_property_value(mat_props, "MaterialHandle")
                count = get_property_value(mat_props, "Count")

                # Extract material row name
                mat_name = None
                if mat_handle and isinstance(mat_handle, list):
                    for mh_prop in mat_handle:
                        if mh_prop.get("Name") == "RowName":
                            mat_name = mh_prop.get("Value")
                            break

                if mat_name and count:
                    materials.append({
                        "Material": mat_name,
                        "Count": count
                    })

        model["Materials"] = materials

        # Sandbox materials (SandboxRequiredMaterials)
        sandbox_materials = []
        sandbox_mats = get_property_value(recipe_props, "SandboxRequiredMaterials")
        if sandbox_mats and isinstance(sandbox_mats, list):
            for mat in sandbox_mats:
                mat_props = mat.get("Value", [])
                mat_handle = get_property_value(mat_props, "MaterialHandle")
                count = get_property_value(mat_props, "Count")

                # Extract material row name
                mat_name = None
                if mat_handle and isinstance(mat_handle, list):
                    for mh_prop in mat_handle:
                        if mh_prop.get("Name") == "RowName":
                            mat_name = mh_prop.get("Value")
                            break

                if mat_name and count:
                    sandbox_materials.append({
                        "Material": mat_name,
                        "Count": count
                    })

        model["SandboxMaterials"] = sandbox_materials

        # Unlock info
        model["bHasSandboxUnlockOverride"] = get_property_value(recipe_props, "bHasSandboxUnlockOverride")

        # Sandbox unlocks
        sandbox_unlocks = get_property_value(recipe_props, "SandboxUnlocks")
        if sandbox_unlocks and isinstance(sandbox_unlocks, list):
            unlock_type = get_property_value(sandbox_unlocks, "UnlockType")
            model["SandboxUnlockType"] = unlock_type

            # Required items for unlock
            required_items = get_property_value(sandbox_unlocks, "UnlockRequiredItems")
            if required_items and isinstance(required_items, list):
                req_item_names = []
                for req in required_items:
                    req_props = req.get("Value", [])
                    for rp in req_props:
                        if rp.get("Name") == "RowName":
                            req_item_names.append(rp.get("Value"))
                model["SandboxRequiredItems"] = req_item_names

            # Required constructions for unlock
            required_constructions = get_property_value(sandbox_unlocks, "UnlockRequiredConstructions")
            if required_constructions and isinstance(required_constructions, list):
                req_const_names = []
                for req in required_constructions:
                    req_props = req.get("Value", [])
                    for rp in req_props:
                        if rp.get("Name") == "RowName":
                            req_const_names.append(rp.get("Value"))
                model["SandboxRequiredConstructions"] = req_const_names

            # Required fragments for unlock
            required_fragments = get_property_value(sandbox_unlocks, "UnlockRequiredFragments")
            if required_fragments and isinstance(required_fragments, list):
                req_frag_names = []
                for req in required_fragments:
                    req_props = req.get("Value", [])
                    for rp in req_props:
                        if rp.get("Name") == "RowName":
                            req_frag_names.append(rp.get("Value"))
                model["SandboxRequiredFragments"] = req_frag_names

        # Default (campaign) unlocks
        default_unlocks = get_property_value(recipe_props, "DefaultUnlocks")
        if default_unlocks and isinstance(default_unlocks, list):
            unlock_type = get_property_value(default_unlocks, "UnlockType")
            model["DefaultUnlockType"] = unlock_type

            # Required items for unlock
            required_items = get_property_value(default_unlocks, "UnlockRequiredItems")
            if required_items and isinstance(required_items, list):
                req_item_names = []
                for req in required_items:
                    req_props = req.get("Value", [])
                    for rp in req_props:
                        if rp.get("Name") == "RowName":
                            req_item_names.append(rp.get("Value"))
                model["DefaultRequiredItems"] = req_item_names

            # Required constructions for unlock
            required_constructions = get_property_value(default_unlocks, "UnlockRequiredConstructions")
            if required_constructions and isinstance(required_constructions, list):
                req_const_names = []
                for req in required_constructions:
                    req_props = req.get("Value", [])
                    for rp in req_props:
                        if rp.get("Name") == "RowName":
                            req_const_names.append(rp.get("Value"))
                model["DefaultRequiredConstructions"] = req_const_names

            # Required fragments for unlock
            required_fragments = get_property_value(default_unlocks, "UnlockRequiredFragments")
            if required_fragments and isinstance(required_fragments, list):
                req_frag_names = []
                for req in required_fragments:
                    req_props = req.get("Value", [])
                    for rp in req_props:
                        if rp.get("Name") == "RowName":
                            req_frag_names.append(rp.get("Value"))
                model["DefaultRequiredFragments"] = req_frag_names

    return model


def load_items_data(filepath):
    """Load DT_Items.json to get item display names."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items_map = {}
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if table:
            items_data = table.get("Data", [])
            for item in items_data:
                item_name = item.get("Name", "")
                properties = item.get("Value", [])

                # Get display name
                display_name_value = get_property_value(properties, "DisplayName")
                if display_name_value:
                    items_map[item_name] = display_name_value

    return items_map


def get_category_from_tags(tags, string_map):
    """Extract building type and subtype from gameplay tags."""
    building_type = None
    subtype = None

    for tag in tags:
        # Tags format: UI.Construction.Category.{Type}.{Subtype}
        if tag.startswith("UI.Construction.Category."):
            parts = tag.split(".")
            if len(parts) >= 4:
                building_type = parts[3]  # e.g., "Base", "Crude", "Advanced"
            if len(parts) >= 5:
                subtype = parts[4]  # e.g., "Handycraft", "Scaffolding", "Decorative"

    # Look up friendly names in string tables if available
    if building_type:
        type_key = f"UI.Construction.Category.{building_type}"
        if type_key in string_map:
            building_type = string_map[type_key]

    if subtype:
        subtype_key = f"UI.Construction.Category.{building_type}.{subtype}"
        if subtype_key in string_map:
            subtype = string_map[subtype_key]

    return building_type, subtype


def format_materials(materials, items_map, string_map):
    """Format materials list as wiki text."""
    import re
    if not materials:
        return ""

    mat_parts = []
    for mat in materials:
        mat_name = mat["Material"]
        count = mat["Count"]

        # Look up display name
        display_name = None
        if mat_name in items_map:
            # Get the string table key from items
            string_key = items_map[mat_name]
            display_name = resolve_string_table_reference(string_key, string_map)

        if not display_name:
            # Fallback: use the internal name, cleaned up
            cleaned = mat_name.replace("Item.", "").replace("Ore.", "").replace("_", " ")
            # Add spaces before capital letters for camelCase
            display_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)

        mat_parts.append(f"{count} [[{display_name}]]")

    return "<br>".join(mat_parts)


def convert_item_key_to_display_name(item_key, string_map):
    """
    Convert item key format to display name for constructions.
    Handles "Ore.ItemName" -> "Item Name Ore" conversion.
    E.g., "Ore.Copper" -> "Copper Ore", "Item.QualityWood" -> "Elven Wood"
    """
    # Handle "Prefix.Suffix" format first (e.g., "Item.QualityWood", "Ore.Copper")
    if '.' in item_key:
        parts = item_key.split('.')
        if len(parts) == 2:
            prefix, suffix = parts

            # Try looking up just the suffix part
            for pattern in [
                f"Items.Items.{suffix}.Name",
                f"Items.Ores.{suffix}.Name",
                f"{suffix}.Name"
            ]:
                display_name = string_map.get(pattern)
                if display_name:
                    return display_name

            # Try reversed format (for cases like "Ore.Copper" -> "CopperOre")
            reversed_key = suffix + prefix
            for pattern in [f"Items.Items.{reversed_key}.Name", f"Items.Ores.{reversed_key}.Name"]:
                display_name = string_map.get(pattern)
                if display_name:
                    return display_name

            # Fallback: format as "Suffix Prefix"
            import re
            suffix_formatted = re.sub(r'([a-z])([A-Z])', r'\1 \2', suffix)
            return f"{suffix_formatted} {prefix}"

    # Try direct lookups for keys without dots
    for pattern in [
        f"Items.Items.{item_key}.Name",
        f"Items.Ores.{item_key}.Name",
        f"{item_key}.Name"
    ]:
        display_name = string_map.get(pattern)
        if display_name:
            return display_name

    # Fallback: return cleaned up key
    import re
    cleaned = item_key.replace("Item.", "").replace("Ore.", "").replace("_", " ")
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)


def format_unlock_requirements(required_constructions, required_items, required_fragments, constructions_map, string_map):
    """Format unlock requirements as 'Discover X' text matching items format."""
    import re

    # Collect all required things
    all_requirements = []

    # Add required items
    if required_items:
        for item_key in required_items:
            display_name = convert_item_key_to_display_name(item_key, string_map)
            all_requirements.append(f"{{{{LI|{display_name}}}}}")

    # Add required constructions
    if required_constructions:
        for const_name in required_constructions:
            # Look up in constructions map
            if const_name in constructions_map:
                const_model = constructions_map[const_name]
                if const_model.get("DisplayName"):
                    all_requirements.append(f"{{{{LI|{const_model['DisplayName']}}}}}")
                else:
                    # Clean up the name
                    cleaned = const_name.replace("_", " ")
                    cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)
                    all_requirements.append(cleaned)
            else:
                # Clean up the name
                cleaned = const_name.replace("_", " ")
                cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)
                all_requirements.append(cleaned)

    # Add required fragments (less common)
    if required_fragments:
        for fragment_key in required_fragments:
            fragment_name = fragment_key.replace("_Fragment", "").replace("_", " ")
            fragment_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', fragment_name)
            all_requirements.append(fragment_name)

    # Format as "Discover X and Y" or "Discover X, Y, and Z"
    if not all_requirements:
        return "Unlocked by discovering dependencies"
    elif len(all_requirements) == 1:
        return f"Discover {all_requirements[0]}"
    elif len(all_requirements) == 2:
        return f"Discover {all_requirements[0]} and {all_requirements[1]}"
    else:
        # Oxford comma for 3+ items
        all_but_last = ", ".join(all_requirements[:-1])
        return f"Discover {all_but_last}, and {all_requirements[-1]}"


def generate_wiki_template(construction_model, items_map, constructions_map, string_map, unlock_overrides):
    """Generate MediaWiki template text for a construction."""
    lines = []

    # Building object infobox
    lines.append("{{Building object")
    lines.append(" | title         = {{PAGENAME}}")
    lines.append(" | image         = {{PAGENAME}}.webp")
    lines.append(" | imagecaption  = ")

    # Type and subtype
    building_type, subtype = get_category_from_tags(construction_model.get("Tags", []), string_map)
    if building_type:
        lines.append(f" | type          = {building_type}")
    else:
        lines.append(" | type          = ")

    if subtype:
        lines.append(f" | subtype       = {subtype}")
    else:
        lines.append(" | subtype       = ")

    # Materials
    materials_str = format_materials(construction_model.get("Materials", []), items_map, string_map)
    if materials_str:
        lines.append(f" | reqs          = {materials_str}")
    else:
        lines.append(" | reqs          = ")

    lines.append("}}")
    lines.append("")
    lines.append("'''{{PAGENAME}}''' is a [[building]] object and building plan in ''[[{{topic}}]]''.")

    # Description section
    if construction_model.get("Description") and construction_model["Description"].strip():
        lines.append("")
        lines.append("==Description==")
        lines.append(construction_model["Description"])

    # Unlock section - matching items format
    has_recipe = construction_model.get("Materials") is not None  # If it has materials, it has a recipe
    has_campaign_unlock = construction_model.get("DefaultUnlockType") not in [None, "EMorRecipeUnlockType::Manual"]
    has_sandbox_unlock = construction_model.get("SandboxUnlockType") not in [None, "EMorRecipeUnlockType::Manual"]

    # Check for individual unlock overrides (highest priority)
    display_name = construction_model.get("DisplayName")
    unlock_override = unlock_overrides.get(display_name)
    has_unlock_override = unlock_override is not None

    # Check for special DLC unlocks (these have Manual type but need custom unlock text)
    dlc_name = construction_model.get("DLC")
    is_special_unlock = False
    special_unlock_text = None

    # DLC unlocks (highest priority)
    if dlc_name == "Beorn":
        is_special_unlock = True
        special_unlock_text = "Purchase the [[The Beorn's Lodge Pack]] DLC"
    elif dlc_name == "Ent":
        is_special_unlock = True
        special_unlock_text = "Purchase the [[The Ent-craft Pack]] DLC"
    elif dlc_name == "OrcHunter":
        is_special_unlock = True
        special_unlock_text = "Purchase the [[The Orc Hunter Pack]] DLC"
    elif dlc_name == "Holiday":
        is_special_unlock = True
        special_unlock_text = "Purchase the [[Yule-tide Pack]] DLC"
    elif dlc_name == "DurinsFolk":
        is_special_unlock = True
        special_unlock_text = "Purchase the {{LI|Durin's Folk Expansion}}"
    else:
        # Check for building set unlocks (lower priority than DLC)
        set_name = construction_model.get("Set")
        if set_name == "Coastal Marble Set":
            is_special_unlock = True
            special_unlock_text = "Purchase the Coastal Marble Building Set blueprints from the {{LI|Blue Mountains Trader}}"
        elif set_name == "Red Sandstone Set":
            is_special_unlock = True
            special_unlock_text = "Purchase the Red Sandstone Building Set blueprints from the {{LI|Red Mountains Trader}}"
        elif set_name == "Ancient Set":
            is_special_unlock = True
            special_unlock_text = "Purchase the Ancient Building Set blueprints from the {{LI|Gondor Trader}}"
        elif set_name == "Imladris Furnishings Set":
            is_special_unlock = True
            special_unlock_text = "Purchase the Imladris Furnishing Plans blueprints from the {{LI|Rivendell Trader}}"

    if has_recipe and (has_campaign_unlock or has_sandbox_unlock or construction_model.get("bHasSandboxUnlockOverride") or is_special_unlock or has_unlock_override):
        lines.append("")
        lines.append("== Unlock ==")

        if has_unlock_override:
            # Use individual unlock override (highest priority)
            lines.append(f"'''Campaign:''' {unlock_override['campaign']}")
            lines.append(f"'''Sandbox:''' {unlock_override['sandbox']}")
        elif is_special_unlock:
            # Use special unlock text (DLC or building set) for both Campaign and Sandbox
            lines.append(f"'''Campaign:''' {special_unlock_text}")
            lines.append(f"'''Sandbox:''' {special_unlock_text}")
        else:
            # Normal unlock processing
            # Campaign unlock
            campaign_req = format_unlock_requirements(
                construction_model.get("DefaultRequiredConstructions", []),
                construction_model.get("DefaultRequiredItems", []),
                construction_model.get("DefaultRequiredFragments", []),
                constructions_map,
                string_map
            )
            lines.append(f"'''Campaign:''' {campaign_req}")

            # Sandbox unlock - check if it has meaningful data
            sandbox_has_data = (
                construction_model.get("SandboxRequiredConstructions") or
                construction_model.get("SandboxRequiredItems") or
                construction_model.get("SandboxRequiredFragments") or
                has_sandbox_unlock
            )

            if sandbox_has_data:
                # Generate separate sandbox unlock text
                sandbox_req = format_unlock_requirements(
                    construction_model.get("SandboxRequiredConstructions", []),
                    construction_model.get("SandboxRequiredItems", []),
                    construction_model.get("SandboxRequiredFragments", []),
                    constructions_map,
                    string_map
                )
                lines.append(f"'''Sandbox:''' {sandbox_req}")
            else:
                # Use campaign unlock for sandbox if no meaningful override
                lines.append(f"'''Sandbox:''' {campaign_req}")

    # DLC and Set information
    has_dlc = construction_model.get("DLCDisplayName") is not None
    has_set = construction_model.get("Set") is not None

    if has_dlc or has_set:
        lines.append("")
        if has_dlc and has_set:
            lines.append("==DLC and Set==")
        elif has_dlc:
            lines.append("==DLC==")
        elif has_set:
            lines.append("==Set==")

        if has_dlc:
            lines.append(f"This building is part of the {construction_model['DLCTitle']}.")

        if has_set:
            lines.append(f"This building is part of the '''{construction_model['Set']}'''.")

    lines.append("")
    lines.append("{{Navbox building objects}}")

    return "\n".join(lines)


def sanitize_filename(filename):
    """Sanitize filename for filesystem compatibility."""
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def write_wiki_files(construction_models, output_dir, items_map, string_map, unlock_overrides, all_constructions_map=None):
    """Write wiki files for all constructions."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Use the provided complete map for cross-references, or build from models if not provided
    if all_constructions_map is None:
        all_constructions_map = {model["InternalName"]: model for model in construction_models}

    print(f"\nWriting wiki files to {output_dir}...")
    for model in construction_models:
        display_name = model.get("DisplayName")
        if not display_name:
            continue

        # Generate wiki content using complete constructions map
        wiki_content = generate_wiki_template(model, items_map, all_constructions_map, string_map, unlock_overrides)

        # Write to file
        filename = sanitize_filename(display_name) + ".wiki"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wiki_content)

    print(f"  Wrote {len(construction_models)} wiki files")


def write_excluded_log(excluded_constructions, output_dir):
    """Write a log of excluded constructions."""
    log_path = os.path.join(output_dir, "excluded_constructions.txt")

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("Excluded Constructions\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total excluded: {len(excluded_constructions)}\n\n")

        for construction in excluded_constructions:
            f.write(f"- {construction['InternalName']}")
            if construction.get('DisplayName'):
                f.write(f" ({construction['DisplayName']})")
            f.write(f" - Reason: {construction.get('ExclusionReason', 'Unknown')}\n")

    print(f"  Wrote exclusion log: {log_path}")


def process_constructions(constructions, recipes, string_map, dlc_map):
    """Process all constructions and generate models.

    Args:
        constructions: List of construction data
        recipes: Dict of recipes keyed by construction name
        string_map: String table mappings
        dlc_map: Dict mapping construction names to DLC short names

    Returns:
        tuple: (construction_models, excluded_constructions, all_constructions_map)
    """
    from collections import defaultdict

    print("\nProcessing constructions...")
    all_constructions_map = {}  # Map of ALL constructions for cross-references
    construction_models = []  # Only constructions to generate wiki files for
    excluded_constructions = []

    # First pass: Build complete map of all constructions
    for construction in constructions:
        name = construction.get("Name", "")
        # Try exact case first, then lowercase for case-insensitive match
        recipe = recipes.get(name) or recipes.get(name.lower())
        model = analyze_construction(construction, recipe, string_map, dlc_map)

        # Check exclusion rules first
        should_exclude, exclusion_reason = should_exclude_construction(name, model.get("DisplayName"))
        if should_exclude:
            model["ExclusionReason"] = exclusion_reason
            excluded_constructions.append(model)
            continue

        # Add to map if it has a display name (for cross-references)
        if model.get("DisplayName"):
            all_constructions_map[name] = model

    # Group by display name to handle V2 duplicates
    display_name_groups = defaultdict(list)
    for name, model in all_constructions_map.items():
        display_name = model.get("DisplayName")
        if display_name:
            display_name_groups[display_name].append((name, model))

    # Second pass: Determine which to include in wiki generation
    for display_name, items in display_name_groups.items():
        if len(items) == 1:
            # No conflict, include it
            name, model = items[0]

            # Skip constructions without recipes (can't be built by player)
            if not (recipes.get(name) or recipes.get(name.lower())):
                model["ExclusionReason"] = "No recipe data"
                excluded_constructions.append(model)
                continue

            construction_models.append(model)
        else:
            # Multiple items with same display name
            # Prefer V2 version if exists, otherwise take first with recipe
            v2_item = None
            non_v2_items = []

            for name, model in items:
                if "_V2" in name or name.endswith("_V2"):
                    v2_item = (name, model)
                else:
                    non_v2_items.append((name, model))

            # Choose which to include
            if v2_item:
                # Use V2 version
                name, model = v2_item
                if recipes.get(name) or recipes.get(name.lower()):
                    construction_models.append(model)
                else:
                    model["ExclusionReason"] = "No recipe data"
                    excluded_constructions.append(model)

                # Exclude non-V2 versions
                for name, model in non_v2_items:
                    model["ExclusionReason"] = "Superseded by V2 version"
                    excluded_constructions.append(model)
            else:
                # No V2 version
                # If multiple items with recipes, disambiguate with suffix
                items_with_recipes = [(n, m) for n, m in items if (recipes.get(n) or recipes.get(n.lower()))]
                items_without_recipes = [(n, m) for n, m in items if not (recipes.get(n) or recipes.get(n.lower()))]

                if len(items_with_recipes) > 1:
                    # Multiple buildable items with same display name
                    # Add disambiguation suffix based on internal name prefix
                    for name, model in items_with_recipes:
                        # Determine suffix from internal name pattern
                        suffix = None
                        if name.startswith("Advanced_Column"):
                            suffix = " (Advanced)"
                        elif name.startswith("Fortress_Column"):
                            suffix = " (Fortress)"
                        elif name.startswith("Crude_"):
                            suffix = " (Crude)"
                        elif name.startswith("Elder_"):
                            suffix = " (Elder)"
                        elif name.startswith("Beorn_"):
                            suffix = " (Beorn)"
                        elif name.startswith("DurinsTowerSet_"):
                            suffix = " (Durin)"
                        elif "_Sandbox" in name:
                            suffix = " (Sandbox)"

                        if suffix:
                            model["DisplayName"] = model["DisplayName"] + suffix
                            model["DisambiguationSuffix"] = suffix

                        construction_models.append(model)
                elif len(items_with_recipes) == 1:
                    # Only one has a recipe, include it
                    construction_models.append(items_with_recipes[0][1])

                # Exclude items without recipes
                for name, model in items_without_recipes:
                    model["ExclusionReason"] = "No recipe data"
                    excluded_constructions.append(model)

    print(f"  Processed {len(construction_models)} constructions for wiki generation")
    print(f"  Excluded {len(excluded_constructions)} constructions")
    print(f"  Total in reference map: {len(all_constructions_map)} constructions")

    return construction_models, excluded_constructions, all_constructions_map


def main():
    """Main entry point."""
    # Load string tables
    print("Loading string tables...")
    string_map = load_all_string_tables(STRINGS_DIR)
    print(f"  Total strings: {len(string_map)}")

    # Load items data for material lookups
    print("Loading items data...")
    items_file = os.path.join(SOURCE_DIR, "DT_Items.json")
    items_map = load_items_data(items_file)
    print(f"  Total items: {len(items_map)}")

    # Load constructions
    print("Loading constructions...")
    constructions = load_constructions_data(CONSTRUCTIONS_FILE)
    print(f"  Total constructions: {len(constructions)}")

    # Load recipes
    print("Loading recipes...")
    recipes = load_recipes_data(RECIPES_FILE)
    print(f"  Total recipes: {len(recipes)}")

    # Load DLC entitlements
    print("Loading DLC entitlements...")
    dlc_map = load_entitlements(ENTITLEMENTS_FILE)
    print(f"  Total DLC constructions: {len(dlc_map)}")

    # Load unlock overrides
    print("Loading unlock overrides...")
    unlock_overrides = load_unlock_overrides(UNLOCK_OVERRIDES_FILE)
    print(f"  Total unlock overrides: {len(unlock_overrides)}")

    # Process constructions
    construction_models, excluded_constructions, all_constructions_map = process_constructions(
        constructions, recipes, string_map, dlc_map
    )

    # Write wiki files using the complete constructions map for cross-references
    write_wiki_files(construction_models, OUTPUT_DIR, items_map, string_map, unlock_overrides, all_constructions_map)

    # Write exclusion log
    if excluded_constructions:
        write_excluded_log(excluded_constructions, "output")

    print("\nDone!")


if __name__ == "__main__":
    main()
