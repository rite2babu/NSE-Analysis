import json

# Read notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Track which cells we've modified
modified_count = 0

# Find and fix the specific cells by looking for the exact code patterns
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Check if this is the 4d cell (has the specific pattern)
        if 'height = 0.08' in source and 'Top 10 Gainers by Period' in source and 'for i, label in enumerate(period_labels):' in source:
            print(f"Found cell {i} with Top Gainers chart, modifying...")
            
            # Replace height and offset lines
            new_source = source.replace('height = 0.08', 'height = 0.16  # Doubled from 0.08')
            new_source = new_source.replace('offset = (j - 4.5) * height', 'offset = (j - 4.5) * height * 1.1  # Added spacing')
            new_source = new_source.replace('figsize=(14, 10)', 'figsize=(14, 12)')
            
            # Fix label positioning - stock name inside, percentage outside
            # Find and replace the text positioning
            if "ax.text(val + 0.5, y[i] + offset," in new_source:
                # Split at the text call
                parts = new_source.split("if val > 0:")
                if len(parts) == 2:
                    before = parts[0]
                    after_if = parts[1]
                    
                    # Replace the text section
                    new_text_section = '''
            # Stock name inside bar (left side)
            ax.text(0.5, y[i] + offset,
                   f'{sym}',
                   ha='left', va='center',
                   fontsize=9, fontweight='bold', color='white')
            # Percentage outside bar (right side)
            ax.text(val + 0.5, y[i] + offset,
                   f'{val:.1f}%',
                   ha='left', va='center',
                   fontsize=9, fontweight='bold')
'''
                    # Find where the old text block ends (before the next major section)
                    lines = after_if.split('\n')
                    new_lines = []
                    skip_lines = 0
                    for j, line in enumerate(lines):
                        if skip_lines > 0:
                            skip_lines -= 1
                            continue
                        if 'ax.text(val + 0.5' in line:
                            skip_lines = 5  # Skip the old text block
                            new_lines.append(new_text_section)
                        else:
                            new_lines.append(line)
                    
                    new_source = before + "if val > 0:" + '\n'.join(new_lines)
            
            cell['source'] = new_source.split('\n')
            modified_count += 1
            print(f"  Modified cell {i} (Gainers)")
        
        # Check if this is the 4e cell (has the specific pattern)
        elif 'height = 0.08' in source and 'Top 10 Losers by Period' in source and 'for i, label in enumerate(period_labels):' in source:
            print(f"Found cell {i} with Top Losers chart, modifying...")
            
            # Replace height and offset lines
            new_source = source.replace('height = 0.08', 'height = 0.16  # Doubled from 0.08')
            new_source = new_source.replace('offset = (j - 4.5) * height', 'offset = (j - 4.5) * height * 1.1  # Added spacing')
            new_source = new_source.replace('figsize=(14, 10)', 'figsize=(14, 12)')
            
            # Fix label positioning - percentage outside, stock name inside
            if "ax.text(val - 0.5, y[i] + offset," in new_source:
                parts = new_source.split("if val < 0:")
                if len(parts) == 2:
                    before = parts[0]
                    after_if = parts[1]
                    
                    new_text_section = '''
            # Percentage outside bar (left side)
            ax.text(val - 0.5, y[i] + offset,
                   f'{val:.1f}%',
                   ha='right', va='center',
                   fontsize=9, fontweight='bold')
            # Stock name inside bar (right side)
            ax.text(-0.5, y[i] + offset,
                   f'{sym}',
                   ha='right', va='center',
                   fontsize=9, fontweight='bold', color='white')
'''
                    lines = after_if.split('\n')
                    new_lines = []
                    skip_lines = 0
                    for j, line in enumerate(lines):
                        if skip_lines > 0:
                            skip_lines -= 1
                            continue
                        if 'ax.text(val - 0.5' in line:
                            skip_lines = 5
                            new_lines.append(new_text_section)
                        else:
                            new_lines.append(line)
                    
                    new_source = before + "if val < 0:" + '\n'.join(new_lines)
            
            cell['source'] = new_source.split('\n')
            modified_count += 1
            print(f"  Modified cell {i} (Losers)")

# Write back
with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"\nModified {modified_count} cells")
print("Changes:")
print("- Bar height: 0.08 -> 0.16")
print("- Offset spacing: * 1.1 multiplier added")
print("- Figure size: (14,10) -> (14,12)")
print("- Labels repositioned: names inside, percentages outside")

# Made with Bob
