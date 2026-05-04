import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

def load_equity_bhavcopy():
    """Load filtered equity bhavcopy"""
    files = glob.glob('data/filtered/equity_bhavcopy_*.csv')
    if not files:
        raise FileNotFoundError("No equity bhavcopy found in data/filtered/")
    latest = max(files)
    df = pd.read_csv(latest)
    print(f"📂 Loaded equity data: {len(df)} stocks")
    print(f"   Columns available: {list(df.columns)[:15]}...")
    return df

def load_volatility_data():
    """
    Load latest volatility report and extract Current Day Underlying Daily Volatility (E)
    """
    files = glob.glob('data/raw/volatility_*.csv')
    if not files:
        print("⚠️ No volatility file found")
        return None
    
    latest = max(files)
    vol_df = pd.read_csv(latest)
    print(f"📂 Loaded volatility data: {len(vol_df)} securities")
    print(f"   Columns available: {list(vol_df.columns)}")
    
    # Find Symbol column (case insensitive)
    symbol_col = None
    for col in vol_df.columns:
        if col.lower() == 'symbol':
            symbol_col = col
            break
    
    # Find Volatility column - try exact match first, then partial match
    vol_col = None
    
    # Exact column name from your CSV
    exact_col = 'Current Day Underlying Daily Volatility (E) = Sqrt(0.995*D*D + 0.005*C*C)'
    
    if exact_col in vol_df.columns:
        vol_col = exact_col
        print(f"   ✅ Found exact volatility column")
    else:
        # Try partial matches
        for col in vol_df.columns:
            if 'Current Day Underlying Daily Volatility' in col:
                vol_col = col
                print(f"   ✅ Found volatility column: '{col}'")
                break
            elif 'Daily Volatility' in col:
                vol_col = col
                print(f"   ✅ Found volatility column: '{col}'")
                break
    
    if symbol_col and vol_col:
        # Rename columns for easier access
        vol_df = vol_df.rename(columns={symbol_col: 'SYMBOL', vol_col: 'VOLATILITY_DAILY'})
        print(f"   Using SYMBOL column: '{symbol_col}'")
        print(f"   Using VOLATILITY column: '{vol_col}'")
        print(f"   Volatility range: {vol_df['VOLATILITY_DAILY'].min():.6f} - {vol_df['VOLATILITY_DAILY'].max():.6f}")
        
        # Keep only necessary columns
        vol_df = vol_df[['SYMBOL', 'VOLATILITY_DAILY']]
        
        # Clean SYMBOL column (remove any whitespace)
        vol_df['SYMBOL'] = vol_df['SYMBOL'].astype(str).str.strip().str.upper()
        
        return vol_df
    else:
        print(f"⚠️ Could not find required columns.")
        print(f"   Symbol column found: {symbol_col}")
        print(f"   Volatility column found: {vol_col}")
        print(f"   Available columns: {list(vol_df.columns)}")
        return None

