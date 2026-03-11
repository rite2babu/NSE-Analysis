import json

with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print('='*70)
print('FINAL VERIFICATION - All Bar Chart Changes')
print('='*70)

# Check Cell 16 (4d Gainers)
print('\n1. Cell 16 - Section 4d (Top Gainers):')
src16 = nb['cells'][16]['source']
for line in src16:
    if 'height' in line or ('offset' in line and '4.5' in line) or ('figsize' in line and '14' in line):
        print(f'   {line.strip()}')

# Check Cell 18 (4e Losers)
print('\n2. Cell 18 - Section 4e (Top Losers):')
src18 = nb['cells'][18]['source']
for line in src18:
    if 'height' in line or ('offset' in line and '4.5' in line) or ('figsize' in line and '14' in line):
        print(f'   {line.strip()}')

# Find email function
print('\n3. Email Function - create_top_losers_chart():')
email_idx = [i for i, c in enumerate(nb['cells']) if 'def create_top_losers_chart' in ''.join(c.get('source', []))]
if email_idx:
    print(f'   Found at cell {email_idx[0]}')
    src_email = nb['cells'][email_idx[0]]['source']
    for line in src_email:
        if 'height' in line or ('offset' in line and '4.5' in line) or ('figsize' in line and '14' in line):
            print(f'   {line.strip()}')
else:
    print('   NOT FOUND')

print('\n' + '='*70)
print('VERIFICATION COMPLETE')
print('='*70)

# Made with Bob
