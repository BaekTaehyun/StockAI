import google.generativeai as genai
import config
import json
import os
import datetime

class GeminiService:
    """Google Gemini SDK를 사용한 AI 분석 서비스"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.AI_MODEL)
        
        # 캐시 디렉토리 생성
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, code, analysis_type):
        """캐시 파일 경로 생성 (종목코드_타입_날짜.json)"""
        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{code}_{analysis_type}_{today}.json"
        return os.path.join(self.cache_dir, filename)

    def _load_from_cache(self, code, analysis_type):
        """캐시에서 데이터 로드"""
        try:
            path = self._get_cache_path(code, analysis_type)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"[Cache] Loaded {analysis_type} for {code}")
                return data
        except Exception as e:
            print(f"[Cache Error] Load failed: {e}")
        return None

    def _save_to_cache(self, code, analysis_type, data):
        """데이터를 캐시에 저장"""
        try:
            path = self._get_cache_path(code, analysis_type)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[Cache] Saved {analysis_type} for {code}")
        except Exception as e:
            print(f"[Cache Error] Save failed: {e}")

    def _call_gemini_api(self, prompt_text):
        """Gemini SDK를 사용한 API 호출"""
        try:
            response = self.model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            print(f"[Gemini API Error] {e}")
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
            else:
                print(f"[Search Error] {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[Search Connection Error] {e}")
            return None

    def search_and_analyze_news(self, stock_name, stock_code, current_price=None, change_rate=None):
        """
        종목 뉴스를 검색하고 AI로 분석 (캐싱 적용)
        """
        # 1. 캐시 확인
        cached_data = self._load_from_cache(stock_code, 'news')
        if cached_data:
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

            prompt = f"""
당신은 주식 시장 애널리스트입니다. 다음 종목에 대한 최신 뉴스를 기반으로 분석해주세요.

종목 정보:
- 종목명: {stock_name}
- 종목코드: {stock_code}
{f"- 현재가: {current_price}원" if current_price else ""}
{f"- 등락률: {change_rate}%" if change_rate else ""}

{news_context}

분석 요청:
1. 위 검색된 뉴스를 바탕으로 이 종목의 주가 변동에 영향을 줄 만한 핵심 이슈를 요약하세요.
2. 전반적인 뉴스/시장 분위기 (긍정/부정/중립)를 판단하세요.

다음 형식으로 답변해주세요:
1. 주요 뉴스: [핵심 이슈 및 재료 요약]
2. 등락 원인: [3줄 요약]
3. 뉴스 분위기: [긍정/부정/중립 중 하나]
"""
            
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
                'raw_response': result_text
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
    
    def generate_outlook(self, stock_name, stock_info, supply_demand, technical_indicators, news_analysis):
        """
        종합 정보를 바탕으로 AI 전망 생성 (캐싱 적용)
        """
        stock_code = stock_info.get('code', 'unknown')
        
        # 1. 캐시 확인
        cached_data = self._load_from_cache(stock_code, 'outlook')
        if cached_data:
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
            
            prompt = f"""
당신은 전문 주식 애널리스트입니다. 다음 정보를 종합하여 투자 의견을 제시하세요.

종목: {stock_name}

1. 주가 정보:
   - 현재가: {stock_info.get('price', 'N/A')}원
   - 등락률: {stock_info.get('rate', 'N/A')}%

2. 수급 데이터:
   - 외국인 순매수: {supply_demand.get('foreign_net', 'N/A')}주
   - 기관 순매수: {supply_demand.get('institution_net', 'N/A')}주

3. 기술적 지표:
   
   [RSI - 상대강도지수]
   - 현재 RSI: {rsi} (신호: {rsi_signal})
   - 해석: 70 이상=과매수(매도 고려), 30 이하=과매도(매수 고려), 50 전후=중립
   
   [MACD - 이동평균 수렴확산]
   - 현재 MACD: {macd} (신호: {macd_signal})
   - 해석: 양수=상승 추세, 음수=하락 추세
   
   [이동평균선]
   - MA5 (5일선): {ma5:,.0f}원
   - MA20 (20일선): {ma20:,.0f}원
   - MA60 (60일선): {ma60:,.0f}원
   - 배열 상태: {ma_signal}
   - 해석: 정배열(5일>20일>60일)=강세장, 역배열=약세장, 골든크로스=매수신호, 데드크로스=매도신호

4. 뉴스 분석:
   - 뉴스 분위기: {news_analysis.get('sentiment', 'N/A')}
   - 주요 내용: {news_analysis.get('reason', 'N/A')}

위 정보를 종합하여 다음 형식으로 답변하세요:
1. 추천: [매수/매도/중립 중 하나]
2. 신뢰도: [0-100 사이의 숫자]
3. 근거: [RSI, MACD, 이동평균선 등 기술적 지표를 적극 참고하여 3-5줄로 추천 이유 설명]
"""
            
            result_text = self._call_gemini_api(prompt)
            
            if not result_text:
                raise Exception("API 응답 없음")
            
            # 응답 파싱
            recommendation = "중립"
            confidence = 50
            reasoning = result_text
            
            lines = result_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if "추천" in line or line.startswith("1."):
                    if "매수" in line:
                        recommendation = "매수"
                    elif "매도" in line:
                        recommendation = "매도"
                    else:
                        recommendation = "중립"
                elif "신뢰도" in line or line.startswith("2."):
                    import re
                    # 콜론(:) 뒤의 숫자를 우선적으로 찾기
                    if ":" in line:
                        after_colon = line.split(":", 1)[1]
                        numbers = re.findall(r'\d+', after_colon)
                    else:
                        numbers = re.findall(r'\d+', line)
                    
                    if numbers:
                        confidence = min(100, max(0, int(numbers[0])))
                elif "근거" in line or line.startswith("3."):
                    reasoning = line.split(":", 1)[-1].strip() if ":" in line else ""
                    idx = lines.index(line)
                    if idx + 1 < len(lines):
                        reasoning += " " + " ".join(lines[idx+1:])
                    break
            
            result = {
                'recommendation': recommendation,
                'confidence': confidence,
                'reasoning': reasoning.strip() if reasoning.strip() else result_text[:300],
                'raw_response': result_text
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
