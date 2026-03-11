import json

with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if '## 4d' in source or '## 4e' in source:
            print(f"\nCell {i}:")
            print(f"First 200 chars: {source[:200]}")
            print(f"Contains matplotlib: {'matplotlib' in source}")

# Made with Bob
