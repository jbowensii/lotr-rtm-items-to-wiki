<img width="3153" height="1786" alt="image" src="https://github.com/user-attachments/assets/e9643abf-7e66-48cf-a17b-1324b18692ad" />

**Moria Wiki Generator**
A desktop application for generating MediaWiki content from LOTR: Return to Moria game data files.

**Purpose**
Extracts item, recipe, and unlock data from the game's data files and generates wiki-formatted templates ready for import into a MediaWiki site.

**Key Capabilities**
Data Import
Imports game data via UAssetGUI JSON export files
Reads from %APPDATA%\MoriaWikiGenerator\output\datajson\
Parses string tables for localized display names and descriptions
Wiki Generation (12 Generators)

Items, Consumables, Constructions
Weapons, Armor, Tools
Ores, Brews, Runes
Storage, Trade Goods
Cross-Reference (links materials across wiki files)
Generated Content Includes

Item infobox templates with stats
Crafting recipes with material links
DLC/expansion pack attribution
Unlock conditions (Campaign/Sandbox spoiler tags)
Crafting station requirements
Selection & Export

Three-column UI: Generators | Selection list | Content preview
Checkbox columns: XCL (exclude), ARC (archive), SEL (select for export)
Package button creates MediaWiki XML import files (batches of 50)
Export to Downloads\wiki import\ folder
Persistence

Selection states saved to XML config
All data stored in %APPDATA%\MoriaWikiGenerator\
Distribution
Runs as Python script or standalone Windows executable
No Python installation required for .exe version
~12 MB executable with all generators embedded
