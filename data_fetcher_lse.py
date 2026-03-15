"""
LSE/US Stock Analysis - Data Fetching Module using yfinance
"""
import os
import pandas as pd
import datetime as dt
import yfinance as yf
import concurrent.futures
from config_lse import CACHE_DIR_LSE, CACHE_FILE_LSE, CACHE_EXPIRY_HOURS

def fetch_one_yf(ticker, start_date, end_date):
    """Fetch data for one ticker using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data returned for {ticker}")
        
        # Rename columns to match NSE format
        df = df.reset_index()
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Add symbol column
        df['symbol'] = ticker
        
        # Select only required columns
        df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
        
        return df
    except Exception as e:
        raise Exception(f"Error fetching {ticker}: {str(e)}")

def is_cache_valid_lse(required_days=365):
    """Check if cache exists, is not expired, contains today's data, and has sufficient historical data"""
    if not os.path.exists(CACHE_FILE_LSE):
        return False
    
    # Check file age
    cache_time = dt.datetime.fromtimestamp(os.path.getmtime(CACHE_FILE_LSE))
    age_hours = (dt.datetime.now() - cache_time).total_seconds() / 3600
    
    if age_hours >= CACHE_EXPIRY_HOURS:
        return False
    
    # Check if cache contains recent data and has sufficient historical range
    try:
        cache_df = pd.read_csv(CACHE_FILE_LSE)
        cache_df['date'] = pd.to_datetime(cache_df['date'])
        latest_cache_date = cache_df['date'].max().date()
        earliest_cache_date = cache_df['date'].min().date()
        today = dt.date.today()
        
        # Allow up to 3 days old data (for weekends/holidays)
        if (today - latest_cache_date).days > 3:
            print(f'[CACHE] Cache has data up to {latest_cache_date}, but today is {today}')
            return False
        
        # Check if cache has sufficient historical data
        cache_days = (latest_cache_date - earliest_cache_date).days
        if cache_days < required_days:
            print(f'[CACHE] Cache has only {cache_days} days of data, but {required_days} days required')
            return False
        
        return True
    except Exception as e:
        print(f'[CACHE] Error reading cache: {e}')
        return False

def load_from_cache_lse():
    """Load data from cache file"""
    print(f'[CACHE] Loading data from {CACHE_FILE_LSE}')
    combined = pd.read_csv(CACHE_FILE_LSE)
    combined['date'] = pd.to_datetime(combined['date'])
    
    cache_time = dt.datetime.fromtimestamp(os.path.getmtime(CACHE_FILE_LSE))
    age_hours = (dt.datetime.now() - cache_time).total_seconds() / 3600
    print(f'[CACHE] Data age: {age_hours:.1f} hours')
    print(f'[OK] Loaded: {len(combined)} rows, {combined["symbol"].nunique()} stocks from cache')
    
    return combined, []

def save_to_cache_lse(combined):
    """Save data to cache file"""
    os.makedirs(CACHE_DIR_LSE, exist_ok=True)
    combined.to_csv(CACHE_FILE_LSE, index=False)
    print(f'[CACHE] Saved data to {CACHE_FILE_LSE}')

def fetch_all_data_lse(stock_list, days=500, max_workers=5, use_cache=True):
    """Fetch data for all stocks in parallel with caching support"""
    
    # Check cache first
    if use_cache and is_cache_valid_lse(required_days=days):
        return load_from_cache_lse()
    
    print('[CACHE] Cache not available or expired, fetching from Yahoo Finance...')
    
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=days)
    print(f'Date range: {start_date} to {end_date}')
    
    skipped = []
    frames = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(fetch_one_yf, ticker, start_date, end_date): ticker
                     for ticker in stock_list}
        
        for future in concurrent.futures.as_completed(future_map):
            ticker = future_map[future]
            try:
                df = future.result()
                print(f'  [OK] {ticker:20s} {len(df)} rows')
                frames.append(df)
            except Exception as e:
                print(f'  [SKIP] {ticker:20s} {e}')
                skipped.append(ticker)
    
    if skipped:
        print(f'\nSkipped: {skipped}')
    
    if not frames:
        # If fetch failed and cache exists, fall back to cache
        if use_cache and os.path.exists(CACHE_FILE_LSE):
            print('\n[ERROR] Failed to fetch from Yahoo Finance')
            print('[CACHE] Falling back to cached data...\n')
            return load_from_cache_lse()
        raise ValueError('No data fetched')
    
    combined = pd.concat(frames, ignore_index=True)
    combined.sort_values(['symbol', 'date'], inplace=True)
    combined.reset_index(drop=True, inplace=True)
    print(f'[OK] Combined: {len(combined)} rows, {combined["symbol"].nunique()} stocks')
    
    # Save to cache
    if use_cache:
        save_to_cache_lse(combined)
    
    return combined, skipped

# Made with Bob