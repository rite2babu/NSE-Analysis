# GitHub Actions Setup Guide

## Overview
The NSE Analysis project is configured to run automatically via GitHub Actions twice daily during market hours.

## Schedule
- **9:30 AM IST (4:00 AM UTC)** - Market opening analysis (Monday-Friday)
- **12:00 PM IST (6:30 AM UTC)** - Mid-day analysis (Monday-Friday)

## Setup Instructions

### 1. Push Code to GitHub
```bash
git add .
git commit -m "NSE Analysis - Modular version"
git push origin main
```

### 2. Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these three secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `EMAIL_FROM` | Gmail address to send from | `your-email@gmail.com` |
| `EMAIL_TO` | Email address to receive reports | `recipient@gmail.com` |
| `EMAIL_PASS` | Gmail App Password (not regular password) | `abcd efgh ijkl mnop` |

### 3. Generate Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" and "Other (Custom name)"
5. Enter "NSE Analysis" as the name
6. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
7. Use this as `EMAIL_PASS` secret (with or without spaces)

### 4. Enable GitHub Actions

1. Go to your repository → Actions tab
2. If prompted, click "I understand my workflows, go ahead and enable them"
3. The workflow should now be visible: "Daily NSE Stock Analysis"

### 5. Test Manual Run

1. Go to Actions tab
2. Click "Daily NSE Stock Analysis" workflow
3. Click "Run workflow" dropdown
4. Click green "Run workflow" button
5. Wait for completion (usually 2-3 minutes)
6. Check your email for the report

## Workflow File Location
`.github/workflows/daily-nse-analysis.yml`

## What Happens During Each Run

1. ✅ Checks out code from repository
2. ✅ Sets up Python 3.11 environment
3. ✅ Installs dependencies from `requirements.txt`
4. ✅ Runs `nse_analysis_modular.py`
5. ✅ Fetches NSE data (or uses cache if < 6 hours old)
6. ✅ Computes all metrics and generates charts
7. ✅ Sends email with embedded charts
8. ✅ Saves CSV report to `dump/` directory

## Monitoring

### View Workflow Runs
- Go to Actions tab to see all runs
- Green checkmark = Success
- Red X = Failed (check logs for details)

### Common Issues

**Issue**: Workflow not running automatically
- **Solution**: Check that GitHub Actions is enabled in repository settings

**Issue**: Email not received
- **Solution**: Verify secrets are set correctly, check spam folder

**Issue**: Authentication error
- **Solution**: Regenerate Gmail App Password and update `EMAIL_PASS` secret

**Issue**: Module not found error
- **Solution**: Ensure all dependencies are in `requirements.txt`

## Cache Behavior

- Data is cached for 6 hours in `cache/nse_data_cache.csv`
- First run of the day fetches fresh data from NSE
- Subsequent runs within 6 hours use cached data
- Cache is stored in GitHub Actions workspace (not persisted between runs)

## Customization

### Change Schedule
Edit `.github/workflows/daily-nse-analysis.yml`:
```yaml
schedule:
  - cron: '0 4 * * 1-5'  # 9:30 AM IST
  - cron: '30 6 * * 1-5' # 12:00 PM IST
```

Use [crontab.guru](https://crontab.guru/) to generate cron expressions.

### Change Stock List
Edit `stocks.txt` - one symbol per line

### Modify Email Recipients
Update `EMAIL_TO` secret to change recipient

## Cost
GitHub Actions provides 2,000 free minutes/month for public repositories and 500 minutes/month for private repositories. This workflow uses ~5 minutes per run (2 runs/day × 5 days = 50 minutes/week).

## Support
For issues, check:
1. GitHub Actions logs (Actions tab → Click on failed run)
2. Email delivery logs in workflow output
3. NSE API status (if data fetching fails)