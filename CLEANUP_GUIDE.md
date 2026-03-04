# Project Cleanup Guide

## Files to Keep (Essential)

### Core Analysis Files
- `NSE_Analysis.py` - Main analysis script
- `NSE_Analysis.ipynb` - Notebook with email functionality
- `make_notebook.py` - Converts .py to .ipynb

### Configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Git exclusions
- `.gitattributes` - Git attributes
- `GITHUB_ACTIONS_SETUP.md` - Setup instructions
- `NSE_Analysis_SPEC.md` - Specification document

### GitHub Actions
- `.github/workflows/daily-nse-analysis.yml` - Automation workflow

### Data Files (Optional)
- `nse_equity_list.csv` - Stock list
- `indices.json` - Index data
- `stk.json` - Stock data
- `dump/` - Analysis results (keep folder, ignore contents)

## Files to Delete (Old/Test Files)

### Test/Experimental Files
```powershell
# Delete these files
Remove-Item Play.ipynb, Play.py
Remove-Item "NSE - 1.ipynb", "NSE - 1.py"
Remove-Item scrape_nse_new.ipynb, scrape-nse.ipynb
Remove-Item stock-price-fetch.ipynb
Remove-Item "Test-NSE Scrap.py"
Remove-Item TestBSE.ipynb, TestBSE.py
Remove-Item Untitled*.ipynb, Untitled*.py, Untitled*.txt
Remove-Item xirr.ipynb, xirr.py
Remove-Item "SMA-Test-Copy1.ipynb", "SMA-Test-Copy1.py"
Remove-Item "stk-mf-Returns calculation.ipynb", "stk-mf-Returns calculation.py"
Remove-Item test.html, file.csv
Remove-Item git
```

### Old SMA Files (Keep or Delete?)
**Keep if still using:**
- `SMA-LSEG-Y.ipynb`, `SMA-LSEG-Y.py`
- `SMA-NSE-Check.ipynb`, `SMA-NSE-Check.py`
- `SMA-NSE-Check2.ipynb`, `SMA-NSE-Check2.py`
- `SMA-NSE-Check-aws.py`

**Delete if replaced by NSE_Analysis:**
```powershell
Remove-Item SMA-*.ipynb, SMA-*.py
```

### Supporting Files (Keep or Delete?)
**Keep if still using:**
- `Stock_Analysis.ipynb`, `Stock_Analysis.py`
- `nse_scrap.py`

**Delete if not needed:**
```powershell
Remove-Item Stock_Analysis.ipynb, Stock_Analysis.py
Remove-Item nse_scrap.py
Remove-Item NSE_Analysis_GitHub.ipynb  # Duplicate, not needed
```

## Cleanup Commands

### Option 1: Delete All Test Files
```powershell
# Navigate to project
cd C:\Projects\bobs_code\NSE

# Delete test files
Remove-Item Play.*, "NSE - 1.*", scrape*.ipynb, stock-price-fetch.ipynb, `
  "Test*.py", Test*.ipynb, Untitled*.*, xirr.*, "SMA-Test*.*", `
  "stk-mf-Returns*.*", test.html, file.csv, git, NSE_Analysis_GitHub.ipynb

# Commit cleanup
git add .
git commit --no-gpg-sign -m "Clean up test and old files"
git push origin main
```

### Option 2: Keep Only Essential Files
```powershell
# Create new clean directory
mkdir C:\Projects\bobs_code\NSE-Analysis-Clean

# Copy essential files
Copy-Item NSE_Analysis.py, NSE_Analysis.ipynb, make_notebook.py, `
  requirements.txt, .gitignore, .gitattributes, `
  GITHUB_ACTIONS_SETUP.md, NSE_Analysis_SPEC.md, `
  nse_equity_list.csv, indices.json, stk.json `
  -Destination C:\Projects\bobs_code\NSE-Analysis-Clean\

# Copy .github folder
Copy-Item .github -Recurse -Destination C:\Projects\bobs_code\NSE-Analysis-Clean\

# Create dump folder
mkdir C:\Projects\bobs_code\NSE-Analysis-Clean\dump
```

## Rename Folder to Match Repo

### Current Structure
```
C:\Projects\bobs_code\NSE\  (local folder)
github.com/rite2babu/NSE-Analysis  (repo name)
```

### Rename Steps
```powershell
# Close VS Code first

# Rename folder
cd C:\Projects\bobs_code\
Rename-Item NSE NSE-Analysis

# Update git remote (if needed)
cd NSE-Analysis
git remote -v  # Check current remote

# If remote is correct, you're done
# If not, update it:
git remote set-url origin https://github.com/rite2babu/NSE-Analysis.git
```

## Final Clean Structure

```
NSE-Analysis/
├── .github/
│   └── workflows/
│       └── daily-nse-analysis.yml
├── dump/                          # Analysis results
├── .gitignore
├── .gitattributes
├── GITHUB_ACTIONS_SETUP.md
├── NSE_Analysis_SPEC.md
├── make_notebook.py
├── NSE_Analysis.py
├── NSE_Analysis.ipynb
├── requirements.txt
├── nse_equity_list.csv
├── indices.json
└── stk.json
```

## Recommendation

**Yes, rename folder to match repo name** for consistency:
- Easier to identify
- Matches GitHub repo
- Professional structure

**Delete test files** - they're not needed and clutter the project.