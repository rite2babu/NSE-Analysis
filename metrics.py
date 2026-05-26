"""
NSE Analysis - Metric Calculation Functions
"""
import pandas as pd

BENCHMARK_ALIAS = '__BENCHMARK__'


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
    dist_high = ((current - h52) / h52 * 100) if h52 else float('nan')
    dist_low = ((current - l52) / l52 * 100) if l52 else float('nan')
    drawdown = ((current - h52) / h52 * 100) if h52 else float('nan')

    return {
        'Current_Price': round(current, 2),
        '52W_High': round(h52, 2), '52W_Low': round(l52, 2),
        '26W_High': round(h26, 2), '26W_Low': round(l26, 2),
        '4W_High': round(h4, 2), '4W_Low': round(l4, 2),
        '1W_High': round(h1, 2), '1W_Low': round(l1, 2),
        '52W_Position': round(pos, 2) if pos == pos else float('nan'),
        'Dist_From_52W_High_%': round(dist_high, 2) if dist_high == dist_high else float('nan'),
        'Dist_From_52W_Low_%': round(dist_low, 2) if dist_low == dist_low else float('nan'),
        'Drawdown_From_52W_High_%': round(drawdown, 2) if drawdown == drawdown else float('nan'),
    }


def compute_sma_crossovers(df):
    """Calculate SMA crossover signals"""
    df = df.sort_values('date').reset_index(drop=True)
    n = len(df)
    close = df['close']

    sma = {p: close.rolling(p).mean() if n >= p else pd.Series([float('nan')] * n, index=df.index)
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


def compute_ema_structure(df):
    """Calculate EMA structure and long-term trend metrics"""
    df = df.sort_values('date').reset_index(drop=True)
    close = df['close']
    n = len(df)

    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()
    current = close.iloc[-1]

    ema50_last = ema50.iloc[-1] if n >= 1 else float('nan')
    ema200_last = ema200.iloc[-1] if n >= 1 else float('nan')
    ema50_prev = ema50.iloc[-21] if n >= 21 else ema50.iloc[0]
    ema200_prev = ema200.iloc[-21] if n >= 21 else ema200.iloc[0]

    close_vs_ema50 = ((current - ema50_last) / ema50_last * 100) if ema50_last else float('nan')
    close_vs_ema200 = ((current - ema200_last) / ema200_last * 100) if ema200_last else float('nan')
    ema50_slope = ((ema50_last - ema50_prev) / ema50_prev * 100) if ema50_prev else float('nan')
    ema200_slope = ((ema200_last - ema200_prev) / ema200_prev * 100) if ema200_prev else float('nan')

    return {
        'EMA50': round(ema50_last, 2) if ema50_last == ema50_last else float('nan'),
        'EMA200': round(ema200_last, 2) if ema200_last == ema200_last else float('nan'),
        'Close_vs_EMA50_%': round(close_vs_ema50, 2) if close_vs_ema50 == close_vs_ema50 else float('nan'),
        'Close_vs_EMA200_%': round(close_vs_ema200, 2) if close_vs_ema200 == close_vs_ema200 else float('nan'),
        'EMA50_above_EMA200': bool(ema50_last > ema200_last) if ema50_last == ema50_last and ema200_last == ema200_last else False,
        'EMA50_Slope_%': round(ema50_slope, 2) if ema50_slope == ema50_slope else float('nan'),
        'EMA200_Slope_%': round(ema200_slope, 2) if ema200_slope == ema200_slope else float('nan'),
    }


def compute_rsi(df, period=14):
    """Calculate daily and weekly RSI"""
    df = df.sort_values('date').reset_index(drop=True)

    def calculate_rsi(series, lookback):
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / lookback, min_periods=lookback, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / lookback, min_periods=lookback, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    close = df['close']
    daily_rsi = calculate_rsi(close, period)

    weekly = (
        df.set_index('date')['close']
        .resample('W-FRI')
        .last()
        .dropna()
    )
    weekly_rsi = calculate_rsi(weekly, period)

    daily_last = daily_rsi.iloc[-1] if not daily_rsi.empty else float('nan')
    daily_prev = daily_rsi.iloc[-6] if len(daily_rsi) >= 6 else daily_rsi.iloc[0] if not daily_rsi.empty else float('nan')
    weekly_last = weekly_rsi.iloc[-1] if not weekly_rsi.empty else float('nan')
    weekly_prev = weekly_rsi.iloc[-2] if len(weekly_rsi) >= 2 else weekly_rsi.iloc[0] if not weekly_rsi.empty else float('nan')

    return {
        'RSI_14_Daily': round(daily_last, 2) if daily_last == daily_last else float('nan'),
        'RSI_14_Weekly': round(weekly_last, 2) if weekly_last == weekly_last else float('nan'),
        'RSI_Daily_Trend': round(daily_last - daily_prev, 2) if daily_last == daily_last and daily_prev == daily_prev else float('nan'),
        'RSI_Weekly_Trend': round(weekly_last - weekly_prev, 2) if weekly_last == weekly_last and weekly_prev == weekly_prev else float('nan'),
    }


def compute_adx(df, period=14):
    """Calculate ADX and directional indicators"""
    df = df.sort_values('date').reset_index(drop=True)
    if len(df) < period + 1:
        return {
            'ADX_14': float('nan'),
            'Plus_DI_14': float('nan'),
            'Minus_DI_14': float('nan'),
        }

    high = df['high']
    low = df['low']
    close = df['close']

    plus_dm = high.diff()
    minus_dm = low.shift(1) - low

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr = pd.concat([
        (high - low),
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)

    atr = tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr)
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)) * 100
    adx = dx.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    return {
        'ADX_14': round(adx.iloc[-1], 2) if adx.iloc[-1] == adx.iloc[-1] else float('nan'),
        'Plus_DI_14': round(plus_di.iloc[-1], 2) if plus_di.iloc[-1] == plus_di.iloc[-1] else float('nan'),
        'Minus_DI_14': round(minus_di.iloc[-1], 2) if minus_di.iloc[-1] == minus_di.iloc[-1] else float('nan'),
    }


