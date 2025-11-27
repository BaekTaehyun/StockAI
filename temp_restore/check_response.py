import pandas as pd

# kt00018 응답 필드 찾기
xl = pd.ExcelFile("키움 REST API 문서.xlsx")
sheet_name = xl.sheet_names[167]

df = pd.read_excel("키움 REST API 문서.xlsx", sheet_name=sheet_name)

# Response Body 부분 찾기
response_start = df[df.apply(lambda row: row.astype(str).str.contains('Response', case=False, na=False).any(), axis=1)].index[1] if len(df[df.apply(lambda row: row.astype(str).str.contains('Response', case=False, na=False).any(), axis=1)]) > 1 else None

if response_start:
    print("=== kt00018 Response Fields ===")
    print(df.iloc[response_start:response_start+50].to_string())
