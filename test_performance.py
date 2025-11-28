import time
from stock_analysis_service import StockAnalysisService
from kis_api import KiwoomApi

def test_performance():
    print("=== Performance Test Start ===")
    
    code = "005930" # Samsung Electronics
    kiwoom = KiwoomApi()
    service = StockAnalysisService()
    
    # 1. Measure Fundamental Data Fetching Time
    print("\n[1] Testing Fundamental Data API Latency...")
    start_time = time.time()
    if not kiwoom.access_token:
        kiwoom.get_access_token()
    kiwoom.get_stock_fundamental_info(code)
    end_time = time.time()
    fund_time = end_time - start_time
    print(f"-> Fundamental Data Fetch: {fund_time:.4f} seconds")
    
    # 2. Measure Full Analysis (Cold Start - Force Refresh)
    print("\n[2] Testing Full Analysis (Cold Start - Force Refresh)...")
    start_time = time.time()
    service.get_full_analysis(code, force_refresh=True)
    end_time = time.time()
    cold_time = end_time - start_time
    print(f"-> Cold Start Time: {cold_time:.4f} seconds")
    
    # 3. Measure Full Analysis (Warm Cache)
    print("\n[3] Testing Full Analysis (Warm Cache)...")
    start_time = time.time()
    service.get_full_analysis(code, force_refresh=False)
    end_time = time.time()
    warm_time = end_time - start_time
    print(f"-> Warm Cache Time: {warm_time:.4f} seconds")
    
    print("\n=== Summary ===")
    print(f"Fundamental API: {fund_time:.4f}s")
    print(f"Cold Start (AI + API): {cold_time:.4f}s")
    print(f"Warm Cache: {warm_time:.4f}s")
    
    if warm_time < 0.1:
        print("\n[PASS] Cache is working effectively.")
    else:
        print("\n[WARN] Cache might not be working as expected.")

if __name__ == "__main__":
    test_performance()
