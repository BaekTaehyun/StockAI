from kis_api import KiwoomApi
import json

def test_api():
    print("=== Kiwoom API Test Start ===")
    kiwoom = KiwoomApi()

    # 1. Authentication
    print("\n[1] Testing Authentication...")
    if kiwoom.get_access_token():
        print("Success!")
    else:
        print("Failed!")
        return

    # 2. Stock Price (Samsung Electronics: 005930)
    print("\n[2] Testing Stock Price (005930)...")
    price_info = kiwoom.get_current_price("005930")
    if price_info:
        print(json.dumps(price_info, indent=2, ensure_ascii=False))
    else:
        print("Failed to get price info.")

    # 3. Account Balance
    print("\n[3] Testing Account Balance...")
    balance = kiwoom.get_account_balance()
    if balance:
        print(json.dumps(balance, indent=2, ensure_ascii=False))
    else:
        print("Failed to get account balance.")

    print("\n=== Kiwoom API Test End ===")

if __name__ == "__main__":
    test_api()