def compute_turnaround_signals(df):
    """Calculate simple stabilisation and breakout signals"""
    df = df.sort_values('date').reset_index(drop=True)
    close = df['close']
    if 'volume' in df.columns:
        volume = pd.Series(pd.to_numeric(df['volume'], errors='coerce'), index=df.index, dtype='float64')
    else:
        volume = pd.Series([float('nan')] * len(df), index=df.index, dtype='float64')
    n = len(df)

    lookback_20 = close.tail(min(20, n))
    prev_20 = close.iloc[-40:-20] if n >= 40 else close.iloc[:-20]
    no_new_low_20d = bool(lookback_20.min() >= prev_20.min()) if len(prev_20) > 0 else False
    range_contraction = float('nan')
    breakout_20d = False
    volume_ratio = float('nan')

    if len(lookback_20) >= 5:
        recent_range = (lookback_20.max() - lookback_20.min()) / lookback_20.min() * 100 if lookback_20.min() else float('nan')
        prior_window = close.iloc[-60:-20] if n >= 60 else close.iloc[:-20]
        if len(prior_window) >= 5 and prior_window.min() != 0:
            prior_range = (prior_window.max() - prior_window.min()) / prior_window.min() * 100
            if prior_range:
                range_contraction = (recent_range / prior_range) * 100

    if n >= 21:
        breakout_20d = bool(close.iloc[-1] > close.iloc[-21:-1].max())

    if len(volume) >= 20:
        avg_vol_20 = float(volume.tail(20).mean())
        if avg_vol_20 == avg_vol_20 and avg_vol_20 != 0.0:
            volume_ratio = float(volume.iloc[-1]) / avg_vol_20

    return {
        'No_New_Low_20D': no_new_low_20d,
        'Range_Contraction_20D_%': round(range_contraction, 2) if range_contraction == range_contraction else float('nan'),
        'Breakout_20D': breakout_20d,
        'Volume_Ratio_20D': round(volume_ratio, 2) if volume_ratio == volume_ratio else float('nan'),
    }


def compute_relative_strength(returns_df, benchmark_returns=None):
    """Add relative-strength columns against the supplied benchmark returns"""
    rs_df = returns_df.copy()
    benchmark_returns = benchmark_returns or {}

    for period in ['3M_%', '6M_%', '1Y_%']:
        bench_val = benchmark_returns.get(period, float('nan'))
        rs_col = f'RS_{period.replace("_%", "")}_%'
        if bench_val == bench_val:
            rs_df[rs_col] = (rs_df[period] - bench_val).round(2)
        else:
            rs_df[rs_col] = float('nan')

    return rs_df


