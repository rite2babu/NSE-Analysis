"""Generate NSE_Analysis.ipynb from NSE_Analysis.py"""
import json

def cell(cell_type, source):
    if cell_type == 'markdown':
        return {"cell_type": "markdown", "id": f"md-{abs(hash(source[:20]))}", "metadata": {}, "source": source}
    else:
        return {"cell_type": "code", "execution_count": None, "id": f"cd-{abs(hash(source[:20]))}", "metadata": {}, "outputs": [], "source": source}

cells = []

# ── Title ──────────────────────────────────────────────────────────────────
cells.append(cell('markdown', """# NSE Stock Analysis
Fetches 1 year of OHLCV data for a configurable stock list and produces:

| Section | Description |
|---------|-------------|
| **5** | Report 1 — 52W Hi/Low Position (all stocks, heat-mapped table) |
| **6** | Report 2 — Golden Crossover signals (crossed last 5d + nearing) |
| **6b** | Chart — Cross-Over: +ve (golden/nearing) vs -ve (bearish) panels, 1-yr % change, markers = last 2 weeks |
| **7** | Report 3 — MACD Signals (score ≥ 2) |
| **7b** | Chart — MACD Overview: Score + Histogram bar charts (top 15) |
| **8** | Report 4 — Top 10 near 52W High / Low tables |
| **8b** | Chart — Top 10 near 52W High / Low (horizontal bar) |
| **8c** | Chart — Current Price vs 52W Range (% position, top 15: 8 near-low + 7 near-high) |
| **8d** | Chart — 1-Year Price Trend for near-high & near-low stocks (split-adjusted %) |
| **9** | Chart — All Stocks 52W Position (df.plot bar, colour-coded) |
| **10** | Save all reports to `dump/NSE-ANALYSIS-{timestamp}.csv` |

**Stock list:** 119 NSE symbols (configurable in Section 1)
**Lookback:** 365 days
**Parallel fetch:** 5 threads"""))

# ── 1. Imports ─────────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 1. Imports & Configuration"))

cells.append(cell('code', """\
import pandas as pd
import numpy as np
from datetime import datetime
import datetime as dt
import os, time, requests, concurrent.futures
from nselib import capital_market
import nselib.capital_market.capital_market_data as _cm_data

print('Imports OK')"""))

cells.append(cell('code', """\
# ── Configuration ─────────────────────────────────────────────
STOCK_LIST = [
    'AARTIIND', 'ABBOTINDIA', 'ABSLAMC', 'ADANIPORTS', 'AMBUJACEM',
    'ARE&M', 'ASIANPAINT', 'ASPINWALL', 'AUROPHARMA', 'BAJAJ-AUTO',
    'BAJFINANCE', 'BALKRISIND', 'BALMLAWRIE', 'BASML', 'CAMS',
    'CARTRADE', 'CASTROLIND', 'CEATLTD', 'CHOLAFIN', 'CHOLAHLDNG',
    'CIPLA', 'COALINDIA', 'COCHINSHIP', 'COSMOFIRST', 'CROMPTON',
    'DABUR', 'DATAPATTNS', 'DMART', 'DRREDDY', 'EIDPARRY',
    'EMBASSY', 'EXIDEIND', 'GAIL', 'GENUSPOWER', 'GESHIP',
    'GLAXO', 'GLENMARK', 'GNFC', 'GOLDBEES', 'GOLDETF',
    'GREAVESCOT', 'GULFOILLUB', 'GULFPETRO', 'HCLTECH', 'HDFCAMC',
    'HDFCBANK', 'HDFCNIFIT', 'HEROMOTOCO', 'HGS', 'HIL',
    'HINDALCO', 'HINDZINC', 'HITECHGEAR', 'ICICIBANK', 'ICICIGOLD',
    'ICICIPRULI', 'ICICITECH', 'ICIL', 'IDFCBank', 'IFCI',
    'INDIANB', 'INFY', 'IOC', 'IPCALAB', 'IRBINVIT',
    'IRFC', 'ITC', 'JINDALPOLY', 'JINDALSAW', 'JPPOWER',
    'JSL', 'JUBLFOOD', 'KTKBANK', 'LGBBROSLTD', 'LT',
    'MAITHANALL', 'MANAPPURAM', 'MARUTI', 'METROPOLIS', 'MIDCAPETF',
    'MOGOLD', 'MOIL', 'MONTECARLO', 'MOTILALOFS', 'MUTHOOTFIN',
    'NATCOPHARM', 'NIFTYETF', 'NTPC', 'OFSS', 'ONGC',
    'PCBL', 'PETRONET', 'PGINVIT', 'PHARMABEES', 'PNBGILTS',
    'PPL', 'PTC', 'RITES', 'RUBFILA', 'RVNL',
    'SAIL', 'SBIGETS', 'SGBN28VIII', 'SMALLCAP', 'SOUTHBANK',
    'STOVEKRAFT', 'TATACHEM', 'TATACONSUM', 'TATASTEEL', 'TCS',
    'TECHM', 'TEGA', 'TITAGARH', 'TITAN', 'TMB',
    'TMCV', 'TMPV', 'TTKPRESTIG', 'TVSMOTOR', 'VEDL',
    'WHIRLPOOL', 'WIPRO', 'WSTCSTPAPR', 'ZYDUSLIFE',
]
MAX_WORKERS = 5   # parallel fetch threads
DAYS        = 365 # lookback period
print(f'{len(STOCK_LIST)} stocks configured')"""))

# ── 2. Helpers ─────────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 2. Helper Functions"))

