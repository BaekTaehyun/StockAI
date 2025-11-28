// charts.js - Chart rendering logic

let minuteChart = null;

const Charts = {
    // 분봉 차트 렌더링
    renderMinuteChart(data) {
        const canvas = document.getElementById('minuteChart');
        if (!canvas) {
            console.warn('Minute chart canvas not found');
            return;
        }
        const ctx = canvas.getContext('2d');

        // 기존 차트 파괴
        if (minuteChart) {
            minuteChart.destroy();
        }

        // 데이터 가공 (API 응답 구조에 따라 조정 필요)
        // Assuming data is list of { stck_bsop_date, stck_cntg_hour, stck_prpr }
        // Reverse to show oldest to newest
        const labels = data.map(item => item.stck_cntg_hour).reverse();
        const prices = data.map(item => parseInt(item.stck_prpr)).reverse();

        minuteChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '주가',
                    data: prices,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    },

    // 기술적 분석 탭 렌더링
    renderTechnical(data, stockInfo) {
        // 현재가 가져오기
        const currentPriceStr = stockInfo ? stockInfo.current_price : '0';
        const currentPrice = parseInt(String(currentPriceStr).replace(/[^0-9]/g, '')) || 0;

        // RSI 색상 및 구간 결정
        let rsiColor = '#6366f1'; // 기본 보라색
        let rsiZone = '중립';
        if (data.rsi > 70) {
            rsiColor = '#ef4444'; // 빨간색
            rsiZone = '과매수';
        } else if (data.rsi < 30) {
            rsiColor = '#10b981'; // 녹색
            rsiZone = '과매도';
        }

        // 이동평균선 괴리율 계산
        const ma5Gap = data.ma5 && currentPrice ? ((currentPrice - data.ma5) / data.ma5 * 100).toFixed(2) : '0.00';
        const ma20Gap = data.ma20 && currentPrice ? ((currentPrice - data.ma20) / data.ma20 * 100).toFixed(2) : '0.00';
        const ma60Gap = data.ma60 && currentPrice ? ((currentPrice - data.ma60) / data.ma60 * 100).toFixed(2) : '0.00';

        // 이동평균선 비교 바 (최대값 기준 정규화)
        const maxMa = Math.max(currentPrice, data.ma5, data.ma20, data.ma60);
        const currentBarWidth = (currentPrice / maxMa * 100).toFixed(1);
        const ma5BarWidth = (data.ma5 / maxMa * 100).toFixed(1);
        const ma20BarWidth = (data.ma20 / maxMa * 100).toFixed(1);
        const ma60BarWidth = (data.ma60 / maxMa * 100).toFixed(1);

        // MACD 바 너비
        const macdBarWidth = Math.min(Math.abs(data.macd) / 100 * 100, 100);
        const macdClass = data.macd >= 0 ? 'positive' : 'negative';
        const macdIcon = data.macd >= 0 ? '📈' : '📉';

        const html = `
            <div class="analysis-section">
                <h3>RSI (상대강도지수)</h3>
                <div class="indicator">
                    <div class="rsi-header">
                        <div class="rsi-value-large" style="color: ${rsiColor}">
                            ${data.rsi}
                        </div>
                        <div class="rsi-zone" style="background: ${rsiColor}33; color: ${rsiColor}; padding: 0.5rem 1rem; border-radius: 20px;">
                            ${rsiZone}
                        </div>
                    </div>
                    <div class="indicator-bar" style="position: relative; margin: 1rem 0; height: 50px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                        <div class="bar-fill" style="width: ${data.rsi}%; background: ${rsiColor}; height: 100%; transition: all 0.3s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 1rem;">
                            <span style="color: white; font-weight: 700; font-size: 1.2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">${data.rsi}</span>
                        </div>
                        <div style="position: absolute; left: 30%; top: 0; bottom: 0; width: 2px; background: rgba(255,255,255,0.3);"></div>
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: rgba(255,255,255,0.5);"></div>
                        <div style="position: absolute; left: 70%; top: 0; bottom: 0; width: 2px; background: rgba(255,255,255,0.3);"></div>
                    </div>
                    <div class="indicator-labels">
                        <span style="color: #10b981">과매도 (30)</span>
                        <span>중립 (50)</span>
                        <span style="color: #ef4444">과매수 (70)</span>
                    </div>
                </div>
            </div>

            <div class="analysis-section">
                <h3>MACD</h3>
                <div class="indicator">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <span class="number" style="font-size: 2rem; font-weight: 700; color: var(--accent-1);">${data.macd.toLocaleString()}</span>
                            <span style="font-size: 1.5rem;">${macdIcon}</span>
                        </div>
                        <span class="signal-badge" style="padding: 0.5rem 1rem; background: rgba(99,102,241,0.2); border-radius: 20px; color: var(--accent-1);">${data.macd_signal}</span>
                    </div>
                    <div style="margin-top: 0.75rem; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px; font-size: 0.9rem; color: var(--text-secondary);">
                        ${data.macd >= 0 ? '📈 상승 추세 - 매수 시점 고려' : '📉 하락 추세 - 관망 또는 매도 고려'}
                    </div>
                </div>
            </div>

            <div class="analysis-section">
                <h3>이동평균선</h3>
                <div class="ma-visualization">
                    <div class="ma-bar-item">
                        <div class="ma-label">현재가</div>
                        <div class="ma-bar-container">
                            <div class="ma-bar current-price" style="width: ${currentBarWidth}%; background: linear-gradient(90deg, #6366f1, #8b5cf6); padding: 0.5rem; border-radius: 6px; font-weight: 600; font-size: 0.9rem;">
                                ${formatCurrency(currentPrice)}
                            </div>
                        </div>
                    </div>
                    <div class="ma-bar-item">
                        <div class="ma-label">5일선</div>
                        <div class="ma-bar-container">
                            <div class="ma-bar ma5" style="width: ${ma5BarWidth}%; background: rgba(255, 200, 87, 0.3); padding: 0.5rem; border-radius: 6px; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;">
                                <span>${formatCurrency(data.ma5)}</span>
                                <span class="ma-gap ${parseFloat(ma5Gap) >= 0 ? 'positive' : 'negative'}" style="font-size: 0.9rem; font-weight: 600;">${parseFloat(ma5Gap) >= 0 ? '+' : ''}${ma5Gap}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="ma-bar-item">
                        <div class="ma-label">20일선</div>
                        <div class="ma-bar-container">
                            <div class="ma-bar ma20" style="width: ${ma20BarWidth}%; background: rgba(41, 182, 246, 0.3); padding: 0.5rem; border-radius: 6px; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;">
                                <span>${formatCurrency(data.ma20)}</span>
                                <span class="ma-gap ${parseFloat(ma20Gap) >= 0 ? 'positive' : 'negative'}" style="font-size: 0.9rem; font-weight: 600;">${parseFloat(ma20Gap) >= 0 ? '+' : ''}${ma20Gap}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="ma-bar-item">
                        <div class="ma-label">60일선</div>
                        <div class="ma-bar-container">
                            <div class="ma-bar ma60" style="width: ${ma60BarWidth}%; background: rgba(171, 71, 188, 0.3); padding: 0.5rem; border-radius: 6px; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;">
                                <span>${formatCurrency(data.ma60)}</span>
                                <span class="ma-gap ${parseFloat(ma60Gap) >= 0 ? 'positive' : 'negative'}" style="font-size: 0.9rem; font-weight: 600;">${parseFloat(ma60Gap) >= 0 ? '+' : ''}${ma60Gap}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="ma-signal-box" style="margin-top: 1rem; padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 8px; text-align: center; color: var(--accent-1); font-size: 1.1rem;">
                        <strong>${data.ma_signal}</strong>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('technicalContent').innerHTML = html;
    }
};
