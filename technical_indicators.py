import pandas as pd
import numpy as np

class TechnicalIndicators:
    """기술적 지표 계산 클래스 (pandas-ta 의존성 제거됨)"""
    
    @staticmethod
    def calculate_indicators(price_data):
        """
        주가 데이터로부터 기술적 지표 계산
        
        Args:
            price_data: DataFrame with columns ['date', 'close', 'high', 'low', 'volume']
            
        Returns:
            {
                'rsi': RSI 값,
                'rsi_signal': '과매수'/'과매도'/'중립',
                'macd': MACD 값,
                'macd_signal': '상승'/'하락'/'중립',
                'ma5': 5일 이동평균,
                'ma20': 20일 이동평균,
                'ma60': 60일 이동평균,
                'ma_signal': '골든크로스'/'데드크로스'/'중립'
            }
        """
        try:
            if price_data is None or len(price_data) < 20:
                return TechnicalIndicators._get_default_indicators()
            
            df = pd.DataFrame(price_data)
            
            # 컬럼명 통일 (소문자로)
            df.columns = df.columns.str.lower()
            
            # close 컬럼이 있는지 확인
            if 'close' not in df.columns:
                return TechnicalIndicators._get_default_indicators()
            
            # 데이터 타입을 숫자로 변환
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            
            # 데이터 개수 확인
            print(f"[TechnicalIndicators] Calculating for {len(df)} records")
            
            # --- RSI 계산 (14일) - Wilder's Smoothing Method ---
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)
            
            # Wilder's smoothing: EMA with alpha = 1/14
            avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
            
            # Avoid division by zero
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi_series = 100 - (100 / (1 + rs))
            
            # fillna(100) for cases where loss is 0 (infinite gain)
            rsi_series = rsi_series.fillna(100)
            
            current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
            
            # RSI 신호 판단
            if current_rsi > 70:
                rsi_signal = "과매수"
            elif current_rsi < 30:
                rsi_signal = "과매도"
            else:
                rsi_signal = "중립"
            
            # --- MACD 계산 ---
            # EMA 12, 26
            ema12 = df['close'].ewm(span=12, adjust=False).mean()
            ema26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_line_series = ema12 - ema26
            signal_line_series = macd_line_series.ewm(span=9, adjust=False).mean()
            
            macd_line = macd_line_series.iloc[-1]
            signal_line = signal_line_series.iloc[-1]
            
            if macd_line > signal_line:
                macd_signal = "상승"
            elif macd_line < signal_line:
                macd_signal = "하락"
            else:
                macd_signal = "중립"
            
            # --- 이동평균선 계산 ---
            ma5_series = df['close'].rolling(window=5).mean()
            ma20_series = df['close'].rolling(window=20).mean()
            ma60_series = df['close'].rolling(window=60).mean()
            
            ma5 = ma5_series.iloc[-1] if len(df) >= 5 else df['close'].iloc[-1]
            ma20 = ma20_series.iloc[-1] if len(df) >= 20 else df['close'].iloc[-1]
            ma60 = ma60_series.iloc[-1] if len(df) >= 60 else df['close'].iloc[-1]
            
            # 이동평균선 배열 신호
            current_price = df['close'].iloc[-1]
            
            # NaN 처리
            if np.isnan(ma5): ma5 = current_price
            if np.isnan(ma20): ma20 = current_price
            if np.isnan(ma60): ma60 = current_price
            
            if current_price > ma5 > ma20 > ma60:
                ma_signal = "정배열"
            elif current_price < ma5 < ma20 < ma60:
                ma_signal = "역배열"
            elif len(df) >= 2:
                prev_ma5 = ma5_series.iloc[-2]
                prev_ma20 = ma20_series.iloc[-2]
                
                if not np.isnan(prev_ma5) and not np.isnan(prev_ma20):
                    if prev_ma5 < prev_ma20 and ma5 > ma20:
                        ma_signal = "골든크로스"
                    elif prev_ma5 > prev_ma20 and ma5 < ma20:
                        ma_signal = "데드크로스"
                    else:
                        ma_signal = "중립"
                else:
                    ma_signal = "중립"
            else:
                ma_signal = "중립"
            
            return {
                'rsi': round(float(current_rsi), 2),
                'rsi_signal': rsi_signal,
                'macd': round(float(macd_line), 2),
                'macd_signal': macd_signal,
                'ma5': round(float(ma5), 2),
                'ma20': round(float(ma20), 2),
                'ma60': round(float(ma60), 2),
                'ma_signal': ma_signal
            }
            
        except Exception as e:
            print(f"[TechnicalIndicators] 계산 오류: {e}")
            return TechnicalIndicators._get_default_indicators()
    
    @staticmethod
    def _get_default_indicators():
        """기본 지표 값 반환"""
        return {
            'rsi': 50,
            'rsi_signal': "데이터부족",
            'macd': 0,
            'macd_signal': "데이터부족",
            'ma5': 0,
            'ma20': 0,
            'ma60': 0,
            'ma_signal': "데이터부족"
        }
