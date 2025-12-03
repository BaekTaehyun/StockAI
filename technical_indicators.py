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

    @staticmethod
    def calculate_bollinger_bands(price_data, window=20, num_std=2):
        """
        볼린저 밴드 및 스퀴즈 지표 계산
        
        Args:
            price_data: List of dicts or DataFrame
            window: 이동평균 기간 (기본 20)
            num_std: 표준편차 승수 (기본 2)
            
        Returns:
            dict: {
                'summary': { 'upper': ..., 'middle': ..., 'lower': ..., 'bandwidth': ..., 'percent_b': ..., 'is_squeeze': ... },
                'history': [ ... last 120 days ... ]
            }
        """
        try:
            if not price_data or len(price_data) < window:
                return None
                
            df = pd.DataFrame(price_data)
            
            # 컬럼명 통일
            df.columns = df.columns.str.lower()
            
            # 숫자 변환
            cols = ['close', 'open', 'high', 'low', 'volume']
            for col in cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 날짜 오름차순 정렬 (과거 -> 현재)
            df = df.sort_values('date', ascending=True)
            
            # 볼린저 밴드 계산
            df['sma'] = df['close'].rolling(window=window).mean()
            df['std'] = df['close'].rolling(window=window).std()
            df['upper_band'] = df['sma'] + (df['std'] * num_std)
            df['lower_band'] = df['sma'] - (df['std'] * num_std)
            
            # %B (Percent B)
            # (Price - Lower Band) / (Upper Band - Lower Band)
            df['percent_b'] = (df['close'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
            
            # Bandwidth
            # (Upper Band - Lower Band) / Middle Band
            df['bandwidth'] = (df['upper_band'] - df['lower_band']) / df['sma']
            
            # Squeeze Detection (120일 기준 최저 Bandwidth 대비 5% 이내 근접 시)
            # 데이터가 120개 미만이면 전체 기간 사용
            min_window = min(120, len(df))
            df['min_bandwidth_120'] = df['bandwidth'].rolling(window=min_window).min()
            df['is_squeeze'] = df['bandwidth'] <= (df['min_bandwidth_120'] * 1.05)
            
            # 최신 값
            last = df.iloc[-1]
            
            summary = {
                'upper': round(float(last['upper_band']), 0),
                'middle': round(float(last['sma']), 0),
                'lower': round(float(last['lower_band']), 0),
                'bandwidth': round(float(last['bandwidth']), 4),
                'percent_b': round(float(last['percent_b']), 4),
                'is_squeeze': bool(last['is_squeeze'])
            }
            
            # 히스토리 (최근 120일) - 차트 및 AI 분석용
            # 필요한 컬럼만 추출
            history_df = df.tail(120).copy()
            history = []
            for _, row in history_df.iterrows():
                history.append({
                    'date': row['date'],
                    'close': int(row['close']),
                    'upper': round(float(row['upper_band']), 0) if not pd.isna(row['upper_band']) else None,
                    'middle': round(float(row['sma']), 0) if not pd.isna(row['sma']) else None,
                    'lower': round(float(row['lower_band']), 0) if not pd.isna(row['lower_band']) else None,
                    'bandwidth': round(float(row['bandwidth']), 4) if not pd.isna(row['bandwidth']) else None,
                    'is_squeeze': bool(row['is_squeeze']) if not pd.isna(row['is_squeeze']) else False
                })
                
            return {
                'summary': summary,
                'history': history
            }
            
        except Exception as e:
            print(f"[TechnicalIndicators] 볼린저 밴드 계산 오류: {e}")
            return None
