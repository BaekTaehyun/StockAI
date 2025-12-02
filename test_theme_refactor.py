"""
테마 리팩토링 검증 스크립트
- ThemeService가 제대로 호출되는지 확인
- market_themes 데이터가 올바르게 생성되는지 확인
"""
import sys
import os
sys.path.append(os.getcwd())

from stock_analysis_service import StockAnalysisService

def test_theme_data_extraction():
    """테마 데이터 추출 로직만 테스트"""
    print("=" * 60)
    print("테마 데이터 추출 테스트")
    print("=" * 60)
    
    service = StockAnalysisService()
    
    try:
        # 실제 ThemeService에서 테마 가져오기
        all_themes = service.theme_service.get_themes().get('themes', [])
        print(f"\n✓ 전체 테마 개수: {len(all_themes)}")
        
        if not all_themes:
            print("✗ 테마 데이터가 없습니다. theme_service 캐시를 확인하세요.")
            return False
            
        # 등락률 기준 정렬 (내림차순)
        sorted_themes = sorted(all_themes, key=lambda x: float(x.get('flu_rt', 0) or 0), reverse=True)
        
        # 상위 3개 추출
        print("\n상위 3개 테마:")
        top_themes = []
        for i, t in enumerate(sorted_themes[:3], 1):
            name = t.get('thema_nm')
            rate = t.get('flu_rt')
            theme_str = f"{name}({rate}%)"
            top_themes.append(theme_str)
            print(f"  {i}. {theme_str}")
            
        market_themes = ", ".join(top_themes) if top_themes else "정보 없음"
        print(f"\n✓ 최종 market_themes 값: {market_themes}")
        
        # 하위 3개도 확인
        print("\n하위 3개 테마:")
        for i, t in enumerate(sorted_themes[-3:], 1):
            name = t.get('thema_nm')
            rate = t.get('flu_rt')
            print(f"  {i}. {name}({rate}%)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_theme_data_extraction()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 테스트 통과: ThemeService 로직이 정상 작동합니다.")
    else:
        print("✗ 테스트 실패: 위 오류를 확인하세요.")
    print("=" * 60)
