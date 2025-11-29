from kis_api import KiwoomApi

def test_theme_api_basic():
    api = KiwoomApi()
    if not api.get_access_token():
        print("Failed to get access token")
        return

    print("Test 1: Get Theme List")
    themes = api.get_theme_group_list()
    if themes:
        print(f"SUCCESS: Retrieved {len(themes)} themes")
        print(f"First theme code: {themes[0].get('thema_grp_cd')}")
    else:
        print("FAIL: Could not retrieve themes")
    
    print("\nTest 2: Get Stocks in Theme 141")
    stocks = api.get_theme_stocks("141")
    if stocks:
        print(f"SUCCESS: Retrieved {len(stocks)} stocks")
        print(f"First stock code: {stocks[0].get('stk_cd')}")
        print(f"First stock price: {stocks[0].get('cur_prc')}")
    else:
        print("FAIL: Could not retrieve stocks")

if __name__ == "__main__":
    test_theme_api_basic()
