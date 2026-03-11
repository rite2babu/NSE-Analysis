#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE Stock Analysis - Complete Python Version
Fetches 1 year OHLCV data, generates analysis reports, charts, and sends email
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime
import datetime as dt
import os
import time
import requests
import concurrent.futures
from nselib import capital_market
import nselib.capital_market.capital_market_data as _cm_data
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import plotly.graph_objects as go
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# ============================================================================
# CONFIGURATION
# ============================================================================

# Email configuration (read from environment or use defaults)
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'peri47.study@gmail.com')
EMAIL_TO = os.environ.get('EMAIL_TO', 'peri47.study@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'fhih lsqp wanu leic')

def load_config():
    """Load configuration from stocks.txt"""
    with open('stocks.txt', 'r') as f:
        stock_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    config = {
        'stock_list': stock_list,
        'max_workers': 5,
        'days': 365,
        'output_dir': 'dump'
    }
    
    print(f'[OK] Loaded {len(stock_list)} stocks from stocks.txt')
    return config

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compute_period_hl(df):
    """Calculate high/low for various periods"""
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    
    def window_hl(days):
        rows = df.tail(days)
        return rows['high'].max(), rows['low'].min()
    
    h52, l52 = window_hl(min(252, n))
    h26, l26 = window_hl(min(126, n))
    h4, l4 = window_hl(min(20, n))
    h1, l1 = window_hl(min(5, n))
    current = df['close'].iloc[-1]
    rng = h52 - l52
    pos = (current - l52) / rng * 100 if rng > 0 else float('nan')
    
    return {
        'Current_Price': round(current, 2),
        '52W_High': round(h52, 2), '52W_Low': round(l52, 2),
        '26W_High': round(h26, 2), '26W_Low': round(l26, 2),
        '4W_High': round(h4, 2), '4W_Low': round(l4, 2),
        '1W_High': round(h1, 2), '1W_Low': round(l1, 2),
        '52W_Position': round(pos, 2) if pos == pos else float('nan'),
    }

def compute_sma_crossovers(df):
    """Calculate SMA crossover signals"""
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    close = df['close']
    
    sma = {p: close.rolling(p).mean() if n >= p else pd.Series([float('nan')]*n, index=df.index)
           for p in [5, 10, 20, 50, 100, 200]}
    
    results = []
    for label, short_p, long_p in [('200/20', 20, 200), ('100/10', 10, 100), ('50/5', 5, 50)]:
        s, l = sma[short_p], sma[long_p]
        if s.isna().all() or l.isna().all():
            continue
        
        cross = (s > l) & (s.shift(1) <= l.shift(1))
        last5_cross = cross.iloc[-5:].any() if n >= 5 else False
        cross_dates = df['date'][cross]
        last_cross_date = cross_dates.iloc[-1].strftime('%Y-%m-%d') if not cross_dates.empty and last5_cross else None
        
        s_last, l_last = s.iloc[-1], l.iloc[-1]
        if pd.isna(s_last) or pd.isna(l_last):
            continue
        
        cross_pct = (s_last - l_last) / l_last * 100
        results.append({
            'cross_type': label,
            'crossed_last_5d': bool(last5_cross),
            'last_cross_date': last_cross_date,
            'nearing': bool(-1.0 <= cross_pct <= 0),
            'cross_pct': round(cross_pct, 3),
        })
    
    return results

def compute_macd(df):
    """Calculate MACD indicators"""
    df = df.sort_values('date').reset_index(drop=True)
    close = df['close']
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    
    n = len(df)
    cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
    bullish_cross = cross.iloc[-5:].any() if n >= 5 else False
    above_zero = bool(macd_line.iloc[-1] > 0)
    
    hist_inc = False
    if n >= 3:
        h = histogram.iloc[-3:].values
        hist_inc = bool(h[1] > h[0] and h[2] > h[1])
    
    score = int(bullish_cross) + int(above_zero) + int(hist_inc)
    
    return {
        'MACD': round(macd_line.iloc[-1], 4),
        'Signal': round(signal_line.iloc[-1], 4),
        'Histogram': round(histogram.iloc[-1], 4),
        'Bullish_Cross': bool(bullish_cross),
        'Above_Zero': above_zero,
        'Hist_Increasing': hist_inc,
        'MACD_Score': score,
    }

def compute_period_returns(df):
    """Calculate percentage returns over multiple periods"""
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    
    if n < 2:
        return None
    
    current_price = df['close'].iloc[-1]
    
    def calc_return(days_back):
        if n <= days_back:
            return float('nan')
        past_price = df['close'].iloc[-(days_back + 1)]
        if past_price == 0:
            return float('nan')
        return ((current_price - past_price) / past_price) * 100
    
    return {
        'Current_Price': round(current_price, 2),
        '1D_%': round(calc_return(1), 2),
        '2D_%': round(calc_return(2), 2),
        '5D_%': round(calc_return(5), 2),
        '10D_%': round(calc_return(10), 2),
        '1M_%': round(calc_return(21), 2),
        '3M_%': round(calc_return(63), 2),
        '6M_%': round(calc_return(126), 2),
        '1Y_%': round(calc_return(252), 2),
    }

# ============================================================================
# DATA FETCHING
# ============================================================================

def init_session():
    """Initialize shared NSE session"""
    print('Initialising NSE session...')
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.nseindia.com/',
    })
    
    r0 = session.get('https://www.nseindia.com/', timeout=30)
    print(f'  Session: HTTP {r0.status_code}')
    time.sleep(2)
    
    def shared_urlfetch(url, origin_url='http://nseindia.com'):
        return session.get(url, timeout=30)
    
    _cm_data.nse_urlfetch = shared_urlfetch
    return session

