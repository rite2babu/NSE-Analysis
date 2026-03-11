"""
NSE Analysis - Chart Generation Module
"""
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import plotly.graph_objects as go

def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    return buf.read()

def create_52w_position_chart(r1):
    """Create 52W position bar chart for all stocks"""
    plot_df = r1[['Symbol', '52W_Position']].set_index('Symbol').sort_values('52W_Position')
    colors = ['#e74c3c' if v <= 20 else '#2ecc71' if v >= 80 else '#3498db' for v in plot_df['52W_Position']]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_df.plot.barh(ax=ax, color=colors, legend=False)
    ax.set_xlabel('52W Position %')
    ax.set_title('All Stocks — 52-Week Position', fontsize=12)
    ax.axvline(20, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.6)
    ax.axvline(80, color='#2ecc71', linestyle='--', linewidth=1, alpha=0.6)
    plt.tight_layout()
    return fig

def create_macd_chart(macd_df):
    """Create MACD score and histogram charts"""
    m2 = macd_df[['Symbol', 'MACD', 'Signal', 'Histogram', 'MACD_Score']].copy()
    m2 = m2.sort_values(['MACD_Score', 'Histogram'], ascending=True).tail(15).set_index('Symbol')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('MACD Overview — Top 15', fontsize=13, fontweight='bold')
    
    sc = {0: '#e74c3c', 1: '#e67e22', 2: '#3498db', 3: '#2ecc71'}
    m2[['MACD_Score']].plot.barh(ax=axes[0], color=[sc.get(int(v), '#95a5a6') for v in m2['MACD_Score']], legend=False)
    axes[0].set_title('MACD Score')
    
    m2[['Histogram']].plot.barh(ax=axes[1], color=['#2ecc71' if v >= 0 else '#e74c3c' for v in m2['Histogram']], legend=False)
    axes[1].set_title('MACD Histogram')
    plt.tight_layout()
    return fig

