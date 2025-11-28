"""
Data Fetcher - 관심종목 시세 조회
================================================================
stocks.json 파일에서 관심종목 리스트를 읽어와서
키움 REST API로 실시간 시세를 조회하는 모듈입니다.

주요 기능:
- stocks.json 파일 로드
- 관심종목 리스트 조회
- 종목별 시세 일괄 조회
================================================================
"""
import json
import os
from kis_api import KiwoomApi

class DataFetcher:
    """관심종목 데이터 조회 클래스"""
    
    def __init__(self, stocks_file='stocks.json'):
        """초기화
        
        Args:
            stocks_file: 관심종목이 저장된 JSON 파일 경로
        """
        self.stocks_file = stocks_file
        self.kiwoom_api = KiwoomApi()
        
    def load_watchlist(self):
        """stocks.json에서 관심종목 리스트 읽기
        
        Returns:
            list: 종목 코드 리스트 (예: ['005930', '000660'])
        """
        if not os.path.exists(self.stocks_file):
            print(f"[Warning] {self.stocks_file} 파일이 없습니다. 빈 리스트를 반환합니다.")
            return []
        
        try:
            with open(self.stocks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                watchlist = data.get('watchlist', [])
                print(f"[DataFetcher] {len(watchlist)}개 관심종목 로드: {watchlist}")
                return watchlist
        except json.JSONDecodeError as e:
            print(f"[Error] JSON 파싱 오류: {e}")
            return []
        except Exception as e:
            print(f"[Error] 파일 읽기 오류: {e}")
            return []
    
    def save_watchlist(self, watchlist):
        """관심종목 리스트를 stocks.json에 저장
        
        Args:
            watchlist: 종목 코드 리스트
        """
        try:
            data = {
                'watchlist': watchlist,
                'description': '모니터링할 종목 코드 리스트'
            }
            with open(self.stocks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[DataFetcher] 관심종목 저장 완료: {len(watchlist)}개")
        except Exception as e:
            print(f"[Error] 파일 저장 오류: {e}")
    
    def add_to_watchlist(self, code):
        """관심종목 추가
        
        Args:
            code: 추가할 종목 코드
            
        Returns:
            bool: 성공 여부
        """
        watchlist = self.load_watchlist()
        
        if code in watchlist:
            print(f"[DataFetcher] {code}는 이미 관심종목에 있습니다.")
            return False
        
        watchlist.append(code)
        self.save_watchlist(watchlist)
        return True
    
    def remove_from_watchlist(self, code):
        """관심종목 삭제
        
        Args:
            code: 삭제할 종목 코드
            
        Returns:
            bool: 성공 여부
        """
        watchlist = self.load_watchlist()
        
        if code not in watchlist:
            print(f"[DataFetcher] {code}는 관심종목에 없습니다.")
            return False
        
        watchlist.remove(code)
        self.save_watchlist(watchlist)
        return True
    
    def fetch_watchlist_prices(self):
        """관심종목의 현재 시세 일괄 조회
        
        Returns:
            list: 각 종목의 시세 정보 딕셔너리 리스트
        """
        watchlist = self.load_watchlist()
        results = []
        
        for code in watchlist:
            try:
                price_data = self.kiwoom_api.get_current_price(code)
                if price_data:
                    results.append({
                        'code': code,
                        'data': price_data
                    })
                    print(f"[DataFetcher] {code} 시세 조회 성공")
                else:
                    print(f"[DataFetcher] {code} 시세 조회 실패")
            except Exception as e:
                print(f"[Error] {code} 조회 중 오류: {e}")
        
        return results


if __name__ == '__main__':
    # 테스트 코드
    fetcher = DataFetcher()
    
    print("\n=== 관심종목 리스트 ===")
    watchlist = fetcher.load_watchlist()
    print(watchlist)
    
    print("\n=== 시세 조회 ===")
    prices = fetcher.fetch_watchlist_prices()
    for item in prices:
        print(f"{item['code']}: {item['data']}")