def fetch_one(sym, start_date, end_date):
    """Fetch data for one symbol"""
    df = capital_market.price_volume_data(symbol=sym, from_date=start_date, to_date=end_date)
    
    for col in ['HighPrice', 'LowPrice', 'OpenPrice', 'ClosePrice', 'TotalTradedQuantity']:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False).astype(float)
    
    df = df.rename(columns={
        'Symbol': 'symbol', 'Date': 'date',
        'HighPrice': 'high', 'LowPrice': 'low',
        'OpenPrice': 'open', 'ClosePrice': 'close',
        'TotalTradedQuantity': 'volume'
    })
    
    df['symbol'] = sym
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%Y')
    return df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]

def fetch_all_data(config):
    """Fetch data for all stocks in parallel"""
    end_date = dt.date.today().strftime('%d-%m-%Y')
    start_date = (dt.date.today() - dt.timedelta(days=config['days'])).strftime('%d-%m-%Y')
    print(f'Date range: {start_date} to {end_date}')
    
    init_session()
    
    skipped = []
    frames = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
        future_map = {executor.submit(fetch_one, sym, start_date, end_date): sym 
                     for sym in config['stock_list']}
        
        for future in concurrent.futures.as_completed(future_map):
            sym = future_map[future]
            try:
                df = future.result()
                print(f'  [OK] {sym:20s} {len(df)} rows')
                frames.append(df)
            except Exception as e:
                print(f'  [SKIP] {sym:20s} {e}')
                skipped.append(sym)
    
    if skipped:
        print(f'\nSkipped: {skipped}')
    
    if not frames:
        raise ValueError('No data fetched')
    
    combined = pd.concat(frames, ignore_index=True)
    combined.sort_values(['symbol', 'date'], inplace=True)
    combined.reset_index(drop=True, inplace=True)
    print(f'[OK] Combined: {len(combined)} rows, {combined["symbol"].nunique()} stocks')
    
    return combined, skipped

# ============================================================================
# ANALYSIS
# ============================================================================

