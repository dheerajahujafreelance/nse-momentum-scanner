import requests
import pandas as pd
import os
from datetime import datetime, timedelta

def get_last_trading_day():
    """Get last trading day (skip weekends)"""
    today = datetime.now()
    # Saturday or Sunday? Go back to Friday
    if today.weekday() == 5:  # Saturday
        today = today - timedelta(days=1)
    elif today.weekday() == 6:  # Sunday
        today = today - timedelta(days=2)
    return today

def download_bhavcopy():
    """
    Download NSE Bhavcopy from the correct URL
    URL: https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{DDMMYYYY}.csv
    """
    target_date = get_last_trading_day()
    date_str = target_date.strftime('%d%m%Y')
    
    # Correct URL as per your reference
    url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    try:
        print(f"📥 Downloading Bhavcopy from: {url}")
        response = requests.get(url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # Parse CSV content
            df = pd.read_csv(response.text)
            
            # Standardize column names to uppercase
            df.columns = [col.upper().strip() for col in df.columns]
            
            print(f"✅ Downloaded bhavcopy: {len(df)} rows")
            print(f"   Columns: {list(df.columns)}")
            
            # Save raw data
            os.makedirs('data/raw', exist_ok=True)
            output_path = f'data/raw/bhavcopy_{date_str}.csv'
            df.to_csv(output_path, index=False)
            print(f"   Saved to: {output_path}")
            
            return df
        else:
            print(f"❌ HTTP {response.status_code}: Could not download bhavcopy for {date_str}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading bhavcopy: {e}")
        return None

if __name__ == "__main__":
    download_bhavcopy()
