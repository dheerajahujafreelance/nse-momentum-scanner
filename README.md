# NSE Momentum Scanner

Automated daily scanner that downloads NSE Bhavcopy and Volatility reports, filters equity stocks, and generates momentum scores for next-day trading.

## Features

- **Daily Automated Run**: Runs at 7:40 PM IST every trading day
- **Downloads from Official NSE Archives**: 
  - Bhavcopy: `https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{DDMMYYYY}.csv`
  - Volatility: `https://nsearchives.nseindia.com/archives/nsccl/volt/CMVOLT_{DDMMYYYY}.CSV`
- **Equity Only Filter**: Excludes ETFs, indices, mutual funds
- **Momentum Scoring**: Weighted score using price, intraday strength, range breakout, volume, and daily volatility
- **Actionable Output**: Generates watchlist with BUY/STRONG_BUY recommendations

## Scoring Weights

| Component | Weight |
|-----------|--------|
| Price Momentum | 35% |
| Intraday Strength | 20% |
| Range Breakout | 15% |
| Volume Momentum | 15% |
| Daily Volatility (E) | 15% |

## Output Files

- `output/watchlist.csv` - Top 30 momentum stocks
- `output/top_10_momentum.csv` - Top 10 for quick reference
- `output/all_stocks_ranked.csv` - Complete ranking
- `output/daily_report.md` - Formatted markdown report

## Setup

1. Clone this repository
2. Push to GitHub
3. GitHub Actions will run automatically daily at 7:40 PM IST

## Manual Run

Go to Actions → "NSE Momentum Scanner" → "Run workflow"

## Disclaimer

For educational purposes only. Not financial advice.
