import requests
from bs4 import BeautifulSoup

def debug_detail_page():
    # 시스템반도체 URL (from previous log)
    url = "https://finance.naver.com/sise/sise_group_detail.naver?type=theme&no=307"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers)
    res.encoding = 'cp949'
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Check selectors
    print("\n--- Checking Selectors ---")
    items = soup.select('div.box_type_l table.type_1 tr td.name a')
    print(f"Items found with 'div.box_type_l table.type_1 tr td.name a': {len(items)}")
    
    if len(items) == 0:
        print("\n--- Dumping Table HTML ---")
        # Try to find the table and print its structure
        tables = soup.select('table.type_5') # Sometimes it's type_5 in detail pages? Or type_1?
        for idx, table in enumerate(tables):
            print(f"Table {idx} class: {table.get('class')}")
            # Print first few rows
            rows = table.select('tr')
            print(f"  Rows: {len(rows)}")
            if rows:
                print(f"  First row html: {rows[0]}")

        print("\n--- Trying alternative selector ---")
        # Try a broader selector
        links = soup.select('td.name a')
        print(f"Links found with 'td.name a': {len(links)}")
        for link in links[:3]:
            print(f"  - {link.text} ({link['href']})")

if __name__ == "__main__":
    debug_detail_page()
