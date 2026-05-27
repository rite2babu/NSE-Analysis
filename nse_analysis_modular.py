#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE Stock Analysis - Main Orchestrator
Modular version with separated concerns
"""

import sys
import io
import os
import logging
import pandas as pd
from datetime import datetime

# Suppress debug/info logs from matplotlib, PIL, kaleido, choreographer
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('kaleido').setLevel(logging.WARNING)
logging.getLogger('choreographer').setLevel(logging.WARNING)
logging.getLogger('browser_proc').setLevel(logging.WARNING)
logging.getLogger('root').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import modules
from config import (
    EMAIL_FROM, EMAIL_TO, EMAIL_PASS, MAX_WORKERS, DAYS, OUTPUT_DIR,
    BENCHMARK_SYMBOL, WEAKNESS_SCORE_THRESHOLD, TURNAROUND_SCORE_THRESHOLD, load_stock_list
)
from data_fetcher import fetch_all_data
from metrics import compute_all_metrics, create_crossover_summary_table, add_pattern_classification
from charts import generate_all_charts
from email_sender import send_email


def generate_reports(hl_df, cross_df, macd_df, returns_df, metrics_df):
    """Generate all analysis reports"""
    print('\n' + '=' * 80)
    print('ANALYSIS REPORTS')
    print('=' * 80)

    # Report 1: 52W Position
    print('\n[REPORT 1] 52W Hi/Low Position (Top 20)')
    r1 = hl_df[['Symbol', 'Current_Price', '52W_High', '52W_Low', '52W_Position']].sort_values('52W_Position')
    print(r1.head(20).to_string(index=False))

    # Report 2: Crossovers
    print('\n[REPORT 2] Golden Crossover Signals')
    crossed = pd.DataFrame()
    nearing = pd.DataFrame()

    if not cross_df.empty:
        crossed = cross_df[cross_df['crossed_last_5d'] == True][['Symbol', 'cross_type', 'cross_pct', 'last_cross_date']]
        if not crossed.empty:
            print('\n[OK] Crossed in last 5 days:')
            print(crossed.to_string(index=False))

        nearing = cross_df[cross_df['nearing'] == True][['Symbol', 'cross_type', 'cross_pct']]
        if not nearing.empty:
            print('\n[OK] Nearing crossover:')
            print(nearing.to_string(index=False))
    else:
        print('  (no crossover data)')

    # Report 3: MACD
    print('\n[REPORT 3] MACD Signals (Score >= 2)')
    r3 = macd_df[macd_df['MACD_Score'] >= 2].sort_values('MACD_Score', ascending=False)
    r3_display = pd.DataFrame()

    if not r3.empty:
        r3_display = r3[['Symbol', 'MACD', 'Signal', 'Histogram', 'MACD_Score']]
        print(r3_display.to_string(index=False))
    else:
        print('  (no stocks with MACD score >= 2)')

    # Report 4: Near 52W High/Low
    print('\n[REPORT 4] Near 52W High / Low')
    near_high = hl_df[hl_df['52W_Position'] >= 80].sort_values('52W_Position', ascending=False).head(10)
    near_low = hl_df[hl_df['52W_Position'] <= 20].sort_values('52W_Position').head(10)

    if not near_high.empty:
        print('\n[OK] Near 52W HIGH (>=80%):')
        print(near_high[['Symbol', 'Current_Price', '52W_Position']].to_string(index=False))

    if not near_low.empty:
        print('\n[OK] Near 52W LOW (<=20%):')
        print(near_low[['Symbol', 'Current_Price', '52W_Position']].to_string(index=False))

    # Report 5: Top Gainers/Losers
    print('\n[REPORT 5] Top Movers (1 Month)')
    gainers = returns_df[returns_df['1M_%'] > 0].nlargest(10, '1M_%')[['Symbol', 'Current_Price', '1M_%']]
    losers = returns_df[returns_df['1M_%'] < 0].nsmallest(10, '1M_%')[['Symbol', 'Current_Price', '1M_%']]

    if not gainers.empty:
        print('\n[+] TOP 10 GAINERS (1M):')
        print(gainers.to_string(index=False))

    if not losers.empty:
        print('\n[-] TOP 10 LOSERS (1M):')
        print(losers.to_string(index=False))

    # Report 6: Long-term weak stocks
    print(f'\n[REPORT 6] Long-Term Weak Stocks (Weakness Score <= {WEAKNESS_SCORE_THRESHOLD})')
    weak_cols = [
        'Symbol', '3M_%', '6M_%', '1Y_%', 'RS_3M_%', 'RS_6M_%', 'RS_1Y_%',
        'Close_vs_EMA200_%', 'RSI_14_Weekly', 'Drawdown_From_52W_High_%', 'Weakness_Score'
    ]
    long_term_weak = metrics_df[metrics_df['Weakness_Score'] <= WEAKNESS_SCORE_THRESHOLD].sort_values(
        ['Weakness_Score', 'RS_1Y_%', '1Y_%']
    )[weak_cols].head(20)
    if not long_term_weak.empty:
        print(long_term_weak.to_string(index=False))
    else:
        print('  (no stocks met the long-term weakness threshold)')

    # Report 7: Turnaround watchlist
    print(f'\n[REPORT 7] Early Turnaround Watchlist (Turnaround Score >= {TURNAROUND_SCORE_THRESHOLD})')
    turnaround_cols = [
        'Symbol', '3M_%', 'RS_3M_%', 'Close_vs_EMA50_%', 'Close_vs_EMA200_%',
        'RSI_14_Daily', 'RSI_14_Weekly', 'RSI_Weekly_Trend',
        'No_New_Low_20D', 'Breakout_20D', 'Volume_Ratio_20D', 'Turnaround_Score'
    ]
    turnaround_watch = metrics_df[metrics_df['Turnaround_Score'] >= TURNAROUND_SCORE_THRESHOLD].sort_values(
        ['Turnaround_Score', 'RS_3M_%', 'RSI_Weekly_Trend'],
        ascending=[False, False, False]
    )[turnaround_cols].head(20)
    if not turnaround_watch.empty:
        print(turnaround_watch.to_string(index=False))
    else:
        print('  (no stocks met the turnaround threshold)')

    return {
        'r1': r1,
        'crossed': crossed if not cross_df.empty else pd.DataFrame(),
        'nearing': nearing if not cross_df.empty else pd.DataFrame(),
        'r3': r3_display if not r3.empty else pd.DataFrame(),
        'near_high': near_high,
        'near_low': near_low,
        'long_term_weak': long_term_weak,
        'turnaround_watch': turnaround_watch,
    }


def create_returns_csv(returns_df, metrics_df):
    """Create CSV file with all stock returns across all periods and new ranking metrics"""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = f"{OUTPUT_DIR}/STOCK-RETURNS-{timestamp}.csv"

    score_cols = [
        'Symbol', 'Close_vs_EMA50_%', 'Close_vs_EMA200_%',
        'RSI_14_Daily', 'RSI_14_Weekly', 'Drawdown_From_52W_High_%', 'Weakness_Score', 'Turnaround_Score',
        'Pattern_Name', 'Pattern_Meaning', 'Pattern_Explanation'
    ]
    returns_export = returns_df.merge(
        metrics_df[score_cols].drop_duplicates(subset=['Symbol']),
        on='Symbol',
        how='left'
    )

    export_cols = [
        'Symbol', 'Current_Price', '1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%',
        'RS_3M_%', 'RS_6M_%', 'RS_1Y_%', 'Close_vs_EMA50_%', 'Close_vs_EMA200_%',
        'RSI_14_Daily', 'RSI_14_Weekly', 'Drawdown_From_52W_High_%', 'Weakness_Score', 'Turnaround_Score',
        'Pattern_Name', 'Pattern_Meaning', 'Pattern_Explanation'
    ]
    returns_export = returns_export[export_cols].copy().sort_values(['Weakness_Score', 'Turnaround_Score', 'Symbol'])

    returns_export.to_csv(csv_path, index=False)
    print(f'[OK] Returns CSV saved to: {csv_path}')

    return csv_path


def save_to_csv(reports, skipped):
    """Save all reports to CSV"""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = f"{OUTPUT_DIR}/NSE-ANALYSIS-{timestamp}.csv"

    csv_sections = [
        pd.DataFrame([['=== REPORT 1: 52W Hi/Low Position ===']]), reports['r1'], pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 2A: Crossed Last 5 Days ===']]),
        reports['crossed'] if not reports['crossed'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 2B: Nearing Crossover ===']]),
        reports['nearing'] if not reports['nearing'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 3: MACD Signals ===']]),
        reports['r3'] if not reports['r3'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 4A: Near 52W HIGH ===']]),
        reports['near_high'] if not reports['near_high'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 4B: Near 52W LOW ===']]),
        reports['near_low'] if not reports['near_low'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 6: Long-Term Weak Stocks ===']]),
        reports['long_term_weak'] if not reports['long_term_weak'].empty else pd.DataFrame([['(none)']]),
        pd.DataFrame([[]]),
        pd.DataFrame([['=== REPORT 7: Early Turnaround Watchlist ===']]),
        reports['turnaround_watch'] if not reports['turnaround_watch'].empty else pd.DataFrame([['(none)']]),
    ]

    with open(out_path, 'w', newline='') as f:
        for section in csv_sections:
            section.to_csv(f, index=False, header=True)
            f.write('\n')

    print(f'\n[OK] Reports saved to: {out_path}')
    if skipped:
        print(f'[WARNING] Skipped stocks: {skipped}')


def main():
    """Main execution function"""
    print('=' * 80)
    print('NSE STOCK ANALYSIS (Modular Version)')
    print('=' * 80)

    stock_list = load_stock_list()
    combined, skipped = fetch_all_data(stock_list, days=DAYS, max_workers=MAX_WORKERS)

    hl_df, cross_df, macd_df, returns_df, metrics_df = compute_all_metrics(combined, benchmark_symbol=BENCHMARK_SYMBOL)
    
    # Add pattern classification
    metrics_df = add_pattern_classification(metrics_df)

    reports = generate_reports(hl_df, cross_df, macd_df, returns_df, metrics_df)

    crossover_summary = create_crossover_summary_table(cross_df, combined)
    if not crossover_summary.empty:
        golden_cross = crossover_summary[crossover_summary['Type'] == 'Golden Cross'].drop('Type', axis=1)
        death_cross = crossover_summary[crossover_summary['Type'] == 'Death Cross'].drop('Type', axis=1)

        print('\n[REPORT 8A] Golden Cross Summary (Last 10 Days)')
        if not golden_cross.empty:
            print(golden_cross.to_string(index=False))
        else:
            print('  (none)')

        print('\n[REPORT 8B] Death Cross Summary (Last 10 Days)')
        if not death_cross.empty:
            print(death_cross.to_string(index=False))
        else:
            print('  (none)')

        reports['golden_cross'] = golden_cross
        reports['death_cross'] = death_cross
    else:
        reports['golden_cross'] = pd.DataFrame()
        reports['death_cross'] = pd.DataFrame()

    chart_images = generate_all_charts(reports, hl_df, macd_df, cross_df, returns_df, combined)

    returns_csv_path = create_returns_csv(returns_df, metrics_df)

    send_email(reports, chart_images, EMAIL_FROM, EMAIL_TO, EMAIL_PASS, returns_csv_path)

    save_to_csv(reports, skipped)

    print('\n' + '=' * 80)
    print('[OK] ANALYSIS COMPLETE')
    print('=' * 80)


if __name__ == '__main__':
    main()

# Made with Bob