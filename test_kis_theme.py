from kis_api import KiwoomApi
import json

def test_theme_api():
    api = KiwoomApi()
    if not api.get_access_token():
        print("Failed to get access token")
        return

    print("\n--- Testing get_theme_group_list (ka90001) ---")
    # 0:전체검색, 1일전 기준, 3:상위등락률
    themes = api.get_theme_group_list(search_type="0", date_type="1", fluctuation_type="3")
    
    if themes:
        print(f"Successfully retrieved {len(themes)} themes.")
        if len(themes) > 0:
            print("First theme sample:")
            print(json.dumps(themes[0], indent=2, ensure_ascii=False))
            
            # Try to find a specific theme, e.g., "2차전지"
            battery_themes = [t for t in themes if "2차전지" in t.get('thema_nm', '')]
            print(f"\nFound {len(battery_themes)} themes related to '2차전지':")
            for t in battery_themes[:3]:
                print(f"- {t.get('thema_nm')} (Code: {t.get('thema_grp_cd')}) - Rate: {t.get('flu_rt')}%")
    else:
        print("Failed to retrieve themes.")

if __name__ == "__main__":
    test_theme_api()
