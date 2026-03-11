"""
Preview of Plotly HORIZONTAL Bar Charts - IMPROVED VERSION
Shows LARGE bars with stock names INSIDE and percentages OUTSIDE
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
periods = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']

# For each period, get top 10 gainers
top_gainers_by_period = {}
for period in periods:
    # Generate 10 random stocks with returns for this period
    stocks = [f'STOCK{i}' for i in range(1, 11)]
    returns = np.random.uniform(5, 20, 10)
    top_gainers_by_period[period] = pd.DataFrame({
        'Symbol': stocks,
        'Return': returns
    }).sort_values('Return', ascending=False)

print("=" * 80)
print("PREVIEW: HORIZONTAL Bar Chart - IMPROVED")
print("=" * 80)
print("\nLayout:")
print("- Each period gets 10 LARGE horizontal bars")
print("- Stock names INSIDE bars (white, bold)")
print("- Percentages OUTSIDE bars (black, bold)")
print("- Bars are THICK and easy to read\n")

# Create figure with subplots - one row per period
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=8, cols=1,
    subplot_titles=periods,
    vertical_spacing=0.02,
    row_heights=[1]*8
)

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

for row_idx, period in enumerate(periods, start=1):
    df = top_gainers_by_period[period]
    
    for idx, (_, stock_row) in enumerate(df.iterrows()):
        symbol = stock_row['Symbol']
        value = stock_row['Return']
        
        fig.add_trace(
            go.Bar(
                x=[value],
                y=[symbol],
                orientation='h',
                marker=dict(color=colors[idx % len(colors)]),
                text=[symbol],  # Stock name INSIDE
                textposition='inside',
                insidetextanchor='start',
                textfont=dict(size=14, color='white', family='Arial Black'),
                hovertemplate=f'<b>{symbol}</b><br>{value:.1f}%<extra></extra>',
                showlegend=False
            ),
            row=row_idx, col=1
        )
        
        # Add percentage OUTSIDE bar
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

# Update layout
fig.update_layout(
    title={
        'text': '🟢 Top 10 Gainers by Period - LARGE BARS',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20, 'color': '#2c3e50'}
    },
    height=2400,  # TALL to fit all periods
    width=1400,
    showlegend=False,
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    margin=dict(l=100, r=100, t=80, b=40)
)

# Update all x-axes
fig.update_xaxes(
    title_text='Return %',
    showgrid=True,
    gridcolor='#ecf0f1',
    range=[0, 25]
)

# Update all y-axes
fig.update_yaxes(
    showgrid=False,
    tickfont=dict(size=12)
)

print("Opening preview in browser...")
print("Also saving as HTML file: preview_chart_v2.html")
fig.write_html("preview_chart_v2.html")
fig.show()
print("\n[+] If browser didn't open, open 'preview_chart_v2.html' manually")

print("\n" + "=" * 80)
print("CHART FEATURES:")
print("=" * 80)
print("[+] LARGE horizontal bars (easy to read)")
print("[+] 8 periods, each with 10 stocks")
print("[+] Stock names INSIDE bars (white, bold, size 14)")
print("[+] Percentages OUTSIDE bars (black, bold, size 14)")
print("[+] Each period in separate panel")
print("[+] Clean spacing, no overlapping")
print("[+] Professional appearance")

print("\n" + "=" * 80)
print("Testing PNG export for email...")
try:
    import io
    buf = io.BytesIO()
    fig.write_image(buf, format='png', width=1400, height=2400, scale=2)
    buf.seek(0)
    size_kb = len(buf.read()) / 1024
    print(f"[+] PNG export successful! Size: {size_kb:.1f} KB")
    print("[+] Ready for email embedding")
except Exception as e:
    print(f"[-] PNG export failed: {e}")
    print("  Install: pip install kaleido")

print("\n" + "=" * 80)
print("This version has LARGE bars with text clearly visible!")
print("=" * 80)

# Made with Bob
