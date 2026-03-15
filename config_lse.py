"""
LSE/US Stock Analysis - Configuration
"""
import os

# Email configuration
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'peri47.study@gmail.com')
EMAIL_TO = os.environ.get('EMAIL_TO', 'peri47.study@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'fhih lsqp wanu leic')

# Analysis configuration
MAX_WORKERS = 5
DAYS = 500
OUTPUT_DIR_LSE = 'dump/lse'
CACHE_DIR_LSE = 'cache/lse'
CACHE_FILE_LSE = 'cache/lse/lse_data_cache.csv'
CACHE_EXPIRY_HOURS = 6  # Cache expires after 6 hours

# Currency symbol for display
CURRENCY_SYMBOL = '£'  # Default to GBP for LSE, but will show $ for US stocks

def load_stock_list_lse(filename='stocks_lse.txt'):
    """Load stock list from file"""
    with open(filename, 'r') as f:
        stock_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f'[OK] Loaded {len(stock_list)} stocks from {filename}')
    return stock_list

# Made with Bob