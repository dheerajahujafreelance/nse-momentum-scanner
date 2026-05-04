import pandas as pd
from datetime import datetime

def safe_float_convert(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def generate_trading_report():
    print("\n" + "="*50)
    print("GENERATING TRADING REPORT")
    print("="*50)
    
    try:
        watchlist = pd.read_csv('output/watchlist.csv')
        all_stocks = pd.read_csv('output/all_stocks_ranked.csv')
    except FileNotFoundError as e:
        print(f"❌ Could not load data: {e}")
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    strong_buy = len(all_stocks[all_stocks['RECOMMENDATION'] == 'STRONG_BUY'])
    buy = len(all_stocks[all_stocks['RECOMMENDATION'] == 'BUY'])
    
    report = f"""# 📈 NIFTY 200 Momentum + Volatility Watchlist
**Generated:** {timestamp} IST

## 🎯 Universe: NIFTY 200 Stocks Only

This scan focuses only on **Nifty 200 constituents** - highly liquid, institutional-grade stocks.

## 🔥 Top 10 Momentum Stocks

| # | Symbol | Close (₹) | Change % | Daily Vol | Score | Action |
|---|--------|----------|----------|-----------|-------|--------|
"""
    for idx, row in watchlist.head(10).iterrows():
        symbol = row.get('SYMBOL', 'N/A')
        close = safe_float_convert(row.get('CLOSE_PRICE', 0))
        change = safe_float_convert(row.get('MOMENTUM_PRICE', 0))
        vol = safe_float_convert(row.get('VOLATILITY_DAILY', 0)) * 100
        score = safe_float_convert(row.get('FINAL_SCORE', 0))
        rec = row.get('RECOMMENDATION', 'HOLD')
        report += f"| {idx+1} | **{symbol}** | {close:.2f} | {change:+.2f}% | {vol:.2f}% | {score:.0f} | {rec} |\n"
    
    report += f"""

## 📊 Summary

| Metric | Value |
|--------|-------|
| Nifty 200 Stocks Analyzed | {len(all_stocks)} |
| **STRONG_BUY** | {strong_buy} |
| **BUY** | {buy} |

---
*Nifty 200 Momentum Scanner | Next run: Tomorrow 7:40 PM IST*
"""
    
    with open('output/daily_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report generated: {len(watchlist)} stocks in watchlist")

if __name__ == "__main__":
    generate_trading_report()
