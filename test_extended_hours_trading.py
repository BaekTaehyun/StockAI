"""
시간외 거래 데이터 수집 테스트 스크립트

목적:
1. 현재 ka10001 API의 시간외 거래 데이터 포함 여부 확인
2. 별도 API ID가 있을 경우 테스트
3. 응답 데이터에 장구분 정보 포함 여부 확인

테스트 시간대:
- 장개시전 시간외: 08:30-08:40
- 장종료후 종가매매: 15:40-16:00
- 시간외 단일가: 16:00-18:00
"""

import json
import datetime
from kis_api import KiwoomApi
import requests
import config

def get_current_market_session():
    """현재 시간대가 어느 거래 세션인지 확인"""
    now = datetime.datetime.now()
    current_time = now.time()
    
    # 시간 범위 정의
    pre_market_start = datetime.time(8, 30)
    pre_market_end = datetime.time(8, 40)
    regular_start = datetime.time(9, 0)
    regular_end = datetime.time(15, 30)
    post_close_start = datetime.time(15, 40)
    post_close_end = datetime.time(16, 0)
    after_hours_start = datetime.time(16, 0)
    after_hours_end = datetime.time(18, 0)
    
    if pre_market_start <= current_time <= pre_market_end:
        return "PRE_MARKET", "장개시전 시간외 (08:30-08:40)"
    elif regular_start <= current_time <= regular_end:
        return "REGULAR", "정규 장중 (09:00-15:30)"
    elif post_close_start <= current_time <= post_close_end:
        return "POST_CLOSE", "장종료후 종가매매 (15:40-16:00)"
    elif after_hours_start <= current_time <= after_hours_end:
        return "AFTER_HOURS", "시간외 단일가 (16:00-18:00)"
    else:
        return "CLOSED", "거래 시간 외"

def test_standard_api(stock_code="005930"):
    """기본 ka10001 API 테스트 - 현재 구현"""
    print("=" * 80)
    print("TEST 1: 기본 ka10001 API (현재 구현)")
    print("=" * 80)
    
    api = KiwoomApi()
    result = api.get_current_price(stock_code)
    
    print(f"\n[결과] get_current_price('{stock_code}'):")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

def test_raw_api_response(stock_code="005930"):
    """ka10001 API의 원본 응답 데이터 전체 확인"""
    print("\n" + "=" * 80)
    print("TEST 2: ka10001 원본 응답 데이터 (모든 필드)")
    print("=" * 80)
    
    api = KiwoomApi()
    
    # 토큰 발급
    if not api.access_token:
        api.get_access_token()
    
    # 직접 API 호출
    url = f"{api.base_url}/api/dostk/stkinfo"
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "api-id": "ka10001",
        "authorization": f"Bearer {api.access_token}"
    }
    body = {"stk_cd": stock_code}
    
    try:
        res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
        if res.status_code == 200:
            data = res.json()
            
            print(f"\n[원본 응답 데이터]:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 장구분 관련 필드 찾기
            print("\n[장구분 관련 필드 검색]:")
            market_related_keys = [k for k in data.keys() if any(
                keyword in k.lower() for keyword in ['market', 'session', 'mrkt', 'trde', 'jang', '장']
            )]
            
            if market_related_keys:
                print(f"발견된 필드: {market_related_keys}")
                for key in market_related_keys:
                    print(f"  - {key}: {data[key]}")
            else:
                print("장구분 관련 필드를 찾을 수 없습니다.")
            
            return data
        else:
            print(f"[에러] HTTP {res.status_code}: {res.text}")
            return None
    except Exception as e:
        print(f"[에러] {e}")
        return None

def test_alternative_apis(stock_code="005930"):
    """시간외 거래 관련 가능성 있는 다른 API ID 테스트"""
    print("\n" + "=" * 80)
    print("TEST 3: 대체 API ID 테스트 (시간외 관련 추정)")
    print("=" * 80)
    
    # 추정되는 시간외 관련 API ID 목록
    # OpenAPI+의 opt10087 (시간외 단일가)을 참고하여 유사 패턴 시도
    alternative_apis = [
        ("ka10087", "시간외 단일가 관련 추정"),
        ("ka10002", "호가 조회 (시간외 호가 포함 가능성)"),
        ("ka10003", "체결 조회 (시간외 체결 포함 가능성)"),
    ]
    
    api = KiwoomApi()
    if not api.access_token:
        api.get_access_token()
    
    results = {}
    
    for api_id, description in alternative_apis:
        print(f"\n[테스트] {api_id} - {description}")
        
        url = f"{api.base_url}/api/dostk/stkinfo"
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "api-id": api_id,
            "authorization": f"Bearer {api.access_token}"
        }
        body = {"stk_cd": stock_code}
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
            if res.status_code == 200:
                data = res.json()
                
                # 성공 여부 확인
                if data.get('return_code') == 0:
                    print(f"  ✓ 성공: {api_id}")
                    print(f"  응답 키: {list(data.keys())}")
                    results[api_id] = data
                else:
                    print(f"  ✗ 실패: {data.get('return_msg', 'Unknown error')}")
            else:
                print(f"  ✗ HTTP {res.status_code}")
        except Exception as e:
            print(f"  ✗ 예외: {e}")
    
    return results

