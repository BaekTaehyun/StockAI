import google.generativeai as genai
import config
import json
import os
import datetime

import prompts

class GeminiService:
    """Google Gemini SDK를 사용한 AI 분석 서비스"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.AI_MODEL)
        
        # 캐시 디렉토리 생성
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # 메모리 캐시 초기화 (파일 I/O 감소 및 실패 대비)
        # 구조: { 'key': { 'data': ..., 'timestamp': ... } }
        self._memory_cache = {}
    
    def _get_cache_path(self, code, analysis_type):
        """캐시 파일 경로 생성 (종목코드_타입_날짜.json)"""
        # 종목 코드 정규화 (A 접두사 제거)
        normalized_code = code.lstrip('A') if code and code.startswith('A') else code
        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{normalized_code}_{analysis_type}_{today}.json"
        path = os.path.join(self.cache_dir, filename)
        # print(f"[DEBUG] Cache path: {code} → {normalized_code} → {filename}")
        return path

    def _load_from_cache(self, code, analysis_type, force_refresh=False):
        """
        캐시에서 데이터 로드 (메모리 -> 파일 순서)
        - force_refresh=True: 캐시 무시하고 (None, dict) 반환
        - 파일 수정 시간이 30분(1800초) 이상 지났으면 만료 처리
        Returns:
            (data, cache_info) - data는 캐싱된 데이터 또는 None, cache_info는 캐시 상태 정보
        """
        cache_info = {'cached': False, 'reason': '', 'age_seconds': 0}
        
        if force_refresh:
            # print(f"[Cache] Force refresh requested for {code} ({analysis_type})")
            cache_info['reason'] = 'force_refresh'
            return None, cache_info

        current_time = datetime.datetime.now().timestamp()
        cache_key = f"{code}_{analysis_type}"

        # 1. 메모리 캐시 확인
        if cache_key in self._memory_cache:
            mem_data = self._memory_cache[cache_key]
            age = current_time - mem_data['timestamp']
            if age <= 1800:
                # print(f"[Memory Cache] HIT for {code} ({analysis_type})")
                cache_info['cached'] = True
                cache_info['reason'] = 'memory_hit'
                cache_info['age_seconds'] = age
                return mem_data['data'], cache_info
            else:
                # 메모리 캐시 만료 -> 삭제
                del self._memory_cache[cache_key]

        try:
            path = self._get_cache_path(code, analysis_type)
            if os.path.exists(path):
                # 30분(1800초) 만료 체크
                mtime = os.path.getmtime(path)
                age = current_time - mtime
                
                if age > 1800:
                    # print(f"[Cache] Expired (Age: {age:.1f}s > 1800s) for {code} ({analysis_type})")
                    cache_info['reason'] = f'expired ({age:.1f}s > 1800s)'
                    cache_info['age_seconds'] = age
                    return None, cache_info
                
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 파일 캐시 적중 시 메모리 캐시에도 업데이트
                self._memory_cache[cache_key] = {
                    'data': data,
                    'timestamp': mtime
                }
                
                # print(f"[Cache] HIT for {code} ({analysis_type}) - Age: {age:.1f}s")
                cache_info['cached'] = True
                cache_info['reason'] = 'hit'
                cache_info['age_seconds'] = age
                return data, cache_info
            else:
                # print(f"[Cache] MISS (File not found) for {code} ({analysis_type})")
                cache_info['reason'] = 'not_found'
        except Exception as e:
            print(f"[Cache Error] Load failed: {e}")
            cache_info['reason'] = f'error: {str(e)}'
        return None, cache_info

    def _save_to_cache(self, code, analysis_type, data):
        """데이터를 캐시에 저장 (메모리 + 파일 Atomic Write)"""
        try:
            # 1. 메모리 캐시 저장
            cache_key = f"{code}_{analysis_type}"
            self._memory_cache[cache_key] = {
                'data': data,
                'timestamp': datetime.datetime.now().timestamp()
            }

            # 2. 파일 캐시 저장 (Atomic Write: 임시 파일 -> 이름 변경)
            path = self._get_cache_path(code, analysis_type)
            temp_path = path + ".tmp"
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 윈도우에서는 rename 시 대상 파일이 있으면 에러가 발생할 수 있으므로 replace 사용
            if os.path.exists(path):
                os.remove(path)
            os.rename(temp_path, path)
            
            # print(f"[Cache] Saved {analysis_type} for {code}")
        except Exception as e:
            print(f"[Cache Error] Save failed: {e}")
            # 임시 파일 정리
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass


    def _call_gemini_api(self, prompt_text):
        """Gemini SDK를 사용한 API 호출 (60초 timeout)"""
        try:
            # timeout 설정: 60초
            response = self.model.generate_content(
                prompt_text,
                request_options={'timeout': 60}
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
                
        except Exception as e:
            print(f"[Gemini API Error] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def search_news(self, query):
        """Google Custom Search API를 사용한 뉴스 검색"""
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
        종목 뉴스를 검색하고 AI로 분석 (캐싱 적용)
        """
        # 1. 캐시 확인
        cached_data, cache_info = self._load_from_cache(stock_code, 'news', force_refresh)
        if cached_data:
            cached_data['_cache_info'] = cache_info
            return cached_data

        try:
            search_query = f"{stock_name} 주식 뉴스"
            search_results = self.search_news(search_query)
            
            news_context = ""
            if search_results:
                news_context = "검색된 최신 뉴스:\n"
                for item in search_results:
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    news_context += f"- [{title}] {snippet} ({link})\n"
            else:
                news_context = "(최신 뉴스 검색 실패 또는 설정되지 않음. 일반적인 지식에 기반하여 분석하세요.)"

            prompt = prompts.NEWS_ANALYSIS_PROMPT.format(
                stock_name=stock_name,
                stock_code=stock_code,
                price_info=f"- 현재가: {current_price}원" if current_price else "",
                change_info=f"- 등락률: {change_rate}%" if change_rate else "",
                news_context=news_context
            )
            
            result_text = self._call_gemini_api(prompt)
            
            if not result_text:
                raise Exception("API 응답 없음")
            
            # 응답 파싱
            news_summary = ""
            reason = ""
            sentiment = "중립"
            
            lines = result_text.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if "주요 뉴스" in line or line.startswith("1."):
                    current_section = "news"
                    news_summary = line.split(":", 1)[-1].strip() if ":" in line else ""
                elif "등락 원인" in line or line.startswith("2."):
                    current_section = "reason"
                    reason = line.split(":", 1)[-1].strip() if ":" in line else ""
                elif "뉴스 분위기" in line or "분위기" in line or line.startswith("3."):
                    sentiment_line = line.split(":", 1)[-1].strip() if ":" in line else line
                    if "긍정" in sentiment_line:
                        sentiment = "긍정"
                    elif "부정" in sentiment_line:
                        sentiment = "부정"
                    else:
                        sentiment = "중립"
                elif current_section == "news" and line:
                    news_summary += " " + line
                elif current_section == "reason" and line:
                    reason += " " + line
            
            result = {
                'news_summary': news_summary.strip() if news_summary else result_text[:200],
                'reason': reason.strip() if reason else "분석 정보 없음",
                'sentiment': sentiment,
                'raw_response': result_text,
                '_cache_info': {'cached': False, 'reason': 'new_data', 'age_seconds': 0}
            }

            # 2. 결과 캐싱
            self._save_to_cache(stock_code, 'news', result)
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
        cached_data, _ = self._load_from_cache('MARKET', 'themes', force_refresh)
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
            self._save_to_cache('MARKET', 'themes', result)
            return result
            
        except Exception as e:
            print(f"[Gemini] 테마 검색 실패: {e}")
            return "테마 정보 확인 불가"

    def fetch_stock_sector(self, stock_name, stock_code, force_refresh=False):
        """
        특정 종목의 섹터/테마 정보를 검색하고 AI로 추출 (캐싱 적용)
        """
        # 1. 캐시 확인
        cached_data, _ = self._load_from_cache(stock_code, 'sector', force_refresh)
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
            self._save_to_cache(stock_code, 'sector', result)
            return result
            
        except Exception as e:
            print(f"[Gemini] 섹터 검색 실패: {e}")
            return "섹터 미상"

    
    def generate_outlook(self, stock_name, stock_info, supply_demand, technical_indicators, news_analysis, market_data=None, fundamental_data=None, force_refresh=False):
        """
        종합 정보를 바탕으로 AI 전망 생성 (캐싱 적용)
        """
        stock_code = stock_info.get('code', 'unknown')
        
        # 1. 캐시 확인
        cached_data, cache_info = self._load_from_cache(stock_code, 'outlook', force_refresh)
        if cached_data:
            cached_data['_cache_info'] = cache_info
            return cached_data

        try:
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
            market_index_status = market_data.get('market_index', '정보 없음')
            current_hot_themes = market_data.get('themes', '정보 없음')
            stock_sector = market_data.get('sector', '정보 없음')

            # 펀더멘털 데이터 추출
            fundamental_data = fundamental_data or {}
            
            # 시가총액 포맷팅 (억 단위 등)
            market_cap = fundamental_data.get('market_cap_raw', 'N/A')
            if market_cap != 'N/A':
                try:
                    # API가 억단위로 주는지 원단위로 주는지에 따라 다르지만, 
                    # test_api_fields 결과 "7780" -> 삼성전자 시총 500조. 
                    # 7780 * 100000000 = 7780억? 너무 작음.
                    # 삼성전자 시가총액은 약 400조원. 
                    # API 응답 "cap": "7780" -> 이게 7780조일리는 없고.
                    # 아마 모의투자 서버라 데이터가 이상하거나, 단위가 다를 수 있음.
                    # 일단 있는 그대로 보여주되 "API 데이터"라고 명시하거나, 
                    # 억 단위로 가정하고 포맷팅.
                    # 여기서는 raw 값을 그대로 쓰되 단위는 프롬프트가 알아서 판단하게 둠.
                    pass
                except:
                    pass

            prompt = prompts.OUTLOOK_GENERATION_PROMPT.format(
                stock_name=stock_name,
                stock_sector=stock_sector,
                market_index_status=market_index_status,
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

            
            # 디버깅: 프롬프트 확인
            # 디버깅: 프롬프트 전체 출력
            # 디버깅: 프롬프트 확인 (필요시 주석 해제)
            # print(f"\n{'='*50}\n[Debug] Generated Prompt:\n{prompt}\n{'='*50}\n")

            
            result_text = self._call_gemini_api(prompt)
            
            if not result_text:
                raise Exception("API 응답 없음")
            
            # 응답 파싱
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
                'reasoning': detailed_analysis.strip() if detailed_analysis.strip() else result_text[:500],
                'raw_response': result_text,
                '_cache_info': {'cached': False, 'reason': 'new_data', 'age_seconds': 0}
            }

            # 2. 결과 캐싱
            self._save_to_cache(stock_code, 'outlook', result)
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
