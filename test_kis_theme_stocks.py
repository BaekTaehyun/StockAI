from kis_api import KiwoomApi
import json

def test_theme_stocks():
    api = KiwoomApi()
    if not api.get_access_token():
        print("Failed to get access token")
        return

    # Use a known theme code from previous test (e.g., 141 for 2차전지 or 280 for whatever that was)
    # Let's try "100" or "141"
    theme_code = "141" 
    
    print(f"\n--- Testing get_theme_stocks (ka90002) for code {theme_code} ---")
    stocks = api.get_theme_stocks(theme_code)
    
    if stocks:
        print(f"Successfully retrieved {len(stocks)} stocks.")
        print(json.dumps(stocks, indent=2, ensure_ascii=False))
    else:
        print("Failed to retrieve theme stocks.")
        
    # Also retry theme list to check encoding
    print("\n--- Retrying Theme List for Encoding Check ---")
    themes = api.get_theme_group_list()
    if themes:
        print("First theme name:", themes[0].get('thema_nm'))

if __name__ == "__main__":
    test_theme_stocks()
