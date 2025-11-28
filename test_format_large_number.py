"""
formatLargeNumber 함수 테스트
"""

# 테스트 케이스
test_cases = [
    ("삼성전자 시가총액", 594923600000000),  # 594.9조원
    ("삼성전자 영업이익", 32726000000000),   # 32.7조원
    ("중형주 시가총액", 5000000000000),      # 5조원
    ("소형주 시가총액", 800000000000),       # 8000억원
    ("소규모 영업이익", 50000000000),        # 500억원
    ("영 값", 0),
]

def format_large_number_py(value):
    """Python 버전의 formatLargeNumber (JavaScript 로직 재현)"""
    if not value or value == 0:
        return 'N/A'
    
    billion = 100000000  # 1억
    trillion = 1000000000000  # 1조
    
    if value >= trillion:
        # 조 단위로 표시
        jo = value / trillion
        return f"{jo:.1f}조원"
    else:
        # 억 단위로 표시
        eok = value / billion
        return f"{int(eok):,}억원"

print("formatLargeNumber 함수 테스트")
print("="*60)

for name, value in test_cases:
    result = format_large_number_py(value)
    print(f"{name:20s}: {value:>20,} -> {result}")

print("\n" + "="*60)
print("결과:")
print("  - 1조 이상: X.X조원 형식")
print("  - 1조 미만: X,XXX억원 형식")
print("="*60)