cells.append(cell('code', """\
def compute_period_hl(df):
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    def window_hl(days):
        rows = df.tail(days)
        return rows['high'].max(), rows['low'].min()
    h52, l52 = window_hl(min(252, n))
    h26, l26 = window_hl(min(126, n))
    h4,  l4  = window_hl(min(20,  n))
    h1,  l1  = window_hl(min(5,   n))
    current = df['close'].iloc[-1]
    rng = h52 - l52
    pos = (current - l52) / rng * 100 if rng > 0 else float('nan')
    return {
        'Current_Price': round(current, 2),
        '52W_High': round(h52, 2), '52W_Low': round(l52, 2),
        '26W_High': round(h26, 2), '26W_Low': round(l26, 2),
        '4W_High':  round(h4,  2), '4W_Low':  round(l4,  2),
        '1W_High':  round(h1,  2), '1W_Low':  round(l1,  2),
        '52W_Position': round(pos, 2) if pos == pos else float('nan'),
    }


def compute_sma_crossovers(df):
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    close = df['close']
    sma = {p: close.rolling(p).mean() if n >= p else pd.Series([float('nan')]*n, index=df.index)
           for p in [5, 10, 20, 50, 100, 200]}
    results = []
    for label, short_p, long_p in [('200/20', 20, 200), ('100/10', 10, 100), ('50/5', 5, 50)]:
        s, l = sma[short_p], sma[long_p]
        if s.isna().all() or l.isna().all(): continue
        cross = (s > l) & (s.shift(1) <= l.shift(1))
        last5_cross = cross.iloc[-5:].any() if n >= 5 else False
        cross_dates = df['date'][cross]
        last_cross_date = cross_dates.iloc[-1].strftime('%Y-%m-%d') if not cross_dates.empty and last5_cross else None
        s_last, l_last = s.iloc[-1], l.iloc[-1]
        if pd.isna(s_last) or pd.isna(l_last): continue
        cross_pct = (s_last - l_last) / l_last * 100
        results.append({
            'cross_type':      label,
            'crossed_last_5d': bool(last5_cross),
            'last_cross_date': last_cross_date,
            'nearing':         bool(-1.0 <= cross_pct <= 0),
            'cross_pct':       round(cross_pct, 3),
        })
    return results


def compute_macd(df):
    df = df.sort_values('date').reset_index(drop=True)
    close = df['close']
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line   = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram   = macd_line - signal_line
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
        'MACD':            round(macd_line.iloc[-1], 4),
        'Signal':          round(signal_line.iloc[-1], 4),
        'Histogram':       round(histogram.iloc[-1], 4),
        'Bullish_Cross':   bool(bullish_cross),
        'Above_Zero':      above_zero,
        'Hist_Increasing': hist_inc,
        'MACD_Score':      score,
    }

print('Helper functions defined')"""))

# ── 3. Fetch ───────────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 3. Fetch Data (Parallel)"))

cells.append(cell('code', """\
end_date   = dt.date.today().strftime('%d-%m-%Y')
start_date = (dt.date.today() - dt.timedelta(days=DAYS)).strftime('%d-%m-%Y')
print(f'Date range: {start_date} to {end_date}')

# Warm up a single shared session and patch nselib to reuse it
print('Initialising shared NSE session...')
_shared_session = requests.Session()
_shared_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.nseindia.com/',
})
_r0 = _shared_session.get('https://www.nseindia.com/', timeout=30)
print(f'  Session: HTTP {_r0.status_code}, cookies: {list(_shared_session.cookies.get_dict().keys())}')
time.sleep(2)

def _shared_urlfetch(url, origin_url='http://nseindia.com'):
    return _shared_session.get(url, timeout=30)

_cm_data.nse_urlfetch = _shared_urlfetch

def fetch_one(sym):
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

skipped = []
frames  = []
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_map = {executor.submit(fetch_one, sym): sym for sym in STOCK_LIST}
    for future in concurrent.futures.as_completed(future_map):
        sym = future_map[future]
        try:
            df = future.result()
            print(f'  OK   {sym:20s}  {len(df)} rows')
            frames.append(df)
        except Exception as e:
            print(f'  SKIP {sym:20s}  {e}')
            skipped.append(sym)

if skipped:
    print(f'\\nSkipped: {skipped}')"""))

# ── 4. Combine & Metrics ───────────────────────────────────────────────────
cells.append(cell('markdown', "## 4. Combine & Compute Metrics"))

cells.append(cell('code', """\
combined = pd.concat(frames, ignore_index=True)
combined.sort_values(['symbol', 'date'], inplace=True)
combined.reset_index(drop=True, inplace=True)
print(f'Combined: {len(combined)} rows, {combined[\"symbol\"].nunique()} stocks')
combined.head()"""))

cells.append(cell('code', """\
hl_rows    = []
cross_rows = []
macd_rows  = []

for sym, grp in combined.groupby('symbol'):
    grp = grp.sort_values('date').reset_index(drop=True)
    try:
        hl = compute_period_hl(grp); hl['Symbol'] = sym; hl_rows.append(hl)
    except Exception as e:
        print(f'  Warning [{sym}] HL: {e}')
    try:
        if len(grp) >= 5:
            for c in compute_sma_crossovers(grp):
                c['Symbol'] = sym; cross_rows.append(c)
    except Exception as e:
        print(f'  Warning [{sym}] SMA: {e}')
    try:
        macd = compute_macd(grp); macd['Symbol'] = sym; macd_rows.append(macd)
    except Exception as e:
        print(f'  Warning [{sym}] MACD: {e}')

hl_df    = pd.DataFrame(hl_rows)
cross_df = pd.DataFrame(cross_rows) if cross_rows else pd.DataFrame()
macd_df  = pd.DataFrame(macd_rows)
print(f'Metrics: {len(hl_df)} HL, {len(cross_df)} crossovers, {len(macd_df)} MACD')"""))

# ── 5. Report 1 ────────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 5. Report 1 — 52W Hi/Low Position"))

