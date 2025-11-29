from theme_service import ThemeService
import json

def test_theme_service():
    """테마 서비스 기능 테스트"""
    
    service = ThemeService()
    
    # Test 1: 캐시 정보 조회
    print("=== Test 1: Cache Info ===")
    info = service.get_cache_info()
    print(json.dumps(info, indent=2, ensure_ascii=False))
    
    # Test 2: 캐시 업데이트
    print("\n=== Test 2: Update Cache ===")
    success = service.update_cache()
    print(f"Update result: {success}")
    
    # Test 3: 테마 목록 조회
    print("\n=== Test 3: Get Themes ===")
    data = service.get_themes()
    print(f"Total themes: {data.get('theme_count')}")
    print(f"Updated at: {data.get('updated_at')}")
    
    if data.get('themes'):
        print(f"First theme: {data['themes'][0].get('thema_nm')} (Code: {data['themes'][0].get('thema_grp_cd')})")
    
    # Test 4: 키워드 검색
    print("\n=== Test 4: Search Theme ===")
    keyword = "2차전지"
    results = service.search_theme(keyword)
    print(f"Search '{keyword}': {len(results)} results")
    
    for theme in results[:3]:
        print(f"  - {theme.get('thema_nm')} (등락률: {theme.get('flu_rt')})")
    
    # Test 5: 다른 키워드 검색
    print("\n=== Test 5: Search Another Keyword ===")
    keyword = "반도체"
    results = service.search_theme(keyword)
    print(f"Search '{keyword}': {len(results)} results")
    
    for theme in results[:3]:
        print(f"  - {theme.get('thema_nm')} (Code: {theme.get('thema_grp_cd')})")

if __name__ == "__main__":
    test_theme_service()
