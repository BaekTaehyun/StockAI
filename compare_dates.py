from kis_api import KiwoomApi
import json
import datetime

def reproduce_issue():
    kis = KiwoomApi()
    
    # Ensure token
    if not kis.get_access_token():
        print("Auth failed")
        return

    # Check Friday
    friday = "20251129"
    stock_code = "005930" # Samsung Electronics
    
    print(f"Fetching supply/demand for {stock_code} on {friday}...")
    
    # Fetch data
    result = kis.get_investor_trading(stock_code, date=friday)
    
    print("\n[Result Friday]")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Check Today (Sunday)
    today = "20251201"
    print(f"\nFetching supply/demand for {stock_code} on {today}...")
    result_today = kis.get_investor_trading(stock_code, date=today)
    print("\n[Result Today]")
    print(json.dumps(result_today, indent=2, ensure_ascii=False))

    if result == result_today:
        print("\n[Conclusion] Data for Today matches Friday (Last Business Day).")
    else:
        print("\n[Conclusion] Data for Today is DIFFERENT from Friday.")

if __name__ == "__main__":
    reproduce_issue()
