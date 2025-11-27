import requests
import json
import datetime
import config

def test_investor_trading(code="005930"):
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
    
    # 2. Call Investor Trading API
    url = f"{config.BASE_URL}/api/dostk/stkinfo"
    
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {token}",
        "api-id": "ka10059"
    }
    
    body = {
        "stk_cd": code,
        "dt": datetime.datetime.now().strftime("%Y%m%d"),
        "amt_qty_tp": "1",
        "trde_tp": "1",
        "unit_tp": "1"
    }
    
    print(f"Requesting investor data for {code}...")
    res = requests.post(url, headers=headers, data=json.dumps(body))
    
    print(f"Status Code: {res.status_code}")
    print(f"Response Body: {res.text}")
    
    if res.status_code == 200:
        data = res.json()
        output = data.get('output', [])
        if output:
            today = output[0]
            print(f"Date: {today.get('dt')}")
            print(f"Foreign Net: {today.get('frgnr_invsr')} (Expected field)")
            print(f"Institution Net: {today.get('orgn')} (Expected field)")
        else:
            print("No output data")

if __name__ == "__main__":
    print("--- Testing 005930 (Samsung) ---")
    test_investor_trading("005930")
