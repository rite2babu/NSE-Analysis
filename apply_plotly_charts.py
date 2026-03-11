"""
Apply Plotly horizontal bar charts to NSE_Analysis.ipynb
Replaces matplotlib sections 4d and 4e with improved Plotly versions
"""

import json

# Read notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# New Section 4d - Plotly Gainers Chart with subplots
new_4d_code = '''## 4d. Top Gainers Chart (Plotly - Horizontal Bars)
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import io

periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']

# Get top 10 gainers for each period
top_gainers_by_period = {}
for period, label in zip(periods, period_labels):
    gainers = returns_df[returns_df[period] > 0].nlargest(10, period)[['Symbol', period]]
    top_gainers_by_period[label] = gainers

# Create subplots - one row per period
fig = make_subplots(
    rows=8, cols=1,
    subplot_titles=period_labels,
    vertical_spacing=0.02,
    row_heights=[1]*8
)

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

for row_idx, (period, label) in enumerate(zip(periods, period_labels), start=1):
    df = top_gainers_by_period[label]
    
    for idx, (_, stock_row) in enumerate(df.iterrows()):
        symbol = stock_row['Symbol']
        value = stock_row[period]
        
        fig.add_trace(
            go.Bar(
                x=[value],
                y=[symbol],
                orientation='h',
                marker=dict(color=colors[idx % len(colors)]),
                text=[symbol],
                textposition='inside',
                insidetextanchor='start',
                textfont=dict(size=14, color='white', family='Arial Black'),
                hovertemplate=f'<b>{symbol}</b><br>{value:.1f}%<extra></extra>',
                showlegend=False
            ),
            row=row_idx, col=1
        )
        
        # Add percentage outside bar
        fig.add_annotation(
            x=value,
            y=symbol,
            text=f'{value:.1f}%',
            xanchor='left',
            xshift=5,
            showarrow=False,
            font=dict(size=14, color='black', family='Arial Black'),
            row=row_idx, col=1
        )

fig.update_layout(
    title={
        'text': '🟢 Top 10 Gainers by Period',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20, 'color': '#2c3e50'}
    },
    height=2400,
    width=1400,
    showlegend=False,
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    margin=dict(l=100, r=100, t=80, b=40)
)

fig.update_xaxes(
    title_text='Return %',
    showgrid=True,
    gridcolor='#ecf0f1',
    range=[0, None]
)

fig.update_yaxes(
    showgrid=False,
    tickfont=dict(size=12)
)

fig.show()

# Save for email
try:
    buf = io.BytesIO()
    fig.write_image(buf, format='png', width=1400, height=2400, scale=2)
    buf.seek(0)
    if 'chart_images' not in globals():
        chart_images = {}
    chart_images['top_gainers'] = buf.read()
    print('Top Gainers chart saved for email')
except Exception as e:
    print(f'Could not save chart for email: {e}')
    print('Install kaleido: pip install kaleido')
'''

# New Section 4e - Plotly Losers Chart with subplots
new_4e_code = '''## 4e. Top Losers Chart (Plotly - Horizontal Bars)
# Get top 10 losers for each period
top_losers_by_period = {}
for period, label in zip(periods, period_labels):
    losers = returns_df[returns_df[period] < 0].nsmallest(10, period)[['Symbol', period]]
    top_losers_by_period[label] = losers

# Create subplots - one row per period
fig = make_subplots(
    rows=8, cols=1,
    subplot_titles=period_labels,
    vertical_spacing=0.02,
    row_heights=[1]*8
)

for row_idx, (period, label) in enumerate(zip(periods, period_labels), start=1):
    df = top_losers_by_period[label]
    
    for idx, (_, stock_row) in enumerate(df.iterrows()):
        symbol = stock_row['Symbol']
        value = stock_row[period]
        
        fig.add_trace(
            go.Bar(
                x=[value],
                y=[symbol],
                orientation='h',
                marker=dict(color=colors[idx % len(colors)]),
                text=[symbol],
                textposition='inside',
                insidetextanchor='end',
                textfont=dict(size=14, color='white', family='Arial Black'),
                hovertemplate=f'<b>{symbol}</b><br>{value:.1f}%<extra></extra>',
                showlegend=False
            ),
            row=row_idx, col=1
        )
        
        # Add percentage outside bar (left side for negative values)
        fig.add_annotation(
            x=value,
            y=symbol,
            text=f'{value:.1f}%',
            xanchor='right',
            xshift=-5,
            showarrow=False,
            font=dict(size=14, color='black', family='Arial Black'),
            row=row_idx, col=1
        )

fig.update_layout(
    title={
        'text': '🔴 Top 10 Losers by Period',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20, 'color': '#2c3e50'}
    },
    height=2400,
    width=1400,
    showlegend=False,
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    margin=dict(l=100, r=100, t=80, b=40)
)

fig.update_xaxes(
    title_text='Return %',
    showgrid=True,
    gridcolor='#ecf0f1',
    range=[None, 0]
)

fig.update_yaxes(
    showgrid=False,
    tickfont=dict(size=12)
)

fig.show()

# Save for email
try:
    buf = io.BytesIO()
    fig.write_image(buf, format='png', width=1400, height=2400, scale=2)
    buf.seek(0)
    if 'chart_images' not in globals():
        chart_images = {}
    chart_images['top_losers'] = buf.read()
    print('Top Losers chart saved for email')
except Exception as e:
    print(f'Could not save chart for email: {e}')
    print('Install kaleido: pip install kaleido')
'''

# Find and replace sections 4d and 4e
modified = 0
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Replace Section 4d
        if '## 4d. Top Gainers Chart (Grouped Bars)' in source and 'matplotlib' in source:
            print("Replacing Section 4d with Plotly version...")
            cell['source'] = new_4d_code.split('\n')
            modified += 1
        
        # Replace Section 4e  
        elif '## 4e. Top Losers Chart (Grouped Bars)' in source and 'matplotlib' in source:
            print("Replacing Section 4e with Plotly version...")
            cell['source'] = new_4e_code.split('\n')
            modified += 1

# Write back
with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"\n[+] Successfully modified {modified} sections!")
print("\nChanges made:")
print("- Replaced matplotlib with Plotly for sections 4d and 4e")
print("- Each period gets its own panel with 10 LARGE horizontal bars")
print("- Stock names INSIDE bars (white, bold, size 14)")
print("- Percentages OUTSIDE bars (black, bold, size 14)")
print("- Automatic chart capture for email")
print("- Charts are 2400px tall to fit all 8 periods")
print("\nNote: Install kaleido for PNG export:")
print("  pip install kaleido")

# Made with Bob
