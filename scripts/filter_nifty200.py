import pandas as pd
import os
import glob
from datetime import datetime

def load_nifty200_list():
    """Load the Nifty 200 constituents list"""
    possible_paths = [
        'data/reference/ind_nifty200list.csv',
        'data/reference/nifty200_list.csv',
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        raise FileNotFoundError(f"Nifty 200 list not found. Tried: {possible_paths}")
    
    print(f"📂 Loading Nifty 200 list from: {file_path}")
    df = pd.read_csv(file_path)
    print(f"   Loaded {len(df)} stocks")
    
    symbol_col = None
    for col in ['Symbol', 'SYMBOL', 'symbol']:
        if col in df.columns:
            symbol_col = col
            break
    
    if symbol_col:
        nifty_symbols = set(df[symbol_col].astype(str).str.strip().str.upper())
        print(f"   Found {len(nifty_symbols)} unique symbols")
        return nifty_symbols
    else:
        print(f"⚠️ Could not find Symbol column. Available: {list(df.columns)}")
        return set()

def load_latest_bhavcopy():
    """Load the most recent bhavcopy file"""
    files = glob.glob('data/raw/bhavcopy_*.csv')
    if not files:
        raise FileNotFoundError("No bhavcopy file found in data/raw/")
    latest = max(files)
    df = pd.read_csv(latest)
    print(f"📂 Loaded bhavcopy: {len(df)} rows")
    return df

def filter_nifty200_stocks(df, nifty_symbols):
    """Filter bhavcopy to only include Nifty 200 stocks"""
    original_count = len(df)
    
    if 'SYMBOL' in df.columns:
        df['SYMBOL'] = df['SYMBOL'].astype(str).str.strip().str.upper()
        df_filtered = df[df['SYMBOL'].isin(nifty_symbols)]
    else:
        print("⚠️ No SYMBOL column found")
        return df.head(0)
    
    print(f"📊 Nifty 200 filter: {original_count} → {len(df_filtered)} stocks")
    print(f"   Filtered out {original_count - len(df_filtered)} non-Nifty stocks")
    
    missing_stocks = nifty_symbols - set(df_filtered['SYMBOL'])
    if missing_stocks:
        print(f"   ⚠️ {len(missing_stocks)} Nifty stocks not found in bhavcopy")
    
    return df_filtered

def filter_equity_only(df):
    """Further filter to only EQ series"""
    if 'SERIES' in df.columns:
        original_count = len(df)
        df = df[df['SERIES'].astype(str).str.upper().str.strip() == 'EQ']
        print(f"   Equity filter: {original_count} → {len(df)} stocks")
    return df

def save_filtered_data(df):
    """Save filtered Nifty 200 bhavcopy"""
    os.makedirs('data/filtered', exist_ok=True)
    date_str = datetime.now().strftime('%Y%m%d')
    output_path = f'data/filtered/nifty200_bhavcopy_{date_str}.csv'
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to: {output_path}")
    return output_path

def main():
    print("\n" + "="*50)
    print("FILTERING NIFTY 200 STOCKS")
    print("="*50)
    
    try:
        nifty_symbols = load_nifty200_list()
        if not nifty_symbols:
            print("❌ No Nifty 200 symbols loaded")
            return None
        
        df = load_latest_bhavcopy()
        if df is None or len(df) == 0:
            print("❌ No bhavcopy data loaded")
            return None
        
        df_filtered = filter_nifty200_stocks(df, nifty_symbols)
        
        if len(df_filtered) == 0:
            print("❌ No matching stocks found")
            return None
        
        df_filtered = filter_equity_only(df_filtered)
        save_filtered_data(df_filtered)
        
        print(f"\n✅ Nifty 200 equity stocks ready: {len(df_filtered)} stocks")
        
        if 'SYMBOL' in df_filtered.columns:
            print(f"   Sample: {df_filtered['SYMBOL'].head(10).tolist()}")
        
        return df_filtered
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
