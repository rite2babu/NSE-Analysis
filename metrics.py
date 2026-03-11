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

def create_crossover_summary_table(cross_df, combined):
    """Create summary table of crossover status (crossed, crossing, will cross) - last 10 days only"""
    if cross_df.empty:
        return pd.DataFrame()
    
    summary_rows = []
    
    for _, row in cross_df.iterrows():
        symbol = row['Symbol']
        cross_type = row['cross_type']
        cross_pct = row['cross_pct']
        crossed_last_5d = row['crossed_last_5d']
        last_cross_date = row.get('last_cross_date', None)
        nearing = row['nearing']
        
        # Determine if Golden Cross (bullish) or Death Cross (bearish)
        if crossed_last_5d or cross_pct >= -1.0:
            cross_direction = 'Golden Cross'
        else:
            cross_direction = 'Death Cross'
        
        # Determine status and calculate days ago if crossed
        days_ago_text = ''
        if crossed_last_5d and last_cross_date:
            # Calculate days ago from last_cross_date
            try:
                cross_date = pd.to_datetime(last_cross_date)
                today = pd.Timestamp.now()
                days_ago = (today - cross_date).days
                if days_ago <= 10:  # Only include if within last 10 days
                    status = 'Crossed'
                    days_ago_text = f'{days_ago}d ago'
                else:
                    continue  # Skip if crossed more than 10 days ago
            except:
                status = 'Crossed'
                days_ago_text = 'Recent'
        elif nearing:
            status = 'Crossing Soon'
            days_ago_text = f'{abs(cross_pct):.2f}% away'
        elif -2.0 <= cross_pct < -1.0:
            status = 'Will Cross'
            days_ago_text = f'{abs(cross_pct):.2f}% away'
        else:
            continue  # Skip others
        
        # Get recent price data for context
        stock_data = combined[combined['symbol'] == symbol].sort_values('date')
        if not stock_data.empty:
            recent_close = stock_data['close'].iloc[-1]
            days_10_ago_close = stock_data['close'].iloc[-11] if len(stock_data) >= 11 else stock_data['close'].iloc[0]
            pct_change_10d = ((recent_close - days_10_ago_close) / days_10_ago_close * 100) if days_10_ago_close > 0 else 0
        else:
            pct_change_10d = 0
        
        summary_rows.append({
            'Symbol': symbol,
            'Type': cross_direction,
            'Cross': cross_type,
            'Status': status,
            'Cross %': f'{cross_pct:.2f}%',
            '10D Chg': f'{pct_change_10d:.1f}%',
            'When': days_ago_text
        })
    
    if not summary_rows:
        return pd.DataFrame()
    
    summary_df = pd.DataFrame(summary_rows)
    
    # Sort by Cross Type (50/5, 100/10, 200/20), then by Status, then by Cross %
    cross_type_order = {'50/5': 1, '100/10': 2, '200/20': 3}
    status_order = {'Crossed': 1, 'Crossing Soon': 2, 'Will Cross': 3}
    summary_df['_cross_sort'] = summary_df['Cross'].map(cross_type_order)
    summary_df['_status_sort'] = summary_df['Status'].map(status_order)
    summary_df = summary_df.sort_values(['_cross_sort', '_status_sort', 'Cross %']).drop(['_cross_sort', '_status_sort'], axis=1)
    
    return summary_df

# Made with Bob
