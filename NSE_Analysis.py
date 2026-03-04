"""
NSE Stock Analysis
Fetches 1 year of data and produces:
  1. 52W Hi/Low Position report
  2. Golden Crossover signals
  3. MACD signals
  4. Top 10 near 52W High/Low
Saves all reports to dump/NSE-ANALYSIS-{timestamp}.csv
"""

import pandas as pd
import numpy as np
from tabulate import tabulate
from datetime import datetime
import datetime as dt
import os
import time
import requests
import concurrent.futures
from nselib import capital_market
import nselib.capital_market.capital_market_data as _cm_data

# ── Configuration ────────────────────────────────────────────────────────────
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

# ── Helpers ───────────────────────────────────────────────────────────────────

def compute_period_hl(df):
    """Compute period high/low metrics for a single stock DataFrame (sorted by date)."""
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)

    def window_hl(days):
        rows = df.tail(days)
        return rows['high'].max(), rows['low'].min()

    w52 = min(252, n)
    w26 = min(126, n)
    w4  = min(20,  n)
    w1  = min(5,   n)

    h52, l52 = window_hl(w52)
    h26, l26 = window_hl(w26)
    h4,  l4  = window_hl(w4)
    h1,  l1  = window_hl(w1)

    current = df['close'].iloc[-1]
    rng = h52 - l52
    pos = (current - l52) / rng * 100 if rng > 0 else np.nan

    return {
        'Current_Price': round(current, 2),
        '52W_High': round(h52, 2), '52W_Low': round(l52, 2),
        '26W_High': round(h26, 2), '26W_Low': round(l26, 2),
        '4W_High':  round(h4,  2), '4W_Low':  round(l4,  2),
        '1W_High':  round(h1,  2), '1W_Low':  round(l1,  2),
        '52W_Position': round(pos, 2) if not np.isnan(pos) else np.nan,
    }


def compute_sma_crossovers(df):
    """Compute SMA crossover signals for a single stock DataFrame."""
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    close = df['close']

    sma = {}
    for p in [5, 10, 20, 50, 100, 200]:
        if n >= p:
            sma[p] = close.rolling(p).mean()
        else:
            sma[p] = pd.Series([np.nan] * n, index=df.index)

    pairs = [
        ('200/20',  20,  200),
        ('100/10',  10,  100),
        ('50/5',     5,   50),
    ]

    results = []
    for label, short_p, long_p in pairs:
        s = sma[short_p]
        l = sma[long_p]

        if s.isna().all() or l.isna().all():
            continue

        # crossover: short crosses above long (prev: short <= long, now: short > long)
        cross = (s > l) & (s.shift(1) <= l.shift(1))

        last5_cross = cross.iloc[-5:].any() if n >= 5 else False
        cross_dates = df['date'][cross]
        last_cross_date = cross_dates.iloc[-1].strftime('%Y-%m-%d') if not cross_dates.empty and last5_cross else None

        s_last = s.iloc[-1]
        l_last = l.iloc[-1]

        if pd.isna(s_last) or pd.isna(l_last):
            continue

        cross_pct = (s_last - l_last) / l_last * 100
        nearing = (-1.0 <= cross_pct <= 0)  # short is within 1% below long

        results.append({
            'cross_type':      label,
            'crossed_last_5d': bool(last5_cross),
            'last_cross_date': last_cross_date,
            'nearing':         bool(nearing),
            'cross_pct':       round(cross_pct, 3),
        })

    return results

