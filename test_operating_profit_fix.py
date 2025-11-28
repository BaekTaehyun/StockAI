"""
영업이익 표시 수정 확인 테스트
"""

from kis_api import KiwoomApi

def test_operating_profit():
    api = KiwoomApi()
    
    # 액세스 토큰 발급
    if not api.get_access_token():
        print("토큰 발급 실패")
        return
    
    # 삼성전자로 테스트
    code = "005930"
    
    print(f"\n{'='*60}")
    print(f"종목: {code} (삼성전자)")
    print(f"{'='*60}\n")
    
    # 펀더멘털 데이터 조회
    data = api.get_stock_fundamental_info(code)
    
    if data:
        print("펀더멘털 데이터:")
        print("-" * 60)
        print(f"  PER: {data.get('per')}")
        print(f"  PBR: {data.get('pbr')}")
        print(f"  ROE: {data.get('roe')}")
        print(f"\n  시가총액:")
        print(f"    - 원 단위: {data.get('market_cap'):,}원")
        print(f"    - 억 단위: {data.get('market_cap_raw')}")
        print(f"    - 조 억 단위: {data.get('market_cap') / 1000000000000:.1f}조원")
        
        print(f"\n  영업이익:")
        print(f"    - 원 단위: {data.get('operating_profit'):,}원")
        print(f"    - 억 단위 (raw): {data.get('operating_profit_raw')}")
        print(f"    - 조 억 단위: {data.get('operating_profit') / 1000000000000:.1f}조원")
        
        print(f"\n  매출액:")
        print(f"    - 원 단위: {data.get('total_sales'):,}원")
        print(f"    - 억 단위 (raw): {data.get('total_sales_raw')}")
        print(f"    - 조 억 단위: {data.get('total_sales') / 1000000000000:.1f}조원")
        
        print("\n" + "="*60)
        print("UI에 표시될 값 시뮬레이션:")
        print("-" * 60)
        
        # charts.js 로직 시뮬레이션
        operating_profit = data.get('operating_profit', 0)
        if operating_profit:
            op_display = f"{(operating_profit / 100000000):.0f}억원"
        else:
            op_display = "N/A"
        
        market_cap = data.get('market_cap', 0)
        if market_cap:
            mc_display = f"{(market_cap / 100000000):.0f}억원"
        else:
            mc_display = "N/A"
        
        print(f"  시가총액: {mc_display}")
        print(f"  PER: {data.get('per')}")
        print(f"  PBR: {data.get('pbr')}")
        print(f"  ROE: {data.get('roe')}%")
        print(f"  영업이익: {op_display}")
        
    else:
        print("데이터 조회 실패")

if __name__ == '__main__':
    test_operating_profit()
