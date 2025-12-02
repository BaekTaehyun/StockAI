from kis_api import KiwoomApi
from technical_indicators import TechnicalIndicators
import json

def test_chart_data():
    kiwoom = KiwoomApi()
    
    # Access Token 확인
    if not kiwoom.access_token:
        print("Getting access token...")
        if not kiwoom.get_access_token():
            print("Failed to get access token")
            return

    code = "005930" # Samsung Electronics
    print(f"Fetching chart data for {code}...")
    
    chart_data = kiwoom.get_daily_chart_data(code)
    
    if not chart_data:
        print("Failed to fetch chart data")
        return
        
    print(f"Got {len(chart_data)} records")
    print("First record sample:", chart_data[0])
    
    # Check keys
    required_keys = ['date', 'close', 'high', 'low', 'volume']
    first_item = chart_data[0]
    missing_keys = [k for k in required_keys if k not in first_item]
    
    if missing_keys:
        print(f"FAIL: Missing keys: {missing_keys}")
    else:
        print("PASS: All required keys present")
        
    # Test Indicator Calculation
    print("Calculating indicators...")
    indicators = TechnicalIndicators.calculate_indicators(chart_data)
    print("Indicators:", json.dumps(indicators, indent=2, ensure_ascii=False))
    
    if indicators['rsi_signal'] == '데이터부족':
        print("FAIL: Indicator calculation returned default values")
    else:
        print("PASS: Indicators calculated successfully")

if __name__ == "__main__":
    test_chart_data()
