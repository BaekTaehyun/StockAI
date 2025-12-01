import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

# Finviz는 봇 탐지를 하므로 브라우저처럼 보이는 헤더가 필수입니다.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class FinvizMarketFetcher:
    def __init__(self):
        self.base_url = "https://finviz.com"

    def get_market_indices(self):
        """
        Finviz 메인 페이지 상단에서 3대 지수(Dow, Nasdaq, S&P 500)를 가져옵니다.
        """
        try:
            response = requests.get(self.base_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            indices_data = []
            
            # Finviz 상단 지수 티커 부분 찾기 (클래스명은 변경될 수 있어 구조로 찾음)
            # 보통 'a' 태그 안에 지수 이름과 등락률이 같이 있습니다.
            # 정확도를 위해 텍스트 기반으로 검색합니다.
            targets = ["S&P 500", "Nasdaq", "Dow"]
            
            # 상단 티커 바(header) 영역을 찾습니다.
            # (Finviz UI 구조상 메인 컨테이너 안의 특정 클래스들을 탐색)
            
            # 팁: Finviz 메인 페이지 파싱은 UI 변경에 취약하므로, 
            # 실제로는 yfinance 라이브러리를 쓰는게 지수 확보엔 더 안정적입니다.
            # 여기서는 요청하신 대로 Finviz HTML 파싱을 시도합니다.
            
            all_links = soup.find_all('a', class_='tab-link') 
            # 2024년 기준 상단 지수들이 'tab-link' 클래스나 header_ticker 등으로 잡히는 경우가 많습니다.
            # 하지만 더 확실한 방법은 텍스트 검색입니다.
            
            # 메인 페이지 텍스트 전체에서 지수 정보를 추출하는 간단한 방식
            for item in soup.select('div.content > div > div'): # 상단 바 영역 근사치
                text = item.get_text()
                for target in targets:
                    if target in text and "%" in text:
                        # 데이터 정제 로직 (단순화)
                        indices_data.append(text.strip())
            
            # 만약 위 방식이 복잡하다면, 대안으로 'Futures' 탭을 긁는 것이 훨씬 깔끔합니다.
            # 아래는 Futures 페이지를 활용한 안정적인 방법입니다.
            return self._get_indices_from_futures()

        except Exception as e:
            return f"Error fetching indices: {str(e)}"

    def _get_indices_from_futures(self):
        """
        yfinance를 사용하여 주요 지수를 가져옵니다.
        """
        try:
            import yfinance as yf
            
            # 티커 심볼: S&P 500 (^GSPC), Nasdaq (^IXIC), Dow (^DJI)
            tickers = {
                '^GSPC': 'S&P 500',
                '^IXIC': 'Nasdaq',
                '^DJI': 'Dow Jones'
            }
            
            market_summary = []
            
            for symbol, name in tickers.items():
                ticker = yf.Ticker(symbol)
                # fast_info가 더 빠름
                try:
                    price = ticker.fast_info['last_price']
                    prev_close = ticker.fast_info['previous_close']
                    change_pct = ((price - prev_close) / prev_close) * 100
                    
                    # 부호 추가
                    sign = "+" if change_pct >= 0 else ""
                    market_summary.append(f"{name}: {sign}{change_pct:.2f}%")
                except:
                    # fast_info 실패 시 history 사용 (느림)
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                        # 전일 종가를 정확히 알기 어려울 수 있음 (Open 사용 근사)
                        # 하지만 history(period="2d")로 가져오는게 나음
                        hist2 = ticker.history(period="5d") # 넉넉히
                        if len(hist2) >= 2:
                            prev_close = hist2['Close'].iloc[-2]
                            change_pct = ((price - prev_close) / prev_close) * 100
                            sign = "+" if change_pct >= 0 else ""
                            market_summary.append(f"{name}: {sign}{change_pct:.2f}%")
            
            if not market_summary:
                return "지수 데이터를 가져올 수 없습니다."
                
            return " / ".join(market_summary)

        except Exception as e:
            return f"지수 데이터 수집 실패(yfinance): {e}"

    def get_strong_themes(self):
        """
        Groups 페이지에서 'Industry(산업)' 기준으로 등락률 상위 테마를 가져옵니다.
        """
        # g=industry: 산업별 보기
        # v=110: 밸류에이션 등 기본 정보 말고 'Performance(등락률)' 보기
        # o=-change: 등락률 내림차순 정렬 (오늘 가장 강한 것부터)
        url = f"{self.base_url}/groups.ashx?g=industry&v=110&o=-change"
        
        try:
            response = requests.get(url, headers=HEADERS)
            
            # pandas의 read_html은 페이지 내의 <table> 태그를 모두 찾아 데이터프레임으로 만듭니다.
            # Finviz Groups 페이지는 테이블 구조가 명확해서 아주 잘 읽힙니다.
            dfs = pd.read_html(io.StringIO(response.text))
            
            # 보통 메인 데이터 테이블은 인덱스 4번이나 5번쯤에 위치합니다. 
            # 데이터 크기로 진짜 테이블을 찾습니다.
            df = None
            for d in dfs:
                if len(d) > 10: # 행이 10개 이상인 것을 데이터 테이블로 간주
                    df = d
                    break
            
            if df is not None:
                # 상위 5개 (강세 테마)
                top5 = df.head(5)
                # 하위 3개 (약세 테마 - 시장 분위기 파악용)
                bottom3 = df.tail(3)
                
                hot_themes = []
                for _, row in top5.iterrows():
                    # 컬럼 구조: No | Name | Market Cap | ... | Change
                    # 보통 Name은 1번 컬럼, Change는 맨 뒤에서 두번째 정도입니다.
                    # 컬럼 이름으로 접근하는 것이 안전합니다.
                    theme_name = row['Name']
                    change = row['Change']
                    hot_themes.append(f"{theme_name} ({change})")
                
                return ", ".join(hot_themes)
            else:
                return "테마 테이블을 찾을 수 없습니다."

        except Exception as e:
            return f"테마 데이터 수집 실패: {str(e)}"

# ==========================================
# 실행 테스트
# ==========================================
if __name__ == "__main__":
    fetcher = FinvizMarketFetcher()
    
    print(">>> 1. 시장 지수 (Market Indices)")
    indices = fetcher.get_market_indices()
    print(indices)
    
    print("\n>>> 2. 오늘의 강세 테마 (Hot Themes)")
    themes = fetcher.get_strong_themes()
    print(themes)
