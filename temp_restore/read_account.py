import pandas as pd

# 시트 목록 get
xl = pd.ExcelFile("키움 REST API 문서.xlsx")

# 167번 시트 읽기 (주식잔고요청)
sheet_name = xl.sheet_names[167]
print(f"시트 이름: {sheet_name}")

df = pd.read_excel("키움 REST API 문서.xlsx", sheet_name=sheet_name, nrows=30)
print("\n=== 주식잔고요청 (kt00018) ===")
print(df.to_string())
