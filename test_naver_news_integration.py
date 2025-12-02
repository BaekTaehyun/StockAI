import unittest
from gemini_service import GeminiService
from unittest.mock import MagicMock

class TestNaverNewsIntegration(unittest.TestCase):
    def setUp(self):
        self.service = GeminiService()
        # Mock API call to avoid actual Gemini usage
        self.service._call_gemini_api = MagicMock(return_value="1. 핵심 이슈\n- 테스트 뉴스\n2. 주가 변동\n- 상승\n3. 종합 투자 판단\n- 단기적 관점: 긍정")
        
    def test_search_and_analyze_news(self):
        stock_name = "삼성전자"
        stock_code = "005930"
        
        print(f"\nTesting news analysis for {stock_name} ({stock_code})...")
        result = self.service.search_and_analyze_news(
            stock_name, stock_code, 
            current_price="70000", 
            change_rate="1.5",
            force_refresh=True
        )
        
        print("\n=== Result ===")
        print(result)
        
        # Verify that the prompt contained Naver news
        if self.service._call_gemini_api.called:
            call_args = self.service._call_gemini_api.call_args
            prompt_used = call_args[0][0]
            print("\n=== Prompt Snippet ===")
            print(prompt_used[:1000])
            
            self.assertIn("네이버 금융 최신 뉴스", prompt_used)
        else:
            self.fail("Gemini API was not called")

if __name__ == '__main__':
    unittest.main()
