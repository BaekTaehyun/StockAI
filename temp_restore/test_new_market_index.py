from kis_api import KiwoomApi
import json

def test_new_market_index():
    api = KiwoomApi()
    
    print("Testing KOSPI (001) with new API pattern...")
    kospi = api.get_market_index("001")
    print(f"\nKOSPI Result:")
    print(json.dumps(kospi, indent=2, ensure_ascii=False) if kospi else "None")
    
    print("\n" + "="*60)
    print("Testing KOSDAQ (101) with new API pattern...")
    kosdaq = api.get_market_index("101")
    print(f"\nKOSDAQ Result:")
    print(json.dumps(kosdaq, indent=2, ensure_ascii=False) if kosdaq else "None")

if __name__ == "__main__":
    test_new_market_index()
