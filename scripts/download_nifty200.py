import requests
import pandas as pd
import os
from datetime import datetime
import io

def download_nifty200():
    """
    Download Nifty 200 index constituents list
    URL: https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv
    """
    url = "https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv"
    
    # Use a consistent filename
    output_filename = "ind_nifty200list.csv"
    os.makedirs('data/reference', exist_ok=True)
    output_path = os.path.join('data/reference', output_filename)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/csv,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        print(f"📥 Downloading Nifty 200 list from: {url}")
        response = requests.get(url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # Read CSV directly from response content
            content = io.StringIO(response.text)
            df = pd.read_csv(content)
            
            if df.empty:
                print("⚠️ Downloaded file is empty.")
                return None
            
            print(f"✅ Downloaded Nifty 200 list: {len(df)} rows")
            print(f"   Columns: {list(df.columns)}")
            
            # Save file
            df.to_csv(output_path, index=False)
            print(f"   Saved to: {output_path}")
            
            # Display first few symbols
            symbol_col = next((col for col in df.columns if col.lower() == 'symbol'), None)
            if symbol_col:
                print(f"   Sample symbols: {df[symbol_col].head(5).tolist()}")
            
            return df
        else:
            print(f"❌ HTTP {response.status_code}: Could not download Nifty 200 list.")
            print("   Please check the URL in a browser or try again later.")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading Nifty 200 list: {e}")
        return None

if __name__ == "__main__":
    download_nifty200()