cells.append(cell('code', """\
r1 = hl_df[[
    'Symbol', 'Current_Price',
    '52W_High', '52W_Low', '52W_Position',
    '26W_High', '26W_Low',
    '4W_High',  '4W_Low',
    '1W_High',  '1W_Low',
]].sort_values('52W_Position').reset_index(drop=True)

r1.rename(columns={'52W_Position': '52W_Pos%'}).style \\
    .format(precision=2) \\
    .background_gradient(subset=['52W_Pos%'], cmap='RdYlGn')"""))

# ── 6. Report 2 ────────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 6. Report 2 — Golden Crossover Signals"))

cells.append(cell('code', """\
print('>> Crossed in last 5 days:')
if not cross_df.empty:
    crossed = cross_df[cross_df['crossed_last_5d'] == True][['Symbol', 'cross_type', 'cross_pct', 'last_cross_date']]
    crossed = crossed.rename(columns={'cross_type': 'Cross Type', 'cross_pct': 'Cross%', 'last_cross_date': 'Cross Date'})
    display(crossed.reset_index(drop=True)) if not crossed.empty else print('  (none)')
else:
    print('  (no data)')"""))

cells.append(cell('code', """\
print('>> Nearing crossover (short SMA within 1% below long SMA):')
if not cross_df.empty:
    nearing = cross_df[cross_df['nearing'] == True][['Symbol', 'cross_type', 'cross_pct']]
    nearing = nearing.rename(columns={'cross_type': 'Cross Type', 'cross_pct': 'Cross% (neg=below)'})
    display(nearing.reset_index(drop=True)) if not nearing.empty else print('  (none)')
else:
    print('  (no data)')"""))

# ── 6b. Crossover Time-Series Charts ──────────────────────────────────────
cells.append(cell('markdown', "## 6b. Cross-Over"))

cells.append(cell('code', """\
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

_sma_pairs     = {'200/20': (20, 200), '100/10': (10, 100), '50/5': (5, 50)}
_two_weeks_ago = pd.Timestamp.today() - pd.Timedelta(weeks=2)
_colors_line   = ['#2980b9','#e67e22','#8e44ad','#27ae60','#c0392b',
                  '#16a085','#d35400','#2c3e50','#7f8c8d','#1abc9c',
                  '#f39c12','#8e44ad','#1abc9c','#e74c3c','#3498db']

# Separate: +ve (golden cross / nearing) vs -ve (death cross)
_pos_syms, _neg_syms = set(), set()
if not cross_df.empty:
    # Positive: crossed bullish in last 5d OR nearing (short approaching long from below)
    _pos_syms.update(cross_df[cross_df['crossed_last_5d'] == True]['Symbol'].tolist())
    _pos_syms.update(cross_df[cross_df['nearing'] == True]['Symbol'].tolist())

    # Negative: stocks where short SMA is BELOW long SMA (cross_pct < 0, not nearing)
    _neg_mask = (cross_df['cross_pct'] < -1.0)   # more than 1% below = bearish
    _neg_syms.update(cross_df[_neg_mask]['Symbol'].tolist())
    # Remove from neg if already in pos
    _neg_syms -= _pos_syms

def _plot_xover_panel(ax, syms, title, marker, marker_color, panel_color):
    if not syms:
        ax.text(0.5, 0.5, 'None', ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title(title, fontsize=11, color=panel_color, fontweight='bold')
        return
    for i, sym in enumerate(sorted(syms)):
        grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
        base = grp['close'].iloc[0]
        pct  = (grp['close'] / base - 1) * 100
        col  = _colors_line[i % len(_colors_line)]
        ax.plot(grp.index, pct, color=col, linewidth=1.5, alpha=0.85)
        # Mark crossover events in last 2 weeks
        sym_crosses = cross_df[cross_df['Symbol'] == sym] if not cross_df.empty else pd.DataFrame()
        for _, row in sym_crosses.iterrows():
            short_p, long_p = _sma_pairs[row['cross_type']]
            sma_s = grp['close'].rolling(short_p).mean()
            sma_l = grp['close'].rolling(long_p).mean()
            gc_mask = ((sma_s > sma_l) & (sma_s.shift(1) <= sma_l.shift(1))).fillna(False)
            gc_r = gc_mask & (grp.index >= _two_weeks_ago)
            if gc_r.any():
                ax.scatter(grp.index[gc_r], (grp['close'][gc_r]/base-1)*100,
                           marker='^', color='#2ecc71', s=110, zorder=5, edgecolors=col, linewidths=1)
            dc_mask = ((sma_s < sma_l) & (sma_s.shift(1) >= sma_l.shift(1))).fillna(False)
            dc_r = dc_mask & (grp.index >= _two_weeks_ago)
            if dc_r.any():
                ax.scatter(grp.index[dc_r], (grp['close'][dc_r]/base-1)*100,
                           marker='v', color='#e74c3c', s=110, zorder=5, edgecolors=col, linewidths=1)
        ax.annotate(sym, xy=(grp.index[-1], pct.iloc[-1]),
                    xytext=(4, 0), textcoords='offset points', fontsize=7.5, color=col, va='center')
    ax.axhline(0, color='grey', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.set_title(title, fontsize=11, color=panel_color, fontweight='bold')
    ax.set_ylabel('% Change from year start')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
    handles = [Line2D([0],[0], color=_colors_line[i%len(_colors_line)], linewidth=1.5, label=s)
               for i, s in enumerate(sorted(syms))]
    handles += [
        Line2D([0],[0], marker='^', color='w', markerfacecolor='#2ecc71', markersize=9, label='Golden X ▲'),
        Line2D([0],[0], marker='v', color='w', markerfacecolor='#e74c3c', markersize=9, label='Death X ▼'),
    ]
    ax.legend(handles=handles, fontsize=7.5, loc='upper left', ncol=2)
    ax.grid(axis='y', alpha=0.3)

if not _pos_syms and not _neg_syms:
    print('No crossover / nearing stocks to plot.')
else:
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle('Cross-Over — 1 Year % Change  |  markers = events in last 2 weeks', fontsize=12, fontweight='bold')
    _plot_xover_panel(axes[0], _pos_syms, '▲ Positive / Nearing Cross-Over', '^', '#2ecc71', '#27ae60')
    _plot_xover_panel(axes[1], _neg_syms, '▼ Negative / Bearish Cross-Over',  'v', '#e74c3c', '#c0392b')
    plt.tight_layout()
    plt.show()"""))

