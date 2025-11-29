"""
테마 등락률 포함 테스트
"""
from stock_analysis_service import StockAnalysisService

def test_theme_with_fluctuation():
    print("=== Testing Theme with Fluctuation Rate ===\n")
    
    service = StockAnalysisService()
    
    # 테스트: 삼성전자
    stock_name = "삼성전자"
    stock_code = "005930"
    
    print(f"Analyzing: {stock_name} ({stock_code})")
    print("-" * 60)
    
    result = service.get_full_analysis(stock_code, stock_name=stock_name)
    
    if result.get('success'):
        print("\n[SUCCESS] Analysis completed!")
        print("\nCheck logs above for:")
        print("  1. Theme matching with stock name")
        print("  2. Theme fluctuation rates")
        print("  3. Final theme string passed to AI")
    else:
        print(f"\n[FAIL] {result.get('message')}")

if __name__ == "__main__":
    test_theme_with_fluctuation()
