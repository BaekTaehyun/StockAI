from waitress import serve
from app import app, kiwoom, theme_service
import socket
from logger import Logger

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    Logger.info("Server", "=== Production Server Starting ===")
    
    # 1. 토큰 사전 발급
    if kiwoom.get_access_token():
        Logger.info("Server", "인증 완료!")
    
    # 2. 테마 캐시 초기화 (서버 시작 전 필수)
    Logger.info("Theme", "테마 캐시 초기화 중...")
    if not theme_service.is_cache_valid():
        Logger.info("Theme", "캐시가 없거나 만료됨. 새로 생성합니다...")
        if theme_service.update_cache():
            cache_info = theme_service.get_cache_info()
            Logger.info("Theme", f"캐시 생성 완료: {cache_info.get('theme_count')}개 테마")
        else:
            Logger.error("Theme", "캐시 생성 실패 - 서비스 제한 모드로 시작")
    else:
        cache_info = theme_service.get_cache_info()
        Logger.info("Theme", f"기존 캐시 사용: {cache_info.get('theme_count')}개 테마")
    
    # 3. 스케줄러 초기화 (매일 오전 9시 테마 캐시 갱신)
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=theme_service.update_cache,
        trigger='cron',
        hour=9,
        minute=0,
        id='daily_theme_update',
        replace_existing=True
    )
    scheduler.start()
    Logger.info("Scheduler", "매일 오전 9시 자동 갱신 예약 완료")
    
    host_ip = get_ip_address()
    port = 5000
    
    Logger.info("Server", "=== Production Server Started (Waitress) ===")
    Logger.info("Server", f"Local:   http://localhost:{port}")
    Logger.info("Server", f"Network: http://{host_ip}:{port}")
    Logger.info("Server", "============================================")
    
    try:
        # threads=8: 동시 요청 처리 능력 향상 (기본값 4)
        serve(app, host='0.0.0.0', port=port, threads=8)
    finally:
        scheduler.shutdown()
