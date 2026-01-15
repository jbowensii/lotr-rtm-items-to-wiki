"""Generate detailed exclusion report with internal and display names."""

# Parse the exclusion log
with open('output/excluded_constructions.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Organize by reason
exclusions = {
    'No recipe data': [],
    'Duplicate display name (kept first)': [],
    'Superseded by V2 version': [],
    'Contains \'Broken\'': [],
    'Internal name starts with [': [],
    'Display name starts with [': [],
    'Internal name starts with _Beorn': [],
    'Display name starts with _': [],
    'Display name starts with _ or *': [],
}

for line in lines:
    line = line.strip()
    if line.startswith('- '):
        # Parse: - InternalName (DisplayName) - Reason: ReasonText
        parts = line.split(' - Reason: ')
        if len(parts) == 2:
            item_part = parts[0][2:]  # Remove '- '
            reason = parts[1]

            # Extract internal name and display name
            if '(' in item_part and ')' in item_part:
                internal = item_part[:item_part.index('(')].strip()
                display = item_part[item_part.index('(')+1:item_part.index(')')].strip()
            else:
                internal = item_part
                display = 'N/A'

            if reason in exclusions:
                exclusions[reason].append((internal, display))

# Print organized report with table format
print('=' * 120)
print('DETAILED EXCLUSION REPORT - CONSTRUCTIONS')
print('=' * 120)
print()

total = 0
for reason, items in exclusions.items():
    if items:
        total += len(items)
        print(f'\n{reason.upper()}: {len(items)} ITEMS')
        print('=' * 120)
        print(f"{'Internal Name (Game)':<60} | {'Display Name (Wiki)':<55}")
        print('-' * 120)

        for internal, display in sorted(items):
            display_str = display if display and display != 'N/A' else '(No display name)'
            print(f'{internal:<60} | {display_str:<55}')

print()
print('=' * 120)
print(f'TOTAL EXCLUDED: {total} constructions')
print('=' * 120)
