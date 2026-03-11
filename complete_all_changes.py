#!/usr/bin/env python3
"""
Complete all remaining changes to NSE_Analysis.ipynb
This script handles all 7 changes comprehensively
"""
import json
import re

def apply_all_changes():
    # Read notebook
    with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    changes = []
    
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue
        
        source = ''.join(cell['source'])
        orig = source
        
        # CHANGE 3: Add 1D period everywhere
        if 'def compute_period_returns' in source and '1D_%' not in source:
            source = source.replace(
                'Returns dict with Symbol and % changes for 2d',
                'Returns dict with Symbol and % changes for 1d, 2d'
            )
            source = re.sub(
                r"(\s+'Current_Price': round\(current_price, 2\),)\s+('2D_%')",
                r"\1\n\n        '1D_%': round(calc_return(1), 2),\n\n        \2",
                source
            )
        
        if "periods = ['2D_%'" in source and "'1D_%'" not in source:
            source = source.replace(
                "periods = ['2D_%'",
                "periods = ['1D_%', '2D_%'"
            )
            source = source.replace(
                "period_labels = ['2D'",
                "period_labels = ['1D', '2D'"
            )
            source = source.replace(
                "period_names = {'2D_%'",
                "period_names = {'1D_%': '1 Day', '2D_%'"
            )
        
        if "summary_cols = ['Symbol', 'Current_Price', '2D_%'" in source and "'1D_%'" not in source:
            source = source.replace(
                "summary_cols = ['Symbol', 'Current_Price', '2D_%'",
                "summary_cols = ['Symbol', 'Current_Price', '1D_%', '2D_%'"
            )
            source = source.replace(
                "subset=['2D_%'",
                "subset=['1D_%', '2D_%'"
            )
            source = source.replace(
                "{'Current_Price': '{:.2f}', '2D_%'",
                "{'Current_Price': '{:.2f}', '1D_%': '{:.2f}', '2D_%'"
            )
        
        if "returns_table_df = returns_df[['Symbol', 'Current_Price', '2D_%'" in source and "'1D_%'" not in source:
            source = source.replace(
                "returns_table_df = returns_df[['Symbol', 'Current_Price', '2D_%'",
                "returns_table_df = returns_df[['Symbol', 'Current_Price', '1D_%', '2D_%'"
            )
        
        # CHANGE 1: Enlarge charts and reposition labels
        if '## 4d. Top Gainers Chart' in source:
            source = source.replace('figsize=(14, 10)', 'figsize=(28, 20)')
            source = source.replace('height = 0.08', 'height = 0.16')
            source = source.replace('fontsize=7', 'fontsize=14')
            source = source.replace('fontsize=11', 'fontsize=22')
            source = source.replace('fontsize=12', 'fontsize=24')
            source = source.replace('fontsize=14', 'fontsize=28')
            
            # Replace label positioning
            old_label = """        # Add label on bar

        if val > 0:

            ax.text(val + 0.5, y[i] + offset,

                   f'{sym} {val:.1f}%',

                   ha='left', va='center',

                   fontsize=14, fontweight='bold')"""
            
            new_label = """        # Add symbol inside bar, percentage outside

        if val > 0:

            ax.text(val / 2, y[i] + offset,

                   f'{sym}',

                   ha='center', va='center',

                   fontsize=14, fontweight='bold', color='white')

            ax.text(val + 0.5, y[i] + offset,

                   f'{val:.1f}%',

                   ha='left', va='center',

                   fontsize=14, fontweight='bold')"""
            
            source = source.replace(old_label, new_label)
        
        if '## 4e. Top Losers Chart' in source:
            source = source.replace('figsize=(14, 10)', 'figsize=(28, 20)')
            source = source.replace('height = 0.08', 'height = 0.16')
            source = source.replace('fontsize=7', 'fontsize=14')
            source = source.replace('fontsize=11', 'fontsize=22')
            source = source.replace('fontsize=12', 'fontsize=24')
            source = source.replace('fontsize=14', 'fontsize=28')
            
            # Replace label positioning
            old_label = """        # Add label on bar

        if val < 0:

            ax.text(val - 0.5, y[i] + offset,

                   f'{sym} {val:.1f}%',

                   ha='right', va='center',

                   fontsize=14, fontweight='bold')"""
            
            new_label = """        # Add symbol inside bar, percentage outside

        if val < 0:

            ax.text(val / 2, y[i] + offset,

                   f'{sym}',

                   ha='center', va='center',

                   fontsize=14, fontweight='bold', color='white')

            ax.text(val - 0.5, y[i] + offset,

                   f'{val:.1f}%',

                   ha='right', va='center',

                   fontsize=14, fontweight='bold')"""
            
            source = source.replace(old_label, new_label)
        
        # CHANGE 2: Comment out Plotly interactive table
        if '## 4g. All Stocks Returns Table (Interactive)' in source and '! pip install plotly' in source:
            lines = source.split('\n')
            commented = ['# CHANGE 2: Removed interactive Plotly table - using CSV export instead']
            commented.extend(['# ' + line for line in lines])
            source = '\n'.join(commented)
        
        # CHANGE 6: Remove Section 8b
        if '## 8b. Chart — Top 10 Near 52W High / Low' in source:
            lines = source.split('\n')
            commented = ['# CHANGE 6: Removed Near 52W High/Low chart - keeping only 8c (52W Range)']
            commented.extend(['# ' + line for line in lines])
            source = '\n'.join(commented)
        
        # Update cell if changed
        if source != orig:
            cell['source'] = [line + '\n' for line in source.split('\n')[:-1]] + [source.split('\n')[-1]]
            changes.append(f"Cell {idx}: Modified")
    
    # Add new cells for CHANGE 5 (MACD heatmap) and CHANGE 7 (treemap)
    # Find insertion points
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # Insert MACD heatmap after Section 7
            if '## 7. Report 3 — MACD Signals' in source and 'display(r3_display' in source:
                # Add new cell for MACD heatmap
                new_cell = {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '## 7c. MACD Signals Heatmap\n',
                        'import matplotlib.pyplot as plt\n',
                        '\n',
                        'if not r3_display.empty:\n',
                        '    fig, ax = plt.subplots(figsize=(14, max(4, len(r3_display) * 0.5)))\n',
                        '    ax.axis(\'tight\')\n',
                        '    ax.axis(\'off\')\n',
                        '    \n',
                        '    # Prepare data\n',
                        '    table_data = []\n',
                        '    for _, row in r3_display.iterrows():\n',
                        '        table_data.append([\n',
                        '            row[\'Symbol\'],\n',
                        '            f"{row[\'MACD\']:.4f}",\n',
                        '            f"{row[\'Signal\']:.4f}",\n',
                        '            f"{row[\'Histogram\']:.4f}",\n',
                        '            \'✓\' if row[\'Bullish X\'] else \'\',\n',
                        '            \'✓\' if row[\'Above 0\'] else \'\',\n',
                        '            \'✓\' if row[\'Hist Inc\'] else \'\',\n',
                        '            str(row[\'Score\'])\n',
                        '        ])\n',
                        '    \n',
                        '    table = ax.table(\n',
                        '        cellText=table_data,\n',
                        '        colLabels=[\'Symbol\', \'MACD\', \'Signal\', \'Histogram\', \'Bull X\', \'Above 0\', \'Hist Inc\', \'Score\'],\n',
                        '        cellLoc=\'center\',\n',
                        '        loc=\'center\',\n',
                        '        bbox=[0, 0, 1, 1]\n',
                        '    )\n',
                        '    \n',
                        '    table.auto_set_font_size(False)\n',
                        '    table.set_fontsize(10)\n',
                        '    table.scale(1, 2)\n',
                        '    \n',
                        '    # Color code by score\n',
                        '    for i, row in enumerate(r3_display.itertuples(), start=1):\n',
                        '        score = row.Score\n',
                        '        if score == 3:\n',
                        '            color = \'#d4edda\'\n',
                        '        elif score == 2:\n',
                        '            color = \'#fff3cd\'\n',
                        '        else:\n',
                        '            color = \'#f8d7da\'\n',
                        '        for j in range(8):\n',
                        '            table[(i, j)].set_facecolor(color)\n',
                        '    \n',
                        '    # Header styling\n',
                        '    for j in range(8):\n',
                        '        table[(0, j)].set_facecolor(\'#4CAF50\')\n',
                        '        table[(0, j)].set_text_props(weight=\'bold\', color=\'white\')\n',
                        '    \n',
                        '    ax.set_title(\'MACD Signals Heatmap (Score ≥ 2)\', fontsize=14, fontweight=\'bold\', pad=20)\n',
                        '    plt.tight_layout()\n',
                        '    plt.show()\n',
                        'else:\n',
                        '    print(\'No MACD signals with score >= 2\')\n'
                    ]
                }
                nb['cells'].insert(idx + 1, new_cell)
                changes.append(f"Added MACD heatmap cell after cell {idx}")
                break
    
    # Add treemap cell
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            if '## 4e. Top Losers Chart' in source:
                new_cell = {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '## 4f. Top 1W Losers Treemap\n',
                        '# Install squarify if needed: pip install squarify\n',
                        'try:\n',
                        '    import squarify\n',
                        '    import matplotlib.pyplot as plt\n',
                        '    \n',
                        '    # Get 1W losers (using 5D as proxy for 1W)\n',
                        '    losers_1w = returns_df[returns_df[\'5D_%\'] < 0].nsmallest(15, \'5D_%\')[[\'Symbol\', \'5D_%\']]\n',
                        '    \n',
                        '    if not losers_1w.empty:\n',
                        '        # Prepare data\n',
                        '        labels = [f"{row[\'Symbol\']}\\n{row[\'5D_%\']:.1f}%" for _, row in losers_1w.iterrows()]\n',
                        '        sizes = [abs(val) for val in losers_1w[\'5D_%\']]\n',
                        '        colors = plt.cm.Reds([0.3 + (s / max(sizes)) * 0.6 for s in sizes])\n',
                        '        \n',
                        '        fig, ax = plt.subplots(figsize=(16, 10))\n',
                        '        squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.8, ax=ax,\n',
                        '                     text_kwargs={\'fontsize\': 12, \'weight\': \'bold\', \'color\': \'white\'})\n',
                        '        ax.set_title(\'Top 1W (5D) Losers - Treemap\', fontsize=16, fontweight=\'bold\', pad=20)\n',
                        '        ax.axis(\'off\')\n',
                        '        plt.tight_layout()\n',
                        '        plt.show()\n',
                        '    else:\n',
                        '        print(\'No 1W losers to display\')\n',
                        'except ImportError:\n',
                        '    print(\'squarify not installed. Run: pip install squarify\')\n'
                    ]
                }
                nb['cells'].insert(idx + 1, new_cell)
                changes.append(f"Added 1W losers treemap cell after cell {idx}")
                break
    
    # Write back
    with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    
    print(f"Applied {len(changes)} changes:")
    for c in changes:
        print(f"  - {c}")
    
    return len(changes)

if __name__ == '__main__':
    count = apply_all_changes()
    print(f"\nSuccessfully applied {count} changes to NSE_Analysis.ipynb")
    print("\nNext steps:")
    print("1. Add 'squarify' to requirements.txt")
    print("2. Update email generation functions to include new charts")
    print("3. Test the notebook")

# Made with Bob
