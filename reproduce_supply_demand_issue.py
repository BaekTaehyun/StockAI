from kis_api import KiwoomApi
import json
import datetime

def reproduce_issue():
    kis = KiwoomApi()
    
    # Ensure token
    if not kis.get_access_token():
        print("Auth failed")
        return

    # Use today's date
    today = datetime.datetime.now().strftime("%Y%m%d")
    stock_code = "005930" # Samsung Electronics
    
    print(f"Fetching supply/demand for {stock_code} on {today}...")
    
    # Fetch data
    result = kis.get_investor_trading(stock_code, date=today)
    
    print("\n[Result]")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n[Analysis]")
    if result:
        print(f"Foreign Net: {result.get('foreign_net', 0):,}")
        print(f"Institution Net: {result.get('institution_net', 0):,}")
        print(f"Individual Net: {result.get('individual_net', 0):,}")
    else:
        print("No result returned.")

if __name__ == "__main__":
    reproduce_issue()
