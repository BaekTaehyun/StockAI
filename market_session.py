"""
시장 세션 판단 유틸리티
====================================
현재 시간을 기반으로 한국 증권시장의 거래 세션을 판단합니다.

세션 종류:
- PRE_MARKET: 장개시전 시간외 (08:30-08:40)
- REGULAR: 정규 장중 (09:00-15:30)
- POST_CLOSE: 장종료후 종가매매 (15:40-16:00)
- AFTER_HOURS: 시간외 단일가 (16:00-18:00)
- CLOSED: 거래시간 외
"""

from datetime import datetime, time
from typing import Dict, Tuple

class MarketSession:
    """시장 세션 정보"""
    
    # 세션 코드
    PRE_MARKET = "PRE_MARKET"
    PRE_OPEN = "PRE_OPEN"  # 장시작 동시호가
    REGULAR = "REGULAR"
    POST_AUCTION = "POST_AUCTION"  # 장마감 동시호가
    POST_CLOSE = "POST_CLOSE"
    AFTER_HOURS = "AFTER_HOURS"
    CLOSED = "CLOSED"
    
    # 세션별 시간 범위
    SESSIONS = {
        PRE_MARKET: {
            "start": time(8, 30),
            "end": time(8, 40),
            "display_name": "장개시전 시간외",
            "display_time": "08:30-08:40",
            "description": "전일 종가로 거래",
            "emoji": "🌅"
        },
        PRE_OPEN: {
            "start": time(8, 40),
            "end": time(9, 0),
            "display_name": "장시작 동시호가",
            "display_time": "08:40-09:00",
            "description": "시가 결정 (주문 접수만 가능)",
            "emoji": "⏳"
        },
        REGULAR: {
            "start": time(9, 0),
            "end": time(15, 30),
            "display_name": "정규 장중",
            "display_time": "09:00-15:30",
            "description": "실시간 체결",
            "emoji": "📈"
        },
        POST_AUCTION: {
            "start": time(15, 20), # 15:20부터 동시호가 접수 시작이나, 실질적 마감 임박은 15:30
            "end": time(15, 40), # 15:30 이후 체결 안됨, 15:40에 종가 결정
            # 로직상 15:30~15:40을 커버하기 위해 조정
            "display_name": "장마감 동시호가",
            "display_time": "15:30-15:40",
            "description": "종가 결정 (주문 접수만 가능)",
            "emoji": "🏁"
        },
        POST_CLOSE: {
            "start": time(15, 40),
            "end": time(16, 0),
            "display_name": "장종료후 종가매매",
            "display_time": "15:40-16:00",
            "description": "당일 종가로 거래",
            "emoji": "🌆"
        },
        AFTER_HOURS: {
            "start": time(16, 0),
            "end": time(18, 0),
            "display_name": "시간외 단일가",
            "display_time": "16:00-18:00",
            "description": "10분 단위 체결 (±10%)",
            "emoji": "🌃"
        }
    }
    
    @classmethod
    def get_current_session(cls) -> Dict[str, str]:
        """
        현재 시장 세션 정보를 반환합니다.
        
        Returns:
            dict: {
                "session": 세션 코드,
                "display_name": 표시명,
                "display_time": 시간대,
                "description": 설명,
                "emoji": 이모지,
                "is_trading": 거래 중 여부
            }
        """
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=월요일, 6=일요일
        
        # 주말 체크
        if current_day >= 5:  # 토요일(5) 또는 일요일(6)
            return {
                "session": cls.CLOSED,
                "display_name": "주말",
                "display_time": "",
                "description": "증권시장 휴장",
                "emoji": "🏖️",
                "is_trading": False
            }
        
        # 시간대별 세션 확인
        for session_code, session_info in cls.SESSIONS.items():
            if session_info["start"] <= current_time <= session_info["end"]:
                return {
                    "session": session_code,
                    "display_name": session_info["display_name"],
                    "display_time": session_info["display_time"],
                    "description": session_info["description"],
                    "emoji": session_info["emoji"],
                    "is_trading": True
                }
        
        # 어느 세션에도 속하지 않음 (거래시간 외)
        return {
            "session": cls.CLOSED,
            "display_name": "거래시간 외",
            "display_time": "",
            "description": "다음 거래일을 기다려주세요",
            "emoji": "🌙",
            "is_trading": False
        }
    
    @classmethod
    def is_extended_hours(cls) -> bool:
        """
        현재 시간외 거래 시간대인지 확인합니다.
        
        Returns:
            bool: 시간외 거래 시간대 여부
        """
        session_info = cls.get_current_session()
        return session_info["session"] in [cls.PRE_MARKET, cls.POST_CLOSE, cls.AFTER_HOURS]
    
    @classmethod
    def get_session_badge_style(cls, session_code: str) -> str:
        """
        세션별 배지 스타일 클래스를 반환합니다.
        
        Args:
            session_code: 세션 코드
            
        Returns:
            str: CSS 클래스명
        """
        styles = {
            cls.PRE_MARKET: "session-pre-market",
            cls.PRE_OPEN: "session-pre-open",
            cls.REGULAR: "session-regular",
            cls.POST_AUCTION: "session-post-auction",
            cls.POST_CLOSE: "session-post-close",
            cls.AFTER_HOURS: "session-after-hours",
            cls.CLOSED: "session-closed"
        }
        return styles.get(session_code, "session-closed")
    
    @classmethod
    def get_user_message(cls, session_code: str) -> str:
        """
        현재 세션에 맞는 사용자 안내 메시지를 반환합니다.
        
        Args:
            session_code: 세션 코드
            
        Returns:
            str: 안내 메시지
        """
        messages = {
            cls.PRE_MARKET: "⚠️ 장개시전 시간외 거래 중입니다. 전일 종가로 거래됩니다.",
            cls.PRE_OPEN: "⏳ 장시작 동시호가 시간입니다. 시가가 결정되는 중입니다.",
            cls.POST_CLOSE: "⚠️ 장종료후 종가매매 시간입니다. 당일 종가로 거래가 체결됩니다.",
            cls.POST_AUCTION: "🏁 장마감 동시호가 시간입니다. 종가가 결정되는 중입니다.",
            cls.AFTER_HOURS: "⚠️ 시간외 단일가 거래 중입니다. 10분 단위로 가격이 체결되며, 종가 대비 ±10% 범위 내에서 거래됩니다.",
            cls.REGULAR: "",
            cls.CLOSED: "현재 거래시간이 아닙니다. 표시된 가격은 가장 최근 거래일의 데이터입니다."
        }
        return messages.get(session_code, "")


def get_market_session_info() -> Dict[str, str]:
    """
    현재 시장 세션 정보를 반환하는 편의 함수
    
    Returns:
        dict: 세션 정보
    """
    return MarketSession.get_current_session()


def is_extended_hours() -> bool:
    """
    시간외 거래 시간대 여부를 반환하는 편의 함수
    
    Returns:
        bool: 시간외 거래 여부
    """
    return MarketSession.is_extended_hours()
