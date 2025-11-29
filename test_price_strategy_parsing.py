# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_analysis_service import StockAnalysisService

def test_price_strategy():
    service = StockAnalysisService()
    stock_code = "000660"
    
    print(f"\n테스트 종목: {stock_code}\n")
    
    result = service.get_full_analysis(stock_code)
    
    if not result['success']:
        print(f"분석 실패: {result.get('message')}")
        return
    
    data = result['data']
    
    if 'outlook' in data:
        outlook = data['outlook']
        print(f"recommendation: {outlook.get('recommendation')}")
        print(f"confidence: {outlook.get('confidence')}")
        
        if 'price_strategy' in outlook:
            ps = outlook['price_strategy']
            print(f"\n[PRICE STRATEGY]")
            print(f"  entry: {ps.get('entry')}")
            print(f"  target: {ps.get('target')}")
            print(f"  stop_loss: {ps.get('stop_loss')}")
            print("\n[OK] price_strategy exists!")
        else:
            print("\n[ERR] No price_strategy in outlook")
            print(f"outlook keys: {list(outlook.keys())}")
    else:
        print("[ERR] No outlook in data")

if __name__ == "__main__":
    test_price_strategy()
