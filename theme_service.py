"""
테마 데이터 캐시 관리 서비스
================================
키움 REST API에서 하루 1회 테마 데이터를 가져와 JSON 파일로 저장하고,
이후 요청은 로컬 JSON에서 빠르게 검색하는 서비스 모듈.

주요 기능:
- update_cache(): REST API에서 테마 데이터 가져와 JSON 저장
- get_themes(): 캐시된 테마 목록 반환
- search_theme(keyword): 키워드로 테마 검색
- is_cache_valid(): 캐시 유효성 확인 (1일 기준)
"""

import os
import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from kis_api import KiwoomApi

class NaverThemeScraper:
    """
    네이버 금융 테마 페이지에서 테마와 종목 정보를 스크래핑하는 클래스
    """
    
    BASE_URL = "https://finance.naver.com/sise/theme.nhn"
    HEADERS = {'User-Agent': 'Mozilla/5.0'}
    
    @staticmethod
    def scrape_all_themes():
        """
        네이버 금융의 모든 테마(1~7페이지)를 스크래핑하여 반환합니다.
        주의: 약 250개 이상의 페이지를 방문하므로 시간이 오래 걸립니다 (3~5분).
        
        Returns:
            list: 테마 목록 (각 테마는 'name', 'link', 'stocks' 포함)
        """
        print("[NaverThemeScraper] Starting FULL scrape of all themes (Pages 1-7)...")
        all_themes = []
        
        try:
            # 1. 모든 테마 링크 수집 (1~7페이지)
            theme_links = []
            for page in range(1, 8):
                url = f"{NaverThemeScraper.BASE_URL}?&page={page}"
                print(f"[NaverThemeScraper] Scanning list page {page}/7...")
                
                res = requests.get(url, headers=NaverThemeScraper.HEADERS)
                res.encoding = 'cp949'
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # table.type_1 tr 태그 순회 (헤더 제외)
                for tr in soup.select('table.type_1 tr'):
                    tds = tr.select('td')
                    if len(tds) < 2: continue # 데이터가 없는 행 제외
                    
                    a_tag = tds[0].select_one('a')
                    if not a_tag: continue
                    
                    theme_name = a_tag.text.strip()
                    theme_link = a_tag['href']
                    
                    # 등락률 추출 (2번째 컬럼)
                    # 예: +1.52% -> 1.52
                    fluctuation_text = tds[1].text.strip().replace('%', '')
                    try:
                        fluctuation = float(fluctuation_text)
                    except:
                        fluctuation = 0.0
                    
                    theme_links.append({
                        "name": theme_name,
                        "link": theme_link,
                        "fluctuation": fluctuation
                    })
                
                # 차단 방지 지연
                import time
                time.sleep(0.1)
            
            print(f"[NaverThemeScraper] Found {len(theme_links)} themes total. Starting detail scrape...")
            
            # 2. 각 테마별 상세 페이지 방문
            for idx, theme in enumerate(theme_links, 1):
                theme_name = theme['name']
                theme_link = theme['link']
                
                if idx % 10 == 0:
                    print(f"[NaverThemeScraper] Processing theme {idx}/{len(theme_links)}: {theme_name}")
                
                detail_url = "https://finance.naver.com" + theme_link
                
                try:
                    res_detail = requests.get(detail_url, headers=NaverThemeScraper.HEADERS)
                    res_detail.encoding = 'cp949'
                    soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
                    
                    stocks = []
                    items = soup_detail.select('table.type_5 tr td.name a')
                    
                    for item in items:
                        stock_name = item.text.strip()
                        code_match = re.search(r'code=(\d+)', item['href'])
                        if code_match:
                            stock_code = code_match.group(1)
                            if stock_name.endswith(" *"): 
                                stock_name = stock_name[:-2]
                            
                            stocks.append({
                                "code": stock_code,
                                "name": stock_name
                            })
                    
                    all_themes.append({
                        "name": theme_name,
                        "link": theme_link,
                        "fluctuation": theme.get('fluctuation', 0.0),
                        "stocks": stocks
                    })
                    
                    # 차단 방지 지연
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"[NaverThemeScraper] Error scraping detail for {theme_name}: {e}")
                    continue
            
            print(f"[NaverThemeScraper] Full scrape completed. {len(all_themes)} themes processed.")
            return all_themes
            
        except Exception as e:
            print(f"[NaverThemeScraper] Error during full scrape: {e}")
            return []

    @staticmethod
    def get_theme_stocks(target_theme_keyword):
        """
        특정 키워드(예: 방위산업)를 포함하는 테마를 찾아
        해당 테마에 소속된 종목 리스트(코드, 종목명)를 반환합니다.
        
        Args:
            target_theme_keyword (str): 찾을 테마 키워드
            
        Returns:
            list: 종목 리스트 ([{'code': '005930', 'name': '삼성전자'}, ...])
        """
        print(f"[NaverThemeScraper] Searching for theme keyword: '{target_theme_keyword}'")
        
        try:
            theme_link = None
            theme_full_name = None
            
            # 1. 네이버 금융 테마 리스트 페이지 순회 (1~7페이지)
            # 네이버 금융 테마는 보통 7페이지 정도임
            for page in range(1, 8):
                url = f"{NaverThemeScraper.BASE_URL}?&page={page}"
                # print(f"[NaverThemeScraper] Scanning page {page}...")
                
                res = requests.get(url, headers=NaverThemeScraper.HEADERS)
                res.encoding = 'cp949' 
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 2. 테마 목록에서 'target_theme_keyword' 찾기
                # table.type_1 a 태그 순회
                for a_tag in soup.select('table.type_1 a'):
                    if target_theme_keyword in a_tag.text:
                        theme_link = a_tag['href']
                        theme_full_name = a_tag.text.strip()
                        print(f"[NaverThemeScraper] ✅ 테마 발견: {theme_full_name} (Link: {theme_link}) at Page {page}")
                        break
                
                if theme_link:
                    break
            
            if not theme_link:
                print(f"[NaverThemeScraper] ❌ '{target_theme_keyword}' 관련 테마를 1~7페이지에서 찾을 수 없습니다.")
                return []

            # 3. 상세 테마 페이지 접속 (종목 리스트 확보)
            detail_url = "https://finance.naver.com" + theme_link
            res_detail = requests.get(detail_url, headers=NaverThemeScraper.HEADERS)
            res_detail.encoding = 'cp949'
            soup_detail = BeautifulSoup(res_detail.text, 'html.parser')

            # 4. 종목 데이터 파싱
            stock_list = []
            # 테마 상세 페이지의 테이블 내 종목 링크들 추출
            # 상세 페이지는 table.type_5 를 사용함 (기존 type_1 아님)
            items = soup_detail.select('table.type_5 tr td.name a')
            
            for item in items:
                stock_name = item.text.strip()
                # href에서 코드 추출
                code_match = re.search(r'code=(\d+)', item['href'])
                if code_match:
                    stock_code = code_match.group(1)
                    # *표시(거래정지 등)가 붙은 종목명 처리
                    if stock_name.endswith(" *"): 
                        stock_name = stock_name[:-2]
                    
                    stock_list.append({
                        "code": stock_code,
                        "name": stock_name
                    })

            print(f"[NaverThemeScraper] Found {len(stock_list)} stocks for theme '{theme_full_name}'")
            return stock_list

        except Exception as e:
            print(f"[NaverThemeScraper] Error scraping theme: {e}")
            return []

