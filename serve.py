from waitress import serve
from app import app, kiwoom, theme_service
import socket

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
    print("=== Production Server Starting ===")
    
    # 1. 토큰 사전 발급
    if kiwoom.get_access_token():
        print("[OK] 인증 완료!")
    
    # 2. 테마 캐시 초기화 (서버 시작 전 필수)
    print("\n[ThemeService] 테마 캐시 초기화 중...")
    if not theme_service.is_cache_valid():
        print("[ThemeService] 캐시가 없거나 만료됨. 새로 생성합니다...")
        if theme_service.update_cache():
            cache_info = theme_service.get_cache_info()
            print(f"[ThemeService] ✓ 캐시 생성 완료: {cache_info.get('theme_count')}개 테마")
        else:
            print("[ThemeService] ✗ 캐시 생성 실패 - 서비스 제한 모드로 시작")
    else:
        cache_info = theme_service.get_cache_info()
        print(f"[ThemeService] ✓ 기존 캐시 사용: {cache_info.get('theme_count')}개 테마")
    
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
    print("[Scheduler] ✓ 매일 오전 9시 자동 갱신 예약 완료\n")
    
    host_ip = get_ip_address()
    port = 5000
    
    print(f"=== Production Server Started (Waitress) ===")
    print(f"Local:   http://localhost:{port}")
    print(f"Network: http://{host_ip}:{port}")
    print(f"============================================")
    
    try:
        serve(app, host='0.0.0.0', port=port)
    finally:
        scheduler.shutdown()
