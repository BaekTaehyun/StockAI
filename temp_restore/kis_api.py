import requests
import json
import datetime
import time
import config

class KiwoomApi:
    def __init__(self):
        self.base_url = config.BASE_URL
        self.app_key = config.APP_KEY
        self.app_secret = config.APP_SECRET
        self.account_no = config.ACCOUNT_NO
        self.access_token = None
        self.token_expired = None

    def get_access_token(self):
        """Issues an OAuth 2.0 Access Token (Kiwoom)."""
        url = f"{self.base_url}/oauth2/token"  # Fixed: /oauth2/token not /oauth2.0/token
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret  # Kiwoom uses 'secretkey', not 'appsecret'
        }

        print(f"[Auth] Requesting token from {url}...")
        res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('return_code') == 0:
                self.access_token = data['token']  # Kiwoom uses 'token', not 'access_token'
                self.token_expired = data.get('expires_dt')
                print(f"[Auth] Token issued successfully. Expires: {self.token_expired}")
                return True
            else:
                print(f"[Auth] Failed: {data.get('return_msg')}")
                return False
        else:
            print(f"[Auth] HTTP Error {res.status_code}: {res.text}")
            return False

    def _clean_code(self, code):
        """종목코드에서 'A' 접두사 제거"""
        if code and isinstance(code, str) and code.startswith('A'):
            return code[1:]
        return code

    def get_current_price(self, code):
        """
        Fetches current price of a stock (Kiwoom ka10001).
        code: Stock code (e.g., "005930")
        """
        if not self.access_token:
            print("[Error] No access token. Call get_access_token() first.")
            return None
            
        code = self._clean_code(code)

        # Kiwoom uses HTTP POST to /api/dostk/stkinfo
        url = f"{self.base_url}/api/dostk/stkinfo"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "ka10001"  # TR code - REQUIRED!
        }
        
        # Request body for ka10001
        body = {
            "stk_cd": code  # Stock code (correct parameter name from Excel docs)
        }

        res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('return_code') == 0:
                # Kiwoom API returns data directly at root level, not nested
                return {
                    "name": data.get('stk_nm', 'Unknown'),
                    "code": code,
                    "price": data.get('cur_prc', 'N/A'),  # 현재가
                    "change": data.get('pred_pre', 'N/A'),  # 전일대비
                    "rate": data.get('flu_rt', 'N/A')  # 등락률
                }
            else:
                print(f"[Error] API Error: {data.get('return_msg')}")
                return None
        else:
            print(f"[Error] HTTP Error {res.status_code}: {res.text}")
            return None

    def get_account_balance(self):
        """
        Fetches account stock holdings (Kiwoom kt00018).
        Returns list of stock holdings.
        """
        if not self.access_token:
            print("[Error] No access token. Call get_access_token() first.")
            return None

        # Kiwoom uses HTTP POST to /api/dostk/acnt
        url = f"{self.base_url}/api/dostk/acnt"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "kt00018"  # TR code for account balance
        }
        
        # Request body for kt00018
        body = {
            "qry_tp": "1",  # 조회구분: 1=수탁잔고
            "dmst_stex_tp": "KRX"  # 국내외구분: KRX=한국거래소
        }

        res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('return_code') == 0:
                # Kiwoom API returns holdings in 'acnt_evlt_remn_indv_tot' array
                holdings = data.get('acnt_evlt_remn_indv_tot', [])
                return {
                    "total_purchase_amount": data.get('tot_pur_amt', '0'),  # 총매입금액
                    "total_eval_amount": data.get('tot_evlt_amt', '0'),  # 총평가금액
                    "total_profit_loss": data.get('tot_evlt_pl', '0'),  # 총평가손익
                    "total_profit_rate": data.get('tot_prft_rt', '0'),  # 총수익률
                    "holdings": holdings
                }
            else:
                print(f"[Error] API Error: {data.get('return_msg')}")
                return None
        else:
            print(f"[Error] HTTP Error {res.status_code}: {res.text}")
            return None

    def get_daily_chart_data(self, code, date=None):
        """
        일봉 차트 데이터 조회 (Kiwoom ka10081)
        Kiwoom API는 base_dt를 무시하고 항상 최근 500일 치 데이터를 반환함
        """
        if not self.access_token:
            print("[Error] No access token. Call get_access_token() first.")
            return None
            
        code = self._clean_code(code)

        url = f"{self.base_url}/api/dostk/chart" 
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "ka10081"
        }
        
        # 단일 시도 (API가 항상 전체 데이터를 반환하므로)
        try_date = date or datetime.datetime.now().strftime("%Y%m%d")
        
        body = {
            "stk_cd": code,
            "base_dt": try_date,
            "tick_range": "1",
            "upd_stkpc_tp": "1" # 수정주가 적용 여부 (1: 적용)
        }

        try:
            print(f"[Chart] Requesting data for {code} (base_dt: {try_date})...")
            res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                
                if data.get('return_code') == 0:
                    # Kiwoom API는 'output' 대신 'stk_dt_pole_chart_qry' 키 사용
                    output = data.get('stk_dt_pole_chart_qry', data.get('output', []))
                    
                    if output:  # 데이터가 있으면 반환
                        print(f"[Chart] ✓ Got {len(output)} records")
                        return output
                    else:
                        print(f"[Chart] ✗ No data available for {code}")
                        return None
                else:
                    print(f"[Chart Error] API Error: {data.get('return_msg')}, Code: {data.get('return_code')}")
                    return None
                print(f"[Chart Error] HTTP {res.status_code}: {res.text[:200]}")
                return None
        except requests.exceptions.Timeout:
            print(f"[Chart Error] Request timeout")
            return None
        except Exception as e:
            print(f"[Chart Error] Connection: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_investor_trading(self, code):
        """
        투자자별 매매동향 조회 (Kiwoom ka10059)
        매수/매도 데이터를 별도로 조회하여 반환
        """
        if not self.access_token:
            print("[Error] No access token. Call get_access_token() first.")
            return None
            
        code = self._clean_code(code)

        url = f"{self.base_url}/api/dostk/stkinfo"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "ka10059"
        }
        
        today_date = datetime.datetime.now().strftime("%Y%m%d")
        
        # 1. 매도 데이터 조회 (trde_tp=3)
        sell_body = {
            "stk_cd": code,
            "dt": today_date,
            "amt_qty_tp": "1", # 금액/수량 구분 (1: 수량, 2: 금액)
            "trde_tp": "3", # 매매구분 (3: 매도)
            "unit_tp": "1" # 단수구분 (1: 1주, 2: 천주)
        }
        
        foreign_sell = 0
        institution_sell = 0
        
        print(f"[Investor] Requesting SELL data for {code}...")
        try:
            res = requests.post(url, headers=headers, data=json.dumps(sell_body), timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get('return_code') == 0:
                    output = data.get('stk_invsr_orgn', [])
                    if output:
                        sell_data = output[0]
                        # 매도 데이터: 음수로 표시되므로 절대값 사용
                        foreign_sell = abs(int(sell_data.get('frgnr_invsr', 0)))
                        institution_sell = abs(int(sell_data.get('orgn', 0)))
        except Exception as e:
            print(f"[Investor Error] Failed to get SELL data: {e}")
        
        # 2. 매수 데이터 조회 (trde_tp=2)
        buy_body = {
            "stk_cd": code,
            "dt": today_date,
            "amt_qty_tp": "1",
            "trde_tp": "2", # 매매구분 (2: 매수)
            "unit_tp": "1"
        }
        
        foreign_buy = 0
        institution_buy = 0
        
        print(f"[Investor] Requesting BUY data for {code}...")
        try:
            res = requests.post(url, headers=headers, data=json.dumps(buy_body), timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get('return_code') == 0:
                    output = data.get('stk_invsr_orgn', [])
                    if output:
                        buy_data = output[0]
                        # 매수 데이터: 음수로 표시되므로 절대값 사용
                        foreign_buy = abs(int(buy_data.get('frgnr_invsr', 0)))
                        institution_buy = abs(int(buy_data.get('orgn', 0)))
        except Exception as e:
            print(f"[Investor Error] Failed to get BUY data: {e}")
        
        # 3. 순매수 계산
        foreign_net = foreign_buy - foreign_sell
        institution_net = institution_buy - institution_sell
        
        return {
            'foreign_buy': foreign_buy,
            'foreign_sell': foreign_sell,
            'foreign_net': foreign_net,
            'institution_buy': institution_buy,
            'institution_sell': institution_sell,
            'institution_net': institution_net
        }

    def _get_empty_investor_data(self):
        return {
            'foreign_buy': 0, 'foreign_sell': 0, 'foreign_net': 0,
            'institution_buy': 0, 'institution_sell': 0, 'institution_net': 0
        }

    def get_market_index(self, market_code):
        """
        시장 지수 조회 (코스피: 001, 코스닥: 101)
        TR: ka20001 (업종기본정보조회)
        """
        if not self.access_token:
            if not self.get_access_token():
                return None

        # 키움 API: /api/dostk/sect + api-id: ka20001
        url = f"{self.base_url}/api/dostk/sect"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "ka20001"  # 업종기본정보조회 TR code
        }

        # 업종코드: 001 = 코스피, 101 = 코스닥
        # mrkt_tp: 0 = 코스피, 1 = 코스닥
        mrkt_tp = "0" if market_code == "001" else "1"
        body = {
            "mrkt_tp": mrkt_tp,
            "inds_cd": market_code
        }

        try:
            res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                if data.get('return_code') == 0 or data.get('cur_prc'):
                    # 키움 API는 결과를 최상위 레벨에 반환
                    return {
                        'price': data.get('cur_prc', '0'),       # 현재가
                        'change': data.get('pred_pre', '0'),     # 전일대비
                        'rate': data.get('flu_rt', '0')          # 등락률
                    }
                else:
                    print(f"[Error] API Error: {data.get('return_msg')}")
                    return None
            else:
                print(f"[Error] HTTP {res.status_code}: {res.text}")
                return None
        except Exception as e:
            print(f"Error fetching market index: {e}")
            return None
