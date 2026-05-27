#!/usr/bin/env python3
"""Fetch current stock prices from NSE"""
import os
import pandas as pd
from datetime import datetime, date
from data_fetcher import fetch_all_data
from config import load_stock_list

# Load stocks
stock_list = load_stock_list()
today = pd.Timestamp(date.today())
print(f'Fetching prices for {len(stock_list)} stocks (last 5 days including today if available)...\n')

# Fetch data (last 5 days) - data_fetcher will intelligently use cache or fetch from NSE
combined, skipped = fetch_all_data(stock_list, days=5, max_workers=5, use_cache=True)

# Get latest available prices for each stock
price_data = []
for symbol in combined['symbol'].unique():
    sym_data = combined[combined['symbol'] == symbol].sort_values('date')
    
    if len(sym_data) >= 2:
        latest = sym_data.iloc[-1]
        previous = sym_data.iloc[-2]
        gain_1d = ((latest['close'] - previous['close']) / previous['close']) * 100
        price_data.append({
            'Symbol': symbol,
            'Date': latest['date'].date(),
            'Current_Price': latest['close'],
            'Prev_Price': previous['close'],
            '1D_Gain_%': round(gain_1d, 2)
        })
    elif len(sym_data) == 1:
        latest = sym_data.iloc[-1]
        price_data.append({
            'Symbol': symbol,
            'Date': latest['date'].date(),
            'Current_Price': latest['close'],
            'Prev_Price': None,
            '1D_Gain_%': None
        })

latest_prices = pd.DataFrame(price_data)

print('\n' + '='*80)
if len(latest_prices) > 0:
    latest_prices = latest_prices.sort_values('1D_Gain_%', ascending=False, na_position='last')
    latest_date = latest_prices['Date'].max()
    print(f'LATEST STOCK PRICES (as of {latest_date}) - Sorted by 1D Gain %')
    print('='*80)
    print(latest_prices.to_string(index=False))
    print('='*80)
    print(f'\nTotal: {len(latest_prices)} stocks')
    if latest_date == today.date():
        print(f'[OK] Data is from today ({today.date()})')
    else:
        print(f'[INFO] Latest available data is from {latest_date} (today is {today.date()})')
else:
    print('No data available')
    print('='*80)

if skipped:
    print(f'Skipped: {len(skipped)} stocks - {skipped}')

# Made with Bob
