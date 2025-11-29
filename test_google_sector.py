import requests
from bs4 import BeautifulSoup
import config
import urllib.parse
import re

def search_google(query):
    if not config.GOOGLE_SEARCH_API_KEY:
        print("Error: GOOGLE_SEARCH_API_KEY not found in config.")
        return []
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': config.GOOGLE_SEARCH_API_KEY,
        'cx': config.GOOGLE_SEARCH_CX,
        'q': query,
        'num': 3
    }
    
    print(f"DEBUG: Query repr: {repr(query)}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"Google Search Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Google Search Exception: {e}")
        return []

def get_naver_sector(stock_name):
    print(f"\n{'='*40}")
    print(f"Searching for sector info for: {stock_name}")
    print(f"{'='*40}")
    
    # Naver Finance specific search
    query = f"{stock_name} 종목분석 site:finance.naver.com"
    results = search_google(query)
    
    if not results:
        print("No search results found.")
        return

    target_url = None
    for item in results:
        link = item.get('link', '')
        # Prefer the main item page
        if 'finance.naver.com/item/main.naver' in link:
            target_url = link
            print(f"Found Naver Finance Link: {link}")
            break
    
    if not target_url:
        print("Could not find a direct Naver Finance main page link.")
        if results:
            target_url = results[0].get('link')
            print(f"Using first result as fallback: {target_url}")
    
    if not target_url:
        return

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        page_response = requests.get(target_url, headers=headers, timeout=10)
        
        if page_response.status_code != 200:
            print(f"Failed to fetch page. Status: {page_response.status_code}")
            return

        soup = BeautifulSoup(page_response.content, 'html.parser')
        
        # --- Parsing Logic ---
        
        # 1. Try to find "WICS" sector (often most accurate)
        # Structure: <dt>WICS :</dt> <dd>...</dd> or similar
        # Actually Naver Finance structure for WICS:
        # <h4 class="h_sub sub_tit7"><em>WICS</em></h4>
        # ... then look for the content
        
        wics_found = False
        h4s = soup.find_all('h4', class_='h_sub')
        for h4 in h4s:
            if 'WICS' in h4.get_text():
                # The WICS info is usually in a dl/dt/dd structure nearby or a table
                # Let's look for the next 'dt' or 'strong' or 'td'
                # In many pages it's like: WICS : [Sector Name]
                pass

        # 2. Try to find "업종" link
        # <a href="/sise/sise_group_detail.naver?type=upjong&no=...">Sector Name</a>
        upjong_links = soup.select('a[href*="type=upjong"]')
        if upjong_links:
            print("\n[Detected Sectors (Upjong)]")
            seen_sectors = set()
            for link in upjong_links:
                sector_name = link.get_text(strip=True)
                if sector_name and sector_name not in seen_sectors:
                    print(f"- {sector_name}")
                    seen_sectors.add(sector_name)
        else:
            print("\n[Sector] No 'Upjong' links found.")

        # 3. Try to find "테마" link (sometimes useful)
        # <a href="/sise/sise_group_detail.naver?type=theme&no=...">Theme Name</a>
        theme_links = soup.select('a[href*="type=theme"]')
        if theme_links:
            print("\n[Detected Themes]")
            seen_themes = set()
            for link in theme_links:
                theme_name = link.get_text(strip=True)
                if theme_name and theme_name not in seen_themes:
                    print(f"- {theme_name}")
                    seen_themes.add(theme_name)
        
        # 4. Extract Company Summary (Overview)
        # <div class="summary_info"> ... </div>
        summary_div = soup.select_one('.summary_info')
        if summary_div:
            print("\n[Company Summary]")
            print(summary_div.get_text(strip=True)[:200] + "...")
        
    except Exception as e:
        print(f"Parsing Error: {e}")

if __name__ == "__main__":
    print("Testing Google Search -> Naver Finance Parsing")
    
    test_stocks = ["삼성전자", "카카오", "에코프로", "현대차"]
    
    for stock in test_stocks:
        get_naver_sector(stock)
