import os
from collections import defaultdict

# Categorize all constructions without unlock sections
constructions_without_unlock = []

output_dir = "output/constructions"
for filename in sorted(os.listdir(output_dir)):
    if filename.endswith('.wiki'):
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if '== Unlock ==' not in content:
                display_name = filename.replace('.wiki', '')

                # Categorize
                is_dlc = '==DLC==' in content or '==DLC and Set==' in content
                is_set = '==Set==' in content or '==DLC and Set==' in content

                # Extract DLC/Set info
                dlc_set_info = ''
                for line in content.split('\n'):
                    if 'part of the {{LI|' in line:
                        dlc_set_info = line.split('{{LI|')[1].split('}}')[0]
                        break
                    elif "part of the '''" in line and 'Set' in line:
                        # Extract set name
                        parts = line.split("'''")
                        if len(parts) > 1:
                            dlc_set_info = parts[1]

                category = ''
                if is_dlc and not is_set:
                    category = 'DLC Only'
                elif is_set and not is_dlc:
                    category = 'Set Only'
                elif is_dlc and is_set:
                    category = 'DLC + Set'
                else:
                    category = 'Base Game'

                constructions_without_unlock.append({
                    'name': display_name,
                    'category': category,
                    'info': dlc_set_info
                })

# Group by category
grouped = defaultdict(list)
for item in constructions_without_unlock:
    grouped[item['category']].append(item)

print('COMPREHENSIVE ANALYSIS: CONSTRUCTIONS WITHOUT ==UNLOCK== SECTIONS')
print('='*80)
print()
print(f'Total: {len(constructions_without_unlock)} constructions')
print()
print('REASON: All constructions listed below have Manual unlock type, meaning they are')
print('either unlocked from the start, unlocked through DLC ownership, or unlocked')
print('through natural game progression without specific item/construction requirements.')
print()
print('='*80)
print()

for category in ['DLC + Set', 'DLC Only', 'Set Only', 'Base Game']:
    items = grouped[category]
    if items:
        print(f'\n{category.upper()}: {len(items)} constructions')
        print('-'*80)

        if category == 'DLC + Set':
            print('Reason: Part of a DLC pack AND a building set')
            print('Unlock: Automatically available when DLC is owned')
        elif category == 'DLC Only':
            print('Reason: Part of a DLC pack')
            print('Unlock: Automatically available when DLC is owned')
        elif category == 'Set Only':
            print('Reason: Part of a building set (e.g., Ancient, Crimson, Fair)')
            print('Unlock: Available from start or unlocked through progression')
        else:
            print('Reason: Base game content with Manual unlock')
            print('Unlock: Available from start or unlocked through natural progression')

        print()

        # Group by DLC/Set within category
        subcategories = defaultdict(list)
        for item in items:
            key = item['info'] if item['info'] else 'Unspecified'
            subcategories[key].append(item['name'])

        for subcat, names in sorted(subcategories.items()):
            print(f'  {subcat}: {len(names)} items')
            for i, name in enumerate(sorted(names), 1):
                print(f'    {i}. {name}')
            print()

print()
print('='*80)
print('SUMMARY BY CATEGORY')
print('='*80)
for category in ['DLC + Set', 'DLC Only', 'Set Only', 'Base Game']:
    items = grouped[category]
    if items:
        print(f'{category}: {len(items)} constructions')
