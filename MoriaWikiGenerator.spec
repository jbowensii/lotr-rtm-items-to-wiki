# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Moria Wiki Generator

import os

block_cipher = None

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['wiki_generator_ui.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        ('icons', 'icons'),  # Include icons folder
        ('construction_unlock_overrides.json', '.'),
        ('consumable_unlock_overrides.json', '.'),
        ('item_unlock_overrides.json', '.'),
        ('ore_unlock_overrides.json', '.'),
        ('weapon_unlock_overrides.json', '.'),
    ],
    # Include generator modules as hidden imports so they get compiled in
    hiddenimports=[
        'generate_armor_wiki',
        'generate_brews_wiki',
        'generate_constructions_wiki',
        'generate_consumables_wiki',
        'generate_crossreference_wiki',
        'generate_items_wiki',
        'generate_ore_wiki',
        'generate_runes_wiki',
        'generate_storage_wiki',
        'generate_tools_wiki',
        'generate_tradegoods_wiki',
        'generate_weapons_wiki',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MoriaWikiGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_dir, 'icons', 'app.ico'),
)
