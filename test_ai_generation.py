import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_service import GeminiService

def test_ai_generation():
    print("=== Testing AI Outlook Generation ===")
    service = GeminiService()
    
    # Mock data
    stock_name = "삼성전자"
    stock_info = {'code': '005930', 'price': 70000, 'rate': 1.5}
    supply_demand = {'foreign_net': 1000, 'institution_net': -500, 'trend': 'foreign_buy'}
    technical_indicators = {
        'rsi': 60, 'rsi_signal': '중립',
        'macd': 100, 'macd_signal': '매수',
        'ma_signal': '정배열'
    }
    news_analysis = {'sentiment': '긍정', 'reason': '반도체 업황 개선 기대'}
    market_data = {'market_index': 'KOSPI 상승', 'themes': '반도체', 'sector': '전기전자'}
    fundamental_data = {'market_cap_raw': '5949236', 'per': 20.3, 'pbr': 1.73, 'roe': 9.0, 'operating_profit_raw': '327260'}
    
    try:
        print("Sending request to Gemini...")
        result = service.generate_outlook(
            stock_name, stock_info, supply_demand, technical_indicators, 
            news_analysis, market_data, fundamental_data, force_refresh=True
        )
        
        print("\n[Result]")
        print(f"Recommendation: {result.get('recommendation')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Scenario: {result.get('trading_scenario')[:50]}...")
        print(f"Reasoning: {result.get('reasoning')[:50]}...")
        
        if result.get('recommendation') in ['매수', '매도', '중립']:
            print("[PASS] Valid recommendation received")
        else:
            print(f"[FAIL] Invalid recommendation: {result.get('recommendation')}")
            
    except Exception as e:
        print(f"[FAIL] Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_generation()
