from flask import Flask, jsonify, render_template
from flask_cors import CORS
from kis_api import KiwoomApi
import config

app = Flask(__name__)
CORS(app)

# Kiwoom API 인스턴스
kiwoom = KiwoomApi()

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
        
        if not kiwoom.access_token:
            kiwoom.get_access_token()
        
        analysis_service = StockAnalysisService()
        # 서비스의 kiwoom 인스턴스를 현재 토큰으로 동기화
        analysis_service.kiwoom = kiwoom
        
        result = analysis_service.get_full_analysis(code)
        
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

if __name__ == '__main__':
    # 토큰 사전 발급
    print("=== 서버 시작 중 ===")
    if kiwoom.get_access_token():
        print("[OK] 인증 완료!")
    
    print("\n서버 주소: http://localhost:5000")
    print("브라우저에서 위 주소로 접속하세요!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
