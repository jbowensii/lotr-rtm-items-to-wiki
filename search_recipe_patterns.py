"""Search for recipes matching specific construction patterns."""

import json

# Load recipes
with open('source/DT_ConstructionRecipes.json', 'r') as f:
    recipes_data = json.load(f)

# Build mapping of what each recipe builds
recipe_builds_map = {}
all_recipe_names = []
for export in recipes_data.get('Exports', []):
    table = export.get('Table', {})
    if table:
        for recipe in table.get('Data', []):
            recipe_name = recipe.get('Name', '')
            all_recipe_names.append(recipe_name)

            # Default: recipe builds itself
            builds = recipe_name

            props = recipe.get('Value', [])
            for prop in props:
                if prop.get('Name') == 'ResultConstructionHandle':
                    handle_value = prop.get('Value')
                    if isinstance(handle_value, list):
                        for item in handle_value:
                            if isinstance(item, dict) and item.get('Name') == 'RowName':
                                builds = item.get('Value', recipe_name)
                                break

            recipe_builds_map[recipe_name] = builds

# Search for recipes that might match our categories
search_patterns = [
    'Slope',
    'Stairs',
    'Column',
    'Holiday',
    'Treasure',
    'Candelabra',
    'StringLight'
]

print('RECIPE PATTERNS SEARCH')
print('=' * 80)
print()

for pattern in search_patterns:
    print(f'\nPattern: {pattern}')
    print('-' * 80)
    matches = []
    for recipe_name, builds in recipe_builds_map.items():
        if pattern.lower() in recipe_name.lower() or pattern.lower() in builds.lower():
            matches.append((recipe_name, builds))

    for recipe_name, builds in sorted(set(matches)):
        if recipe_name != builds:
            print(f'  {recipe_name:<50} -> {builds}')
        else:
            print(f'  {recipe_name}')

    print(f'  Total: {len(matches)}')