def create_near_hl_chart(near_high, near_low):
    """Create near 52W high/low horizontal bar charts"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle('Near 52W High / Low', fontsize=14, fontweight='bold')
    
    if not near_high.empty:
        nh = near_high.copy().sort_values('52W_Position')
        nh.set_index('Symbol')[['52W_Position']].plot.barh(ax=axes[0], color='#2ecc71', legend=False)
        axes[0].set_title('Near 52W HIGH')
    
    if not near_low.empty:
        nl = near_low.copy().sort_values('52W_Position', ascending=False)
        nl.set_index('Symbol')[['52W_Position']].plot.barh(ax=axes[1], color='#e74c3c', legend=False)
        axes[1].set_title('Near 52W LOW')
    
    plt.tight_layout()
    return fig

def create_top_gainers_chart(returns_df):
    """Create horizontal bar chart for top gainers across periods using Plotly"""
    periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
    period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']
    
    # Color palette for different stocks
    color_palette = [
        '#2ecc71', '#27ae60', '#16a085', '#1abc9c', '#3498db',
        '#2980b9', '#9b59b6', '#8e44ad', '#e74c3c', '#c0392b'
    ]
    
    fig = go.Figure()
    
    # Build Y-axis with normalized bars
    y_positions = []
    y_labels = []
    x_values = []
    colors = []
    text_labels = []
    actual_values = []
    period_midpoints = []
    period_names = []
    
    position = 0
    # Show 1D, 2D, 5D first (ascending order)
    for period, label in zip(periods, period_labels):
        gainers = returns_df[returns_df[period] > 0].nlargest(10, period)[['Symbol', period]]
        
        if not gainers.empty:
            # Get max value for this period to normalize
            max_val = gainers[period].max()
            
            start_pos = position
            for idx, (_, row) in enumerate(gainers.iterrows()):
                # Each stock gets unique numeric position
                y_positions.append(position)
                y_labels.append("")  # Empty label for individual bars
                # Normalize to 100 (max value = 100)
                normalized = (row[period] / max_val) * 100 if max_val > 0 else 0
                x_values.append(normalized)
                actual_values.append(row[period])
                # Assign color based on stock position (0-9)
                colors.append(color_palette[idx % len(color_palette)])
                # Show symbol and ACTUAL percentage inside bar
                text_labels.append(f"{row['Symbol']}: {row[period]:.1f}%")
                position += 1
            
            # Store midpoint for period label
            end_pos = position - 1
            period_midpoints.append((start_pos + end_pos) / 2)
            period_names.append(label)
            
            # Add spacing between periods
            position += 2
    
    # Create single trace with all bars
    fig.add_trace(go.Bar(
        x=x_values,
        y=y_positions,
        orientation='h',
        text=text_labels,
        textposition='inside',
        textfont=dict(size=9, color='white', family='Arial Black'),
        marker=dict(
            color=colors,
            line=dict(width=0.5, color='white')
        ),
        hovertemplate='<b>%{text}</b><extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(
            text='Top 10 Gainers by Period (Normalized Scale)',
            font=dict(size=16, family='Arial Black')
        ),
        xaxis_title='Relative Performance (100 = Top Gainer in Period)',
        yaxis_title='',
        height=2800,
        width=1200,
        plot_bgcolor='white',
        yaxis=dict(
            tickmode='array',
            tickvals=period_midpoints,
            ticktext=period_names,
            tickfont=dict(size=12, family='Arial Black'),
            autorange='reversed'
        ),
        xaxis=dict(
            tickfont=dict(size=11),
            range=[0, 105]
        ),
        margin=dict(l=60, r=40, t=80, b=60)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=False)
    
    # Convert to image bytes
    img_bytes = fig.to_image(format='png', width=1200, height=2800, scale=2)
    return img_bytes

def create_top_losers_chart(returns_df):
    """Create horizontal bar chart for top losers across periods using Plotly"""
    periods = ['1D_%', '2D_%', '5D_%', '10D_%', '1M_%', '3M_%', '6M_%', '1Y_%']
    period_labels = ['1D', '2D', '5D', '10D', '1M', '3M', '6M', '1Y']
    
    # Color palette for different stocks (red shades)
    color_palette = [
        '#e74c3c', '#c0392b', '#e67e22', '#d35400', '#f39c12',
        '#f1c40f', '#e8b923', '#d68910', '#ca6f1e', '#ba4a00'
    ]
    
    fig = go.Figure()
    
    # Build Y-axis with normalized bars
    y_positions = []
    y_labels = []
    x_values = []
    colors = []
    text_labels = []
    actual_values = []
    period_midpoints = []
    period_names = []
    
    position = 0
    # Show 1D, 2D, 5D first (ascending order)
    for period, label in zip(periods, period_labels):
        losers = returns_df[returns_df[period] < 0].nsmallest(10, period)[['Symbol', period]]
        
        if not losers.empty:
            # Get min value (most negative) for this period to normalize
            min_val = losers[period].min()
            
            start_pos = position
            for idx, (_, row) in enumerate(losers.iterrows()):
                # Each stock gets unique numeric position
                y_positions.append(position)
                y_labels.append("")  # Empty label for individual bars
                # Normalize to -100 (worst loser = -100)
                # Since values are negative, we need to keep them negative
                normalized = (row[period] / abs(min_val)) * 100 if min_val < 0 else 0
                x_values.append(normalized)
                actual_values.append(row[period])
                # Assign color based on stock position (0-9)
                colors.append(color_palette[idx % len(color_palette)])
                # Show symbol and ACTUAL percentage inside bar
                text_labels.append(f"{row['Symbol']}: {row[period]:.1f}%")
                position += 1
            
            # Store midpoint for period label
            end_pos = position - 1
            period_midpoints.append((start_pos + end_pos) / 2)
            period_names.append(label)
            
            # Add spacing between periods
            position += 2
    
    # Create single trace with all bars
    fig.add_trace(go.Bar(
        x=x_values,
        y=y_positions,
        orientation='h',
        text=text_labels,
        textposition='inside',
        textfont=dict(size=9, color='white', family='Arial Black'),
        marker=dict(
            color=colors,
            line=dict(width=0.5, color='white')
        ),
        hovertemplate='<b>%{text}</b><extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(
            text='Top 10 Losers by Period (Normalized Scale)',
            font=dict(size=16, family='Arial Black')
        ),
        xaxis_title='Relative Performance (-100 = Worst Loser in Period)',
        yaxis_title='',
        height=2800,
        width=1200,
        plot_bgcolor='white',
        yaxis=dict(
            tickmode='array',
            tickvals=period_midpoints,
            ticktext=period_names,
            tickfont=dict(size=12, family='Arial Black'),
            autorange='reversed'
        ),
        xaxis=dict(
            tickfont=dict(size=11),
            range=[-105, 0]
        ),
        margin=dict(l=60, r=40, t=80, b=60)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=False)
    
    # Convert to image bytes
    img_bytes = fig.to_image(format='png', width=1200, height=2800, scale=2)
    return img_bytes

def create_crossover_chart(cross_df, combined):
    """Create crossover trend chart with positive/negative panels"""
    colors_line = ['#2980b9','#e67e22','#8e44ad','#27ae60','#c0392b',
                   '#16a085','#d35400','#2c3e50','#7f8c8d','#1abc9c',
                   '#f39c12','#8e44ad','#1abc9c','#e74c3c','#3498db']
    
    pos_syms, neg_syms = set(), set()
    if not cross_df.empty:
        pos_syms.update(cross_df[cross_df['crossed_last_5d'] == True]['Symbol'].tolist())
        pos_syms.update(cross_df[cross_df['nearing'] == True]['Symbol'].tolist())
        neg_mask = (cross_df['cross_pct'] < -1.0)
        neg_syms.update(cross_df[neg_mask]['Symbol'].tolist())
        neg_syms -= pos_syms
    
    def plot_panel(ax, syms, title, panel_color):
        if not syms:
            ax.text(0.5, 0.5, 'None', ha='center', va='center', transform=ax.transAxes, fontsize=10)
            ax.set_title(title, fontsize=10, color=panel_color, fontweight='bold')
            return
        for i, sym in enumerate(sorted(syms)):
            grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
            base = grp['close'].iloc[0]
            pct = (grp['close'] / base - 1) * 100
            col = colors_line[i % len(colors_line)]
            ax.plot(grp.index, pct, color=col, linewidth=1.2, alpha=0.85, label=sym)
        ax.axhline(0, color='grey', linewidth=0.7, linestyle='--', alpha=0.5)
        ax.set_title(title, fontsize=10, color=panel_color, fontweight='bold')
        ax.set_ylabel('% Change', fontsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.legend(fontsize=6.5, loc='upper left', ncol=2)
        ax.grid(axis='y', alpha=0.3)
    
    if pos_syms or neg_syms:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Cross-Over — 1 Year % Change', fontsize=12, fontweight='bold')
        plot_panel(axes[0], pos_syms, '▲ Positive / Nearing', '#27ae60')
        plot_panel(axes[1], neg_syms, '▼ Negative / Bearish', '#c0392b')
        plt.tight_layout()
        return fig
    return None

def create_52w_range_chart(hl_df):
    """Create current price vs 52W range chart"""
    hl_all = hl_df[['Symbol', 'Current_Price', '52W_High', '52W_Low', '52W_Position']].dropna(subset=['52W_Position'])
    hl_sorted = hl_all.sort_values('52W_Position')
    hl = pd.concat([hl_sorted.head(8), hl_sorted.tail(7)]).reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    for i, row in hl.iterrows():
        lo, hi, cur, sym, pos = row['52W_Low'], row['52W_High'], row['Current_Price'], row['Symbol'], row['52W_Position']
        color = '#e74c3c' if pos <= 20 else '#2ecc71' if pos >= 80 else '#3498db'
        
        ax.barh(i, 100, left=0, height=0.5, color='#ecf0f1', edgecolor='#bdc3c7', linewidth=0.5)
        ax.barh(i, pos, left=0, height=0.5, color=color, alpha=0.55)
        ax.scatter(pos, i, color=color, s=90, zorder=5, edgecolors='white', linewidths=0.8)
        ax.text(-1, i, sym, ha='right', va='center', fontsize=8.5, fontweight='bold')
        ax.text(pos, i + 0.33, f'£{cur:,.0f}  ({pos:.1f}%)', ha='center', fontsize=7.5, color=color, fontweight='bold')
        ax.text(0, i - 0.35, f'£{lo:,.0f}', ha='left', fontsize=6.5, color='#7f8c8d')
        ax.text(100, i - 0.35, f'£{hi:,.0f}', ha='right', fontsize=6.5, color='#7f8c8d')
    
    ax.set_xlim(-2, 108)
    ax.set_yticks([])
    ax.set_xlabel('52W Position %  (0% = 52W Low  →  100% = 52W High)')
    ax.axvline(20, color='#e74c3c', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.axvline(80, color='#2ecc71', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.axvline(50, color='grey', linestyle=':', linewidth=0.8, alpha=0.4)
    ax.set_title('Current Price vs 52W Range', fontsize=11, fontweight='bold')
    ax.grid(axis='x', alpha=0.2)
    plt.tight_layout()
    return fig

def create_price_trend_chart(near_high, near_low, combined):
    """Create 1-year price trend chart for near high/low stocks"""
    def split_adjusted_pct(grp, split_threshold=0.45):
        close = grp['close'].copy()
        daily_ret = close.pct_change()
        split_days = daily_ret[daily_ret < -split_threshold].index
        for sd in split_days:
            ratio = close.loc[sd] / close.shift(1).loc[sd]
            close.loc[close.index < sd] *= ratio
        base = close.iloc[0]
        return (close / base - 1) * 100
    
    near_syms_high = near_high['Symbol'].tolist() if not near_high.empty else []
    near_syms_low = near_low['Symbol'].tolist() if not near_low.empty else []
    
    if not (near_syms_high or near_syms_low):
        return None
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('1-Year Price Trend — Near 52W High & Low Stocks', fontsize=12, fontweight='bold')
    
    for ax, syms, title, color in [
        (axes[0], near_syms_high, 'Near 52W HIGH', '#27ae60'),
        (axes[1], near_syms_low, 'Near 52W LOW', '#c0392b'),
    ]:
        if not syms:
            ax.text(0.5, 0.5, 'None', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontsize=10, color=color, fontweight='bold')
            continue
        for sym in syms:
            grp = combined[combined['symbol'] == sym].sort_values('date').set_index('date')
            pct = split_adjusted_pct(grp)
            ax.plot(grp.index, pct, linewidth=1.2, label=sym, alpha=0.85)
        ax.axhline(0, color='grey', linewidth=0.7, linestyle='--', alpha=0.5)
        ax.set_title(title, fontsize=10, color=color, fontweight='bold')
        ax.set_ylabel('% Change', fontsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.legend(fontsize=6.5, loc='upper left', ncol=2)
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_crossover_summary_table(cross_df, combined):
    """Create summary table of crossover status (crossed, crossing, will cross) - last 10 days only"""
    if cross_df.empty:
        return pd.DataFrame()
    
    summary_rows = []
    
    for _, row in cross_df.iterrows():
        symbol = row['Symbol']
        cross_type = row['cross_type']
        cross_pct = row['cross_pct']
        crossed_last_5d = row['crossed_last_5d']
        last_cross_date = row.get('last_cross_date', None)
        nearing = row['nearing']
        
        # Determine if Golden Cross (bullish) or Death Cross (bearish)
        if crossed_last_5d or cross_pct >= -1.0:
            cross_direction = 'Golden Cross'
        else:
            cross_direction = 'Death Cross'
        
        # Determine status and calculate days ago if crossed
        days_ago_text = ''
        if crossed_last_5d and last_cross_date:
            # Calculate days ago from last_cross_date
            from datetime import datetime
            try:
                cross_date = pd.to_datetime(last_cross_date)
                today = pd.Timestamp.now()
                days_ago = (today - cross_date).days
                if days_ago <= 10:  # Only include if within last 10 days
                    status = 'Crossed'
                    days_ago_text = f'{days_ago}d ago'
                else:
                    continue  # Skip if crossed more than 10 days ago
            except:
                status = 'Crossed'
                days_ago_text = 'Recent'
        elif nearing:
            status = 'Crossing Soon'
            days_ago_text = f'{abs(cross_pct):.2f}% away'
        elif -2.0 <= cross_pct < -1.0:
            status = 'Will Cross'
            days_ago_text = f'{abs(cross_pct):.2f}% away'
        else:
            continue  # Skip others
        
        # Get recent price data for context
        stock_data = combined[combined['symbol'] == symbol].sort_values('date')
        if not stock_data.empty:
            recent_close = stock_data['close'].iloc[-1]
            days_10_ago_close = stock_data['close'].iloc[-11] if len(stock_data) >= 11 else stock_data['close'].iloc[0]
            pct_change_10d = ((recent_close - days_10_ago_close) / days_10_ago_close * 100) if days_10_ago_close > 0 else 0
        else:
            pct_change_10d = 0
        
        summary_rows.append({
            'Symbol': symbol,
            'Type': cross_direction,
            'Cross': cross_type,
            'Status': status,
            'Cross %': f'{cross_pct:.2f}%',
            '10D Chg': f'{pct_change_10d:.1f}%',
            'When': days_ago_text
        })
    
    if not summary_rows:
        return pd.DataFrame()
    
    summary_df = pd.DataFrame(summary_rows)
    
    # Sort by Cross Type (50/5, 100/10, 200/20), then by Status, then by Cross %
    cross_type_order = {'50/5': 1, '100/10': 2, '200/20': 3}
    status_order = {'Crossed': 1, 'Crossing Soon': 2, 'Will Cross': 3}
    summary_df['_cross_sort'] = summary_df['Cross'].map(cross_type_order)
    summary_df['_status_sort'] = summary_df['Status'].map(status_order)
    summary_df = summary_df.sort_values(['_cross_sort', '_status_sort', 'Cross %']).drop(['_cross_sort', '_status_sort'], axis=1)
    
    return summary_df

def create_crossover_heatmap(cross_df, returns_df):
    """Create heatmap showing crossover signals for stocks with activity"""
    if cross_df.empty:
        return None
    
    # Filter to only stocks with crossover activity (crossed, crossing, or will cross)
    active_stocks = cross_df[
        (cross_df['crossed_last_5d'] == True) |
        (cross_df['nearing'] == True) |
        (cross_df['cross_pct'] >= -2.0)
    ]['Symbol'].unique()
    
    if len(active_stocks) == 0:
        return None
    
    # Pivot crossover data: rows=stocks, columns=cross_types
    pivot_data = cross_df[cross_df['Symbol'].isin(active_stocks)].pivot_table(
        index='Symbol',
        columns='cross_type',
        values='cross_pct',
        aggfunc='first'
    )
    
    # Reorder columns: 50/5, 100/10, 200/20
    col_order = ['50/5', '100/10', '200/20']
    pivot_data = pivot_data[[c for c in col_order if c in pivot_data.columns]]
    
    # Sort by most active (closest to crossing)
    # Calculate average cross_pct across all timeframes (higher = closer to crossing)
    pivot_data['_avg_cross'] = pivot_data[col_order].mean(axis=1, skipna=True)
    pivot_data = pivot_data.sort_values('_avg_cross', ascending=False).drop('_avg_cross', axis=1)
    
    # Take top 25 most active stocks
    pivot_data = pivot_data.head(25)
    
    # Create color mapping: green for positive (crossed), red for negative (far from crossing)
    fig = go.Figure()
    
    # Prepare data for heatmap
    z_values = []
    hover_texts = []
    
    for col in pivot_data.columns:
        col_values = []
        col_hover = []
        for idx, val in pivot_data[col].items():
            if pd.isna(val):
                col_values.append(0)
                col_hover.append(f"{idx}<br>{col}: N/A")
            else:
                col_values.append(val)
                if col == '1M_%':
                    col_hover.append(f"{idx}<br>{col}: {val:.1f}%")
                else:
                    col_hover.append(f"{idx}<br>{col}: {val:.2f}%")
        z_values.append(col_values)
        hover_texts.append(col_hover)
    
    # Transpose for proper orientation
    z_values = list(map(list, zip(*z_values)))
    hover_texts = list(map(list, zip(*hover_texts)))
    
    # Create text annotations showing the percentage values and status
    text_display = []
    for col_idx, col in enumerate(pivot_data.columns):
        col_text = []
        for row_idx, (idx, val) in enumerate(pivot_data[col].items()):
            if pd.isna(val):
                col_text.append('')
            else:
                # Add status indicator
                if val > 0:
                    status = '✓'  # Crossed
                elif val >= -1.0:
                    status = '⚠'  # Crossing Soon
                elif val >= -2.0:
                    status = '→'  # Will Cross
                else:
                    status = ''
                col_text.append(f'{status} {val:.2f}%')
        text_display.append(col_text)
    
    # Transpose for proper orientation
    text_display = list(map(list, zip(*text_display)))
    
    fig.add_trace(go.Heatmap(
        z=z_values,
        x=pivot_data.columns.tolist(),
        y=pivot_data.index.tolist(),
        colorscale=[
            [0.0, '#c0392b'],   # Deep red for very negative
            [0.4, '#e74c3c'],   # Red
            [0.48, '#f39c12'],  # Orange
            [0.5, '#f1c40f'],   # Yellow (near zero)
            [0.52, '#2ecc71'],  # Light green
            [0.6, '#27ae60'],   # Green
            [1.0, '#16a085']    # Deep green for very positive
        ],
        text=text_display,
        texttemplate='%{text}',
        textfont=dict(size=10, color='white', family='Arial Black'),
        hovertext=hover_texts,
        hovertemplate='%{hovertext}<extra></extra>',
        colorbar=dict(
            title=dict(text='Cross %', side='right'),
            tickmode='linear',
            tick0=-10,
            dtick=5
        )
    ))
    
    fig.update_layout(
        title=dict(
            text='Golden Crossover Heatmap (Stocks with Activity)',
            font=dict(size=16, family='Arial Black')
        ),
        xaxis_title='Crossover Type / 1M Return',
        yaxis_title='Stock Symbol',
        height=1000,
        width=1000,
        plot_bgcolor='white',
        xaxis=dict(
            tickfont=dict(size=11, family='Arial Black'),
            side='top'
        ),
        yaxis=dict(
            tickfont=dict(size=10, family='Arial'),
            autorange='reversed'
        )
    )
    
    # Convert to image bytes
    img_bytes = fig.to_image(format='png', width=1000, height=800, scale=2)
    return img_bytes

def create_macd_heatmap(macd_df, returns_df):
    """Create heatmap showing MACD indicators across stocks"""
    if macd_df.empty:
        return None
    
    # Select relevant MACD columns
    macd_subset = macd_df[['Symbol', 'MACD', 'Signal', 'Histogram', 'MACD_Score']].copy()
    macd_subset = macd_subset.set_index('Symbol')
    
    # Add 1M return for context
    if not returns_df.empty:
        returns_1m = returns_df.set_index('Symbol')[['1M_%']]
        macd_subset = macd_subset.join(returns_1m, how='left')
    
    # Sort by MACD_Score (descending), then Histogram
    macd_subset = macd_subset.sort_values(['MACD_Score', 'Histogram'], ascending=[False, False])
    
    # Take top 20 stocks
    macd_subset = macd_subset.head(20)
    
    # Create heatmap
    fig = go.Figure()
    
    # Prepare data
    z_values = []
    hover_texts = []
    
    for col in macd_subset.columns:
        col_values = []
        col_hover = []
        for idx, val in macd_subset[col].items():
            if pd.isna(val):
                col_values.append(0)
                col_hover.append(f"{idx}<br>{col}: N/A")
            else:
                col_values.append(val)
                if col == 'MACD_Score':
                    col_hover.append(f"{idx}<br>{col}: {int(val)}")
                elif col == '1M_%':
                    col_hover.append(f"{idx}<br>{col}: {val:.1f}%")
                else:
                    col_hover.append(f"{idx}<br>{col}: {val:.2f}")
        z_values.append(col_values)
        hover_texts.append(col_hover)
    
    # Transpose
    z_values = list(map(list, zip(*z_values)))
    hover_texts = list(map(list, zip(*hover_texts)))
    
    fig.add_trace(go.Heatmap(
        z=z_values,
        x=macd_subset.columns.tolist(),
        y=macd_subset.index.tolist(),
        colorscale=[
            [0.0, '#c0392b'],   # Red for negative
            [0.4, '#e74c3c'],
            [0.48, '#f39c12'],
            [0.5, '#f1c40f'],   # Yellow for neutral
            [0.52, '#2ecc71'],
            [0.6, '#27ae60'],
            [1.0, '#16a085']    # Green for positive
        ],
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        colorbar=dict(
            title=dict(text='Value', side='right')
        )
    ))
    
    fig.update_layout(
        title=dict(
            text='MACD Indicators Heatmap (Top 20 by Score)',
            font=dict(size=16, family='Arial Black')
        ),
        xaxis_title='MACD Indicator',
        yaxis_title='Stock Symbol',
        height=800,
        width=1200,
        plot_bgcolor='white',
        xaxis=dict(
            tickfont=dict(size=11, family='Arial Black'),
            side='top'
        ),
        yaxis=dict(
            tickfont=dict(size=10, family='Arial'),
            autorange='reversed'
        )
    )
    
    # Convert to image bytes
    img_bytes = fig.to_image(format='png', width=1200, height=800, scale=2)
    return img_bytes

def generate_all_charts(reports, hl_df, macd_df, cross_df, returns_df, combined):
    """Generate all charts and return as bytes dictionary"""
    print('\nGenerating charts...')
    chart_images = {}
    
    # 52W position chart
    fig = create_52w_position_chart(reports['r1'])
    chart_images['52w_position'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # MACD chart
    fig = create_macd_chart(macd_df)
    chart_images['macd'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # Near high/low chart
    fig = create_near_hl_chart(reports['near_high'], reports['near_low'])
    chart_images['52w_hl'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # Crossover chart
    fig = create_crossover_chart(cross_df, combined)
    if fig:
        chart_images['crossover'] = fig_to_bytes(fig)
        plt.close(fig)
    
    # 52W range chart
    fig = create_52w_range_chart(hl_df)
    chart_images['52w_range'] = fig_to_bytes(fig)
    plt.close(fig)
    
    # Price trend chart
    fig = create_price_trend_chart(reports['near_high'], reports['near_low'], combined)
    if fig:
        chart_images['52w_trend'] = fig_to_bytes(fig)
        plt.close(fig)
    
    # Top gainers chart (Plotly - returns bytes directly)
    print('  - Generating top gainers chart...')
    chart_images['top_gainers'] = create_top_gainers_chart(returns_df)
    print(f'    ✓ Top gainers chart: {len(chart_images["top_gainers"])} bytes')
    
    # Top losers chart (Plotly - returns bytes directly)
    print('  - Generating top losers chart...')
    chart_images['top_losers'] = create_top_losers_chart(returns_df)
    print(f'    ✓ Top losers chart: {len(chart_images["top_losers"])} bytes')
    
    print(f'[OK] Generated {len(chart_images)} charts')
    print(f'    Chart keys: {list(chart_images.keys())}')
    return chart_images

# Made with Bob
