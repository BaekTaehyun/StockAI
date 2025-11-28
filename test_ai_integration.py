import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 encoding for stdout to prevent mojibake in Windows terminal
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from stock_analysis_service import StockAnalysisService

def test_ai_integration():
    print("Initializing Service...")
    service = StockAnalysisService()
    
    code = "005930" # Samsung Electronics
    print(f"Analyzing {code} to generate AI prompt...")
    
    # This will trigger get_full_analysis -> gemini.generate_outlook -> print prompt
    result = service.get_full_analysis(code, force_refresh=True)
    
    if result['success']:
        print("\nAnalysis Complete.")
    else:
        print(f"\nAnalysis Failed: {result.get('message')}")

if __name__ == "__main__":
    test_ai_integration()
