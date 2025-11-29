import sys
import os
import time
import datetime
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_service import GeminiService
from stock_analysis_service import StockAnalysisService

def test_cache_sharing():
    print("============================================================")
    print("[TEST] Server-Side Cache Sharing Test")
    print("   Goal: Verify Client 1's request populates cache for Client 2")
    print("============================================================")

    target_code = "005930" # Samsung Electronics
    analysis_type = "outlook"
    
    # 1. Clear Cache
    print("\n[Step 1] Clearing Cache (Clean State)")
    service = GeminiService()
    cache_path = service._get_cache_path(target_code, analysis_type)
    
    if os.path.exists(cache_path):
        os.remove(cache_path)
        print(f"   - Deleted existing cache file: {os.path.basename(cache_path)}")
    else:
        print(f"   - No existing cache file (Already clean)")

    # 2. Client 1 Request
    print("\n[Step 2] Client 1 Request (Expect Cache Miss)")
    print("   - Calling API and generating data... (May take 5-10s)")
    
    client1_service = StockAnalysisService()
    # Force a new GeminiService instance to ensure no memory cache interference from previous steps
    client1_service.gemini = GeminiService() 
    
    start_time = time.time()
    result1 = client1_service.get_full_analysis(target_code)
    duration1 = time.time() - start_time
    
    # Parse Result 1
    if result1.get('success'):
        data1 = result1.get('data', {})
        outlook_data1 = data1.get('outlook', {})
        cache_status1 = outlook_data1.get('_cache_info', {})
        
        print(f"   - Client 1 Duration: {duration1:.2f}s")
        print(f"   - Cache Status: {cache_status1.get('reason', 'N/A')} (Cached: {cache_status1.get('cached', False)})")
        
        if cache_status1.get('cached') is True:
            print("   [WARN] Client 1 hit the cache. Cache clearing might have failed.")
        else:
            print("   [OK] Client 1 generated new data.")
    else:
        print(f"   [FAIL] Client 1 failed: {result1.get('message')}")
        return

    # 3. Verify Cache File
    if os.path.exists(cache_path):
        print(f"   [OK] Cache file created on server. ({os.path.basename(cache_path)})")
    else:
        print(f"   [FAIL] Cache file not created.")

    # 4. Client 2 Request
    print("\n[Step 3] Client 2 Request (Expect Cache Hit)")
    print("   - Requesting same data from a new client instance")
    
    # Completely new service instance
    client2_service = StockAnalysisService()
    client2_service.gemini = GeminiService()
    
    start_time = time.time()
    result2 = client2_service.get_full_analysis(target_code)
    duration2 = time.time() - start_time
    
    # Parse Result 2
    if result2.get('success'):
        data2 = result2.get('data', {})
        outlook_data2 = data2.get('outlook', {})
        cache_status2 = outlook_data2.get('_cache_info', {})
        
        print(f"   - Client 2 Duration: {duration2:.2f}s")
        print(f"   - Cache Status: {cache_status2.get('reason', 'N/A')} (Cached: {cache_status2.get('cached', False)})")
        
        # Threshold: < 5.0s (Kiwoom API calls take ~2-3s, Gemini Cache Hit takes ~0.1s)
        if cache_status2.get('cached') is True and duration2 < 5.0:
            print("   [PASS] Client 2 used server cache and got fast response.")
        else:
            print("   [FAIL] Client 2 did not use cache or was too slow.")
            
        # 5. Data Consistency
        print("\n[Step 4] Verifying Data Consistency")
        outlook_reasoning1 = outlook_data1.get('reasoning', '')[:50]
        outlook_reasoning2 = outlook_data2.get('reasoning', '')[:50]
        
        if outlook_reasoning1 == outlook_reasoning2:
            print("   [PASS] Both clients received identical data.")
        else:
            print("   [FAIL] Data mismatch.")
            print(f"   Client 1: {outlook_reasoning1}...")
            print(f"   Client 2: {outlook_reasoning2}...")
            
    else:
        print(f"   [FAIL] Client 2 failed: {result2.get('message')}")

if __name__ == "__main__":
    test_cache_sharing()
