
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from finviz_market_crawler import FinvizMarketFetcher

def test_finviz():
    print("Initializing FinvizMarketFetcher...")
    fetcher = FinvizMarketFetcher()
    
    print("\n--- Testing get_market_indices ---")
    indices = fetcher.get_market_indices()
    print(f"Result: {indices}")
    
    print("\n--- Testing get_strong_themes ---")
    themes = fetcher.get_strong_themes()
    print(f"Result: {themes}")
    
    print("\n--- Testing get_market_headlines ---")
    headlines = fetcher.get_market_headlines()
    print(f"Result: {headlines[:5]}")

if __name__ == "__main__":
    test_finviz()
