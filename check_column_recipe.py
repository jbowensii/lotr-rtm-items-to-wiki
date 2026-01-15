from generate_constructions_wiki import *
import json

recipes_data = load_recipes_data('source/DT_ConstructionRecipes.json')
recipe = recipes_data.get('Advanced_Column_Stone_Base')
print('Recipe found:', recipe is not None)

if recipe:
    props = recipe.get('Value', [])
    print('Properties in recipe:')
    for prop in props:
        prop_name = prop.get('Name')
        print(f'  {prop_name}')

    default_mats_prop = get_property_value(props, 'DefaultRequiredMaterials')
    print('Has DefaultRequiredMaterials:', default_mats_prop is not None)
    if default_mats_prop:
        print('DefaultRequiredMaterials count:', len(default_mats_prop))
        print('DefaultRequiredMaterials:', default_mats_prop)
