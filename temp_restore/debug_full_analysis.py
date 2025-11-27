from stock_analysis_service import StockAnalysisService
from kis_api import KiwoomApi
import json

def debug_analysis(code="A000660"):
    print(f"--- Debugging Analysis for {code} ---")
    
    # 1. Initialize Service
    service = StockAnalysisService()
    
    # 2. Test Kiwoom API directly first
    print("\n[1] Testing KiwoomApi directly...")
    kiwoom = KiwoomApi()
    if not kiwoom.get_access_token():
        print("Auth failed")
        return

    # Test Investor Trading
    print(f"\n[1.1] Investor Trading (ka10059) for {code}")
    investor_data = kiwoom.get_investor_trading(code)
    print(f"Result: {json.dumps(investor_data, indent=2, ensure_ascii=False)}")

    # Test Daily Chart
    print(f"\n[1.2] Daily Chart (ka10081) for {code}")
    chart_data = kiwoom.get_daily_chart_data(code)
    if chart_data:
        print(f"Result count: {len(chart_data)}")
        print(f"First item: {chart_data[0]}")
    else:
        print("Result: None or Empty")

    # 3. Test Full Analysis Service
    print("\n[2] Testing StockAnalysisService...")
    # Inject the authenticated kiwoom instance
    service.kiwoom = kiwoom
    
    # Test Supply/Demand wrapper
    print(f"\n[2.1] get_supply_demand_data({code})")
    sd_data = service.get_supply_demand_data(code)
    print(f"Result: {json.dumps(sd_data, indent=2, ensure_ascii=False)}")
    
    # Test Full Analysis
    print(f"\n[2.2] get_full_analysis({code})")
    full_data = service.get_full_analysis(code)
    
    if full_data['success']:
        tech = full_data['data']['technical']
        print(f"\nTechnical Indicators:")
        print(f"RSI: {tech.get('rsi')}")
        print(f"MACD: {tech.get('macd')}")
        print(f"MA5: {tech.get('ma5')}")
    else:
        print(f"Analysis Failed: {full_data.get('message')}")

if __name__ == "__main__":
    debug_analysis("A000660")
