import json

# Read the notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find and fix the problematic cell in build_html_body function
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Check if this is the build_html_body function with the issue
        if 'def build_html_body' in source and "if 'macd' in chart_images:" in source:
            print("Found problematic email cell, fixing...")
            
            # Fix the missing line after "if 'macd' in chart_images:"
            fixed_source = source.replace(
                "    if 'macd' in chart_images:\n    if 'macd_heatmap' in chart_images:",
                "    if 'macd' in chart_images:\n        sections.append(embed_chart('macd', 'MACD Overview — Top 15'))\n    if 'macd_heatmap' in chart_images:"
            )
            
            # Also fix the duplicate line issue
            fixed_source = fixed_source.replace(
                "        sections.append(embed_chart('macd_heatmap', 'MACD Signals Heatmap'))\n        sections.append(embed_chart('macd', 'MACD Overview — Top 15'))",
                "        sections.append(embed_chart('macd_heatmap', 'MACD Signals Heatmap'))"
            )
            
            # Fix the top_losers section
            fixed_source = fixed_source.replace(
                "    if 'top_losers' in chart_images:\n    \n    # 1W losers treemap\n    if '1w_losers_treemap' in chart_images:\n        sections.append(embed_chart('1w_losers_treemap', '📉 Top 15 Losers — 1 Week (5D) Treemap'))\n        sections.append(embed_chart('top_losers', '🔴 Top 10 Losers by Period'))",
                "    if 'top_losers' in chart_images:\n        sections.append(embed_chart('top_losers', '🔴 Top 10 Losers by Period'))\n    \n    # 1W losers treemap\n    if '1w_losers_treemap' in chart_images:\n        sections.append(embed_chart('1w_losers_treemap', '📉 Top 15 Losers — 1 Week (5D) Treemap'))"
            )
            
            # Update the cell source
            cell['source'] = fixed_source.split('\n')
            # Add newlines back
            cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line 
                            for i, line in enumerate(cell['source'])]
            
            print("Fixed!")
            break

# Write the fixed notebook
with open('NSE_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Email section fixed successfully!")

# Made with Bob
