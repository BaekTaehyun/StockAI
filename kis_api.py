"""
키움증권 REST API 클라이언트
================================================================
키움증권 개발자 센터의 REST API를 Python으로 래핑한 클라이언트입니다.

주요 기능:
- OAuth 2.0 인증 토큰 발급 및 관리
- 현재가 조회 (get_current_price)
- 계좌 잔고 조회 (get_account_balance)
- 일봉 차트 데이터 조회 (get_daily_chart_data)
- 투자자별 매매 동향 조회 (get_investor_trading)
- 시장 지수 조회 (get_market_index)

API 문서: https://www.kiwoom.com/
================================================================
"""
import requests
import json
import datetime
import time
import config

class KiwoomApi:
    """키움 REST API 클라이언트 클래스"""
    
    def __init__(self):
        """API 클라이언트 초기화 - config.py에서 설정 값 로드"""
        self.base_url = config.BASE_URL
        self.app_key = config.APP_KEY
        self.app_secret = config.APP_SECRET
        self.account_no = config.ACCOUNT_NO
        self.access_token = None  # OAuth 토큰 (get_access_token으로 발급)
        self.token_expired = None  # 토큰 만료 시간

    def get_access_token(self):
        """Issues an OAuth 2.0 Access Token (Kiwoom)."""
        url = f"{self.base_url}/oauth2/token"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret
        }

        print(f"[Auth] Requesting token from {url}...")
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                # API 문서에 따라 성공 여부 확인 (보통 return_code 사용 안할 수도 있음, 토큰 존재 여부 확인)
                if 'token' in data or 'access_token' in data:
                    self.access_token = data.get('token') or data.get('access_token')
                    self.token_expired = data.get('expires_dt') or data.get('expires_in')
                    print(f"[Auth] Token issued successfully. Expires: {self.token_expired}")
                    return True
                elif data.get('return_code') == 0: # 기존 로직 유지
                    self.access_token = data.get('token')
                    self.token_expired = data.get('expires_dt')
                    print(f"[Auth] Token issued successfully. Expires: {self.token_expired}")
                    return True
                else:
                    print(f"[Auth] Failed: {data.get('return_msg')}")
                    return False
            else:
                print(f"[Auth] HTTP Error {res.status_code}: {res.text}")
                return False
        except Exception as e:
            print(f"[Auth] Connection Error: {e}")
            return False

    def _send_request(self, url, headers, body=None, method='POST'):
        """
        API 요청을 보내고 토큰 만료(8005) 시 자동 갱신 및 재시도하는 헬퍼 메소드
        """
        # 1. 토큰이 없으면 발급 시도
        if not self.access_token:
            print("[API] No token found. Requesting new token...")
            if not self.get_access_token():
                return None

        # 헤더에 최신 토큰 적용
        headers["authorization"] = f"Bearer {self.access_token}"

        try:
            if method == 'POST':
                res = requests.post(url, headers=headers, data=json.dumps(body) if body else None, timeout=10)
            else:
                res = requests.get(url, headers=headers, timeout=10)

            if res.status_code == 200:
                data = res.json()
                
                # 토큰 만료/유효하지 않음 에러 체크 (8005 등)
                msg = data.get('return_msg', '')
                code = data.get('return_code')
                
                # 에러 코드가 있고, 메시지에 'Token'이나 '8005'가 포함된 경우
                if code is not None and str(code) != '0' and ('Token' in msg or '8005' in str(code) or '인증' in msg):
                    print(f"[API] Token invalid ({msg}). Refreshing token and retrying...")
                    
                    # 토큰 재발급
                    if self.get_access_token():
                        # 헤더 업데이트 및 재시도
                        headers["authorization"] = f"Bearer {self.access_token}"
                        if method == 'POST':
                            res = requests.post(url, headers=headers, data=json.dumps(body) if body else None, timeout=10)
                        else:
                            res = requests.get(url, headers=headers, timeout=10)
                            
                        if res.status_code == 200:
                            return res.json()
                    else:
                        print("[API] Failed to refresh token.")
                        return None
                
                return data
            
            # 401 Unauthorized 처리
            elif res.status_code == 401:
                print(f"[API] HTTP 401 Unauthorized. Refreshing token...")
                if self.get_access_token():
                    headers["authorization"] = f"Bearer {self.access_token}"
                    if method == 'POST':
                        res = requests.post(url, headers=headers, data=json.dumps(body) if body else None, timeout=10)
                    else:
                        res = requests.get(url, headers=headers, timeout=10)
                    
                    if res.status_code == 200:
                        return res.json()

            else:
                print(f"[API] HTTP Error {res.status_code}: {res.text}")
                return None

        except Exception as e:
            print(f"[API] Request Error: {e}")
            return None

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
        code = self._clean_code(code)
        url = f"{self.base_url}/api/dostk/stkinfo"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "api-id": "ka10001"
        }
        
        body = {"stk_cd": code}

        data = self._send_request(url, headers, body)
        
        if data and data.get('return_code') == 0:
            return {
                "name": data.get('stk_nm', 'Unknown'),
                "code": code,
                "price": data.get('cur_prc', 'N/A'),
                "change": data.get('pred_pre', 'N/A'),
                "rate": data.get('flu_rt', 'N/A')
            }
        else:
            if data: print(f"[Error] API Error: {data.get('return_msg')}")
            return None

    def get_account_balance(self):
        """
        Fetches account stock holdings (Kiwoom kt00018).
        Returns list of stock holdings.
        """
        url = f"{self.base_url}/api/dostk/acnt"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "api-id": "kt00018"
        }
        
        body = {
            "qry_tp": "1",
            "dmst_stex_tp": "KRX"
        }

        data = self._send_request(url, headers, body)
        
        if data and data.get('return_code') == 0:
            holdings = data.get('acnt_evlt_remn_indv_tot', [])
            return {
                "total_purchase_amount": data.get('tot_pur_amt', '0'),
                "total_eval_amount": data.get('tot_evlt_amt', '0'),
                "total_profit_loss": data.get('tot_evlt_pl', '0'),
                "total_profit_rate": data.get('tot_prft_rt', '0'),
                "holdings": holdings
            }
        else:
            if data: print(f"[Error] API Error: {data.get('return_msg')}")
            return None

    def get_daily_chart_data(self, code, date=None):
        """
        일봉 차트 데이터 조회 (Kiwoom ka10081)
        """
        code = self._clean_code(code)
        url = f"{self.base_url}/api/dostk/chart" 
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "api-id": "ka10081"
        }
        
        try_date = date or datetime.datetime.now().strftime("%Y%m%d")
        
        body = {
            "stk_cd": code,
            "base_dt": try_date,
            "tick_range": "1",
            "upd_stkpc_tp": "1"
        }

        print(f"[Chart] Requesting data for {code} (base_dt: {try_date})...")
        data = self._send_request(url, headers, body)
        
        if data and data.get('return_code') == 0:
            output = data.get('stk_dt_pole_chart_qry', data.get('output', []))
            if output:
                print(f"[Chart] ✓ Got {len(output)} records")
                return output
            else:
                print(f"[Chart] ✗ No data available for {code}")
                return None
        else:
            if data: print(f"[Chart Error] API Error: {data.get('return_msg')}")
            return None

    def get_investor_trading(self, code):
        """
        투자자별 매매동향 조회 (Kiwoom ka10059)
        """
        code = self._clean_code(code)
        url = f"{self.base_url}/api/dostk/stkinfo"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "api-id": "ka10059"
        }
        
        today_date = datetime.datetime.now().strftime("%Y%m%d")
        
        # 1. 매도 데이터 조회
        sell_body = {
            "stk_cd": code, "dt": today_date, "amt_qty_tp": "1", "trde_tp": "3", "unit_tp": "1"
        }
        
        foreign_sell = 0
        institution_sell = 0
        
        data_sell = self._send_request(url, headers, sell_body)
        if data_sell and data_sell.get('return_code') == 0:
            output = data_sell.get('stk_invsr_orgn', [])
            if output:
                sell_data = output[0]
                foreign_sell = abs(int(sell_data.get('frgnr_invsr', 0)))
                institution_sell = abs(int(sell_data.get('orgn', 0)))

        # 2. 매수 데이터 조회
        buy_body = {
            "stk_cd": code, "dt": today_date, "amt_qty_tp": "1", "trde_tp": "2", "unit_tp": "1"
        }
        
        foreign_buy = 0
        institution_buy = 0
        
        data_buy = self._send_request(url, headers, buy_body)
        if data_buy and data_buy.get('return_code') == 0:
            output = data_buy.get('stk_invsr_orgn', [])
            if output:
                buy_data = output[0]
                foreign_buy = abs(int(buy_data.get('frgnr_invsr', 0)))
                institution_buy = abs(int(buy_data.get('orgn', 0)))
        
        return {
            'foreign_buy': foreign_buy, 'foreign_sell': foreign_sell,
            'foreign_net': foreign_buy - foreign_sell,
            'institution_buy': institution_buy, 'institution_sell': institution_sell,
            'institution_net': institution_buy - institution_sell
        }

    def get_market_index(self, market_code):
        """
        시장 지수 조회 (코스피: 001, 코스닥: 101)
        """
        url = f"{self.base_url}/api/dostk/sect"
        
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "api-id": "ka20001"
        }

        mrkt_tp = "0" if market_code == "001" else "1"
        body = {"mrkt_tp": mrkt_tp, "inds_cd": market_code}

        data = self._send_request(url, headers, body)
        
        if data and (data.get('return_code') == 0 or data.get('cur_prc')):
            return {
                'price': data.get('cur_prc', '0'),
                'change': data.get('pred_pre', '0'),
                'rate': data.get('flu_rt', '0')
            }
        else:
            if data: print(f"[Error] API Error: {data.get('return_msg')}")
            return None

    def get_minute_chart_data(self, code):
        """
        분봉 차트 데이터 조회 (Kiwoom ka10086 - 추정)
        Note: app.py에서 호출되므로 추가함.
        """
        code = self._clean_code(code)
        # 분봉 API URL 및 TR 코드는 문서 확인 필요. 
        # 여기서는 일봉과 유사한 패턴으로 가정하거나, 기존에 구현되어 있었다면 복구해야 함.
        # 만약 이전 파일에 없었다면 app.py가 에러를 냈을 것임.
        # 안전을 위해 빈 리스트 반환 또는 에러 로그 출력
        print(f"[Warning] get_minute_chart_data not fully implemented for {code}")
        return []
