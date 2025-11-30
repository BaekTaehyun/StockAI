"""
키움 주식 모니터링 시스템 - 메인 애플리케이션
================================================================
Flask 기반 웹 서버로 다음 기능을 제공합니다:
- 실시간 보유 종목 조회
- 계좌 잔고 및 수익률 표시
- AI 기반 종목 분석 (Gemini API)
- 기술적 지표 계산 및 시각화
- 시장 지수 (KOSPI/KOSDAQ) 모니터링
================================================================
"""
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_cors import CORS
from kis_api import KiwoomApi
from data_fetcher import DataFetcher
from theme_service import ThemeService
from datetime import timedelta
import config

app = Flask(__name__)
CORS(app)  # CORS 활성화 (프론트엔드 연동)

# 세션 설정
app.secret_key = getattr(config, 'SECRET_KEY', 'default-secret-key')
app.permanent_session_lifetime = timedelta(days=7) # 로그인 7일 유지

# Kiwoom API 인스턴스 생성
kiwoom = KiwoomApi()

# 관심종목 관리 인스턴스 생성
data_fetcher = DataFetcher()

# 테마 서비스 인스턴스 생성
theme_service = ThemeService()

@app.after_request
def add_header(response):
    """
    모바일 캐시 문제 해결을 위한 헤더 추가
    모든 응답에 대해 캐시를 무효화합니다.
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.before_request
def require_login():
    """모든 요청에 대해 로그인 여부 확인"""
    # 정적 파일 및 로그인 페이지는 제외
    if request.endpoint in ['login', 'static']:
        return
    
    # 로그인되지 않은 경우 로그인 페이지로 리다이렉트
    if not session.get('logged_in'):
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 및 처리"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = getattr(config, 'USERS', {})
        
        if username in users and users[username] == password:
            session.permanent = True  # 세션 영구 유지 (설정된 lifetime 만큼)
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    """메인 대시보드 페이지"""
    return render_template('index.html')

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """인증 및 토큰 발급"""
    try:
        if kiwoom.get_access_token():
            return jsonify({
                'success': True,
                'message': '인증 성공',
                'expires': kiwoom.token_expired
            })
        else:
            return jsonify({
                'success': False,
                'message': '인증 실패'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/price/<code>')
def get_price(code):
    """특정 종목의 현재가 조회"""
    try:
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        price_info = kiwoom.get_current_price(code)
        if price_info:
            return jsonify({
                'success': True,
                'data': price_info
            })
        else:
            return jsonify({
                'success': False,
                'message': '가격 조회 실패'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/account/balance')
def get_account_balance():
    """계좌 잔고 조회"""
    try:
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        balance = kiwoom.get_account_balance()
        if balance:
            return jsonify({
                'success': True,
                'data': balance
            })
        else:
            return jsonify({
                'success': False,
                'message': '잔고 조회 실패'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/account/summary')
def get_account_summary():
    """계좌 요약 정보"""
    try:
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        balance = kiwoom.get_account_balance()
        if balance:
            # 숫자 변환 (앞의 0 제거)
            total_purchase = int(balance['total_purchase_amount'])
            total_eval = int(balance['total_eval_amount'])
            total_pl = int(balance['total_profit_loss'])
            profit_rate = float(balance['total_profit_rate'])
            
            return jsonify({
                'success': True,
                'data': {
                    'total_purchase': total_purchase,
                    'total_eval': total_eval,
                    'total_pl': total_pl,
                    'profit_rate': profit_rate,
                    'holdings_count': len(balance['holdings'])
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '요약 정보 조회 실패'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/chart/minute/<code>')
def get_minute_chart(code):
    """분봉 차트 데이터 조회"""
    try:
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        chart_data = kiwoom.get_minute_chart_data(code)
        if chart_data is not None:
            return jsonify({
                'success': True,
                'data': chart_data
            })
        else:
            return jsonify({
                'success': False,
                'message': '차트 데이터 조회 실패'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/analysis/full/<code>')
def get_full_analysis(code):
    """종목 종합 분석"""
    try:
        from stock_analysis_service import StockAnalysisService
        
        # 종목 코드 정규화 (A 접두사 제거)
        normalized_code = code.lstrip('A') if code.startswith('A') else code
        
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        analysis_service = StockAnalysisService()
        # 서비스의 kiwoom 인스턴스를 현재 토큰으로 동기화
        analysis_service.kiwoom = kiwoom
        
        # 강제 갱신 여부 확인 (쿼리 파라미터 refresh=true)
        force_refresh = request.args.get('refresh', '').lower() == 'true'
        
        result = analysis_service.get_full_analysis(normalized_code, force_refresh=force_refresh)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/analysis/supply-demand/<code>')
def get_supply_demand(code):
    """수급 데이터 조회"""
    try:
        from stock_analysis_service import StockAnalysisService
        
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        analysis_service = StockAnalysisService()
        analysis_service.kiwoom = kiwoom
        
        supply_demand = analysis_service.get_supply_demand_data(code)
        
        return jsonify({
            'success': True,
            'data': supply_demand
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/config')
def get_config():
    """프론트엔드 설정 제공"""
    return jsonify({
        'success': True,
        'data': {
            'sentiment_refresh_minutes': getattr(config, 'SENTIMENT_REFRESH_MINUTES', 5),
            'sentiment_update_delay_seconds': getattr(config, 'SENTIMENT_UPDATE_DELAY_SECONDS', 15)
        }
    })

@app.route('/api/analysis/sentiment/<code>')
def get_sentiment_analysis(code):
    """종목의 감성 분석 결과만 반환 (카드 표시용)"""
    try:
        from stock_analysis_service import StockAnalysisService
        stock_analysis = StockAnalysisService()
        
        # 종합 분석 호출 (캐싱 활용)
        result = stock_analysis.get_full_analysis(code)
        
        if result['success']:
            data = result['data']
            return jsonify({
                'success': True,
                'data': {
                    'code': code,
                    'news_sentiment': data['news_analysis']['sentiment'],
                    'supply_trend': data['supply_demand']['trend'],
                    'ai_recommendation': data['outlook']['recommendation'],
                    'ai_confidence': data['outlook']['confidence'],
                    'price_strategy': data['outlook'].get('price_strategy')
                }
            })
        else:
            return jsonify({'success': False, 'message': result.get('message', '분석 실패')})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/analysis/news/<code>')
def get_news_analysis(code):
    """뉴스 분석"""
    try:
        from gemini_service import GeminiService
        
        # 종목명 조회
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        price_info = kiwoom.get_current_price(code)
        stock_name = price_info.get('name', '알 수 없음') if price_info else '알 수 없음'
        
        gemini = GeminiService()
        news_analysis = gemini.search_and_analyze_news(
            stock_name=stock_name,
            stock_code=code,
            current_price=price_info.get('price') if price_info else None,
            change_rate=price_info.get('rate') if price_info else None
        )
        
        return jsonify({
            'success': True,
            'data': news_analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/market/indices')
def get_market_indices():
    """코스피, 코스닥 지수 조회"""
    try:
        # 코스피 (001), 코스닥 (101)
        kospi = kiwoom.get_market_index("001")
        kosdaq = kiwoom.get_market_index("101")
        
        return jsonify({
            'success': True,
            'data': {
                'kospi': kospi,
                'kosdaq': kosdaq
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ================================================================
# 관심종목 API
# ================================================================

@app.route('/api/watchlist')
def get_watchlist():
    """관심종목 리스트 조회"""
    try:
        watchlist = data_fetcher.load_watchlist()
        return jsonify({
            'success': True,
            'data': watchlist
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/watchlist/prices')
def get_watchlist_prices():
    """관심종목 시세 일괄 조회"""
    try:
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        prices = data_fetcher.fetch_watchlist_prices()
        return jsonify({
            'success': True,
            'data': prices
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """관심종목 추가"""
    try:
        code = request.json.get('code')
        if not code:
            return jsonify({'success': False, 'message': '종목 코드가 필요합니다'}), 400
        
        success = data_fetcher.add_to_watchlist(code)
        return jsonify({
            'success': success,
            'message': '추가 완료' if success else '이미 존재하는 종목입니다'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """관심종목 삭제"""
    try:
        code = request.json.get('code')
        if not code:
            return jsonify({'success': False, 'message': '종목 코드가 필요합니다'}), 400
        
        success = data_fetcher.remove_from_watchlist(code)
        return jsonify({
            'success': success,
            'message': '삭제 완료' if success else '존재하지 않는 종목입니다'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ================================================================
# 테마 API
# ================================================================

@app.route('/api/themes')
def get_themes():
    """테마 목록 조회 (캐시된 데이터)"""
    try:
        data = theme_service.get_themes()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/themes/search')
def search_themes():
    """테마 검색"""
    try:
        keyword = request.args.get('q', '')
        results = theme_service.search_theme(keyword)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/themes/refresh', methods=['POST'])
def refresh_themes():
    """테마 캐시 수동 갱신"""
    try:
        success = theme_service.update_cache()
        if success:
            return jsonify({
                'success': True,
                'message': '테마 캐시 갱신 완료'
            })
        else:
            return jsonify({
                'success': False,
                'message': '테마 캐시 갱신 실패'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    print("=== 서버 시작 중 ===")
    
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
    print("[Scheduler] ✓ 매일 오전 9시 자동 갱신 예약 완료")
    
    print("\n서버 주소: http://localhost:5000")
    print("브라우저에서 위 주소로 접속하세요!\n")
    
    # 보안 주의: 외부 접속(0.0.0.0) 허용 시 반드시 debug=False로 설정해야 합니다.
    # debug=True 상태에서 외부 접속을 허용하면 원격 코드 실행 취약점이 발생할 수 있습니다.
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    finally:
        scheduler.shutdown()