# ── 6c. SMA Crossover in Last 5 Days (Table/Heatmap) ─────────────────────
cells.append(cell('markdown', "## 6c. SMA Crossover Summary (Last 5 Days)"))

cells.append(cell('code', """\
_sma_pairs = {'200/20': (20, 200), '100/10': (10, 100), '50/5': (5, 50)}

_crossed_data = []
if not cross_df.empty:
    for _, row in cross_df[cross_df['crossed_last_5d'] == True].iterrows():
        sym = row['Symbol']
        cross_type = row['cross_type']
        cross_date = row['last_cross_date']
        
        # Get current signal strength
        grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
        short_p, long_p = _sma_pairs[cross_type]
        sma_s = grp['close'].rolling(short_p).mean()
        sma_l = grp['close'].rolling(long_p).mean()
        signal_pct = ((sma_s.iloc[-1] - sma_l.iloc[-1]) / sma_l.iloc[-1] * 100)
        
        # Days since cross
        cross_dt = pd.to_datetime(cross_date)
        days_since = (grp.index[-1] - cross_dt).days
        
        # Current price and 52W position
        cur_price = grp['close'].iloc[-1]
        hl_row = hl_df[hl_df['Symbol'] == sym]
        pos_52w = hl_row['52W_Position'].values[0] if not hl_row.empty else None
        
        _crossed_data.append({
            'Symbol': sym,
            'Cross Type': cross_type,
            'Cross Date': cross_date,
            'Days Ago': days_since,
            'Signal %': round(signal_pct, 2),
            'Current Price': round(cur_price, 2),
            '52W Position': round(pos_52w, 1) if pos_52w else None,
            'Direction': '▲ Golden' if signal_pct > 0 else '▼ Death'
        })

if not _crossed_data:
    print('No stocks crossed in last 5 days.')
else:
    cross_summary = pd.DataFrame(_crossed_data).sort_values('Signal %', ascending=False)
    
    # Display with styling
    cross_summary.style \\
        .background_gradient(subset=['Signal %'], cmap='RdYlGn', vmin=-5, vmax=5) \\
        .background_gradient(subset=['52W Position'], cmap='RdYlGn') \\
        .format({'Signal %': '{:.2f}%', 'Current Price': '₹{:.2f}', '52W Position': '{:.1f}%'})"""))

# ── 7. Report 3 ────────────────────────────────────────────────────────────
cells.append(cell('markdown', """## 7. Report 3 — MACD Signals (Score ≥ 2)

### What is MACD?
**MACD (Moving Average Convergence Divergence)** is a momentum indicator that shows the relationship between two Exponential Moving Averages (EMAs) of a stock's price.

**Three components:**
| Component | Calculation | What it means |
|-----------|-------------|---------------|
| **MACD Line** | EMA(12) − EMA(26) | Difference between short & long-term momentum |
| **Signal Line** | EMA(9) of MACD Line | Smoothed trigger line |
| **Histogram** | MACD Line − Signal Line | Visual momentum: growing = accelerating, shrinking = fading |

---

### How to read it

**MACD Line vs Signal Line:**
- 📈 **MACD crosses above Signal** → Bullish signal (buy)
- 📉 **MACD crosses below Signal** → Bearish signal (sell)
- The further apart they are, the stronger the momentum

**Above / Below Zero:**
- **MACD > 0** → Short-term EMA above long-term EMA → uptrend
- **MACD < 0** → Short-term EMA below long-term EMA → downtrend

**Histogram:**
- **Growing positive bars** → Bullish momentum increasing
- **Shrinking positive bars** → Bullish momentum fading (possible reversal)
- **Growing negative bars** → Bearish momentum increasing

---

### MACD Score (used in this notebook)
Each stock gets a score **0–3** based on three conditions:

| Condition | Score |
|-----------|-------|
| MACD crossed above Signal in last 5 days | +1 |
| MACD Line > 0 (above zero) | +1 |
| Histogram increasing for last 3 days | +1 |

**Score 3** = all three bullish signals present → strongest buy signal
**Score 0** = none present → bearish / no momentum

> ⚠️ MACD is a **lagging indicator** — it confirms trends rather than predicting them. Always use alongside price action and other signals (e.g. 52W position, crossovers)."""))

cells.append(cell('code', """\
r3 = macd_df[macd_df['MACD_Score'] >= 2].sort_values('MACD_Score', ascending=False)
r3_display = r3[['Symbol', 'MACD', 'Signal', 'Histogram', 'Bullish_Cross', 'Above_Zero', 'Hist_Increasing', 'MACD_Score']]
r3_display = r3_display.rename(columns={
    'Bullish_Cross': 'Bullish X', 'Above_Zero': 'Above 0',
    'Hist_Increasing': 'Hist Inc', 'MACD_Score': 'Score'
})
display(r3_display.reset_index(drop=True)) if not r3_display.empty else print('(no stocks with MACD score >= 2)')"""))

# ── 7b. MACD Chart ─────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 7b. Chart — MACD Overview (All Stocks)"))

