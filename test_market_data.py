import sys
import os
from stock_analysis_service import StockAnalysisService
from gemini_service import GeminiService

def test_market_data():
    print("=== 시장 데이터 수집 테스트 ===")
    
    # 1. 시장 지수 테스트
    print("\n1. 시장 지수 (Kiwoom API)")
    try:
        service = StockAnalysisService()
        indices = service._get_market_indices_string()
        print(f"Result: {indices}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. 테마 검색 테스트
    print("\n2. 주도 테마 (Gemini Search)")
    try:
        gemini = GeminiService()
        themes = gemini.fetch_market_themes()
        print(f"Result: {themes}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. 섹터 검색 테스트
    print("\n3. 종목 섹터 (Gemini Search - 삼성전자)")
    try:
        sector = gemini.fetch_stock_sector("삼성전자", "005930")
        print(f"Result: {sector}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_market_data()
