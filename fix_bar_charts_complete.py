import json

# Read notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find and fix ALL chart sections
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Fix Section 4d: Top Gainers Chart (notebook display)
        if '## 4d. Top Gainers Chart (Grouped Bars)' in source:
            print("Found Section 4d (notebook display), fixing...")
            
            new_source = '''## 4d. Top Gainers Chart (Grouped Bars)
import matplotlib.pyplot as plt
import numpy as np


periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']

# For each period, find top 10 gainers (only positive returns)
top_gainers_by_period = {}
for period, label in zip(periods, period_labels):
    gainers = returns_df[returns_df[period] > 0].nlargest(10, period)[['Symbol', period]]
    top_gainers_by_period[label] = gainers

# Prepare horizontal bar chart data
fig, ax = plt.subplots(figsize=(14, 12))
y = np.arange(len(period_labels))
height = 0.16  # Doubled from 0.08 to 0.16 (100% increase)

# Plot horizontal bars grouped by period
for i, label in enumerate(period_labels):
    gainers = top_gainers_by_period[label]
    for j, (idx, row) in enumerate(gainers.iterrows()):
        sym = row['Symbol']
        val = row[periods[i]]
        offset = (j - 4.5) * height * 1.1  # Added 1.1 multiplier for spacing
        bar = ax.barh(y[i] + offset, val, height, alpha=0.8)
        
        if val > 0:
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

ax.set_ylabel('Period', fontsize=12, fontweight='bold')
ax.set_xlabel('Return %', fontsize=12, fontweight='bold')
ax.set_title('🟢 Top 10 Gainers by Period', fontsize=14, fontweight='bold', pad=20)
ax.set_yticks(y)
ax.set_yticklabels(period_labels, fontsize=11)
ax.axvline(0, color='black', linewidth=0.8, linestyle='-', alpha=0.3)
ax.grid(axis='x', alpha=0.3)
ax.set_xlim(left=0)

plt.tight_layout()
plt.show()'''
            cell['source'] = new_source.split('\n')
            print("Fixed Section 4d!")
        
        # Fix Section 4e: Top Losers Chart (notebook display)
        if '## 4e. Top Losers Chart (Grouped Bars)' in source:
            print("Found Section 4e (notebook display), fixing...")
            
            new_source = '''## 4e. Top Losers Chart (Grouped Bars)
# For each period, find top 10 losers (only negative returns)
top_losers_by_period = {}
for period, label in zip(periods, period_labels):
    losers = returns_df[returns_df[period] < 0].nsmallest(10, period)[['Symbol', period]]
    top_losers_by_period[label] = losers

# Prepare horizontal bar chart data
fig, ax = plt.subplots(figsize=(14, 12))
y = np.arange(len(period_labels))
height = 0.16  # Doubled from 0.08 to 0.16 (100% increase)

# Plot horizontal bars grouped by period
for i, label in enumerate(period_labels):
    losers = top_losers_by_period[label]
    for j, (idx, row) in enumerate(losers.iterrows()):
        sym = row['Symbol']
        val = row[periods[i]]
        offset = (j - 4.5) * height * 1.1  # Added 1.1 multiplier for spacing
        bar = ax.barh(y[i] + offset, val, height, alpha=0.8)
        
        if val < 0:
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

ax.set_ylabel('Period', fontsize=12, fontweight='bold')
ax.set_xlabel('Return %', fontsize=12, fontweight='bold')
ax.set_title('🔴 Top 10 Losers by Period', fontsize=14, fontweight='bold', pad=20)
ax.set_yticks(y)
ax.set_yticklabels(period_labels, fontsize=11)
ax.axvline(0, color='black', linewidth=0.8, linestyle='-', alpha=0.3)
ax.grid(axis='x', alpha=0.3)
ax.set_xlim(right=0)

plt.tight_layout()
plt.show()'''
            cell['source'] = new_source.split('\n')
            print("Fixed Section 4e!")
        
        # Fix create_top_losers_chart in email section
        if 'def create_top_losers_chart(returns_df):' in source and '## 11. Send Email' in source:
            print("Found email section with create_top_losers_chart, fixing...")
            
            # Replace just the function
            lines = source.split('\n')
            new_lines = []
            in_function = False
            skip_until_next_def = False
            
            for line in lines:
                if 'def create_top_losers_chart(returns_df):' in line:
                    in_function = True
                    skip_until_next_def = True
                    # Insert the corrected function
                    new_lines.append('def create_top_losers_chart(returns_df):')
                    new_lines.append('    periods = [\'1D_%\', \'2D_%\', \'5D_%\', \'10D_%\', \'1M_%\', \'3M_%\', \'6M_%\', \'1Y_%\']')
                    new_lines.append('    period_labels = [\'1D\', \'2D\', \'5D\', \'10D\', \'1M\', \'3M\', \'6M\', \'1Y\']')
                    new_lines.append('    ')
                    new_lines.append('    top_losers_by_period = {}')
                    new_lines.append('    for period, label in zip(periods, period_labels):')
                    new_lines.append('        losers = returns_df[returns_df[period] < 0].nsmallest(10, period)[[\'Symbol\', period]]')
                    new_lines.append('        top_losers_by_period[label] = losers')
                    new_lines.append('    ')
                    new_lines.append('    fig, ax = plt.subplots(figsize=(14, 12))')
                    new_lines.append('    y = np.arange(len(period_labels))')
                    new_lines.append('    height = 0.16  # Doubled from 0.08 to 0.16 (100% increase)')
                    new_lines.append('    ')
                    new_lines.append('    for i, label in enumerate(period_labels):')
                    new_lines.append('        losers = top_losers_by_period[label]')
                    new_lines.append('        for j, (idx, row) in enumerate(losers.iterrows()):')
                    new_lines.append('            sym = row[\'Symbol\']')
                    new_lines.append('            val = row[periods[i]]')
                    new_lines.append('            offset = (j - 4.5) * height * 1.1  # Added 1.1 multiplier for spacing')
                    new_lines.append('            bar = ax.barh(y[i] + offset, val, height, alpha=0.8)')
                    new_lines.append('            ')
                    new_lines.append('            if val < 0:')
                    new_lines.append('                # Percentage outside bar (left side)')
                    new_lines.append('                ax.text(val - 0.5, y[i] + offset,')
                    new_lines.append('                       f\'{val:.1f}%\',')
                    new_lines.append('                       ha=\'right\', va=\'center\',')
                    new_lines.append('                       fontsize=9, fontweight=\'bold\')')
                    new_lines.append('                # Stock name inside bar (right side)')
                    new_lines.append('                ax.text(-0.5, y[i] + offset,')
                    new_lines.append('                       f\'{sym}\',')
                    new_lines.append('                       ha=\'right\', va=\'center\',')
                    new_lines.append('                       fontsize=9, fontweight=\'bold\', color=\'white\')')
                    new_lines.append('    ')
                    new_lines.append('    ax.set_ylabel(\'Period\', fontsize=12, fontweight=\'bold\')')
                    new_lines.append('    ax.set_xlabel(\'Return %\', fontsize=12, fontweight=\'bold\')')
                    new_lines.append('    ax.set_title(\'🔴 Top 10 Losers by Period\', fontsize=14, fontweight=\'bold\', pad=20)')
                    new_lines.append('    ax.set_yticks(y)')
                    new_lines.append('    ax.set_yticklabels(period_labels, fontsize=11)')
                    new_lines.append('    ax.axvline(0, color=\'black\', linewidth=0.8, linestyle=\'-\', alpha=0.3)')
                    new_lines.append('    ax.grid(axis=\'x\', alpha=0.3)')
                    new_lines.append('    ax.set_xlim(right=0)')
                    new_lines.append('    plt.tight_layout()')
                    new_lines.append('    return fig')
                    new_lines.append('')
                    continue
                elif skip_until_next_def and (line.startswith('def ') or line.startswith('# ')):
                    skip_until_next_def = False
                    in_function = False
                
                if not skip_until_next_def:
                    new_lines.append(line)
            
            cell['source'] = new_lines
            print("Fixed email create_top_losers_chart!")

# Write back
with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("\nAll bar chart sections fixed successfully!")
print("Changes:")
print("- Bar height: 0.08 -> 0.16 (100% increase)")
print("- Offset spacing: added 1.1x multiplier to prevent overlap")
print("- Stock names: moved inside bars (white text)")
print("- Percentages: moved outside bars")
print("- Figure height: 10 -> 12 for better spacing")

# Made with Bob
