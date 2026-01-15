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

# Find Feast Table
matches = [c for c in constructions if 'Feast' in c.get('Name', '') and 'Table' in c.get('Name', '')]
print(f'Found {len(matches)} matching constructions:')
for c in matches:
    print(f'  {c.get("Name")}')

if matches:
    construction = matches[0]
    name = construction.get('Name')
    recipe = recipes_data.get(name)

    # Analyze it
    model = analyze_construction(construction, recipe, string_map, dlc_map)

    print(f'\nInternal Name: {name}')
    print(f'Display Name: {model.get("DisplayName")}')
    print(f'Materials: {model.get("Materials")}')
    print(f'Set: {model.get("Set")}')
    print(f'DLC: {model.get("DLC")}')
    print(f'DefaultUnlockType: {model.get("DefaultUnlockType")}')
    print(f'SandboxUnlockType: {model.get("SandboxUnlockType")}')
    print(f'Has recipe in recipes_data: {recipe is not None}')
