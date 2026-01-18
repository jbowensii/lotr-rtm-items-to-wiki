"""
Moria Wiki Generator
A desktop GUI application for managing wiki generation for LOTR: Return to Moria.

This application embeds all wiki generator functionality and does not require
external script files. Configuration and data are stored in %APPDATA%\\MoriaWikiGenerator.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import subprocess
import shutil
import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom


# =============================================================================
# EMBEDDED GENERATOR FUNCTIONS
# =============================================================================

def get_generator_function(gen_type):
    """Get the generator function for the given type."""
    generators = {
        "items": generate_items_wiki,
        "consumables": generate_consumables_wiki,
        "constructions": generate_constructions_wiki,
        "weapons": generate_weapons_wiki,
        "armor": generate_armor_wiki,
        "tools": generate_tools_wiki,
        "ores": generate_ores_wiki,
        "brews": generate_brews_wiki,
        "runes": generate_runes_wiki,
        "storage": generate_storage_wiki,
        "tradegoods": generate_tradegoods_wiki,
        "crossreference": generate_crossreference_wiki,
    }
    return generators.get(gen_type)


def verify_trader_unlocks(output_path, log_callback):
    """Verify that all trader items have correct unlock sections."""
    log_callback("Verifying trader unlock sections...")

    # List of items that should have trader unlocks
    trader_items = [
        "Northern Wool", "Shell", "Coastal Marble", "Elven Silk",
        "Elanor Seed", "Niphredil Seed", "Fireclay Brick", "Sea Wax",
        "Ithildin Ingot", "Pumpkin Seed", "Sweetroot Seed",
        "Salt-cured Fish", "Saffron", "Southern Oil", "Whale Tallow",
        "Thanazutsam", "Pumice", "Volcanic Glass", "Red Sandstone",
        "Drakhbarzin", "Crimson Fire Brazier", "White Tree Replica",
        "Hanging Cookware"
    ]

    found_count = 0
    missing_count = 0

    # Search through output directories
    for root, dirs, files in os.walk(output_path):
        for filename in files:
            if filename.endswith('.wiki'):
                item_name = filename[:-5]  # Remove .wiki extension
                if item_name in trader_items or item_name.rstrip() in trader_items:
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if "== Unlock ==" in content and "Trader" in content:
                        found_count += 1
                        log_callback(f"  OK: {item_name}")
                    else:
                        missing_count += 1
                        log_callback(f"  MISSING: {item_name}")

    log_callback(f"\nResults: {found_count} found, {missing_count} missing")
    return missing_count == 0


# =============================================================================
# SHARED GENERATOR UTILITIES
# =============================================================================

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

# Mapping from CraftingStation keys to Constructions string keys
STATION_KEY_MAP = {
    "CraftingStation_BasicForge": "Constructions.BasicForge",
    "CraftingStation_AdvancedForge": "Constructions.ForgeAdvanced",
    "CraftingStation_FloodedForge": "Constructions.FloodedForge",
    "CraftingStation_DurinForge": "Constructions.DurinForge",
    "CraftingStation_MithrilForge": "Constructions.MithrilForge",
    "CraftingStation_NogrodForge": "Constructions.NogrodForge",
    "CraftingStation_LegendayElvishForge": "Constructions.LegendayElvishForge",
    "CraftingStation_ForgeUpgrade": "Constructions.ForgeUpgrade",
    "CraftingStation_BasicFurnace": "Constructions.BasicFurnace",
    "CraftingStation_AdvancedFurnace": "Constructions.FurnaceAdvanced",
    "CraftingStation_FloodedFurnace": "Constructions.FloodedFurnace.Name",
    "CraftingStation_LegendaryDurinsFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_LegendaryFloodedFurnace": "Constructions.FloodedFurnace.Name",
    "CraftingStation_LegendaryMithrilFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_LegendaryNogrodFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_LegendayElvishFurnace": "Constructions.LegendayElvishFurnace",
    "CraftingStation_FurnaceUpgrade": "Constructions.ForgeUpgrade",
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

# Material name mappings for special cases
MATERIAL_KEY_MAP = {
    "Item.Scrap": "Metal Fragments",
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


def load_all_string_tables(strings_dir, log_callback=None):
    """Load all string table files from the strings directory."""
    combined_map = {}
    if not os.path.exists(strings_dir):
        return combined_map

    for filename in os.listdir(strings_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(strings_dir, filename)
            if log_callback:
                log_callback(f"  Loading {filename}...")
            table_map = load_string_table(filepath)
            if log_callback:
                log_callback(f"    Found {len(table_map)} strings")
            combined_map.update(table_map)
    return combined_map


def load_data_table(filepath):
    """Load a data table JSON file and return the list of entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = []
    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if isinstance(table, dict) and "Data" in table:
            entries.extend(table.get("Data", []))

    return entries


def load_recipe_data(filepath):
    """Load recipe data and return a dictionary keyed by normalized item name."""
    recipes = {}
    if not os.path.exists(filepath):
        return recipes

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    exports = data.get("Exports", [])
    for export in exports:
        table = export.get("Table", {})
        if isinstance(table, dict) and "Data" in table:
            recipe_entries = table.get("Data", [])
            for recipe in recipe_entries:
                name = recipe.get("Name")
                if name:
                    normalized = name.lower().replace("_", "").replace(" ", "").replace("-", "")
                    recipes[normalized] = recipe

    return recipes


def get_property_value(properties, prop_name):
    """Extract a property value from the list of properties."""
    for prop in properties:
        if prop.get("Name") == prop_name:
            return prop.get("Value")
    return None


def detect_dlc(actor_path, icon_path):
    """Detect DLC information from actor or icon path."""
    paths_to_check = [actor_path or "", icon_path or ""]
    for path in paths_to_check:
        if "/DLC/" in path:
            parts = path.split("/DLC/")
            if len(parts) > 1:
                dlc_name = parts[1].split("/")[0]
                dlc_title = DLC_TITLE_MAP.get(dlc_name, f"{{{{LI|{dlc_name}}}}}")
                return True, dlc_title, dlc_name
    return False, None, None


def get_material_display_name(material_key, string_map):
    """Get display name for a crafting material."""
    if material_key in MATERIAL_KEY_MAP:
        return MATERIAL_KEY_MAP[material_key]

    lookup_patterns = [
        f"Items.Items.{material_key}.Name",
        f"Items.Ores.{material_key}.Name",
        f"Consumable.{material_key}.Name",
        material_key,
    ]

    for pattern in lookup_patterns:
        display_name = string_map.get(pattern)
        if display_name:
            return display_name

    return material_key


def get_station_display_name(station_key, string_map):
    """Get display name for a crafting station."""
    mapped_key = STATION_KEY_MAP.get(station_key, station_key)
    return string_map.get(mapped_key, station_key)


def load_unlock_overrides(override_file):
    """Load unlock overrides from a JSON file."""
    if not os.path.exists(override_file):
        return {}, {}

    with open(override_file, 'r', encoding='utf-8') as f:
        overrides = json.load(f)

    campaign_overrides = {}
    sandbox_overrides = {}
    for item_name, unlock_data in overrides.items():
        if "campaign" in unlock_data:
            campaign_overrides[item_name] = unlock_data["campaign"]
        if "sandbox" in unlock_data:
            sandbox_overrides[item_name] = unlock_data["sandbox"]

    return campaign_overrides, sandbox_overrides


# =============================================================================
# STANDALONE SCRIPT RUNNER
# =============================================================================

def _get_script_dir():
    """Get the directory containing the standalone generator scripts."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - check PyInstaller's temp directory first
        # For onefile builds, files are extracted to _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        # Scripts are in the 'generators' subdirectory within the bundle
        script_dir = os.path.join(base_path, 'generators')
        if not os.path.exists(script_dir):
            # Fallback to executable directory (for onedir builds or if placed alongside exe)
            script_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
    return script_dir


def _run_standalone_script(script_name, log_callback):
    """Run a standalone generator script and capture its output."""
    # Check if running as frozen executable
    if getattr(sys, 'frozen', False):
        # When frozen, import and run the generator module directly
        return _run_embedded_generator(script_name, log_callback)

    # Running as normal Python script - use subprocess
    script_dir = _get_script_dir()
    script_path = os.path.join(script_dir, script_name)

    if not os.path.exists(script_path):
        log_callback(f"Error: Script not found: {script_path}")
        return False

    log_callback(f"Running {script_name}...")

    try:
        # Run the script and capture output in real-time
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=script_dir,
            bufsize=1
        )

        # Read output line by line
        for line in process.stdout:
            log_callback(line.rstrip())

        process.wait()

        if process.returncode == 0:
            log_callback(f"  {script_name} completed successfully")
            return True
        else:
            log_callback(f"  {script_name} failed with return code {process.returncode}")
            return False

    except Exception as e:
        log_callback(f"Error running {script_name}: {str(e)}")
        return False


def _run_embedded_generator(script_name, log_callback):
    """Import and run an embedded generator module when running as frozen executable."""
    import importlib
    import io
    from contextlib import redirect_stdout

    # Convert script name to module name (e.g., "generate_armor_wiki.py" -> "generate_armor_wiki")
    module_name = script_name.replace('.py', '')

    log_callback(f"Running {script_name} (embedded)...")

    try:
        # Import the embedded module
        module = importlib.import_module(module_name)

        # Capture stdout to display in log
        output_buffer = io.StringIO()

        # Run the module's main function with captured output
        with redirect_stdout(output_buffer):
            if hasattr(module, 'main'):
                module.main()
            else:
                log_callback(f"Warning: {module_name} has no main() function")
                return False

        # Log the captured output
        output = output_buffer.getvalue()
        for line in output.splitlines():
            log_callback(line)

        log_callback(f"  {script_name} completed successfully")
        return True

    except Exception as e:
        log_callback(f"Error running {script_name}: {str(e)}")
        import traceback
        log_callback(traceback.format_exc())
        return False


# =============================================================================
# GENERATOR FUNCTIONS - Call standalone scripts
# =============================================================================

def generate_items_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for items using standalone script."""
    return _run_standalone_script("generate_items_wiki.py", log_callback)


def generate_consumables_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for consumables using standalone script."""
    return _run_standalone_script("generate_consumables_wiki.py", log_callback)


def generate_constructions_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for constructions using standalone script."""
    return _run_standalone_script("generate_constructions_wiki.py", log_callback)


def generate_weapons_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for weapons using standalone script."""
    return _run_standalone_script("generate_weapons_wiki.py", log_callback)


def generate_armor_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for armor using standalone script."""
    return _run_standalone_script("generate_armor_wiki.py", log_callback)


