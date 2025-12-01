import google.generativeai as genai
from google.api_core import exceptions
import config
import json
import os
import datetime

import prompts
from gemini_cache import GeminiCache

class GeminiService:
    """Google Gemini SDK를 사용한 AI 분석 서비스"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.AI_MODEL)
        
        # 캐시 관리자 초기화
        self.cache = GeminiCache()
    



    def _call_gemini_api(self, prompt_text):
        """Gemini SDK를 사용한 API 호출 (120초 timeout)"""
        try:
            # timeout 설정: 120초 (긴 분석에 대비)
            response = self.model.generate_content(
                prompt_text,
                request_options={'timeout': 120}
            )
            
            # 디버깅: 응답 확인
            print(f"[Gemini API] Response received")
            print(f"[Gemini API] Response object type: {type(response)}")
            
            # Safety ratings 확인 (응답이 차단되었는지 확인)
            if hasattr(response, 'prompt_feedback'):
                print(f"[Gemini API] Prompt feedback: {response.prompt_feedback}")
            
            # 응답 텍스트 확인
            if hasattr(response, 'text') and response.text:
                print(f"[Gemini API] Response text length: {len(response.text)}")
                return response.text
            else:
                print(f"[Gemini API] No text in response. Candidates: {response.candidates if hasattr(response, 'candidates') else 'N/A'}")
                return None
                
        except exceptions.DeadlineExceeded:
            print(f"[Gemini API Error] Timeout (60s exceeded). The model took too long to respond.")
            return None
        except exceptions.ResourceExhausted:
            print(f"[Gemini API Error] Quota exceeded (429). Please try again later.")
            return None
        except exceptions.ServiceUnavailable:
            print(f"[Gemini API Error] Service unavailable (503). Google servers might be overloaded.")
            return None
        except exceptions.GoogleAPICallError as e:
            print(f"[Gemini API Error] API Call Error ({e.code}): {e.message}")
            return None
        except Exception as e:
            print(f"[Gemini API Error] Unexpected error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def search_news(self, query):
        """
        [Deprecated] Google Custom Search API를 사용한 뉴스 검색
        - 현재는 NaverNewsCrawler로 대체되어 사용되지 않음 (2025-12-01)
        """
        if not config.GOOGLE_SEARCH_API_KEY:
            print("[Search] API Key not configured.")
            return None
            
        import requests
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': config.GOOGLE_SEARCH_API_KEY,
            'cx': config.GOOGLE_SEARCH_CX,
            'q': query,
            'num': 5,
            'dateRestrict': f'd{config.NEWS_SEARCH_DAYS}'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get('items', [])
            elif response.status_code == 429:
                print(f"[Search] Daily quota exceeded. Skipping news search.")
                return []
            else:
                print(f"[Search Error] {response.status_code}")
                return None
        except Exception as e:
            print(f"[Search Connection Error] {e}")
            return None

    def search_and_analyze_news(self, stock_name, stock_code, current_price=None, change_rate=None, force_refresh=False):
        """
        종목 뉴스를 검색하고 AI로 분석 (MK AI 검색 + 구글 검색 동시 활용)
        """
        # 1. 캐시 확인
        cached_data, cache_info = self.cache.load(stock_code, 'news', force_refresh)
        if cached_data:
            cached_data['_cache_info'] = cache_info
            return cached_data

        try:
            mk_report = ""
            google_news = ""

            # --- 병렬 실행: MK AI 검색 + 구글 검색 ---
            import concurrent.futures
            
            def fetch_mk_report():
                try:
                    from mk_scraper import MKScraper
                    scraper = MKScraper(headless=True)
                    print(f"[Gemini] MK AI 검색 시도: {stock_name}")
                    mk_result = scraper.get_ai_answer(stock_name)
                    scraper.close()

                    if mk_result:
                        print(f"[Gemini] MK AI 검색 성공 (길이: {len(mk_result)})")
                        return f"[MK AI 분석 리포트]\n{mk_result}"
                    else:
                        print("[Gemini] MK AI 검색 결과 없음")
                        return "MK AI 분석 정보를 가져올 수 없습니다."
                except Exception as e:
                    print(f"[Gemini] MK AI 검색 중 오류 발생: {e}")
                    return "MK AI 분석 중 오류가 발생했습니다."

            def fetch_naver_news():
                try:
                    from naver_news_crawler import NaverNewsCrawler
                    crawler = NaverNewsCrawler()
                    print(f"[Gemini] 네이버 금융 뉴스 검색 시도: {stock_name} ({stock_code})")
                    news_list = crawler.get_news(stock_code)
                    
                    if news_list:
                        news_text = "네이버 금융 최신 뉴스 (AI 선별):\n"
                        # 최대 7개 정도만 사용
                        for news in news_list[:7]:
                            news_text += f"- [{news['source']}] {news['headline']} ({news['date']})\n"
                        return news_text
                    else:
                        return "(최신 뉴스 검색 실패)"
                except Exception as e:
                    print(f"[Gemini] 네이버 뉴스 검색 실패: {e}")
                    return "(뉴스 검색 오류)"

            # ThreadPoolExecutor를 사용하여 병렬 실행
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_mk = executor.submit(fetch_mk_report)
                future_news = executor.submit(fetch_naver_news)
                
                mk_report = future_mk.result()
                news_context = future_news.result()

            # --- 3단계: AI 분석 ---
            # 기업 리포트 데이터 구성 (기본 정보 + MK 리포트)
            company_report = f"""
            [기본 정보]
            - 종목명: {stock_name} ({stock_code})
            - 현재가: {current_price}원
            - 등락률: {change_rate}%

            {mk_report}
            """
            
            prompt = prompts.INVESTMENT_ANALYSIS_PROMPT.format(
                company_report=company_report,
                news_context=news_context
            )
            
            result_text = self._call_gemini_api(prompt)
            
            if not result_text:
                raise Exception("API 응답 없음")
            
            # 응답 파싱 (새로운 프롬프트 포맷에 맞춤)
            news_summary = ""
            reason = ""
            sentiment = "중립"
            
            lines = result_text.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                # 섹션 감지
                if "핵심 이슈" in line or line.startswith("1.") or "#### 1." in line:
                    current_section = "news"
                elif "주가 변동" in line or line.startswith("2.") or "#### 2." in line:
                    current_section = "reason"
                elif "종합 투자 판단" in line or line.startswith("3.") or "#### 3." in line:
                    current_section = "sentiment"
                
                # 내용 추출
                elif current_section == "news" and line.startswith("-"):
                    news_summary += line + "\n"
                elif current_section == "reason" and line.startswith("-"):
                    reason += line + "\n"
                elif current_section == "sentiment":
                    if "단기적 관점" in line:
                        if "긍정" in line: sentiment = "긍정"
                        elif "부정" in line: sentiment = "부정"
                        else: sentiment = "중립"
            
            # 파싱 결과가 비어있으면 원본 텍스트 일부 사용
            if not news_summary: news_summary = result_text[:300] + "..."
            if not reason: reason = "상세 분석 내용을 참고하세요."

            result = {
                'news_summary': news_summary.strip(),
                'reason': reason.strip(),
                'sentiment': sentiment,
                'raw_response': result_text,
                '_cache_info': {'cached': False, 'reason': 'new_data', 'age_seconds': 0}
            }

            # 2. 결과 캐싱
            self.cache.save(stock_code, 'news', result)
            return result
            
        except Exception as e:
            print(f"[Gemini] 뉴스 분석 실패: {e}")
            return {
                'news_summary': "뉴스 정보를 가져올 수 없습니다",
                'reason': f"오류 발생: {str(e)}",
                'sentiment': "중립",
                'raw_response': ""
            }

    def fetch_market_themes(self, force_refresh=False):
        """
        오늘의 주식 시장 주도 테마를 검색하고 AI로 요약 (캐싱 적용)
        """
        # 1. 캐시 확인 (테마는 'market_themes'라는 가상의 코드로 저장)
        cached_data, _ = self.cache.load('MARKET', 'themes', force_refresh)
        if cached_data:
            return cached_data

        try:
            # 검색 쿼리: "오늘 주식 시장 주도 테마", "오늘 증시 특징주"
            search_query = "오늘 한국 주식 시장 주도 테마 특징주"
            search_results = self.search_news(search_query)
            
            context = ""
            if search_results:
                for item in search_results:
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    context += f"- {title}: {snippet}\n"
            else:
                context = "검색 결과 없음"

            prompt = f"""
            다음은 오늘 한국 주식 시장의 주요 뉴스 검색 결과입니다.
            이 정보를 바탕으로 '오늘의 주도 테마' 3가지를 요약해주세요.
            
            [검색 결과]
            {context}
            
            [요청사항]
            - 가장 강한 상승세를 보인 테마 3개를 선정하세요.
            - 각 테마별로 대표 종목이 있다면 괄호 안에 적어주세요.
            - 답변은 쉼표(,)로 구분된 한 줄의 문자열로 작성하세요.
            - 예시: 2차전지(에코프로), 반도체(삼성전자), 초전도체
            """
            
            result_text = self._call_gemini_api(prompt)
            if not result_text:
                result_text = "테마 정보 없음"
                
            result = result_text.strip()
            
            # 2. 결과 캐싱
            self.cache.save('MARKET', 'themes', result)
            return result
            
        except Exception as e:
            print(f"[Gemini] 테마 검색 실패: {e}")
            return "테마 정보 확인 불가"

    def fetch_stock_sector(self, stock_name, stock_code, force_refresh=False):
        """
        특정 종목의 섹터/테마 정보를 검색하고 AI로 추출 (캐싱 적용)
        """
        # 1. 캐시 확인
        cached_data, _ = self.cache.load(stock_code, 'sector', force_refresh)
        if cached_data:
            return cached_data

        try:
            search_query = f"{stock_name} 관련주 테마 섹터"
            search_results = self.search_news(search_query)
            
            context = ""
            if search_results:
                for item in search_results:
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    context += f"- {title}: {snippet}\n"
            
            prompt = f"""
            다음은 '{stock_name}' 종목에 대한 검색 결과입니다.
            이 종목이 속한 핵심 '섹터' 또는 '테마'를 1~2단어로 정의해주세요.
            
            [검색 결과]
            {context}
            
            [요청사항]
            - 설명 없이 핵심 섹터명만 출력하세요.
            - 예시: 반도체 장비, 2차전지 소재, 제약바이오
            """
            
            result_text = self._call_gemini_api(prompt)
            if not result_text:
                result_text = "알 수 없음"
                
            result = result_text.strip()
            
            # 2. 결과 캐싱
            self.cache.save(stock_code, 'sector', result)
            return result
            
        except Exception as e:
            print(f"[Gemini] 섹터 검색 실패: {e}")
            return "섹터 미상"

    def select_core_themes(self, stock_name, stock_code, all_themes, force_refresh=False):
        """
        종목의 전체 테마 중 핵심 테마 3~5개를 AI로 선정 (30일 캐싱)
        """
        # 1. 캐시 확인 (유효기간 30일)
        cached_data, _ = self.cache.load(stock_code, 'core_themes', force_refresh)
        if cached_data:
            return cached_data

        try:
            # 테마 이름만 추출
            theme_names = [t['theme_name'] for t in all_themes]
            theme_list_str = ", ".join(theme_names)
            
            prompt = prompts.CORE_THEME_SELECTION_PROMPT.format(
                stock_name=stock_name,
                all_themes=theme_list_str
            )
            
            result_text = self._call_gemini_api(prompt)
            if not result_text:
                return theme_names[:3] # 실패 시 앞의 3개 반환
            
            # JSON 파싱 시도
            import re
            try:
                # 대괄호 안의 내용만 추출
                match = re.search(r'\[.*\]', result_text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    core_themes = json.loads(json_str)
                else:
                    # JSON 형식이 아니면 쉼표로 분리 시도
                    core_themes = [t.strip() for t in result_text.split(',')]
            except:
                # 파싱 실패 시 원본 텍스트를 적절히 처리하거나 기본값 사용
                print(f"[Gemini] 핵심 테마 파싱 실패. Raw: {result_text}")
                core_themes = theme_names[:3]

            # 2. 결과 캐싱
            self.cache.save(stock_code, 'core_themes', core_themes)
            return core_themes
            
        except Exception as e:
            print(f"[Gemini] 핵심 테마 선정 실패: {e}")
            return []

    def generate_outlook(self, stock_name, stock_info, supply_demand, technical_indicators, news_analysis, market_data=None, fundamental_data=None, theme_service=None, force_refresh=False):
        """
        종합 정보를 바탕으로 AI 전망 생성 (캐싱 적용)
        Core + Active 테마 전략 적용
        """
        stock_code = stock_info.get('code', 'unknown')
        
        # 1. 캐시 확인
        cached_data, cache_info = self.cache.load(stock_code, 'outlook', force_refresh)
        if cached_data:
            cached_data['_cache_info'] = cache_info
            return cached_data

        try:
            # --- 테마 분석 (Core + Active) ---
            stock_sector_str = "정보 없음"
            
            if theme_service:
                # 1. 전체 테마 가져오기
                all_themes = theme_service.find_themes_by_stock(stock_code)
                
                # 2. 핵심 테마 선정 (AI)
                core_themes = self.select_core_themes(stock_name, stock_code, all_themes)
                
                # 3. 오늘 강세 테마 (Active) 필터링
                # 등락률이 1.0% 이상이거나, 상위 3개 테마
                active_themes = []
                for theme in all_themes:
                    try:
                        fluc = float(theme.get('theme_fluctuation', 0))
                        if fluc >= 1.0:
                            active_themes.append(f"{theme['theme_name']}({fluc}%)")
                    except:
                        pass
                
                # 상위 3개만 추리기
                active_themes = active_themes[:3]
                
                # 프롬프트용 문자열 구성
                stock_sector_str = f"- 핵심 테마(Identity): {', '.join(core_themes)}\n- 오늘 강세 테마(Active): {', '.join(active_themes) if active_themes else '없음 (모든 테마가 약세거나 보합)'}"
            else:
                # theme_service가 없는 경우 (기존 로직 호환)
                stock_sector_str = market_data.get('sector', '정보 없음')

            # 기술적 지표 상세 정보 추출
            rsi = technical_indicators.get('rsi', 50)
            rsi_signal = technical_indicators.get('rsi_signal', '중립')
            macd = technical_indicators.get('macd', 0)
            macd_signal = technical_indicators.get('macd_signal', '중립')
            ma5 = technical_indicators.get('ma5', 0)
            ma20 = technical_indicators.get('ma20', 0)
            ma60 = technical_indicators.get('ma60', 0)
            ma_signal = technical_indicators.get('ma_signal', '중립')
            
            # 시장 데이터 추출
            market_data = market_data or {}
            market_index_status = market_data.get('market_index', '정보 없음') # 국내 지수
            
            # 글로벌 시장 데이터 (US)
            us_indices = market_data.get('us_indices', '정보 없음')
            us_themes = market_data.get('us_themes', '정보 없음')
            
            # 국내외 시장 상황 통합
            market_context_str = f"""
            - 국내 지수: {market_index_status}
            - 미국 지수: {us_indices}
            - 미국 강세 테마: {us_themes}
            """
            
            current_hot_themes = market_data.get('themes', '정보 없음')
            # stock_sector는 위에서 계산함

            # 펀더멘털 데이터 추출
            fundamental_data = fundamental_data or {}
            
            # 시가총액 포맷팅 (억 단위 등)
            market_cap = fundamental_data.get('market_cap_raw', 'N/A')
            if market_cap != 'N/A':
                try:
                    pass
                except:
                    pass

            prompt = prompts.OUTLOOK_GENERATION_PROMPT.format(
                stock_name=stock_name,
                stock_sector=stock_sector_str,
                market_context=market_context_str, # 통합된 시장 상황 전달
                current_hot_themes=current_hot_themes,
                current_price=stock_info.get('price', 'N/A'),
                change_rate=stock_info.get('rate', 'N/A'),
                foreign_net=supply_demand.get('foreign_net', 'N/A'),
                institution_net=supply_demand.get('institution_net', 'N/A'),
                rsi=rsi,
                rsi_signal=rsi_signal,
                macd=macd,
                macd_signal=macd_signal,
                ma5=ma5,
                ma20=ma20,
                ma60=ma60,
                ma_signal=ma_signal,
                news_sentiment=news_analysis.get('sentiment', 'N/A'),
                news_reason=news_analysis.get('reason', 'N/A'),
                # 펀더멘털 데이터 추가
                market_cap=self._format_large_number(fundamental_data.get('market_cap_raw', '0')),
                per=fundamental_data.get('per', 'N/A'),
                pbr=fundamental_data.get('pbr', 'N/A'),
                roe=fundamental_data.get('roe', 'N/A'),
                operating_profit=self._format_large_number(fundamental_data.get('operating_profit_raw', '0'))
            )
            
            result_text = self._call_gemini_api(prompt)
            
            if not result_text:
                raise Exception("API 응답 없음")
            
            # 응답 파싱
            recommendation = "중립"
            confidence = 50
            trading_scenario = ""
            detailed_analysis = ""
            
            lines = result_text.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if "투자의견" in line or line.startswith("1."):
                    current_section = "recommendation"
                    if "매수" in line:
                        recommendation = "매수"
                    elif "매도" in line:
                        recommendation = "매도"
                    else:
                        recommendation = "중립"
                elif "신뢰도" in line or line.startswith("2."):
                    current_section = "confidence"
                    import re
                    # 콜론(:) 뒤의 숫자를 우선적으로 찾기
                    if ":" in line:
                        after_colon = line.split(":", 1)[1]
                        numbers = re.findall(r'\d+', after_colon)
                    else:
                        numbers = re.findall(r'\d+', line)
                    
                    if numbers:
                        confidence = min(100, max(0, int(numbers[0])))
                elif "매매 시나리오" in line or line.startswith("3."):
                    current_section = "scenario"
                    if ":" in line:
                         trading_scenario = line.split(":", 1)[-1].strip()
                elif "상세 분석" in line or line.startswith("4."):
                    current_section = "detailed_analysis"
                    if ":" in line:
                        detailed_analysis = line.split(":", 1)[-1].strip()
                
                # 섹션별 내용 수집
                elif current_section == "scenario" and line:
                    trading_scenario += "\n" + line
                elif current_section == "detailed_analysis" and line:
                    detailed_analysis += "\n" + line
            
            # 매매 시나리오에서 가격 정보 추출 (간단한 파싱)
            price_strategy = {'entry': '', 'target': '', 'stop_loss': ''}
            try:
                scenario_lines = trading_scenario.split('\n')
                for s_line in scenario_lines:
                    if "진입" in s_line:
                        price_strategy['entry'] = s_line.split(":", 1)[-1].strip()
                    elif "목표" in s_line:
                        price_strategy['target'] = s_line.split(":", 1)[-1].strip()
                    elif "손절" in s_line:
                        price_strategy['stop_loss'] = s_line.split(":", 1)[-1].strip()
            except:
                pass

            result = {
                'recommendation': recommendation,
                'confidence': confidence,
                'trading_scenario': trading_scenario.strip(),
                'price_strategy': price_strategy,
                'reasoning': detailed_analysis.strip() if detailed_analysis.strip() else result_text,
                'raw_response': result_text,
                '_cache_info': {'cached': False, 'reason': 'new_data', 'age_seconds': 0}
            }

            # 2. 결과 캐싱
            self.cache.save(stock_code, 'outlook', result)
            return result
            
        except Exception as e:
            print(f"[Gemini] 전망 생성 실패: {e}")
            return {
                'recommendation': "중립",
                'confidence': 0,
                'reasoning': f"분석 실패: {str(e)}",
                'raw_response': ""
            }

    def _format_large_number(self, value_str):
        """
        억 단위 숫자를 '조 억' 단위로 변환
        예: 5949236 -> 594조 9236억
        """
        try:
            val = int(value_str)
            if val == 0: return "0"
            
            trillion = val // 10000
            billion = val % 10000
            
            result = ""
            if trillion > 0:
                result += f"{trillion}조 "
            if billion > 0:
                result += f"{billion}억"
            
            return result.strip() + "원"
        except:
            return str(value_str)
