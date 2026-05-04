import pandas as pd
import os
import glob
from datetime import datetime

def load_latest_bhavcopy():
    """Load the most recent bhavcopy file"""
    files = glob.glob('data/raw/bhavcopy_*.csv')
    if not files:
        raise FileNotFoundError("No bhavcopy file found in data/raw/")
    latest = max(files)
    print(f"📂 Loading: {latest}")
    
    try:
        df = pd.read_csv(latest)
        print(f"   Loaded {len(df)} rows")
        return df
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        raise

def filter_only_equity(df):
    """
    Filter only equity shares (SERIES = EQ)
    Exclude: ETFs, Mutual Funds, Preference Shares, etc.
    """
    original_count = len(df)
    
    # Check if SERIES column exists
    if 'SERIES' in df.columns:
        # Keep only EQ series (equity shares)
        df = df[df['SERIES'].astype(str).str.upper().str.strip() == 'EQ']
        print(f"📊 Equity filter: {original_count} → {len(df)} stocks (excluded {original_count - len(df)} non-equity)")
    else:
        print("⚠️ No SERIES column found - checking for alternative...")
        # Check for other possible column names
        possible_series = ['Series', 'series', 'SERIES']
        for col in possible_series:
            if col in df.columns:
                df = df[df[col].astype(str).str.upper().str.strip() == 'EQ']
                print(f"   Using '{col}' column: {len(df)} stocks remaining")
                break
    
    # Additional filters: Remove indices, ETFs, mutual funds by symbol
    exclude_keywords = ['NIFTY', 'BANKNIFTY', 'ETF', 'MUTUAL', 'GOLD', 'SILVER', 
                        'GSEC', 'GILT', 'LIQUID', 'LIQ']
    
    before = len(df)
    if 'SYMBOL' in df.columns:
        for keyword in exclude_keywords:
            df = df[~df['SYMBOL'].astype(str).str.contains(keyword, case=False, na=False)]
        print(f"   Excluded {before - len(df)} rows with keyword filters")
    
    return df

def create_master_equity_list(df):
    """Save filtered equity list as reference"""
    if 'SYMBOL' in df.columns:
        equity_symbols = df[['SYMBOL']].copy()
        equity_symbols['TRADABLE'] = True
        
        os.makedirs('data/reference', exist_ok=True)
        equity_symbols.to_csv('data/reference/equity_master_list.csv', index=False)
        print(f"✅ Saved master equity list: {len(equity_symbols)} symbols")
    
    return df

def main():
    print("\n" + "="*50)
    print("FILTERING EQUITY STOCKS")
    print("="*50)
    
    try:
        df = load_latest_bhavcopy()
        df_filtered = filter_only_equity(df)
        df_final = create_master_equity_list(df_filtered)
        
        # Save filtered bhavcopy
        os.makedirs('data/filtered', exist_ok=True)
        date_str = datetime.now().strftime('%Y%m%d')
        output_path = f'data/filtered/equity_bhavcopy_{date_str}.csv'
        df_final.to_csv(output_path, index=False)
        
        print(f"\n✅ Final equity dataset: {len(df_final)} stocks ready for momentum analysis")
        print(f"   Saved to: {output_path}")
        
        return df_final
    except Exception as e:
        print(f"❌ Error in filtering: {e}")
        return None

if __name__ == "__main__":
    main()
