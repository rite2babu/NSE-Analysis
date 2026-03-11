# NSE Analysis Changes Applied

## Change 1: Enlarge Top 10 Losers/Gainers bars by 100%, scrip names inside, percentages outside
- Line 625: Changed figsize from (14, 10) to (28, 20)
- Line 629: Changed height from 0.08 to 0.16
- Lines 653-661: Modified text placement - symbol inside bar, percentage outside
- Lines 665-673: Increased font sizes (12→24, 14→28, 11→22)
- Line 701: Changed figsize from (14, 10) to (28, 20)
- Line 705: Changed height from 0.08 to 0.16
- Lines 729-737: Modified text placement - symbol inside bar, percentage outside
- Lines 741-749: Increased font sizes (12→24, 14→28, 11→22)

## Change 2: Export All stock returns by period to CSV
- Already implemented at line 2705-2707 (returns_table.csv)
- Section 4g (Plotly interactive table) can be removed/commented as CSV export exists

## Change 3: Add 1D period to both charts/data
- Line 431: Updated docstring to include 1d
- Line 467-485: Added '1D_%': round(calc_return(1), 2) as first return period
- Line 565-569: Added '1D_%' to periods list and period_names dict
- Line 605-607: Added '1D_%' and '1D' to periods and period_labels
- Line 765-785: Added '1D_%' to summary_cols and formatting

## Change 4: Add NIFTY50 to stocks.txt
- ✓ Already completed - NIFTY50 added to stocks.txt at line 6

## Change 5: Convert MACD signal table to heatmap and include in email
- Need to create heatmap visualization for MACD signals
- Include in email generation section

## Change 6: Remove "Near 52W High / Low" chart (Section 8b)
- Keep Section 8 (tables)
- Remove Section 8b chart code (lines 1386-1471)
- Keep Section 8c (Current Price vs 52W Range)
- Update email generation to exclude 52w_hl chart

## Change 7: Add treemap/squarify chart for top 1W losers
- Need to add squarify library
- Create new section for 1W losers treemap
- Include in email generation