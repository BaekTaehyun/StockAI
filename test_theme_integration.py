"""
AI 분석에서 테마 서비스 통합 테스트
"""
from stock_analysis_service import StockAnalysisService

def test_theme_integration():
    print("=== Testing Theme Service Integration in AI Analysis ===\n")
    
    # StockAnalysisService 인스턴스 생성
    service = StockAnalysisService()
    
    # 테스트 종목들
    test_stocks = [
        ("삼성전자", "005930"),
        ("LG에너지솔루션", "373220"),
    ]
    
    for stock_name, stock_code in test_stocks:
        print(f"\n{'='*60}")
        print(f"Testing: {stock_name} ({stock_code})")
        print(f"{'='*60}")
        
        # 종합 분석 수행 (테마 서비스 사용)
        result = service.get_full_analysis(stock_code, stock_name=stock_name)
        
        if result.get('success'):
            data = result['data']
            stock_info = data.get('stock_info', {})
            
            print(f"\n[Stock Info]")
            print(f"  Name: {stock_info.get('name')}")
            print(f"  Price: {stock_info.get('current_price')}")
            print(f"  Change: {stock_info.get('change_rate')}")
            
            # 여기서 market_data는 분석 내부에서 사용되므로
            # 로그를 통해 테마 정보를 확인
            print(f"\n[*] Check logs above for theme information")
            
        else:
            print(f"[FAIL] {result.get('message')}")
        
        print("\n")

if __name__ == "__main__":
    test_theme_integration()
