#!/usr/bin/env python3
"""
Apply all requested changes to NSE_Analysis.ipynb
"""
import json
import re

def modify_notebook():
    # Read the notebook
    with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    # Track changes
    changes_made = []
    
    # Process each cell
    for cell_idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue
            
        source = ''.join(cell['source'])
        original_source = source
        
        # Change 3: Add 1D period to compute_period_returns
        if 'def compute_period_returns(df):' in source:
            source = source.replace(
                "Returns dict with Symbol and % changes for 2d, 5d, 10d, 1m, 3m, 6m, 1y.",
                "Returns dict with Symbol and % changes for 1d, 2d, 5d, 10d, 1m, 3m, 6m, 1y."
            )
            source = source.replace(
                "    return {\n\n        'Current_Price': round(current_price, 2),\n\n        '2D_%': round(calc_return(2), 2),",
                "    return {\n\n        'Current_Price': round(current_price, 2),\n\n        '1D_%': round(calc_return(1), 2),\n\n        '2D_%': round(calc_return(2), 2),"
            )
            if source != original_source:
                changes_made.append(f"Cell {cell_idx}: Added 1D period to compute_period_returns")
        
        # Change 3: Add 1D to periods list
        if "periods = ['2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']" in source and 'period_names' in source:
            source = source.replace(
                "periods = ['2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']",
                "periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']"
            )
            source = source.replace(
                "period_names = {'2D_%': '2 Days', '5D_%': '5 Days', '10D_%': '10 Days',",
                "period_names = {'1D_%': '1 Day', '2D_%': '2 Days', '5D_%': '5 Days', '10D_%': '10 Days',"
            )
            if source != original_source:
                changes_made.append(f"Cell {cell_idx}: Added 1D to periods list")
        
        # Change 1 & 3: Top Gainers Chart
        if '## 4d. Top Gainers Chart (Grouped Bars)' in source:
            # Add 1D to periods
            source = source.replace(
                "periods = ['2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']\n\nperiod_labels = ['2D', '5D', '10D', '1M', '3M', '6M', '1Y']",
                "periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']\n\nperiod_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']"
            )
            # Enlarge chart
            source = source.replace(
                "fig, ax = plt.subplots(figsize=(14, 10))",
                "fig, ax = plt.subplots(figsize=(28, 20))"
            )
            source = source.replace(
                "height = 0.08",
                "height = 0.16"
            )
            # Move labels
            source = source.replace(
                "        # Add label on bar\n\n        if val > 0:\n\n            ax.text(val + 0.5, y[i] + offset,\n\n                   f'{sym} {val:.1f}%',\n\n                   ha='left', va='center',\n\n                   fontsize=7, fontweight='bold')",
                "        # Add symbol inside bar, percentage outside\n\n        if val > 0:\n\n            ax.text(val / 2, y[i] + offset,\n\n                   f'{sym}',\n\n                   ha='center', va='center',\n\n                   fontsize=14, fontweight='bold', color='white')\n\n            ax.text(val + 0.5, y[i] + offset,\n\n                   f'{val:.1f}%',\n\n                   ha='left', va='center',\n\n                   fontsize=14, fontweight='bold')"
            )
            # Increase font sizes
            source = source.replace(
                "ax.set_ylabel('Period', fontsize=12, fontweight='bold')\n\nax.set_xlabel('Return %', fontsize=12, fontweight='bold')\n\nax.set_title('🟢 Top 10 Gainers by Period', fontsize=14, fontweight='bold', pad=20)\n\nax.set_yticks(y)\n\nax.set_yticklabels(period_labels, fontsize=11)",
                "ax.set_ylabel('Period', fontsize=24, fontweight='bold')\n\nax.set_xlabel('Return %', fontsize=24, fontweight='bold')\n\nax.set_title('🟢 Top 10 Gainers by Period', fontsize=28, fontweight='bold', pad=20)\n\nax.set_yticks(y)\n\nax.set_yticklabels(period_labels, fontsize=22)"
            )
            if source != original_source:
                changes_made.append(f"Cell {cell_idx}: Modified Top Gainers Chart")
        
        # Change 1: Top Losers Chart
        if '## 4e. Top Losers Chart (Grouped Bars)' in source:
            # Enlarge chart
            source = source.replace(
                "fig, ax = plt.subplots(figsize=(14, 10))",
                "fig, ax = plt.subplots(figsize=(28, 20))"
            )
            source = source.replace(
                "height = 0.08",
                "height = 0.16"
            )
            # Move labels
            source = source.replace(
                "        # Add label on bar\n\n        if val < 0:\n\n            ax.text(val - 0.5, y[i] + offset,\n\n                   f'{sym} {val:.1f}%',\n\n                   ha='right', va='center',\n\n                   fontsize=7, fontweight='bold')",
                "        # Add symbol inside bar, percentage outside\n\n        if val < 0:\n\n            ax.text(val / 2, y[i] + offset,\n\n                   f'{sym}',\n\n                   ha='center', va='center',\n\n                   fontsize=14, fontweight='bold', color='white')\n\n            ax.text(val - 0.5, y[i] + offset,\n\n                   f'{val:.1f}%',\n\n                   ha='right', va='center',\n\n                   fontsize=14, fontweight='bold')"
            )
            # Increase font sizes
            source = source.replace(
                "ax.set_ylabel('Period', fontsize=12, fontweight='bold')\n\nax.set_xlabel('Return %', fontsize=12, fontweight='bold')\n\nax.set_title('🔴 Top 10 Losers by Period', fontsize=14, fontweight='bold', pad=20)\n\nax.set_yticks(y)\n\nax.set_yticklabels(period_labels, fontsize=11)",
                "ax.set_ylabel('Period', fontsize=24, fontweight='bold')\n\nax.set_xlabel('Return %', fontsize=24, fontweight='bold')\n\nax.set_title('🔴 Top 10 Losers by Period', fontsize=28, fontweight='bold', pad=20)\n\nax.set_yticks(y)\n\nax.set_yticklabels(period_labels, fontsize=22)"
            )
            if source != original_source:
                changes_made.append(f"Cell {cell_idx}: Modified Top Losers Chart")
        
        # Change 3: Update summary table
        if "## 4f. Period Returns Summary Table (Top 20)" in source:
            source = source.replace(
                "summary_cols = ['Symbol', 'Current_Price', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']",
                "summary_cols = ['Symbol', 'Current_Price', '1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']"
            )
            source = source.replace(
                "    .background_gradient(subset=['2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%'],",
                "    .background_gradient(subset=['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%'],"
            )
            source = source.replace(
                "    .format({'Current_Price': '{:.2f}', '2D_%': '{:.2f}', '5D_%': '{:.2f}',",
                "    .format({'Current_Price': '{:.2f}', '1D_%': '{:.2f}', '2D_%': '{:.2f}', '5D_%': '{:.2f}',"
            )
            if source != original_source:
                changes_made.append(f"Cell {cell_idx}: Updated summary table with 1D")
        
        # Change 2 & 3: Update interactive table
        if "## 4g. All Stocks Returns Table (Interactive)" in source:
            source = source.replace(
                "returns_table_df = returns_df[['Symbol', 'Current_Price', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']].copy()",
                "returns_table_df = returns_df[['Symbol', 'Current_Price', '1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']].copy()"
            )
            if source != original_source:
                changes_made.append(f"Cell {cell_idx}: Updated interactive table with 1D")
        
        # Change 6: Remove Section 8b chart
        if "## 8b. Chart — Top 10 Near 52W High / Low" in source:
            # Comment out the entire cell
            source = "# REMOVED: Section 8b - Near 52W High/Low chart (keeping only 8c)\n# " + source.replace('\n', '\n# ')
            changes_made.append(f"Cell {cell_idx}: Commented out Section 8b chart")
        
        # Update cell source if changed
        if source != original_source:
            cell['source'] = [line + '\n' for line in source.split('\n')[:-1]] + [source.split('\n')[-1]]
    
    # Write modified notebook
    with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    
    print(f"Applied {len(changes_made)} changes:")
    for change in changes_made:
        print(f"  - {change}")
    
    return changes_made

if __name__ == '__main__':
    changes = modify_notebook()
    print(f"\nSuccessfully modified NSE_Analysis.ipynb with {len(changes)} changes")

# Made with Bob