def calculate_momentum_indicators(df):
    """Calculate multiple momentum indicators from bhavcopy data"""
    
    # Determine column names
    close_col = 'CLOSE_PRICE' if 'CLOSE_PRICE' in df.columns else 'CLOSE'
    prev_close_col = 'PREV_CLOSE' if 'PREV_CLOSE' in df.columns else 'PREVCLOSE'
    open_col = 'OPEN_PRICE' if 'OPEN_PRICE' in df.columns else 'OPEN'
    high_col = 'HIGH_PRICE' if 'HIGH_PRICE' in df.columns else 'HIGH'
    low_col = 'LOW_PRICE' if 'LOW_PRICE' in df.columns else 'LOW'
    vol_col = 'TTL_TRD_QNTY' if 'TTL_TRD_QNTY' in df.columns else 'TOTTRDQTY'
    
    # Clean SYMBOL column for merging
    if 'SYMBOL' in df.columns:
        df['SYMBOL'] = df['SYMBOL'].astype(str).str.strip().str.upper()
    
    # 1. Price momentum
    if prev_close_col in df.columns:
        df['MOMENTUM_PRICE'] = ((df[close_col] - df[prev_close_col]) / df[prev_close_col]) * 100
        print(f"   Price momentum calculated")
    else:
        print("⚠️ No previous close column found")
        df['MOMENTUM_PRICE'] = 0
    
    # 2. Intraday strength
    if open_col in df.columns:
        df['MOMENTUM_INTRADAY'] = ((df[close_col] - df[open_col]) / df[open_col]) * 100
    else:
        df['MOMENTUM_INTRADAY'] = 0
    
    # 3. Range breakout
    if high_col in df.columns and low_col in df.columns:
        df['RANGE'] = df[high_col] - df[low_col]
        df['RANGE_POSITION'] = (df[close_col] - df[low_col]) / df['RANGE'].replace(0, 1)
        df['MOMENTUM_RANGE'] = df['RANGE_POSITION'] * 100
    else:
        df['MOMENTUM_RANGE'] = 50
    
    # 4. Volume momentum
    if vol_col in df.columns:
        median_vol = df[vol_col].median()
        if median_vol > 0:
            df['MOMENTUM_VOLUME'] = (df[vol_col] / median_vol) * 50
        else:
            df['MOMENTUM_VOLUME'] = 50
        df['MOMENTUM_VOLUME'] = df['MOMENTUM_VOLUME'].clip(0, 100)
    else:
        df['MOMENTUM_VOLUME'] = 50
    
    return df

def combine_with_volatility(df, vol_df):
    """Merge momentum scores with daily volatility data"""
    
    if vol_df is not None and 'VOLATILITY_DAILY' in vol_df.columns:
        print(f"   Before merge: equity {len(df)} rows, volatility {len(vol_df)} rows")
        
        # Merge on SYMBOL
        df = df.merge(vol_df, on='SYMBOL', how='left')
        
        print(f"   After merge: {len(df)} rows")
        print(f"   Volatility data present for {df['VOLATILITY_DAILY'].notna().sum()} stocks")
        
        if 'VOLATILITY_DAILY' in df.columns:
            # Fill NaN with 0
            df['VOLATILITY_DAILY'] = df['VOLATILITY_DAILY'].fillna(0)
            
            # Cap at 95th percentile to handle outliers (only for non-zero values)
            non_zero_vol = df[df['VOLATILITY_DAILY'] > 0]['VOLATILITY_DAILY']
            if len(non_zero_vol) > 0:
                max_vol = non_zero_vol.quantile(0.95)
                if max_vol > 0:
                    df['SCORE_VOLATILITY'] = (df['VOLATILITY_DAILY'] / max_vol) * 100
                else:
                    df['SCORE_VOLATILITY'] = 50
            else:
                df['SCORE_VOLATILITY'] = 50
                
            df['SCORE_VOLATILITY'] = df['SCORE_VOLATILITY'].clip(0, 100).fillna(50)
            
            print(f"   Volatility score range: {df['SCORE_VOLATILITY'].min():.1f} - {df['SCORE_VOLATILITY'].max():.1f}")
        else:
            df['SCORE_VOLATILITY'] = 50
    else:
        print("⚠️ No volatility data - using default score 50")
        df['SCORE_VOLATILITY'] = 50
    
    return df

def calculate_final_score(df):
    """
    Final weighted score (0-100)
    """
    weights = {
        'MOMENTUM_PRICE': 0.35,
        'MOMENTUM_INTRADAY': 0.20,
        'MOMENTUM_RANGE': 0.15,
        'MOMENTUM_VOLUME': 0.15,
        'SCORE_VOLATILITY': 0.15
    }
    
    df['FINAL_SCORE'] = 0
    
    for metric, weight in weights.items():
        if metric in df.columns:
            series = df[metric].fillna(0)
            
            # Clip outliers to 1st and 99th percentiles
            q01 = series.quantile(0.01)
            q99 = series.quantile(0.99)
            clipped = series.clip(q01, q99)
            
            min_val = clipped.min()
            max_val = clipped.max()
            
            if max_val > min_val:
                normalized = ((clipped - min_val) / (max_val - min_val)) * 100
                df['FINAL_SCORE'] += normalized * weight
            else:
                df['FINAL_SCORE'] += 50 * weight
    
    # Classify recommendations
    df['RECOMMENDATION'] = pd.cut(
        df['FINAL_SCORE'],
        bins=[0, 20, 40, 60, 75, 101],
        labels=['AVOID', 'WATCH', 'HOLD', 'BUY', 'STRONG_BUY'],
        right=False
    )
    
    return df

