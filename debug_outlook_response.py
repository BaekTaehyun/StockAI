"""
카드 상세창 출력 문제 디버깅용 스크립트
실제 outlook 응답 데이터 확인
"""

from gemini_service import GeminiService
from kis_api import KiwoomApi
from technical_indicators import TechnicalIndicators
import json

def debug_outlook(stock_code="005930"):  # 기본값: 삼성전자
    """특정 종목의 outlook 생성 및 파싱 결과 확인"""
    
    print(f"=== 종목 코드: {stock_code} ===\n")
    
    # 1. 필요한 데이터 수집
    kis_api = KiwoomApi()
    gemini = GeminiService()
    
    # 주가 정보
    price_data = kis_api.get_current_price(stock_code)
    if not price_data:
        print("❌ 주가 정보를 가져올 수 없습니다.")
        return
    
    stock_info = {
        'name': price_data.get('hts_kor_isnm', '종목'),
        'code': stock_code,
        'price': int(price_data.get('stck_prpr', 0)),
        'change': int(price_data.get('prdy_vrss', 0)),
        'rate': float(price_data.get('prdy_ctrt', 0))
    }
    print(f"[1] 주가 정보: {stock_info}\n")
    
    # 수급 정보 - stock_analysis_service 사용
    from stock_analysis_service import StockAnalysisService
    analysis_service = StockAnalysisService()
    supply_demand = analysis_service.get_supply_demand_data(stock_code)
    print(f"[2] 수급 정보: {supply_demand}\n")
    
    # 기술적 지표
    chart_data = kis_api.get_daily_chart_data(stock_code)
    technical = TechnicalIndicators.calculate_indicators(chart_data)
    print(f"[3] 기술적 지표: RSI={technical.get('rsi')}, MACD Signal={technical.get('macd_signal')}\n")
    
    # 뉴스 분석
    news_analysis = gemini.search_and_analyze_news(
        stock_name=stock_info.get('name', '종목'),
        stock_code=stock_code,
        current_price=stock_info.get('price'),
        change_rate=stock_info.get('rate')
    )
    print(f"[4] 뉴스 분석: Sentiment={news_analysis.get('sentiment')}\n")
    
    # 2. Outlook 생성
    print("=" * 50)
    print("Outlook 생성 중...")
    print("=" * 50)
    
    outlook = gemini.generate_outlook(
        stock_name=stock_info.get('name'),
        stock_info=stock_info,
        supply_demand=supply_demand,
        technical_indicators=technical,
        news_analysis=news_analysis
    )
    
    # 3. 결과 출력
    print("\n" + "=" * 50)
    print("📊 파싱된 Outlook 결과")
    print("=" * 50)
    
    print(f"\n[투자의견] {outlook.get('recommendation')}")
    print(f"[신뢰도] {outlook.get('confidence')}%")
    
    print(f"\n[핵심 논리]")
    print(f"내용: '{outlook.get('key_logic')}'")
    print(f"길이: {len(outlook.get('key_logic', ''))} 글자")
    print(f"비어있음: {not outlook.get('key_logic')}")
    
    print(f"\n[매매 시나리오]")
    print(f"내용: '{outlook.get('trading_scenario')}'")
    print(f"길이: {len(outlook.get('trading_scenario', ''))} 글자")
    
    print(f"\n[상세 분석]")
    print(f"내용: '{outlook.get('detailed_analysis')}'")
    print(f"길이: {len(outlook.get('detailed_analysis', ''))} 글자")
    print(f"비어있음: {not outlook.get('detailed_analysis')}")
    
    print(f"\n[가격 전략]")
    price_strategy = outlook.get('price_strategy', {})
    print(f"진입: {price_strategy.get('entry')}")
    print(f"목표: {price_strategy.get('target')}")
    print(f"손절: {price_strategy.get('stop_loss')}")
    
    # 4. Raw Response 확인
    print("\n" + "=" * 50)
    print("🔍 AI 원본 응답 (Raw Response)")
    print("=" * 50)
    raw_response = outlook.get('raw_response', '')
    print(raw_response[:1000])  # 처음 1000자만 출력
    if len(raw_response) > 1000:
        print(f"\n... (총 {len(raw_response)} 글자)")
    
    # 5. JSON 출력 (frontend 전송 형태)
    print("\n" + "=" * 50)
    print("📤 Frontend로 전송되는 데이터 (JSON)")
    print("=" * 50)
    
    # raw_response 제외하고 출력
    outlook_for_frontend = {k: v for k, v in outlook.items() if k != 'raw_response'}
    print(json.dumps(outlook_for_frontend, ensure_ascii=False, indent=2))
    
    # 6. 문제 진단
    print("\n" + "=" * 50)
    print("🔧 문제 진단")
    print("=" * 50)
    
    issues = []
    
    if not outlook.get('key_logic'):
        issues.append("❌ key_logic이 비어있습니다.")
    else:
        print("✅ key_logic 정상")
        
    if not outlook.get('detailed_analysis'):
        issues.append("❌ detailed_analysis가 비어있습니다.")
    else:
        print("✅ detailed_analysis 정상")
        
    if not outlook.get('trading_scenario'):
        issues.append("❌ trading_scenario가 비어있습니다.")
    else:
        print("✅ trading_scenario 정상")
    
    if issues:
        print("\n발견된 문제:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n모든 필드가 정상적으로 파싱되었습니다!")


if __name__ == "__main__":
    import sys
    
    # 명령줄 인자로 종목 코드 받기 (기본값: 삼성전자)
    stock_code = sys.argv[1] if len(sys.argv) > 1 else "005930"
    
    debug_outlook(stock_code)
