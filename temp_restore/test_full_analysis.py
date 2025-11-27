from stock_analysis_service import StockAnalysisService
import json

def test_full_analysis():
    service = StockAnalysisService()
    
    # Get token first
    if not service.kiwoom.get_access_token():
        print("Failed to get access token")
        return
    
    code = "005930"
    print(f"\n=== Testing Full Analysis for {code} ===\n")
    
    result = service.get_full_analysis(code)
    
    if result.get('success'):
        data = result['data']
        
        print("Stock Info:", data['stock_info'])
        print("\nSupply/Demand:", data['supply_demand'])
        print("\nTechnical Indicators:", data['technical'])
        print("\nNews Analysis:", data['news_analysis'])
        print("\nOutlook:", data['outlook'])
    else:
        print(f"Analysis failed: {result.get('message')}")

if __name__ == "__main__":
    test_full_analysis()
