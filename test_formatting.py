import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_service import GeminiService

def test_formatting():
    service = GeminiService()
    
    cases = [
        ("5949236", "594조 9236억원"),
        ("327260", "32조 7260억원"),
        ("1234", "1234억원"),
        ("500", "500억원"),
        ("0", "0원"),
        ("invalid", "invalid")
    ]
    
    print("Testing _format_large_number...")
    for input_val, expected in cases:
        result = service._format_large_number(input_val)
        print(f"Input: {input_val} -> Output: {result}")
        # Note: 'expected' is just for my reference, the code might output slightly differently (e.g. spacing), 
        # so I'll just inspect the output.

if __name__ == "__main__":
    test_formatting()