cells.append(cell('code', """\
import matplotlib.pyplot as plt

# Top 15 by MACD Score then Histogram (most bullish)
_m_all = macd_df[['Symbol', 'MACD', 'Signal', 'Histogram', 'MACD_Score']].copy()
_m = _m_all.sort_values(['MACD_Score', 'Histogram'], ascending=False).head(15)
_m = _m.sort_values(['MACD_Score', 'Histogram'], ascending=True).set_index('Symbol')

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle('MACD Overview — Top 15 Stocks (by Score & Histogram)', fontsize=13, fontweight='bold')

# ── Left: MACD Score (0-3) ────────────────────────────────────────────────
score_colors = {0: '#e74c3c', 1: '#e67e22', 2: '#3498db', 3: '#2ecc71'}
colors_score = [score_colors.get(int(v), '#95a5a6') for v in _m['MACD_Score']]
_m[['MACD_Score']].plot.barh(ax=axes[0], color=colors_score, legend=False)
axes[0].set_xlabel('MACD Score (0=bearish → 3=bullish)')
axes[0].set_title('MACD Score per Stock', fontsize=11)
axes[0].axvline(2, color='#2ecc71', linestyle='--', linewidth=1, alpha=0.7)
for p in axes[0].patches:
    axes[0].text(p.get_width() + 0.05, p.get_y() + p.get_height() / 2,
                 str(int(p.get_width())), va='center', fontsize=9)

# ── Right: MACD Histogram (momentum) ─────────────────────────────────────
hist_colors = ['#2ecc71' if v >= 0 else '#e74c3c' for v in _m['Histogram']]
_m[['Histogram']].plot.barh(ax=axes[1], color=hist_colors, legend=False)
axes[1].set_xlabel('MACD Histogram value')
axes[1].set_title('MACD Histogram\\n(green = bullish momentum, red = bearish)', fontsize=11)
axes[1].axvline(0, color='black', linewidth=0.8, alpha=0.5)

plt.tight_layout()
plt.show()"""))

# ── 8. Report 4 ────────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 8. Report 4 — Top 10 Near 52W High / Low"))

cells.append(cell('code', """\
r4_cols = ['Symbol', 'Current_Price', '52W_High', '52W_Low', '52W_Position']
near_high = hl_df[hl_df['52W_Position'] >= 80].sort_values('52W_Position', ascending=False).head(10)[r4_cols]
near_low  = hl_df[hl_df['52W_Position'] <= 20].sort_values('52W_Position', ascending=True).head(10)[r4_cols]

print('>> Near 52W HIGH (position >= 80%):')
display(near_high.reset_index(drop=True)) if not near_high.empty else print('  (none)')

print('\\n>> Near 52W LOW (position <= 20%):')
display(near_low.reset_index(drop=True)) if not near_low.empty else print('  (none)')"""))

# ── 8b. Chart: 52W High/Low ───────────────────────────────────────────────
cells.append(cell('markdown', "## 8b. Chart — Top 10 Near 52W High / Low"))

cells.append(cell('code', """\
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.suptitle('Top Stocks Near 52-Week High / Low', fontsize=14, fontweight='bold')

# ── Left: Near 52W HIGH ───────────────────────────────────────────────────
if not near_high.empty:
    nh = near_high.copy().sort_values('52W_Position')
    bars = axes[0].barh(nh['Symbol'], nh['52W_Position'], color='#2ecc71', edgecolor='white')
    axes[0].set_xlim(0, 110)
    axes[0].axvline(80, color='#27ae60', linestyle='--', linewidth=1.2, alpha=0.7)
    axes[0].axvline(100, color='#1a8a4a', linestyle='-', linewidth=1.2, alpha=0.5)
    for bar, (_, row) in zip(bars, nh.iterrows()):
        axes[0].text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                     f\"{row['52W_Position']:.1f}%  ₹{row['Current_Price']:,.0f}\",
                     va='center', fontsize=8.5)
    axes[0].set_title('Near 52W HIGH  (position ≥ 80%)', fontsize=11, color='#27ae60')
    axes[0].set_xlabel('52W Position %')
    axes[0].tick_params(axis='y', labelsize=9)
else:
    axes[0].text(0.5, 0.5, 'No stocks near 52W High', ha='center', va='center', transform=axes[0].transAxes)
    axes[0].set_title('Near 52W HIGH  (position ≥ 80%)', fontsize=11)

# ── Right: Near 52W LOW ───────────────────────────────────────────────────
if not near_low.empty:
    nl = near_low.copy().sort_values('52W_Position', ascending=False)
    bars = axes[1].barh(nl['Symbol'], nl['52W_Position'], color='#e74c3c', edgecolor='white')
    axes[1].set_xlim(0, 35)
    axes[1].axvline(20, color='#c0392b', linestyle='--', linewidth=1.2, alpha=0.7)
    for bar, (_, row) in zip(bars, nl.iterrows()):
        axes[1].text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                     f\"{row['52W_Position']:.1f}%  ₹{row['Current_Price']:,.0f}\",
                     va='center', fontsize=8.5)
    axes[1].set_title('Near 52W LOW  (position ≤ 20%)', fontsize=11, color='#c0392b')
    axes[1].set_xlabel('52W Position %')
    axes[1].tick_params(axis='y', labelsize=9)
else:
    axes[1].text(0.5, 0.5, 'No stocks near 52W Low', ha='center', va='center', transform=axes[1].transAxes)
    axes[1].set_title('Near 52W LOW  (position ≤ 20%)', fontsize=11)

plt.tight_layout()
plt.show()"""))

# ── 8c. Price Range Chart: current vs 52W Hi/Low ─────────────────────────
cells.append(cell('markdown', "## 8c. Chart — Current Price vs 52W Range"))

