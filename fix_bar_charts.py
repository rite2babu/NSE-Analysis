import json

# Read notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find and fix the create_top_gainers_chart function in notebook cells
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Fix create_top_gainers_chart
        if 'def create_top_gainers_chart(returns_df):' in source:
            print("Found create_top_gainers_chart, fixing...")
            
            # Replace the function
            new_source = '''def create_top_gainers_chart(returns_df):
    periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
    period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']
    
    top_gainers_by_period = {}
    for period, label in zip(periods, period_labels):
        gainers = returns_df[returns_df[period] > 0].nlargest(10, period)[['Symbol', period]]
        top_gainers_by_period[label] = gainers
    
    fig, ax = plt.subplots(figsize=(14, 10))
    y = np.arange(len(period_labels))
    height = 0.16  # Doubled from 0.08 to 0.16 (100% increase)
    
    for i, label in enumerate(period_labels):
        gainers = top_gainers_by_period[label]
        for j, (idx, row) in enumerate(gainers.iterrows()):
            sym = row['Symbol']
            val = row[periods[i]]
            offset = (j - 4.5) * height
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
    return fig
'''
            cell['source'] = new_source.split('\n')
            print("Fixed create_top_gainers_chart!")
        
        # Fix create_top_losers_chart
        if 'def create_top_losers_chart(returns_df):' in source:
            print("Found create_top_losers_chart, fixing...")
            
            new_source = '''def create_top_losers_chart(returns_df):
    periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
    period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']
    
    top_losers_by_period = {}
    for period, label in zip(periods, period_labels):
        losers = returns_df[returns_df[period] < 0].nsmallest(10, period)[['Symbol', period]]
        top_losers_by_period[label] = losers
    
    fig, ax = plt.subplots(figsize=(14, 10))
    y = np.arange(len(period_labels))
    height = 0.16  # Doubled from 0.08 to 0.16 (100% increase)
    
    for i, label in enumerate(period_labels):
        losers = top_losers_by_period[label]
        for j, (idx, row) in enumerate(losers.iterrows()):
            sym = row['Symbol']
            val = row[periods[i]]
            offset = (j - 4.5) * height
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
    return fig
'''
            cell['source'] = new_source.split('\n')
            print("Fixed create_top_losers_chart!")

# Write back
with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("\nBar chart functions fixed successfully!")
print("- Bar height doubled: 0.08 → 0.16 (100% increase)")
print("- Stock names moved inside bars")
print("- Percentages moved outside bars")

# Made with Bob
