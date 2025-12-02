import sys
import os
import pandas as pd
import json

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kis_api import KiwoomApi

def calculate_bollinger_features(data, window=20, num_std=2):
    df = pd.DataFrame(data)
    cols = ['close', 'open', 'high', 'low', 'volume']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])
    
    df = df.sort_values('date', ascending=True)
    
    df['sma'] = df['close'].rolling(window=window).mean()
    df['std'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['sma'] + (df['std'] * num_std)
    df['lower_band'] = df['sma'] - (df['std'] * num_std)
    
    # Bandwidth for Squeeze detection
    df['bandwidth'] = (df['upper_band'] - df['lower_band']) / df['sma']
    df['min_bandwidth_120'] = df['bandwidth'].rolling(window=120).min()
    df['is_squeeze'] = df['bandwidth'] <= (df['min_bandwidth_120'] * 1.05)
    
    return df

def main():
    api = KiwoomApi()
    code = "005930" # Samsung Electronics
    
    print(f"Fetching data for {code}...")
    daily_data = api.get_daily_chart_data(code)
    
    if not daily_data:
        print("Failed to fetch data.")
        return

    print("Calculating features...")
    df = calculate_bollinger_features(daily_data)
    
    # Take last 200 days for visualization
    df_recent = df.tail(200).copy()
    
    # Prepare JSON data
    chart_data = {
        "dates": df_recent['date'].tolist(),
        "prices": df_recent['close'].tolist(),
        "upper": df_recent['upper_band'].fillna(0).tolist(),
        "middle": df_recent['sma'].fillna(0).tolist(),
        "lower": df_recent['lower_band'].fillna(0).tolist(),
        "is_squeeze": df_recent['is_squeeze'].fillna(False).tolist()
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bollinger_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chart_data, f, ensure_ascii=False)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
