import sys
import io
# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from kis_api import KiwoomApi
import json

print("=" * 60)
print("차트 API 응답 디버깅")
print("=" * 60)

api = KiwoomApi()
api.get_access_token()

code = "005930"
date = "20251122"  # 금요일 지정해서 직접 조회

print(f"\n종목코드: {code}")
print(f"조회 날짜: {date}")
print("\nAPI 호출 중...\n")

# 원시 HTTP 응답 확인을 위해 직접 호출
import requests

url = f"{api.base_url}/api/dostk/chart"
headers = {
    "content-type": "application/json;charset=UTF-8",
    "authorization": f"Bearer {api.access_token}",
    "api-id": "ka10081"
}

body = {
    "stk_cd": code,
    "base_dt": date,
    "tick_range": "1",
    "upd_stkpc_tp": "1"
}

print("요청 URL:", url)
print("요청 헤더:", json.dumps(headers, indent=2, ensure_ascii=False))
print("요청 BODY:", json.dumps(body, indent=2, ensure_ascii=False))
print("\n" + "=" * 60)

res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)

print(f"\n응답 상태 코드: {res.status_code}")
print("응답 헤더:", dict(res.headers))
print("\n응답 BODY:")
print(json.dumps(res.json(), indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("테스트 완료")