def main():
    print("\n" + "="*60)
    print("NSE MOMENTUM SCANNER - Using Daily Volatility (E)")
    print("="*60)
    
    try:
        # Load data
        df = load_equity_bhavcopy()
        if df is None or len(df) == 0:
            print("❌ No equity data loaded")
            return
        
        # Calculate momentum
        df = calculate_momentum_indicators(df)
        
        # Load and merge volatility
        vol_df = load_volatility_data()
        df = combine_with_volatility(df, vol_df)
        
        # Final scoring
        df = calculate_final_score(df)
        
        # Sort by score
        df = df.sort_values('FINAL_SCORE', ascending=False)
        
        # Save all results
        os.makedirs('output', exist_ok=True)
        
        # Select relevant columns for output
        output_columns = ['SYMBOL', 'CLOSE_PRICE', 'MOMENTUM_PRICE', 'MOMENTUM_INTRADAY', 
                          'MOMENTUM_VOLUME', 'VOLATILITY_DAILY', 'FINAL_SCORE', 'RECOMMENDATION']
        
        existing_cols = [col for col in output_columns if col in df.columns]
        df[existing_cols].to_csv('output/all_stocks_ranked.csv', index=False)
        
        # Create watchlist (top 30 from BUY/STRONG_BUY)
        watchlist = df[df['RECOMMENDATION'].isin(['BUY', 'STRONG_BUY'])].head(30)
        if len(watchlist) > 0:
            watchlist[existing_cols].to_csv('output/watchlist.csv', index=False)
        
        # Create top 10 for quick reference
        top10 = df.head(10)[['SYMBOL', 'CLOSE_PRICE', 'MOMENTUM_PRICE', 
                             'VOLATILITY_DAILY', 'FINAL_SCORE', 'RECOMMENDATION']]
        top10.to_csv('output/top_10_momentum.csv', index=False)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 ANALYSIS COMPLETE")
        print("="*60)
        print(f"   Total equity stocks analyzed: {len(df):,}")
        print(f"   STRONG_BUY: {len(df[df['RECOMMENDATION'] == 'STRONG_BUY'])}")
        print(f"   BUY: {len(df[df['RECOMMENDATION'] == 'BUY'])}")
        print(f"   HOLD: {len(df[df['RECOMMENDATION'] == 'HOLD'])}")
        
        if 'VOLATILITY_DAILY' in df.columns and len(df) > 0:
            non_zero_vol = df[df['VOLATILITY_DAILY'] > 0]['VOLATILITY_DAILY']
            if len(non_zero_vol) > 0:
                print(f"\n📈 Volatility Statistics (Daily):")
                print(f"   Mean: {non_zero_vol.mean():.6f}")
                print(f"   Median: {non_zero_vol.median():.6f}")
                print(f"   Max: {non_zero_vol.max():.6f}")
        
        if len(top10) > 0:
            print(f"\n🏆 TOP 5 MOMENTUM STOCKS:")
            print("-" * 60)
            for idx, row in top10.head().iterrows():
                vol_text = f"{row['VOLATILITY_DAILY']:.4f}" if 'VOLATILITY_DAILY' in row else "N/A"
                print(f"   {row['SYMBOL']}: {row['MOMENTUM_PRICE']:+.2f}% (Vol: {vol_text}, Score: {row['FINAL_SCORE']:.0f})")
        
    except Exception as e:
        print(f"❌ Error in calculation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
