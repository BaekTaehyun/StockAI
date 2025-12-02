from finviz_market_crawler import FinvizMarketFetcher

def test_market_data():
    fetcher = FinvizMarketFetcher()
    
    print("Testing get_market_indices()...")
    indices = fetcher.get_market_indices()
    print(f"Indices: {indices}")
    
    print("\nTesting get_strong_themes()...")
    themes = fetcher.get_strong_themes()
    print(f"Themes: {themes}")

if __name__ == "__main__":
    test_market_data()
