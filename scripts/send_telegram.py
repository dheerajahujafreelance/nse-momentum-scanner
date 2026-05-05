import requests
import os
import glob
from datetime import datetime

def get_latest_report():
    """Get the most recent MD report file"""
    files = glob.glob('output/nifty200_momentum_report_*.md')
    if not files:
        return None
    latest = max(files)
    return latest

def format_report_for_telegram(report_path):
    """Convert MD report to Telegram-friendly format"""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Telegram has message length limit of 4096 characters
    # Split into multiple messages if needed
    messages = []
    
    # Extract key sections for summary
    lines = content.split('\n')
    
    # Build a compact version
    compact_report = []
    in_table = False
    table_count = 0
    
    for line in lines:
        # Skip long tables after first 2
        if line.startswith('|'):
            table_count += 1
            if table_count <= 15:  # Keep top part of table
                compact_report.append(line)
            elif table_count == 16:
                compact_report.append('| ... | ... | ... | ... |')
            continue
        
        # Keep important sections
        if any(keyword in line for keyword in [
            'TOP 10 BUY CANDIDATES', 'Market Summary', 'BUY Side Signals',
            'Nifty 200 Stocks Analyzed', 'STRONG_BUY', 'Generated:'
        ]):
            compact_report.append(line)
        elif line.startswith('#') or line.startswith('##'):
            compact_report.append(line)
        elif line.startswith('---'):
            compact_report.append(line)
    
    result = '\n'.join(compact_report)
    
    # Split if too long (Telegram limit 4096)
    if len(result) > 4000:
        return [result[:4000], result[4000:8000]]
    return [result]

def send_telegram_message(bot_token, chat_id, message):
    """Send message via Telegram bot"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',  # Use HTML formatting
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ Telegram message sent successfully")
            return True
        else:
            print(f"❌ Failed to send: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def send_file_as_document(bot_token, chat_id, file_path):
    """Send MD file as a document"""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id}
        
        try:
            response = requests.post(url, data=data, files=files, timeout=60)
            if response.status_code == 200:
                print(f"✅ Document sent: {os.path.basename(file_path)}")
                return True
            else:
                print(f"❌ Failed to send document: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending document: {e}")
            return False

def send_formatted_summary(bot_token, chat_id, all_stocks_file, watchlist_file):
    """Send a formatted summary with key stats"""
    
    try:
        import pandas as pd
        
        # Read data
        all_stocks = pd.read_csv(all_stocks_file)
        watchlist = pd.read_csv(watchlist_file)
        
        # Calculate stats
        total_stocks = len(all_stocks)
        strong_buy = len(all_stocks[all_stocks['RECOMMENDATION'] == 'STRONG_BUY'])
        buy = len(all_stocks[all_stocks['RECOMMENDATION'] == 'BUY'])
        
        # Get top 5 stocks
        top_5 = watchlist.head(5)
        
        # Build message
        now = datetime.now().strftime('%d %b %Y %H:%M')
        message = f"""<b>📈 NSE Nifty 200 Momentum Report</b>
<b>🕐 {now} IST</b>

<b>📊 Market Summary</b>
├ Nifty 200 Analyzed: {total_stocks}
├ <b>STRONG_BUY</b>: {strong_buy} stocks
└ <b>BUY</b>: {buy} stocks

<b>🏆 Top 5 Momentum Stocks</b>
"""
        
        for idx, row in top_5.iterrows():
            symbol = row.get('SYMBOL', 'N/A')
            change = row.get('MOMENTUM_PRICE', 0)
            score = row.get('FINAL_SCORE', 0)
            
            # Emoji based on performance
            if change > 3:
                emoji = "🚀"
            elif change > 1:
                emoji = "📈"
            elif change > 0:
                emoji = "↗️"
            else:
                emoji = "📉"
            
            message += f"\n{idx+1}. <b>{symbol}</b> {emoji} {change:+.2f}% (Score: {score:.0f})"
        
        message += f"\n\n<i>Full report attached 📎</i>"
        
        # Send summary
        send_telegram_message(bot_token, chat_id, message)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating summary: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("SENDING REPORT TO TELEGRAM")
    print("="*50)
    
    # Get secrets from environment
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Telegram credentials not found in secrets")
        print("   Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to repository secrets")
        return
    
    # Find report file
    report_file = get_latest_report()
    if not report_file:
        print("❌ No report file found")
        return
    
    print(f"📄 Found report: {report_file}")
    
    # Send summary first
    all_stocks_file = 'output/all_stocks_ranked.csv'
    watchlist_file = 'output/top_30_buy_watchlist.csv'
    
    if os.path.exists(all_stocks_file) and os.path.exists(watchlist_file):
        send_formatted_summary(bot_token, chat_id, all_stocks_file, watchlist_file)
    else:
        # Fallback: just send the report as text
        messages = format_report_for_telegram(report_file)
        for msg in messages:
            send_telegram_message(bot_token, chat_id, msg)
    
    # Send full report as document
    send_file_as_document(bot_token, chat_id, report_file)
    
    # Also send CSV watchlist as document
    csv_file = 'output/top_30_buy_watchlist.csv'
    if os.path.exists(csv_file):
        send_file_as_document(bot_token, chat_id, csv_file)
    
    print("\n✅ Telegram notification complete")

if __name__ == "__main__":
    main()
