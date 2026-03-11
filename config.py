"""
NSE Analysis - Configuration
"""
import os

# Email configuration
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'peri47.study@gmail.com')
EMAIL_TO = os.environ.get('EMAIL_TO', 'peri47.study@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'fhih lsqp wanu leic')

# Analysis configuration
MAX_WORKERS = 5
DAYS = 365
OUTPUT_DIR = 'dump'
CACHE_DIR = 'cache'
CACHE_FILE = 'cache/nse_data_cache.csv'
CACHE_EXPIRY_HOURS = 6  # Cache expires after 6 hours

def load_stock_list(filename='stocks.txt'):
    """Load stock list from file"""
    with open(filename, 'r') as f:
        stock_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f'[OK] Loaded {len(stock_list)} stocks from {filename}')
    return stock_list

# Made with Bob
