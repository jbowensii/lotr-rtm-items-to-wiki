# Changelog: Version 0.6 - Construction System

## Major New Features

### 1. Complete Construction Wiki Generator
**File:** `generate_constructions_wiki.py`

Generates comprehensive wiki pages for all buildable construction items in Lord of the Rings: Return to Moria.

**Output:**
- 793 wiki pages for buildable constructions
- 40 legitimate exclusions with detailed reporting
- Full MediaWiki template formatting

**Key Features:**
- Building object infobox with type, subtype, and material requirements
- Description section
- Campaign and sandbox unlock requirements
- DLC and Set membership information
- Cross-referenced prerequisites

### 2. DLC Detection System
Tracks which constructions belong to DLC packs using data from `DT_Entitlements.json`.

**Supported DLCs:**
- The Beorn's Lodge Pack
- The Orc Hunter Pack
- The Ent-craft Pack
- The Rohirrim Pack
- Yule-tide Pack
- Durin's Folk Expansion

**Implementation:**
- Primary: Explicit mapping from DT_Entitlements.json (132 constructions)
- Fallback: Actor path pattern detection
- Wiki output: `{{LI|DLC Name}}` template format

### 3. Set Detection System
Automatically determines set membership based on naming patterns and DLC affiliation.

**Supported Sets:**
1. **Ancient Set** - Items containing "Fortress" in internal name
2. **Coastal Marble Set** - Items containing "Fair" in display name
3. **Red Sandstone Set** - Items containing "Crimson" in display name
4. **Lodge Set** - All Beorn DLC items
5. **Ent-craft Set** - All Ent DLC items
6. **Orc Hunter Set** - All OrcHunter DLC items
7. **Rohirrim Set** - All Rohan DLC items
8. **Yule-tide Set** - All Holiday DLC items

**Wiki Output Example:**
```mediawiki
==DLC and Set==
This building is part of the {{LI|Durin's Folk Expansion}}.
This building is part of the '''Ancient Set'''.
```

### 4. Recipe-to-Construction Name Mapping
Solves the problem where recipe names differ from the constructions they build.

**Examples Fixed:**
- `Beorn_Roof_Slope1_200x100x100_A` → `BP_Beorn_RoofTile_Slope1_1m_A`
- `Fortress_Slope_1m` → `Elder_Slope_1m`
- `Advanced_Stairs_Inside` → `Elder_Stairs_Inside`
- `HolidayPack_CandelabraA` → `HolidayPack_Deco_Candelabra_A`
- `TreasurePile_Coin_Huge` → `TreasurePile_Coins_Huge`

**Implementation:**
Parses `ResultConstructionHandle` property from recipes to determine the actual construction being built.

### 5. Disambiguation System
Handles items with identical display names by adding suffixes.

**Suffixes Applied:**
- `(Advanced)` - for Advanced_Column_* items
- `(Fortress)` - for Fortress_Column_* items
- `(Elder)` - for Elder_* items
- `(Crude)` - for Crude_* items
- `(Beorn)` - for Beorn_* items
- `(Durin)` - for DurinsTowerSet_* items
- `(Sandbox)` - for *_Sandbox items

**Example Results:**
- `Crimson Column Base (Advanced).wiki` - 1 Red Sandstone, Tiled Hearth unlock
- `Crimson Column Base (Fortress).wiki` - 2 Red Sandstone, Grand Hearth unlock

**Impact:** Recovered 19 previously excluded items

### 6. Material Variant Naming
Automatically adds prefixes to material variant constructions.

**Prefixes:**
- "Crimson" for RedSandstone variants
- "Fair" for WhiteMarble variants

**Smart Detection:**
- Only adds prefix if not already present in display name
- Checks both internal and display names
- Placed as first word for consistency

**Examples:**
- `Advanced_Column_Stone_Base_RedSandstone` → "Crimson Column Base (Advanced)"
- `Elder_Wall_D_WhiteMarble` → "Fair Decorated Wall"

### 7. Case-Insensitive Recipe Lookup
Fixes issues where recipes use different case than constructions.

**Problem:** Recipes used `4M`, `8M` but constructions used `4m`, `8m`

**Solution:** Store both original and lowercase keys in recipe dictionary

**Impact:** Recovered 7 items (Fortress_Column 4m/8m variants)

