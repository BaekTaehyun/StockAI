import pandas as pd
from technical_indicators import TechnicalIndicators

def test_technical_indicators():
    print("Testing Technical Indicators...")
    
    # Create dummy data (100 days of increasing prices)
    data = []
    for i in range(100):
        data.append({
            'date': f'2023-01-{i+1:02d}' if i < 31 else f'2023-02-{i-30:02d}',
            'close': 1000 + i * 10,
            'high': 1000 + i * 10 + 5,
            'low': 1000 + i * 10 - 5,
            'volume': 1000
        })
    
    # Calculate indicators
    result = TechnicalIndicators.calculate_indicators(data)
    
    print("\nResults:")
    print(f"RSI: {result['rsi']} (Expected: > 50)")
    print(f"MACD: {result['macd']} (Expected: > 0)")
    print(f"MA5: {result['ma5']} (Expected: approx 1980)")
    print(f"MA20: {result['ma20']} (Expected: approx 1905)")
    print(f"MA60: {result['ma60']} (Expected: approx 1705)")
    
    # Check for issues
    issues = []
    if result['macd'] == 0:
        issues.append("MACD is 0")
    if result['ma5'] == 0 or result['ma20'] == 0 or result['ma60'] == 0:
        issues.append("One or more Moving Averages are 0")
        
    if issues:
        print("\n[FAIL] Issues found:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("\n[PASS] Basic indicators seem to be working.")

if __name__ == "__main__":
    test_technical_indicators()
