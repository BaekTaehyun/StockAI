from kis_api import KiwoomApi
from stock_analysis_service import StockAnalysisService
import json

# 삼성전자 종목 코드
code = "005930"

print("=" * 50)
print("수급 및 기술적 분석 테스트")
print("=" * 50)

# 1. KIS API 수급 데이터 테스트
print("\n[1] 수급 데이터 테스트")
print("-" * 50)
kiwoom = KiwoomApi()
kiwoom.get_access_token()

investor_data = kiwoom.get_investor_trading(code)
if investor_data:
    print("[OK] 수급 데이터 조회 성공:")
    print(f"  외국인 매수: {investor_data['foreign_buy']:,}주")
    print(f"  외국인 매도: {investor_data['foreign_sell']:,}주")
    print(f"  외국인 순매수: {investor_data['foreign_net']:,}주")
    print(f"  기관 매수: {investor_data['institution_buy']:,}주")
    print(f"  기관 매도: {investor_data['institution_sell']:,}주")
    print(f"  기관 순매수: {investor_data['institution_net']:,}주")
else:
    print("[ERROR] 수급 데이터 조회 실패")

# 2. 차트 데이터 테스트
print("\n[2] 차트 데이터 테스트")
print("-" * 50)
chart_data = kiwoom.get_daily_chart_data(code)
if chart_data and len(chart_data) > 0:
    print(f"[OK] 일봉 데이터 조회 성공: {len(chart_data)}일치")
    recent = chart_data[0]
    print(f"  최근일자: {recent.get('dt')}")
    print(f"  종가: {recent.get('cur_prc')}")
    print(f"  고가: {recent.get('high_pric')}")
    print(f"  저가: {recent.get('low_pric')}")
    print(f"  거래량: {recent.get('trde_qty')}")
else:
    print("[ERROR] 차트 데이터 조회 실패")

# 3. 종합 분석 테스트
print("\n[3] 종합 분석 테스트")
print("-" * 50)
service = StockAnalysisService()
analysis = service.get_full_analysis(code, "삼성전자")

if analysis.get('success'):
    data = analysis['data']
    
    # 수급 정보
    supply = data['supply_demand']
    print("\n[OK] 수급 분석:")
    print(f"  외국인 매수: {supply['foreign_buy']:,}주")
    print(f"  외국인 매도: {supply['foreign_sell']:,}주")
    print(f"  외국인 순매수: {supply['foreign_net']:,}주")
    print(f"  기관 매수: {supply['institution_buy']:,}주")
    print(f"  기관 매도: {supply['institution_sell']:,}주")
    print(f"  기관 순매수: {supply['institution_net']:,}주")
    print(f"  수급 트렌드: {supply['trend']}")
    
    # 기술적 지표
    tech = data['technical']
    print("\n[OK] 기술적 지표:")
    print(f"  RSI: {tech['rsi']} ({tech['rsi_signal']})")
    print(f"  MACD: {tech['macd']} ({tech['macd_signal']})")
    print(f"  5일 이동평균: {tech['ma5']:,.2f}원")
    print(f"  20일 이동평균: {tech['ma20']:,.2f}원")
    print(f"  60일 이동평균: {tech['ma60']:,.2f}원")
    print(f"  이동평균 신호: {tech['ma_signal']}")
else:
    print(f"[ERROR] 종합 분석 실패: {analysis.get('message')}")

print("\n" + "=" * 50)
print("테스트 완료")
print("=" * 50)