## Technical Improvements

### Recipe Processing
- Parse `ResultConstructionHandle` for accurate recipe-to-construction mapping
- Support for case-insensitive lookups
- Fallback to recipe name when no explicit construction reference

### Exclusion System
**Excluded items (40 total):**

1. **No Recipe Data (17)** - Cannot be built by players:
   - 7 Legendary crafting stations (Great Forges)
   - 4 Item display racks
   - 6 Utility items (platforms, narrow floors, chest)

2. **Superseded by V2 Version (8)** - Older implementations:
   - 4 Floor variants
   - 2 Wall variants
   - 2 Railing variants

3. **Contains 'Broken' (3)** - Placeholder objects

4. **Display Name Starts with [ (11)** - Development items

5. **Display Name Starts with _ or * (1)** - Placeholder items:
   - `*Beorn Medium Hearth`

### Data Processing
- Comprehensive string table resolution
- Material requirement parsing with cross-references
- Unlock requirement formatting with spoiler tags
- Campaign vs Sandbox unlock differentiation
- Tag-based category extraction

## New Data Files

1. **DT_Constructions.json** - All construction definitions (854 items)
2. **DT_ConstructionRecipes.json** - Building recipes (814 recipes)
3. **DT_Entitlements.json** - DLC ownership mappings
4. **DT_RecipeBundles.json** - Recipe bundle definitions

## New Scripts

1. **generate_constructions_wiki.py** (1,017 lines)
   - Main construction wiki generator
   - DLC and Set detection
   - Recipe mapping and disambiguation

2. **generate_detailed_exclusions.py** (62 lines)
   - Generates formatted exclusion reports
   - Organizes by exclusion reason
   - Shows internal and display names

## Investigation and Bug Fixes

### Recipe Pattern Investigation
Thoroughly investigated and resolved issues with:
- Elder_Slope items (18 items) ✓
- Crude_Stairs variants (5 items) ✓
- Elder_Stairs variants (6 items) ✓
- Fortress_Stairs variants (18 items) ✓
- Fortress_Column 4m/8m (6 items) ✓
- HolidayPack items (8 items) ✓
- TreasurePile items (4 items) ✓

### Total Recovery
- **97 constructions recovered** from initial 697 to final 793
- All buildable items now included

## Output Statistics

### Wiki Files Generated
- **793 construction wiki pages**
- All pages include DLC/Set information where applicable
- Proper cross-references for prerequisites
- MediaWiki template formatting

### Example Wiki Page Structure
```mediawiki
{{Building object
 | title         = {{PAGENAME}}
 | image         = {{PAGENAME}}.webp
 | imagecaption  =
 | type          = Elder
 | subtype       = Columns
 | reqs          = 16 [[Adamant]]
}}

'''{{PAGENAME}}''' is a [[building]] object and building plan in ''[[{{topic}}]]''.

==Description==
A large two story column.

==Unlocks==
*Campaign: {{spoiler | Available from start}}
*Sandbox: {{spoiler | Build a {{LI|Grand Hearth}}}}

==Set==
This building is part of the '''Ancient Set'''.

{{Navbox building objects}}
```

## Documentation

### Generated Reports
1. **final_exclusions_detailed.txt** - Complete exclusion breakdown
2. **investigation_results.txt** - Investigation process documentation
3. **final_summary.txt** - Overall implementation summary
4. **session_summary.txt** - Session accomplishments

### Key Decisions
- Disambiguate identical display names rather than exclude
- Use entitlements file as primary DLC source
- Pattern-based Set detection for flexibility
- Exclude placeholder items (asterisk, brackets)
- Prefer V2 versions over legacy implementations

## Breaking Changes
None - This is a new generator addition

## Migration Notes
Not applicable - First release of construction generator

## Known Issues
None - All identified issues resolved

## Future Enhancements
Potential areas for expansion:
- Additional Set detection rules as game content expands
- More detailed construction placement requirements
- Building footprint information
- Material cost calculations for complex structures

## Contributors
- Claude Sonnet 4.5 (Implementation)
- User feedback and testing

---

**Version:** 0.6
**Release Date:** 2026-01-15
**Total Lines Added:** 746,088
**Files Changed:** 6 files
**Commit:** 24114a9
