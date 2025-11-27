import pandas as pd

# API 트리 시트에서 계좌 관련 TR 찾기
df = pd.read_excel("키움 REST API 문서.xlsx", sheet_name="API 트리")

# "계좌" 또는 "잔고" 포함된 행 찾기
account_apis = df[df.apply(lambda row: row.astype(str).str.contains('계좌|잔고', case=False, na=False).any(), axis=1)]

print("=== 계좌/잔고 관련 API ===")
print(account_apis.to_string())