cells.append(cell('code', """\
import matplotlib.pyplot as plt

# Top 15: bottom 8 (near low) + top 7 (near high) by 52W position
_hl_all = hl_df[['Symbol', 'Current_Price', '52W_High', '52W_Low', '52W_Position']].dropna(subset=['52W_Position'])
_hl_sorted = _hl_all.sort_values('52W_Position')
_hl_bottom = _hl_sorted.head(8)
_hl_top    = _hl_sorted.tail(7)
_hl = pd.concat([_hl_bottom, _hl_top]).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12, 8))

for i, row in _hl.iterrows():
    lo, hi, cur = row['52W_Low'], row['52W_High'], row['Current_Price']
    sym = row['Symbol']
    pos = row['52W_Position']
    rng = hi - lo if hi != lo else 1

    # Normalise to % position within range (0% = 52W low, 100% = 52W high)
    lo_pct, hi_pct, cur_pct = 0.0, 100.0, pos

    # Range bar (grey background)
    ax.barh(i, 100, left=0, height=0.5, color='#ecf0f1', edgecolor='#bdc3c7', linewidth=0.5)
    # Filled portion up to current price
    color = '#e74c3c' if pos <= 20 else '#2ecc71' if pos >= 80 else '#3498db'
    ax.barh(i, cur_pct, left=0, height=0.5, color=color, alpha=0.55)
    # Current price dot
    ax.scatter(cur_pct, i, color=color, s=90, zorder=5, edgecolors='white', linewidths=0.8)
    # Stock label on left
    ax.text(-1, i, sym, ha='right', va='center', fontsize=8.5, fontweight='bold')
    # Current price label on dot
    ax.text(cur_pct, i + 0.33, f'₹{cur:,.0f}  ({pos:.1f}%)', ha='center', fontsize=7.5, color=color, fontweight='bold')
    # 52W low / high labels at ends
    ax.text(0,   i - 0.35, f'₹{lo:,.0f}', ha='left',  fontsize=6.5, color='#7f8c8d')
    ax.text(100, i - 0.35, f'₹{hi:,.0f}', ha='right', fontsize=6.5, color='#7f8c8d')

ax.set_xlim(-2, 108)
ax.set_yticks([])
ax.set_xlabel('52W Position %  (0% = 52W Low  →  100% = 52W High)')
ax.axvline(20,  color='#e74c3c', linestyle='--', linewidth=0.8, alpha=0.5)
ax.axvline(80,  color='#2ecc71', linestyle='--', linewidth=0.8, alpha=0.5)
ax.axvline(50,  color='grey',    linestyle=':',  linewidth=0.8, alpha=0.4)
ax.set_title('Current Price vs 52W Range  (x-axis = % position  |  label = ₹ price)', fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.2)
plt.tight_layout()
plt.show()"""))

# ── 8d. 1-Year trend for near-high and near-low stocks ────────────────────
cells.append(cell('markdown', "## 8d. Chart — 1-Year Price Trend (Near High & Low Stocks)"))

cells.append(cell('code', """\
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def split_adjusted_pct(grp, split_threshold=0.45):
    \"\"\"Return % change series adjusted for stock splits.
    A single-day drop > split_threshold (45%) is treated as a split event;
    all prior prices are scaled down by the same ratio so the series is continuous.
    \"\"\"
    close = grp['close'].copy()
    daily_ret = close.pct_change()
    split_days = daily_ret[daily_ret < -split_threshold].index
    for sd in split_days:
        ratio = close.loc[sd] / close.shift(1).loc[sd]   # e.g. 0.5 for 2:1 split
        close.loc[close.index < sd] *= ratio
    base = close.iloc[0]
    return (close / base - 1) * 100

_near_syms_high = near_high['Symbol'].tolist() if not near_high.empty else []
_near_syms_low  = near_low['Symbol'].tolist()  if not near_low.empty  else []

if not _near_syms_high and not _near_syms_low:
    print('No near-high or near-low stocks to plot.')
else:
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=False)
    fig.suptitle('1-Year Price Trend — Near 52W High & Low Stocks\\n(% change, split-adjusted)', fontsize=12, fontweight='bold')

    for ax, syms, title, base_color in [
        (axes[0], _near_syms_high, 'Near 52W HIGH', '#27ae60'),
        (axes[1], _near_syms_low,  'Near 52W LOW',  '#c0392b'),
    ]:
        if not syms:
            ax.text(0.5, 0.5, 'None', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontsize=11, color=base_color)
            continue
        for sym in syms:
            grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
            pct  = split_adjusted_pct(grp)
            ax.plot(grp.index, pct, linewidth=1.5, label=sym, alpha=0.85)
            ax.annotate(sym, xy=(grp.index[-1], pct.iloc[-1]),
                        xytext=(3, 0), textcoords='offset points', fontsize=7.5, va='center')
        ax.axhline(0, color='grey', linewidth=0.8, linestyle='--', alpha=0.5)
        ax.set_title(title, fontsize=11, color=base_color, fontweight='bold')
        ax.set_ylabel('% Change from year start (split-adjusted)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
        ax.legend(fontsize=7.5, loc='upper left')
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.show()"""))

# ── 9. Simple df.plot chart: All stocks 52W Position ────────────────────
cells.append(cell('markdown', "## 9. Chart — All Stocks 52W Position (df.plot)"))

cells.append(cell('code', """\
plot_df = r1[['Symbol', '52W_Position']].set_index('Symbol').sort_values('52W_Position')
colors = ['#e74c3c' if v <= 20 else '#2ecc71' if v >= 80 else '#3498db'
          for v in plot_df['52W_Position']]

ax = plot_df.plot.barh(figsize=(10, 8), color=colors, legend=False)
ax.set_xlabel('52W Position %')
ax.set_title('All Stocks — 52-Week Position\\n(red ≤20%  |  blue = mid  |  green ≥80%)', fontsize=12)
ax.axvline(20,  color='#e74c3c', linestyle='--', linewidth=1, alpha=0.6)
ax.axvline(80,  color='#2ecc71', linestyle='--', linewidth=1, alpha=0.6)
ax.axvline(50,  color='grey',    linestyle=':',  linewidth=1, alpha=0.5)
for p in ax.patches:
    ax.text(p.get_width() + 0.5, p.get_y() + p.get_height() / 2,
            f'{p.get_width():.1f}%', va='center', fontsize=8)
import matplotlib.pyplot as plt
plt.tight_layout()
plt.show()"""))