class ThemeService:
    """테마 데이터 캐시 관리 서비스"""
    
    def __init__(self, cache_file="static/data/themes_cache.json", naver_cache_file="static/data/naver_themes_cache.json"):
        """
        Args:
            cache_file (str): 키움 테마 캐시 파일 경로
            naver_cache_file (str): 네이버 테마 캐시 파일 경로
        """
        self.cache_file = cache_file
        self.naver_cache_file = naver_cache_file
        self.api = KiwoomApi()
        
        # 캐시 디렉토리 생성
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        # 네이버 캐시 로드 (자동 갱신 체크 포함)
        self.naver_themes = self.load_naver_cache()

    def load_naver_cache(self):
        """
        네이버 테마 캐시를 로드합니다.
        30일이 지났으면 update_naver_cache()를 호출하여 갱신을 시도합니다.
        """
        if not os.path.exists(self.naver_cache_file):
            print("[ThemeService] Naver theme cache not found. Please run 'update_naver_cache.py' to generate it.")
            return []
            
        try:
            with open(self.naver_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            updated_at_str = data.get('updated_at')
            if updated_at_str:
                updated_at = datetime.fromisoformat(updated_at_str)
                age = datetime.now() - updated_at
                
                # 30일 경과 체크
                if age > timedelta(days=30):
                    print(f"[ThemeService] Naver cache expired (Age: {age.days} days). Triggering auto-update...")
                    # 백그라운드에서 실행하거나 여기서 바로 실행 (시간이 오래 걸리므로 주의)
                    # 여기서는 사용자가 '자동 갱신'을 원했으므로 바로 실행하지만, 
                    # 실제 서비스에서는 별도 스레드나 프로세스로 돌리는 것이 좋음.
                    # 일단은 동기적으로 실행하고 로그를 남김.
                    if self.update_naver_cache():
                        # 갱신 성공 시 다시 로드
                        with open(self.naver_cache_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
            
            themes = data.get('themes', [])
            print(f"[ThemeService] Loaded {len(themes)} Naver themes from cache.")
            return themes
            
        except Exception as e:
            print(f"[ThemeService] Error loading Naver cache: {e}")
            return []

    def update_naver_cache(self):
        """
        네이버 테마 전체를 스크래핑하여 캐시 파일로 저장합니다.
        (수동 실행 또는 30일 만료 시 자동 실행)
        """
        try:
            print("[ThemeService] Updating Naver theme cache... This may take a few minutes.")
            themes = NaverThemeScraper.scrape_all_themes()
            
            if not themes:
                print("[ThemeService] Failed to scrape Naver themes.")
                return False
                
            cache_data = {
                "updated_at": datetime.now().isoformat(),
                "theme_count": len(themes),
                "themes": themes
            }
            
            with open(self.naver_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            print(f"[ThemeService] [OK] Naver theme cache updated: {len(themes)} themes.")
            return True
            
        except Exception as e:
            print(f"[ThemeService] Error updating Naver cache: {e}")
            return False

    def update_cache(self):
        """
        REST API에서 테마 데이터 가져와 JSON 파일로 저장
        각 테마의 종목 정보도 함께 저장하여 빠른 검색 지원
        
        Returns:
            bool: 성공 여부
        """
        try:
            print("[ThemeService] Updating theme cache from REST API...")
            
            # 인증 토큰 발급
            if not self.api.get_access_token():
                print("[ThemeService] Failed to get access token")
                return False
            
            # 1단계: 테마 목록 조회
            themes = self.api.get_theme_group_list()
            
            if not themes:
                print("[ThemeService] No themes retrieved")
                return False
            
            print(f"[ThemeService] Retrieved {len(themes)} themes. Fetching stocks for each theme...")
            
            # 2단계: 각 테마의 종목 정보 조회
            for idx, theme in enumerate(themes, 1):
                theme_code = theme.get('thema_grp_cd')
                theme_name = theme.get('thema_nm', 'Unknown')
                
                # 진행 상황 표시 (매 10개마다)
                if idx % 10 == 0:
                    print(f"[ThemeService] Progress: {idx}/{len(themes)} themes processed...")
                
                # 테마의 종목 목록 조회
                stocks = self.api.get_theme_stocks(theme_code)
                
                if stocks:
                    theme['stocks'] = stocks  # 종목 정보를 테마에 추가
                else:
                    theme['stocks'] = []  # 비어있으면 빈 리스트
            
            # 캐시 데이터 구성
            cache_data = {
                "updated_at": datetime.now().isoformat(),
                "theme_count": len(themes),
                "themes": themes
            }
            
            # JSON 파일로 저장
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"[ThemeService] [OK] Cache updated successfully: {len(themes)} themes with stock info")
            return True
            
        except Exception as e:
            print(f"[ThemeService] Error updating cache: {e}")
            return False
    
    def get_themes(self, force_refresh=False):
        """
        캐시된 테마 목록 반환 (캐시가 없거나 오래된 경우 자동 갱신)
        
        Args:
            force_refresh (bool): 강제 갱신 여부
            
        Returns:
            dict: 캐시 데이터 (updated_at, theme_count, themes)
        """
        # 강제 갱신 또는 캐시 파일이 없는 경우
        if force_refresh or not os.path.exists(self.cache_file):
            print("[ThemeService] Cache not found or force refresh requested")
            self.update_cache()
        
        # 캐시 유효성 확인 (1일 경과 시 갱신)
        elif not self.is_cache_valid():
            print("[ThemeService] Cache expired, refreshing...")
            self.update_cache()
        
        # 캐시 데이터 로드
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ThemeService] Error reading cache: {e}")
            return {"updated_at": None, "theme_count": 0, "themes": []}
    
    def search_theme(self, keyword):
        """
        키워드로 테마 검색
        
        Args:
            keyword (str): 검색 키워드
            
        Returns:
            list: 검색된 테마 목록
        """
        data = self.get_themes()
        themes = data.get('themes', [])
        
        if not keyword:
            return themes
        
        # 테마명에 키워드가 포함된 항목 필터링
        results = [
            theme for theme in themes 
            if keyword.lower() in theme.get('thema_nm', '').lower()
        ]
        
        return results
    
    def is_cache_valid(self, max_age_hours=24):
        """
        캐시 유효성 확인
        
        Args:
            max_age_hours (int): 최대 캐시 유효 시간 (기본 24시간)
            
        Returns:
            bool: 캐시 유효 여부
        """
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated_at = datetime.fromisoformat(data.get('updated_at', ''))
            age = datetime.now() - updated_at
            
            return age < timedelta(hours=max_age_hours)
            
        except Exception as e:
            print(f"[ThemeService] Error checking cache validity: {e}")
            return False
    
    def get_cache_info(self):
        """
        캐시 정보 반환
        
        Returns:
            dict: 캐시 정보 (존재 여부, 업데이트 시간, 테마 개수)
        """
        if not os.path.exists(self.cache_file):
            return {
                "exists": False,
                "updated_at": None,
                "theme_count": 0,
                "is_valid": False
            }
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "exists": True,
                "updated_at": data.get('updated_at'),
                "theme_count": data.get('theme_count', 0),
                "is_valid": self.is_cache_valid()
            }
        except Exception as e:
            print(f"[ThemeService] Error getting cache info: {e}")
            return {
                "exists": True,
                "updated_at": None,
                "theme_count": 0,
                "is_valid": False,
                "error": str(e)
            }
    
    def find_themes_by_stock(self, stock_name_or_code):
        """
        주식 이름 또는 코드로 해당 주식이 속한 테마 찾기 (캐시된 데이터 사용)
        키움 테마와 네이버 테마를 모두 검색합니다.
        
        Args:
            stock_name_or_code (str): 주식 이름 또는 코드
            
        Returns:
            list: 해당 주식이 속한 테마 목록과 종목 정보
        """
        print(f"\n[ThemeSearch] Searching themes for stock: '{stock_name_or_code}'")
        matched_themes = []
        search_keyword = stock_name_or_code.lower()
        
        # 1. 키움 테마 검색
        themes_data = self.get_themes()
        kiwoom_themes = themes_data.get('themes', [])
        
        print(f"[ThemeSearch] Searching in {len(kiwoom_themes)} Kiwoom themes...")
        for theme in kiwoom_themes:
            theme_code = theme.get('thema_grp_cd')
            theme_name = theme.get('thema_nm', 'Unknown')
            stocks = theme.get('stocks', [])
            
            for stock in stocks:
                stock_name = stock.get('stk_nm', '').lower()
                stock_code = stock.get('stk_cd', '').lower()
                
                if search_keyword in stock_name or search_keyword in stock_code:
                    print(f"  [Kiwoom MATCH]: '{stock.get('stk_nm')}' found in '{theme_name}'")
                    matched_themes.append({
                        'source': 'Kiwoom',
                        'theme_code': theme_code,
                        'theme_name': theme_name,
                        'theme_fluctuation': theme.get('flu_rt'),
                        'stock_name': stock.get('stk_nm'),
                        'stock_code': stock.get('stk_cd'),
                        'stock_price': stock.get('cur_prc'),
                        'stock_change': stock.get('flu_rt')
                    })
                    break

        # 2. 네이버 테마 검색
        print(f"[ThemeSearch] Searching in {len(self.naver_themes)} Naver themes...")
        for theme in self.naver_themes:
            theme_name = theme.get('name', 'Unknown')
            theme_link = theme.get('link')
            stocks = theme.get('stocks', [])
            
            for stock in stocks:
                stock_name = stock.get('name', '').lower()
                stock_code = stock.get('code', '').lower()
                
                if search_keyword in stock_name or search_keyword in stock_code:
                    print(f"  [Naver MATCH]: '{stock.get('name')}' found in '{theme_name}'")
                    matched_themes.append({
                        'source': 'Naver',
                        'theme_code': None, # 네이버는 코드가 없음 (링크로 대체 가능)
                        'theme_name': theme_name,
                        'theme_fluctuation': theme.get('fluctuation', 0.0),
                        'theme_link': theme_link,
                        'stock_name': stock.get('name'),
                        'stock_code': stock.get('code'),
                        # 네이버 스크래핑 데이터에는 현재가/등락률이 없을 수 있음 (상세 페이지 파싱 시 추가 가능하지만 현재는 없음)
                        'stock_price': None,
                        'stock_change': None
                    })
                    break
        
        # 최종 결과 요약 로그
        if matched_themes:
            theme_names = [f"{t['theme_name']}({t['source']})" for t in matched_themes]
            print(f"\n[ThemeSearch] [RESULT] 주식 '{stock_name_or_code}' 매칭 결과:")
            print(f"[ThemeSearch]   -> 속한 테마: {', '.join(theme_names)}")
            print(f"[ThemeSearch]   -> 총 {len(matched_themes)}개 테마 발견 (검색 시간: 즉시)\n")
        else:
            print(f"\n[ThemeSearch] [X] 주식 '{stock_name_or_code}'와 매칭되는 테마를 찾지 못했습니다.\n")
        
        return matched_themes
