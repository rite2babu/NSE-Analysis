# Stock Analysis System - Technical Specification

## Project Overview

Dual-market stock analysis system providing automated technical analysis, reporting, and email notifications for NSE and LSE/US markets.

## System Architecture

### Core Components

| Component | Purpose | Lines |
|-----------|---------|-------|
| `nse_analysis_modular.py` | NSE orchestrator | 212 |
| `lse_analysis.py` | LSE orchestrator | 222 |
| `data_fetcher.py` | NSE data via nselib | 163 |
| `data_fetcher_lse.py` | LSE/US data via yfinance | 158 |
| `metrics.py` | Technical indicators and composite scoring | 487 |
| `charts.py` | Visualization (matplotlib/plotly) | 727 |
| `email_sender.py` | SMTP email with attachments | 93 |
| `config.py` | NSE configuration | 30 |
| `config_lse.py` | LSE configuration | 36 |

## Data Sources

### NSE Market
- **Library**: nselib
- **Stocks**: 119+ symbols from `stocks.txt`
- **Cache**: `cache/nse_data_cache.csv` (6h expiry)
- **Output**: `dump/NSE-ANALYSIS-*.csv`

### LSE/US Market
- **Library**: yfinance
- **Stocks**: Symbols from `stocks_lse.txt`
- **Cache**: `cache/lse/lse_data_cache.csv` (6h expiry)
- **Output**: `dump/lse/LSE-ANALYSIS-*.csv`

## Technical Indicators

### 52-Week Position
```text
Position = ((Current - 52W_Low) / (52W_High - 52W_Low)) × 100
```
- Range: 0-100%
- Near High: ≥80%
- Near Low: ≤20%

### Drawdown / Distance Metrics
```text
Dist_From_52W_High_% = ((Current - 52W_High) / 52W_High) × 100
Dist_From_52W_Low_%  = ((Current - 52W_Low) / 52W_Low) × 100
```

### SMA Crossovers
| Type | Fast SMA | Slow SMA | Signal |
|------|----------|----------|--------|
| Golden Cross | 200 | 20 | Bullish |
| Golden Cross | 100 | 10 | Bullish |
| Golden Cross | 50 | 5 | Bullish |
| Death Cross | 200 | 20 | Bearish |
| Death Cross | 100 | 10 | Bearish |
| Death Cross | 50 | 5 | Bearish |

**Detection**:
- Crossed: Last 5 days
- Nearing: Within 2% of crossover

### MACD (12, 26, 9)
```text
MACD = EMA(12) - EMA(26)
Signal = EMA(MACD, 9)
Histogram = MACD - Signal
```

**Scoring** (0-3):
- +1: Bullish cross in last 5 days
- +1: MACD > 0
- +1: Histogram increasing for last 3 values

### Period Returns
| Period | Trading Days | Column |
|--------|--------------|--------|
| 1 Day | 1 | `1D_%` |
| 2 Days | 2 | `2D_%` |
| 5 Days | 5 | `5D_%` |
| 10 Days | 10 | `10D_%` |
| 1 Month | 21 | `1M_%` |
| 3 Months | 63 | `3M_%` |
| 6 Months | 126 | `6M_%` |
| 1 Year | 252 | `1Y_%` |

### Relative Strength vs Benchmark
```text
RS_3M_% = Stock_3M_% - Benchmark_3M_%
RS_6M_% = Stock_6M_% - Benchmark_6M_%
RS_1Y_% = Stock_1Y_% - Benchmark_1Y_%
```

### EMA Structure
```text
EMA50  = Exponential moving average of close over 50 periods
EMA200 = Exponential moving average of close over 200 periods
Close_vs_EMA50_%  = ((Close - EMA50) / EMA50) × 100
Close_vs_EMA200_% = ((Close - EMA200) / EMA200) × 100
```

### RSI Regime
- `RSI_14_Daily`
- `RSI_14_Weekly`
- `RSI_Daily_Trend`
- `RSI_Weekly_Trend`

### ADX / Directional Indicators
- `ADX_14`
- `Plus_DI_14`
- `Minus_DI_14`

### Turnaround Signals
- `No_New_Low_20D`
- `Range_Contraction_20D_%`
- `Breakout_20D`
- `Volume_Ratio_20D`

### Weakness Score
Composite negative score for long-term laggards.

**Components**:
- RS 1Y negative: -3
- RS 6M negative: -2
- 3M return negative: -1
- Close below EMA200: -2
- EMA50 below EMA200: -2
- Weekly RSI below 50: -1
- Drawdown from 52W high worse than -25%: -1
- ADX > 20 and Minus_DI > Plus_DI: -1

### Turnaround Score
Composite positive score for stabilising / improving weak stocks.

**Components**:
- RS 3M positive: +2
- No new 20D low: +1
- Close above EMA50: +2
- Daily RSI above 50: +1
- Weekly RSI trend positive: +1
- Breakout 20D: +2
- Volume ratio > 1.2: +1
- Close above EMA200: +2

## Reports Generated

