from kis_api import KiwoomApi
import config

def main():
    print("=== Kiwoom REST API Client ===")
    
    # 1. Initialize API
    kiwoom = KiwoomApi()
    
    # 2. Authenticate
    if not kiwoom.get_access_token():
        print("[Error] Authentication failed. Please check your AppKey and SecretKey in config.py")
        return

    # 3. Test: Get Price of Samsung Electronics (005930)
    code = "005930"
    print(f"\n[Test] Fetching price for {code}...")
    
    price_info = kiwoom.get_current_price(code)
    if price_info:
        print(f"Code: {price_info['code']}")
        print(f"Price: {price_info['price']} KRW")
        print(f"Change: {price_info['change']} ({price_info['rate']}%)")
    else:
        print("[Error] Failed to fetch price.")
    
    # 4. 계좌 잔고 조회 테스트
    print(f"\n[Test] Fetching account balance...")
    balance = kiwoom.get_account_balance()
    if balance:
        print(f"\n총매입금액: {balance['total_purchase_amount']} 원")
        print(f"총평가금액: {balance['total_eval_amount']} 원")
        print(f"총평가손익: {balance['total_profit_loss']} 원")
        print(f"총수익률: {balance['total_profit_rate']}%")
        print(f"\n보유종목 ({len(balance['holdings'])}개):")
        for stock in balance['holdings']:
            print(f"\n  종목명: {stock.get('stk_nm', 'N/A')}")
            print(f"  종목코드: {stock.get('stk_cd', 'N/A')}")
            print(f"  보유수량: {stock.get('rmnd_qty', '0')} 주")
            print(f"  매입가: {stock.get('pur_pric', '0')} 원")
            print(f"  현재가: {stock.get('cur_prc', '0')} 원")
            print(f"  평가손익: {stock.get('evltv_prft', '0')} 원 ({stock.get('prft_rt', '0')}%)")
    else:
        print("[Error] Failed to fetch account balance.")

if __name__ == "__main__":
    main()
