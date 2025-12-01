# 디테일 창 캐시 불일치 분석 보고서

## 조사 범위

디테일 창(`ui_details.js`)이 표시하는 모든 데이터를 조사하여, 카드와 같은 캐시 불일치 문제가 있는지 확인했습니다.

## 데이터 흐름 매핑

### 1. 수급 데이터 (Supply/Demand) ✅ 수정 완료

**문제 발견:**
- 카드: `API.fetchSupplyDemand` → 캐시 없음 (항상 최신)
- 디테일: `API.fetchFullAnalysis` → 60초 캐시

**해결:**
`stock_analysis_service.py`의 `get_supply_demand_data()`에 캐시 업데이트 로직 추가

---

### 2. 주가 정보 (Price Info) ⚠️ 주의

**현재 상태:**
- 카드: `API.fetchHoldings` → `/api/account/balance` → `kiwoom.get_account_balance()` (캐시 없음)
- 디테일: `API.fetchFullAnalysis` → `get_full_analysis()` → `price_cache_key` (60초 캐시)
- 추가 엔드포인트: `/api/price/<code>` → `kiwoom.get_current_price()` (캐시 없음)

**잠재적 문제:**
현재 `/api/price/<code>` 엔드포인트는 **프론트엔드에서 사용되지 않음**. 
만약 향후 카드나 다른 곳에서 이 엔드포인트를 직접 호출하면 불일치 발생 가능.

**권장 조치:**
필요 시 `/api/price/<code>` 엔드포인트도 `StockAnalysisService`의 캐시를 업데이트하도록 수정.

---

### 3. 차트 데이터 (Chart Data) ✅ 문제 없음

**현재 상태:**
- 디테일: `API.fetchFullAnalysis` → `chart_cache_key` (60초 캐시)
- 추가 엔드포인트: `/api/chart/minute/<code>` → 분봉 데이터 (별도, 디테일 창에서 사용 안 함)

**결론:**
차트 데이터는 `get_full_analysis()`에서만 조회되므로 불일치 문제 없음.

---

### 4. 펀더멘털 데이터 (Fundamental) ✅ 문제 없음

**현재 상태:**
- 디테일: `API.fetchFullAnalysis` → `fundamental_key` (300초 = 5분 캐시)

**결론:**
펀더멘털 데이터는 `get_full_analysis()`에서만 조회되므로 불일치 문제 없음.

---

### 5. 뉴스 분석 (News Analysis) ✅ 문제 없음

**현재 상태:**
- 디테일: `API.fetchFullAnalysis` → `gemini_service.search_and_analyze_news()` → `GeminiCache` (30분 캐시)
- 추가 엔드포인트: `/api/analysis/news/<code>` → 직접 `search_and_analyze_news()` 호출

**중요:**
`GeminiCache`는 **파일 기반 캐시**이므로, 어느 엔드포인트에서 호출하든 **동일한 캐시**를 공유합니다.

```python
# gemini_service.py
def search_and_analyze_news(...):
    cached_data, cache_info = self.cache.load(stock_code, 'news', force_refresh)
    if cached_data:
        return cached_data
    # ... (새 데이터 생성)
    self.cache.save(stock_code, 'news', result)
```

**결론:**
뉴스 데이터는 파일 캐시 공유로 불일치 문제 없음. ✅

---

### 6. AI 전망 (Outlook) ✅ 문제 없음

**현재 상태:**
- 디테일: `API.fetchFullAnalysis` → `gemini_service.generate_outlook()` → `GeminiCache` (30분 캐시)

**중요:**
AI 전망도 `GeminiCache`를 사용하므로 파일 기반 캐시 공유.

```python
# gemini_service.py
def generate_outlook(...):
    cached_data, cache_info = self.cache.load(stock_code, 'outlook', force_refresh)
    if cached_data:
        return cached_data
    # ... (새 데이터 생성)
    self.cache.save(stock_code, 'outlook', result)
```

