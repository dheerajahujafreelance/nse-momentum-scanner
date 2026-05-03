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
    
    # Use Current Day Underlying Daily Volatility (E)
    vol_col = 'Current Day Underlying Daily Volatility (E)'
    
    if vol_col in vol_df.columns and 'Symbol' in vol_df.columns:
        vol_df = vol_df[['Symbol', vol_col]].rename(columns={'Symbol': 'SYMBOL', vol_col: 'VOLATILITY_DAILY'})
        print(f"   ✅ Using volatility column: '{vol_col}'")
        print(f"   Volatility range: {vol_df['VOLATILITY_DAILY'].min():.4f} - {vol_df['VOLATILITY_DAILY'].max():.4f}")
        return vol_df
    else:
        print(f"⚠️ Expected volatility column not found. Available: {list(vol_df.columns)}")
        return None

def calculate_momentum_indicators(df):
    """Calculate multiple momentum indicators from bhavcopy data"""
    
    # 1. Price momentum (today's close vs previous close)
    if 'PREV_CLOSE' in df.columns:
        df['MOMENTUM_PRICE'] = ((df['CLOSE_PRICE'] - df['PREV_CLOSE']) / df['PREV_CLOSE']) * 100
    elif 'PREVCLOSE' in df.columns:
        df['MOMENTUM_PRICE'] = ((df['CLOSE_PRICE'] - df['PREVCLOSE']) / df['PREVCLOSE']) * 100
    else:
        print("⚠️ No previous close column found")
        df['MOMENTUM_PRICE'] = 0
    
    # 2. Intraday strength (close vs open)
    if 'OPEN_PRICE' in df.columns:
        df['MOMENTUM_INTRADAY'] = ((df['CLOSE_PRICE'] - df['OPEN_PRICE']) / df['OPEN_PRICE']) * 100
    elif 'OPEN' in df.columns:
        df['MOMENTUM_INTRADAY'] = ((df['CLOSE_PRICE'] - df['OPEN']) / df['OPEN']) * 100
    else:
        df['MOMENTUM_INTRADAY'] = 0
    
    # 3. Range breakout (where close sits in today's range)
    high_col = 'HIGH_PRICE' if 'HIGH_PRICE' in df.columns else 'HIGH'
    low_col = 'LOW_PRICE' if 'LOW_PRICE' in df.columns else 'LOW'
    
    if high_col in df.columns and low_col in df.columns:
        df['RANGE'] = df[high_col] - df[low_col]
        df['RANGE_POSITION'] = (df['CLOSE_PRICE'] - df[low_col]) / df['RANGE'].replace(0, 1)
        df['MOMENTUM_RANGE'] = df['RANGE_POSITION'] * 100
    else:
        df['MOMENTUM_RANGE'] = 50
    
    # 4. Volume momentum
    vol_col = 'TTL_TRD_QNTY' if 'TTL_TRD_QNTY' in df.columns else 'TOTTRDQTY'
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
        # Merge on SYMBOL
        df = df.merge(vol_df, on='SYMBOL', how='left')
        
        if 'VOLATILITY_DAILY' in df.columns:
            df['VOLATILITY_DAILY'] = df['VOLATILITY_DAILY'].fillna(0)
            
            # Cap at 95th percentile to handle outliers
            max_vol = df['VOLATILITY_DAILY'].quantile(0.95)
            if max_vol > 0:
                df['SCORE_VOLATILITY'] = (df['VOLATILITY_DAILY'] / max_vol) * 100
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
    Weights optimized for daily momentum trading:
    - Price momentum: 35%
    - Intraday strength: 20%
    - Range breakout: 15%
    - Volume momentum: 15%
    - Daily Volatility (E): 15%
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
    
    # Load data
    df = load_equity_bhavcopy()
    
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
    
    if 'VOLATILITY_DAILY' in df.columns:
        print(f"\n📈 Volatility Statistics (Daily):")
        print(f"   Mean: {df['VOLATILITY_DAILY'].mean():.4f}")
        print(f"   Median: {df['VOLATILITY_DAILY'].median():.4f}")
    
    print(f"\n🏆 TOP 5 MOMENTUM STOCKS:")
    print("-" * 60)
    print(top10.head().to_string(index=False))
    
    return df

if __name__ == "__main__":
    main()
