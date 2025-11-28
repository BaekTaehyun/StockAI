"""
API 응답 필드 확인 테스트
실제 API에서 펀더멘털 데이터 필드명을 확인합니다.
"""

from kis_api import KiwoomApi

def test_api_fields():
    api = KiwoomApi()
    
    # 액세스 토큰 발급
    if not api.get_access_token():
        print("❌ 토큰 발급 실패")
        return
    
    # 삼성전자로 테스트
    code = "005930"
    
    print(f"\n{'='*60}")
    print(f"종목 코드: {code}")
    print(f"{'='*60}\n")
    
    # ka10001 API 호출
    url = f"{api.base_url}/api/dostk/stkinfo"
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "api-id": "ka10001",
        "authorization": f"Bearer {api.access_token}"
    }
    body = {"stk_cd": code}
    
    import requests
    import json
    
    res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
    
    if res.status_code == 200:
        data = res.json()
        
        print("전체 응답 키 목록:")
        print("-" * 60)
        for key in sorted(data.keys()):
            value = data[key]
            # 긴 값은 잘라서 표시
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"  {key}: {value}")
        
        print("\n\n펀더멘털 관련 추정 필드:")
        print("-" * 60)
        
        # 시가총액 관련
        for key in data.keys():
            if 'mac' in key.lower() or 'cap' in key.lower() or 'tot' in key.lower():
                print(f"  [시가총액?] {key}: {data[key]}")
        
        # PER, PBR, ROE 관련
        for key in data.keys():
            if 'per' in key.lower() or 'pbr' in key.lower() or 'roe' in key.lower():
                print(f"  [배율?] {key}: {data[key]}")
        
        # 영업이익 관련
        for key in data.keys():
            if 'bus' in key.lower() or 'op' in key.lower() or 'pro' in key.lower() or 'sal' in key.lower():
                print(f"  [수익?] {key}: {data[key]}")
        
        print("\n\n현재 사용 중인 매핑:")
        print("-" * 60)
        print(f"  per: {data.get('per', 'N/A')}")
        print(f"  pbr: {data.get('pbr', 'N/A')}")
        print(f"  roe: {data.get('roe', 'N/A')}")
        print(f"  mac (시가총액): {data.get('mac', 'N/A')}")
        print(f"  bus_pro (영업이익): {data.get('bus_pro', 'N/A')}")
        print(f"  sale_amt (매출액): {data.get('sale_amt', 'N/A')}")

        
    else:
        print(f"❌ API 오류: {res.status_code}")
        print(res.text)

if __name__ == '__main__':
    test_api_fields()
