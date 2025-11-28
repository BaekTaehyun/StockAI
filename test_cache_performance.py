import time
from stock_analysis_service import StockAnalysisService
import logging

# 로깅 설정 (시간 측정을 위해)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def test_performance():
    service = StockAnalysisService()
    code = "005930" # 삼성전자
    
    print(f"\n{'='*60}")
    print(f"성능 테스트 시작: {code}")
    print(f"{'='*60}")

    # 1. 첫 번째 호출 (캐시가 없거나 있을 수 있음)
    start_time = time.time()
    print("\n[1차 호출] 시작...")
    result1 = service.get_full_analysis(code, force_refresh=False)
    end_time = time.time()
    
    duration1 = end_time - start_time
    print(f"[1차 호출] 완료: {duration1:.2f}초")
    
    if result1['success']:
        print(f"  - Gemini 캐시 상태 (Outlook): {result1['data']['outlook'].get('_cache_info', 'N/A')}")
    else:
        print(f"  - 실패: {result1.get('message')}")

    # 잠시 대기
    time.sleep(1)

    # 2. 두 번째 호출 (캐시가 확실히 있어야 함)
    start_time = time.time()
    print("\n[2차 호출] 시작 (캐시 활용 기대)...")
    result2 = service.get_full_analysis(code, force_refresh=False)
    end_time = time.time()
    
    duration2 = end_time - start_time
    print(f"[2차 호출] 완료: {duration2:.2f}초")
    
    if result2['success']:
        print(f"  - Gemini 캐시 상태 (Outlook): {result2['data']['outlook'].get('_cache_info', 'N/A')}")
    else:
        print(f"  - 실패: {result2.get('message')}")

    print(f"\n{'='*60}")
    print("결과 분석")
    print(f"{'='*60}")
    print(f"1차 소요 시간: {duration1:.2f}초")
    print(f"2차 소요 시간: {duration2:.2f}초")
    print(f"단축된 시간: {duration1 - duration2:.2f}초")
    
    if duration2 > 2.0:
        print("\n[주의] 2차 호출도 2초 이상 소요됨. 원인 분석 필요:")
        print("1. Kiwoom API 호출 (현재가, 차트, 수급, 펀더멘털)은 캐싱되지 않음")
        print("2. 각 Kiwoom API 호출당 약 0.2~0.5초 소요 예상")
        print("3. 총 4-5번의 Kiwoom API 호출이 매번 발생함")

if __name__ == "__main__":
    test_performance()
