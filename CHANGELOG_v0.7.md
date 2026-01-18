# Version 0.7 - Trader Unlocks & Construction System Completion

## Release Date
January 15, 2026

## Overview
This release completes the comprehensive unlock system for all wiki generators, with a focus on trader-purchased items from the Durin's Folk Expansion and full construction unlock coverage.

---

## Major Features

### Trader Unlock System (NEW)
- **23 Trader Items** from Durin's Folk Expansion now have complete unlock sections
- Created JSON-based unlock override system for all wiki generators:
  - `item_unlock_overrides.json` - 16 items
  - `consumable_unlock_overrides.json` - 5 consumables
  - `ore_unlock_overrides.json` - 5 ores (including Shell with trailing space)
  - `weapon_unlock_overrides.json` - 1 weapon (Drakhbarzin)

### Items Updated
- **Items (11)**: Northern Wool, Shell, Elven Silk, Elanor Seed, Niphredil Seed, Fireclay Brick, Sea Wax, Ithildin Ingot, Pumpkin Seed, Sweetroot Seed, Coastal Marble
- **Consumables (5)**: Salt-cured Fish, Saffron, Southern Oil, Whale Tallow, Thanazutsam
- **Ores (5)**: Shell, Coastal Marble, Red Sandstone, Pumice, Volcanic Glass
- **Weapons (1)**: Drakhbarzin
- **Constructions (3)**: Crimson Fire Brazier, White Tree Replica, Hanging Cookware

All trader items now show standardized format:
```
== Unlock ==
'''Campaign:''' Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|[Trader Name]}}
'''Sandbox:''' Purchase the {{LI|Durin's Folk Expansion}} Purchased from the {{LI|[Trader Name]}}
```

### Construction Unlock System (COMPLETE)
- **100% Coverage**: All 266 constructions now have unlock sections
- **Building Set Detection**: Automatically detects and applies unlocks for:
  - Coastal Marble Set (Fair prefix)
  - Red Sandstone Set (Crimson prefix)
  - Ancient Set (Ancient prefix)
  - Imladris Furnishings Set
- **DLC-Specific Unlocks**: Proper handling for:
  - Durin's Folk Expansion
  - Beorn's Lodge Pack
  - Ent-craft Pack
  - Orc Hunter Pack
  - Yule-tide Pack
- **60 Individual Overrides**: Custom unlock requirements via `construction_unlock_overrides.json`

### Verification Tools (NEW)
- `verify_trader_unlocks.py` - Validates all 23 trader items have correct unlock sections
- `verify_item_unlocks.py` - General purpose unlock verification script
- Both scripts search across all output directories with exact matching

---

## Updated Wiki Generators

### generate_items_wiki.py
- Added JSON-based unlock override loading system
- Enhanced unlock section to display for items without recipes if overrides exist
- Fixed override checking for items without recipes

### generate_consumables_wiki.py
- Added JSON-based unlock override loading system
- Fixed unlock section format from "== Unlocks ==" to "== Unlock ==" (singular)
- Changed format from spoiler bullets to bold labels for consistency

### generate_ore_wiki.py
- Added JSON-based unlock override loading system
- Fixed unlock section format from "== Unlocks ==" to "== Unlock ==" (singular)
- Changed format from spoiler bullets to bold labels for consistency

### generate_weapons_wiki.py
- Added JSON-based unlock override loading system
- Fixed unlock section format from "== Unlocks ==" to "== Unlock ==" (singular)
- Changed format from spoiler bullets to bold labels for consistency
- Merged existing hardcoded overrides with JSON file for flexibility

### generate_constructions_wiki.py
- Already had JSON loading from previous release
- Updated overrides for Crimson Fire Brazier, White Tree Replica, Hanging Cookware

---

## New Files Created

### Override Files
- `item_unlock_overrides.json` - 16 item unlock overrides
- `consumable_unlock_overrides.json` - 5 consumable unlock overrides
- `ore_unlock_overrides.json` - 5 ore unlock overrides
- `weapon_unlock_overrides.json` - 1 weapon unlock override

### Verification Scripts
- `verify_trader_unlocks.py` - Validates 23 trader items
- `verify_item_unlocks.py` - General purpose verification tool

---

## Bug Fixes
- Fixed Shell item with trailing space in display name
- Fixed DLC detection mismatch for path-based detection
- Fixed Unicode apostrophe handling in King's Brew Tank
- Fixed set detection for Ancient/Fair/Crimson building pieces
- Standardized unlock section format across all generators (singular "Unlock")

---

## Technical Improvements
- Consistent unlock section formatting across all wiki types
- JSON-based override system allows easy maintenance without code changes
- Verification scripts ensure data quality and catch regressions
- Improved file matching with exact match priority and special case handling

---

## Statistics
- **Total Wiki Files Generated**: 1,200+
- **Construction Unlock Coverage**: 266/266 (100%)
- **Trader Items Updated**: 23/23 (100%)
- **Override Files**: 4 new JSON files
- **Verification Scripts**: 2 new tools

---

## Previous Releases in v0.6 - v0.7 Development

### v0.6.1 - Construction Unlock System (January 14, 2026)
- Comprehensive construction unlock system (266 constructions)
- Building set detection and DLC-specific unlocks
- 60 individual construction overrides

### v0.6.0 - Construction Wiki Generator (January 13, 2026)
- Added constructions wiki generator
- DLC detection and Set tracking
- Recipe integration with materials and crafting time

### v0.5.1 - Additional Generators (January 12, 2026)
- Added ore and storage wiki generators
- Added brews and runes wiki generators
- Brew effects and durations

### v0.5.0 - Enhanced Consumables (January 11, 2026)
- Enhanced consumables with tag interpretation
- MediaWiki import file generator utility
- Trade goods wiki generator

---

## Commit History Since Last Release (09e6256)
```
647fb0c Add trader unlock sections for 23 Durin's Folk items
15a7674 Add comprehensive construction unlock system
7be1e33 Add Unlock section to constructions matching items format
a762a09 Fix ingot recipe matching and unlock parsing
611243d Add version 0.6 changelog
24114a9 Add constructions wiki generator with DLC and Set tracking
4f58cca Add brew effects and durations to wiki generator
3cb8ece Update brews wiki generator with recipe data and new template
1c6dc03 Add brews and runes wiki generators
013fce7 Add ore and storage wiki generators
7aba13f Release 0.5: Enhanced consumables wiki with tag interpretation system
41ceab8 Add MediaWiki import file generator utility
a17185f Add trade goods wiki generator with recipe integration
```

---

## Known Issues
- None currently identified

## Future Enhancements
- Cross-reference system for "Used In" sections
- Armor and tool wiki generators
- Automated wiki page upload system

---

## Credits
Generated with assistance from Claude Sonnet 4.5
