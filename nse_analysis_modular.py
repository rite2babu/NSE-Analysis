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
from config import EMAIL_FROM, EMAIL_TO, EMAIL_PASS, MAX_WORKERS, DAYS, OUTPUT_DIR, load_stock_list
from data_fetcher import fetch_all_data
from metrics import compute_all_metrics
from charts import generate_all_charts, create_crossover_summary_table
from email_sender import send_email

def generate_reports(hl_df, cross_df, macd_df, returns_df):
    """Generate all analysis reports"""
    print('\n' + '='*80)
    print('ANALYSIS REPORTS')
    print('='*80)
    
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
    
    return {
        'r1': r1,
        'crossed': crossed if not cross_df.empty else pd.DataFrame(),
        'nearing': nearing if not cross_df.empty else pd.DataFrame(),
        'r3': r3_display if not r3.empty else pd.DataFrame(),
        'near_high': near_high,
        'near_low': near_low
    }

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
    print('='*80)
    print('NSE STOCK ANALYSIS (Modular Version)')
    print('='*80)
    
    # Load configuration
    stock_list = load_stock_list()
    
    # Fetch data
    combined, skipped = fetch_all_data(stock_list, days=DAYS, max_workers=MAX_WORKERS)
    
    # Compute metrics
    hl_df, cross_df, macd_df, returns_df = compute_all_metrics(combined)
    
    # Generate reports
    reports = generate_reports(hl_df, cross_df, macd_df, returns_df)
    
    # Generate crossover summary tables (split by type)
    crossover_summary = create_crossover_summary_table(cross_df, combined)
    if not crossover_summary.empty:
        golden_cross = crossover_summary[crossover_summary['Type'] == 'Golden Cross'].drop('Type', axis=1)
        death_cross = crossover_summary[crossover_summary['Type'] == 'Death Cross'].drop('Type', axis=1)
        
        print('\n[REPORT 6A] Golden Cross Summary (Last 10 Days)')
        if not golden_cross.empty:
            print(golden_cross.to_string(index=False))
        else:
            print('  (none)')
        
        print('\n[REPORT 6B] Death Cross Summary (Last 10 Days)')
        if not death_cross.empty:
            print(death_cross.to_string(index=False))
        else:
            print('  (none)')
        
        reports['golden_cross'] = golden_cross
        reports['death_cross'] = death_cross
    else:
        reports['golden_cross'] = pd.DataFrame()
        reports['death_cross'] = pd.DataFrame()
    
    # Generate charts
    chart_images = generate_all_charts(reports, hl_df, macd_df, cross_df, returns_df, combined)
    
    # Send email
    send_email(reports, chart_images, EMAIL_FROM, EMAIL_TO, EMAIL_PASS)
    
    # Save results
    save_to_csv(reports, skipped)
    
    print('\n' + '='*80)
    print('[OK] ANALYSIS COMPLETE')
    print('='*80)

if __name__ == '__main__':
    main()

# Made with Bob