# ── 10. Save ───────────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 10. Save to CSV"))

cells.append(cell('code', """\
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
os.makedirs('dump', exist_ok=True)
out_path = f'dump/NSE-ANALYSIS-{timestamp}.csv'

csv_sections = [
    pd.DataFrame([['=== REPORT 1: 52W Hi/Low Position ===']]), r1, pd.DataFrame([[]]),
    pd.DataFrame([['=== REPORT 2A: Crossed Last 5 Days ===']]),
    crossed.reset_index(drop=True) if not cross_df.empty and not crossed.empty else pd.DataFrame([['(none)']]),
    pd.DataFrame([[]]),
    pd.DataFrame([['=== REPORT 2B: Nearing Crossover ===']]),
    nearing.reset_index(drop=True) if not cross_df.empty and not nearing.empty else pd.DataFrame([['(none)']]),
    pd.DataFrame([[]]),
    pd.DataFrame([['=== REPORT 3: MACD Signals (Score>=2) ===']]),
    r3_display.reset_index(drop=True) if not r3_display.empty else pd.DataFrame([['(none)']]),
    pd.DataFrame([[]]),
    pd.DataFrame([['=== REPORT 4A: Near 52W HIGH ===']]),
    near_high.reset_index(drop=True) if not near_high.empty else pd.DataFrame([['(none)']]),
    pd.DataFrame([[]]),
    pd.DataFrame([['=== REPORT 4B: Near 52W LOW ===']]),
    near_low.reset_index(drop=True) if not near_low.empty else pd.DataFrame([['(none)']]),
    pd.DataFrame([[]]),
]

with open(out_path, 'w', newline='') as f:
    for section in csv_sections:
        section.to_csv(f, index=False, header=True)
        f.write('\\n')

print(f'Reports saved to: {out_path}')
if skipped:
    print(f'Skipped stocks: {skipped}')"""))

# ── 11. Send Email ─────────────────────────────────────────────────────────
cells.append(cell('markdown', "## 11. Send Email"))

cells.append(cell('code', """\
import io, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

EMAIL_FROM = 'peri47.study@gmail.com'
EMAIL_TO   = 'peri47.study@gmail.com'
EMAIL_PASS = 'fhih lsqp wanu leic'

def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    return buf.read()

def create_52w_position_chart(r1):
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

def create_52w_color_chart(hl_df):
    fig, ax = plt.subplots(figsize=(20, 5))
    all_pos = hl_df[['Symbol', '52W_Position']].dropna()
    low = all_pos[all_pos['52W_Position'] <= 30]
    mid = all_pos[(all_pos['52W_Position'] > 30) & (all_pos['52W_Position'] <= 65)]
    high = all_pos[all_pos['52W_Position'] > 65]
    ax.bar(low['Symbol'], low['52W_Position'], color='red', label='% < 30')
    ax.bar(mid['Symbol'], mid['52W_Position'], color='blue', label='30 < % < 65')
    ax.bar(high['Symbol'], high['52W_Position'], color='green', label='% > 65')
    ax.set_title('52W H/L Position — Color Coded', fontsize=12)
    ax.set_ylabel('52W Position %')
    ax.legend()
    ax.tick_params(axis='x', rotation=90, labelsize=7)
    plt.tight_layout()
    return fig

def create_crossover_chart(cross_df, combined):
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

def build_crossover_summary(cross_df, combined, hl_df):
    sma_pairs = {'200/20': (20, 200), '100/10': (10, 100), '50/5': (5, 50)}
    crossed_data = []
    
    if not cross_df.empty:
        for _, row in cross_df[cross_df['crossed_last_5d'] == True].iterrows():
            sym = row['Symbol']
            cross_type = row['cross_type']
            cross_date = row['last_cross_date']
            
            grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
            short_p, long_p = sma_pairs[cross_type]
            sma_s = grp['close'].rolling(short_p).mean()
            sma_l = grp['close'].rolling(long_p).mean()
            signal_pct = ((sma_s.iloc[-1] - sma_l.iloc[-1]) / sma_l.iloc[-1] * 100)
            
            cross_dt = pd.to_datetime(cross_date)
            days_since = (grp.index[-1] - cross_dt).days
            
            cur_price = grp['close'].iloc[-1]
            hl_row = hl_df[hl_df['Symbol'] == sym]
            pos_52w = hl_row['52W_Position'].values[0] if not hl_row.empty else None
            
            crossed_data.append({
                'Symbol': sym, 'Cross Type': cross_type, 'Cross Date': cross_date,
                'Days Ago': days_since, 'Signal %': round(signal_pct, 2),
                'Current Price': round(cur_price, 2),
                '52W Position': round(pos_52w, 1) if pos_52w else None,
                'Direction': '▲ Golden' if signal_pct > 0 else '▼ Death'
            })
    
    return pd.DataFrame(crossed_data).sort_values('Signal %', ascending=False) if crossed_data else pd.DataFrame()

def create_crossover_heatmap(cross_summary):
    if cross_summary.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(12, max(4, len(cross_summary) * 0.4)))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = [[row['Symbol'], row['Cross Type'], row['Direction'],
                   f\"{row['Days Ago']}d\", f\"{row['Signal %']:.2f}%\",
                   f\"₹{row['Current Price']:.0f}\",
                   f\"{row['52W Position']:.1f}%\" if row['52W Position'] else 'N/A']
                  for _, row in cross_summary.iterrows()]
    
    table = ax.table(cellText=table_data,
                     colLabels=['Symbol', 'Cross Type', 'Direction', 'Days Ago', 'Signal %', 'Price', '52W Pos%'],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Color code cells
    for i, row in enumerate(cross_summary.itertuples(), start=1):
        if '▲' in row.Direction:
            table[(i, 2)].set_facecolor('#d4edda')
        else:
            table[(i, 2)].set_facecolor('#f8d7da')
        
        sig = row._5
        if sig > 2:
            table[(i, 4)].set_facecolor('#d4edda')
        elif sig < -2:
            table[(i, 4)].set_facecolor('#f8d7da')
        else:
            table[(i, 4)].set_facecolor('#fff3cd')
        
        pos = row._7
        if pos and pos > 70:
            table[(i, 6)].set_facecolor('#d4edda')
        elif pos and pos < 30:
            table[(i, 6)].set_facecolor('#f8d7da')
    
    for j in range(7):
        table[(0, j)].set_facecolor('#e9ecef')
        table[(0, j)].set_text_props(weight='bold')
    
    ax.set_title('SMA Crossover Summary — Last 5 Days', fontsize=12, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def create_52w_range_chart(hl_df):
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
        ax.text(pos, i + 0.33, f'₹{cur:,.0f}  ({pos:.1f}%)', ha='center', fontsize=7.5, color=color, fontweight='bold')
        ax.text(0, i - 0.35, f'₹{lo:,.0f}', ha='left', fontsize=6.5, color='#7f8c8d')
        ax.text(100, i - 0.35, f'₹{hi:,.0f}', ha='right', fontsize=6.5, color='#7f8c8d')
    
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

# Generate all charts
chart_images = {}

fig = create_52w_position_chart(r1)
chart_images['52w_position'] = fig_to_bytes(fig)
plt.close(fig)

fig = create_macd_chart(macd_df)
chart_images['macd'] = fig_to_bytes(fig)
plt.close(fig)

fig = create_near_hl_chart(near_high, near_low)
chart_images['52w_hl'] = fig_to_bytes(fig)
plt.close(fig)

fig = create_52w_color_chart(hl_df)
chart_images['52w_color'] = fig_to_bytes(fig)
plt.close(fig)

fig = create_crossover_chart(cross_df, combined)
if fig:
    chart_images['crossover'] = fig_to_bytes(fig)
    plt.close(fig)

cross_summary_email = build_crossover_summary(cross_df, combined, hl_df)
fig = create_crossover_heatmap(cross_summary_email)
if fig:
    chart_images['xover_heatmap'] = fig_to_bytes(fig)
    plt.close(fig)

fig = create_52w_range_chart(hl_df)
chart_images['52w_range'] = fig_to_bytes(fig)
plt.close(fig)

fig = create_price_trend_chart(near_high, near_low, combined)
if fig:
    chart_images['52w_trend'] = fig_to_bytes(fig)
    plt.close(fig)

print(f'{len(chart_images)} charts prepared for email')"""))

