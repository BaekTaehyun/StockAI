from kis_api import KiwoomApi
import json

def inspect_stock_info(code):
    api = KiwoomApi()
    if not api.get_access_token():
        print("Failed to get access token via KiwoomApi")
        return

    # Use the same endpoint as get_current_price but print full response
    url = f"{api.base_url}/api/dostk/stkinfo"
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {api.access_token}",
        "api-id": "ka10001"
    }
    body = {"stk_cd": code}
    
    print(f"Requesting info for {code}...")
    res = api._send_request(url, headers, body)
    
    if res:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Failed to get response")

if __name__ == "__main__":
    inspect_stock_info("005930")
