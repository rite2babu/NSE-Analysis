import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

# Load the notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Read stocks list
with open('stocks.txt', 'r') as f:
    stocks = [line.strip() for line in f if line.strip() and not line.startswith('#')]

print(f"Loaded {len(stocks)} stocks")

# Calculate returns for different periods
periods = {
    '1D': 1,
    '1W': 5,
    '1M': 21,
    '3M': 63,
    '6M': 126,
    '1Y': 252
}

returns_data = []
end_date = datetime.now()

print("Fetching stock data...")
for i, stock in enumerate(stocks[:20], 1):  # Limit to 20 stocks for quick verification
    try:
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1y')
        
        if len(hist) > 0:
            current_price = hist['Close'].iloc[-1]
            stock_returns = {'Stock': stock}
            
            for period_name, days in periods.items():
                if len(hist) >= days + 1:
                    past_price = hist['Close'].iloc[-(days + 1)]
                    ret = ((current_price - past_price) / past_price) * 100
                    stock_returns[period_name] = ret
                else:
                    stock_returns[period_name] = np.nan
            
            returns_data.append(stock_returns)
            print(f"  {i}/20: {stock} - Done")
    except Exception as e:
        print(f"  {i}/20: {stock} - Error: {str(e)}")

df_returns = pd.DataFrame(returns_data)
print(f"\nProcessed {len(df_returns)} stocks successfully")

# Create Top 10 Gainers chart (1W period)
if '1W' in df_returns.columns:
    top_gainers = df_returns.nlargest(10, '1W')[['Stock', '1W']].reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(top_gainers)))
    height = 0.16  # Doubled from 0.08
    
    for j, (idx, row) in enumerate(top_gainers.iterrows()):
        offset = (j - 4.5) * height * 1.1  # Added spacing
        bar = ax.barh(offset, row['1W'], height=height, color=colors[j], 
                     edgecolor='black', linewidth=1.5)
        
        # Stock name inside bar (white text)
        ax.text(row['1W']/2, offset, row['Stock'], 
               ha='center', va='center', fontsize=11, fontweight='bold', color='white')
        
        # Percentage outside bar (black text)
        ax.text(row['1W'] + 0.3, offset, f"{row['1W']:.2f}%", 
               ha='left', va='center', fontsize=10, fontweight='bold', color='black')
    
    ax.set_yticks([])
    ax.set_xlabel('Return (%)', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Gainers (1 Week)', fontsize=16, fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('verify_gainers_chart.png', dpi=150, bbox_inches='tight')
    print("\n✓ Gainers chart saved to verify_gainers_chart.png")
    plt.close()

# Create Top 10 Losers chart (1W period)
if '1W' in df_returns.columns:
    top_losers = df_returns.nsmallest(10, '1W')[['Stock', '1W']].reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_losers)))
    height = 0.16  # Doubled from 0.08
    
    for j, (idx, row) in enumerate(top_losers.iterrows()):
        offset = (j - 4.5) * height * 1.1  # Added spacing
        bar = ax.barh(offset, row['1W'], height=height, color=colors[j], 
                     edgecolor='black', linewidth=1.5)
        
        # Percentage outside bar (left side, black text)
        ax.text(row['1W'] - 0.3, offset, f"{row['1W']:.2f}%", 
               ha='right', va='center', fontsize=10, fontweight='bold', color='black')
        
        # Stock name inside bar (right side, white text)
        ax.text(row['1W']/2, offset, row['Stock'], 
               ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    
    ax.set_yticks([])
    ax.set_xlabel('Return (%)', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Losers (1 Week)', fontsize=16, fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('verify_losers_chart.png', dpi=150, bbox_inches='tight')
    print("✓ Losers chart saved to verify_losers_chart.png")
    plt.close()

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
print("\nBar Chart Configuration:")
print(f"  • Bar height: 0.16 (doubled from 0.08)")
print(f"  • Spacing: offset = (j - 4.5) * height * 1.1")
print(f"  • Figure size: 14x12")
print(f"\nGainers Chart:")
print(f"  • Stock names: Inside bars (white, centered)")
print(f"  • Percentages: Outside bars (black, right side)")
print(f"\nLosers Chart:")
print(f"  • Percentages: Outside bars (black, left side)")
print(f"  • Stock names: Inside bars (white, centered)")
print("\nPlease open the generated PNG files to visually verify:")
print("  1. verify_gainers_chart.png")
print("  2. verify_losers_chart.png")

# Made with Bob
