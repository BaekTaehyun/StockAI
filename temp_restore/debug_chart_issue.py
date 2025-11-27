from kis_api import KiwoomApi
import json

code = "005930"

print("=" * 50)
print("차트 데이터 디버깅")
print("=" * 50)

kiwoom = KiwoomApi()
kiwoom.get_access_token()

print(f"\n종목 코드: {code}")
print("차트 데이터 요청 중...")

chart_data = kiwoom.get_daily_chart_data(code)

print(f"\n반환된 데이터:")
print(f"데이터 타입: {type(chart_data)}")
print(f"데이터 존재 여부: {chart_data is not None}")

if chart_data:
    print(f"데이터 길이: {len(chart_data)}")
    if len(chart_data) > 0:
        print("\n최근 5개 데이터:")
        for i, item in enumerate(chart_data[:5]):
            print(f"\n[{i}] {json.dumps(item, indent=2, ensure_ascii=False)}")
else:
    print("차트 데이터가 None입니다.")
    
print("\n" + "=" * 50)
