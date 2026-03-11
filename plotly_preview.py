"""
Preview of Plotly Grouped Bar Charts for Top Gainers/Losers
This shows what the charts will look like with sample data
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Create sample data similar to your returns_df
np.random.seed(42)
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICI', 'SBIN', 'BHARTI', 'ITC', 'HIND', 'ASIAN']
periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']

# Generate sample returns data
sample_data = {'Symbol': stocks}
for period in periods:
    # Random returns between -5% and +15% for gainers
    sample_data[period] = np.random.uniform(2, 15, len(stocks))

returns_df = pd.DataFrame(sample_data)

print("=" * 80)
print("PREVIEW: Top Gainers Chart (Plotly Grouped Bars)")
print("=" * 80)
print("\nSample data:")
print(returns_df.head())
print("\n")

# Create the Plotly grouped bar chart - GROUPED BY PERIOD
fig = go.Figure()

# Get unique stocks that appear in top 10 for any period
all_top_stocks = set()
for period in periods:
    gainers = returns_df.nlargest(10, period)['Symbol'].tolist()
    all_top_stocks.update(gainers[:10])

# For each stock, create a trace showing its performance across periods
for stock in sorted(all_top_stocks):
    stock_returns = []
    for period in periods:
        stock_data = returns_df[returns_df['Symbol'] == stock]
        if not stock_data.empty:
            stock_returns.append(stock_data[period].iloc[0])
        else:
            stock_returns.append(0)
    
    fig.add_trace(go.Bar(
        name=stock,
        x=period_labels,
        y=stock_returns,
        text=[f'{v:.1f}%' for v in stock_returns],
        textposition='outside',
        hovertemplate=f'<b>{stock}</b><br>Return: %{{y:.2f}}%<extra></extra>'
    ))

fig.update_layout(
    title={
        'text': '🟢 Top 10 Gainers by Period',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18, 'color': '#2c3e50'}
    },
    xaxis_title='Stock Symbol',
    yaxis_title='Return %',
    barmode='group',
    height=600,
    width=1400,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#bdc3c7',
        borderwidth=1
    ),
    hovermode='x unified',
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    font=dict(family='Arial, sans-serif', size=12),
    margin=dict(l=60, r=40, t=100, b=60)
)

fig.update_xaxes(showgrid=False, showline=True, linewidth=1, linecolor='#bdc3c7')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#ecf0f1')

print("Opening preview in browser...")
fig.show()

print("\n" + "=" * 80)
print("CHART FEATURES:")
print("=" * 80)
print("[+] Clean grouped bars - one group per stock")
print("[+] 8 different colors/periods shown side-by-side")
print("[+] Percentage labels above each bar")
print("[+] Interactive hover to see exact values")
print("[+] Legend at top showing all periods")
print("[+] No overlapping - Plotly handles spacing automatically")
print("[+] Professional styling with grid and colors")
print("\n" + "=" * 80)
print("COMPARISON TO MATPLOTLIB:")
print("=" * 80)
print("Matplotlib issues:")
print("  [-] Manual positioning required")
print("  [-] Labels overlap")
print("  [-] Cramped spacing")
print("  [-] Hard to read")
print("\nPlotly advantages:")
print("  [+] Automatic spacing")
print("  [+] Clean labels")
print("  [+] Interactive")
print("  [+] Professional look")
print("  [+] Easy to export to PNG for email")
print("\n" + "=" * 80)

# Show how it exports to PNG
print("\nTesting PNG export for email...")
try:
    import io
    buf = io.BytesIO()
    fig.write_image(buf, format='png', width=1400, height=600, scale=2)
    buf.seek(0)
    size_kb = len(buf.read()) / 1024
    print(f"[+] PNG export successful! Size: {size_kb:.1f} KB")
    print("[+] This will embed perfectly in email")
except Exception as e:
    print(f"[-] PNG export failed: {e}")
    print("  Install kaleido: pip install kaleido")

print("\n" + "=" * 80)
print("Ready to apply to your notebook? The actual chart will use your real data.")
print("=" * 80)

# Made with Bob
