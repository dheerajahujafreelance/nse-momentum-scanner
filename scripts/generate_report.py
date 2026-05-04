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
        all_stocks = pd.read_csv('output/all_stocks_ranked.csv')
        buy_watchlist = pd.read_csv('output/top_30_buy_watchlist.csv')
        sell_watchlist = pd.read_csv('output/top_20_sell_watchlist.csv')
    except FileNotFoundError as e:
        print(f"❌ Could not load data: {e}")
        return
    
    # Get current timestamp for filename
    now = datetime.now()
    timestamp_str = now.strftime('%Y%m%d_%H%M%S')
    date_str = now.strftime('%d %B %Y')
    time_str = now.strftime('%H:%M:%S')
    
    # Create timestamped filename
    md_filename = f"output/nifty200_momentum_report_{timestamp_str}.md"
    
    # Calculate stats
    strong_buy = len(all_stocks[all_stocks['BUY_RECOMMENDATION'] == 'STRONG_BUY'])
    buy = len(all_stocks[all_stocks['BUY_RECOMMENDATION'] == 'BUY'])
    hold = len(all_stocks[all_stocks['BUY_RECOMMENDATION'] == 'HOLD'])
    
    short_candidate = len(all_stocks[all_stocks['SELL_RECOMMENDATION'] == 'SHORT_CANDIDATE'])
    strong_avoid = len(all_stocks[all_stocks['SELL_RECOMMENDATION'] == 'STRONG_AVOID'])
    avoid = len(all_stocks[all_stocks['SELL_RECOMMENDATION'] == 'AVOID'])
    
    report = f"""# 📈 NIFTY 200 Momentum Report
**Generated:** {date_str} at {time_str} IST  
**Report ID:** {timestamp_str}

---

## 🎯 Strategy Overview

This report analyzes **Nifty 200 constituents** using a weighted momentum strategy:

| Component | BUY Weight | SELL Weight | Description |
|-----------|-----------|-------------|-------------|
| Price Momentum | +35% | -40% | Close vs previous close |
| Intraday Strength | +20% | -20% | Close vs Open |
| Range Position | +15% | -15% | Closing near high/low |
| Volume Momentum | +15% | +10% | Volume confirmation |
| Daily Volatility | +15% | +15% | Price expansion |

---

## 📊 Market Summary

| Metric | Value |
|--------|-------|
| **Nifty 200 Stocks Analyzed** | {len(all_stocks)} |
| **Analysis Date** | {date_str} |

### 📈 BUY Side Signals
| Recommendation | Count | Action |
|---------------|-------|--------|
| **STRONG_BUY** (Score > 75) | {strong_buy} | High conviction buys |
| **BUY** (Score 60-75) | {buy} | Positive momentum |
| **HOLD** (Score 40-60) | {hold} | Wait for breakout |

### 📉 SELL Side Signals
| Recommendation | Count | Action |
|---------------|-------|--------|
| **SHORT_CANDIDATE** | {short_candidate} | Potential short opportunities |
| **STRONG_AVOID** | {strong_avoid} | Stay away completely |
| **AVOID** | {avoid} | Negative momentum |

---

## 🔥 TOP 10 BUY CANDIDATES (Highest Momentum)

| # | Symbol | Close (₹) | Change % | Daily Vol | BUY Score | Action |
|---|--------|----------|----------|-----------|-----------|--------|
"""
    
    for idx, row in buy_watchlist.head(10).iterrows():
        symbol = row.get('SYMBOL', 'N/A')
        close = safe_float_convert(row.get('CLOSE_PRICE', 0))
        change = safe_float_convert(row.get('MOMENTUM_PRICE', 0))
        vol = safe_float_convert(row.get('VOLATILITY_DAILY', 0)) * 100
        score = safe_float_convert(row.get('BUY_SCORE', 0))
        rec = row.get('BUY_RECOMMENDATION', 'HOLD')
        report += f"| {idx+1} | **{symbol}** | {close:.2f} | {change:+.2f}% | {vol:.2f}% | {score:.0f} | {rec} |\n"
    
    report += f"""

---

## ⚠️ TOP 10 SELL SIGNALS (Stocks to Avoid/Short)

| # | Symbol | Change % | SELL Score | Recommendation | Signal Type |
|---|--------|----------|------------|----------------|-------------|
"""
    
    for idx, row in sell_watchlist.head(10).iterrows():
        symbol = row.get('SYMBOL', 'N/A')
        change = safe_float_convert(row.get('MOMENTUM_PRICE', 0))
        sell_score = safe_float_convert(row.get('SELL_SCORE', 0))
        sell_rec = row.get('SELL_RECOMMENDATION', 'HOLD')
        sell_signal = row.get('SELL_SIGNAL', 'NO_SIGNAL')
        report += f"| {idx+1} | **{symbol}** | {change:+.2f}% | {sell_score:.0f} | {sell_rec} | {sell_signal} |\n"
    
    report += f"""

---

## 📋 Interpretation Guide

### BUY Signals
- **STRONG_BUY** > 75: High probability up move, consider entering
- **BUY** 60-75: Positive momentum, watch for entry
- **HOLD** 40-60: Consolidating, wait for breakout

### SELL Signals  
- **SHORT_CANDIDATE**: Strong downward momentum, potential short opportunity
- **STRONG_AVOID**: Significant weakness, stay away
- **AVOID**: Negative momentum, not recommended for buying

### Signal Types
- **HIGH_VOLUME_BREAKDOWN**: Price down with high volume - institutional selling
- **STRONG_DOWNTREND**: Sustained negative momentum
- **WEAK_CLOSE**: Closing near day's low with weak intraday

---

## ⚠️ Disclaimer

This is an **automated scan** based on NSE data. Always perform your own research before trading. Past performance does not guarantee future results.

---
*Generated by NSE Nifty 200 Momentum Scanner*
*Next run: Tomorrow at 7:40 PM IST*
"""
    
    # Save the report with timestamp
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Timestamped report generated: {md_filename}")
    print(f"   BUY watchlist: {len(buy_watchlist)} stocks")
    print(f"   SELL watchlist: {len(sell_watchlist)} stocks")
    
    # Also save a latest copy (overwrites previous)
    with open('output/nifty200_momentum_report_latest.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   Latest report saved: output/nifty200_momentum_report_latest.md")

if __name__ == "__main__":
    generate_trading_report()
