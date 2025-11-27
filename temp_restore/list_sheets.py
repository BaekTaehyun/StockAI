import pandas as pd

# 시트 목록 확인
xl = pd.ExcelFile("키움 REST API 문서.xlsx")
print("시트 목록:")
for i, sheet in enumerate(xl.sheet_names):
    print(f"{i}: {sheet}")

# "계좌" 관련 시트 찾기
print("\n=== '계좌' 포함 시트 ===")
for sheet in xl.sheet_names:
    if '계좌' in sheet or '잔고' in sheet or 'kt' in sheet:
        print(f"  - {sheet}")