def compute_all_metrics(combined):
    """Compute all metrics for all stocks"""
    print('Computing metrics...')
    
    hl_rows = []
    cross_rows = []
    macd_rows = []
    return_rows = []
    
    for sym, grp in combined.groupby('symbol'):
        grp = grp.sort_values('date').reset_index(drop=True)
        
        # High/Low
        try:
            hl = compute_period_hl(grp)
            hl['Symbol'] = sym
            hl_rows.append(hl)
        except Exception as e:
            print(f'  Warning [{sym}] HL: {e}')
        
        # Crossovers
        try:
            if len(grp) >= 5:
                for c in compute_sma_crossovers(grp):
                    c['Symbol'] = sym
                    cross_rows.append(c)
        except Exception as e:
            print(f'  Warning [{sym}] SMA: {e}')
        
        # MACD
        try:
            macd = compute_macd(grp)
            macd['Symbol'] = sym
            macd_rows.append(macd)
        except Exception as e:
            print(f'  Warning [{sym}] MACD: {e}')
        
        # Returns
        try:
            ret = compute_period_returns(grp)
            if ret:
                ret['Symbol'] = sym
                return_rows.append(ret)
        except Exception as e:
            print(f'  Warning [{sym}] Returns: {e}')
    
    hl_df = pd.DataFrame(hl_rows)
    cross_df = pd.DataFrame(cross_rows) if cross_rows else pd.DataFrame()
    macd_df = pd.DataFrame(macd_rows)
    returns_df = pd.DataFrame(return_rows)
    
    print(f'[OK] Metrics: {len(hl_df)} HL, {len(cross_df)} crossovers, {len(macd_df)} MACD, {len(returns_df)} returns')
    
    return hl_df, cross_df, macd_df, returns_df

# ============================================================================
# REPORTS
# ============================================================================

def generate_reports(hl_df, cross_df, macd_df, returns_df):
    """Generate all analysis reports"""
    print('\n' + '='*80)
    print('ANALYSIS REPORTS')
    print('='*80)
    
    # Report 1: 52W Position
    print('\n[REPORT 1] 52W Hi/Low Position (Top 20)')
    r1 = hl_df[['Symbol', 'Current_Price', '52W_High', '52W_Low', '52W_Position']].sort_values('52W_Position')
    print(r1.head(20).to_string(index=False))
    
    # Report 2: Crossovers
    print('\n[REPORT 2] Golden Crossover Signals')
    crossed = pd.DataFrame()
    nearing = pd.DataFrame()
    
    if not cross_df.empty:
        crossed = cross_df[cross_df['crossed_last_5d'] == True][['Symbol', 'cross_type', 'cross_pct', 'last_cross_date']]
        if not crossed.empty:
            print('\n[OK] Crossed in last 5 days:')
            print(crossed.to_string(index=False))
        
        nearing = cross_df[cross_df['nearing'] == True][['Symbol', 'cross_type', 'cross_pct']]
        if not nearing.empty:
            print('\n[OK] Nearing crossover:')
            print(nearing.to_string(index=False))
    else:
        print('  (no crossover data)')
    
    # Report 3: MACD
    print('\n[REPORT 3] MACD Signals (Score >= 2)')
    r3 = macd_df[macd_df['MACD_Score'] >= 2].sort_values('MACD_Score', ascending=False)
    r3_display = pd.DataFrame()
    
    if not r3.empty:
        r3_display = r3[['Symbol', 'MACD', 'Signal', 'Histogram', 'MACD_Score']]
        print(r3_display.to_string(index=False))
    else:
        print('  (no stocks with MACD score >= 2)')
    
    # Report 4: Near 52W High/Low
    print('\n[REPORT 4] Near 52W High / Low')
    near_high = hl_df[hl_df['52W_Position'] >= 80].sort_values('52W_Position', ascending=False).head(10)
    near_low = hl_df[hl_df['52W_Position'] <= 20].sort_values('52W_Position').head(10)
    
    if not near_high.empty:
        print('\n[OK] Near 52W HIGH (>=80%):')
        print(near_high[['Symbol', 'Current_Price', '52W_Position']].to_string(index=False))
    
    if not near_low.empty:
        print('\n[OK] Near 52W LOW (<=20%):')
        print(near_low[['Symbol', 'Current_Price', '52W_Position']].to_string(index=False))
    
    # Report 5: Top Gainers/Losers
    print('\n[REPORT 5] Top Movers (1 Month)')
    gainers = returns_df[returns_df['1M_%'] > 0].nlargest(10, '1M_%')[['Symbol', 'Current_Price', '1M_%']]
    losers = returns_df[returns_df['1M_%'] < 0].nsmallest(10, '1M_%')[['Symbol', 'Current_Price', '1M_%']]
    
    if not gainers.empty:
        print('\n[+] TOP 10 GAINERS (1M):')
        print(gainers.to_string(index=False))
    
    if not losers.empty:
        print('\n[-] TOP 10 LOSERS (1M):')
        print(losers.to_string(index=False))
    
    return {
        'r1': r1,
        'crossed': crossed if not cross_df.empty else pd.DataFrame(),
        'nearing': nearing if not cross_df.empty else pd.DataFrame(),
        'r3': r3_display if not r3.empty else pd.DataFrame(),
        'near_high': near_high,
        'near_low': near_low
    }

