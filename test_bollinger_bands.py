import sys
import os
import pandas as pd
import numpy as np

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kis_api import KiwoomApi

def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    Calculate Bollinger Bands.
    
    Args:
        data (list): List of dictionaries containing 'close' price.
        window (int): Moving average window size.
        num_std (int): Number of standard deviations.
        
    Returns:
        pd.DataFrame: DataFrame with 'close', 'sma', 'upper_band', 'lower_band'.
    """
    df = pd.DataFrame(data)
    
    # Ensure 'close' is numeric
    df['close'] = pd.to_numeric(df['close'])
    
    # Sort by date ascending for calculation (API returns descending usually)
    df = df.sort_values('date', ascending=True)
    
    # Calculate SMA
    df['sma'] = df['close'].rolling(window=window).mean()
    
    # Calculate Standard Deviation
    df['std'] = df['close'].rolling(window=window).std()
    
    # Calculate Upper and Lower Bands
    df['upper_band'] = df['sma'] + (df['std'] * num_std)
    df['lower_band'] = df['sma'] - (df['std'] * num_std)
    
    return df

def main():
    api = KiwoomApi()
    
    # Samsung Electronics
    code = "005930" 
    
    print(f"Fetching daily chart data for {code}...")
    # Fetch enough data for 20-day MA (e.g., 100 days)
    # Note: get_daily_chart_data usually fetches a fixed amount or has pagination. 
    # Let's see what it returns. The current implementation seems to fetch a default amount.
    daily_data = api.get_daily_chart_data(code)
    
    if not daily_data:
        print("Failed to fetch data.")
        return

    print(f"Fetched {len(daily_data)} records.")
    
    if len(daily_data) < 20:
        print("Not enough data to calculate Bollinger Bands (need at least 20).")
        return

    print("Calculating Bollinger Bands...")
    bb_df = calculate_bollinger_bands(daily_data)
    
    # Show last 5 records (most recent dates)
    # Since we sorted ascending for calculation, the last rows are the most recent.
    print("\nRecent Bollinger Bands Data:")
    print(bb_df[['date', 'close', 'sma', 'upper_band', 'lower_band']].tail())
    
    # Check if calculation is valid (not NaN for recent data)
    last_row = bb_df.iloc[-1]
    if not np.isnan(last_row['upper_band']):
        print("\n[SUCCESS] Bollinger Bands calculated successfully.")
        print(f"Date: {last_row['date']}")
        print(f"Close: {last_row['close']}")
        print(f"Upper: {last_row['upper_band']:.2f}")
        print(f"Middle (SMA): {last_row['sma']:.2f}")
        print(f"Lower: {last_row['lower_band']:.2f}")
    else:
        print("\n[FAIL] Bollinger Bands calculation resulted in NaN for the most recent date.")

if __name__ == "__main__":
    main()
