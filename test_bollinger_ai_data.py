import sys
import os
import pandas as pd
import numpy as np
import json

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kis_api import KiwoomApi

def calculate_bollinger_features(data, window=20, num_std=2):
    """
    Calculate Bollinger Bands and AI-ready features.
    """
    df = pd.DataFrame(data)
    
    # Ensure numeric
    cols = ['close', 'open', 'high', 'low', 'volume']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])
            
    # Sort by date ascending
    df = df.sort_values('date', ascending=True)
    
    # 1. Standard Bollinger Bands
    df['sma'] = df['close'].rolling(window=window).mean()
    df['std'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['sma'] + (df['std'] * num_std)
    df['lower_band'] = df['sma'] - (df['std'] * num_std)
    
    # 2. Advanced AI Features
    
    # %B (Percent B): Position of price relative to bands
    # 1.0 = Upper Band, 0.0 = Lower Band, 0.5 = SMA
    df['percent_b'] = (df['close'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
    
    # Bandwidth: Width of bands normalized by SMA
    # Lower value = Squeeze (Low Volatility)
    df['bandwidth'] = (df['upper_band'] - df['lower_band']) / df['sma']
    
    # Squeeze Indicator: Is current bandwidth the lowest in last 120 days (approx 6 months)?
    # We use a rolling min on bandwidth
    df['min_bandwidth_120'] = df['bandwidth'].rolling(window=120).min()
    df['is_squeeze'] = df['bandwidth'] <= (df['min_bandwidth_120'] * 1.05) # Within 5% of 6-month low
    
    # Trend: Slope of SMA (vs 5 days ago)
    df['sma_slope'] = df['sma'].diff(periods=5)
    df['trend'] = np.where(df['sma_slope'] > 0, 'upward', np.where(df['sma_slope'] < 0, 'downward', 'flat'))
    
    return df

def generate_ai_context(df, history_days=5):
    """
    Generates a text summary for the AI based on the latest data and recent history.
    """
    latest = df.iloc[-1]
    
    # Extract recent history (last N days)
    history_df = df.tail(history_days).copy()
    history_list = []
    for _, row in history_df.iterrows():
        history_list.append({
            "date": row['date'],
            "price": float(row['close']),
            "percent_b": round(row['percent_b'], 2),
            "bandwidth": round(row['bandwidth'], 4)
        })
    
    context = {
        "date": latest['date'],
        "price": float(latest['close']),
        "bollinger_summary": {
            "upper_band": round(latest['upper_band'], 2),
            "middle_band": round(latest['sma'], 2),
            "lower_band": round(latest['lower_band'], 2),
            "percent_b": round(latest['percent_b'], 4),
            "bandwidth": round(latest['bandwidth'], 4),
            "is_squeeze": bool(latest['is_squeeze']),
            "trend": latest['trend']
        },
        "recent_history": history_list,
        "analysis_hint": ""
    }
    
    # Generate a dynamic hint for the AI
    hints = []
    if latest['percent_b'] > 1.0:
        hints.append("Price has broken ABOVE the upper band (Strong Momentum or Overbought).")
    elif latest['percent_b'] < 0.0:
        hints.append("Price has broken BELOW the lower band (Strong Downtrend or Oversold).")
        
    if latest['is_squeeze']:
        hints.append("Volatility is at a historical low (Squeeze). Watch for a potential explosive breakout.")
        
    if latest['bandwidth'] > df['bandwidth'].mean() * 1.5:
        hints.append("Volatility is very high (Bands are wide).")
        
    # Check for trend in %B (Momentum)
    pb_change = latest['percent_b'] - history_list[0]['percent_b']
    if pb_change > 0.3:
        hints.append("Strong upward momentum in recent days.")
    elif pb_change < -0.3:
        hints.append("Strong downward momentum in recent days.")
        
    context['analysis_hint'] = " ".join(hints)
    
    return context

def main():
    api = KiwoomApi()
    code = "005930" # Samsung Electronics
    
    print(f"Fetching data for {code}...")
    daily_data = api.get_daily_chart_data(code)
    
    if not daily_data or len(daily_data) < 120:
        print("Insufficient data.")
        return

    print("Calculating AI features...")
    df = calculate_bollinger_features(daily_data)
    
    print("\n--- Recent Data (Last 5 Days) ---")
    cols = ['date', 'close', 'percent_b', 'bandwidth', 'is_squeeze', 'trend']
    print(df[cols].tail())
    
    print("\n--- AI Context Output (JSON) ---")
    ai_context = generate_ai_context(df)
    print(json.dumps(ai_context, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