# ============================================================================
# CHART GENERATION
# ============================================================================

def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    return buf.read()

def create_52w_position_chart(r1):
    """Create 52W position bar chart for all stocks"""
    plot_df = r1[['Symbol', '52W_Position']].set_index('Symbol').sort_values('52W_Position')
    colors = ['#e74c3c' if v <= 20 else '#2ecc71' if v >= 80 else '#3498db' for v in plot_df['52W_Position']]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_df.plot.barh(ax=ax, color=colors, legend=False)
    ax.set_xlabel('52W Position %')
    ax.set_title('All Stocks — 52-Week Position', fontsize=12)
    ax.axvline(20, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.6)
    ax.axvline(80, color='#2ecc71', linestyle='--', linewidth=1, alpha=0.6)
    plt.tight_layout()
    return fig

def create_macd_chart(macd_df):
    """Create MACD score and histogram charts"""
    m2 = macd_df[['Symbol', 'MACD', 'Signal', 'Histogram', 'MACD_Score']].copy()
    m2 = m2.sort_values(['MACD_Score', 'Histogram'], ascending=True).tail(15).set_index('Symbol')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('MACD Overview — Top 15', fontsize=13, fontweight='bold')
    
    sc = {0: '#e74c3c', 1: '#e67e22', 2: '#3498db', 3: '#2ecc71'}
    m2[['MACD_Score']].plot.barh(ax=axes[0], color=[sc.get(int(v), '#95a5a6') for v in m2['MACD_Score']], legend=False)
    axes[0].set_title('MACD Score')
    
    m2[['Histogram']].plot.barh(ax=axes[1], color=['#2ecc71' if v >= 0 else '#e74c3c' for v in m2['Histogram']], legend=False)
    axes[1].set_title('MACD Histogram')
    plt.tight_layout()
    return fig