def compute_sma_crossovers_ta(df):
    """
    Compute SMA crossover signals using pandas_ta library.
    Simpler alternative to compute_sma_crossovers().
    
    Usage: pip install pandas_ta
    """
    import pandas_ta as ta
    
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    
    # Calculate all SMAs in one go
    df.ta.sma(length=5, append=True)
    df.ta.sma(length=10, append=True)
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=100, append=True)
    df.ta.sma(length=200, append=True)
    
    pairs = [
        ('200/20',  'SMA_20',  'SMA_200'),
        ('100/10',  'SMA_10',  'SMA_100'),
        ('50/5',    'SMA_5',   'SMA_50'),
    ]
    
    results = []
    for label, short_col, long_col in pairs:
        if short_col not in df.columns or long_col not in df.columns:
            continue
            
        s = df[short_col]
        l = df[long_col]
        
        if s.isna().all() or l.isna().all():
            continue
        
        # Crossover detection
        cross = (s > l) & (s.shift(1) <= l.shift(1))
        last5_cross = cross.iloc[-5:].any() if n >= 5 else False
        cross_dates = df['date'][cross]
        last_cross_date = cross_dates.iloc[-1].strftime('%Y-%m-%d') if not cross_dates.empty and last5_cross else None
        
        s_last = s.iloc[-1]
        l_last = l.iloc[-1]
        
        if pd.isna(s_last) or pd.isna(l_last):
            continue
        
        cross_pct = (s_last - l_last) / l_last * 100
        nearing = (-1.0 <= cross_pct <= 0)
        
        results.append({
            'cross_type':      label,
            'crossed_last_5d': bool(last5_cross),
            'last_cross_date': last_cross_date,
            'nearing':         bool(nearing),
            'cross_pct':       round(cross_pct, 3),
        })
    
    return results



