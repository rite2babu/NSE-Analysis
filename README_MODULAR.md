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

### 1. **config.py** (22 lines)
- Email configuration (from environment variables)
- Analysis parameters (workers, days, output directory)
- Stock list loader function

### 2. **data_fetcher.py** (95 lines)
- NSE session initialization
- Parallel data fetching with ThreadPoolExecutor
- Data cleaning and formatting
- Returns combined DataFrame and skipped stocks list

### 3. **metrics.py** (197 lines)
- `compute_period_hl()` - 52-week high/low positions
- `compute_sma_crossovers()` - SMA crossover signals
- `compute_macd()` - MACD indicators and scoring
- `compute_period_returns()` - Multi-period returns (1D, 2D, 5D, 10D, 1M, 3M, 6M, 1Y)
- `compute_all_metrics()` - Orchestrates all metric calculations

### 4. **charts.py** (344 lines)
- Matplotlib charts: 52W position, MACD, near high/low, crossovers, price trends, 52W range
- **Plotly charts**: Top gainers/losers (horizontal bars with labels inside)
- `generate_all_charts()` - Creates all charts and returns bytes dictionary

### 5. **email_sender.py** (93 lines)
- HTML email body builder
- Chart embedding with Content-ID references
- SMTP email sending with inline images

### 6. **nse_analysis_modular.py** (175 lines)
- Main orchestrator
- Report generation and console output
- CSV export functionality
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

### Reports Generated
1. 52W Hi/Low Position (all stocks)
2. Golden Crossover Signals (crossed + nearing)
3. MACD Signals (score ≥ 2)
4. Near 52W High/Low (top 10 each)
5. Top Movers (1 Month gainers/losers)

### Charts Generated
1. **52W Position** - All stocks bar chart
2. **MACD Overview** - Score + histogram (top 15)
3. **Near High/Low** - Horizontal bars
4. **Crossovers** - Positive/negative trend panels
5. **52W Range** - Current price vs range (top 15)
6. **Price Trends** - 1-year trends for near high/low
7. **Top Gainers** - Horizontal grouped bars (Plotly) ✨
8. **Top Losers** - Horizontal grouped bars (Plotly) ✨

### Email Report
- HTML formatted with embedded charts
- All tables and visualizations included
- Sent via Gmail SMTP

### CSV Export
- Timestamped file in `dump/` directory
- All reports in structured format

## Recent Updates

### Plotly Charts (Gainers/Losers)
- ✅ Horizontal orientation for better readability
- ✅ Thicker bars with improved spacing
- ✅ Symbol and percentage labels inside bars
- ✅ Added 1D period alongside existing periods
- ✅ Color-coded: Green gradient (gainers), Red gradient (losers)
- ✅ High-resolution PNG export (1200x600, scale=2)

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