def create_near_hl_chart(near_high, near_low):
    """Create near 52W high/low horizontal bar charts"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle('Near 52W High / Low', fontsize=14, fontweight='bold')
    
    if not near_high.empty:
        nh = near_high.copy().sort_values('52W_Position')
        nh.set_index('Symbol')[['52W_Position']].plot.barh(ax=axes[0], color='#2ecc71', legend=False)
        axes[0].set_title('Near 52W HIGH')
    
    if not near_low.empty:
        nl = near_low.copy().sort_values('52W_Position', ascending=False)
        nl.set_index('Symbol')[['52W_Position']].plot.barh(ax=axes[1], color='#e74c3c', legend=False)
        axes[1].set_title('Near 52W LOW')
    
    plt.tight_layout()
    return fig

def create_top_gainers_chart(returns_df):
    """Create horizontal bar chart for top gainers across periods using Plotly"""
    periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
    period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']
    
    fig = go.Figure()
    
    for period, label in zip(periods, period_labels):
        gainers = returns_df[returns_df[period] > 0].nlargest(10, period)[['Symbol', period]]
        
        if not gainers.empty:
            symbols = gainers['Symbol'].tolist()
            values = gainers[period].tolist()
            
            # Create text labels with symbol and percentage inside bars
            text_labels = [f'{sym}<br>{val:.1f}%' for sym, val in zip(symbols, values)]
            
            fig.add_trace(go.Bar(
                name=label,
                y=symbols,
                x=values,
                orientation='h',
                text=text_labels,
                textposition='inside',
                textfont=dict(size=10, color='white'),
                marker=dict(
                    color=values,
                    colorscale='Greens',
                    line=dict(width=0.5, color='white')
                ),
                hovertemplate='<b>%{y}</b><br>%{x:.2f}%<extra></extra>'
            ))
    
    fig.update_layout(
        title='Top 10 Gainers by Period',
        xaxis_title='Return %',
        yaxis_title='',
        barmode='group',
        height=600,
        width=1200,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        bargap=0.15,
        bargroupgap=0.1
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=False)
    
    # Convert to image bytes
    img_bytes = fig.to_image(format='png', width=1200, height=600, scale=2)
    return img_bytes

def create_top_losers_chart(returns_df):
    """Create horizontal bar chart for top losers across periods using Plotly"""
    periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
    period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']
    
    fig = go.Figure()
    
    for period, label in zip(periods, period_labels):
        losers = returns_df[returns_df[period] < 0].nsmallest(10, period)[['Symbol', period]]
        
        if not losers.empty:
            symbols = losers['Symbol'].tolist()
            values = losers[period].tolist()
            
            # Create text labels with symbol and percentage inside bars
            text_labels = [f'{sym}<br>{val:.1f}%' for sym, val in zip(symbols, values)]
            
            fig.add_trace(go.Bar(
                name=label,
                y=symbols,
                x=values,
                orientation='h',
                text=text_labels,
                textposition='inside',
                textfont=dict(size=10, color='white'),
                marker=dict(
                    color=[abs(v) for v in values],
                    colorscale='Reds',
                    line=dict(width=0.5, color='white')
                ),
                hovertemplate='<b>%{y}</b><br>%{x:.2f}%<extra></extra>'
            ))
    
    fig.update_layout(
        title='Top 10 Losers by Period',
        xaxis_title='Return %',
        yaxis_title='',
        barmode='group',
        height=600,
        width=1200,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        bargap=0.15,
        bargroupgap=0.1
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=False)
    
    # Convert to image bytes
    img_bytes = fig.to_image(format='png', width=1200, height=600, scale=2)
    return img_bytes

def create_crossover_chart(cross_df, combined):
    """Create crossover trend chart with positive/negative panels"""
    colors_line = ['#2980b9','#e67e22','#8e44ad','#27ae60','#c0392b',
                   '#16a085','#d35400','#2c3e50','#7f8c8d','#1abc9c',
                   '#f39c12','#8e44ad','#1abc9c','#e74c3c','#3498db']
    
    pos_syms, neg_syms = set(), set()
    if not cross_df.empty:
        pos_syms.update(cross_df[cross_df['crossed_last_5d'] == True]['Symbol'].tolist())
        pos_syms.update(cross_df[cross_df['nearing'] == True]['Symbol'].tolist())
        neg_mask = (cross_df['cross_pct'] < -1.0)
        neg_syms.update(cross_df[neg_mask]['Symbol'].tolist())
        neg_syms -= pos_syms
    
    def plot_panel(ax, syms, title, panel_color):
        if not syms:
            ax.text(0.5, 0.5, 'None', ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title(title, fontsize=10, color=panel_color, fontweight='bold')
            return
        for i, sym in enumerate(sorted(syms)):
            grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
            base = grp['close'].iloc[0]
            pct = (grp['close'] / base - 1) * 100
            col = colors_line[i % len(colors_line)]
            ax.plot(grp.index, pct, color=col, linewidth=1.2, alpha=0.85, label=sym)
        ax.axhline(0, color='grey', linewidth=0.7, linestyle='--', alpha=0.5)
        ax.set_title(title, fontsize=10, color=panel_color, fontweight='bold')
        ax.set_ylabel('% Change', fontsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.legend(fontsize=6.5, loc='upper left', ncol=2)
        ax.grid(axis='y', alpha=0.3)
    
    if pos_syms or neg_syms:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Cross-Over — 1 Year % Change', fontsize=12, fontweight='bold')
        plot_panel(axes[0], pos_syms, '▲ Positive / Nearing', '#27ae60')
        plot_panel(axes[1], neg_syms, '▼ Negative / Bearish', '#c0392b')
        plt.tight_layout()
        return fig
    return None

def create_52w_range_chart(hl_df):
    """Create current price vs 52W range chart"""
    hl_all = hl_df[['Symbol', 'Current_Price', '52W_High', '52W_Low', '52W_Position']].dropna(subset=['52W_Position'])
    hl_sorted = hl_all.sort_values('52W_Position')
    hl = pd.concat([hl_sorted.head(8), hl_sorted.tail(7)]).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    for i, row in hl.iterrows():
        lo, hi, cur, sym, pos = row['52W_Low'], row['52W_High'], row['Current_Price'], row['Symbol'], row['52W_Position']
        color = '#e74c3c' if pos <= 20 else '#2ecc71' if pos >= 80 else '#3498db'
        
        ax.barh(i, 100, left=0, height=0.5, color='#ecf0f1', edgecolor='#bdc3c7', linewidth=0.5)
        ax.barh(i, pos, left=0, height=0.5, color=color, alpha=0.55)
        ax.scatter(pos, i, color=color, s=90, zorder=5, edgecolors='white', linewidths=0.8)
        ax.text(-1, i, sym, ha='right', va='center', fontsize=8.5, fontweight='bold')
        ax.text(pos, i + 0.33, f'£{cur:,.0f}  ({pos:.1f}%)', ha='center', fontsize=7.5, color=color, fontweight='bold')
        ax.text(0, i - 0.35, f'£{lo:,.0f}', ha='left', fontsize=6.5, color='#7f8c8d')
        ax.text(100, i - 0.35, f'£{hi:,.0f}', ha='right', fontsize=6.5, color='#7f8c8d')
    
    ax.set_xlim(-2, 108)
    ax.set_yticks([])
    ax.set_xlabel('52W Position %  (0% = 52W Low  →  100% = 52W High)')
    ax.axvline(20, color='#e74c3c', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.axvline(80, color='#2ecc71', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.axvline(50, color='grey', linestyle=':', linewidth=0.8, alpha=0.4)
    ax.set_title('Current Price vs 52W Range', fontsize=11, fontweight='bold')
    ax.grid(axis='x', alpha=0.2)
    plt.tight_layout()
    return fig

def create_price_trend_chart(near_high, near_low, combined):
    """Create 1-year price trend chart for near high/low stocks"""
    def split_adjusted_pct(grp, split_threshold=0.45):
        close = grp['close'].copy()
        daily_ret = close.pct_change()
        split_days = daily_ret[daily_ret < -split_threshold].index
        for sd in split_days:
            ratio = close.loc[sd] / close.shift(1).loc[sd]
            close.loc[close.index < sd] *= ratio
        base = close.iloc[0]
        return (close / base - 1) * 100
    
    near_syms_high = near_high['Symbol'].tolist() if not near_high.empty else []
    near_syms_low = near_low['Symbol'].tolist() if not near_low.empty else []
    
    if not (near_syms_high or near_syms_low):
        return None
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('1-Year Price Trend — Near 52W High & Low Stocks', fontsize=12, fontweight='bold')
    
    for ax, syms, title, color in [
        (axes[0], near_syms_high, 'Near 52W HIGH', '#27ae60'),
        (axes[1], near_syms_low, 'Near 52W LOW', '#c0392b'),
    ]:
        if not syms:
            ax.text(0.5, 0.5, 'None', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontsize=10, color=color, fontweight='bold')
            continue
        for sym in syms:
            grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
            pct = split_adjusted_pct(grp)
            ax.plot(grp.index, pct, linewidth=1.2, label=sym, alpha=0.85)
        ax.axhline(0, color='grey', linewidth=0.7, linestyle='--', alpha=0.5)
        ax.set_title(title, fontsize=10, color=color, fontweight='bold')
        ax.set_ylabel('% Change', fontsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.legend(fontsize=6.5, loc='upper left', ncol=2)
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

def generate_all_charts(reports, hl_df, macd_df, cross_df, returns_df, combined):
    """Generate all charts and return as bytes dictionary"""
    print('\nGenerating charts...')
    chart_images = {}
    
    # 52W position chart
    fig = create_52w_position_chart(reports['r1'])
    chart_images['52w_position'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # MACD chart
    fig = create_macd_chart(macd_df)
    chart_images['macd'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # Near high/low chart
    fig = create_near_hl_chart(reports['near_high'], reports['near_low'])
    chart_images['52w_hl'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # Crossover chart
    fig = create_crossover_chart(cross_df, combined)
    if fig:
        chart_images['crossover'] = fig_to_bytes(fig)
        plt.close(fig)
    
    # 52W range chart
    fig = create_52w_range_chart(hl_df)
    chart_images['52w_range'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # Price trend chart
    fig = create_price_trend_chart(reports['near_high'], reports['near_low'], combined)
    if fig:
        chart_images['52w_trend'] = fig_to_bytes(fig)
        plt.close(fig)
    
    # Top gainers chart (Plotly - returns bytes directly)
    chart_images['top_gainers'] = create_top_gainers_chart(returns_df)
    
    # Top losers chart (Plotly - returns bytes directly)
    chart_images['top_losers'] = create_top_losers_chart(returns_df)
    
    print(f'[OK] Generated {len(chart_images)} charts')
    return chart_images

# ============================================================================
# EMAIL FUNCTIONALITY
# ============================================================================

def df_to_html_table(df, title):
    """Convert DataFrame to HTML table with title"""
    return f'<h3>{title}</h3>' + df.to_html(index=False, border=1)

def embed_chart(cid, title, width=900):
    """Create HTML for embedded chart"""
    return f'<h2>{title}</h2><img src="cid:{cid}" width="{width}"><br><br>'

def build_html_body(reports, chart_images):
    """Build HTML email body with tables and embedded charts"""
    sections = ['<html><body>', '<h1>NSE Stock Analysis Report</h1>']
    
    # 52W Position summary
    sections.append(df_to_html_table(reports['r1'][['Symbol','Current_Price','52W_Position']].head(20),
                                     '52W Position (top 20)'))
    
    # Near High/Low tables and chart
    sections.append(df_to_html_table(reports['near_high'], 'Near 52W HIGH'))
    sections.append(df_to_html_table(reports['near_low'], 'Near 52W LOW'))
    if '52w_hl' in chart_images:
        sections.append(embed_chart('52w_hl', 'Near 52W High / Low'))
    
    # MACD table and chart
    if not reports['r3'].empty:
        sections.append(df_to_html_table(reports['r3'], 'MACD Signals (Score ≥ 2)'))
    if 'macd' in chart_images:
        sections.append(embed_chart('macd', 'MACD Overview — Top 15'))
    
    # Crossover tables and charts
    if not reports['crossed'].empty:
        sections.append(df_to_html_table(reports['crossed'], 'Golden Crossover (last 5d)'))
    
    if 'crossover' in chart_images:
        sections.append(embed_chart('crossover', 'Cross-Over — 1 Year % Change'))
    
    # 52W Range chart
    if '52w_range' in chart_images:
        sections.append(embed_chart('52w_range', 'Current Price vs 52W Range (Top 15)'))
    
    # Price trend chart
    if '52w_trend' in chart_images:
        sections.append(embed_chart('52w_trend', '1-Year Price Trend — Near 52W High & Low Stocks'))
    
    # Top gainers chart
    if 'top_gainers' in chart_images:
        sections.append(embed_chart('top_gainers', 'Top 10 Gainers by Period'))
    
    # Top losers chart
    if 'top_losers' in chart_images:
        sections.append(embed_chart('top_losers', 'Top 10 Losers by Period'))
    
    sections.append('</body></html>')
    return ''.join(sections)

def send_email(reports, chart_images):
    """Assemble and send email with embedded charts"""
    print('\nPreparing email...')
    
    html_body = build_html_body(reports, chart_images)
    
    msg = MIMEMultipart('related')
    msg['Subject'] = f'NSE Analysis — {datetime.now().strftime("%d %b %Y")}'
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg.attach(MIMEText(html_body, 'html'))
    
    for cid, img_bytes in chart_images.items():
        img = MIMEImage(img_bytes, 'png')
        img.add_header('Content-ID', f'<{cid}>')
        msg.attach(img)
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_FROM, EMAIL_PASS)
            smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f'[OK] Email sent to {EMAIL_TO} with {len(chart_images)} inline charts')
    except Exception as e:
        print(f'[ERROR] Failed to send email: {e}')

# ============================================================================
# SAVE RESULTS
# ============================================================================

def save_to_csv(reports, config, skipped):
    """Save all reports to CSV"""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    os.makedirs(config['output_dir'], exist_ok=True)
    out_path = f"{config['output_dir']}/NSE-ANALYSIS-{timestamp}.csv"
    
    csv_sections = [
        pd.DataFrame([['=== REPORT 1: 52W Hi/Low Position ===']]), reports['r1'], pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 2A: Crossed Last 5 Days ===']]),
        reports['crossed'] if not reports['crossed'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 2B: Nearing Crossover ===']]),
        reports['nearing'] if not reports['nearing'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 3: MACD Signals ===']]),
        reports['r3'] if not reports['r3'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 4A: Near 52W HIGH ===']]),
        reports['near_high'] if not reports['near_high'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 4B: Near 52W LOW ===']]),
        reports['near_low'] if not reports['near_low'].empty else pd.DataFrame([['(none)']]),
    ]
    
    with open(out_path, 'w', newline='') as f:
        for section in csv_sections:
            section.to_csv(f, index=False, header=True)
            f.write('\n')
    
    print(f'\n[OK] Reports saved to: {out_path}')
    if skipped:
        print(f'[WARNING] Skipped stocks: {skipped}')

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution function"""
    print('='*80)
    print('NSE STOCK ANALYSIS')
    print('='*80)
    
    # Load config
    config = load_config()
    
    # Fetch data
    combined, skipped = fetch_all_data(config)
    
    # Compute metrics
    hl_df, cross_df, macd_df, returns_df = compute_all_metrics(combined)
    
    # Generate reports
    reports = generate_reports(hl_df, cross_df, macd_df, returns_df)
    
    # Generate charts
    chart_images = generate_all_charts(reports, hl_df, macd_df, cross_df, returns_df, combined)
    
    # Send email
    send_email(reports, chart_images)
    
    # Save results
    save_to_csv(reports, config, skipped)
    
    print('\n' + '='*80)
    print('[OK] ANALYSIS COMPLETE')
    print('='*80)

if __name__ == '__main__':
    main()

# Made with Bob
