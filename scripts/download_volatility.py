import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import io

def get_last_trading_day():
    today = datetime.now()
    if today.weekday() == 5:
        today = today - timedelta(days=1)
    elif today.weekday() == 6:
        today = today - timedelta(days=2)
    return today

def download_volatility():
    target_date = get_last_trading_day()
    date_str = target_date.strftime('%d%m%Y')
    url = f"https://nsearchives.nseindia.com/archives/nsccl/volt/CMVOLT_{date_str}.CSV"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        print(f"📥 Downloading Volatility Report from: {url}")
        response = requests.get(url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            content = io.StringIO(response.text)
            df = pd.read_csv(content)
            print(f"✅ Downloaded volatility report: {len(df)} securities")
            
            os.makedirs('data/raw', exist_ok=True)
            output_path = f'data/raw/volatility_{date_str}.csv'
            df.to_csv(output_path, index=False)
            print(f"   Saved to: {output_path}")
            return df
        else:
            print(f"❌ HTTP {response.status_code}: Could not download volatility")
            return None
    except Exception as e:
        print(f"❌ Error downloading volatility: {e}")
        return None

if __name__ == "__main__":
    download_volatility()
