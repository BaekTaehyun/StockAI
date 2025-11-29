from kis_api import KiwoomApi
import json

def test_theme_api_complete():
    api = KiwoomApi()
    if not api.get_access_token():
        print("Failed to get access token")
        return

    print("\n=== Test 1: Get Theme List ===")
    themes = api.get_theme_group_list()
    if themes:
        print(f"[OK] Retrieved {len(themes)} themes")
        print(f"Sample theme: {themes[0].get('thema_nm')} (Code: {themes[0].get('thema_grp_cd')})")
        
        # Find battery theme
        battery = [t for t in themes if "2차전지" in t.get('thema_nm', '')]
        if battery:
            print(f"[OK] Found '2차전지' theme: {battery[0]}")
    
    print("\n=== Test 2: Get Stocks in Theme (Code 141) ===")
    stocks = api.get_theme_stocks("141")
    if stocks:
        print(f"[OK] Retrieved {len(stocks)} stocks in theme 141")
        print(f"Top 3 stocks:")
        for stock in stocks[:3]:
            print(f"  - {stock.get('stk_nm')} ({stock.get('stk_cd')}) | Price: {stock.get('cur_prc')} | Change: {stock.get('flu_rt')}%")
    else:
        print("[FAIL] Failed to retrieve stocks")

if __name__ == "__main__":
    test_theme_api_complete()
