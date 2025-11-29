import requests

url = "https://openapi.kiwoom.com/guide/apiguide"
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    print(response.text)
except Exception as e:
    print(f"Error fetching docs: {e}")