def generate_tools_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for tools using standalone script."""
    return _run_standalone_script("generate_tools_wiki.py", log_callback)


def generate_ores_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for ores using standalone script."""
    return _run_standalone_script("generate_ore_wiki.py", log_callback)


def generate_brews_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for brews using standalone script."""
    return _run_standalone_script("generate_brews_wiki.py", log_callback)


def generate_runes_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for runes using standalone script."""
    return _run_standalone_script("generate_runes_wiki.py", log_callback)


def generate_storage_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for storage using standalone script."""
    return _run_standalone_script("generate_storage_wiki.py", log_callback)


def generate_tradegoods_wiki(source_path, output_path, log_callback):
    """Generate wiki pages for trade goods using standalone script."""
    return _run_standalone_script("generate_tradegoods_wiki.py", log_callback)


def generate_crossreference_wiki(source_path, output_path, log_callback):
    """Generate cross-reference data for wiki pages using standalone script."""
    return _run_standalone_script("generate_crossreference_wiki.py", log_callback)

# Application constants
APP_TITLE = "Moria Wiki Generator"
APP_VERSION = "0.9"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

# Configuration constants
CONFIG_DIR_NAME = "MoriaWikiGenerator"
CONFIG_FILE_NAME = "config.xml"
SELECTION_STATES_FILE = "selection_states.xml"

# Known game installation paths
GAME_PATHS = {
    "Steam": r"C:\Program Files (x86)\Steam\steamapps\common\The Lord of the Rings Return to Moria™",
    "Epic": r"C:\Program Files\Epic Games\ReturnToMoria",
}


def detect_windows_dark_mode():
    """Detect if Windows is using dark mode. Returns True for dark mode, False for light mode."""
    try:
        import winreg
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return value == 0  # 0 = dark mode, 1 = light mode
    except Exception:
        return False  # Default to light mode if detection fails


def get_default_source_path():
    """Get default source data directory in %APPDATA%."""
    return os.path.join(get_config_dir(), "source")


def get_default_output_path():
    """Get default output directory in %APPDATA%."""
    return os.path.join(get_config_dir(), "output")


def get_default_utilities_path():
    """Get default utilities directory in %APPDATA%."""
    return os.path.join(get_config_dir(), "utilities")


def get_config_dir():
    """Get the configuration directory path in %APPDATA%."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        # Fallback for non-Windows systems
        appdata = os.path.expanduser("~")
    return os.path.join(appdata, CONFIG_DIR_NAME)


def get_config_path():
    """Get the full path to the configuration file."""
    return os.path.join(get_config_dir(), CONFIG_FILE_NAME)


