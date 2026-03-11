import json

# Read the notebook
with open('NSE_Analysis.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find and fix the problematic cell
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Check if this is the problematic create_price_trend_chart function
        if 'def create_price_trend_chart' in source and 'def create_1w_losers_treemap' in source:
            print("Found problematic cell, fixing...")
            
            # Fix the indentation issue
            fixed_source = source.replace(
                '            ax.plot(grp.index, pct, linewidth=1.2, label=sym, alpha=0.85)\n\n\n\n\ndef create_1w_losers_treemap',
                '            ax.plot(grp.index, pct, linewidth=1.2, label=sym, alpha=0.85)\n        ax.axhline(0, color=\'grey\', linewidth=0.7, linestyle=\'--\', alpha=0.5)\n        ax.set_title(title, fontsize=10, color=color, fontweight=\'bold\')\n        ax.set_ylabel(\'% Change\', fontsize=8)\n        ax.xaxis.set_major_formatter(mdates.DateFormatter(\'%b\'))\n        ax.legend(fontsize=6.5, loc=\'upper left\', ncol=2)\n        ax.grid(axis=\'y\', alpha=0.3)\n    \n    plt.tight_layout()\n    return fig\n\ndef create_1w_losers_treemap'
            )
            
            # Remove the duplicate lines at the end
            fixed_source = fixed_source.replace(
                '    return fig\n\n        ax.axhline(0, color=\'grey\', linewidth=0.7, linestyle=\'--\', alpha=0.5)\n        ax.set_title(title, fontsize=10, color=color, fontweight=\'bold\')\n        ax.set_ylabel(\'% Change\', fontsize=8)\n        ax.xaxis.set_major_formatter(mdates.DateFormatter(\'%b\'))\n        ax.legend(fontsize=6.5, loc=\'upper left\', ncol=2)\n        ax.grid(axis=\'y\', alpha=0.3)\n    \n    plt.tight_layout()\n    return fig',
                '    return fig'
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

print("Notebook fixed successfully!")

# Made with Bob