def analyze_market_session_data(stock_code="005930"):
    """현재 시장 세션과 API 응답 데이터 분석"""
    print("\n" + "=" * 80)
    print("시간외 거래 데이터 종합 분석")
    print("=" * 80)
    
    # 현재 세션 확인
    session_code, session_name = get_current_market_session()
    now = datetime.datetime.now()
    
    print(f"\n[현재 시간]: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[시장 세션]: {session_name} ({session_code})")
    
    # 세션별 권장 사항
    if session_code == "PRE_MARKET":
        print("\n✓ 현재 장개시전 시간외 거래 시간대입니다.")
        print("  → 장개시전 시간외 가격 데이터가 있어야 합니다.")
    elif session_code == "AFTER_HOURS":
        print("\n✓ 현재 시간외 단일가 거래 시간대입니다.")
        print("  → 시간외 단일가 데이터가 있어야 합니다.")
    elif session_code == "POST_CLOSE":
        print("\n✓ 현재 장종료후 종가매매 시간대입니다.")
        print("  → 당일 종가 기준 거래 데이터가 있어야 합니다.")
    elif session_code == "REGULAR":
        print("\n→ 현재 정규 장중입니다.")
        print("  시간외 데이터는 해당 시간대에만 확인 가능할 수 있습니다.")
    else:
        print("\n→ 현재 거래 시간이 아닙니다.")
        print("  API 응답은 가장 최근 거래 데이터를 반환합니다.")
    
    print("\n" + "-" * 80)

def main():
    """메인 테스트 실행"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "키움 REST API 시간외 거래 데이터 테스트" + " " * 19 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # 테스트 종목 코드
    test_stock = "005930"  # 삼성전자
    
    # 현재 시장 세션 분석
    analyze_market_session_data(test_stock)
    
    # TEST 1: 기본 API
    standard_result = test_standard_api(test_stock)
    
    # TEST 2: 원본 응답 데이터 분석
    raw_result = test_raw_api_response(test_stock)
    
    # TEST 3: 대체 API 테스트
    alternative_results = test_alternative_apis(test_stock)
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)
    
    print("\n1. ka10001 API (현재 구현):")
    if standard_result:
        print(f"   - 종목명: {standard_result.get('name')}")
        print(f"   - 현재가: {standard_result.get('price')}")
        print(f"   - 등락률: {standard_result.get('rate')}%")
    else:
        print("   [실패] 데이터를 가져올 수 없습니다.")
    
    print("\n2. 장구분 필드:")
    if raw_result:
        # 장구분 관련 필드가 있는지 확인
        has_market_session = any(
            key for key in raw_result.keys() 
            if '장' in key or 'market' in key.lower() or 'session' in key.lower()
        )
        if has_market_session:
            print("   ✓ 장구분 관련 필드가 존재합니다.")
        else:
            print("   ✗ 장구분 필드를 찾을 수 없습니다.")
            print("   → ka10001은 시간외 거래를 구분하지 않는 것으로 보입니다.")
    
    print("\n3. 대체 API:")
    if alternative_results:
        print(f"   ✓ {len(alternative_results)}개의 대체 API가 작동합니다:")
        for api_id in alternative_results.keys():
            print(f"   - {api_id}")
    else:
        print("   ✗ 테스트한 대체 API 중 작동하는 것이 없습니다.")
    
    print("\n" + "=" * 80)
    print("권장 사항")
    print("=" * 80)
    
    session_code, _ = get_current_market_session()
    
    if session_code in ["PRE_MARKET", "AFTER_HOURS", "POST_CLOSE"]:
        print("\n✓ 현재 시간외 거래 시간대입니다.")
        print("  1. 위 API 응답에 시간외 가격이 반영되어 있는지 확인하세요.")
        print("  2. HTS에서 같은 시간대 가격과 비교하세요.")
        print("  3. 차이가 있다면 별도 API ID가 필요할 수 있습니다.")
    else:
        print("\n→ 정확한 테스트를 위해 시간외 거래 시간대에 다시 실행하세요:")
        print("  - 장개시전: 08:30-08:40")
        print("  - 장종료후: 15:40-18:00")
    
    print("\n다음 단계:")
    print("  1. '키움 REST API 문서.xlsx' 파일에서 시간외 관련 API 확인")
    print("  2. 키움 개발자 포털에서 공식 문서 확인")
    print("  3. 실시간 WebSocket API 사용 가능 여부 확인")
    
    print("\n")

if __name__ == "__main__":
    main()
