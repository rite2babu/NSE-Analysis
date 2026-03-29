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
        # Return NaN if insufficient data - ensures accurate period calculations
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
        
        # Get short_name if available
        short_name = grp['short_name'].iloc[0] if 'short_name' in grp.columns else None
        
        # High/Low
        try:
            hl = compute_period_hl(grp)
            hl['Symbol'] = sym
            if short_name:
                hl['short_name'] = short_name
            hl_rows.append(hl)
        except Exception as e:
            print(f'  Warning [{sym}] HL: {e}')
        
        # Crossovers
        try:
            if len(grp) >= 5:
                for c in compute_sma_crossovers(grp):
                    c['Symbol'] = sym
                    if short_name:
                        c['short_name'] = short_name
                    cross_rows.append(c)
        except Exception as e:
            print(f'  Warning [{sym}] SMA: {e}')
        
        # MACD
        try:
            macd = compute_macd(grp)
            macd['Symbol'] = sym
            if short_name:
                macd['short_name'] = short_name
            macd_rows.append(macd)
        except Exception as e:
            print(f'  Warning [{sym}] MACD: {e}')
        
        # Returns
        try:
            ret = compute_period_returns(grp)
            if ret:
                ret['Symbol'] = sym
                if short_name:
                    ret['short_name'] = short_name
                return_rows.append(ret)
        except Exception as e:
            print(f'  Warning [{sym}] Returns: {e}')
    
    hl_df = pd.DataFrame(hl_rows)
    cross_df = pd.DataFrame(cross_rows) if cross_rows else pd.DataFrame()
    macd_df = pd.DataFrame(macd_rows)
    returns_df = pd.DataFrame(return_rows)
    
    print(f'[OK] Metrics: {len(hl_df)} HL, {len(cross_df)} crossovers, {len(macd_df)} MACD, {len(returns_df)} returns')
    
    return hl_df, cross_df, macd_df, returns_df

def create_crossover_summary_table(cross_df, combined):
    """
    Create summary table of crossover status (crossed, crossing, will cross) - last 10 days only.
    
    Args:
        cross_df: DataFrame with crossover signals
        combined: DataFrame with historical price data
        
    Returns:
        DataFrame with crossover summary or empty DataFrame
    """
    # Constants
    MAX_DAYS_AGO = 10
    NEARING_THRESHOLD = -1.0
    WILL_CROSS_THRESHOLD = -2.0
    LOOKBACK_PERIOD = 11  # 10 days + current day
    
    if cross_df.empty or combined.empty:
        return pd.DataFrame()
    
    # Pre-process combined data for efficient lookups
    stock_cache = {}
    for symbol in cross_df['Symbol'].unique():
        stock_data = combined[combined['symbol'] == symbol].sort_values('date')
        if not stock_data.empty:
            stock_cache[symbol] = {
                'recent_close': stock_data['close'].iloc[-1],
                'lookback_close': stock_data['close'].iloc[-LOOKBACK_PERIOD] if len(stock_data) >= LOOKBACK_PERIOD else stock_data['close'].iloc[0]
            }
    
    summary_rows = []
    current_time = pd.Timestamp.now(tz='UTC')
    
    for _, row in cross_df.iterrows():
        symbol = row.get('Symbol', 'UNKNOWN')
        try:
            cross_type = row['cross_type']
            cross_pct = row['cross_pct']
            crossed_last_5d = row['crossed_last_5d']
            last_cross_date = row.get('last_cross_date')
            nearing = row['nearing']
            
            # Determine crossover direction: Golden (bullish) if short > long, Death (bearish) if short < long
            cross_direction = 'Golden Cross' if cross_pct > 0 else 'Death Cross'
            
            # Determine status and timing
            status, days_ago_text = _determine_crossover_status(
                crossed_last_5d, last_cross_date, nearing, cross_pct,
                current_time, MAX_DAYS_AGO, NEARING_THRESHOLD, WILL_CROSS_THRESHOLD
            )
            
            if status is None:
                continue  # Skip if doesn't meet criteria
            
            # Calculate 10-day price change
            pct_change_10d = _calculate_price_change(symbol, stock_cache)
            
            summary_rows.append({
                'Symbol': symbol,
                'Type': cross_direction,
                'Cross': cross_type,
                'Status': status,
                'Cross %': f'{cross_pct:.2f}%',
                '10D Chg': f'{pct_change_10d:.1f}%',
                'When': days_ago_text
            })
            
        except Exception as e:
            print(f'  Warning [{symbol}] Crossover summary: {e}')
            continue
    
    if not summary_rows:
        return pd.DataFrame()
    
    return _sort_summary_dataframe(pd.DataFrame(summary_rows))


def _determine_crossover_status(crossed_last_5d, last_cross_date, nearing, cross_pct,
                                 current_time, max_days, nearing_threshold, will_cross_threshold):
    """Determine crossover status and timing text."""
    if crossed_last_5d and last_cross_date:
        try:
            cross_date = pd.to_datetime(last_cross_date).tz_localize('UTC') if pd.to_datetime(last_cross_date).tz is None else pd.to_datetime(last_cross_date)
            days_ago = (current_time - cross_date).days
            
            if days_ago <= max_days:
                return 'Crossed', f'{days_ago}d ago'
            return None, None  # Too old
        except Exception:
            return 'Crossed', 'Recent'
    
    elif nearing:
        return 'Crossing Soon', f'{abs(cross_pct):.2f}% away'
    
    elif will_cross_threshold <= cross_pct < nearing_threshold:
        return 'Will Cross', f'{abs(cross_pct):.2f}% away'
    
    return None, None


def _calculate_price_change(symbol, stock_cache):
    """Calculate 10-day percentage price change."""
    if symbol not in stock_cache:
        return 0.0
    
    cache = stock_cache[symbol]
    recent = cache['recent_close']
    lookback = cache['lookback_close']
    
    if lookback > 0:
        return ((recent - lookback) / lookback) * 100
    return 0.0


def _sort_summary_dataframe(df):
    """Sort summary DataFrame by cross type, status, and percentage."""
    cross_type_order = {'50/5': 1, '100/10': 2, '200/20': 3}
    status_order = {'Crossed': 1, 'Crossing Soon': 2, 'Will Cross': 3}
    
    df['_cross_sort'] = df['Cross'].map(cross_type_order)
    df['_status_sort'] = df['Status'].map(status_order)
    
    return df.sort_values(
        ['_cross_sort', '_status_sort', 'Cross %']
    ).drop(['_cross_sort', '_status_sort'], axis=1).reset_index(drop=True)

# Made with Bob
