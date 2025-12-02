"""
원/달러 환율 정보 수집 모듈
네이버 금융 모바일 API를 통해 실시간 환율 정보를 가져옵니다.
"""
import requests
import json
from datetime import datetime


class ExchangeRateFetcher:
    """원/달러 환율 정보를 가져오는 클래스"""
    
    def __init__(self):
        # 업데이트된 API 엔드포인트 (2025년 12월 기준)
        self.api_url = "https://m.stock.naver.com/front-api/marketIndex/prices"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://m.stock.naver.com/'
        }
    
    def get_usd_krw_rate(self):
        """
        실시간 원/달러 환율을 가져옵니다.
        
        Returns:
            dict: {
                'rate': float,           # 현재 환율 (예: 1432.5)
                'change': float,         # 전일 대비 변화량 (예: +5.0 또는 -3.2)
                'change_pct': float,     # 등락률 (예: 0.35)
                'status': str,           # 상승/하락 텍스트
                'timestamp': str,        # 조회 시각
                'success': bool          # 성공 여부
            }
        """
        params = {
            'category': 'exchange',
            'reutersCode': 'FX_USDKRW'
        }
        
        try:
            response = requests.get(self.api_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 데이터 파싱
            if 'result' not in data or len(data['result']) == 0:
                raise ValueError("환율 데이터가 비어있습니다")
            
            result = data['result'][0]  # 첫 번째 결과 사용
            
            # closePrice: 현재 매매기준율 (쉼표 제거 필요)
            current_rate = float(str(result.get('closePrice', '0')).replace(',', ''))
            
            # 등락 정보 (쉼표 제거 필요)
            change_val = float(str(result.get('compareToPreviousClosePrice', '0')).replace(',', ''))  # 전일 대비
            change_pct = float(str(result.get('fluctuationsRatio', '0')).replace(',', ''))  # 등락률
            
            # 상승/하락 판단
            if change_val > 0:
                status = '상승'
                status_text = f"📈 상승 {abs(change_val):.2f}원"
            elif change_val < 0:
                status = '하락'
                status_text = f"📉 하락 {abs(change_val):.2f}원"
            else:
                status = '보합'
                status_text = "➡️ 보합"
            
            return {
                'success': True,
                'rate': current_rate,
                'change': change_val,
                'change_pct': change_pct,
                'status': status,
                'status_text': status_text,
                'timestamp': datetime.now().isoformat(),
                'formatted': f"₩{current_rate:,.2f}/$ ({status_text})"
            }
            
        except requests.exceptions.RequestException as e:
            print(f"[ExchangeRate] 네트워크 오류: {e}")
            return {
                'success': False,
                'error': f"네트워크 오류: {str(e)}",
                'rate': 0,
                'change': 0,
                'change_pct': 0,
                'status': 'error'
            }
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"[ExchangeRate] 데이터 파싱 오류: {e}")
            return {
                'success': False,
                'error': f"데이터 파싱 오류: {str(e)}",
                'rate': 0,
                'change': 0,
                'change_pct': 0,
                'status': 'error'
            }
        except Exception as e:
            print(f"[ExchangeRate] 알 수 없는 오류: {e}")
            return {
                'success': False,
                'error': f"알 수 없는 오류: {str(e)}",
                'rate': 0,
                'change': 0,
                'change_pct': 0,
                'status': 'error'
            }


# === 실행 테스트 ===
if __name__ == "__main__":
    fetcher = ExchangeRateFetcher()
    exchange_info = fetcher.get_usd_krw_rate()
    
    print("=== 원/달러 환율 정보 ===")
    if exchange_info['success']:
        print(f"현재 환율: {exchange_info['rate']:,.2f}원")
        print(f"전일 대비: {exchange_info['change']:+.2f}원 ({exchange_info['change_pct']:+.2f}%)")
        print(f"상태: {exchange_info['status_text']}")
        print(f"조회 시각: {exchange_info['timestamp']}")
        print(f"\n포맷된 출력: {exchange_info['formatted']}")
    else:
        print(f"오류 발생: {exchange_info.get('error', '알 수 없는 오류')}")
