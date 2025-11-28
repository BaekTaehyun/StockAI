from kis_api import KiwoomApi
import json

def test_api_fields():
    kiwoom = KiwoomApi()
    if not kiwoom.get_access_token():
        print("Auth failed")
        return

    # Samsung Electronics
    code = "005930"
    print(f"Fetching data for {code}...")
    
    # We want to see the raw response of get_current_price to check for PER/PBR
    # Since get_current_price returns a processed dict, we'll mimic its internal call
    
    url = f"{kiwoom.base_url}/api/dostk/stkinfo"
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "api-id": "ka10001",
        "authorization": f"Bearer {kiwoom.access_token}"
    }
    body = {"stk_cd": code}
    
    res = kiwoom._send_request(url, headers, body)
    
    print("\n=== Raw API Response ===")
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_api_fields()
