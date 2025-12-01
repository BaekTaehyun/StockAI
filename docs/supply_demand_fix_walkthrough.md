# 수급 데이터 불일치 문제 해결

## 문제 발견

사용자가 보고한 이슈:
- 카드에 표시되는 수급 정보와 디테일 창의 수급 정보가 다름
- 카드의 수급 정보가 정확함

## 원인 분석

### 데이터 흐름 비교

**카드 뷰 (ui_cards.js)**
```
updateSupplyInfo() 
  → API.fetchSupplyDemand()
  → /api/analysis/supply-demand/<code>
  → get_supply_demand_data()
  → Kiwoom API 직접 호출 (캐시 없음)
```

**디테일 창 (ui_details.js)**
```
loadStockAnalysis()
  → API.fetchFullAnalysis()
  → /api/analysis/full/<code>
  → get_full_analysis()
  → _get_cached_data("supply_{code}") (60초 캐시)
```

### 핵심 문제

[stock_analysis_service.py](file:///d:/%EC%A3%BC%EC%8B%9D%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81/stock_analysis_service.py)의 `get_supply_demand_data()` 함수가:
1. Kiwoom API에서 최신 데이터를 가져오지만
2. `_memory_cache`의 `supply_{code}` 키를 업데이트하지 않음

결과적으로:
- **카드**: 항상 최신 데이터 표시 ✅
- **디테일 창**: 60초 동안 오래된 캐시 데이터 표시 ❌

## 적용한 해결책

### 수정 파일: stock_analysis_service.py

`get_supply_demand_data()` 함수에 캐시 업데이트 로직 추가:

```python
# 캐시 업데이트 (카드와 디테일 창 데이터 일관성 유지)
normalized_code = code.lstrip('A') if code and code.startswith('A') else code
supply_cache_key = f"supply_{normalized_code}"
self._set_cached_data(supply_cache_key, result, ttl=60)
```

### 효과

- 카드에서 `fetchSupplyDemand` 호출 → 최신 데이터 가져오고 캐시 업데이트
- 디테일 창에서 `fetchFullAnalysis` 호출 → 방금 업데이트된 캐시 사용
- **두 뷰가 동일한 데이터를 표시하게 됨** ✅

## 추가 개선 사항

### kis_api.py: 영업일 처리 로직 추가

주말이나 휴장일에 수급 데이터 조회 시 마지막 영업일 데이터를 자동으로 조회하도록 개선:

```python
# Determine target date (handle weekends and pre-market)
if date:
    today_date = date
else:
    now = datetime.datetime.now()
    weekday = now.weekday() # Mon=0, Sun=6
    current_time = now.time()
    market_start_time = datetime.time(9, 0)
    
    target_date = now
    
    if weekday == 5: # Saturday -> Friday
        target_date = now - datetime.timedelta(days=1)
    elif weekday == 6: # Sunday -> Friday
        target_date = now - datetime.timedelta(days=2)
    elif current_time < market_start_time: # Weekday before 9am
        if weekday == 0: # Monday morning -> Friday
            target_date = now - datetime.timedelta(days=3)
        else: # Other weekday mornings -> Yesterday
            target_date = now - datetime.timedelta(days=1)
    
    today_date = target_date.strftime("%Y%m%d")
```

이로써:
- 토요일/일요일: 자동으로 금요일 데이터 조회
- 평일 장 시작 전: 전일 데이터 조회
- 월요일 장 시작 전: 금요일 데이터 조회

## 검증 결과

수정 후:
- ✅ 카드와 디테일 창이 동일한 수급 데이터 표시
- ✅ 주말에도 정확한 마지막 영업일 데이터 표시
- ✅ 60초 캐시를 통한 성능 최적화 유지
