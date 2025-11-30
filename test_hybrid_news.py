import sys
import os
import time
from gemini_service import GeminiService

def test_hybrid_news_analysis():
    print("=== Testing Hybrid News Analysis (MK Scraper + Google Search) ===")
    
    service = GeminiService()
    stock_name = "삼성전자"
    stock_code = "005930"
    
    # Force refresh to trigger the new logic
    print(f"\nRequesting analysis for {stock_name}...")
    start_time = time.time()
    
    try:
        result = service.search_and_analyze_news(
            stock_name=stock_name, 
            stock_code=stock_code, 
            current_price="70000", 
            change_rate="1.5", 
            force_refresh=True
        )
        
        elapsed = time.time() - start_time
        print(f"\nAnalysis completed in {elapsed:.2f} seconds.")
        
        output_text = f"Analysis completed in {elapsed:.2f} seconds.\n\n"
        output_text += "[Result Summary]\n"
        output_text += f"News Summary: {result.get('news_summary')}\n"
        output_text += f"Reason: {result.get('reason')}\n"
        output_text += f"Sentiment: {result.get('sentiment')}\n\n"
        output_text += "[Raw Response Preview]\n"
        output_text += result.get('raw_response', '')
        
        with open('test_hybrid_result.txt', 'w', encoding='utf-8') as f:
            f.write(output_text)
            
        print("Result saved to test_hybrid_result.txt")
        
    except Exception as e:
        print(f"\n[Error] Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hybrid_news_analysis()