cells.append(cell('code', """\
def df_to_html_table(df, title):
    return f'<h3>{title}</h3>' + df.to_html(index=False, border=1)

def embed_chart(cid, title, width=900):
    return f'<h2>{title}</h2><img src="cid:{cid}" width="{width}"><br><br>'

def build_html_body(r1, near_high, near_low, r3_display, cross_df, crossed,
                    cross_summary_email, chart_images):
    sections = ['<html><body>', '<h1>NSE Stock Analysis Report</h1>']
    
    # 52W Position summary
    sections.append(df_to_html_table(r1[['Symbol','Current_Price','52W_Position']].head(20),
                                     '52W Position (top 20)'))
    
    # Near High/Low tables and chart
    sections.append(df_to_html_table(near_high, 'Near 52W HIGH'))
    sections.append(df_to_html_table(near_low, 'Near 52W LOW'))
    if '52w_hl' in chart_images:
        sections.append(embed_chart('52w_hl', 'Near 52W High / Low'))
    
    # MACD table and chart
    if not r3_display.empty:
        sections.append(df_to_html_table(r3_display, 'MACD Signals (Score ≥ 2)'))
    if 'macd' in chart_images:
        sections.append(embed_chart('macd', 'MACD Overview — Top 15'))
    
    # Crossover tables and charts
    if not cross_df.empty and not crossed.empty:
        sections.append(df_to_html_table(crossed, 'Golden Crossover (last 5d)'))
    
    if 'xover_heatmap' in chart_images:
        sections.append(embed_chart('xover_heatmap', 'SMA Crossover Summary — Last 5 Days'))
    elif not cross_summary_email.empty:
        sections.append(df_to_html_table(cross_summary_email, 'SMA Crossover Summary (Last 5 Days)'))
    
    if 'crossover' in chart_images:
        sections.append(embed_chart('crossover', 'Cross-Over — 1 Year % Change (All Signals)'))
    
    # 52W Range chart
    if '52w_range' in chart_images:
        sections.append(embed_chart('52w_range', 'Current Price vs 52W Range (Top 15)'))
    
    # Price trend chart
    if '52w_trend' in chart_images:
        sections.append(embed_chart('52w_trend', '1-Year Price Trend — Near 52W High & Low Stocks'))
    
    sections.append('</body></html>')
    return ''.join(sections)

def assemble_and_send_email(html_body, chart_images):
    msg = MIMEMultipart('related')
    msg['Subject'] = f'NSE Analysis — {datetime.now().strftime("%d %b %Y")}'
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg.attach(MIMEText(html_body, 'html'))
    
    for cid, img_bytes in chart_images.items():
        img = MIMEImage(img_bytes, 'png')
        img.add_header('Content-ID', f'<{cid}>')
        msg.attach(img)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    
    print(f'Email sent to {EMAIL_TO} with {len(chart_images)} inline charts')

# Build and send email
html_body = build_html_body(r1, near_high, near_low, r3_display, cross_df,
                            crossed, cross_summary_email, chart_images)
assemble_and_send_email(html_body, chart_images)"""))

# ── Build notebook ─────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"}
    },
    "cells": cells
}

with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('NSE_Analysis.ipynb created successfully')

# Made with Bob
