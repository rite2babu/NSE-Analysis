#!/usr/bin/env python3
"""
Fix the email chart function to add spacing multiplier to offset calculation.
This ensures bars don't overlap when height is doubled.
"""

import json
import sys

def fix_email_chart():
    # Read the notebook
    with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    changes_made = 0
    
    # Find and fix the create_top_losers_chart function
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = cell['source']
            source_str = ''.join(source)
            
            # Look for the create_top_losers_chart function
            if 'def create_top_losers_chart(returns_df):' in source_str:
                print("Found create_top_losers_chart function")
                
                # Find and replace the offset line
                new_source = []
                for i, line in enumerate(source):
                    if 'offset = (j - 4.5) * height' in line and '* 1.1' not in line:
                        # Replace with spacing multiplier
                        new_line = line.replace(
                            'offset = (j - 4.5) * height',
                            'offset = (j - 4.5) * height * 1.1  # Added spacing'
                        )
                        new_source.append(new_line)
                        print(f"  Fixed line {i}: {line.strip()} -> {new_line.strip()}")
                        changes_made += 1
                    else:
                        new_source.append(line)
                
                if changes_made > 0:
                    cell['source'] = new_source
    
    if changes_made > 0:
        # Write back
        with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"\n✓ Successfully updated {changes_made} line(s) in email chart function")
        return 0
    else:
        print("\n✗ No changes needed or function not found")
        return 1

if __name__ == '__main__':
    sys.exit(fix_email_chart())

# Made with Bob
