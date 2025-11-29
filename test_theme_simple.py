from theme_service import ThemeService

def test_simple():
    """간단한 기능 테스트"""
    service = ThemeService()
    
    # 캐시 업데이트
    print("Updating cache...")
    service.update_cache()
    
    # 테마 개수 확인
    data = service.get_themes()
    print(f"Total themes: {data.get('theme_count')}")
    
    # 검색 테스트
    for keyword in ["2차전지", "반도체", "AI"]:
        results = service.search_theme(keyword)
        print(f"Keyword '{keyword}': {len(results)} themes")
    
    print("SUCCESS")

if __name__ == "__main__":
    test_simple()
