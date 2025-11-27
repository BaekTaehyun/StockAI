import pandas as pd
import traceback
import sys

try:
    excel_file = "키움 REST API 문서.xlsx"
    print(f"Opening {excel_file}...")
    xl = pd.ExcelFile(excel_file)

    print("Searching for '분봉' or 'chart' in all sheets...")

    found = False
    for sheet in xl.sheet_names:
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet)
            # Convert all to string and search
            mask = df.astype(str).apply(lambda x: x.str.contains('분봉|chart|opt10080', case=False, na=False)).any(axis=1)
            if mask.any():
                print(f"\n[Found in Sheet: {sheet}]")
                # Print the first few columns to avoid too much output, or specific columns if known
                print(df[mask].to_string())
                found = True
        except Exception as e:
            print(f"Error reading sheet {sheet}: {e}")

    if not found:
        print("No matches found.")

except Exception as e:
    print("An error occurred:")
    traceback.print_exc()
    sys.exit(1)
