# 주식 분석 기능 설치 및 사용 가이드

## 📦 패키지 설치

터미널에서 다음 명령어를 실행하세요:

```bash
cd d:\주식모니터링
python -m pip install pandas pandas-ta google-generativeai
```

## 🔑 Gemini API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. "Get API Key" 클릭
3. API 키 복사
4. `config.py` 파일 열기
5. 아래 라인 찾아서 API 키 입력:
   ```python
   GEMINI_API_KEY = "your_gemini_api_key_here"  # 여기에 발급받은 키 붙여넣기
   ```

## ✅ 구현된 기능

### 백엔드 (Flask API)
- `/api/analysis/full/<code>` - **종합 분석** (추천)
- `/api/analysis/supply-demand/<code>` - 수급 데이터만
- `/api/analysis/news/<code>` - 뉴스 분석만

### 프론트엔드 (웹 UI)
- 종목 카드 클릭 시 상세 분석 모달 표시
- **4개 탭**:
  1. **종합**: AI 투자 의견 + 주가/수급/뉴스 요약
  2. **수급**: 외국인/기관 매매 상세
  3. **뉴스**: Gemini가 분석한 뉴스 요약 및 등락 원인
  4. **기술적분석**: RSI, MACD, 이동평균선

### AI 기능 (Gemini)
- 🔍 실시간 뉴스 검색 (Gemini grounding)
- 📊 뉴스 기반 등락 원인 분석
- 💡 종합 정보 기반 투자 의견 (매수/매도/중립)
- 🎯 신뢰도 점수 제공

## 🚀 실행 방법

```bash
python app.py
```

브라우저에서 http://localhost:5000 접속 후 보유 종목을 클릭하세요!

## ⚠️ 주의사항

### Kiwoom API 수급 데이터
현재 `kis_api.py`의 `get_investor_trading()` 메서드는 **예상 구조**로 작성되었습니다.
실제 Kiwoom REST API 문서에서 다음을 확인해주세요:
- 정확한 TR 코드 (현재: ka10008)
- API 엔드포인트 URL
- 응답 데이터 필드명

### 기술적 지표
현재 일봉 데이터를 가져오는 API가 없어 기본값으로 표시됩니다.
일봉 API 추가 후 `technical_indicators.py` 활성화 필요

### Gemini API 무료 한도
- 분당 60 requests (무료 티어)
- 초과 시 유료 전환 또는 대기 필요

## 🎨 커스터마이징

### AI 모델 변경
`config.py`에서:
```python
AI_MODEL = "gemini-1.5-flash"  # 또는 "gemini-1.5-pro"
```

### 뉴스 검색 기간 변경
```python
NEWS_SEARCH_DAYS = 3  # 1~7일 권장
```

## 🐛 트러블슈팅

### "gemini_service" 모듈을 찾을 수 없습니다
→ `google-generativeai` 패키지가 설치되지 않았습니다. 위 설치 명령어 실행

### "API key not valid"
→ `config.py`의 `GEMINI_API_KEY`를 올바르게 입력했는지 확인

### 수급 데이터가 0으로 표시됨
→ Kiwoom API 문서에서 정확한 TR 코드 및 필드명 확인 필요
