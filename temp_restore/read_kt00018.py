import pandas as pd

# kt00018 시트 읽기
df = pd.read_excel("키움 REST API 문서.xlsx", sheet_name="주식잔고요청(kt00018)", nrows=30)
print("=== kt00018 주식잔고요청 ===")
print(df.to_string())