def compute_composite_scores(metrics_df):
    """Add weakness and turnaround composite scores"""
    df = metrics_df.copy()

    def weakness_score(row):
        score = 0
        if pd.notna(row.get('RS_1Y_%')) and row['RS_1Y_%'] < 0:
            score -= 3
        if pd.notna(row.get('RS_6M_%')) and row['RS_6M_%'] < 0:
            score -= 2
        if pd.notna(row.get('3M_%')) and row['3M_%'] < 0:
            score -= 1
        if pd.notna(row.get('Close_vs_EMA200_%')) and row['Close_vs_EMA200_%'] < 0:
            score -= 2
        if not bool(row.get('EMA50_above_EMA200', False)):
            score -= 2
        if pd.notna(row.get('RSI_14_Weekly')) and row['RSI_14_Weekly'] < 50:
            score -= 1
        if pd.notna(row.get('Drawdown_From_52W_High_%')) and row['Drawdown_From_52W_High_%'] <= -25:
            score -= 1
        adx = row.get('ADX_14')
        plus_di = row.get('Plus_DI_14')
        minus_di = row.get('Minus_DI_14')
        if pd.notna(adx) and pd.notna(plus_di) and pd.notna(minus_di) and adx > 20 and minus_di > plus_di:
            score -= 1
        return score

    def turnaround_score(row):
        score = 0
        if pd.notna(row.get('RS_3M_%')) and row['RS_3M_%'] > 0:
            score += 2
        if bool(row.get('No_New_Low_20D', False)):
            score += 1
        if pd.notna(row.get('Close_vs_EMA50_%')) and row['Close_vs_EMA50_%'] > 0:
            score += 2
        if pd.notna(row.get('RSI_14_Daily')) and row['RSI_14_Daily'] > 50:
            score += 1
        if pd.notna(row.get('RSI_Weekly_Trend')) and row['RSI_Weekly_Trend'] > 0:
            score += 1
        if bool(row.get('Breakout_20D', False)):
            score += 2
        if pd.notna(row.get('Volume_Ratio_20D')) and row['Volume_Ratio_20D'] > 1.2:
            score += 1
        if pd.notna(row.get('Close_vs_EMA200_%')) and row['Close_vs_EMA200_%'] > 0:
            score += 2
        return score

    df['Weakness_Score'] = df.apply(weakness_score, axis=1)
    df['Turnaround_Score'] = df.apply(turnaround_score, axis=1)
    return df


