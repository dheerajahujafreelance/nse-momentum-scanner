# 📈 NSE Nifty 200 Momentum Scanner

An automated daily scanner that analyzes Nifty 200 stocks, calculates momentum scores, and sends reports to Telegram.

## ✨ Features

- **Nifty 200 Focus** - Analyzes only liquid, institutional-grade stocks
- **Daily Automation** - Runs at 7:40 PM IST every trading day
- **Momentum Scoring** - Weighted score using price, volume, and volatility
- **Telegram Integration** - Get reports directly on your phone
- **Top 30 Watchlist** - Best momentum stocks for next day
- **Timestamped Reports** - Never lose historical data

## 🎯 Scoring Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Price Momentum | 35% | Today's close vs previous close |
| Intraday Strength | 20% | Close vs Open (buying pressure) |
| Range Breakout | 15% | Closing near day's high |
| Volume Momentum | 15% | Higher than average volume |
| Daily Volatility | 15% | Price expansion confirmation |

## 📊 Output Files

| File | Description |
|------|-------------|
| `nifty200_momentum_report_*.md` | Timestamped markdown report |
| `nifty200_momentum_report_latest.md` | Latest report (overwrites) |
| `top_30_buy_watchlist.csv` | Top 30 momentum stocks |
| `top_10_momentum.csv` | Top 10 quick reference |
| `all_stocks_ranked.csv` | Complete ranking of all Nifty 200 stocks |

## 🤖 Telegram Setup

### Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Name your bot (e.g., `NSE Momentum Scanner`)
4. Get your **Bot Token** (format: `1234567890:ABCdefGHIjklmNOPqrstUVwxyz`)

### Get Your Chat ID

1. Open Telegram and search for `@get_id_bot`
2. Send `/start`
3. Copy your **User ID** (a positive number like `987654321`)

> ⚠️ **Important**: Use `@get_id_bot`, NOT `@userinfobot`. The latter gives a bot ID which won't work.

### Add Secrets to GitHub

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → Add:

| Secret Name | Value |
|-------------|-------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your numeric user ID from @get_id_bot |

## 🚀 Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/dheerajahujafreelance/nse-momentum-scanner.git
cd nse-momentum-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run all scripts manually
python scripts/clean_folders.py
python scripts/download_nifty200.py
python scripts/download_bhavcopy.py
python scripts/download_volatility.py
python scripts/filter_nifty200.py
python scripts/calculate_momentum.py
python scripts/generate_report.py
python scripts/send_telegram.py
