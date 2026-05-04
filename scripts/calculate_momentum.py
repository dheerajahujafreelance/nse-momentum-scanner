import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

def load_nifty200_bhavcopy():
    """Load Nifty 200 filtered bhavcopy"""
    files = glob.glob('data/filtered/nifty200_bhavcopy_*.csv')
    if not files:
        raise FileNotFoundError("No Nifty 200 bhavcopy found in data/filtered/")
    latest = max(files)
    df = pd.read_csv(latest)
    print(f"📂 Loaded Nifty 200 equity data: {len(df)} stocks")
    return df

def load_volatility_data():
    """Load volatility report and extract daily volatility"""
    files = glob.glob('data/raw/volatility_*.csv')
    if not files:
        print("⚠️ No volatility file found")
        return None
    
    latest = max(files)
    vol_df = pd.read_csv(latest)
    print(f"📂 Loaded volatility data: {len(vol_df)} securities")
    
    # Find volatility column
    vol_col = None
    for col in vol_df.columns:
        if 'Current Day Underlying Daily Volatility' in col:
            vol_col = col
            break
    
    # Find symbol column
    symbol_col = 'Symbol' if 'Symbol' in vol_df.columns else None
    
    if symbol_col and vol_col:
        vol_df = vol_df.rename(columns={symbol_col: 'SYMBOL', vol_col: 'VOLATILITY_DAILY_RAW'})
        vol_df['SYMBOL'] = vol_df['SYMBOL'].astype(str).str.strip().str.upper()
        vol_df['VOLATILITY_DAILY'] = pd.to_numeric(vol_df['VOLATILITY_DAILY_RAW'], errors='coerce')
        vol_df = vol_df.dropna(subset=['VOLATILITY_DAILY'])
        vol_df = vol_df[['SYMBOL', 'VOLATILITY_DAILY']]
        
        print(f"   Volatility range: {vol_df['VOLATILITY_DAILY'].min():.6f} - {vol_df['VOLATILITY_DAILY'].max():.6f}")
        return vol_df
    else:
        print("⚠️ Could not find volatility columns")
        return None

def calculate_momentum_indicators(df):
    """Calculate momentum indicators"""
    
    # Column mappings
    close_col = 'CLOSE_PRICE' if 'CLOSE_PRICE' in df.columns else 'CLOSE'
    prev_close_col = 'PREV_CLOSE' if 'PREV_CLOSE' in df.columns else 'PREVCLOSE'
    open_col = 'OPEN_PRICE' if 'OPEN_PRICE' in df.columns else 'OPEN'
    high_col = 'HIGH_PRICE' if 'HIGH_PRICE' in df.columns else 'HIGH'
    low_col = 'LOW_PRICE' if 'LOW_PRICE' in df.columns else 'LOW'
    vol_col = 'TTL_TRD_QNTY' if 'TTL_TRD_QNTY' in df.columns else 'TOTTRDQTY'
    
    # Clean SYMBOL
    if 'SYMBOL' in df.columns:
        df['SYMBOL'] = df['SYMBOL'].astype(str).str.strip().str.upper()
    
    # Price momentum
    if prev_close_col in df.columns:
        df['MOMENTUM_PRICE'] = ((df[close_col] - df[prev_close_col]) / df[prev_close_col]) * 100
    
    # Intraday strength
    if open_col in df.columns:
        df['MOMENTUM_INTRADAY'] = ((df[close_col] - df[open_col]) / df[open_col]) * 100
    else:
        df['MOMENTUM_INTRADAY'] = 0
    
    # Range breakout
    if high_col in df.columns and low_col in df.columns:
        df['RANGE'] = df[high_col] - df[low_col]
        df['RANGE_POSITION'] = (df[close_col] - df[low_col]) / df['RANGE'].replace(0, 1)
        df['MOMENTUM_RANGE'] = df['RANGE_POSITION'] * 100
    else:
        df['MOMENTUM_RANGE'] = 50
    
    # Volume momentum
    if vol_col in df.columns:
        df[vol_col] = pd.to_numeric(df[vol_col], errors='coerce').fillna(0)
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
    """Merge with volatility data"""
    
    if vol_df is not None:
        df = df.merge(vol_df, on='SYMBOL', how='left')
        df['VOLATILITY_DAILY'] = df['VOLATILITY_DAILY'].fillna(0)
        
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
    else:
        df['SCORE_VOLATILITY'] = 50
        df['VOLATILITY_DAILY'] = 0
    
    return df

def calculate_final_score(df):
    """Calculate weighted final score"""
    
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
            series = pd.to_numeric(df[metric], errors='coerce').fillna(0)
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
    
    df['RECOMMENDATION'] = pd.cut(
        df['FINAL_SCORE'],
        bins=[0, 20, 40, 60, 75, 101],
        labels=['AVOID', 'WATCH', 'HOLD', 'BUY', 'STRONG_BUY'],
        right=False
    )
    
    return df

def main():
    print("\n" + "="*60)
    print("NSE MOMENTUM SCANNER - NIFTY 200 ONLY")
    print("="*60)
    
    try:
        df = load_nifty200_bhavcopy()
        if df is None or len(df) == 0:
            print("❌ No Nifty 200 data loaded")
            return
        
        df = calculate_momentum_indicators(df)
        vol_df = load_volatility_data()
        df = combine_with_volatility(df, vol_df)
        df = calculate_final_score(df)
        df = df.sort_values('FINAL_SCORE', ascending=False)
        
        os.makedirs('output', exist_ok=True)
        
        # Save results
        output_cols = ['SYMBOL', 'CLOSE_PRICE', 'MOMENTUM_PRICE', 'MOMENTUM_INTRADAY', 
                       'MOMENTUM_VOLUME', 'VOLATILITY_DAILY', 'FINAL_SCORE', 'RECOMMENDATION']
        existing_cols = [c for c in output_cols if c in df.columns]
        df[existing_cols].to_csv('output/all_stocks_ranked.csv', index=False)
        
        watchlist = df[df['RECOMMENDATION'].isin(['BUY', 'STRONG_BUY'])].head(30)
        if len(watchlist) > 0:
            watchlist[existing_cols].to_csv('output/watchlist.csv', index=False)
        
        top10 = df.head(10)[['SYMBOL', 'CLOSE_PRICE', 'MOMENTUM_PRICE', 
                             'VOLATILITY_DAILY', 'FINAL_SCORE', 'RECOMMENDATION']]
        top10.to_csv('output/top_10_momentum.csv', index=False)
        
        print("\n" + "="*60)
        print("📊 ANALYSIS COMPLETE")
        print("="*60)
        print(f"   Nifty 200 stocks analyzed: {len(df)}")
        print(f"   STRONG_BUY: {len(df[df['RECOMMENDATION'] == 'STRONG_BUY'])}")
        print(f"   BUY: {len(df[df['RECOMMENDATION'] == 'BUY'])}")
        
        if len(top10) > 0:
            print(f"\n🏆 TOP 5 NIFTY 200 MOMENTUM STOCKS:")
            print("-" * 50)
            for idx, row in top10.head().iterrows():
                print(f"   {row['SYMBOL']}: {row['MOMENTUM_PRICE']:+.2f}% (Score: {row['FINAL_SCORE']:.0f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
