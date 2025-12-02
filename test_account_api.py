"""
계좌 요약 API 테스트 스크립트
대시보드 요약 정보가 제대로 반환되는지 확인
"""
from kis_api import KiwoomApi

kiwoom = KiwoomApi()

# 토큰 발급
if kiwoom.get_access_token():
    print("✓ 인증 성공\n")
    
    # 계좌 잔고 조회
    balance = kiwoom.get_account_balance()
    
    if balance:
        print("=" * 60)
        print("계좌 요약 정보")
        print("=" * 60)
        print(f"총 매입금액: {int(balance['total_purchase_amount']):,}원")
        print(f"총 평가금액: {int(balance['total_eval_amount']):,}원")
        print(f"총 평가손익: {int(balance['total_profit_loss']):,}원")
        print(f"수익률: {float(balance['total_profit_rate']):.2f}%")
        print(f"보유종목 수: {len(balance['holdings'])}개")
        print("=" * 60)
        
        print("\n✅ API가 정상적으로 데이터를 반환하고 있습니다.")
    else:
        print("❌ 계좌 잔고 조회 실패")
else:
    print("❌ 인증 실패")
