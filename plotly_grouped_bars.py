import json

# Read notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# New Section 4d using Plotly
new_4d_code = '''## 4d. Top Gainers Chart (Grouped Bars)
import plotly.graph_objects as go

periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']

# Get unique stocks that appear in top 10 gainers for any period
all_top_stocks = set()
for period in periods:
    gainers = returns_df[returns_df[period] > 0].nlargest(10, period)['Symbol'].tolist()
    all_top_stocks.update(gainers[:10])

# Create HORIZONTAL bar chart - grouped by PERIOD (periods on Y-axis)
fig = go.Figure()

for stock in sorted(all_top_stocks):
    stock_returns = []
    stock_labels = []  # For stock names inside bars
    stock_pcts = []    # For percentages outside bars
    
    for period in periods:
        stock_data = returns_df[returns_df['Symbol'] == stock]
        if not stock_data.empty and stock_data[period].iloc[0] > 0:
            val = stock_data[period].iloc[0]
            stock_returns.append(val)
            stock_labels.append(stock)  # Stock name
            stock_pcts.append(f'{val:.1f}%')  # Percentage
        else:
            stock_returns.append(None)
            stock_labels.append('')
            stock_pcts.append('')
    
    fig.add_trace(go.Bar(
        name=stock,
        y=period_labels,  # Periods on Y-axis
        x=stock_returns,  # Values on X-axis (horizontal)
        orientation='h',  # HORIZONTAL bars
        text=stock_labels,  # Stock name INSIDE bar
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(color='white', size=10, family='Arial Black'),
        hovertemplate=f'<b>{stock}</b><br>Return: %{{x:.2f}}%<extra></extra>',
        marker=dict(line=dict(width=0.5, color='white'))
    ))

# Add percentage labels OUTSIDE bars
for trace in fig.data:
    for i, (val, pct) in enumerate(zip(trace.x, stock_pcts)):
        if val:
            fig.add_annotation(
                x=val,
                y=period_labels[i],
                text=pct,
                xanchor='left',
                xshift=5,
                showarrow=False,
                font=dict(size=10, color='black', family='Arial')
            )

fig.update_layout(
    title={
        'text': '🟢 Top 10 Gainers by Period',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18}
    },
    yaxis_title='Period',
    xaxis_title='Return %',
    barmode='group',
    height=800,
    width=1400,
    showlegend=False,  # Hide legend since names are in bars
    hovermode='y unified',
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#ecf0f1')
)

fig.show()

# Save for email
import io
buf = io.BytesIO()
fig.write_image(buf, format='png', width=1400, height=800, scale=2)
buf.seek(0)
chart_images['top_gainers'] = buf.read()
print('Top Gainers chart saved for email')'''

# New Section 4e using Plotly
new_4e_code = '''## 4e. Top Losers Chart (Grouped Bars)
# Get unique stocks that appear in top 10 losers for any period
all_top_losers = set()
for period in periods:
    losers = returns_df[returns_df[period] < 0].nsmallest(10, period)['Symbol'].tolist()
    all_top_losers.update(losers[:10])

# Create HORIZONTAL bar chart - grouped by PERIOD (periods on Y-axis)
fig = go.Figure()

for stock in sorted(all_top_losers):
    stock_returns = []
    stock_labels = []  # For stock names inside bars
    stock_pcts = []    # For percentages outside bars
    
    for period in periods:
        stock_data = returns_df[returns_df['Symbol'] == stock]
        if not stock_data.empty and stock_data[period].iloc[0] < 0:
            val = stock_data[period].iloc[0]
            stock_returns.append(val)
            stock_labels.append(stock)  # Stock name
            stock_pcts.append(f'{val:.1f}%')  # Percentage
        else:
            stock_returns.append(None)
            stock_labels.append('')
            stock_pcts.append('')
    
    fig.add_trace(go.Bar(
        name=stock,
        y=period_labels,  # Periods on Y-axis
        x=stock_returns,  # Values on X-axis (horizontal)
        orientation='h',  # HORIZONTAL bars
        text=stock_labels,  # Stock name INSIDE bar
        textposition='inside',
        insidetextanchor='end',  # Right side for negative bars
        textfont=dict(color='white', size=10, family='Arial Black'),
        hovertemplate=f'<b>{stock}</b><br>Return: %{{x:.2f}}%<extra></extra>',
        marker=dict(line=dict(width=0.5, color='white'))
    ))

# Add percentage labels OUTSIDE bars
for trace in fig.data:
    for i, (val, pct) in enumerate(zip(trace.x, stock_pcts)):
        if val:
            fig.add_annotation(
                x=val,
                y=period_labels[i],
                text=pct,
                xanchor='right',
                xshift=-5,
                showarrow=False,
                font=dict(size=10, color='black', family='Arial')
            )

fig.update_layout(
    title={
        'text': '🔴 Top 10 Losers by Period',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18}
    },
    yaxis_title='Period',
    xaxis_title='Return %',
    barmode='group',
    height=800,
    width=1400,
    showlegend=False,  # Hide legend since names are in bars
    hovermode='y unified',
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#ecf0f1')
)

fig.show()

# Save for email
buf = io.BytesIO()
fig.write_image(buf, format='png', width=1400, height=800, scale=2)
buf.seek(0)
chart_images['top_losers'] = buf.read()
print('Top Losers chart saved for email')'''

# Find and replace the cells
modified = 0
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Replace Section 4d
        if '## 4d. Top Gainers Chart (Grouped Bars)' in source and 'plt.show()' in source:
            print("Replacing Section 4d with Plotly version...")
            cell['source'] = new_4d_code.split('\n')
            modified += 1
        
        # Replace Section 4e
        elif '## 4e. Top Losers Chart (Grouped Bars)' in source and 'plt.show()' in source:
            print("Replacing Section 4e with Plotly version...")
            cell['source'] = new_4e_code.split('\n')
            modified += 1

# Add chart_images initialization before Section 11 if not exists
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if '## 11. Send Email' in source or 'def create_top_losers_chart' in source:
            # Check if previous cell initializes chart_images
            if i > 0:
                prev_source = ''.join(nb['cells'][i-1]['source'])
                if 'chart_images' not in prev_source:
                    # Insert initialization cell
                    print("Adding chart_images initialization...")
                    new_cell = {
                        'cell_type': 'code',
                        'execution_count': None,
                        'metadata': {},
                        'outputs': [],
                        'source': ['# Initialize chart_images dictionary for email\n',
                                  'import io\n',
                                  'chart_images = {}\n',
                                  'print("Chart images dictionary initialized")']
                    }
                    nb['cells'].insert(i, new_cell)
                    modified += 1
            break

# Write back
with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Successfully modified {modified} sections!")
print("\nChanges made:")
print("- Replaced matplotlib with Plotly for grouped bar charts")
print("- Added automatic chart capture for email")
print("- Charts will be clean, professional, and properly spaced")
print("- No overlapping labels")
print("\nNote: You'll need to install kaleido for PNG export:")
print("  pip install kaleido")

# Made with Bob
