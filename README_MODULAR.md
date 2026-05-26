# NSE Stock Analysis - Modular Version

## Overview
The NSE analysis system has been refactored into a modular architecture for better maintainability and organization.

## File Structure

```
NSE/
├── nse_analysis_modular.py    # Main orchestrator script
├── config.py                  # Configuration and constants
├── data_fetcher.py           # Data fetching logic
├── metrics.py                # Metric calculation functions
├── charts.py                 # Chart generation (matplotlib + plotly)
├── email_sender.py           # Email functionality
├── stocks.txt                # Stock list (input)
└── dump/                     # Output directory for CSV reports
```

## Module Descriptions

### 1. **config.py**
- Email configuration (from environment variables)
- Analysis parameters (workers, days, output directory)
- Benchmark symbol and score thresholds
- Stock list loader function

### 2. **data_fetcher.py**
- NSE session initialization
- Parallel data fetching with ThreadPoolExecutor
- Data cleaning and formatting
- Returns combined DataFrame and skipped stocks list

### 3. **metrics.py**
- [`compute_period_hl()`](metrics.py:9) - 52-week high/low positions plus drawdown from highs
- [`compute_sma_crossovers()`](metrics.py:37) - SMA crossover signals
- [`compute_macd()`](metrics.py:72) - MACD indicators and scoring
- [`compute_period_returns()`](metrics.py:105) - Multi-period returns (1D, 2D, 5D, 10D, 1M, 3M, 6M, 1Y)
- [`compute_ema_structure()`](metrics.py:137) - EMA50/EMA200 structure and distance metrics
- [`compute_rsi()`](metrics.py:164) - Daily and weekly RSI regime
- [`compute_adx()`](metrics.py:197) - ADX and directional movement
- [`compute_turnaround_signals()`](metrics.py:235) - Stabilisation and breakout checks
- [`compute_relative_strength()`](metrics.py:276) - Relative strength vs benchmark returns
- [`compute_composite_scores()`](metrics.py:289) - Weakness and turnaround scoring
- [`compute_all_metrics()`](metrics.py:336) - Orchestrates all metric calculations

### 4. **charts.py**
- Matplotlib charts: 52W position, MACD, near high/low, crossovers, price trends, 52W range
- Plotly charts: Top gainers/losers
- [`generate_all_charts()`](charts.py:676) - Creates all charts and returns bytes dictionary

### 5. **email_sender.py**
- HTML email body builder
- Chart embedding with Content-ID references
- SMTP email sending with inline images

### 6. **nse_analysis_modular.py**
- Main orchestrator
- Report generation and console output
- CSV export functionality
- Long-term weak-stock and turnaround watchlist reports
- Coordinates all modules

## Usage

### Run Analysis
```bash
python nse_analysis_modular.py
```

### Environment Variables (Optional)
```bash
export EMAIL_FROM="your-email@gmail.com"
export EMAIL_TO="recipient@gmail.com"
export EMAIL_PASS="your-app-password"
export BENCHMARK_SYMBOL="NIFTY 50"
export WEAKNESS_SCORE_THRESHOLD="-8"
export TURNAROUND_SCORE_THRESHOLD="5"
```

## Features

### Data Analysis
- Fetches 1-year OHLCV data for 119+ NSE stocks
- Parallel fetching with 5 workers
- Automatic retry and error handling

### Metrics Computed
- 52-week high/low positions
- SMA crossovers (200/20, 100/10, 50/5)
- MACD signals with scoring (0-3)
- Period returns: 1D, 2D, 5D, 10D, 1M, 3M, 6M, 1Y
- Relative strength vs benchmark on 3M, 6M, and 1Y
- EMA50 / EMA200 structure and slope
- Daily / weekly RSI regime
- ADX / DI trend strength
- Drawdown from 52-week high
- Weakness and turnaround composite scores

### Reports Generated
1. 52W Hi/Low Position (all stocks)
2. Golden Crossover Signals (crossed + nearing)
3. MACD Signals (score ≥ 2)
4. Near 52W High/Low (top 10 each)
5. Top Movers (1 Month gainers/losers)
6. Long-Term Weak Stocks
7. Early Turnaround Watchlist
8. Crossover Summary

### Charts Generated
1. **52W Position** - All stocks bar chart
2. **MACD Overview** - Score + histogram (top 15)
3. **Near High/Low** - Horizontal bars
4. **Crossovers** - Positive/negative trend panels
5. **52W Range** - Current price vs range (top 15)
6. **Price Trends** - 1-year trends for near high/low
7. **Top Gainers** - Horizontal grouped bars (Plotly)
8. **Top Losers** - Horizontal grouped bars (Plotly)

### Email Report
- HTML formatted with embedded charts
- All tables and visualizations included
- Sent via Gmail SMTP

### CSV Export
- Timestamped file in `dump/` directory
- Returns CSV now includes relative strength, EMA structure, RSI, drawdown, weakness score, and turnaround score

## Benefits of Modular Structure

1. **Maintainability** - Each module has a single responsibility
2. **Testability** - Individual modules can be tested independently
3. **Reusability** - Functions can be imported and used elsewhere
4. **Readability** - Smaller files are easier to understand
5. **Scalability** - Easy to add new features or modify existing ones

## Dependencies

```
pandas
numpy
matplotlib
plotly
nselib
requests
```

## Original Version

The original monolithic version (`nse_analysis.py` - 1001 lines) is still available for reference.