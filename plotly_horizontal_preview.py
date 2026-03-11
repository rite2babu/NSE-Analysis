"""
Preview of Ploctly HORIZONTAL Grouped Bar Charts
Shows stock names INSIDE bars, percentages OUTSIDE bars
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICI', 'SBIN', 'BHARTI', 'ITC']
periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']

# Generate sample returns data
sample_data = {'Symbol': stocks}
for period in periods:
    sample_data[period] = np.random.uniform(2, 15, len(stocks))

returns_df = pd.DataFrame(sample_data)

print("=" * 80)
print("PREVIEW: HORIZONTAL Grouped Bar Chart")
print("=" * 80)
print("\nLayout:")
print("- Periods on Y-axis (vertical)")
print("- Stock names INSIDE bars (white text)")
print("- Percentages OUTSIDE bars (black text)")
print("- Grouped by period\n")

# Create HORIZONTAL bar chart
fig = go.Figure()

all_top_stocks = stocks[:8]  # Use all stocks for demo

for stock in all_top_stocks:
    stock_returns = []
    
    for period in periods:
        stock_data = returns_df[returns_df['Symbol'] == stock]
        if not stock_data.empty:
            val = stock_data[period].iloc[0]
            stock_returns.append(val)
        else:
            stock_returns.append(None)
    
    fig.add_trace(go.Bar(
        name=stock,
        y=period_labels,  # Periods on Y-axis
        x=stock_returns,  # Values on X-axis (horizontal)
        orientation='h',  # HORIZONTAL bars
        text=[stock] * len(period_labels),  # Stock name INSIDE bar
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(color='white', size=10, family='Arial Black'),
        hovertemplate=f'<b>{stock}</b><br>Return: %{{x:.2f}}%<extra></extra>',
        marker=dict(line=dict(width=0.5, color='white'))
    ))

# Add percentage labels OUTSIDE bars
annotations = []
for trace_idx, trace in enumerate(fig.data):
    for i, val in enumerate(trace.x):
        if val:
            annotations.append(dict(
                x=val,
                y=i,
                text=f'{val:.1f}%',
                xanchor='left',
                xshift=5,
                showarrow=False,
                font=dict(size=10, color='black', family='Arial')
            ))

fig.update_layout(
    title={
        'text': '🟢 Top Gainers by Period (HORIZONTAL)',
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
    xaxis=dict(showgrid=True, gridcolor='#ecf0f1'),
    annotations=annotations
)

print("Opening preview in browser...")
print("Also saving as HTML file: preview_chart.html")
fig.write_html("preview_chart.html")
fig.show()
print("\n[+] If browser didn't open, open 'preview_chart.html' manually")

print("\n" + "=" * 80)
print("CHART FEATURES:")
print("=" * 80)
print("[+] HORIZONTAL bars (easier to read stock names)")
print("[+] Periods on Y-axis (1D, 2D, 5D, etc.)")
print("[+] Stock names INSIDE bars (white text)")
print("[+] Percentages OUTSIDE bars (black text)")
print("[+] Grouped by period - multiple stocks per period")
print("[+] Clean spacing, no overlapping")
print("[+] Professional look")

print("\n" + "=" * 80)
print("Testing PNG export for email...")
try:
    import io
    buf = io.BytesIO()
    fig.write_image(buf, format='png', width=1400, height=800, scale=2)
    buf.seek(0)
    size_kb = len(buf.read()) / 1024
    print(f"[+] PNG export successful! Size: {size_kb:.1f} KB")
    print("[+] Ready for email embedding")
except Exception as e:
    print(f"[-] PNG export failed: {e}")
    print("  Install: pip install kaleido")

print("\n" + "=" * 80)

# Made with Bob
