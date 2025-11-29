"""
테마 API 엔드포인트 테스트
"""
import requests

BASE_URL = "http://localhost:5000"

def test_theme_endpoints():
    print("=== Theme API Endpoint Test ===\n")
    
    # Test 1: 전체 테마 목록
    print("1. GET /api/themes")
    response = requests.get(f"{BASE_URL}/api/themes")
    if response.status_code == 200:
        data = response.json()
        theme_count = data['data'].get('theme_count', 0)
        print(f"   SUCCESS: {theme_count} themes retrieved")
    else:
        print(f"   FAIL: {response.status_code}")
    
    # Test 2: 테마 검색
    print("\n2. GET /api/themes/search?q=2차전지")
    response = requests.get(f"{BASE_URL}/api/themes/search", params={'q': '2차전지'})
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        print(f"   SUCCESS: {len(results)} themes found")
    else:
        print(f"   FAIL: {response.status_code}")
    
    # Test 3: 캐시 갱신 (선택적)
    print("\n3. POST /api/themes/refresh (skipped - no need to refresh)")
    print("   To test: curl -X POST http://localhost:5000/api/themes/refresh")
    
    print("\n=== All Tests Complete ===")

if __name__ == "__main__":
    print("Make sure the server is running on port 5000!")
    print("Starting tests in 3 seconds...\n")
    import time
    time.sleep(3)
    test_theme_endpoints()