def compute_macd(df):
    """Compute MACD signals for a single stock DataFrame."""
    df = df.sort_values('date').reset_index(drop=True)
    close = df['close']

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line   = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram   = macd_line - signal_line

    n = len(df)

    # bullish cross: macd crossed above signal in last 5 days
    cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
    bullish_cross = cross.iloc[-5:].any() if n >= 5 else False

    above_zero = bool(macd_line.iloc[-1] > 0)

    hist_inc = False
    if n >= 3:
        h = histogram.iloc[-3:].values
        hist_inc = bool(h[1] > h[0] and h[2] > h[1])

    score = int(bullish_cross) + int(above_zero) + int(hist_inc)

    return {
        'MACD':               round(macd_line.iloc[-1], 4),
        'Signal':             round(signal_line.iloc[-1], 4),
        'Histogram':          round(histogram.iloc[-1], 4),
        'Bullish_Cross':      bool(bullish_cross),
        'Above_Zero':         above_zero,
        'Hist_Increasing':    hist_inc,
        'MACD_Score':         score,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    os.makedirs('dump', exist_ok=True)
    out_path = f'dump/NSE-ANALYSIS-{timestamp}.csv'

    # ── 1. Fetch data ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  NSE Stock Analysis  --  {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"{'='*60}")
    print(f"Fetching data for {len(STOCK_LIST)} stocks (365 days)...")

    end_date   = dt.date.today().strftime('%d-%m-%Y')
    start_date = (dt.date.today() - dt.timedelta(days=365)).strftime('%d-%m-%Y')

    # Warm up a single shared requests session and patch nselib to reuse it
    print("Initialising shared NSE session...")
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
    print(f"  Session: HTTP {_r0.status_code}, cookies: {list(_shared_session.cookies.get_dict().keys())}")
    time.sleep(2)

    # Patch nselib to use our shared session (avoids per-call homepage hit)
    def _shared_urlfetch(url, origin_url="http://nseindia.com"):
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

    MAX_WORKERS = 5
    skipped = []
    frames = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {executor.submit(fetch_one, sym): sym for sym in STOCK_LIST}
        for future in concurrent.futures.as_completed(future_map):
            sym = future_map[future]
            try:
                df = future.result()
                print(f"  OK   {sym:20s}  {len(df)} rows")
                frames.append(df)
            except Exception as e:
                print(f"  SKIP {sym:20s}  {e}")
                skipped.append(sym)

    # ── 2. Combine into single DataFrame ──────────────────────────────────────
    if not frames:
        print("ERROR: No data fetched. Exiting.")
        return

    combined = pd.concat(frames, ignore_index=True)
    combined.sort_values(['symbol', 'date'], inplace=True)
    combined.reset_index(drop=True, inplace=True)
    print(f"\nCombined DataFrame: {len(combined)} rows, {combined['symbol'].nunique()} stocks")

    # ── 3. Compute metrics per stock ──────────────────────────────────────────
    hl_rows      = []
    cross_rows   = []
    macd_rows    = []

    for sym, grp in combined.groupby('symbol'):
        grp = grp.sort_values('date').reset_index(drop=True)

        # 3.1 Period High/Low
        try:
            hl = compute_period_hl(grp)
            hl['Symbol'] = sym
            hl_rows.append(hl)
        except Exception as e:
            print(f"  Warning [{sym}] period HL failed: {e}", flush=True)

        # 3.2 Golden Crossover
        try:
            if len(grp) < 5:
                raise ValueError("Insufficient data for SMA")
            crosses = compute_sma_crossovers(grp)
            for c in crosses:
                c['Symbol'] = sym
                cross_rows.append(c)
        except Exception as e:
            print(f"  Warning [{sym}] SMA crossover failed: {e}")

        # 3.3 MACD
        try:
            macd = compute_macd(grp)
            macd['Symbol'] = sym
            macd_rows.append(macd)
        except Exception as e:
            print(f"  Warning [{sym}] MACD failed: {e}")

    hl_df   = pd.DataFrame(hl_rows)
    cross_df = pd.DataFrame(cross_rows) if cross_rows else pd.DataFrame()
    macd_df  = pd.DataFrame(macd_rows)

    # ── 4. Reports ────────────────────────────────────────────────────────────
    csv_sections = []

    # ── Report 1: 52W Hi/Low Position ────────────────────────────────────────
    print(f"\n{'-'*60}")
    print("REPORT 1: All Stocks - 52W Hi/Low Position (Ascending)")
    print(f"{'-'*60}")

    r1 = pd.DataFrame(hl_df[[
        'Symbol', 'Current_Price',
        '52W_High', '52W_Low', '52W_Position',
        '26W_High', '26W_Low',
        '4W_High',  '4W_Low',
        '1W_High',  '1W_Low',
    ]]).sort_values('52W_Position').reset_index(drop=True)

    r1_display = r1.rename(columns={'52W_Position': '52W_Pos%'})
    print(tabulate(r1_display, headers='keys', tablefmt='grid', showindex=False,
                   floatfmt='.2f'))

    csv_sections.append(pd.DataFrame([['=== REPORT 1: 52W Hi/Low Position ===']]))
    csv_sections.append(r1)
    csv_sections.append(pd.DataFrame([[]]))

    # ── Report 2: Golden Crossover Signals ───────────────────────────────────
    print(f"\n{'-'*60}")
    print("REPORT 2: Golden Crossover Signals")
    print(f"{'-'*60}")

    if not cross_df.empty:
        # Sub-table A: crossed in last 5 days
        _crossed = pd.DataFrame(cross_df[cross_df['crossed_last_5d'] == True])
        _crossed = _crossed[['Symbol', 'cross_type', 'cross_pct', 'last_cross_date']]
        crossed = pd.DataFrame(_crossed).rename(columns={
            'cross_type': 'Cross Type', 'cross_pct': 'Cross%', 'last_cross_date': 'Cross Date'
        })

        print("\n  >> Crossed in last 5 days:")
        if not crossed.empty:
            print(tabulate(crossed, headers='keys', tablefmt='grid', showindex=False, floatfmt='.3f'))
        else:
            print("  (none)")

        # Sub-table B: nearing crossover
        _nearing = pd.DataFrame(cross_df[cross_df['nearing'] == True])
        _nearing = _nearing[['Symbol', 'cross_type', 'cross_pct']]
        nearing = pd.DataFrame(_nearing).rename(columns={
            'cross_type': 'Cross Type', 'cross_pct': 'Cross% (neg=below)'
        })

        print("\n  >> Nearing crossover (short SMA within 1% below long SMA):")
        if not nearing.empty:
            print(tabulate(nearing, headers='keys', tablefmt='grid', showindex=False, floatfmt='.3f'))
        else:
            print("  (none)")

        csv_sections.append(pd.DataFrame([['=== REPORT 2A: Crossed Last 5 Days ===']]))
        csv_sections.append(crossed if not crossed.empty else pd.DataFrame([['(none)']]))
        csv_sections.append(pd.DataFrame([[]]))
        csv_sections.append(pd.DataFrame([['=== REPORT 2B: Nearing Crossover ===']]))
        csv_sections.append(nearing if not nearing.empty else pd.DataFrame([['(none)']]))
        csv_sections.append(pd.DataFrame([[]]))
    else:
        print("  No crossover data available.")

    # ── Report 3: MACD Signals ────────────────────────────────────────────────
    print(f"\n{'-'*60}")
    print("REPORT 3: MACD Signals (Score >= 2)")
    print(f"{'-'*60}")

    r3 = pd.DataFrame(macd_df[macd_df['MACD_Score'] >= 2]).sort_values('MACD_Score', ascending=False)
    _r3 = r3[['Symbol', 'MACD', 'Signal', 'Histogram',
               'Bullish_Cross', 'Above_Zero', 'Hist_Increasing', 'MACD_Score']]
    r3_display = pd.DataFrame(_r3).rename(columns={
        'Bullish_Cross': 'Bullish X', 'Above_Zero': 'Above 0',
        'Hist_Increasing': 'Hist Inc', 'MACD_Score': 'Score'
    })

    if not r3_display.empty:
        print(tabulate(r3_display, headers='keys', tablefmt='grid', showindex=False, floatfmt='.4f'))
    else:
        print("  (no stocks with MACD score >= 2)")

    csv_sections.append(pd.DataFrame([['=== REPORT 3: MACD Signals (Score>=2) ===']]))
    csv_sections.append(r3_display if not r3_display.empty else pd.DataFrame([['(none)']]))
    csv_sections.append(pd.DataFrame([[]]))

    # ── Report 4: Top 10 near 52W High/Low ───────────────────────────────────
    print(f"\n{'-'*60}")
    print("REPORT 4: Top 10 Near 52W High/Low")
    print(f"{'-'*60}")

    r4_cols = ['Symbol', 'Current_Price', '52W_High', '52W_Low', '52W_Position']

    near_high = pd.DataFrame(hl_df[hl_df['52W_Position'] >= 80]).sort_values(
        '52W_Position', ascending=False).head(10)[r4_cols]
    near_low  = pd.DataFrame(hl_df[hl_df['52W_Position'] <= 20]).sort_values(
        '52W_Position', ascending=True).head(10)[r4_cols]

    print("\n  >> Top 10 near 52W HIGH (position >= 80%):")
    if not near_high.empty:
        print(tabulate(near_high, headers='keys', tablefmt='grid', showindex=False, floatfmt='.2f'))
    else:
        print("  (none)")

    print("\n  >> Top 10 near 52W LOW (position <= 20%):")
    if not near_low.empty:
        print(tabulate(near_low, headers='keys', tablefmt='grid', showindex=False, floatfmt='.2f'))
    else:
        print("  (none)")

    csv_sections.append(pd.DataFrame([['=== REPORT 4A: Near 52W HIGH ===']]))
    csv_sections.append(near_high if not near_high.empty else pd.DataFrame([['(none)']]))
    csv_sections.append(pd.DataFrame([[]]))
    csv_sections.append(pd.DataFrame([['=== REPORT 4B: Near 52W LOW ===']]))
    csv_sections.append(near_low if not near_low.empty else pd.DataFrame([['(none)']]))
    csv_sections.append(pd.DataFrame([[]]))

    # ── 5. Save to CSV ────────────────────────────────────────────────────────
    with open(out_path, 'w', newline='') as f:
        for section in csv_sections:
            section.to_csv(f, index=False, header=True)
            f.write('\n')

    print(f"\n{'='*60}")
    print(f"  Reports saved to: {out_path}")
    if skipped:
        print(f"  Skipped stocks:   {', '.join(skipped)}")
    print(f"{'='*60}")
    print()


if __name__ == '__main__':
    main()

# Made with Bob