**결론:**
AI 전망은 파일 캐시 공유로 불일치 문제 없음. ✅

---

### 7. 시장 지수 (Market Indices) ✅ 문제 없음

**현재 상태:**
- 메인: `API.fetchMarketIndices` → `/api/market/indices` → `kiwoom.get_market_index()` (캐시 없음)
- 디테일: `get_full_analysis()` → `market_index_key` (60초 캐시)

**결론:**
시장 지수는 메인 페이지에서만 사용되고, 디테일 창에는 표시되지 않으므로 불일치 문제 없음.

---

## 캐시 전략 요약

### StockAnalysisService (메모리 캐시)
- `_memory_cache` 딕셔너리 사용
- TTL: 대부분 60초, 펀더멘털은 300초
- **문제점**: 인스턴스별로 캐시가 분리됨 (각 API 요청마다 새 인스턴스 생성)

```python
# app.py - 매번 새 인스턴스 생성!
analysis_service = StockAnalysisService()
```

**실제 영향**: 
현재는 각 API 요청이 독립적이므로 문제 없으나, 만약 장시간 실행되는 서비스로 변경 시 주의 필요.

### GeminiCache (파일 캐시)
- `cache/` 디렉토리에 JSON 파일로 저장
- TTL: 30분
- **장점**: 모든 프로세스/인스턴스에서 캐시 공유 ✅

---

## 종합 결론

### 현재 발견된 문제
1. ✅ **수급 데이터** - 수정 완료 (`get_supply_demand_data`에 캐시 업데이트 추가)

### 잠재적 문제 (현재는 발생하지 않음)
1. ⚠️ **주가 정보**: `/api/price/<code>` 엔드포인트가 사용되면 불일치 가능
2. ⚠️ **StockAnalysisService 인스턴스**: 장시간 실행 시 인스턴스 간 캐시 불일치 가능

### 문제 없는 데이터
- ✅ 차트 데이터
- ✅ 펀더멘털 데이터  
- ✅ 뉴스 분석 (파일 캐시)
- ✅ AI 전망 (파일 캐시)
- ✅ 시장 지수

---

## 권장 사항

### 1. 즉시 조치 필요 ❌ 없음
현재 프론트엔드에서 문제가 되는 엔드포인트는 없습니다.

### 2. 향후 개선 사항

#### Option A: 컨트롤러에서 캐시 업데이트 강제
개별 API 엔드포인트가 `StockAnalysisService`의 캐시를 업데이트하도록 수정

```python
# app.py 예시
@app.route('/api/price/<code>')
def get_price(code):
    price_info = kiwoom.get_current_price(code)
    
    # 캐시 업데이트 (옵션)
    from stock_analysis_service import StockAnalysisService
    analysis = StockAnalysisService()
    analysis._set_cached_data(f"price_{code}", price_info, ttl=60)
    
    return jsonify({'success': True, 'data': price_info})
```

#### Option B: 싱글톤 패턴 적용
`StockAnalysisService`를 싱글톤으로 만들어 모든 요청이 동일한 캐시 인스턴스 사용

```python
# app.py
analysis_service = StockAnalysisService()  # 전역으로 한 번만 생성

@app.route('/api/analysis/full/<code>')
def get_full_analysis(code):
    # 기존 인스턴스 재사용
    result = analysis_service.get_full_analysis(code)
    return jsonify(result)
```

#### Option C: Redis 같은 중앙 캐시 사용
파일 캐시(`GeminiCache`)처럼 중앙 집중식 캐시 시스템 도입

---

## 모니터링 포인트

향후 새로운 기능 추가 시 다음 사항 확인:
1. ✅ 새 API 엔드포인트가 `get_full_analysis` 외부에서 데이터를 조회하는가?
2. ✅ 해당 데이터가 디테일 창에도 표시되는가?
3. ✅ 그렇다면 캐시 업데이트 로직이 필요한가?
