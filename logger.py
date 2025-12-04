"""
Logger 유틸리티
================================================================
디버그 모드에 따라 로그 출력을 제어합니다.
- DEBUG 모드 ON: 모든 로그 출력
- DEBUG 모드 OFF: 중요 로그만 출력
================================================================
"""
import config

class Logger:
    """로그 출력을 제어하는 싱글톤 로거"""
    
    DEBUG = getattr(config, 'DEBUG_MODE', True)
    
    @staticmethod
    def debug(tag, message):
        """디버그 로그 (DEBUG 모드에서만 출력)"""
        if Logger.DEBUG:
            print(f"[{tag}] {message}")
    
    @staticmethod
    def info(tag, message):
        """정보 로그 (항상 출력)"""
        print(f"ℹ️ [{tag}] {message}")
    
    @staticmethod
    def warning(tag, message):
        """경고 로그 (항상 출력)"""
        print(f"⚠️ [{tag}] {message}")
    
    @staticmethod
    def error(tag, message):
        """에러 로그 (항상 출력)"""
        print(f"❌ [{tag}] {message}")
    
    @staticmethod
    def set_debug_mode(enabled):
        """디버그 모드 동적 변경"""
        Logger.DEBUG = enabled
        print(f"🔧 Debug mode: {'ON' if enabled else 'OFF'}")
