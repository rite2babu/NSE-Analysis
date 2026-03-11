"""
NSE Analysis - Metric Calculation Functions
"""
import pandas as pd

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

# Made with Bob
