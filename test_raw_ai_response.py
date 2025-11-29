# -*- coding: utf-8 -*-
import sys
import os
import io

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_analysis_service import StockAnalysisService

def test_raw_response():
    service = StockAnalysisService()
    stock_code = "000660"
    
    print(f"\nTest for: {stock_code}\n")
    
    result = service.get_full_analysis(stock_code, force_refresh=True)
    
    if not result['success']:
        print(f"FAIL: {result.get('message')}")
        return
    
    data = result['data']
    
    if 'outlook' in data:
        outlook = data['outlook']
        raw = outlook.get('raw_response', '')
        
        print("="*60)
        print("RAW AI RESPONSE:")
        print("="*60)
        print(raw)
        print("="*60)
        
        print("\nEXTRACTED DATA:")
        print(f"recommendation: {outlook.get('recommendation')}")
        print(f"confidence: {outlook.get('confidence')}")
        print(f"trading_scenario: {outlook.get('trading_scenario', 'NONE')}")
        print(f"price_strategy: {outlook.get('price_strategy', 'NONE')}")

if __name__ == "__main__":
    test_raw_response()
