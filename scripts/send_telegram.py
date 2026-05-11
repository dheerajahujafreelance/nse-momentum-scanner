import requests
import os
import glob
from datetime import datetime

def send_to_telegram_channel(bot_token, channel_username, message):
    """
    Send message to a Telegram channel using the channel's @username.
    
    Args:
        bot_token: Your bot's API token from BotFather
        channel_username: Channel username WITH @ symbol (e.g., @CompoundMindFin)
        message: The message text to send
    """
    # Ensure channel username has @ prefix
    if not channel_username.startswith('@'):
        channel_username = '@' + channel_username
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': channel_username,  # Use @username for channels
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if result.get('ok'):
            print(f"✅ Message sent to channel: {channel_username}")
            return True
        else:
            error = result.get('description', 'Unknown error')
            print(f"❌ Failed: {error}")
            
            if 'chat not found' in error:
                print("\n💡 Troubleshooting:")
                print("   1. Make sure the channel username is correct")
                print("   2. Add your bot as an ADMIN to the channel")
                print("   3. The channel must be PUBLIC or bot must be added as admin")
            return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def send_file_to_channel(bot_token, channel_username, file_path):
    """Send a file (MD or CSV) to the Telegram channel"""
    if not channel_username.startswith('@'):
        channel_username = '@' + channel_username
    
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return False
    
    with open(file_path, 'rb') as f:
        try:
            response = requests.post(
                url, 
                data={'chat_id': channel_username}, 
                files={'document': f},
                timeout=60
            )
            result = response.json()
            if result.get('ok'):
                print(f"✅ File sent to channel: {os.path.basename(file_path)}")
                return True
            else:
                print(f"❌ Failed: {result.get('description')}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def get_latest_report():
    """Get the most recent MD report file"""
    files = glob.glob('output/nifty200_momentum_report_*.md')
    if not files:
        return None
    return max(files)

def create_channel_summary():
    """Create a formatted summary message for the channel"""
    try:
        import pandas as pd
        
        all_stocks = pd.read_csv('output/all_stocks_ranked.csv')
        watchlist = pd.read_csv('output/top_30_buy_watchlist.csv')
        
        # Calculate stats
        total = len(all_stocks)
        strong_buy = len(all_stocks[all_stocks['RECOMMENDATION'] == 'STRONG_BUY'])
        buy = len(all_stocks[all_stocks['RECOMMENDATION'] == 'BUY'])
        
        # Get top 5 stocks
        top5 = watchlist.head(5)
        
        # Get current time in IST
        now = datetime.now()
        date_str = now.strftime('%d %b %Y')
        time_str = now.strftime('%I:%M %p')
        
        # Build message with HTML formatting
        msg = f"<b>📈 NIFTY 200 MOMENTUM REPORT</b>\n"
        msg += f"<b>📅 {date_str} | ⏰ {time_str} IST</b>\n\n"
        
        msg += f"<b>📊 MARKET SUMMARY</b>\n"
        msg += f"├ Nifty 200 Analyzed: {total}\n"
        msg += f"├ <b>STRONG_BUY</b>: {strong_buy} stocks\n"
        msg += f"└ <b>BUY</b>: {buy} stocks\n\n"
        
        msg += f"<b>🏆 TOP 5 MOMENTUM STOCKS</b>\n"
        
        for i, row in top5.iterrows():
            symbol = row['SYMBOL']
            change = row['MOMENTUM_PRICE']
            score = row['FINAL_SCORE']
            
            # Emoji based on performance
            if change > 3:
                emoji = "🚀"
            elif change > 1:
                emoji = "📈"
            elif change > 0:
                emoji = "↗️"
            else:
                emoji = "📉"
            
            msg += f"\n{i+1}. <b>{symbol}</b> {emoji} {change:+.2f}%"
            msg += f"\n   └ Score: {score:.0f}\n"
        
        msg += f"\n<i>📎 Full reports attached below</i>"
        msg += f"\n\n<i>🔔 Next scan: Tomorrow at 7:40 PM IST</i>"
        
        return msg
    except Exception as e:
        return f"📈 NSE Nifty 200 Scanner completed at {datetime.now().strftime('%H:%M')} IST"

def main():
    print("\n" + "="*50)
    print("TELEGRAM CHANNEL PUBLISHER")
    print("="*50)
    
    # Get secrets from environment
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    channel_username = os.environ.get('TELEGRAM_CHAT_ID')  # Should be @CompoundMindFin
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in secrets")
        print("\nTo fix:")
        print("1. Go to @BotFather on Telegram")
        print("2. Create a bot or get your existing token")
        print("3. Add it as TELEGRAM_BOT_TOKEN in GitHub secrets")
        return
    
    if not channel_username:
        print("❌ TELEGRAM_CHAT_ID not found in secrets")
        print("\nTo fix:")
        print("1. Add your channel username: @CompoundMindFin")
        print("2. Make sure your bot is an ADMIN in the channel")
        return
    
    print(f"📢 Publishing to channel: {channel_username}")
    
    # Send formatted summary
    summary = create_channel_summary()
    send_to_telegram_channel(bot_token, channel_username, summary)
    
    # Send the full MD report as a document
    report_file = get_latest_report()
    if report_file:
        send_file_to_channel(bot_token, channel_username, report_file)
    
    # Send the CSV watchlist as a document
    csv_file = 'output/top_30_buy_watchlist.csv'
    if os.path.exists(csv_file):
        send_file_to_channel(bot_token, channel_username, csv_file)
    
    print("\n" + "="*50)
    print("✅ Channel publishing complete")
    print("="*50)

if __name__ == "__main__":
    main()
