# 📈 StockAI - AI 기반 한국 주식 모니터링 대시보드

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Custom-red.svg)](#license)

키움증권 OpenAPI와 Google Gemini AI를 활용한 실시간 주식 모니터링 및 AI 투자 분석 웹 애플리케이션입니다.

![StockAI Dashboard](docs/screenshot.png)

## ✨ 주요 기능

### 🤖 AI 기반 투자 분석
- **Google Gemini AI 통합**: 종목별 맞춤형 투자 의견 자동 생성
- **다층 캐싱 시스템**: 메모리(10분) + 파일(60분) 티어드 캐싱으로 빠른 응답
- **실시간 시장 분석**: 기본적/기술적 분석 결합

### 📊 실시간 데이터 모니터링
- 보유 종목 실시간 가격 추적
- 시장 지수 (KOSPI/KOSDAQ) 모니터링
- 외국인/기관 수급 정보
- 관심 종목 관리

### 📈 기술적 분석
- RSI (상대강도지수)
- MACD (이동평균 수렴확산)
- 이동평균선 (5/20/60일)
- 실시간 차트 시각화

### 💡 스마트 UI/UX
- 모바일 반응형 디자인
- 다크 테마
- 실시간 업데이트
- 직관적인 대시보드

## 🚀 시작하기

### 필수 요구사항

- Python 3.8 이상
- 키움증권 계좌 (OpenAPI 이용 신청 필요)
- Google Gemini API 키

### 설치

1. **저장소 클론**
```bash
git clone https://github.com/BaekTaehyun/StockAI.git
cd StockAI
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경 설정**
`config.py.template`을 `config.py`로 복사하고 API키 입력:
```python
# API 키 설정
GEMINI_API_KEY = "your-gemini-api-key"
APP_KEY = "your-kiwoom-app-key"
APP_SECRET = "your-kiwoom-app-secret"
ACCOUNT_NO = "your-account-number"
```

### 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 📁 프로젝트 구조

```
StockAI/
├── app.py                      # Flask 메인 애플리케이션
├── config.py.template          # 설정 템플릿
├── requirements.txt            # Python 의존성
│
├── kis_api.py                  # 키움증권 API 연동
├── gemini_service.py          # Gemini AI 서비스
├── gemini_cache.py            # AI 응답 캐싱
├── stock_analysis_service.py  # 주식 분석 로직
├── technical_indicators.py    # 기술적 지표 계산
├── prompts.py                 # AI 프롬프트 관리
│
├── static/
│   ├── css/                   # 스타일시트
│   └── js/                    # JavaScript 모듈
│       ├── main.js           # 메인 로직
│       ├── api.js            # API 통신
│       ├── ui_core.js        # 핵심 UI 기능
│       ├── ui_cards.js       # 카드 UI 렌더링
│       └── ui_details.js     # 상세 모달 UI
│
└── templates/
    └── index.html             # 메인 템플릿
```

## 🔑 API 키 발급

### 1. Google Gemini API
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. "Get API Key" 클릭
3. 새 API 키 생성

### 2. 키움증권 OpenAPI
1. [키움증권 OpenAPI](https://apiportal.koreainvestment.com/) 접속
2. 회원가입 및 앱 등록
3. App Key, App Secret 발급

## 💻 기술 스택

**Backend**
- Python 3.8+
- Flask 2.0+
- Google Gemini AI API

**Frontend**
- Vanilla JavaScript (ES6+)
- Chart.js (차트 시각화)
- CSS3 (Flexbox, Grid)

**데이터**
- 한국투자증권(키움) OpenAPI
- JSON 파일 기반 캐싱

## 📝 사용 예시

### 1. 보유 종목 확인
대시보드에서 실시간으로 보유 종목의 가격 변동과 수익률을 확인할 수 있습니다.

### 2. AI 투자 분석
종목 카드 클릭 시 Gemini AI가 생성한 맞춤형 투자 의견을 확인:
- 매수/매도/중립 추천
- 신뢰도 점수
- 상세 분석 근거
- 목표가 제시

### 3. 기술적 분석
모달의 "기술적분석" 탭에서 RSI, MACD, 이동평균선 등의 지표를 시각적으로 확인

## 🤝 기여하기

이 프로젝트는 개인 프로젝트이지만, 개선 제안과 이슈 리포트를 환영합니다!

## 📧 연락처

- **작성자**: 백태현 (Baek Taehyun)
- **이메일**: bak1210@gmail.com
- **GitHub**: [BaekTaehyun](https://github.com/BaekTaehyun)

## 📄 License

이 프로젝트는 사용자 지정 라이선스 하에 배포됩니다. 
**사용 시 이메일 연락을 부탁드립니다**: bak1210@gmail.com

자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## ⚠️ 면책조항

이 애플리케이션은 정보 제공 목적으로만 제공되며, 투자 권유나 투자 조언이 아닙니다. 
모든 투자 결정은 사용자 본인의 책임하에 이루어져야 합니다.

## 🙏 감사의 말

- [Google Gemini AI](https://ai.google.dev/) - AI 분석 제공
- [한국투자증권](https://www.koreainvestment.com/) - 주식 데이터 API 제공

---

⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!
