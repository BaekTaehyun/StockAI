from kis_api import KiwoomApi
from gemini_service import GeminiService
from technical_indicators import TechnicalIndicators
from theme_service import ThemeService
import config
import time

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

    def get_full_analysis(self, code, stock_name=None, force_refresh=False, global_market_data=None):
        """
        종목에 대한 종합 분석 수행
        
        Args:
            code: 종목코드
            stock_name: 종목명 (선택, 없으면 API로 조회)
            force_refresh: 캐시 강제 갱신 여부
            global_market_data: 외부에서 주입된 글로벌 시장 데이터 (선택)
            
        Returns:
            종합 분석 데이터
        """
        try:
            # 종목 코드 정규화 (A 접두사 제거)
            normalized_code = code.lstrip('A') if code and code.startswith('A') else code
            # print(f"[Debug] Stock code normalization: {code} → {normalized_code}")
            
            # 1. 현재가 정보 조회 (캐싱 적용)
            price_cache_key = f"price_{normalized_code}"
            price_info = None
            
            if not force_refresh:
                price_info = self._get_cached_data(price_cache_key)
                
            if not price_info:
                price_info = self.kiwoom.get_current_price(normalized_code)
                if price_info:
                    self._set_cached_data(price_cache_key, price_info, ttl=60) # 60초 캐시
            
            if not price_info:
                return {'success': False, 'message': '주가 정보 조회 실패'}
            
            stock_name = stock_name or price_info.get('name', '알 수 없음')
            
            # 2. 수급 데이터 조회 (캐싱 적용)
            supply_cache_key = f"supply_{normalized_code}"
            supply_demand = None
            
            if not force_refresh:
                supply_demand = self._get_cached_data(supply_cache_key)
                
            if not supply_demand:
                supply_demand = self.get_supply_demand_data(normalized_code)
                if supply_demand:
                    self._set_cached_data(supply_cache_key, supply_demand, ttl=60) # 60초 캐시
            
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
                    # print(f"[Debug] First chart item keys: {daily_chart[0].keys()}")
                    # print(f"[Debug] First chart item sample: {daily_chart[0]}")
                    pass

                for item in daily_chart:
                    # Kiwoom API 응답 필드명 매핑
                    # cur_prc: 현재가(종가), high_pric: 고가, low_pric: 저가, trde_qty: 거래량
                    # stck_oprc: 시가 (필요시 추가)
                    close_price = abs(self._safe_int(item.get('cur_prc', 0))) # 종가 (stck_clpr)
                    high_price = abs(self._safe_int(item.get('high_pric', 0))) # 고가 (stck_hgpr)
                    low_price = abs(self._safe_int(item.get('low_pric', 0))) # 저가 (stck_lwpr)
                    volume = self._safe_int(item.get('trde_qty', 0)) # 거래량 (acml_vol)
                    
                    # 날짜 필드 확인 (stck_bsop_date or dt)
                    date_str = item.get('stck_bsop_date', item.get('dt', ''))

                    price_data.append({
                        'date': date_str, # 일자
                        'close': close_price, # 종가
                        'high': high_price, # 고가
                        'low': low_price, # 저가
                        'volume': volume # 거래량
                    })
                # 날짜 오름차순 정렬 (과거 -> 현재)
                price_data.sort(key=lambda x: x['date'])
                
            technical = TechnicalIndicators.calculate_indicators(price_data)
            
            # 4. 뉴스 분석 (Gemini) - Optional
            news_analysis = {
                'news_summary': '뉴스 분석을 사용할 수 없습니다',
                'reason': 'Gemini API가 설정되지 않았습니다',
                'sentiment': '중립',
                'raw_response': ''
            }
            try:
                news_analysis = self.gemini.search_and_analyze_news(
                    stock_name=stock_name,
                    stock_code=normalized_code,  # 정규화된 코드 사용
                    current_price=price_info.get('price'),
                    change_rate=price_info.get('rate'),
                    force_refresh=force_refresh
                )
            except Exception as e:
                print(f"[StockAnalysisService] 뉴스 분석 건너뜀: {e}")
            
            # 5. 시장 데이터 수집 (Top-Down Analysis)
            market_data = {}
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
                if global_market_data:
                    market_data['us_indices'] = global_market_data.get('indices', '정보 없음')
                    market_data['us_themes'] = global_market_data.get('themes', '정보 없음')
                
                # 5-2. 주도 테마 (Gemini Search)
                market_data['themes'] = self.gemini.fetch_market_themes(force_refresh=force_refresh)
                
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
                    print(f"[Analysis] 종목 '{stock_name}' 테마: {market_data['sector']}")
                else:
                    market_data['sector'] = '테마 정보 없음'
                    print(f"[Analysis] 종목 '{stock_name}' 테마를 찾을 수 없습니다")
                
            except Exception as e:
                print(f"[StockAnalysisService] 시장 데이터 수집 실패: {e}")

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
                    print(f"[StockAnalysisService] 펀더멘털 데이터 수집 실패: {e}")
                    fundamental_data = {}

            # 7. AI 전망 생성 (Gemini) - Optional
            outlook = {
                'recommendation': '중립',
                'confidence': 0,
                'reasoning': 'AI 전망을 사용할 수 없습니다 (Gemini API가 설정되지 않았습니다)',
                'raw_response': ''
            }
            try:
                # print(f"[Debug] AI 전망 생성 요청 - 펀더멘털 데이터: {fundamental_data}")
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
                    force_refresh=force_refresh
                )
            except Exception as e:
                print(f"[StockAnalysisService] AI 전망 건너뜀: {e}")
            
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
                    'news_analysis': {
                        'summary': news_analysis.get('news_summary', ''),
                        'reason': news_analysis.get('reason', ''),
                        'sentiment': news_analysis.get('sentiment', '중립')
                    },
                    'outlook': {
                        'recommendation': outlook.get('recommendation', '중립'),
                        'confidence': outlook.get('confidence', 0),
                        'reasoning': outlook.get('reasoning', ''),
                        'trading_scenario': outlook.get('trading_scenario', ''),
                        'price_strategy': outlook.get('price_strategy', {}),
                        'raw_response': outlook.get('raw_response', ''),
                        '_cache_info': outlook.get('_cache_info', {})
                    },
                    'fundamental_data': fundamental_data
                }
            }

            
        except Exception as e:
            print(f"[StockAnalysisService] 종합 분석 실패: {e}")
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
            print(f"[StockAnalysisService] 지수 조회 실패: {e}")
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
                
                result = {
                    'foreign_buy': investor_data.get('foreign_buy', 0),
                    'foreign_sell': investor_data.get('foreign_sell', 0),
                    'foreign_net': foreign_net,
                    'institution_buy': investor_data.get('institution_buy', 0),
                    'institution_sell': investor_data.get('institution_sell', 0),
                    'institution_net': institution_net,
                    'trend': trend
                }
                
                # 캐시 업데이트 (카드와 디테일 창 데이터 일관성 유지)
                normalized_code = code.lstrip('A') if code and code.startswith('A') else code
                supply_cache_key = f"supply_{normalized_code}"
                self._set_cached_data(supply_cache_key, result, ttl=60)
                
                return result
            else:
                return self._get_default_supply_demand()
                
        except Exception as e:
            print(f"[StockAnalysisService] 수급 데이터 조회 실패: {e}")
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
