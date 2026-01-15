# Version 0.7 - Construction System with DLC and Set Tracking

## Major Features

### Construction Wiki Generator
- **793 buildable construction wiki pages** generated
- Complete MediaWiki template formatting with infoboxes
- Material requirements with item cross-references
- Campaign and sandbox unlock requirements
- Full description and prerequisite tracking

### DLC Detection System
- Loads DLC mappings from DT_Entitlements.json
- **132 constructions** explicitly mapped to DLCs
- Supports 6 DLC packs:
  - The Beorn's Lodge Pack
  - The Orc Hunter Pack
  - The Ent-craft Pack
  - The Rohirrim Pack
  - Yule-tide Pack
  - Durin's Folk Expansion

### Set Detection System
8 construction sets automatically detected:
- **Pattern-based:** Ancient Set (Fortress), Coastal Marble Set (Fair), Red Sandstone Set (Crimson)
- **DLC-based:** Lodge Set, Ent-craft Set, Orc Hunter Set, Rohirrim Set, Yule-tide Set

### Advanced Recipe Mapping
- Handles recipe name mismatches via ResultConstructionHandle parsing
- **Recovered 70+ items** including:
  - Beorn slate roof tiles
  - Elder slope variants
  - Fortress stairs
  - Holiday candelabras and string lights
  - Treasure pile variants

### Disambiguation System
- Creates unique wiki pages for items with identical display names
- Suffixes: (Advanced), (Fortress), (Elder), (Crude), (Sandbox), etc.
- **Recovered 19 duplicate items** that were previously excluded

### Material Variant Naming
- Automatic prefixes: "Crimson" for RedSandstone, "Fair" for WhiteMarble
- Smart detection prevents double-prefixing
- Consistent naming across all material variants

## Technical Improvements

- **Case-insensitive recipe lookup** - Fixed 4M vs 4m naming mismatches
- **Comprehensive exclusion system** - 40 legitimate exclusions properly categorized
- **Detailed exclusion reporting** - generate_detailed_exclusions.py
- **Complete category investigation** - All construction types verified

## Total Impact

- **97 constructions recovered** (from 697 to 793 wiki pages)
- **746,088 lines of code and data added**
- **All buildable items now included**

## Files Added

- generate_constructions_wiki.py (1,017 lines) - Main generator
- generate_detailed_exclusions.py (62 lines) - Exclusion reporting
- source/DT_Constructions.json - All construction definitions (854 items)
- source/DT_ConstructionRecipes.json - Building recipes (814 recipes)
- source/DT_Entitlements.json - DLC ownership mappings
- source/DT_RecipeBundles.json - Recipe bundle definitions
- CHANGELOG_0.6.md - Complete changelog documentation

## Example Wiki Output

```
==DLC and Set==
This building is part of the {{LI|Durin's Folk Expansion}}.
This building is part of the '''Ancient Set'''.
```

## Previous Releases

This release builds on:
- 0.5: Enhanced consumables wiki
- 0.4: Tools and weapons generators
- 0.3: Ores, storage, runes, and brews
- 0.2: NPC and trader systems
- 0.1: Initial wiki generation framework

---

For complete technical details, see CHANGELOG_0.6.md
