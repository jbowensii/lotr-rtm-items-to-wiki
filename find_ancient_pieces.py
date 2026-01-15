from generate_constructions_wiki import *
import json

string_map = load_all_string_tables('source/strings')
data = json.load(open('source/DT_Constructions.json', 'r', encoding='utf-8'))
exports = data.get('Exports', [])
constructions = []
[constructions.extend(export.get('Table', {}).get('Data', [])) for export in exports]

print("Looking for Ancient, Fair, and Crimson pieces...")
print()

for c in constructions:
    name = c.get('Name', '')
    props = c.get('Value', [])
    display = resolve_construction_display_name(name, props, string_map)

    if display and ('Ancient' in display or 'Fair' in display or 'Crimson' in display):
        # Determine set
        dlc_map = load_entitlements('source/DT_Entitlements.json')
        dlc_short_name = dlc_map.get(name)
        set_name = determine_set(name, display, dlc_short_name)

        print(f'{display}')
        print(f'  Internal: {name}')
        print(f'  Set: {set_name}')
        print(f'  DLC: {dlc_short_name}')
        print()
