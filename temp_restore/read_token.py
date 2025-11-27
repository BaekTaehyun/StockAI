import requests
import json
import config

# 접근토큰 발급
def fn_au10001(data):
    # 1. 요청할 API URL
    host = config.BASE_URL # 실전투자/모의투자
    endpoint = '/oauth2/token'
    url =  host + endpoint

    # 2. header 데이터
    headers = {
        'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
    }

    # 3. http POST 요청
    print(f"Requesting to {url} with data: {json.dumps(data, indent=4)}")
    response = requests.post(url, headers=headers, json=data)

    # 4. 응답 상태 코드와 데이터 출력
    print('Code:', response.status_code)
    try:
        # Check for specific headers if they exist, otherwise just print what we have or skip
        header_keys = ['next-key', 'cont-yn', 'api-id']
        header_dict = {key: response.headers.get(key) for key in header_keys if response.headers.get(key)}
        if header_dict:
            print('Header:', json.dumps(header_dict, indent=4, ensure_ascii=False))
        
        print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력
    except Exception as e:
        print('Error parsing response:', e)
        print('Raw Body:', response.text)

# 실행 구간
if __name__ == '__main__':
    # 1. 요청 데이터
    params = {
        'grant_type': 'client_credentials',  # grant_type
        'appkey': config.APP_KEY,  # 앱키
        'secretkey': config.APP_SECRET,  # 시크릿키
    }

    # 2. API 실행
    fn_au10001(data=params)
