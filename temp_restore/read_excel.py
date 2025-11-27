import pandas as pd

# Excel 파일 읽기
excel_file = "키움 REST API 문서.xlsx"

# 모든 시트 이름 확인
xl = pd.ExcelFile(excel_file)
print("시트 목록:")
for sheet in xl.sheet_names:
    print(f"  - {sheet}")

print("\n" + "="*50)

# 각 시트의 첫 몇 행 확인
for sheet in xl.sheet_names[:5]:  # 처음 5개 시트만
    print(f"\n[{sheet}]")
    df = pd.read_excel(excel_file, sheet_name=sheet, nrows=10)
    print(df.to_string())
    print("-" * 50)
