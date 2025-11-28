import sys
import os
import time

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kis_api import KiwoomApi

def test_fundamental_data():
    api = KiwoomApi()
    
    # Ensure token
    if not api.get_access_token():
        print("Failed to get access token")
        return

    # Test with Samsung Electronics (005930)
    code = "005930"
    print(f"\nFetching fundamental data for {code}...")
    
    data = api.get_stock_fundamental_info(code)
    
    if data:
        print("\n[Fundamental Data]")
        print(f"PER: {data.get('per')}")
        print(f"PBR: {data.get('pbr')}")
        print(f"ROE: {data.get('roe')}")
        print(f"Market Cap (Raw): {data.get('market_cap_raw')}")
        print(f"Market Cap (Calculated): {data.get('market_cap')}")
        print(f"Operating Profit: {data.get('operating_profit')}")
        print(f"Total Sales: {data.get('total_sales')}")
        
        # Validation Logic
        market_cap_raw = data.get('market_cap_raw')
        if market_cap_raw:
            try:
                # Assuming Samsung's market cap is huge, let's see what the raw value is.
                # If it's around 4000000, it might be in 100 millions (억).
                val = float(market_cap_raw)
                print(f"\n[Analysis]")
                print(f"Raw Value: {val}")
                print(f"If unit is '억' (100M): {val * 100000000:,.0f} KRW")
                print(f"If unit is '백만' (1M): {val * 1000000:,.0f} KRW")
                print(f"If unit is '원' (1): {val:,.0f} KRW")
            except:
                print("Raw market cap is not a number.")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    test_fundamental_data()
