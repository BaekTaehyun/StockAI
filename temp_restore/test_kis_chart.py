import sys
import io
# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from kis_api import KiwoomApi
import json

print("=" * 60)
print("API 응답 비교 테스트")
print("=" * 60)

api = KiwoomApi()
api.get_access_token()

code = "005930"

print(f"\n1. get_daily_chart_data() 함수 직접 호출:")
print("-" * 60)
result = api.get_daily_chart_data(code)
if result:
    print(f"✓ 데이터 개수: {len(result)}")
    print(f"✓ 첫 번째 레코드: {result[0]}")
    print(f"✓ 마지막 레코드: {result[-1]}")
else:
    print("✗ 데이터 없음 (None)")

print("\n" + "=" * 60)
print("테스트 완료")
