from kis_api import KiwoomApi
import json
import datetime
import requests

def debug_investor_data_v2():
    api = KiwoomApi()
    if not api.get_access_token():
        print("Token generation failed")
        return

    code = "005930"
    url = f"{api.base_url}/api/dostk/stkinfo"
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {api.access_token}",
        "api-id": "ka10059"
    }
    
    # Try trde_tp = 2 (Buy)
    print("\n--- Testing trde_tp=2 (Buy) ---")
    body = {
        "stk_cd": code,
        "dt": datetime.datetime.now().strftime("%Y%m%d"),
        "amt_qty_tp": "1",
        "trde_tp": "2", 
        "unit_tp": "1"
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(body))
        if res.status_code == 200:
            data = res.json()
            print(json.dumps(data.get('stk_invsr_orgn', [])[:1], indent=2, ensure_ascii=False))
        else:
            print(res.text)
    except Exception as e:
        print(e)

    # Try trde_tp = 3 (Sell)
    print("\n--- Testing trde_tp=3 (Sell) ---")
    body["trde_tp"] = "3"
    try:
        res = requests.post(url, headers=headers, data=json.dumps(body))
        if res.status_code == 200:
            data = res.json()
            print(json.dumps(data.get('stk_invsr_orgn', [])[:1], indent=2, ensure_ascii=False))
        else:
            print(res.text)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    debug_investor_data_v2()
