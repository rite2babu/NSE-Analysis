"""
NSE Analysis - Data Fetching Module
"""
import os
import pandas as pd
import datetime as dt
import time
import requests
import concurrent.futures
from nselib import capital_market
import nselib.capital_market.capital_market_data as _cm_data
from config import CACHE_DIR, CACHE_FILE, CACHE_EXPIRY_HOURS

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

def is_cache_valid(required_days=365):
    """Check if cache exists, is not expired, contains today's data, and has sufficient historical data"""
    if not os.path.exists(CACHE_FILE):
        return False
    
    # Check file age
    cache_time = dt.datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    age_hours = (dt.datetime.now() - cache_time).total_seconds() / 3600
    
    if age_hours >= CACHE_EXPIRY_HOURS:
        return False
    
    # Check if cache contains today's data and has sufficient historical range
    try:
        cache_df = pd.read_csv(CACHE_FILE)
        cache_df['date'] = pd.to_datetime(cache_df['date'])
        latest_cache_date = cache_df['date'].max().date()
        earliest_cache_date = cache_df['date'].min().date()
        today = dt.date.today()
        
        if latest_cache_date < today:
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

def load_from_cache():
    """Load data from cache file"""
    print(f'[CACHE] Loading data from {CACHE_FILE}')
    combined = pd.read_csv(CACHE_FILE)
    combined['date'] = pd.to_datetime(combined['date'])
    
    cache_time = dt.datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    age_hours = (dt.datetime.now() - cache_time).total_seconds() / 3600
    print(f'[CACHE] Data age: {age_hours:.1f} hours')
    print(f'[OK] Loaded: {len(combined)} rows, {combined["symbol"].nunique()} stocks from cache')
    
    return combined, []

def save_to_cache(combined):
    """Save data to cache file"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    combined.to_csv(CACHE_FILE, index=False)
    print(f'[CACHE] Saved data to {CACHE_FILE}')

def fetch_all_data(stock_list, days=365, max_workers=5, use_cache=True):
    """Fetch data for all stocks in parallel with caching support"""
    
    # Check cache first
    if use_cache and is_cache_valid(required_days=days):
        return load_from_cache()
    
    print('[CACHE] Cache not available or expired, fetching from NSE...')
    
    end_date = dt.date.today().strftime('%d-%m-%Y')
    start_date = (dt.date.today() - dt.timedelta(days=days)).strftime('%d-%m-%Y')
    print(f'Date range: {start_date} to {end_date}')
    
    init_session()
    
    skipped = []
    frames = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(fetch_one, sym, start_date, end_date): sym
                     for sym in stock_list}
        
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
        # If NSE fetch failed and cache exists, fall back to cache
        if use_cache and os.path.exists(CACHE_FILE):
            print('\n[ERROR] Failed to fetch from NSE')
            print('[CACHE] Falling back to cached data...\n')
            return load_from_cache()
        raise ValueError('No data fetched')
    
    combined = pd.concat(frames, ignore_index=True)
    combined.sort_values(['symbol', 'date'], inplace=True)
    combined.reset_index(drop=True, inplace=True)
    print(f'[OK] Combined: {len(combined)} rows, {combined["symbol"].nunique()} stocks')
    
    # Save to cache
    if use_cache:
        save_to_cache(combined)
    
    return combined, skipped

# Made with Bob
