from stock_analysis_service import StockAnalysisService
import json

def debug_stock_analysis():
    print("Debugging Stock Analysis Service...")
    service = StockAnalysisService()
    
    # Test with Samsung Electronics (005930)
    code = "005930"
    print(f"\nFetching analysis for {code}...")
    
    result = service.get_full_analysis(code)
    
    if result['success']:
        data = result['data']
        tech = data['technical']
        
        print("\n[Technical Indicators Result]")
        print(json.dumps(tech, indent=2, ensure_ascii=False))
        
        # Check specific values
        print(f"\nRSI: {tech['rsi']}")
        print(f"MACD: {tech['macd']}")
        print(f"MA5: {tech['ma5']}")
        print(f"MA20: {tech['ma20']}")
        print(f"MA60: {tech['ma60']}")
        
        if tech['macd'] == 0:
            print("\n[FAIL] MACD is 0. Likely insufficient data or calculation error.")
        else:
            print("\n[PASS] MACD is non-zero.")
            
    else:
        print(f"\n[FAIL] Analysis failed: {result['message']}")

if __name__ == "__main__":
    debug_stock_analysis()
