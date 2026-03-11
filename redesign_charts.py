import json

# Read notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# New design for Section 4d - Simple, clean subplots
new_4d_code = '''## 4d. Top Gainers Chart (Grouped Bars)
import matplotlib.pyplot as plt
import numpy as np

periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
period_names = {'1D_%': '1 Day', '2D_%': '2 Days', '5D_%': '5 Days', '10D_%': '10 Days', 
                '1M_%': '1 Month', '3M_%': '3 Months', '6M_%': '6 Months', '1Y_%': '1 Year'}

# Create figure with subplots (2 rows x 4 columns)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle('🟢 Top 10 Gainers by Period', fontsize=16, fontweight='bold', y=0.995)
axes = axes.flatten()

for idx, period in enumerate(periods):
    ax = axes[idx]
    
    # Get top 10 gainers for this period (only positive returns)
    gainers = returns_df[returns_df[period] > 0].nlargest(10, period)[['Symbol', period]]
    
    if not gainers.empty:
        # Sort by value for better visualization
        gainers = gainers.sort_values(period)
        
        # Create horizontal bar chart
        bars = ax.barh(range(len(gainers)), gainers[period], color='#2ecc71', alpha=0.8)
        
        # Add stock symbols on the left
        ax.set_yticks(range(len(gainers)))
        ax.set_yticklabels(gainers['Symbol'], fontsize=9)
        
        # Add percentage values on the bars
        for i, (val, bar) in enumerate(zip(gainers[period], bars)):
            ax.text(val + 0.3, i, f'{val:.1f}%', 
                   va='center', fontsize=8, fontweight='bold')
        
        ax.set_xlabel('Return %', fontsize=10)
        ax.set_title(period_names[period], fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        ax.set_xlim(left=0)
    else:
        ax.text(0.5, 0.5, 'No gainers', ha='center', va='center', 
               transform=ax.transAxes, fontsize=10)
        ax.set_title(period_names[period], fontsize=11, fontweight='bold')

plt.tight_layout()
plt.show()'''

# New design for Section 4e - Simple, clean subplots
new_4e_code = '''## 4e. Top Losers Chart (Grouped Bars)
# Create figure with subplots (2 rows x 4 columns)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle('🔴 Top 10 Losers by Period', fontsize=16, fontweight='bold', y=0.995)
axes = axes.flatten()

for idx, period in enumerate(periods):
    ax = axes[idx]
    
    # Get top 10 losers for this period (only negative returns)
    losers = returns_df[returns_df[period] < 0].nsmallest(10, period)[['Symbol', period]]
    
    if not losers.empty:
        # Sort by value for better visualization (most negative at bottom)
        losers = losers.sort_values(period, ascending=False)
        
        # Create horizontal bar chart
        bars = ax.barh(range(len(losers)), losers[period], color='#e74c3c', alpha=0.8)
        
        # Add stock symbols on the left
        ax.set_yticks(range(len(losers)))
        ax.set_yticklabels(losers['Symbol'], fontsize=9)
        
        # Add percentage values on the bars
        for i, (val, bar) in enumerate(zip(losers[period], bars)):
            ax.text(val - 0.3, i, f'{val:.1f}%', 
                   va='center', ha='right', fontsize=8, fontweight='bold')
        
        ax.set_xlabel('Return %', fontsize=10)
        ax.set_title(period_names[period], fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        ax.set_xlim(right=0)
    else:
        ax.text(0.5, 0.5, 'No losers', ha='center', va='center', 
               transform=ax.transAxes, fontsize=10)
        ax.set_title(period_names[period], fontsize=11, fontweight='bold')

plt.tight_layout()
plt.show()'''

# Find and replace the cells
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Replace Section 4d
        if '## 4d. Top Gainers Chart (Grouped Bars)' in source and 'plt.show()' in source:
            print("Replacing Section 4d with new design...")
            cell['source'] = new_4d_code.split('\n')
        
        # Replace Section 4e
        elif '## 4e. Top Losers Chart (Grouped Bars)' in source and 'plt.show()' in source:
            print("Replacing Section 4e with new design...")
            cell['source'] = new_4e_code.split('\n')

# Write back
with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("\n✅ Charts redesigned successfully!")
print("\nNew design features:")
print("- 2x4 subplot grid (one chart per period)")
print("- Clean horizontal bars")
print("- Stock symbols on Y-axis")
print("- Percentages labeled on bars")
print("- Much easier to read and compare")
print("- No overlapping labels")

# Made with Bob
