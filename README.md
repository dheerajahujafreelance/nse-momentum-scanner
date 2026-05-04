# NSE Nifty 200 Momentum Scanner

Automated daily scanner for Nifty 200 stocks.

## Features

- Downloads Nifty 200 constituents list
- Downloads NSE Bhavcopy and Volatility reports
- Filters only Nifty 200 equity stocks
- Calculates momentum scores
- Generates timestamped MD reports
- Top 30 buy recommendations

## Output Files

- `top_30_buy_watchlist.csv` - Top 30 momentum stocks
- `top_10_momentum.csv` - Top 10 quick reference
- `all_stocks_ranked.csv` - Complete ranking
- `nifty200_momentum_report_*.md` - Timestamped report

## Schedule

Runs daily at 7:40 PM IST

## Manual Run

```bash
python scripts/clean_folders.py
python scripts/download_nifty200.py
python scripts/download_bhavcopy.py
python scripts/download_volatility.py
python scripts/filter_nifty200.py
python scripts/calculate_momentum.py
python scripts/generate_report.py
