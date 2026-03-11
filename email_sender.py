"""
NSE Analysis - Email Sending Module
"""
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def df_to_html_table(df, title, color_column=None, color_map=None):
    """Convert DataFrame to HTML table with title and optional color coding"""
    html = f'<h3>{title}</h3>'
    
    if color_column and color_map and color_column in df.columns:
        # Manually create HTML table with row colors
        html += '<table border="1" style="border-collapse: collapse;">'
        
        # Header row
        html += '<thead><tr style="background-color: #f0f0f0;">'
        for col in df.columns:
            html += f'<th style="padding: 8px; text-align: left;">{col}</th>'
        html += '</tr></thead>'
        
        # Data rows with color coding
        html += '<tbody>'
        for _, row in df.iterrows():
            bg_color = color_map.get(row[color_column], '#ffffff')
            html += f'<tr style="background-color: {bg_color};">'
            for col in df.columns:
                html += f'<td style="padding: 8px;">{row[col]}</td>'
            html += '</tr>'
        html += '</tbody></table>'
    else:
        html += df.to_html(index=False, border=1)
    
    return html

def embed_chart(cid, title, width=900):
    """Create HTML for embedded chart"""
    return f'<h2>{title}</h2><img src="cid:{cid}" width="{width}"><br><br>'

def build_html_body(reports, chart_images):
    """Build HTML email body with tables and embedded charts"""
    sections = ['<html><body>', '<h1>NSE Stock Analysis Report</h1>']
    
    # Top losers chart - FIRST
    if 'top_losers' in chart_images:
        sections.append(embed_chart('top_losers', 'Top 10 Losers by Period'))
    
    # Top gainers chart - SECOND
    if 'top_gainers' in chart_images:
        sections.append(embed_chart('top_gainers', 'Top 10 Gainers by Period'))
    
    # Golden Cross table - THIRD (after top 2 charts)
    if 'golden_cross' in reports and not reports['golden_cross'].empty:
        sections.append('<div style="background-color: #d4edda; padding: 10px; margin: 10px 0;">')
        sections.append(df_to_html_table(reports['golden_cross'], '🟢 Golden Cross Signals (Last 10 Days)'))
        sections.append('</div>')
    
    # Death Cross table - FOURTH
    if 'death_cross' in reports and not reports['death_cross'].empty:
        sections.append('<div style="background-color: #f8d7da; padding: 10px; margin: 10px 0;">')
        sections.append(df_to_html_table(reports['death_cross'], '🔴 Death Cross Signals (Last 10 Days)'))
        sections.append('</div>')
    
    # Crossover line chart
    if 'crossover' in chart_images:
        sections.append(embed_chart('crossover', 'Cross-Over — 1 Year % Change'))
    
    # Crossover tables (original)
    if not reports['crossed'].empty:
        sections.append(df_to_html_table(reports['crossed'], 'Golden Crossover (last 5d)'))
    
    # MACD table with color coding
    if not reports['r3'].empty:
        # Create color map based on MACD_Score
        macd_color_map = {3: '#d4edda', 2: '#fff3cd'}  # Green for 3, Yellow for 2
        sections.append(df_to_html_table(
            reports['r3'],
            'MACD Signals (Score ≥ 2)',
            color_column='MACD_Score',
            color_map=macd_color_map
        ))
    if 'macd' in chart_images:
        sections.append(embed_chart('macd', 'MACD Overview — Top 15'))
    
    # Near High/Low tables and chart
    sections.append(df_to_html_table(reports['near_high'], 'Near 52W HIGH'))
    sections.append(df_to_html_table(reports['near_low'], 'Near 52W LOW'))
    if '52w_hl' in chart_images:
        sections.append(embed_chart('52w_hl', 'Near 52W High / Low'))
    
    # 52W Position summary
    sections.append(df_to_html_table(reports['r1'][['Symbol','Current_Price','52W_Position']].head(20),
                                     '52W Position (top 20)'))
    
    # 52W Range chart
    if '52w_range' in chart_images:
        sections.append(embed_chart('52w_range', 'Current Price vs 52W Range (Top 15)'))
    
    # Price trend chart
    if '52w_trend' in chart_images:
        sections.append(embed_chart('52w_trend', '1-Year Price Trend — Near 52W High & Low Stocks'))
    
    sections.append('</body></html>')
    return ''.join(sections)

def send_email(reports, chart_images, email_from, email_to, email_pass):
    """Assemble and send email with embedded charts"""
    print('\nPreparing email...')
    
    html_body = build_html_body(reports, chart_images)
    
    msg = MIMEMultipart('related')
    msg['Subject'] = f'NSE Analysis — {datetime.now().strftime("%d %b %Y")}'
    msg['From'] = email_from
    msg['To'] = email_to
    msg.attach(MIMEText(html_body, 'html'))
    
    for cid, img_bytes in chart_images.items():
        img = MIMEImage(img_bytes, 'png')
        img.add_header('Content-ID', f'<{cid}>')
        msg.attach(img)
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(email_from, email_pass)
            smtp.sendmail(email_from, email_to, msg.as_string())
        print(f'[OK] Email sent to {email_to} with {len(chart_images)} inline charts')
    except Exception as e:
        print(f'[ERROR] Failed to send email: {e}')

# Made with Bob
