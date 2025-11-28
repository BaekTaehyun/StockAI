import os
import time
import json
import datetime
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_service import GeminiService

def test_cache_refresh():
    print("=== Testing Cache Expiration and Force Refresh ===")
    service = GeminiService()
    code = "TEST_CODE"
    analysis_type = "test_type"
    
    # 1. Create a dummy cache file (fresh)
    data = {"value": "fresh_data"}
    service._save_to_cache(code, analysis_type, data)
    
    # 2. Load without force refresh (should succeed)
    loaded = service._load_from_cache(code, analysis_type)
    if loaded and loaded['value'] == "fresh_data":
        print("[PASS] Fresh cache loaded successfully")
    else:
        print("[FAIL] Fresh cache load failed")
        
    # 3. Load with force refresh (should return None)
    loaded = service._load_from_cache(code, analysis_type, force_refresh=True)
    if loaded is None:
        print("[PASS] Force refresh ignored cache")
    else:
        print("[FAIL] Force refresh returned data")
        
    # 4. Simulate expired cache (modify mtime to 2 hours ago)
    path = service._get_cache_path(code, analysis_type)
    two_hours_ago = time.time() - 7200
    os.utime(path, (two_hours_ago, two_hours_ago))
    
    # 5. Load expired cache (should return None)
    loaded = service._load_from_cache(code, analysis_type)
    if loaded is None:
        print("[PASS] Expired cache ignored")
    else:
        print("[FAIL] Expired cache returned data")
        
    # Cleanup
    if os.path.exists(path):
        os.remove(path)
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_cache_refresh()
