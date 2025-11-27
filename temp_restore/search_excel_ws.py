import pandas as pd

excel_file = "키움 REST API 문서.xlsx"
xl = pd.ExcelFile(excel_file)

print("Searching for 'WebSocket' or '웹소켓' in all sheets...")

found = False
for sheet in xl.sheet_names:
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        # Convert all to string and search
        mask = df.astype(str).apply(lambda x: x.str.contains('WebSocket|웹소켓|socket', case=False, na=False)).any(axis=1)
        if mask.any():
            print(f"\n[Found in Sheet: {sheet}]")
            print(df[mask].to_string())
            found = True
    except Exception as e:
        print(f"Error reading sheet {sheet}: {e}")

if not found:
    print("No matches found.")
