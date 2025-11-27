from kis_api import KiwoomApi
import requests
import datetime
import json

def test_index_as_stock():
    api = KiwoomApi()
    if not api.access_token:
        api.get_access_token()
        
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {api.access_token}",
        "appkey": api.app_key,
        "appsecret": api.app_secret,
        "tr_id": "FHKST03010100", # 주식 차트 TR
        "custtype": "P"
    }
    
    # URL: 주식기간별시세 (기존에 잘 동작하는 API)
    url = f"{api.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
    
    today = datetime.datetime.now().strftime("%Y%m%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y%m%d")
    
    print(f"Testing Stock Chart API for KOSPI (0001)...")
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": "0001",
        "fid_input_date_1": start_date,
        "fid_input_date_2": today,
        "fid_period_div_code": "D",
        "fid_org_adj_prc": "0"
    }
    
    try:
        res = requests.get(url, headers=headers, params=params)
        print(f"Status: {res.status_code}")
        print(f"Body: {res.text[:500]}")
        
        if res.status_code == 200:
            data = res.json()
            if data['rt_cd'] == '0':
                print("\nSuccess! Data found.")
                if data.get('output2'):
                    print(f"Latest: {data['output2'][0]}")
            else:
                print(f"Failed: {data.get('msg1')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_index_as_stock()
