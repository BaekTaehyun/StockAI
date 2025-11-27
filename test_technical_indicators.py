import sys
import io
# UTF-8 인코딩 설정 (Windows cp949 환경 대응)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from stock_analysis_service import StockAnalysisService
import json

print("=" * 60)
print("기술적 지표 테스트")
print("=" * 60)

# 삼성전자 종목 코드
code = "005930"
stock_name = "삼성전자"

service = StockAnalysisService()

print(f"\n종목: {stock_name} ({code})")
print("종합 분석 수행 중...\n")

result = service.get_full_analysis(code, stock_name)

if result.get('success'):
    data = result['data']
    technical = data.get('technical', {})
    
    print("=" * 60)
    print("기술적 지표 결과")
    print("=" * 60)
    
    print("\n[RSI - Relative Strength Index]")
    print(f"  RSI 값: {technical.get('rsi', 'N/A')}")
    print(f"  신호: {technical.get('rsi_signal', 'N/A')}")
    print(f"  (정상 범위: 0-100, 70이상=과매수, 30이하=과매도)")
    
    print("\n[MACD - Moving Average Convergence Divergence]")
    print(f"  MACD 값: {technical.get('macd', 'N/A')}")
    print(f"  신호: {technical.get('macd_signal', 'N/A')}")
    print(f"  (양수이면서 증가=상승, 음수이면서 감소=하락)")
    
    print("\n[이동평균선 - Moving Averages]")
    print(f"  MA5 (5일): {technical.get('ma5', 'N/A')}")
    print(f"  MA20 (20일): {technical.get('ma20', 'N/A')}")
    print(f"  MA60 (60일): {technical.get('ma60', 'N/A')}")
    print(f"  신호: {technical.get('ma_signal', 'N/A')}")
    
    print("\n[현재가 정보]")
    stock_info = data.get('stock_info', {})
    print(f"  현재가: {stock_info.get('current_price', 'N/A')}")
    print(f"  변동: {stock_info.get('change', 'N/A')}")
    print(f"  변동률: {stock_info.get('change_rate', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("검증 체크리스트")
    print("=" * 60)
    
    # 검증
    checks = []
    
    rsi_val = technical.get('rsi', 50)
    if rsi_val != 50 and 0 <= rsi_val <= 100:
        checks.append("[OK] RSI 값이 정상 범위 내에 있습니다 (0-100)")
    else:
        checks.append("[ERROR] RSI 값이 비정상입니다 (기본값 50 또는 범위 초과)")
    
    macd_val = technical.get('macd', 0)
    if macd_val != 0:
        checks.append("[OK] MACD 값이 0이 아닙니다 (정상)")
    else:
        checks.append("[WARN] MACD 값이 0입니다 (데이터 확인 필요)")
    
    ma5_val = technical.get('ma5', 0)
    ma20_val = technical.get('ma20', 0)
    ma60_val = technical.get('ma60', 0)
    if ma5_val > 0 and ma20_val > 0 and ma60_val > 0:
        checks.append("[OK] 이동평균선 값이 모두 양수입니다 (정상)")
    else:
        checks.append("[ERROR] 이동평균선 값에 0이 포함되어 있습니다 (비정상)")
    
    for check in checks:
        print(f"  {check}")
    
    print("\n" + "=" * 60)
    
else:
    print(f"\n오류: {result.get('message', '알 수 없는 오류')}")

print("\n테스트 완료\n")