def compute_all_metrics(combined, benchmark_symbol=None):
    """Compute all metrics for all stocks"""
    print('Computing metrics...')

    hl_rows = []
    cross_rows = []
    macd_rows = []
    return_rows = []
    ema_rows = []
    rsi_rows = []
    adx_rows = []
    turnaround_rows = []
    benchmark_returns = None

    for sym, grp in combined.groupby('symbol'):
        grp = grp.sort_values('date').reset_index(drop=True)

        short_name = grp['short_name'].iloc[0] if 'short_name' in grp.columns else None

        try:
            hl = compute_period_hl(grp)
            hl['Symbol'] = sym
            if short_name:
                hl['short_name'] = short_name
            hl_rows.append(hl)
        except Exception as e:
            print(f'  Warning [{sym}] HL: {e}')

        try:
            if len(grp) >= 5:
                for c in compute_sma_crossovers(grp):
                    c['Symbol'] = sym
                    if short_name:
                        c['short_name'] = short_name
                    cross_rows.append(c)
        except Exception as e:
            print(f'  Warning [{sym}] SMA: {e}')

        try:
            macd = compute_macd(grp)
            macd['Symbol'] = sym
            if short_name:
                macd['short_name'] = short_name
            macd_rows.append(macd)
        except Exception as e:
            print(f'  Warning [{sym}] MACD: {e}')

        try:
            ret = compute_period_returns(grp)
            if ret:
                ret['Symbol'] = sym
                if short_name:
                    ret['short_name'] = short_name
                return_rows.append(ret)
                if benchmark_symbol and sym == benchmark_symbol:
                    benchmark_returns = ret.copy()
        except Exception as e:
            print(f'  Warning [{sym}] Returns: {e}')

        try:
            ema = compute_ema_structure(grp)
            ema['Symbol'] = sym
            if short_name:
                ema['short_name'] = short_name
            ema_rows.append(ema)
        except Exception as e:
            print(f'  Warning [{sym}] EMA: {e}')

        try:
            rsi = compute_rsi(grp)
            rsi['Symbol'] = sym
            if short_name:
                rsi['short_name'] = short_name
            rsi_rows.append(rsi)
        except Exception as e:
            print(f'  Warning [{sym}] RSI: {e}')

        try:
            adx = compute_adx(grp)
            adx['Symbol'] = sym
            if short_name:
                adx['short_name'] = short_name
            adx_rows.append(adx)
        except Exception as e:
            print(f'  Warning [{sym}] ADX: {e}')

        try:
            turnaround = compute_turnaround_signals(grp)
            turnaround['Symbol'] = sym
            if short_name:
                turnaround['short_name'] = short_name
            turnaround_rows.append(turnaround)
        except Exception as e:
            print(f'  Warning [{sym}] Turnaround: {e}')

    hl_df = pd.DataFrame(hl_rows)
    cross_df = pd.DataFrame(cross_rows) if cross_rows else pd.DataFrame()
    macd_df = pd.DataFrame(macd_rows)
    returns_df = pd.DataFrame(return_rows)
    ema_df = pd.DataFrame(ema_rows)
    rsi_df = pd.DataFrame(rsi_rows)
    adx_df = pd.DataFrame(adx_rows)
    turnaround_df = pd.DataFrame(turnaround_rows)

    if benchmark_symbol and benchmark_returns is None and benchmark_symbol in combined['symbol'].unique():
        benchmark_grp = combined[combined['symbol'] == benchmark_symbol].sort_values('date').reset_index(drop=True)
        benchmark_returns = compute_period_returns(benchmark_grp)

    returns_df = compute_relative_strength(returns_df, benchmark_returns)

    join_keys = ['Symbol']
    base_df = returns_df.merge(hl_df.drop(columns=[c for c in ['short_name'] if c in hl_df.columns]), on='Symbol', how='left')
    base_df = base_df.merge(ema_df.drop(columns=[c for c in ['short_name'] if c in ema_df.columns]), on='Symbol', how='left')
    base_df = base_df.merge(rsi_df.drop(columns=[c for c in ['short_name'] if c in rsi_df.columns]), on='Symbol', how='left')
    base_df = base_df.merge(adx_df.drop(columns=[c for c in ['short_name'] if c in adx_df.columns]), on='Symbol', how='left')
    base_df = base_df.merge(turnaround_df.drop(columns=[c for c in ['short_name'] if c in turnaround_df.columns]), on='Symbol', how='left')

    if 'short_name' in returns_df.columns:
        short_names = returns_df[['Symbol', 'short_name']].drop_duplicates()
        base_df = short_names.merge(base_df, on='Symbol', how='right')

    metrics_df = compute_composite_scores(base_df)

    print(
        f'[OK] Metrics: {len(hl_df)} HL, {len(cross_df)} crossovers, {len(macd_df)} MACD, '
        f'{len(returns_df)} returns, {len(metrics_df)} composite rows'
    )

    return hl_df, cross_df, macd_df, returns_df, metrics_df


def create_crossover_summary_table(cross_df, combined):
    """
    Create summary table of crossover status (crossed, crossing, will cross) - last 10 days only.

    Args:
        cross_df: DataFrame with crossover signals
        combined: DataFrame with historical price data

    Returns:
        DataFrame with crossover summary or empty DataFrame
    """
    MAX_DAYS_AGO = 10
    NEARING_THRESHOLD = -1.0
    WILL_CROSS_THRESHOLD = -2.0
    LOOKBACK_PERIOD = 11

    if cross_df.empty or combined.empty:
        return pd.DataFrame()

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

            cross_direction = 'Golden Cross' if cross_pct > 0 else 'Death Cross'

            status, days_ago_text = _determine_crossover_status(
                crossed_last_5d, last_cross_date, nearing, cross_pct,
                current_time, MAX_DAYS_AGO, NEARING_THRESHOLD, WILL_CROSS_THRESHOLD
            )

            if status is None:
                continue

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
            return None, None
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
