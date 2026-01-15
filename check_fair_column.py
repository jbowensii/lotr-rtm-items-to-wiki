from generate_constructions_wiki import *
import json

# Load all required data
string_map = load_all_string_tables('source/strings')
recipes_data = load_recipes_data('source/DT_ConstructionRecipes.json')
dlc_map = load_entitlements('source/DT_Entitlements.json')

# Load constructions
data = json.load(open('source/DT_Constructions.json', 'r', encoding='utf-8'))
exports = data.get('Exports', [])
constructions = []
[constructions.extend(export.get('Table', {}).get('Data', [])) for export in exports]

# Find Fair Column Base (WhiteMarble variant)
construction = [c for c in constructions if c.get('Name') == 'Advanced_Column_Stone_Base_WhiteMarble'][0]
recipe = recipes_data.get('Advanced_Column_Stone_Base_WhiteMarble')

# Analyze it
model = analyze_construction(construction, recipe, string_map, dlc_map)

print('Internal Name: Advanced_Column_Stone_Base_WhiteMarble')
print('Display Name:', model.get('DisplayName'))
print('Materials:', model.get('Materials'))
print('Set:', model.get('Set'))
print('DLC:', model.get('DLC'))
print('DefaultUnlockType:', model.get('DefaultUnlockType'))
print('SandboxUnlockType:', model.get('SandboxUnlockType'))