### Report 1: 52W Position
All stocks sorted by position (low to high)

### Report 2: Crossover Signals
- **2A**: Crossed in last 5 days
- **2B**: Nearing crossover (within 2%)

### Report 3: MACD Signals
Stocks with MACD score ≥ 2

### Report 4: Near Extremes
- **4A**: Near 52W High (≥80%)
- **4B**: Near 52W Low (≤20%)

### Report 5: Top Movers
- Top 10 gainers (1M)
- Top 10 losers (1M)

### Report 6: Long-Term Weak Stocks
Columns include returns, relative strength, EMA200 distance, weekly RSI, drawdown, and weakness score

### Report 7: Early Turnaround Watchlist
Columns include RS improvement, EMA repair, RSI recovery, new-low check, breakout status, volume ratio, and turnaround score

### Report 8: Crossover Summary
- **8A**: Golden Cross (last 10 days)
- **8B**: Death Cross (last 10 days)

## Visualizations

### Matplotlib Charts
1. **52W Position**: Bar chart (all stocks)
2. **MACD Overview**: Score + histogram (top 15)
3. **Near High/Low**: Horizontal bars
4. **Crossovers**: Positive/negative panels
5. **52W Range**: Current vs range (top 15)
6. **Price Trends**: 1-year trends

### Plotly Charts
7. **Top Gainers**: Horizontal grouped bars
8. **Top Losers**: Horizontal grouped bars

## Email Delivery

### Configuration
```python
EMAIL_FROM = os.environ.get('EMAIL_FROM')
EMAIL_TO = os.environ.get('EMAIL_TO')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
```

### Content
- HTML formatted body
- Embedded charts (Content-ID)
- CSV attachment (all returns plus weakness/turnaround columns)
- Subject: "NSE Stock Analysis" or "LSE/US Stock Analysis"

### SMTP
- Server: smtp.gmail.com:587
- TLS: Enabled
- Auth: App password required

## Performance

### Parallel Processing
- **Workers**: 5 concurrent threads
- **Fetch Time**: ~2-3 min for 119 stocks
- **Total Runtime**: ~3-5 min (including analysis)

### Caching
- **Duration**: 6 hours
- **Purpose**: Reduce API calls
- **Format**: CSV with timestamp

## Data Flow

```text
Stock List → Data Fetcher → Cache Check → API Fetch
                                ↓
                          Combined DataFrame
                                ↓
                          Metrics Computation
                                ↓
                    ┌───────────┴───────────┐
                    ↓                       ↓
              Report Generation      Chart Generation
                    ↓                       ↓
                    └───────────┬───────────┘
                                ↓
                          Email Sender
                                ↓
                          CSV Export
```

## File Structure

```text
NSE/
├── nse_analysis_modular.py    # NSE orchestrator
├── lse_analysis.py            # LSE orchestrator
├── config.py                  # NSE config
├── config_lse.py              # LSE config
├── data_fetcher.py            # NSE data
├── data_fetcher_lse.py        # LSE data
├── metrics.py                 # Indicators and scoring
├── charts.py                  # Visualizations
├── email_sender.py            # Email
├── stocks.txt                 # NSE symbols
├── stocks_lse.txt             # LSE/US symbols
├── requirements.txt           # Dependencies
├── cache/                     # Data cache
│   ├── nse_data_cache.csv
│   └── lse/
│       └── lse_data_cache.csv
├── dump/                      # NSE outputs
│   ├── NSE-ANALYSIS-*.csv
│   └── STOCK-RETURNS-*.csv
└── dump/lse/                  # LSE outputs
    ├── LSE-ANALYSIS-*.csv
    └── LSE-STOCK-RETURNS-*.csv
```

## Environment Variables

```bash
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@gmail.com
EMAIL_PASS=your-app-password
BENCHMARK_SYMBOL=NIFTY 50
BENCHMARK_SYMBOL_LSE=^FTSE
WEAKNESS_SCORE_THRESHOLD=-8
TURNAROUND_SCORE_THRESHOLD=5
MAX_WORKERS=5
DAYS=370
```

## Maintenance

### Adding Stocks
1. Edit `stocks.txt` or `stocks_lse.txt`
2. Add symbol (one per line or row)
3. Comments supported in `stocks.txt`

### Modifying Indicators
- Edit `metrics.py` for calculations
- Update `charts.py` for visualizations
- Adjust thresholds in orchestrator/config files

## Future Enhancements

- [ ] Benchmark auto-fetch inside data layer
- [ ] Weakness / turnaround charts
- [ ] Portfolio tracking
- [ ] Backtesting framework
- [ ] Machine learning predictions
- [ ] Sector rotation analysis

## Version History

- **v2.1**: Added relative strength, EMA structure, RSI/ADX, weakness score, turnaround score
- **v2.0**: Dual-market support (NSE + LSE/US)
- **v1.5**: Plotly charts with enhanced styling
- **v1.0**: Modular architecture refactor
- **v0.1**: Initial monolithic version

---

*Last Updated: 2026-05-26*
*Made with Bob*