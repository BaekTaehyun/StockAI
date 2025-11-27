import requests
import json
import datetime
import config

def test_daily_chart(code="005930"):
    # 1. Get Token
    token_url = f"{config.BASE_URL}/oauth2/token"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": config.APP_KEY,
        "secretkey": config.APP_SECRET
    }
    
    print(f"Getting token...")
    res = requests.post(token_url, headers=headers, data=json.dumps(body))
    if res.status_code != 200:
        print(f"Token Error: {res.text}")
        return
        
    token = res.json()['token']
    print(f"Token obtained.")
    
    # 2. Call Daily Chart API
    url = f"{config.BASE_URL}/api/dostk/chart"
    
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {token}",
        "api-id": "ka10081"
    }
    
    date = datetime.datetime.now().strftime("%Y%m%d")
    body = {
        "stk_cd": code,
        "base_dt": date,
        "tick_range": "1",
        "upd_stkpc_tp": "1"
    }
    
    print(f"Requesting daily chart for {code}...")
    res = requests.post(url, headers=headers, data=json.dumps(body))
    
    print(f"Status Code: {res.status_code}")
    # print(f"Response Body: {res.text}")
    
    if res.status_code == 200:
        data = res.json()
        output = data.get('output', [])
        if output:
            print(f"Data count: {len(output)}")
            print(f"First item: {output[0]}")
        else:
            print("No output data")
            print(f"Full Response: {data}")

if __name__ == "__main__":
    test_daily_chart()
