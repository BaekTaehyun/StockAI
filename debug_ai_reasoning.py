import sys
sys.path.append('d:/주식모니터링')

from gemini_service import GeminiService

# 현대차 outlook 캐시 확인
service = GeminiService()

# 캐시 삭제 후 새로 생성
import os
cache_files = [f for f in os.listdir('cache') if '005380' in f and 'outlook' in f]
print(f"Found cache files: {cache_files}")

# 강제로 새 분석 요청
stock_info = {
    'code': '005380',
    'price': 260000,
    'rate': 0.5
}

supply_demand = {
    'foreign_net': 100000,
    'institution_net': 50000
}

technical = {
    'rsi': 55,
    'rsi_signal': '중립',
    'macd': 100,
    'macd_signal': '상승',
    'ma5': 255000,
    'ma20': 250000,
    'ma60': 245000,
    'ma_signal': '상승'
}

news = {
    'sentiment': '중립',
    'reason': '전기차 경쟁 심화'
}

result = service.generate_outlook(
    '현대차', 
    stock_info, 
    supply_demand, 
    technical, 
    news,
    force_refresh=True
)

print("\n=== REASONING 필드 길이 ===")
print(f"Length: {len(result.get('reasoning', ''))}")
print(f"\n=== REASONING 필드 내용 (처음 500자) ===")
print(result.get('reasoning', '')[:500])
print(f"\n=== REASONING 필드 내용 (마지막 500자) ===")
print(result.get('reasoning', '')[-500:])

print(f"\n=== RAW_RESPONSE 길이 ===")
print(f"Length: {len(result.get('raw_response', ''))}")
