import pandas as pd
import traceback
import sys

try:
    excel_file = "키움 REST API 문서.xlsx"
    print(f"Opening {excel_file}...")
    xl = pd.ExcelFile(excel_file)

    print("Searching for '분봉' (minute) or '일봉' (daily) in all sheets...")

    found = False
    for sheet in xl.sheet_names:
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet)
            # Search for keywords
            mask = df.astype(str).apply(lambda x: x.str.contains('분봉|일봉|chart', case=False, na=False)).any(axis=1)
            if mask.any():
                print(f"\n[Found in Sheet: {sheet}]")
                # Print the first few rows of the matching sheet
                print(df.head(5).to_string()) 
                found = True
        except Exception as e:
            # print(f"Error reading sheet {sheet}: {e}")
            pass

    if not found:
        print("No matches found.")

except Exception as e:
    print("An error occurred:")
    traceback.print_exc()
