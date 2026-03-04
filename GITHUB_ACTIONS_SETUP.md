# GitHub Actions Setup Guide - Daily NSE Analysis

## What You Get
- Automatic daily analysis at 9:30 AM IST (Mon-Fri)
- Results saved as artifacts (downloadable for 90 days)
- Optional: Results committed back to repo
- Manual trigger option anytime
- **100% FREE** (GitHub provides 2000 minutes/month free)

## Setup Steps

### Method 1: Using GitHub CLI (Recommended - Fastest)

```bash
# 1. Create repo and push in one command
gh repo create NSE --public --source=. --remote=origin --push

# 2. Enable workflow (if needed)
gh workflow enable daily-nse-analysis.yml

# 3. Configure permissions (one-time)
gh repo view --web
# In browser: Settings → Actions → General → Workflow permissions → "Read and write"

# 4. Test run immediately
gh workflow run daily-nse-analysis.yml

# 5. Watch the run
gh run watch

# 6. Download results
gh run download
```

**Daily usage:**
```bash
# Check latest run status
gh run list --workflow=daily-nse-analysis.yml --limit 1

# Download latest results
gh run download $(gh run list --workflow=daily-nse-analysis.yml --limit 1 --json databaseId --jq '.[0].databaseId')

# View logs
gh run view --log
```

### Method 2: Using Git + Web Interface

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Add NSE Analysis with GitHub Actions"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/NSE.git
git branch -M main
git push -u origin main
```

**Then on GitHub.com:**

1. **Enable Actions**: Go to **Actions** tab → Enable workflows
2. **Set Permissions**: **Settings** → **Actions** → **General** → **Workflow permissions** → "Read and write"
3. **Test Run**: **Actions** → **Daily NSE Stock Analysis** → **Run workflow**
4. **View Results**: Click completed run → Download artifacts

### View Results

**Using GitHub CLI:**
```bash
gh run list                    # List all runs
gh run view                    # View latest run details
gh run download                # Download artifacts
```

**Using Web Interface:**
1. Go to **Actions** tab
2. Click on completed workflow run
3. Scroll to **Artifacts** section
4. Download `nse-analysis-XXX.zip`

**In repo** (if auto-commit enabled):
- Results in `dump/` folder
- Updated automatically after each run

## Schedule Details

```yaml
cron: '0 4 * * 1-5'  # 4:00 AM UTC = 9:30 AM IST (Mon-Fri)
```

**Adjust timing:**
- `0 3 * * 1-5` = 8:30 AM IST
- `30 4 * * 1-5` = 10:00 AM IST
- `0 10 * * 1-5` = 3:30 PM IST (market close)

## Cost Breakdown

| Item | Cost |
|------|------|
| GitHub Actions (2000 min/month) | FREE |
| Storage (artifacts 90 days) | FREE |
| Private repo | FREE |
| **Total** | **£0.00** |

Each run takes ~2-3 minutes = ~60 minutes/month for daily runs.

## Troubleshooting

### Workflow not running?
- Check **Actions** tab for errors
- Verify schedule syntax in `.github/workflows/daily-nse-analysis.yml`
- Ensure repo is not archived

### Dependencies failing?
- Check `requirements.txt` has all packages
- Test locally: `pip install -r requirements.txt`

### NSE API errors?
- NSE may block GitHub IPs occasionally
- Add retry logic or use proxy if needed

### Want email notifications?
Add to workflow after "Run NSE Analysis" step:

```yaml
- name: Send email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: NSE Analysis Complete
    to: your-email@example.com
    from: GitHub Actions
    body: Daily analysis completed. Check artifacts.
    attachments: dump/NSE-ANALYSIS-*.csv
```

## Advanced Options

### Run multiple times per day
```yaml
schedule:
  - cron: '0 4 * * 1-5'   # 9:30 AM IST
  - cron: '30 9 * * 1-5'  # 3:00 PM IST (before close)
```

### Only analyze specific stocks
Modify `STOCK_LIST` in `NSE_Analysis.py` or pass as environment variable.

### Send to Telegram/Slack
Add notification step using respective GitHub Actions.

## Files Created

```
NSE/
├── .github/
│   └── workflows/
│       └── daily-nse-analysis.yml  # Workflow definition
├── requirements.txt                 # Python dependencies
├── NSE_Analysis.py                  # Main script
└── GITHUB_ACTIONS_SETUP.md         # This file
```

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Enable Actions
3. ✅ Configure permissions
4. ✅ Test manual run
5. ✅ Wait for first scheduled run
6. 📊 Download and review results

## Support

- GitHub Actions docs: https://docs.github.com/actions
- Cron syntax: https://crontab.guru/
- Issues? Check Actions tab for logs