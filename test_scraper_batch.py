import sys
import time
from mk_scraper import MKScraper

def test_batch():
    # Test targets: Code -> Name
    targets = {
        "035420": "NAVER",
        "000660": "SK하이닉스",
        "005380": "현대차"
    }
    
    scraper = MKScraper(headless=True)
    results = {}
    
    try:
        for code, name in targets.items():
            print(f"\n{'='*50}")
            print(f"Testing: {name} ({code})")
            print(f"{'='*50}")
            
            start_time = time.time()
            result = scraper.get_ai_answer(name)
            elapsed = time.time() - start_time
            
            if result:
                length = len(result)
                preview = result[:100].replace('\n', ' ')
                print(f"\n[SUCCESS] Length: {length} chars, Time: {elapsed:.2f}s")
                print(f"Preview: {preview}...")
                results[name] = {"status": "success", "length": length, "time": elapsed}
            else:
                print(f"\n[FAILURE] No result found. Time: {elapsed:.2f}s")
                results[name] = {"status": "failure", "length": 0, "time": elapsed}
                
            # Respectful delay between requests
            time.sleep(2)
            
    finally:
        scraper.close()
        
    print("\n" + "="*50)
    print("BATCH TEST SUMMARY")
    print("="*50)
    for name, data in results.items():
        print(f"{name}: {data['status'].upper()} (Len: {data['length']}, Time: {data['time']:.2f}s)")

if __name__ == "__main__":
    test_batch()
