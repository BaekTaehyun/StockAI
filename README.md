# 키움 주식 모니터링 시스템

키움증권 REST API를 활용한 실시간 주식 모니터링 및 AI 기반 투자 분석 시스템입니다.

## 주요 기능

- ✅ 실시간 보유 종목 조회 및 수익률 표시
- ✅ 시장 지수 (KOSPI, KOSDAQ) 모니터링
- ✅ 기술적 분석 (RSI, MACD, 이동평균선)
- ✅ AI 기반 뉴스 분석 및 투자 의견
- ✅ 수급 현황 (외국인/기관 매매 동향)

## 설치 방법

### 1. 필수 요구사항
- Python 3.8 이상
- 키움증권 REST API 계정 (https://www.kiwoom.com/)
- Google Gemini API 키 (https://makersuite.google.com/app/apikey)

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 설정 파일 구성
1. `config.py.template`을 `config.py`로 복사
2. `config.py`에 본인의 API 키 입력:
   - `APP_KEY`: 키움 API 키
   - `APP_SECRET`: 키움 시크릿 키
   - `ACCOUNT_NO`: 계좌번호
   - `GEMINI_API_KEY`: Google Gemini API 키

```bash
copy config.py.template config.py
# config.py 파일을 편집기로 열어서 키 입력
```

### 4. 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 프로젝트 구조

```
주식모니터링/
├── app.py                      # Flask 메인 애플리케이션
├── kis_api.py                  # 키움 REST API 클라이언트
├── stock_analysis_service.py   # 주식 분석 서비스
├── technical_indicators.py     # 기술적 지표 계산
├── gemini_service.py          # AI 분석 서비스
├── config.py                  # 설정 파일 (⚠️ git에 커밋 금지)
├── static/                    # 정적 파일 (CSS, JS)
│   ├── style.css
│   └── script.js
└── templates/                 # HTML 템플릿
    └── index.html
```

## 보안 주의사항

⚠️ **중요**: 다음 파일들은 절대 공개 저장소에 업로드하지 마세요!
- `config.py` - API 키 포함
- `*.txt` (키 파일들)
- `cache/` 폴더

`.gitignore` 파일이 이미 설정되어 있으니 확인하세요.

## 라이선스

개인 프로젝트용

## 문의

문제가 발생하면 Issue를 등록해주세요.
