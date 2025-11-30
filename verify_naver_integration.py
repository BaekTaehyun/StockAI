from theme_service import ThemeService
import os
import json

def verify_integration():
    print("=== Naver Theme Integration Verification ===")
    
    # 1. Check cache file existence
    cache_file = "static/data/naver_themes_cache.json"
    if os.path.exists(cache_file):
        print(f"✅ Cache file found: {cache_file}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"   - Themes count: {data.get('theme_count')}")
            print(f"   - Updated at: {data.get('updated_at')}")
    else:
        print(f"❌ Cache file NOT found: {cache_file}")
        return

    # 2. Test search functionality (ThemeService should look into both caches)
    service = ThemeService()
    
    # Test case: 삼성전자 (Should be in both Kiwoom and Naver themes)
    stock = "삼성전자"
    print(f"\n🔍 Searching themes for '{stock}'...")
    results = service.find_themes_by_stock(stock)
    
    naver_results = [r for r in results if r.get('source') == 'Naver']
    kiwoom_results = [r for r in results if r.get('source') == 'Kiwoom']
    
    print(f"   - Total matches: {len(results)}")
    print(f"   - Kiwoom matches: {len(kiwoom_results)}")
    print(f"   - Naver matches: {len(naver_results)}")
    
    if naver_results:
        print(f"✅ Successfully found Naver themes for '{stock}'!")
        print(f"   Sample: {naver_results[0]['theme_name']}")
    else:
        print(f"❌ Failed to find Naver themes for '{stock}'.")

if __name__ == "__main__":
    verify_integration()
