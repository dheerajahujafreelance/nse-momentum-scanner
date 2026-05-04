import requests
import pandas as pd
import os
from datetime import datetime

def download_nifty200():
    """
    Download Nifty 200 index constituents list
    URL: https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv
    """
    url = "https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        print(f"📥 Downloading Nifty 200 list from: {url}")
        response = requests.get(url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # Parse CSV content
            df = pd.read_csv(response.text)
            
            print(f"✅ Downloaded Nifty 200 list: {len(df)} stocks")
            print(f"   Columns: {list(df.columns)}")
            
            # Save raw data
            os.makedirs('data/reference', exist_ok=True)
            output_path = 'data/reference/nifty200_list.csv'
            df.to_csv(output_path, index=False)
            print(f"   Saved to: {output_path}")
            
            # Display first few symbols
            if 'Symbol' in df.columns:
                print(f"   Sample symbols: {df['Symbol'].head(5).tolist()}")
            
            return df
        else:
            print(f"❌ HTTP {response.status_code}: Could not download Nifty 200 list")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading Nifty 200 list: {e}")
        return None

if __name__ == "__main__":
    download_nifty200()
