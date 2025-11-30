import sys
import os

# 현재 디렉토리를 path에 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from theme_service import ThemeService
from gemini_service import GeminiService

def verify_stock_themes(stock_name):
    print(f"\n{'='*60}")
    print(f"🔍 주식 테마 정밀 분석: {stock_name}")
    print(f"{'='*60}")

    # 1. 서비스 초기화
    print("[0] 서비스 초기화 중...")
    try:
        theme_service = ThemeService()
        gemini_service = GeminiService()
    except Exception as e:
        print(f"❌ 서비스 초기화 실패: {e}")
        return

    # 2. 전체 테마 검색 (Kiwoom + Naver)
    print(f"\n[1] 전체 테마 검색 (Kiwoom + Naver)...")
    all_themes = theme_service.find_themes_by_stock(stock_name)
    
    if not all_themes:
        print(f"❌ '{stock_name}'에 대한 테마 정보를 찾을 수 없습니다.")
        print("   (종목명이 정확한지, 또는 테마 데이터가 업데이트되었는지 확인해주세요)")
        return

    # 테마 리스트 출력
    print(f"   -> 총 {len(all_themes)}개 테마 발견:")
    sorted_themes = sorted(all_themes, key=lambda x: float(x.get('theme_fluctuation', 0) or 0), reverse=True)
    
    for t in sorted_themes:
        fluc = t.get('theme_fluctuation', 0)
        source = t.get('source', 'Unknown')
        name = t.get('theme_name')
        
        # 등락률 색상 표시 (터미널 지원 시)
        fluc_str = f"{fluc}%"
        if fluc > 0: fluc_str = f"+{fluc}%"
        
        print(f"      - {name:<20} \t[{source}] \t{fluc_str}")

    # 3. Core 테마 선정 (AI)
    print(f"\n[2] AI Core 테마 선정 (Identity Analysis)...")
    # 종목 코드는 첫 번째 테마 정보에서 가져오거나 없으면 더미 사용
    stock_code = all_themes[0].get('stock_code', '000000')
    
    print("   ... AI가 기업의 본질을 분석 중입니다 ...")
    core_themes = gemini_service.select_core_themes(stock_name, stock_code, all_themes, force_refresh=True)
    
    print(f"   -> 🎯 핵심 테마 (Core): {core_themes}")
    print("      (기업의 주력 사업과 본질을 나타내는 테마)")

    # 4. Active 테마 식별 (Market Logic)
    print(f"\n[3] Active 테마 식별 (Market Trend Analysis)...")
    active_themes = []
    for t in sorted_themes:
        try:
            fluc = float(t.get('theme_fluctuation', 0))
            # 기준: 1% 이상 상승 또는 상위 3개 (여기서는 1% 이상만 표시해봄)
            if fluc >= 1.0: 
                active_themes.append(f"{t['theme_name']}({fluc}%)")
        except:
            pass
    
    if active_themes:
        print(f"   -> 🔥 강세 테마 (Active): {', '.join(active_themes)}")
        print("      (오늘 시장에서 수급이 몰리고 있는 테마)")
    else:
        print(f"   -> ❄️ 강세 테마 (Active): 없음")
        print("      (오늘 1% 이상 상승한 테마가 없습니다)")

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    # 명령행 인자가 있으면 그 종목을, 없으면 사용자 입력 받기
    if len(sys.argv) > 1:
        target_stock = sys.argv[1]
        verify_stock_themes(target_stock)
    else:
        while True:
            target_stock = input("분석할 종목명을 입력하세요 (종료: q): ").strip()
            if target_stock.lower() == 'q':
                break
            if target_stock:
                verify_stock_themes(target_stock)
