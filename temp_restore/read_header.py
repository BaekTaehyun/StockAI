import pandas as pd

# ka10001 시트의 헤더 부분 읽기
df = pd.read_excel("키움 REST API 문서.xlsx", sheet_name="주식기본정보요청(ka10001)", nrows=30)
print("=== ka10001 Header Info ===")
print(df.to_string())
