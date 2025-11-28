"""
Watchlist Card Transformer
================================================================
키움 API 응답을 프론트엔드 친화적인 관심종목 카드 형식으로 변환
================================================================
"""

def transform_to_watchlist_card(code, price_data, supply_data=None):
    """키움 API 데이터를 관심종목 카드 형식으로 변환
    
    Args:
        code: 종목 코드
        price_data: 현재가 정보 (kis_api.get_current_price 응답)
        supply_data: 수급 정보 (kis_api.get_investor_trading 응답, 선택)
    
    Returns:
        dict: 프론트엔드 카드용 JSON
    """
    if not price_data:
        return None
    
    # 가격 정보
    current_price = int(price_data.get('price', 0))
    diff = int(price_data.get('change', 0))
    rate = float(price_data.get('rate', 0))
    
    # 색상 결정
    if diff > 0:
        color = "RED"
    elif diff < 0:
        color = "BLUE"
    else:
        color = "GRAY"
    
    # 기본 카드 구조
    card_data = {
        "id": code,
        "name": price_data.get('name', ''),
        "tags": [],  # 추후 추가 가능
        "price": {
            "current": current_price,
            "diff": diff,
            "rate": rate,
            "color": color
        },
        "supply": None,
        "signal": {
            "volume_ratio": None,
            "ai_summary": None,
            "tech_alert": None
        },
        "mini_chart_data": []
    }
    
    # 수급 정보 추가
    if supply_data:
        foreigner_net = supply_data.get('foreigner_net_buy', 0)
        institution_net = supply_data.get('institution_net_buy', 0)
        
        # 수급 트렌드 결정
        if abs(foreigner_net) > abs(institution_net):
            trend = "FOREIGNER_BUYING" if foreigner_net > 0 else "FOREIGNER_SELLING"
        elif abs(institution_net) > 0:
            trend = "INSTITUTION_BUYING" if institution_net > 0 else "INSTITUTION_SELLING"
        else:
            trend = "NEUTRAL"
        
        card_data["supply"] = {
            "foreigner": foreigner_net,
            "institution": institution_net,
            "trend": trend
        }
    
    return card_data


def format_supply_badge(trend):
    """수급 트렌드를 뱃지 텍스트로 변환
    
    Args:
        trend: "FOREIGNER_BUYING", "INSTITUTION_BUYING" 등
        
    Returns:
        str: 뱃지에 표시할 텍스트
    """
    trend_map = {
        "FOREIGNER_BUYING": "외인 매수중 📈",
        "FOREIGNER_SELLING": "외인 매도중 📉",
        "INSTITUTION_BUYING": "기관 매수중 🏢",
        "INSTITUTION_SELLING": "기관 매도중 🏢",
        "NEUTRAL": "보합 ➡️"
    }
    return trend_map.get(trend, "")


if __name__ == '__main__':
    # 테스트
    sample_price = {
        'name': '삼성전자',
        'price': '72500',
        'change': '2500',
        'rate': '3.57'
    }
    
    sample_supply = {
        'foreigner_net_buy': 150000,
        'institution_net_buy': -20000
    }
    
    result = transform_to_watchlist_card('005930', sample_price, sample_supply)
    print(result)
    print(format_supply_badge(result['supply']['trend']))
