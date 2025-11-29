from theme_service import ThemeService

def test_stock_theme_search():
    """주식 이름으로 테마 검색 테스트"""
    
    service = ThemeService()
    
    # 테스트할 주식 이름들
    test_stocks = [
        "삼성전자",
        "LG에너지솔루션", 
        "SK하이닉스"
    ]
    
    for stock_name in test_stocks:
        print(f"\n{'='*60}")
        results = service.find_themes_by_stock(stock_name)
        print(f"{'='*60}")
        
        if results:
            print(f"\n[RESULT] 주식 '{stock_name}'이(가) 속한 테마: {len(results)}개")
            for r in results:
                print(f"  - [{r['theme_name']}] 등락률: {r['theme_fluctuation']}")
        else:
            print(f"\n[RESULT] 주식 '{stock_name}'에 대한 테마를 찾을 수 없습니다.")

if __name__ == "__main__":
    test_stock_theme_search()
