
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from stock_analysis_service import StockAnalysisService

def test_refactored_service():
    print("Initializing StockAnalysisService...")
    service = StockAnalysisService()
    
    # Mock KiwoomApi to avoid connection issues during test
    class MockKiwoom:
        def get_access_token(self): return True
        def get_current_price(self, code): return {'price': '50000', 'rate': '1.0', 'name': 'TestStock'}
        def get_investor_trading(self, code): return {}
        def get_daily_chart_data(self, code): return [{'date': '20240101', 'close': 50000, 'open': 50000, 'high': 51000, 'low': 49000, 'volume': 1000}]
        def get_stock_fundamental_info(self, code): return {}
        def get_market_index(self, code): return {'price': '2500', 'rate': '1.0'}
        
    service.kiwoom = MockKiwoom()
    
    # Mock ThemeService to return dummy themes
    class MockThemeService:
        def get_themes(self):
            return {
                'themes': [
                    {'thema_nm': 'ThemeA', 'flu_rt': '2.5'},
                    {'thema_nm': 'ThemeB', 'flu_rt': '1.5'},
                    {'thema_nm': 'ThemeC', 'flu_rt': '0.5'},
                    {'thema_nm': 'ThemeD', 'flu_rt': '-1.0'}
                ]
            }
        def find_themes_by_stock(self, name): return []
            
    service.theme_service = MockThemeService()
    
    print("\n--- Testing get_full_analysis ---")
    # We pass lightweight=True to skip Gemini calls (which we aren't testing here), 
    # BUT wait, the theme logic is inside `if not lightweight`.
    # So we must pass lightweight=False.
    # However, `fetch_news` will try to call Gemini.
    # We should mock GeminiService too to avoid API calls.
    
    class MockGemini:
        def search_and_analyze_news(self, **kwargs):
            return {'news_summary': 'Mock News', 'sentiment': 'Neutral'}
        def fetch_market_themes(self, **kwargs):
            raise Exception("This should NOT be called!")
            
    service.gemini = MockGemini()
    
    result = service.get_full_analysis("005930", stock_name="Samsung", global_market_data={}, lightweight=False)
    
    if result['success']:
        # We can't easily inspect local variables, but we can check if it crashed.
        # And we can verify if the code ran without calling the deleted method.
        print("Analysis successful.")
        # In a real scenario we'd check the prompt or logs, but here success is good enough 
        # to prove the code structure is valid and doesn't call the deleted method.
    else:
        print(f"Analysis failed: {result.get('message')}")

if __name__ == "__main__":
    test_refactored_service()
