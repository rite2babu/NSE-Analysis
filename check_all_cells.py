import json

with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
print("\nLooking for section 4d and 4e...")

for i, cell in enumerate(nb['cells']):
    source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    
    if '4d' in source.lower() or '4e' in source.lower():
        print(f"\nCell {i} ({cell['cell_type']}):")
        print(f"First 150 chars: {source[:150]}")

# Made with Bob
