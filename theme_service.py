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
from datetime import datetime, timedelta
from kis_api import KiwoomApi

class ThemeService:
    """테마 데이터 캐시 관리 서비스"""
    
    def __init__(self, cache_file="static/data/themes_cache.json"):
        """
        Args:
            cache_file (str): 캐시 파일 경로
        """
        self.cache_file = cache_file
        self.api = KiwoomApi()
        
        # 캐시 디렉토리 생성
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    
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
        
        Args:
            stock_name_or_code (str): 주식 이름 또는 코드
            
        Returns:
            list: 해당 주식이 속한 테마 목록과 종목 정보
        """
        print(f"\n[ThemeSearch] Searching themes for stock: '{stock_name_or_code}'")
        
        # 캐시된 테마 데이터 조회
        themes_data = self.get_themes()
        themes = themes_data.get('themes', [])
        
        matched_themes = []
        search_keyword = stock_name_or_code.lower()
        
        print(f"[ThemeSearch] Searching in {len(themes)} cached themes...")
        
        # 각 테마의 캐시된 종목 목록에서 검색
        for theme in themes:
            theme_code = theme.get('thema_grp_cd')
            theme_name = theme.get('thema_nm', 'Unknown')
            stocks = theme.get('stocks', [])  # 캐시된 종목 목록
            
            # 종목 목록에서 검색
            for stock in stocks:
                stock_name = stock.get('stk_nm', '').lower()
                stock_code = stock.get('stk_cd', '').lower()
                
                if search_keyword in stock_name or search_keyword in stock_code:
                    print(f"  [MATCH]: '{stock.get('stk_nm')}' ({stock.get('stk_cd')}) found in theme '{theme_name}' (등락률: {theme.get('flu_rt')})")
                    
                    matched_themes.append({
                        'theme_code': theme_code,
                        'theme_name': theme_name,
                        'theme_fluctuation': theme.get('flu_rt'),
                        'stock_name': stock.get('stk_nm'),
                        'stock_code': stock.get('stk_cd'),
                        'stock_price': stock.get('cur_prc'),
                        'stock_change': stock.get('flu_rt')
                    })
                    break  # 해당 테마에서 매칭되면 다음 테마로
        
        # 최종 결과 요약 로그
        if matched_themes:
            theme_names = [t['theme_name'] for t in matched_themes]
            print(f"\n[ThemeSearch] [RESULT] 주식 '{stock_name_or_code}' 매칭 결과:")
            print(f"[ThemeSearch]   -> 속한 테마: {', '.join(theme_names)}")
            print(f"[ThemeSearch]   -> 총 {len(matched_themes)}개 테마 발견 (검색 시간: 즉시)\n")
        else:
            print(f"\n[ThemeSearch] [X] 주식 '{stock_name_or_code}'와 매칭되는 테마를 찾지 못했습니다.\n")
        
        return matched_themes
