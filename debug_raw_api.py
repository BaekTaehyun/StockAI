from kis_api import KiwoomApi
import json
import datetime
import requests

class DebugKiwoom(KiwoomApi):
    def debug_investor_trading(self, code, date=None):
        url = f"{self.base_url}/api/dostk/stkinfo"
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "ka10059"
        }
        
        today_date = date or datetime.datetime.now().strftime("%Y%m%d")
        
        # 3. Net data (trde_tp="3")
        net_body = {
            "stk_cd": code, "dt": today_date, "amt_qty_tp": "1", "trde_tp": "3", "unit_tp": "1"
        }
        
        print(f"Requesting for date: {today_date}")
        res = requests.post(url, headers=headers, data=json.dumps(net_body))
        print("Raw Response:")
        print(res.text)

def run():
    api = DebugKiwoom()
    if not api.get_access_token():
        return
        
    print("--- Checking Today (Sunday) ---")
    api.debug_investor_trading("005930", "20251201")
    
    print("\n--- Checking Friday ---")
    api.debug_investor_trading("005930", "20251129")

if __name__ == "__main__":
    run()
