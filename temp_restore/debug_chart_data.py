from kis_api import KiwoomApi
import json
import datetime
import requests

def debug_chart_data_v2():
    api = KiwoomApi()
    if not api.get_access_token():
        print("Token generation failed")
        return

    code = "005930"
    url = f"{api.base_url}/api/dostk/chart" 
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {api.access_token}",
        "api-id": "ka10081"
    }
    
    body = {
        "stk_cd": code,
        "base_dt": datetime.datetime.now().strftime("%Y%m%d"),
        "tick_range": "1",
        "upd_stkpc_tp": "1"
    }

    print(f"\n--- Requesting Chart Data for {code} ---")
    try:
        res = requests.post(url, headers=headers, data=json.dumps(body))
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("Raw Response Keys:", data.keys())
            print("Return Code:", data.get('return_code'))
            print("Return Msg:", data.get('return_msg'))
            output = data.get('output', [])
            print(f"Output Type: {type(output)}")
            print(f"Output Length: {len(output)}")
            if output:
                print("First Item:", output[0])
            else:
                print("Full Response:", json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_chart_data_v2()
