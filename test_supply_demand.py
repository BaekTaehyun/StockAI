from kis_api import KiwoomApi
import json

def test_supply_demand():
    kis = KiwoomApi()
    
    # Ensure token
    if not kis.get_access_token():
        print("Auth failed")
        return

    target_date = "20251128"
    stock_code = "005930" # Samsung Electronics
    
    print(f"Fetching supply/demand for {stock_code} on {target_date}...")
    
    # Fetch data
    result = kis.get_investor_trading(stock_code, date=target_date)
    
    print("\n[Result]")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n[Analysis]")
    print(f"Foreign Net: {result['foreign_net']:,}")
    print(f"Institution Net: {result['institution_net']:,}")
    print(f"Individual Net: {result.get('individual_net', 0):,}")

if __name__ == "__main__":
    test_supply_demand()
