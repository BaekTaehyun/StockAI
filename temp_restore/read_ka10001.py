import pandas as pd

# ka10001 시트 읽기
# ka10001 시트 읽기
df = pd.read_excel("키움 REST API 문서.xlsx", sheet_name="주식기본정보요청(ka10001)", header=None)
print("=== ka10001 Sheet Content (First 20 rows) ===")
print(df.head(20).to_string())
