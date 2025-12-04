from kis_api import KiwoomApi
from gemini_service import GeminiService
from technical_indicators import TechnicalIndicators
from theme_service import ThemeService
import config
import time
from logger import Logger

class StockAnalysisService:
    """주식 종목 종합 분석 서비스"""
    
    def __init__(self):
        self.kiwoom = KiwoomApi()
        # 자동으로 액세스 토큰 획득
        self.kiwoom.get_access_token()
        self.gemini = GeminiService()
        self.theme_service = ThemeService()
        
        # 메모리 캐시 초기화
        # 구조: { 'key': { 'data': ..., 'timestamp': ..., 'ttl': ... } }
        self._memory_cache = {}
        
    def _safe_int(self, value):
        """안전한 정수 변환"""
        try:
            if isinstance(value, str):
                return int(value.strip())
            return int(value)
        except (ValueError, TypeError):
            return 0

    def _get_cached_data(self, key):
        """캐시된 데이터 조회"""
        if key in self._memory_cache:
            cache_item = self._memory_cache[key]
            current_time = time.time()
            if current_time - cache_item['timestamp'] < cache_item['ttl']:
                return cache_item['data']
            else:
                # 만료된 캐시 삭제
                del self._memory_cache[key]
        return None

    def _set_cached_data(self, key, data, ttl=60):
        """데이터 캐싱"""
        self._memory_cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl
        }

    def get_full_analysis(self, code, stock_name=None, force_refresh=False, global_market_data=None, lightweight=False):
        """
        종목에 대한 종합 분석 수행
        
        Args:
            code: 종목코드
            stock_name: 종목명 (선택, 없으면 API로 조회)
            force_refresh: 캐시 강제 갱신 여부
            global_market_data: 외부에서 주입된 글로벌 시장 데이터 (선택)
            lightweight: True면 AI 분석을 스킵하고 기본 정보만 반환 (빠른 응답)
            
        Returns:
            종합 분석 데이터
        """
        try:
            # 종목 코드 정규화 (A 접두사 제거)
            normalized_code = code.lstrip('A') if code and code.startswith('A') else code
            # Logger.debug("Analysis", f"Stock code normalization: {code} → {normalized_code}")
            
            # 1. 현재가 정보 조회 (실시간 데이터이므로 캐싱 안 함)
            price_info = self.kiwoom.get_current_price(normalized_code)
            
            if not price_info:
                return {'success': False, 'message': '주가 정보 조회 실패'}
            
            stock_name = stock_name or price_info.get('name', '알 수 없음')
            
            # 2. 수급 데이터 조회 (get_supply_demand_data 자체 캐싱 사용)
            # get_supply_demand_data가 내부적으로 캐싱을 관리하므로 여기서는 중복 캐싱하지 않음
            supply_demand = self.get_supply_demand_data(normalized_code)
            
            # 3. 기술적 지표 계산 (일봉 데이터 필요, 캐싱 적용)
            # 일봉 데이터는 양이 많으므로 데이터 자체를 캐싱
            chart_cache_key = f"chart_{normalized_code}"
            daily_chart = None
            
            if not force_refresh:
                daily_chart = self._get_cached_data(chart_cache_key)
                
            if not daily_chart:
                daily_chart = self.kiwoom.get_daily_chart_data(normalized_code)
                if daily_chart:
                    self._set_cached_data(chart_cache_key, daily_chart, ttl=60) # 60초 캐시
            
            # 일봉 데이터가 있으면 전처리
            price_data = []
            if daily_chart:
                # 디버깅: 첫 번째 데이터 항목 출력하여 키 확인
                if len(daily_chart) > 0:
                    # Logger.debug("Analysis", f"First chart item keys: {daily_chart[0].keys()}")
                    # Logger.debug("Analysis", f"First chart item sample: {daily_chart[0]}")
                    pass

                # kis_api.py에서 이미 표준화된 키(date, close, high, low, volume)로 변환되어 반환됨
                price_data = daily_chart
                
                # 날짜 오름차순 정렬 (과거 -> 현재)
                price_data.sort(key=lambda x: x['date'])
                
            technical = TechnicalIndicators.calculate_indicators(price_data)
            bollinger = TechnicalIndicators.calculate_bollinger_bands(price_data)
            
            # 4-5. 뉴스 분석과 시장 데이터 수집을 병렬로 처리 (성능 개선)
            news_analysis = {
                'news_summary': '뉴스 분석을 사용할 수 없습니다',
                'reason': 'Gemini API가 설정되지 않았습니다',
                'sentiment': '중립',
                'raw_response': ''
            }
            market_data = {}
            
            if not lightweight:
                # 병렬 처리: 뉴스 분석 + 테마 조회
                import concurrent.futures
                
                def fetch_news():
                    try:
                        return self.gemini.search_and_analyze_news(
                            stock_name=stock_name,
                            stock_code=normalized_code,
                            current_price=price_info.get('price'),
                            change_rate=price_info.get('rate'),
                            force_refresh=force_refresh
                        )
                    except Exception as e:
                        Logger.warning("Analysis", f"뉴스 분석 건너뜀: {e}")
                        return news_analysis  # 기본값 반환
                
                # ThreadPoolExecutor로 병렬 실행 (뉴스 분석만)
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    news_future = executor.submit(fetch_news)
                    
                    # 결과 대기
                    news_analysis = news_future.result()
                    
                # 테마 정보는 ThemeService에서 직접 조회 (빠름)
                try:
                    # 전체 테마 가져오기 (캐시됨)
                    all_themes = self.theme_service.get_themes().get('themes', [])
                    
                    # 등락률 기준 정렬 (내림차순)
                    sorted_themes = sorted(all_themes, key=lambda x: float(x.get('flu_rt', 0) or 0), reverse=True)
                    
                    # 상위 3개 추출
                    top_themes = []
                    for t in sorted_themes[:3]:
                        name = t.get('thema_nm')
                        rate = t.get('flu_rt')
                        top_themes.append(f"{name}({rate}%)")
                        
                    market_themes = ", ".join(top_themes) if top_themes else "정보 없음"
                except Exception as e:
                    Logger.error("Analysis", f"테마 조회 실패: {e}")
                    market_themes = "정보 없음"
            else:
                market_themes = '정보 없음'  # 경량 모드
            
            # 시장 데이터 구성
            try:
                # 5-1. 시장 지수 (KOSPI/KOSDAQ) - 캐싱 적용
                market_index_key = "market_index"
                market_index_str = None
                if not force_refresh:
                    market_index_str = self._get_cached_data(market_index_key)
                
                if not market_index_str:
                    market_index_str = self._get_market_indices_string()
                    self._set_cached_data(market_index_key, market_index_str, ttl=60)
                
                market_data['market_index'] = market_index_str
                
                # 글로벌 시장 데이터 병합 (US Indices, Themes)
                # 데이터가 있고 유효한 경우
                if global_market_data and global_market_data.get('indices') and global_market_data.get('themes'):
                    market_data['us_indices'] = global_market_data.get('indices', '정보 없음')
                    market_data['us_themes'] = global_market_data.get('themes', '정보 없음')
                else:
                    # 데이터가 없거나 누락된 경우 직접 수집 시도 (Fallback)
                    Logger.warning("Analysis", "글로벌 시장 데이터 누락됨, 직접 수집 시도...")
                    try:
                        from finviz_market_crawler import FinvizMarketFetcher
                        fetcher = FinvizMarketFetcher()
                        # 타임아웃 등 안전장치는 fetcher 내부 또는 여기서 고려 가능
                        market_data['us_indices'] = fetcher.get_market_indices()
                        market_data['us_themes'] = fetcher.get_strong_themes()
                        Logger.info("Analysis", f"직접 수집 성공: {market_data['us_indices']}")
                    except Exception as e:
                        Logger.error("Analysis", f"직접 수집 실패: {e}")
                        import traceback
                        traceback.print_exc()
                        market_data['us_indices'] = f'정보 없음 (오류: {str(e)})'
                        market_data['us_themes'] = f'정보 없음 (오류: {str(e)})'
                
                # 5-2. 주도 테마 (병렬로 가져온 데이터 사용)
                market_data['themes'] = market_themes
                
                # 5-3. 종목 테마 (Theme Service - REST API 캐시 사용)
                themes_found = self.theme_service.find_themes_by_stock(stock_name)
                if themes_found:
                    # 찾은 테마들을 등락률과 함께 문자열로 결합
                    theme_info_list = []
                    for t in themes_found[:3]:  # 최대 3개
                        theme_name = t['theme_name']
                        theme_flu = t['theme_fluctuation']
                        theme_info_list.append(f"{theme_name}({theme_flu})")
                    
                    market_data['sector'] = ', '.join(theme_info_list)
                    Logger.info("Analysis", f"종목 '{stock_name}' 테마: {market_data['sector']}")
                else:
                    market_data['sector'] = '테마 정보 없음'
                    Logger.info("Analysis", f"종목 '{stock_name}' 테마를 찾을 수 없습니다")
                
            except Exception as e:
                Logger.error("Analysis", f"시장 데이터 수집 실패: {e}")

            # 6. 펀더멘털 데이터 수집 (Fundamental, 정규화된 코드 사용) - 캐싱 적용
            fundamental_key = f"fundamental_{normalized_code}"
            fundamental_data = None
            
            if not force_refresh:
                fundamental_data = self._get_cached_data(fundamental_key)
                
            if not fundamental_data:
                try:
                    fundamental_data = self.kiwoom.get_stock_fundamental_info(normalized_code)
                    if not fundamental_data:
                        fundamental_data = {}
                    else:
                        self._set_cached_data(fundamental_key, fundamental_data, ttl=300) # 5분 캐시
                except Exception as e:
                    Logger.error("Analysis", f"펀더멘털 데이터 수집 실패: {e}")
                    fundamental_data = {}

            # 7. AI 전망 생성 (Gemini) - Optional, 경량 모드 시 스킵
            outlook = {
                'recommendation': '중립',
                'confidence': 0,
                'reasoning': 'AI 전망을 사용할 수 없습니다 (Gemini API가 설정되지 않았습니다)',
                'raw_response': ''
            }
            if not lightweight:
                try:
                    # Logger.debug("Analysis", f"AI 전망 생성 요청 - 펀더멘털 데이터: {fundamental_data}")
                    # stock_info에 정규화된 코드 전달
                    stock_info_for_outlook = {
                        'code': normalized_code,  # 정규화된 코드 사용!
                        'price': price_info.get('price'),
                        'rate': price_info.get('rate')
                    }
                    outlook = self.gemini.generate_outlook(
                        stock_name=stock_name,
                        stock_info=stock_info_for_outlook,
                        supply_demand=supply_demand,
                        technical_indicators=technical,
                        news_analysis=news_analysis,
                        market_data=market_data,
                        fundamental_data=fundamental_data,
                        bollinger_data=bollinger,
                        force_refresh=force_refresh
                    )
                except Exception as e:
                    Logger.error("Analysis", f"AI 전망 건너뜀: {e}")
            
            # 종합 결과 반환 (정규화된 코드 사용)
            return {
                'success': True,
                'data': {
                    'stock_info': {
                        'code': normalized_code,  # 정규화된 코드 사용
                        'name': stock_name,
                        'current_price': price_info.get('price', 'N/A'),
                        'change': price_info.get('change', 'N/A'),
                        'change_rate': price_info.get('rate', 'N/A')
                    },
                    'supply_demand': supply_demand,
                    'technical': technical,
                    'bollinger': bollinger,
                    'news_analysis': {
                        'summary': news_analysis.get('news_summary', ''),
                        'reason': news_analysis.get('reason', ''),
                        'sentiment': news_analysis.get('sentiment', '중립')
                    },
                    'outlook': {
                        'recommendation': outlook.get('recommendation', '중립'),
                        'confidence': outlook.get('confidence', 0),
                        'reasoning': outlook.get('reasoning', ''),
                        'key_logic': outlook.get('key_logic', ''),  # [FIX] 추가
                        'trading_scenario': outlook.get('trading_scenario', ''),
                        'detailed_analysis': outlook.get('detailed_analysis', ''),  # [FIX] 추가
                        'price_strategy': outlook.get('price_strategy', {}),
                        'raw_response': outlook.get('raw_response', ''),
                        '_cache_info': outlook.get('_cache_info', {})
                    },
                    'fundamental_data': fundamental_data
                }
            }

            
        except Exception as e:
            Logger.error("Analysis", f"종합 분석 실패: {e}")
            return {
                'success': False,
                'message': f'분석 중 오류 발생: {str(e)}'
            }
    
    def _get_market_indices_string(self):
        """
        코스피/코스닥 지수 조회 및 문자열 포맷팅
        """
        try:
            kospi = self.kiwoom.get_market_index("001")
            kosdaq = self.kiwoom.get_market_index("101")
            
            result = []
            if kospi:
                sign = "▲" if float(kospi['rate']) > 0 else "▼" if float(kospi['rate']) < 0 else "-"
                result.append(f"KOSPI {kospi['price']} ({sign} {kospi['rate']}%)")
            
            if kosdaq:
                sign = "▲" if float(kosdaq['rate']) > 0 else "▼" if float(kosdaq['rate']) < 0 else "-"
                result.append(f"KOSDAQ {kosdaq['price']} ({sign} {kosdaq['rate']}%)")
                
            return " / ".join(result) if result else "지수 정보 없음"
        except Exception as e:
            Logger.error("Analysis", f"지수 조회 실패: {e}")
            return "지수 정보 없음"

    def get_supply_demand_data(self, code):
        """
        수급 데이터 조회
        
        Args:
            code: 종목코드
            
        Returns:
            수급 정보 딕셔너리
        """
        try:
            # Kiwoom API에서 수급 데이터 조회
            investor_data = self.kiwoom.get_investor_trading(code)
            
            if investor_data:
                foreign_net = investor_data.get('foreign_net', 0)
                institution_net = investor_data.get('institution_net', 0)
                
                # 수급 트렌드 분석
                if foreign_net > 0 and institution_net > 0:
                    trend = "외국인/기관 동반 매수"
                elif foreign_net > 0:
                    trend = "외국인 매수 우세"
                elif institution_net > 0:
                    trend = "기관 매수 우세"
                elif foreign_net < 0 and institution_net < 0:
                    trend = "외국인/기관 동반 매도"
                else:
                    trend = "혼조세"
                
                # 수급 정보는 REST API 실시간 데이터이므로 캐싱하지 않음
                return {
                    'foreign_buy': investor_data.get('foreign_buy', 0),
                    'foreign_sell': investor_data.get('foreign_sell', 0),
                    'foreign_net': foreign_net,
                    'institution_buy': investor_data.get('institution_buy', 0),
                    'institution_sell': investor_data.get('institution_sell', 0),
                    'institution_net': institution_net,
                    'trend': trend
                }
            else:
                return self._get_default_supply_demand()
                
        except Exception as e:
            Logger.error("Analysis", f"수급 데이터 조회 실패: {e}")
            return self._get_default_supply_demand()
    
    def _get_default_supply_demand(self):
        """기본 수급 데이터 반환"""
        return {
            'foreign_buy': 0,
            'foreign_sell': 0,
            'foreign_net': 0,
            'institution_buy': 0,
            'institution_sell': 0,
            'institution_net': 0,
            'trend': '데이터 없음'
        }
