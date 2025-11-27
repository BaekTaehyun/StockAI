from kis_api import KiwoomApi
import json
import requests

def test_market_index_daily():
    api = KiwoomApi()
    if not api.access_token:
        api.get_access_token()
        
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {api.access_token}",
        "appkey": api.app_key,
        "appsecret": api.app_secret,
        "tr_id": "FHKUP03500100",
        "custtype": "P"
    }
    
    # URL 변경: 업종기간별시세
    url = f"{api.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-index-chartprice"
    
    print(f"\nTesting URL: {url}")
    params = {
        "fid_cond_mrkt_div_code": "U",
        "fid_input_iscd": "0001", # KOSPI
        "fid_period_div_code": "D", # 일별
        "fid_org_adj_prc": "0" # 수정주가 미반영
    }
    
    try:
        res = requests.get(url, headers=headers, params=params)
        print(f"Status: {res.status_code}")
        print(f"Body: {res.text}")
        
        if res.status_code == 200:
            data = res.json()
            if data['rt_cd'] == '0':
                print("Success!")
                # 첫 번째 데이터(최신) 출력
                if data['output2']:
                    print(f"Latest Data: {data['output2'][0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_market_index_daily()
