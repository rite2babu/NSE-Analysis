# NSE Stock Analysis — Specification

## Original Requirements

1. **Fetch Data** — current + last 1 year historical stock prices from NSE
   - 1.1 Use `nselib` library (`capital_market.price_volume_data`)
   - 1.2 Reference: `SMA-NSE-Check.ipynb` for nselib API usage
   - Input: configurable stock list array (119 NSE symbols)

2. **Compute Indicators**
   - 2.1 52W, 26W, 4W, 1W High and Low
   - 2.2 Golden Crossover: 200/20, 100/10, 50/5 day SMA pairs
   - 2.3 MACD (EMA 12/26/9)

3. **Reports**
   - 3.1 All stocks sorted ascending by 52W Hi/Low position
   - 3.2 Stocks in golden crossover (last 5 days) + stocks nearing crossover
   - 3.3 Stocks showing good MACD signals (score ≥ 2)
   - 3.5 Top 10 stocks trading near 52W High / Low

---

## Implemented — Current State

### Files
| File | Purpose |
|------|---------|
| `NSE_Analysis.py` | Standalone script (CLI) — fetches, computes, prints reports, saves CSV |
| `make_notebook.py` | Generates `NSE_Analysis.ipynb` from cell definitions |
| `NSE_Analysis.ipynb` | Jupyter notebook (run `make_notebook.py` to regenerate) |

### Stock List
119 NSE symbols (configurable in Section 1 of both `.py` files). Duplicate symbols removed.

### Fetch
- Parallel fetch using `ThreadPoolExecutor` (5 workers)
- Single shared `requests.Session` with NSE cookies (avoids per-call homepage hit)
- 365-day lookback

### Computed Indicators
| Indicator | Detail |
|-----------|--------|
| 52W / 26W / 4W / 1W Hi/Low | Rolling window high/low |
| 52W Position % | `(current - 52W_low) / (52W_high - 52W_low) * 100` |
| SMA Crossovers | 200/20, 100/10, 50/5 — golden cross + death cross detection |
| MACD Score (0–3) | Bullish cross (last 5d) + above zero + histogram increasing |

---

## Notebook Sections

| Section | Type | Description |
|---------|------|-------------|
| **1** | Config | Imports + STOCK_LIST (119 symbols) + parameters |
| **2** | Code | Helper functions: `compute_period_hl`, `compute_sma_crossovers`, `compute_macd` |
| **3** | Fetch | Parallel data fetch with shared NSE session |
| **4** | Compute | Combine DataFrames + compute all metrics |
| **5** | Table | Report 1 — All stocks sorted by 52W Position (heat-mapped Styler) |
| **6** | Table | Report 2 — Golden Crossover: crossed last 5d + nearing (within 1%) |
| **6b** | Chart | Cross-Over chart — two panels: ▲ Positive/Nearing vs ▼ Negative/Bearish; 1-year % change lines; crossover markers shown only for last 2 weeks |
| **7** | Table | Report 3 — MACD Signals (score ≥ 2), sorted by score |
| **7b** | Chart | MACD Overview — top 15 stocks: Score bar chart + Histogram bar chart (green=bullish, red=bearish) |
| **8** | Table | Report 4 — Top 10 near 52W High (≥80%) + Top 10 near 52W Low (≤20%) |
| **8b** | Chart | Horizontal bar chart — Top 10 near 52W High/Low |
| **8c** | Chart | Current Price vs 52W Range — top 15 (8 near-low + 7 near-high); x-axis = % position; labels show ₹ price + %; 52W low/high at bar ends |
| **8d** | Chart | 1-Year Price Trend for near-high & near-low stocks; split-adjusted % change; two panels |
| **9** | Chart | All Stocks 52W Position — `df.plot.barh`; red ≤20%, blue mid, green ≥80% |
| **10** | Save | All reports saved to `dump/NSE-ANALYSIS-{timestamp}.csv` |

---

## Chart Design Decisions
- All % change charts normalise from year start (base = first close price)
- Stock splits handled in 8d: single-day drops > 45% treated as split; prior prices scaled
- Section 8c x-axis is % position (0–100%), not ₹ price — makes all stocks comparable
- MACD chart (7b) limited to top 15 by score + histogram to avoid clutter
- 8c limited to top 15 (8 near-low + 7 near-high)
- Cross-over chart (6b) split into positive (golden/nearing) and negative (bearish) panels

---

## To Regenerate Notebook
```
python make_notebook.py