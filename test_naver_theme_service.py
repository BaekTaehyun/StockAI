from theme_service import NaverThemeScraper

def test_naver_scraper():
    print("=== NaverThemeScraper Test ===")
    
    # Test 1: 방위산업
    keyword = "방위산업"
    print(f"\n🔍 Testing keyword: {keyword}")
    stocks = NaverThemeScraper.get_theme_stocks(keyword)
    
    if stocks:
        print(f"✅ Success! Found {len(stocks)} stocks.")
        print("Sample stocks:")
        for s in stocks[:5]:
            print(f"  - [{s['code']}] {s['name']}")
    else:
        print("❌ Failed to find stocks.")

    # Test 2: 반도체
    keyword = "반도체"
    print(f"\n🔍 Testing keyword: {keyword}")
    stocks = NaverThemeScraper.get_theme_stocks(keyword)
    
    if stocks:
        print(f"✅ Success! Found {len(stocks)} stocks.")
        print("Sample stocks:")
        for s in stocks[:5]:
            print(f"  - [{s['code']}] {s['name']}")
    else:
        print("❌ Failed to find stocks.")
        
    # Test 3: Non-existent theme
    keyword = "없는테마123"
    print(f"\n🔍 Testing non-existent keyword: {keyword}")
    stocks = NaverThemeScraper.get_theme_stocks(keyword)
    if not stocks:
        print("✅ Correctly returned empty list for non-existent theme.")
    else:
        print(f"❌ Unexpectedly found stocks: {len(stocks)}")

if __name__ == "__main__":
    test_naver_scraper()
