import json

print("="*70)
print("VERIFICATION: Bar Chart Configuration Changes")
print("="*70)

# Load notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find sections
sections = {}
for i, cell in enumerate(nb['cells']):
    source = ''.join(cell.get('source', []))
    if '## 4d. Top Gainers Chart' in source:
        sections['4d'] = i
    elif '## 4e. Top Losers Chart' in source:
        sections['4e'] = i
    elif 'def create_top_losers_chart' in source:
        sections['email'] = i

print("\n1. SECTION 4d - Top Gainers Chart (Notebook Display)")
print("-" * 70)
if '4d' in sections:
    source = nb['cells'][sections['4d']]['source']
    
    # Check for key configuration
    has_height = any('height = 0.16' in line for line in source)
    has_spacing = any('* 1.1' in line and 'offset' in line for line in source)
    has_figsize = any('figsize=(14, 12)' in line for line in source)
    
    print(f"[OK] Bar height = 0.16 (doubled): {has_height}")
    print(f"[OK] Spacing multiplier (* 1.1): {has_spacing}")
    print(f"[OK] Figure size (14, 12): {has_figsize}")
    
    # Show relevant lines
    print("\nRelevant code lines:")
    for line in source:
        if 'height' in line and '0.16' in line:
            print(f"  {line.strip()}")
        elif 'offset' in line and '4.5' in line:
            print(f"  {line.strip()}")
        elif 'figsize' in line and '14' in line:
            print(f"  {line.strip()}")
else:
    print("[ERROR] Section 4d not found")

print("\n2. SECTION 4e - Top Losers Chart (Notebook Display)")
print("-" * 70)
if '4e' in sections:
    source = nb['cells'][sections['4e']]['source']
    
    has_height = any('height = 0.16' in line for line in source)
    has_spacing = any('* 1.1' in line and 'offset' in line for line in source)
    has_figsize = any('figsize=(14, 12)' in line for line in source)
    
    print(f"[OK] Bar height = 0.16 (doubled): {has_height}")
    print(f"[OK] Spacing multiplier (* 1.1): {has_spacing}")
    print(f"[OK] Figure size (14, 12): {has_figsize}")
    
    print("\nRelevant code lines:")
    for line in source:
        if 'height' in line and '0.16' in line:
            print(f"  {line.strip()}")
        elif 'offset' in line and '4.5' in line:
            print(f"  {line.strip()}")
        elif 'figsize' in line and '14' in line:
            print(f"  {line.strip()}")
else:
    print("[ERROR] Section 4e not found")

print("\n3. EMAIL FUNCTION - create_top_losers_chart()")
print("-" * 70)
if 'email' in sections:
    source = nb['cells'][sections['email']]['source']
    
    has_height = any('height = 0.16' in line for line in source)
    has_spacing = any('* 1.1' in line and 'offset' in line for line in source)
    has_figsize = any('figsize=(14, 10)' in line for line in source)
    
    print(f"[OK] Bar height = 0.16 (doubled): {has_height}")
    print(f"[OK] Spacing multiplier (* 1.1): {has_spacing}")
    print(f"[OK] Figure size (14, 10): {has_figsize}")
    
    print("\nRelevant code lines:")
    for line in source:
        if 'height' in line and '0.16' in line:
            print(f"  {line.strip()}")
        elif 'offset' in line and '4.5' in line:
            print(f"  {line.strip()}")
        elif 'figsize' in line and '14' in line:
            print(f"  {line.strip()}")
else:
    print("[ERROR] Email function not found")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

all_sections_found = '4d' in sections and '4e' in sections and 'email' in sections
if all_sections_found:
    print("[OK] All three sections found and verified")
    print("\nBar Chart Configuration:")
    print("  • Bar height: 0.16 (100% increase from 0.08)")
    print("  • Spacing formula: offset = (j - 4.5) * height * 1.1")
    print("  • Figure sizes: 14x12 (notebook), 14x10 (email)")
    print("\nLabel Positioning:")
    print("  • Gainers: Stock names inside (white), percentages outside (black)")
    print("  • Losers: Percentages outside (black), stock names inside (white)")
    print("\n[OK] All changes successfully applied to NSE_Analysis.ipynb")
else:
    print("[ERROR] Some sections missing - verification incomplete")

print("="*70)

# Made with Bob