class Configuration:
    """Handles loading and saving application configuration as XML."""

    DEFAULT_CONFIG = {
        "source_path": "",
        "output_path": "",
        "utilities_path": "",
        "game_install_type": "",  # Steam, Epic, or Custom
        "game_install_path": "",
        "theme_mode": "auto",  # auto, light, or dark
        "first_run_complete": "false",
        "window_width": str(WINDOW_WIDTH),
        "window_height": str(WINDOW_HEIGHT),
        "window_x": "",
        "window_y": "",
    }

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = get_config_path()
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure the configuration directory and default subdirectories exist."""
        config_dir = get_config_dir()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # Create default subdirectories
        for subdir in ["source", "output", "utilities"]:
            subdir_path = os.path.join(config_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)

    def load(self):
        """Load configuration from XML file."""
        if not os.path.exists(self.config_path):
            return False

        try:
            tree = ET.parse(self.config_path)
            root = tree.getroot()

            for element in root:
                if element.tag in self.config:
                    self.config[element.tag] = element.text or ""

            return True
        except ET.ParseError:
            return False

    def save(self):
        """Save configuration to XML file."""
        root = ET.Element("MoriaWikiGeneratorConfig")
        root.set("version", APP_VERSION)

        for key, value in self.config.items():
            element = ET.SubElement(root, key)
            element.text = value

        # Pretty print the XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        # Remove the XML declaration line that minidom adds
        lines = xml_str.split('\n')
        xml_str = '\n'.join(lines[1:])

        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(xml_str)

    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = str(value)

    def is_first_run(self):
        """Check if this is the first run."""
        return self.config.get("first_run_complete", "false").lower() != "true"

    def mark_first_run_complete(self):
        """Mark the first run setup as complete."""
        self.config["first_run_complete"] = "true"
        self.save()

    def get_theme_mode(self):
        """Get the current theme mode setting."""
        return self.config.get("theme_mode", "auto")

    def is_dark_mode(self):
        """Determine if dark mode should be used based on settings."""
        theme_mode = self.get_theme_mode()
        if theme_mode == "dark":
            return True
        elif theme_mode == "light":
            return False
        else:  # auto
            return detect_windows_dark_mode()

    def get_source_path(self):
        """Get source path, using default if not set."""
        path = self.config.get("source_path", "")
        return path if path else get_default_source_path()

    def get_output_path(self):
        """Get output path, using default if not set."""
        path = self.config.get("output_path", "")
        return path if path else get_default_output_path()

    def get_utilities_path(self):
        """Get utilities path, using default if not set."""
        path = self.config.get("utilities_path", "")
        return path if path else get_default_utilities_path()


class SetupWizard:
    """First-run setup wizard dialog."""

    def __init__(self, parent, config, is_first_run=True):
        self.parent = parent
        self.config = config
        self.result = False
        self.is_first_run = is_first_run

        # Create the wizard dialog
        self.dialog = tk.Toplevel(parent)
        title = f"{APP_TITLE} - Setup" if is_first_run else f"{APP_TITLE} - Settings"
        self.dialog.title(title)
        self.dialog.geometry("650x650")
        self.dialog.resizable(False, False)

        # Only make transient if parent is visible (not on first run when parent is withdrawn)
        if not is_first_run:
            self.dialog.transient(parent)

        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 650) // 2
        y = (self.dialog.winfo_screenheight() - 650) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Prevent closing without completing setup on first run
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._create_ui()

        # Auto-detect game installation on first run
        if is_first_run:
            self._auto_detect_game()

        # Ensure the dialog is visible and focused
        self.dialog.lift()
        self.dialog.focus_force()

    def _create_ui(self):
        """Create the setup wizard UI."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_text = f"Welcome to {APP_TITLE}" if self.is_first_run else "Settings"
        title_label = ttk.Label(
            main_frame,
            text=title_text,
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(0, 5))

        # Subtitle
        if self.is_first_run:
            subtitle_label = ttk.Label(
                main_frame,
                text="Please configure the required paths to get started.",
                font=("Segoe UI", 10)
            )
            subtitle_label.pack(pady=(0, 15))

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 15))

        # Game Installation tab
        game_frame = ttk.Frame(notebook, padding="10")
        notebook.add(game_frame, text="Game Installation")
        self._create_game_tab(game_frame)

        # Project Paths tab
        paths_frame = ttk.Frame(notebook, padding="10")
        notebook.add(paths_frame, text="Project Paths")
        self._create_paths_tab(paths_frame)

        # UI tab
        ui_frame = ttk.Frame(notebook, padding="10")
        notebook.add(ui_frame, text="UI")
        self._create_ui_tab(ui_frame)

        # Info label
        info_label = ttk.Label(
            main_frame,
            text=f"Configuration saved to: {get_config_path()}",
            font=("Segoe UI", 8),
            foreground="gray",
            justify="center"
        )
        info_label.pack(pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=15
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Save & Continue" if self.is_first_run else "Save",
            command=self._on_save,
            width=15
        ).pack(side="right")

    def _create_game_tab(self, parent):
        """Create the game installation tab."""
        # Game installation type
        type_frame = ttk.LabelFrame(parent, text="Game Installation Type", padding="10")
        type_frame.pack(fill="x", pady=(0, 15))

        self.game_type_var = tk.StringVar(value=self.config.get("game_install_type", ""))

        # Detect available installations
        steam_available = os.path.exists(GAME_PATHS["Steam"])
        epic_available = os.path.exists(GAME_PATHS["Epic"])

        # Steam option
        steam_text = "Steam"
        if steam_available:
            steam_text += " (Detected)"
        steam_rb = ttk.Radiobutton(
            type_frame,
            text=steam_text,
            variable=self.game_type_var,
            value="Steam",
            command=self._on_game_type_changed
        )
        steam_rb.grid(row=0, column=0, sticky="w", pady=2)
        if not steam_available:
            steam_rb.configure(state="disabled")

        # Epic option
        epic_text = "Epic Games"
        if epic_available:
            epic_text += " (Detected)"
        epic_rb = ttk.Radiobutton(
            type_frame,
            text=epic_text,
            variable=self.game_type_var,
            value="Epic",
            command=self._on_game_type_changed
        )
        epic_rb.grid(row=1, column=0, sticky="w", pady=2)
        if not epic_available:
            epic_rb.configure(state="disabled")

        # Custom option
        ttk.Radiobutton(
            type_frame,
            text="Custom Location",
            variable=self.game_type_var,
            value="Custom",
            command=self._on_game_type_changed
        ).grid(row=2, column=0, sticky="w", pady=2)

        # Game path
        path_frame = ttk.LabelFrame(parent, text="Game Installation Path", padding="10")
        path_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            path_frame,
            text="Path to the game installation folder:",
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.game_path_var = tk.StringVar(value=self.config.get("game_install_path", ""))
        self.game_path_entry = ttk.Entry(path_frame, textvariable=self.game_path_var, width=55)
        self.game_path_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        self.game_browse_btn = ttk.Button(
            path_frame,
            text="Browse...",
            command=lambda: self._browse_directory(self.game_path_var)
        )
        self.game_browse_btn.grid(row=1, column=1)

        path_frame.columnconfigure(0, weight=1)

        # Status indicator
        self.game_status_var = tk.StringVar(value="")
        self.game_status_label = ttk.Label(
            path_frame,
            textvariable=self.game_status_var,
            font=("Segoe UI", 9)
        )
        self.game_status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Update UI state based on current selection
        self._on_game_type_changed()

    def _create_paths_tab(self, parent):
        """Create the project paths tab."""
        # Info about default paths
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill="x", pady=(0, 10))

        default_path = get_config_dir()
        ttk.Label(
            info_frame,
            text=f"Default location: {default_path}",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(anchor="w")

        # Source Path
        src_frame = ttk.LabelFrame(parent, text="Source Data Directory", padding="10")
        src_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            src_frame,
            text="Directory containing extracted game data files (DT_*.json, strings/):",
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Use default path if not set
        source_default = self.config.get("source_path", "") or get_default_source_path()
        self.source_path_var = tk.StringVar(value=source_default)
        ttk.Entry(src_frame, textvariable=self.source_path_var, width=55).grid(
            row=1, column=0, sticky="ew", padx=(0, 10)
        )
        ttk.Button(
            src_frame,
            text="Browse...",
            command=lambda: self._browse_directory(self.source_path_var)
        ).grid(row=1, column=1)
        src_frame.columnconfigure(0, weight=1)

        # Output Path
        out_frame = ttk.LabelFrame(parent, text="Output Directory", padding="10")
        out_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            out_frame,
            text="Directory where generated wiki files will be saved:",
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Use default path if not set
        output_default = self.config.get("output_path", "") or get_default_output_path()
        self.output_path_var = tk.StringVar(value=output_default)
        ttk.Entry(out_frame, textvariable=self.output_path_var, width=55).grid(
            row=1, column=0, sticky="ew", padx=(0, 10)
        )
        ttk.Button(
            out_frame,
            text="Browse...",
            command=lambda: self._browse_directory(self.output_path_var)
        ).grid(row=1, column=1)
        out_frame.columnconfigure(0, weight=1)

        # Utilities Path
        util_frame = ttk.LabelFrame(parent, text="Utilities Directory", padding="10")
        util_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            util_frame,
            text="Directory for tools like retoc.exe:",
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Use default path if not set
        utilities_default = self.config.get("utilities_path", "") or get_default_utilities_path()
        self.utilities_path_var = tk.StringVar(value=utilities_default)
        ttk.Entry(util_frame, textvariable=self.utilities_path_var, width=55).grid(
            row=1, column=0, sticky="ew", padx=(0, 10)
        )
        ttk.Button(
            util_frame,
            text="Browse...",
            command=lambda: self._browse_directory(self.utilities_path_var)
        ).grid(row=1, column=1)
        util_frame.columnconfigure(0, weight=1)

        # Reset to defaults button
        reset_frame = ttk.Frame(parent)
        reset_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(
            reset_frame,
            text="Reset to Default Paths",
            command=self._reset_paths_to_defaults
        ).pack()

    def _reset_paths_to_defaults(self):
        """Reset all paths to their default values."""
        self.source_path_var.set(get_default_source_path())
        self.output_path_var.set(get_default_output_path())
        self.utilities_path_var.set(get_default_utilities_path())

    def _create_ui_tab(self, parent):
        """Create the UI settings tab."""
        # Theme settings
        theme_frame = ttk.LabelFrame(parent, text="Appearance", padding="10")
        theme_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            theme_frame,
            text="Theme Mode:",
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.theme_mode_var = tk.StringVar(value=self.config.get("theme_mode", "auto"))

        theme_options_frame = ttk.Frame(theme_frame)
        theme_options_frame.grid(row=1, column=0, sticky="w")

        # Auto option
        auto_text = "Auto (Match OS)"
        if detect_windows_dark_mode():
            auto_text += " - Currently Dark"
        else:
            auto_text += " - Currently Light"
        ttk.Radiobutton(
            theme_options_frame,
            text=auto_text,
            variable=self.theme_mode_var,
            value="auto"
        ).pack(anchor="w", pady=2)

        # Light option
        ttk.Radiobutton(
            theme_options_frame,
            text="Light",
            variable=self.theme_mode_var,
            value="light"
        ).pack(anchor="w", pady=2)

        # Dark option
        ttk.Radiobutton(
            theme_options_frame,
            text="Dark",
            variable=self.theme_mode_var,
            value="dark"
        ).pack(anchor="w", pady=2)

        ttk.Label(
            theme_frame,
            text="Note: Theme changes take effect after restarting the application.",
            font=("Segoe UI", 8),
            foreground="gray"
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

    def _on_game_type_changed(self):
        """Handle game type selection change."""
        game_type = self.game_type_var.get()

        if game_type == "Steam":
            self.game_path_var.set(GAME_PATHS["Steam"])
            self.game_path_entry.configure(state="disabled")
            self.game_browse_btn.configure(state="disabled")
        elif game_type == "Epic":
            self.game_path_var.set(GAME_PATHS["Epic"])
            self.game_path_entry.configure(state="disabled")
            self.game_browse_btn.configure(state="disabled")
        elif game_type == "Custom":
            self.game_path_entry.configure(state="normal")
            self.game_browse_btn.configure(state="normal")
        else:
            self.game_path_entry.configure(state="normal")
            self.game_browse_btn.configure(state="normal")

        self._update_game_status()

    def _update_game_status(self):
        """Update the game installation status indicator."""
        game_path = self.game_path_var.get()

        if not game_path:
            self.game_status_var.set("")
            self.game_status_label.configure(foreground="gray")
            return

        if os.path.exists(game_path):
            # Check for expected game files
            pak_path = os.path.join(game_path, "Moria", "Content", "Paks")
            if os.path.exists(pak_path):
                self.game_status_var.set("✓ Valid game installation detected")
                self.game_status_label.configure(foreground="green")
            else:
                self.game_status_var.set("⚠ Directory exists but game files not found")
                self.game_status_label.configure(foreground="orange")
        else:
            self.game_status_var.set("✗ Directory does not exist")
            self.game_status_label.configure(foreground="red")

    def _auto_detect_game(self):
        """Auto-detect game installation on first run."""
        # Check Steam first, then Epic
        if os.path.exists(GAME_PATHS["Steam"]):
            self.game_type_var.set("Steam")
            self.game_path_var.set(GAME_PATHS["Steam"])
        elif os.path.exists(GAME_PATHS["Epic"]):
            self.game_type_var.set("Epic")
            self.game_path_var.set(GAME_PATHS["Epic"])

        self._on_game_type_changed()

    def _browse_directory(self, var):
        """Open directory browser dialog."""
        initial_dir = var.get() or os.getcwd()
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()

        directory = filedialog.askdirectory(
            parent=self.dialog,
            initialdir=initial_dir,
            title="Select Directory"
        )
        if directory:
            var.set(directory)
            # Update status if it's the game path
            if var == self.game_path_var:
                self._update_game_status()

    def _validate(self):
        """Validate the configuration."""
        errors = []

        # Validate game installation
        game_type = self.game_type_var.get()
        game_path = self.game_path_var.get().strip()

        if not game_type:
            errors.append("Please select a game installation type")
        elif not game_path:
            errors.append("Game installation path is required")
        elif not os.path.isdir(game_path):
            errors.append("Game installation path does not exist")

        # Validate paths
        source_path = self.source_path_var.get().strip()
        output_path = self.output_path_var.get().strip()
        utilities_path = self.utilities_path_var.get().strip()

        if not source_path:
            errors.append("Source data directory is required")

        if not output_path:
            errors.append("Output directory is required")

        if not utilities_path:
            errors.append("Utilities directory is required")

        if errors:
            messagebox.showerror(
                "Validation Error",
                "Please fix the following errors:\n\n" + "\n".join(f"• {e}" for e in errors),
                parent=self.dialog
            )
            return False

        # Create directories if they don't exist
        for dir_path, dir_name in [(source_path, "source"), (output_path, "output"), (utilities_path, "utilities")]:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path)
                except OSError as e:
                    messagebox.showerror(
                        "Error",
                        f"Could not create {dir_name} directory:\n{e}",
                        parent=self.dialog
                    )
                    return False

        return True

    def _on_save(self):
        """Save configuration and close dialog."""
        if not self._validate():
            return

        self.config.set("game_install_type", self.game_type_var.get())
        self.config.set("game_install_path", self.game_path_var.get().strip())
        self.config.set("source_path", self.source_path_var.get().strip())
        self.config.set("output_path", self.output_path_var.get().strip())
        self.config.set("utilities_path", self.utilities_path_var.get().strip())
        self.config.set("theme_mode", self.theme_mode_var.get())

        if self.is_first_run:
            self.config.mark_first_run_complete()
        else:
            self.config.save()

        self.result = True
        self.dialog.destroy()

    def _on_cancel(self):
        """Handle cancel/close."""
        if self.is_first_run:
            if messagebox.askyesno(
                "Exit Setup",
                "Setup is required to use the application.\nAre you sure you want to exit?",
                parent=self.dialog
            ):
                self.result = False
                self.dialog.destroy()
        else:
            self.result = False
            self.dialog.destroy()

    def show(self):
        """Show the wizard and wait for it to close."""
        self.dialog.wait_window()
        return self.result


class WikiGeneratorApp:
    """Main application class for the Wiki Generator UI."""

    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")

        # Restore window geometry
        width = int(config.get("window_width", WINDOW_WIDTH))
        height = int(config.get("window_height", WINDOW_HEIGHT))
        self.root.geometry(f"{width}x{height}")

        # Restore window position if saved
        x = config.get("window_x", "")
        y = config.get("window_y", "")
        if x and y:
            self.root.geometry(f"+{x}+{y}")

        self.root.minsize(800, 600)

        # Save geometry on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Track running processes
        self.running_process = None

        # Set up the UI
        self.setup_ui()

    def _on_close(self):
        """Handle window close - save geometry and exit."""
        # Save window geometry
        self.config.set("window_width", self.root.winfo_width())
        self.config.set("window_height", self.root.winfo_height())
        self.config.set("window_x", self.root.winfo_x())
        self.config.set("window_y", self.root.winfo_y())
        self.config.save()
        self.root.destroy()

    def setup_ui(self):
        """Set up the main UI components."""
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=0)  # Button column - fixed width
        main_frame.columnconfigure(1, weight=1)  # Selection pane - expandable
        main_frame.columnconfigure(2, weight=1)  # Contents pane - same width as Selection
        main_frame.rowconfigure(1, weight=1)     # Main content area
        main_frame.rowconfigure(2, weight=0)     # Output area - fixed height

        # Header section (spans all columns)
        self.create_header(main_frame)

        # Left column - Buttons
        self.create_button_column(main_frame)

        # Middle pane - Selection
        self.create_selection_pane(main_frame)

        # Right pane - Contents
        self.create_contents_pane(main_frame)

        # Output/Log section (spans all columns, at bottom)
        self.create_output_section(main_frame)

        # Status bar
        self.create_status_bar(main_frame)

    def create_header(self, parent):
        """Create the header section with title and settings gear."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        # Title and version
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky="w")

        # Load and display application icon
        icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        app_icon_path = os.path.join(icons_dir, "Application Icon.png")
        if os.path.exists(app_icon_path):
            self.app_icon_image = tk.PhotoImage(file=app_icon_path)
            # Subsample to get approximately 64x64 (the icon is larger)
            # PhotoImage subsample reduces by factor, so we check the size
            width = self.app_icon_image.width()
            height = self.app_icon_image.height()
            # Target size is 64 pixels
            factor = max(1, min(width, height) // 64)
            if factor > 1:
                self.app_icon_image = self.app_icon_image.subsample(factor, factor)
            icon_label = ttk.Label(title_frame, image=self.app_icon_image)
            icon_label.pack(side="left", padx=(0, 10))

        title_label = ttk.Label(
            title_frame,
            text=APP_TITLE,
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(side="left")

        version_label = ttk.Label(
            title_frame,
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 10)
        )
        version_label.pack(side="left", padx=(10, 0))

        # Settings gear button on the right
        # Using Unicode gear character: ⚙ (U+2699)
        settings_btn = ttk.Button(
            header_frame,
            text="⚙",
            command=self.show_settings,
            width=3
        )
        settings_btn.grid(row=0, column=1, sticky="e")

        # Add tooltip-like behavior
        self._create_tooltip(settings_btn, "Settings")

    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget, positioned above the cursor."""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            # Position above the cursor (offset by ~30 pixels up)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-30}")

            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1,
                           font=("Segoe UI", 9))
            label.pack()

            widget.tooltip = tooltip

            def hide_tooltip(e):
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                    del widget.tooltip

            widget.bind("<Leave>", hide_tooltip)
            tooltip.bind("<Leave>", hide_tooltip)

        widget.bind("<Enter>", show_tooltip)

    def _add_tooltip(self, widget, text):
        """Add tooltip to a widget using additional bindings (doesn't overwrite Leave)."""
        def show_tooltip(event):
            if hasattr(widget, '_tooltip_window'):
                return  # Already showing
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            # Position above the cursor
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-30}")
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1,
                           font=("Segoe UI", 9))
            label.pack()
            widget._tooltip_window = tooltip

        def hide_tooltip(event):
            if hasattr(widget, '_tooltip_window'):
                widget._tooltip_window.destroy()
                del widget._tooltip_window

        widget.bind("<Enter>", show_tooltip, add="+")
        widget.bind("<Leave>", hide_tooltip, add="+")

    def create_button_column(self, parent):
        """Create the left column with image buttons in a 2-column grid layout."""
        # Button column frame
        btn_frame = ttk.Frame(parent, padding="5")
        btn_frame.grid(row=1, column=0, sticky="ns", padx=(0, 10))

        # Store references to PhotoImage objects to prevent garbage collection
        self.button_images = {}

        # Icons directory
        icons_dir = os.path.join(os.path.dirname(__file__), "icons")

        # Target icon size
        target_size = 48

        def load_icon(name):
            """Load an icon image at 48x48, return None if not found."""
            # Map button names to icon filenames
            icon_map = {
                "Consumables": "Lembas.png",  # Use Lembas icon for Consumables
            }
            filename = icon_map.get(name, f"{name}.png")
            icon_path = os.path.join(icons_dir, filename)
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.button_images[name] = img  # Keep reference
                return img
            return None

        def create_cancel_icon():
            """Create a red X cancel icon programmatically."""
            size = target_size
            img = tk.PhotoImage(width=size, height=size)
            # Create red X on transparent background
            red = "#cc3333"
            dark_red = "#991111"
            line_width = 8
            for i in range(size):
                for j in range(size):
                    # Check if pixel is on one of the diagonal lines
                    on_diag1 = abs(i - j) < line_width
                    on_diag2 = abs(i - (size - 1 - j)) < line_width
                    # Add margin from edges
                    margin = 8
                    if (on_diag1 or on_diag2) and margin < i < size - margin and margin < j < size - margin:
                        img.put(red, (i, j))
            self.button_images["Cancel"] = img
            return img

        def create_tooltip(widget, text):
            """Create a tooltip for a widget, positioned above the cursor."""
            def show_tooltip(event):
                tooltip = tk.Toplevel(widget)
                tooltip.wm_overrideredirect(True)
                # Position above the cursor (offset by ~30 pixels up)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-30}")
                label = tk.Label(tooltip, text=text, background="#ffffe0",
                               relief="solid", borderwidth=1, font=("Segoe UI", 9))
                label.pack()
                widget._tooltip = tooltip

            def hide_tooltip(event):
                if hasattr(widget, '_tooltip'):
                    widget._tooltip.destroy()
                    del widget._tooltip

            widget.bind('<Enter>', show_tooltip)
            widget.bind('<Leave>', hide_tooltip)

        row = 0
        col = 0
        buttons_per_row = 2

        # Import Game Files button
        img = load_icon("Import Game Files")
        self.import_btn = ttk.Button(
            btn_frame,
            image=img,
            command=self.run_import_game_files,
            style="Icon.TButton"
        )
        self.import_btn.grid(row=row, column=col, pady=2, padx=2)
        create_tooltip(self.import_btn, "Import Game Files")
        col += 1

        # Run All Generators button
        img = load_icon("Run All Generators")
        self.run_all_btn = ttk.Button(
            btn_frame,
            image=img,
            command=self.run_all_generators,
            style="Icon.TButton"
        )
        self.run_all_btn.grid(row=row, column=col, pady=2, padx=2)
        create_tooltip(self.run_all_btn, "Run All Generators")
        col += 1

        # Move to next row
        row += 1
        col = 0

        # Separator before wiki generators
        ttk.Separator(btn_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=buttons_per_row, sticky="ew", pady=10
        )
        row += 1

        # Wiki Generators label
        gen_label = ttk.Label(btn_frame, text="WIKI GENERATORS", font=("Segoe UI", 9, "bold"))
        gen_label.grid(row=row, column=0, columnspan=buttons_per_row, pady=(0, 5), sticky="w")
        row += 1

        # Define generators with their function names (alphabetical order, Cross-Reference moved out)
        self.generators = [
            ("Armor", "armor"),
            ("Brews", "brews"),
            ("Constructions", "constructions"),
            ("Consumables", "consumables"),
            ("Items", "items"),
            ("Ores", "ores"),
            ("Runes", "runes"),
            ("Storage", "storage"),
            ("Tools", "tools"),
            ("Trade Goods", "tradegoods"),
            ("Weapons", "weapons"),
        ]

        # Create generator buttons in a 2-column grid
        self.generator_buttons = {}
        col = 0
        for name, gen_type in self.generators:
            img = load_icon(name)
            btn = ttk.Button(
                btn_frame,
                image=img,
                command=lambda t=gen_type, n=name: self.run_generator(t, n),
                style="Icon.TButton"
            )
            btn.grid(row=row, column=col, pady=2, padx=2)
            create_tooltip(btn, name)
            self.generator_buttons[gen_type] = btn
            col += 1
            if col >= buttons_per_row:
                col = 0
                row += 1

        # If we didn't finish a complete row, move to next row
        if col != 0:
            row += 1
            col = 0

        # Separator before utility buttons
        ttk.Separator(btn_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=buttons_per_row, sticky="ew", pady=10
        )
        row += 1

        # Verify Trader Unlocks button (blue utility button)
        img = load_icon("Verify Trader Unlocks")
        self.verify_btn = ttk.Button(
            btn_frame,
            image=img,
            command=self.run_verification,
            style="BlueIcon.TButton"
        )
        self.verify_btn.grid(row=row, column=col, pady=2, padx=2)
        create_tooltip(self.verify_btn, "Verify Trader Unlocks")
        col += 1

        # Cross-Reference button (moved here from generators)
        img = load_icon("Cross-Reference")
        self.crossref_btn = ttk.Button(
            btn_frame,
            image=img,
            command=lambda: self.run_generator("crossreference", "Cross-Reference"),
            style="BlueIcon.TButton"
        )
        self.crossref_btn.grid(row=row, column=col, pady=2, padx=2)
        create_tooltip(self.crossref_btn, "Cross-Reference")
        self.generator_buttons["crossreference"] = self.crossref_btn
        col += 1

        row += 1
        col = 0

        # Clear Output button (red action button)
        img = load_icon("Clear Output")
        self.clear_btn = ttk.Button(
            btn_frame,
            image=img,
            command=self.clear_output,
            style="RedIcon.TButton"
        )
        self.clear_btn.grid(row=row, column=col, pady=2, padx=2)
        create_tooltip(self.clear_btn, "Clear Output")
        col += 1

        # Cancel button (red action button with X icon)
        cancel_img = create_cancel_icon()
        self.cancel_btn = ttk.Button(
            btn_frame,
            image=cancel_img,
            command=self.cancel_process,
            state="disabled",
            style="RedIcon.TButton"
        )
        self.cancel_btn.grid(row=row, column=col, pady=2, padx=2)
        create_tooltip(self.cancel_btn, "Cancel")

    def create_selection_pane(self, parent):
        """Create the middle Selection pane with checkboxes using native ttk styling."""
        # Main container frame
        selection_container = ttk.Frame(parent)
        selection_container.grid(row=1, column=1, sticky="nsew", padx=(0, 10))
        selection_container.columnconfigure(0, weight=1)
        selection_container.rowconfigure(2, weight=1)  # Row 2 is the scrollable area (was row 3)

        # Header frame with title and Package button
        title_frame = ttk.Frame(selection_container)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        title_frame.columnconfigure(1, weight=1)  # Middle column expands for centered buttons

        # Large title label
        selection_title = ttk.Label(
            title_frame,
            text="SELECTION",
            font=("Segoe UI", 14, "bold")
        )
        selection_title.grid(row=0, column=0, sticky="w")

        # Generator type label (shown next to SELECTION title)
        self.selection_gen_label = ttk.Label(
            title_frame,
            text="",
            font=("Segoe UI", 12)
        )
        self.selection_gen_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Center frame for toggle buttons (XCL, ARC, SEL)
        toggle_frame = ttk.Frame(title_frame)
        toggle_frame.grid(row=0, column=2, sticky="e", padx=(10, 10))

        # Create small toggle buttons for XCL, ARC, SEL
        btn_width = 5
        self.xcl_toggle_btn = ttk.Button(
            toggle_frame, text="XCL", width=btn_width,
            command=lambda: self.toggle_all_column("xcl")
        )
        self.xcl_toggle_btn.pack(side="left", padx=(0, 2))
        self._add_tooltip(self.xcl_toggle_btn, "Toggle all XCL checkboxes")

        self.arc_toggle_btn = ttk.Button(
            toggle_frame, text="ARC", width=btn_width,
            command=lambda: self.toggle_all_column("arc")
        )
        self.arc_toggle_btn.pack(side="left", padx=2)
        self._add_tooltip(self.arc_toggle_btn, "Toggle all ARC checkboxes")

        self.sel_toggle_btn = ttk.Button(
            toggle_frame, text="SEL", width=btn_width,
            command=lambda: self.toggle_all_column("sel")
        )
        self.sel_toggle_btn.pack(side="left", padx=2)
        self._add_tooltip(self.sel_toggle_btn, "Toggle all SEL checkboxes")

        # Package button
        self.package_btn = ttk.Button(
            title_frame,
            text="Package",
            command=self.package_selected,
            width=10
        )
        self.package_btn.grid(row=0, column=3, sticky="e", padx=(10, 0))

        # Fixed column header row (XCL, ARC, SEL, FILE NAME) - using tk.Label for reliable white text
        header_frame = ttk.Frame(selection_container)
        header_frame.grid(row=1, column=0, sticky="ew")

        # Track current sort column and direction
        self.sort_column = "filename"  # Default sort by filename
        self.sort_ascending = True

        # Create header labels using tk.Label for reliable foreground color
        # Font size increased by 50% (9 -> 14)
        header_font = ("Segoe UI", 14, "bold")
        header_bg = "#0d0d0d"  # Match the background color

        # XCL header (clickable for sorting)
        self.xcl_header = tk.Label(header_frame, text="XCL", font=header_font, width=4, cursor="hand2",
                                   fg="#ffffff", bg=header_bg)
        self.xcl_header.pack(side="left", padx=(5, 0))
        self.xcl_header.bind("<Button-1>", lambda e: self.sort_selection("xcl"))
        self._add_tooltip(self.xcl_header, "Excluded - Click to sort")

        # ARC header (clickable for sorting)
        self.arc_header = tk.Label(header_frame, text="ARC", font=header_font, width=4, cursor="hand2",
                                   fg="#ffffff", bg=header_bg)
        self.arc_header.pack(side="left")
        self.arc_header.bind("<Button-1>", lambda e: self.sort_selection("arc"))
        self._add_tooltip(self.arc_header, "Archived - Click to sort")

        # SEL header (clickable for sorting)
        self.sel_header = tk.Label(header_frame, text="SEL", font=header_font, width=4, cursor="hand2",
                                   fg="#ffffff", bg=header_bg)
        self.sel_header.pack(side="left")
        self.sel_header.bind("<Button-1>", lambda e: self.sort_selection("sel"))
        self._add_tooltip(self.sel_header, "Selected - Click to sort")

        # FILE NAME header (clickable for sorting)
        self.name_header = tk.Label(header_frame, text="FILE NAME", font=header_font, anchor="w", cursor="hand2",
                                    fg="#ffffff", bg=header_bg)
        self.name_header.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.name_header.bind("<Button-1>", lambda e: self.sort_selection("filename"))
        self._add_tooltip(self.name_header, "File Name - Click to sort")

        # Selection list using Treeview for native styling and scrolling
        list_frame = ttk.Frame(selection_container)
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Create Treeview with checkbutton-like columns
        columns = ("xcl", "arc", "sel", "filename")
        self.selection_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        # Configure columns - widths increased by 50% for larger text
        self.selection_tree.heading("xcl", text="")
        self.selection_tree.heading("arc", text="")
        self.selection_tree.heading("sel", text="")
        self.selection_tree.heading("filename", text="")

        self.selection_tree.column("xcl", width=45, minwidth=45, stretch=False, anchor="center")
        self.selection_tree.column("arc", width=45, minwidth=45, stretch=False, anchor="center")
        self.selection_tree.column("sel", width=45, minwidth=45, stretch=False, anchor="center")
        self.selection_tree.column("filename", width=200, minwidth=100, stretch=True, anchor="w")

        self.selection_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        selection_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.selection_tree.yview)
        selection_scroll.grid(row=0, column=1, sticky="ns")
        self.selection_tree.configure(yscrollcommand=selection_scroll.set)

        # Bind selection event
        self.selection_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.selection_tree.bind("<Button-1>", self._on_tree_click)

        # Store checkbox variables and current generator type
        self.checkbox_vars = {}  # {item_name: {'xcl': BooleanVar, 'arc': BooleanVar, 'sel': BooleanVar}}
        self.current_gen_type = None
        self.selection_items = {}  # Maps display name to file path
        self.tree_item_map = {}  # Maps tree item id to display name

        # Load selection states from config
        self.selection_states = self.load_selection_states()

    def _on_tree_select(self, event):
        """Handle tree selection - show file contents."""
        selection = self.selection_tree.selection()
        if selection:
            item_id = selection[0]
            if item_id in self.tree_item_map:
                display_name = self.tree_item_map[item_id]
                self.on_item_clicked(display_name)

    def _on_tree_click(self, event):
        """Handle click on tree - toggle checkboxes in XCL/ARC/SEL columns."""
        region = self.selection_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.selection_tree.identify_column(event.x)
            item_id = self.selection_tree.identify_row(event.y)

            if item_id and item_id in self.tree_item_map:
                display_name = self.tree_item_map[item_id]
                col_idx = int(column.replace("#", "")) - 1

                # Columns: 0=xcl, 1=arc, 2=sel, 3=filename
                col_map = {0: 'xcl', 1: 'arc', 2: 'sel'}

                if col_idx in col_map:
                    col_name = col_map[col_idx]
                    # Toggle the checkbox state
                    current_val = self.checkbox_vars[display_name][col_name].get()
                    self.checkbox_vars[display_name][col_name].set(not current_val)

                    # Update tree display
                    self._update_tree_item(item_id, display_name)

                    # Save state
                    self.on_checkbox_changed(display_name, col_name)

    def _update_tree_item(self, item_id, display_name):
        """Update the tree item display based on checkbox states."""
        xcl = "☑" if self.checkbox_vars[display_name]['xcl'].get() else "☐"
        arc = "☑" if self.checkbox_vars[display_name]['arc'].get() else "☐"
        sel = "☑" if self.checkbox_vars[display_name]['sel'].get() else "☐"
        self.selection_tree.item(item_id, values=(xcl, arc, sel, display_name))

    def load_selection_states(self):
        """Load selection states from XML config file."""
        states_file = os.path.join(get_config_dir(), SELECTION_STATES_FILE)
        if os.path.exists(states_file):
            try:
                tree = ET.parse(states_file)
                root = tree.getroot()
                states = {}

                for gen_elem in root.findall("generator"):
                    gen_type = gen_elem.get("type")
                    if gen_type:
                        states[gen_type] = {}
                        for item_elem in gen_elem.findall("item"):
                            item_name = item_elem.get("name")
                            # Load checkbox states (xcl, arc, sel as booleans)
                            xcl = item_elem.get("xcl", "0") == "1"
                            arc = item_elem.get("arc", "0") == "1"
                            sel = item_elem.get("sel", "0") == "1"
                            if item_name:
                                states[gen_type][item_name] = {'xcl': xcl, 'arc': arc, 'sel': sel}

                return states
            except Exception as e:
                print(f"Error loading selection states: {e}")
        return {}

    def save_selection_states(self):
        """Save selection states to XML config file."""
        states_file = os.path.join(get_config_dir(), SELECTION_STATES_FILE)
        try:
            root = ET.Element("SelectionStates")
            root.set("version", APP_VERSION)

            for gen_type, items in self.selection_states.items():
                gen_elem = ET.SubElement(root, "generator")
                gen_elem.set("type", gen_type)

                for item_name, state in items.items():
                    item_elem = ET.SubElement(gen_elem, "item")
                    item_elem.set("name", item_name)
                    # Save checkbox states as 0/1
                    item_elem.set("xcl", "1" if state.get('xcl', False) else "0")
                    item_elem.set("arc", "1" if state.get('arc', False) else "0")
                    item_elem.set("sel", "1" if state.get('sel', False) else "0")

            # Pretty print the XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            # Remove the XML declaration line that minidom adds
            lines = xml_str.split('\n')
            xml_str = '\n'.join(lines[1:])

            with open(states_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(xml_str)
        except Exception as e:
            self.log(f"Error saving selection states: {str(e)}", "error")

    def sort_selection(self, column):
        """Sort the selection list by the specified column."""
        # Toggle direction if same column clicked again
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True

        # Re-populate with the new sort order
        if self.current_gen_type:
            self.populate_selection_tree(self.current_gen_type)

    def toggle_all_column(self, column):
        """Toggle all checkboxes in a column (XCL, ARC, or SEL)."""
        if not self.checkbox_vars:
            return

        # Count how many are currently checked
        checked_count = sum(1 for vars in self.checkbox_vars.values() if vars[column].get())
        total_count = len(self.checkbox_vars)

        # If more than half are checked, turn all off; otherwise turn all on
        new_state = checked_count < (total_count / 2)

        # Update all checkboxes in this column
        for item_name, vars in self.checkbox_vars.items():
            vars[column].set(new_state)
            # Update the treeview display
            for item_id in self.selection_tree.get_children():
                if self.selection_tree.item(item_id, "values")[3] == item_name:
                    values = list(self.selection_tree.item(item_id, "values"))
                    col_index = {"xcl": 0, "arc": 1, "sel": 2}[column]
                    values[col_index] = "☑" if new_state else "☐"
                    self.selection_tree.item(item_id, values=values)
                    break

            # Update selection states
            if self.current_gen_type:
                if self.current_gen_type not in self.selection_states:
                    self.selection_states[self.current_gen_type] = {}
                if item_name not in self.selection_states[self.current_gen_type]:
                    self.selection_states[self.current_gen_type][item_name] = {'xcl': False, 'arc': False, 'sel': False}
                self.selection_states[self.current_gen_type][item_name][column] = new_state

        # Save changes
        self.save_selection_states()

        # Log the action
        state_text = "checked" if new_state else "unchecked"
        self.log(f"Toggled all {column.upper()} checkboxes to {state_text}", "info")

    def on_checkbox_changed(self, item_name, checkbox_type):
        """Handle checkbox state change and save to config."""
        if self.current_gen_type:
            if self.current_gen_type not in self.selection_states:
                self.selection_states[self.current_gen_type] = {}
            if item_name not in self.selection_states[self.current_gen_type]:
                self.selection_states[self.current_gen_type][item_name] = {'xcl': False, 'arc': False, 'sel': False}
            # Update the specific checkbox state
            self.selection_states[self.current_gen_type][item_name][checkbox_type] = self.checkbox_vars[item_name][checkbox_type].get()
            self.save_selection_states()

    def package_selected(self):
        """Package selected items into MediaWiki XML import files."""
        # Get items with SEL checkbox checked
        selected_items = [name for name, vars in self.checkbox_vars.items() if vars['sel'].get()]

        if not selected_items:
            self.log("No items selected for packaging (SEL column)", "warning")
            return

        self.log(f"Packaging {len(selected_items)} selected items...", "info")

        # Get user's Downloads directory
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        wiki_import_dir = os.path.join(downloads_dir, "wiki import")

        # Create output directory if it doesn't exist
        os.makedirs(wiki_import_dir, exist_ok=True)

        # Load all pages
        pages = []
        for item_name in sorted(selected_items):
            if item_name in self.selection_items:
                file_path = self.selection_items[item_name]
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        pages.append((item_name, content))
                    except Exception as e:
                        self.log(f"Error reading {item_name}: {e}", "error")

        if not pages:
            self.log("No valid wiki files found for selected items", "error")
            return

        # Split into batches of 50 or less
        MAX_PAGES_PER_FILE = 50
        num_batches = (len(pages) + MAX_PAGES_PER_FILE - 1) // MAX_PAGES_PER_FILE

        # Generate a prefix based on the current generator type
        gen_prefix = self.current_gen_type if self.current_gen_type else "wiki"

        for batch_num in range(num_batches):
            start_idx = batch_num * MAX_PAGES_PER_FILE
            end_idx = min(start_idx + MAX_PAGES_PER_FILE, len(pages))
            batch_pages = pages[start_idx:end_idx]

            # Create output filename
            output_file = os.path.join(wiki_import_dir, f'{gen_prefix}_import_{batch_num + 1:02d}.xml')

            try:
                self._create_mediawiki_import(batch_pages, output_file)
                self.log(f"Created {os.path.basename(output_file)} with {len(batch_pages)} pages", "info")
            except Exception as e:
                self.log(f"Error creating import file: {e}", "error")

        self.log(f"Packaging complete! Created {num_batches} file(s) in: {wiki_import_dir}", "success")

    def _create_mediawiki_import(self, pages, output_file):
        """Create a MediaWiki XML import file with the given pages."""
        # Create root mediawiki element
        mediawiki = ET.Element('mediawiki')
        mediawiki.set('xmlns', 'http://www.mediawiki.org/xml/export-0.11/')
        mediawiki.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        mediawiki.set('xsi:schemaLocation', 'http://www.mediawiki.org/xml/export-0.11/ http://www.mediawiki.org/xml/export-0.11.xsd')
        mediawiki.set('version', '0.11')
        mediawiki.set('xml:lang', 'en')

        # Add siteinfo
        siteinfo = ET.SubElement(mediawiki, 'siteinfo')
        sitename = ET.SubElement(siteinfo, 'sitename')
        sitename.text = 'Wiki'

        # Add each page
        for page_title, page_content in pages:
            page = ET.SubElement(mediawiki, 'page')

            title = ET.SubElement(page, 'title')
            title.text = page_title

            ns = ET.SubElement(page, 'ns')
            ns.text = '0'

            revision = ET.SubElement(page, 'revision')

            timestamp = ET.SubElement(revision, 'timestamp')
            timestamp.text = '2024-01-01T00:00:00Z'

            contributor = ET.SubElement(revision, 'contributor')
            username = ET.SubElement(contributor, 'username')
            username.text = 'WikiBot'

            comment = ET.SubElement(revision, 'comment')
            comment.text = 'Automated import'

            model = ET.SubElement(revision, 'model')
            model.text = 'wikitext'

            format_elem = ET.SubElement(revision, 'format')
            format_elem.text = 'text/x-wiki'

            text = ET.SubElement(revision, 'text')
            text.set('xml:space', 'preserve')
            text.set('bytes', str(len(page_content.encode('utf-8'))))
            text.text = page_content

        # Write to file with pretty formatting
        rough_string = ET.tostring(mediawiki, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        xml_str = reparsed.toprettyxml(indent="  ")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)

    def create_contents_pane(self, parent):
        """Create the right Contents pane with Copy button using native styling."""
        # Main container frame
        contents_container = ttk.Frame(parent)
        contents_container.grid(row=1, column=2, sticky="nsew")
        contents_container.columnconfigure(0, weight=1)
        contents_container.rowconfigure(1, weight=1)

        # Header frame with title and Copy button
        header_frame = ttk.Frame(contents_container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header_frame.columnconfigure(0, weight=1)

        # Large title label
        contents_title = ttk.Label(
            header_frame,
            text="CONTENTS",
            font=("Segoe UI", 14, "bold")
        )
        contents_title.grid(row=0, column=0, sticky="w")

        # Copy button
        self.copy_btn = ttk.Button(
            header_frame,
            text="Copy",
            command=self.copy_contents,
            width=10
        )
        self.copy_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # Text widget for displaying file contents - use stored system colors
        text_frame = ttk.Frame(contents_container)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # Get colors from root (set by apply_theme)
        bg_color = getattr(self.root, 'tk_bg', 'SystemWindow')
        fg_color = getattr(self.root, 'tk_fg', 'SystemWindowText')

        self.contents_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=bg_color,
            fg=fg_color,
            insertbackground=fg_color
        )
        self.contents_text.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar
        contents_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.contents_text.yview)
        contents_scroll.grid(row=0, column=1, sticky="ns")
        self.contents_text.configure(yscrollcommand=contents_scroll.set)

    def copy_contents(self):
        """Copy contents pane text to clipboard."""
        try:
            content = self.contents_text.get(1.0, tk.END).strip()
            if content:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self.log("Contents copied to clipboard", "success")
            else:
                self.log("No content to copy", "warning")
        except Exception as e:
            self.log(f"Error copying to clipboard: {str(e)}", "error")

    def on_item_clicked(self, item_name):
        """Handle click on an item in the selection list."""
        if item_name in self.selection_items:
            self.load_file_contents(self.selection_items[item_name])

    def load_file_contents(self, file_path):
        """Load and display the contents of a file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.contents_text.configure(state="normal")
                self.contents_text.delete(1.0, tk.END)
                self.contents_text.insert(tk.END, content)
                self.contents_text.configure(state="disabled")
        except Exception as e:
            self.contents_text.configure(state="normal")
            self.contents_text.delete(1.0, tk.END)
            self.contents_text.insert(tk.END, f"Error loading file: {str(e)}")
            self.contents_text.configure(state="disabled")

    def populate_selection_tree(self, gen_type):
        """Populate the selection Treeview with checkboxes for generated wiki files."""
        # Clear existing items
        for item in self.selection_tree.get_children():
            self.selection_tree.delete(item)
        self.checkbox_vars.clear()
        self.selection_items.clear()
        self.tree_item_map.clear()
        self.current_gen_type = gen_type

        # Map generator types to display names
        gen_display_names = {
            "items": "Items",
            "consumables": "Consumables",
            "constructions": "Constructions",
            "weapons": "Weapons",
            "armor": "Armor",
            "tools": "Tools",
            "ores": "Ores",
            "brews": "Brews",
            "runes": "Runes",
            "storage": "Storage",
            "tradegoods": "Trade Goods",
            "crossreference": "Cross Reference",
        }

        # Update the generator type label next to SELECTION title
        display_name = gen_display_names.get(gen_type, gen_type.title() if gen_type else "")
        self.selection_gen_label.config(text=f"- {display_name}" if display_name else "")

        # Map generator types to output directories
        output_dirs = {
            "items": "items",
            "consumables": "consumables",
            "constructions": "constructions",
            "weapons": "weapons",
            "armor": "armor",
            "tools": "tools",
            "ores": "ores",
            "brews": "brews",
            "runes": "runes",
            "storage": "storage",
            "tradegoods": "tradegoods",
            "crossreference": "crossreference",
        }

        if gen_type in output_dirs:
            # Wiki files are in %APPDATA%\MoriaWikiGenerator\output\wiki\<gen_type>
            output_path = os.path.join(get_default_output_path(), "wiki", output_dirs[gen_type])
            if os.path.exists(output_path):
                # Get saved states for this generator
                saved_states = self.selection_states.get(gen_type, {})

                # Get all wiki files
                files = [f for f in os.listdir(output_path) if f.endswith('.wiki')]

                # Build list of (filename, display_name, state_dict) for sorting
                file_data = []
                for filename in files:
                    display_name = filename[:-5]  # Remove .wiki extension
                    state = saved_states.get(display_name, {'xcl': False, 'arc': False, 'sel': False})
                    file_data.append((filename, display_name, state))

                # Apply sorting based on sort_column
                if self.sort_column == "filename":
                    file_data.sort(key=lambda x: x[1].lower(), reverse=not self.sort_ascending)
                elif self.sort_column == "xcl":
                    file_data.sort(key=lambda x: (0 if x[2].get('xcl', False) else 1, x[1].lower()), reverse=not self.sort_ascending)
                elif self.sort_column == "arc":
                    file_data.sort(key=lambda x: (0 if x[2].get('arc', False) else 1, x[1].lower()), reverse=not self.sort_ascending)
                elif self.sort_column == "sel":
                    file_data.sort(key=lambda x: (0 if x[2].get('sel', False) else 1, x[1].lower()), reverse=not self.sort_ascending)

                # Ensure we have a dict for this generator type in selection_states
                if gen_type not in self.selection_states:
                    self.selection_states[gen_type] = {}

                # Track new items added
                new_items_count = 0

                # Add items to treeview
                for filename, display_name, state in file_data:
                    file_path = os.path.join(output_path, filename)
                    self.selection_items[display_name] = file_path

                    # Create checkbox variables for each column
                    xcl_var = tk.BooleanVar(value=state.get('xcl', False))
                    arc_var = tk.BooleanVar(value=state.get('arc', False))
                    sel_var = tk.BooleanVar(value=state.get('sel', False))
                    self.checkbox_vars[display_name] = {'xcl': xcl_var, 'arc': arc_var, 'sel': sel_var}

                    # Update selection_states: preserve existing, add new items with defaults
                    if display_name not in self.selection_states[gen_type]:
                        # New item - add with default unchecked states
                        self.selection_states[gen_type][display_name] = {
                            'xcl': False, 'arc': False, 'sel': False
                        }
                        new_items_count += 1
                    # Existing items are already in selection_states, don't overwrite

                    # Create checkbox display characters
                    xcl = "☑" if xcl_var.get() else "☐"
                    arc = "☑" if arc_var.get() else "☐"
                    sel = "☑" if sel_var.get() else "☐"

                    # Insert into treeview
                    item_id = self.selection_tree.insert("", "end", values=(xcl, arc, sel, display_name))
                    self.tree_item_map[item_id] = display_name

                # Save selection states to persist new items
                if new_items_count > 0:
                    self.save_selection_states()

    def create_output_section(self, parent):
        """Create the output/log section spanning all columns at bottom using native styling."""
        output_frame = ttk.LabelFrame(parent, text="Output", padding="5")
        output_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)

        # Text widget with scrollbar for output - use stored system colors
        text_frame = ttk.Frame(output_frame)
        text_frame.grid(row=0, column=0, sticky="ew")
        text_frame.columnconfigure(0, weight=1)

        # Get colors from root (set by apply_theme)
        bg_color = getattr(self.root, 'tk_bg', 'SystemWindow')
        fg_color = getattr(self.root, 'tk_fg', 'SystemWindowText')

        self.output_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=10,  # Approximately 10 lines of text
            bg=bg_color,
            fg=fg_color,
            insertbackground=fg_color
        )
        self.output_text.grid(row=0, column=0, sticky="ew")

        output_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.output_text.yview)
        output_scroll.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=output_scroll.set)

        # Configure tags for colored output - these colors work in both light and dark modes
        self.output_text.tag_configure("info", foreground="#0066cc")
        self.output_text.tag_configure("success", foreground="#008000")
        self.output_text.tag_configure("error", foreground="#cc0000")
        self.output_text.tag_configure("warning", foreground="#cc6600")

    def create_status_bar(self, parent):
        """Create the status bar at the bottom."""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9)
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        # Game install info
        game_type = self.config.get("game_install_type", "")
        if game_type:
            game_label = ttk.Label(
                status_frame,
                text=f"Game: {game_type}",
                font=("Segoe UI", 8),
                foreground="gray"
            )
            game_label.grid(row=0, column=1, sticky="e", padx=(10, 10))

        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(
            status_frame,
            mode="indeterminate",
            length=200
        )
        self.progress.grid(row=0, column=2, sticky="e", padx=(10, 0))
        self.progress.grid_remove()  # Hide initially

    def show_settings(self):
        """Show the settings dialog."""
        wizard = SetupWizard(self.root, self.config, is_first_run=False)
        if wizard.show():
            self.log("Configuration updated successfully", "success")
            messagebox.showinfo(
                "Settings Saved",
                "Settings have been saved.\nSome changes may require restarting the application.",
                parent=self.root
            )

    def log(self, message, tag=None):
        """Add a message to the output log."""
        self.output_text.configure(state="normal")
        if tag:
            self.output_text.insert(tk.END, message + "\n", tag)
        else:
            self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state="disabled")

    def clear_output(self):
        """Clear the output log."""
        self.output_text.configure(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state="disabled")

    def set_running_state(self, running):
        """Update UI state based on whether a process is running."""
        state = "disabled" if running else "normal"

        # Disable/enable generator buttons
        for widget in self.root.winfo_children():
            self._set_button_states(widget, state)

        # Update cancel button
        self.cancel_btn.configure(state="normal" if running else "disabled")

        # Show/hide progress bar
        if running:
            self.progress.grid()
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.grid_remove()

    def _set_button_states(self, widget, state):
        """Recursively set button states."""
        if isinstance(widget, ttk.Button) and widget != self.cancel_btn:
            widget.configure(state=state)
        for child in widget.winfo_children():
            self._set_button_states(child, state)

    def show_generator_prompt(self, name, file_count):
        """Show a themed dialog asking whether to re-run generator or view files."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Existing Output Found")
        dialog.transient(self.root)
        dialog.grab_set()

        # Apply theme colors
        is_dark = self.config.is_dark_mode()
        if is_dark:
            bg_color = "#2d2d2d"
            fg_color = "#ffffff"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"

        dialog.configure(bg=bg_color)

        # Center the dialog
        dialog.geometry("350x120")
        dialog.resizable(False, False)

        # Position relative to parent
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 60
        dialog.geometry(f"+{x}+{y}")

        # Result variable
        result = [None]  # Use list to allow modification in nested function

        # Message
        msg_frame = ttk.Frame(dialog)
        msg_frame.pack(fill="x", padx=20, pady=15)

        msg = ttk.Label(
            msg_frame,
            text=f"The {name} output directory already contains {file_count} wiki files.",
            wraplength=310
        )
        msg.pack()

        # Buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        def on_rerun():
            result[0] = True
            dialog.destroy()

        def on_files():
            result[0] = False
            dialog.destroy()

        rerun_btn = ttk.Button(btn_frame, text="Re-run", command=on_rerun, width=12)
        rerun_btn.pack(side="left", expand=True, padx=5)

        files_btn = ttk.Button(btn_frame, text="Files", command=on_files, width=12)
        files_btn.pack(side="right", expand=True, padx=5)

        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", on_files)

        # Wait for dialog to close
        dialog.wait_window()

        return result[0]

    def run_generator(self, gen_type, name):
        """Run a single generator or show existing files."""
        # Map generator types to output directories
        output_dirs = {
            "items": "items",
            "consumables": "consumables",
            "constructions": "constructions",
            "weapons": "weapons",
            "armor": "armor",
            "tools": "tools",
            "ores": "ores",
            "brews": "brews",
            "runes": "runes",
            "storage": "storage",
            "tradegoods": "tradegoods",
            "crossreference": "crossreference",
        }

        # Check if output directory has existing files
        if gen_type in output_dirs:
            # Wiki files are in %APPDATA%\MoriaWikiGenerator\output\wiki\<gen_type>
            output_path = os.path.join(get_default_output_path(), "wiki", output_dirs[gen_type])
            if os.path.exists(output_path):
                wiki_files = [f for f in os.listdir(output_path) if f.endswith('.wiki')]
                if wiki_files:
                    # Prompt user whether to re-run or view existing
                    result = self.show_generator_prompt(name, len(wiki_files))
                    if not result:
                        # User chose Files - show existing files in Selection pane
                        self.populate_selection_tree(gen_type)
                        self.log(f"Loaded {len(wiki_files)} existing {name} files", "info")
                        return

        # User chose Yes or no existing files - run the generator
        self.log(f"\n{'='*60}", "info")
        self.log(f"Running {name} Generator...", "info")
        self.log(f"{'='*60}", "info")

        self.set_running_state(True)
        self.status_var.set(f"Running {name} generator...")

        # Store current gen_type for populating selection after completion
        self.current_gen_type = gen_type

        # Run in a separate thread to keep UI responsive
        thread = threading.Thread(
            target=self._run_generator,
            args=(gen_type, name),
            daemon=True
        )
        thread.start()

    def _run_generator(self, gen_type, name):
        """Execute a generator function."""
        try:
            source_path = self.config.get_source_path()
            output_path = self.config.get_output_path()

            # Get the generator function
            generator_func = get_generator_function(gen_type)
            if generator_func is None:
                self.root.after(0, self.log,
                               f"Generator '{gen_type}' not yet implemented", "warning")
                return

            # Create a log callback that posts to the UI thread
            def log_callback(message):
                self.root.after(0, self.log, message)

            # Run the generator
            success = generator_func(source_path, output_path, log_callback)

            if success:
                self.root.after(0, self.log,
                               f"\n{name} completed successfully!", "success")
                # Populate selection tree with generated files
                self.root.after(0, self.populate_selection_tree, gen_type)
            else:
                self.root.after(0, self.log,
                               f"\n{name} finished with errors", "error")

        except Exception as e:
            self.root.after(0, self.log, f"Error running {name}: {str(e)}", "error")

        finally:
            self.running_process = None
            self.root.after(0, self.set_running_state, False)
            self.root.after(0, lambda: self.status_var.set("Ready"))

    def run_all_generators(self):
        """Run all generators in sequence."""
        self.log("\n" + "="*60, "info")
        self.log("Running ALL Generators...", "info")
        self.log("="*60, "info")

        self.set_running_state(True)
        self.status_var.set("Running all generators...")

        thread = threading.Thread(
            target=self._run_all_generators,
            daemon=True
        )
        thread.start()

    def _run_all_generators(self):
        """Execute all generators in sequence."""
        success_count = 0
        error_count = 0

        source_path = self.config.get_source_path()
        output_path = self.config.get_output_path()

        for name, gen_type in self.generators:
            self.root.after(0, lambda n=name: self.status_var.set(f"Running {n}..."))
            self.root.after(0, self.log, f"\n--- {name} ---", "info")

            try:
                generator_func = get_generator_function(gen_type)
                if generator_func is None:
                    self.root.after(0, self.log,
                                   f"Skipping {name}: not yet implemented", "warning")
                    continue

                def log_callback(message):
                    self.root.after(0, self.log, message)

                success = generator_func(source_path, output_path, log_callback)

                if success:
                    success_count += 1
                else:
                    error_count += 1
                    self.root.after(0, self.log, f"{name} finished with errors", "error")

            except Exception as e:
                error_count += 1
                self.root.after(0, self.log, f"Error running {name}: {str(e)}", "error")

        # Summary
        self.root.after(0, self.log, f"\n{'='*60}", "info")
        self.root.after(
            0, self.log,
            f"Completed: {success_count} successful, {error_count} errors",
            "success" if error_count == 0 else "warning"
        )

        self.running_process = None
        self.root.after(0, self.set_running_state, False)
        self.root.after(0, lambda: self.status_var.set("Ready"))

    def run_verification(self):
        """Run the trader unlock verification."""
        self.log("\n" + "="*60, "info")
        self.log("Running Trader Unlock Verification...", "info")
        self.log("="*60, "info")

        self.set_running_state(True)
        self.status_var.set("Running verification...")

        thread = threading.Thread(
            target=self._run_verification,
            daemon=True
        )
        thread.start()

    def _run_verification(self):
        """Execute trader unlock verification."""
        try:
            output_path = self.config.get_output_path()

            def log_callback(message):
                self.root.after(0, self.log, message)

            success = verify_trader_unlocks(output_path, log_callback)

            if success:
                self.root.after(0, self.log,
                               "\nVerification completed successfully!", "success")
            else:
                self.root.after(0, self.log,
                               "\nVerification found issues", "warning")

        except Exception as e:
            self.root.after(0, self.log, f"Error during verification: {str(e)}", "error")

        finally:
            self.root.after(0, self.set_running_state, False)
            self.root.after(0, lambda: self.status_var.set("Ready"))

    def cancel_process(self):
        """Cancel the currently running process."""
        # Note: Thread-based execution cannot be easily cancelled
        # This is kept for UI consistency
        self.log("\nCancellation requested (processing will complete current item)", "warning")
        self.status_var.set("Cancelling...")

    def run_import_game_files(self):
        """Run the game file import process (retoc + UAssetGUI)."""
        self.log("\n" + "="*60, "info")
        self.log("Importing Game Files...", "info")
        self.log("="*60, "info")

        self.set_running_state(True)
        self.status_var.set("Importing game files...")

        thread = threading.Thread(
            target=self._run_import_game_files,
            daemon=True
        )
        thread.start()

    def _run_import_game_files(self):
        """Execute the game file import process."""
        try:
            # Get paths from config
            game_path = self.config.get("game_install_path", "")
            output_path = self.config.get_output_path()
            utilities_path = self.config.get_utilities_path()

            # Validate game path
            if not game_path:
                self.root.after(0, self.log, "Error: Game installation path not configured", "error")
                return

            # Build paths
            paks_path = os.path.join(game_path, "Moria", "Content", "Paks")
            retoc_output = os.path.join(output_path, "retoc")
            datajson_output = os.path.join(output_path, "datajson")
            retoc_exe = os.path.join(utilities_path, "retoc.exe")
            uassetgui_exe = os.path.join(utilities_path, "UAssetGUI.exe")

            # Validate paths
            if not os.path.exists(paks_path):
                self.root.after(0, self.log, f"Error: Game Paks folder not found: {paks_path}", "error")
                return

            if not os.path.exists(retoc_exe):
                self.root.after(0, self.log, f"Error: retoc.exe not found: {retoc_exe}", "error")
                return

            if not os.path.exists(uassetgui_exe):
                self.root.after(0, self.log, f"Error: UAssetGUI.exe not found: {uassetgui_exe}", "error")
                return

            # Create output directories
            # Note: retoc needs to create its output directory itself, so remove if exists
            if os.path.exists(retoc_output):
                self.root.after(0, self.log, f"  Removing existing retoc output: {retoc_output}", "info")
                shutil.rmtree(retoc_output)
            os.makedirs(datajson_output, exist_ok=True)

            # Step 1: Run retoc.exe
            self.root.after(0, self.log, "\nStep 1: Extracting game files with retoc...", "info")
            self.root.after(0, self.log, f"  Input: {paks_path}", "info")
            self.root.after(0, self.log, f"  Output: {retoc_output}", "info")
            self.root.after(0, lambda: self.status_var.set("Running retoc.exe..."))

            # Ensure retoc output directory exists
            os.makedirs(retoc_output, exist_ok=True)

            # Build command as list (subprocess handles quoting automatically)
            retoc_cmd = [retoc_exe, "to-legacy", "--version", "UE4_27", paks_path, retoc_output]

            # Display command with quotes for clarity
            display_cmd = f'"{retoc_exe}" to-legacy --version UE4_27 "{paks_path}" "{retoc_output}"'
            self.root.after(0, self.log, f"  Command: {display_cmd}", "info")

            try:
                process = subprocess.Popen(
                    retoc_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )

                # Stream output
                for line in process.stdout:
                    line = line.rstrip()
                    if line:
                        self.root.after(0, self.log, f"  {line}")

                process.wait()

                if process.returncode != 0:
                    self.root.after(0, self.log, f"Error: retoc.exe exited with code {process.returncode}", "error")
                    return

                self.root.after(0, self.log, "  retoc.exe completed successfully", "success")

            except Exception as e:
                self.root.after(0, self.log, f"Error running retoc.exe: {str(e)}", "error")
                return

            # Step 2: Run UAssetGUI to convert each .uasset file to JSON
            # UAssetGUI syntax: UAssetGUI tojson <source> <destination> <engine version>
            self.root.after(0, self.log, "\nStep 2: Converting to JSON with UAssetGUI...", "info")
            self.root.after(0, self.log, f"  Input: {retoc_output}", "info")
            self.root.after(0, self.log, f"  Output: {datajson_output}", "info")
            self.root.after(0, lambda: self.status_var.set("Running UAssetGUI..."))

            # Find all .uasset files in retoc output
            uasset_files = []
            for root_dir, dirs, files in os.walk(retoc_output):
                for file in files:
                    if file.endswith(".uasset"):
                        uasset_files.append(os.path.join(root_dir, file))

            self.root.after(0, self.log, f"  Found {len(uasset_files)} .uasset files to convert", "info")

            converted_count = 0
            error_count = 0

            for uasset_file in uasset_files:
                # Calculate relative path to preserve directory structure
                rel_path = os.path.relpath(uasset_file, retoc_output)
                json_file = os.path.join(datajson_output, rel_path.replace(".uasset", ".json"))

                # Create output directory if needed
                json_dir = os.path.dirname(json_file)
                os.makedirs(json_dir, exist_ok=True)

                # UAssetGUI command: tojson <source> <destination> <engine version>
                uassetgui_cmd = [uassetgui_exe, "tojson", uasset_file, json_file, "VER_UE4_27"]

                try:
                    process = subprocess.Popen(
                        uassetgui_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    )
                    process.wait()

                    if process.returncode == 0:
                        converted_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1

                # Update progress periodically
                if (converted_count + error_count) % 100 == 0:
                    self.root.after(0, self.log,
                        f"  Progress: {converted_count + error_count}/{len(uasset_files)} files processed")

            self.root.after(0, self.log,
                f"  Converted {converted_count} files, {error_count} errors", "success" if error_count == 0 else "warning")

            # Success
            self.root.after(0, self.log, "\n" + "="*60, "info")
            self.root.after(0, self.log, "Game file import completed successfully!", "success")
            self.root.after(0, self.log, f"JSON data available at: {datajson_output}", "success")

        except Exception as e:
            self.root.after(0, self.log, f"Error during import: {str(e)}", "error")

        finally:
            self.root.after(0, self.set_running_state, False)
            self.root.after(0, lambda: self.status_var.set("Ready"))


