
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from stock_analysis_service import StockAnalysisService

def test_service():
    print("Initializing StockAnalysisService...")
    service = StockAnalysisService()
    
    print("\n--- Testing get_full_analysis (lightweight=False) ---")
    # Use a real stock code, e.g., Samsung Electronics (005930)
    # We need to mock KiwoomApi because we don't have real connection in this script
    # But StockAnalysisService initializes KiwoomApi.
    # KiwoomApi might fail if not connected?
    # Let's see if we can run it.
    
    # Mocking KiwoomApi to avoid connection issues
    class MockKiwoom:
        def get_access_token(self): return True
        def get_current_price(self, code): return {'price': '50000', 'rate': '1.0', 'name': 'TestStock'}
        def get_investor_trading(self, code): return {}
        def get_daily_chart_data(self, code): return [{'date': '20240101', 'close': 50000, 'open': 50000, 'high': 51000, 'low': 49000, 'volume': 1000}]
        def get_stock_fundamental_info(self, code): return {}
        def get_market_index(self, code): return {'price': '2500', 'rate': '1.0'}
        
    service.kiwoom = MockKiwoom()
    
    # Force fallback by passing empty global_market_data
    print("Calling get_full_analysis with empty global_market_data...")
    result = service.get_full_analysis("005930", stock_name="Samsung", global_market_data={}, lightweight=False)
    
    if result['success']:
        outlook = result['data']['outlook']
        print(f"\nOutlook Raw Response Snippet: {outlook.get('raw_response')[:100]}...")
        
        # Check market_data in the service (we can't easily access local var, but we can check the prompt if we could)
        # But we can check if 'us_indices' was fetched by checking the logs (stdout)
    else:
        print(f"Analysis failed: {result.get('message')}")

if __name__ == "__main__":
    test_service()
