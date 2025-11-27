from kis_api import KiwoomApi
import json
import datetime
import requests

def test_all_chart_dates():
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
    
    # Try different dates
    dates_to_try = [
        "20251126",  # Yesterday
        "20251125",  # 2 days ago
        "20251122",  # Last Friday
        "20251120",  # Last Wednesday
    ]
    
    for date_str in dates_to_try:
        body = {
            "stk_cd": code,
            "base_dt": date_str,
            "tick_range": "1",
            "upd_stkpc_tp": "1"
        }
    
        print(f"\n--- Testing date: {date_str} ---")
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body))
            if res.status_code == 200:
                data = res.json()
                print(f"Return Code: {data.get('return_code')}")
                print(f"Return Msg: {data.get('return_msg')}")
                output = data.get('output', [])
                print(f"Output Length: {len(output)}")
                if output:
                    print(f"SUCCESS! Got {len(output)} records")
                    print(f"First record: {json.dumps(output[0], ensure_ascii=False)}")
                    break
            else:
                print(f"HTTP Error: {res.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_all_chart_dates()