def apply_theme(root, config):
    """Apply custom dark theme with colored accents."""
    style = ttk.Style()

    # Always use clam as base (most customizable)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    # Custom dark theme colors
    bg_color = "#0d0d0d"          # Very dark grey, almost black
    pane_bg = "#1a1a1a"           # Dark grey for panes
    fg_color = "#e0e0e0"          # Light grey text
    border_color = "#4a90d9"      # Light blue for borders
    select_bg = "#2d5a8a"         # Selection highlight
    select_fg = "#ffffff"         # White text on selection

    # Button colors
    button_green = "#2d5a2d"      # Dark green
    button_green_hover = "#3d7a3d"
    button_red = "#5a2d2d"        # Dark red
    button_red_hover = "#7a3d3d"
    button_blue = "#2d4a5a"       # Dark blue-grey
    button_blue_hover = "#3d6a7a"

    entry_bg = "#252525"          # Entry/text field background
    trough_color = "#1a1a1a"

    # Configure root window
    root.configure(bg=bg_color)

    # Configure ttk styles
    style.configure(".", background=bg_color, foreground=fg_color, fieldbackground=entry_bg,
                    bordercolor=border_color, lightcolor=border_color, darkcolor=border_color)
    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, foreground=fg_color)
    style.configure("TLabelframe", background=pane_bg, foreground=fg_color, bordercolor=border_color)
    style.configure("TLabelframe.Label", background=pane_bg, foreground=border_color)

    # Green buttons (default action buttons)
    style.configure("TButton", background=button_green, foreground=fg_color, bordercolor=border_color,
                    focuscolor=border_color, padding=[8, 4])
    style.map("TButton",
              background=[("active", button_green_hover), ("pressed", button_green_hover)],
              foreground=[("active", select_fg)])

    # Icon buttons (transparent background, no border)
    style.configure("Icon.TButton", background=bg_color, foreground=fg_color, bordercolor=bg_color,
                    focuscolor=bg_color, borderwidth=0, padding=2, relief="flat")
    style.map("Icon.TButton",
              background=[("active", pane_bg), ("pressed", pane_bg)],
              bordercolor=[("active", bg_color), ("pressed", bg_color)])

    # Red icon buttons (transparent background, no border)
    style.configure("RedIcon.TButton", background=bg_color, foreground=fg_color, bordercolor=bg_color,
                    focuscolor=bg_color, borderwidth=0, padding=2, relief="flat")
    style.map("RedIcon.TButton",
              background=[("active", button_red), ("pressed", button_red)],
              bordercolor=[("active", bg_color), ("pressed", bg_color)])

    # Blue icon buttons (transparent background, no border)
    style.configure("BlueIcon.TButton", background=bg_color, foreground=fg_color, bordercolor=bg_color,
                    focuscolor=bg_color, borderwidth=0, padding=2, relief="flat")
    style.map("BlueIcon.TButton",
              background=[("active", button_blue), ("pressed", button_blue)],
              bordercolor=[("active", bg_color), ("pressed", bg_color)])

    # Red buttons (cancel/clear)
    style.configure("Red.TButton", background=button_red, foreground=fg_color, bordercolor=border_color,
                    focuscolor=border_color, padding=[8, 4])
    style.map("Red.TButton",
              background=[("active", button_red_hover), ("pressed", button_red_hover)],
              foreground=[("active", select_fg)])

    # Blue buttons (utility actions)
    style.configure("Blue.TButton", background=button_blue, foreground=fg_color, bordercolor=border_color,
                    focuscolor=border_color, padding=[8, 4])
    style.map("Blue.TButton",
              background=[("active", button_blue_hover), ("pressed", button_blue_hover)],
              foreground=[("active", select_fg)])

    style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color, bordercolor=border_color,
                    insertcolor=fg_color)
    style.configure("TRadiobutton", background=bg_color, foreground=fg_color, indicatorcolor=entry_bg)
    style.map("TRadiobutton", background=[("active", bg_color)], indicatorcolor=[("selected", border_color)])

    style.configure("TCheckbutton", background=bg_color, foreground=fg_color, indicatorcolor=entry_bg)
    style.map("TCheckbutton", background=[("active", bg_color)], indicatorcolor=[("selected", border_color)])

    style.configure("TNotebook", background=bg_color, bordercolor=border_color)
    style.configure("TNotebook.Tab", background=button_blue, foreground=fg_color, padding=[10, 5],
                    bordercolor=border_color)
    style.map("TNotebook.Tab",
              background=[("selected", pane_bg)],
              foreground=[("selected", fg_color)])

    style.configure("Horizontal.TProgressbar", background=border_color, troughcolor=trough_color,
                    bordercolor=border_color)
    style.configure("TSeparator", background=border_color)

    style.configure("Treeview", background=pane_bg, foreground="#ffffff", fieldbackground=pane_bg,
                    bordercolor=border_color, rowheight=36, font=("Segoe UI", 15))
    style.configure("Treeview.Heading", background=button_blue, foreground="#ffffff",
                    bordercolor=border_color, font=("Segoe UI", 14, "bold"))
    style.map("Treeview",
              background=[("selected", select_bg)],
              foreground=[("selected", select_fg)])

    style.configure("TScrollbar", background=pane_bg, troughcolor=trough_color, bordercolor=border_color,
                    arrowcolor=fg_color)

    # Store colors for tk widgets (Text, etc.)
    root.tk_bg = pane_bg
    root.tk_fg = fg_color
    root.tk_select_bg = select_bg
    root.tk_border = border_color


def main():
    """Main entry point for the application."""
    # Load configuration
    config = Configuration()
    config.load()

    # Create root window (hidden initially for setup)
    root = tk.Tk()
    root.withdraw()  # Hide until setup is complete

    # Apply theme
    apply_theme(root, config)

    # Show setup wizard on first run
    if config.is_first_run():
        wizard = SetupWizard(root, config, is_first_run=True)
        if not wizard.show():
            # User cancelled setup
            root.destroy()
            return

    # Show main application
    root.deiconify()
    app = WikiGeneratorApp(root, config)
    root.mainloop()


if __name__ == "__main__":
    main()
