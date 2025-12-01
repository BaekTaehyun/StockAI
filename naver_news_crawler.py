import requests
from bs4 import BeautifulSoup
import difflib

class NaverNewsCrawler:
    """
    네이버 금융 뉴스 크롤러
    - 실시간 뉴스 탭 크롤링
    - 광고성/스팸 뉴스 필터링
    - 중복 뉴스 제거
    """
    
    # 필터링 키워드 (광고/스팸/노이즈)
    SPAM_KEYWORDS = ["무료추천", "카톡방", "▲", "대박", "속보", "급등주", "특징주"]
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://finance.naver.com/'
        }

    def get_news(self, code):
        """
        특정 종목의 최신 뉴스를 가져옵니다.
        """
        # 종목 코드 정규화 (005930)
        code = code.lstrip('A') if code.startswith('A') else code
        
        base_url = f"https://finance.naver.com/item/news_news.naver?code={code}"
        
        try:
            response = requests.get(base_url, headers=self.headers)
            response.encoding = 'euc-kr' # 네이버 금융 인코딩 처리
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            raw_news_list = []
            
            # 뉴스 리스트 테이블 찾기 (.type5)
            # 네이버 금융 뉴스 페이지 구조에 따라 선택자 조정
            # 보통 body > div > table.type5 > tbody > tr
            articles = soup.select('.type5 tbody tr')
            
            for article in articles:
                # 제목 태그
                title_tag = article.select_one('.title a')
                
                if title_tag:
                    headline = title_tag.get_text(strip=True)
                    link = "https://finance.naver.com" + title_tag['href']
                    
                    # 정보 제공처
                    source_tag = article.select_one('.info')
                    source = source_tag.get_text(strip=True) if source_tag else "Unknown"
                    
                    # 날짜
                    date_tag = article.select_one('.date')
                    date = date_tag.get_text(strip=True) if date_tag else ""
                    
                    # 1차 필터링: 스팸 키워드
                    if self._is_spam(headline):
                        continue
                        
                    raw_news_list.append({
                        "date": date,
                        "source": source,
                        "headline": headline,
                        "link": link
                    })
            
            # 2차 필터링: 중복 제거
            clean_news_list = self._deduplicate(raw_news_list)
            
            return clean_news_list

        except Exception as e:
            print(f"[NaverNewsCrawler] Error fetching news for {code}: {e}")
            return []

    def _is_spam(self, headline):
        """스팸 키워드가 포함되어 있는지 확인"""
        for keyword in self.SPAM_KEYWORDS:
            if keyword in headline:
                return True
        return False

    def _deduplicate(self, news_list):
        """
        중복 뉴스 제거
        - 제목 앞 10글자가 같거나
        - 유사도가 80% 이상인 경우
        """
        unique_news = []
        
        for news in news_list:
            is_duplicate = False
            for existing in unique_news:
                # 1. 앞 10글자 비교
                if news['headline'][:10] == existing['headline'][:10]:
                    is_duplicate = True
                    break
                
                # 2. 유사도 비교 (SequenceMatcher)
                similarity = difflib.SequenceMatcher(None, news['headline'], existing['headline']).ratio()
                if similarity >= 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_news.append(news)
                
        return unique_news

if __name__ == "__main__":
    # 테스트 코드
    crawler = NaverNewsCrawler()
    stock_code = "005930" # 삼성전자
    print(f"Fetching news for {stock_code}...")
    news = crawler.get_news(stock_code)
    
    print(f"Found {len(news)} clean articles:")
    for n in news[:5]:
        print(f"- [{n['source']}] {n['headline']} ({n['date']})")
