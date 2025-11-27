import re

# 테스트 케이스
test_lines = [
    "2. 신뢰도: 65%",
    "2. 신뢰도: 75",
    "신뢰도: 80%",
    "2.신뢰도:90",
    "신뢰도 85%",
]

print("신뢰도 파싱 테스트:")
print("=" * 50)

for line in test_lines:
    # 콜론(:) 뒤의 숫자를 우선적으로 찾기
    if ":" in line:
        after_colon = line.split(":", 1)[1]
        numbers = re.findall(r'\d+', after_colon)
    else:
        numbers = re.findall(r'\d+', line)
    
    if numbers:
        confidence = min(100, max(0, int(numbers[0])))
        print(f"입력: '{line}'")
        print(f"추출된 신뢰도: {confidence}")
        print("-" * 50)
    else:
        print(f"입력: '{line}'")
        print("✗ 숫자를 찾을 수 없음")
        print("-" * 50)
