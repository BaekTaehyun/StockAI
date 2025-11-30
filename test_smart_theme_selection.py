from gemini_service import GeminiService
from theme_service import ThemeService
from unittest.mock import MagicMock

def test_smart_theme_selection():
    print("=== Smart Theme Selection Test (Core + Active) ===")
    
    # 1. Mock ThemeService
    mock_theme_service = MagicMock()
    
    # Mock themes for Samsung Electronics
    # Includes some core themes (Semiconductor, Mobile) and some active themes (CXL +5%, OnDevice AI +3%)
    mock_themes = [
        {'theme_name': '반도체 대표주', 'theme_fluctuation': 0.5},
        {'theme_name': '스마트폰', 'theme_fluctuation': -0.2},
        {'theme_name': 'CXL(컴퓨트익스프레스링크)', 'theme_fluctuation': 5.2}, # Active!
        {'theme_name': '온디바이스 AI', 'theme_fluctuation': 3.1}, # Active!
        {'theme_name': '시스템반도체', 'theme_fluctuation': 0.1},
        {'theme_name': '2024 상반기 실적', 'theme_fluctuation': 0.0},
        {'theme_name': '환율 하락 수혜', 'theme_fluctuation': -1.5}
    ]
    mock_theme_service.find_themes_by_stock.return_value = mock_themes
    
    # 2. Initialize GeminiService
    gemini = GeminiService()
    
    # 3. Test select_core_themes (Actual API Call)
    print("\n[1] Testing select_core_themes (AI Call)...")
    stock_name = "삼성전자"
    stock_code = "005930"
    
    # Force refresh to trigger AI
    core_themes = gemini.select_core_themes(stock_name, stock_code, mock_themes, force_refresh=True)
    print(f"   -> AI Selected Core Themes: {core_themes}")
    
    # Verify core themes contains expected keywords
    expected_keywords = ["반도체", "스마트폰"]
    found = any(k in str(core_themes) for k in expected_keywords)
    if found:
        print("   ✅ Core theme selection looks reasonable.")
    else:
        print("   ⚠️ Core theme selection might be unexpected. Check output.")

    # 4. Test generate_outlook (Prompt Construction Logic)
    print("\n[2] Testing generate_outlook (Prompt Construction)...")
    
    # Mock other inputs
    stock_info = {'code': stock_code, 'price': 70000, 'rate': 1.5}
    supply_demand = {}
    technical = {}
    news = {}
    
    # We want to see the prompt, but generate_outlook calls API.
    # We can inspect the prompt by temporarily monkey-patching _call_gemini_api
    original_call = gemini._call_gemini_api
    
    def mock_call_api(prompt):
        print("\n   [Captured Prompt Segment regarding Themes]")
        # Extract the theme section from prompt
        import re
        # Look for the new format: "- 핵심 테마(Identity): ..."
        match_core = re.search(r'- 핵심 테마\(Identity\): (.*?)\n', prompt)
        match_active = re.search(r'- 오늘 강세 테마\(Active\): (.*?)\n', prompt)
        
        if match_core:
            print(f"   [Core] {match_core.group(1).strip()}")
        else:
            print("   ⚠️ Could not find Core Themes in prompt.")

        if match_active:
            print(f"   [Active] {match_active.group(1).strip()}")
        else:
            print("   ⚠️ Could not find Active Themes in prompt.")
            
        return "Mock Response"
        
    gemini._call_gemini_api = mock_call_api
    
    gemini.generate_outlook(
        stock_name, stock_info, supply_demand, technical, news, 
        theme_service=mock_theme_service, force_refresh=True
    )
    
    # Restore
    gemini._call_gemini_api = original_call
    print("\n✅ Test Completed.")

if __name__ == "__main__":
    test_smart_theme_selection()
