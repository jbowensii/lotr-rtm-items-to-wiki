from generate_constructions_wiki import *

string_map = load_all_string_tables('source/strings')
name = string_map.get('Interactables.Brewery.Massive.Name')
print(f'Display name: {repr(name)}')
print(f'Codepoints: {[hex(ord(c)) for c in name]}')

# Load overrides
import json
with open('construction_unlock_overrides.json', 'r', encoding='utf-8') as f:
    overrides = json.load(f)

print(f'\nMatch found: {name in overrides}')
print(f'Override keys with Brew: {[k for k in overrides.keys() if "Brew" in k]}')
