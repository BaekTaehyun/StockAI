// API Base URL
const API_BASE = '';

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 키움 주식 대시보드 시작');
    checkAuth();
    loadAccountSummary();
    loadHoldings();
    loadMarketIndices(); // 시장 지수 로드
    loadWatchlist(); // 관심종목 로드

    // 5초마다 자동 새로고침
    setInterval(() => {
        loadAccountSummary();
        loadHoldings();
        loadMarketIndices(); // 시장 지수 주기적 업데이트
        loadWatchlist(); // 관심종목 로드
    }, 5000);
});

// 인증 상태 확인
async function checkAuth() {
    const statusText = document.querySelector('.status-text');
    const statusDot = document.querySelector('.status-dot');

    try {
        const response = await fetch(`${API_BASE}/api/account/summary`);
        if (response.ok) {
            statusText.textContent = '연결됨';
            statusDot.style.background = 'var(--success)';
        } else {
            statusText.textContent = '연결 실패';
            statusDot.style.background = 'var(--danger)';
        }
    } catch (error) {
        statusText.textContent = '오프라인';
        statusDot.style.background = 'var(--warning)';
    }
}

// 계좌 요약 정보 로드
async function loadAccountSummary() {
    try {
        const response = await fetch(`${API_BASE}/api/account/summary`);
        const result = await response.json();

        if (result.success) {
            const data = result.data;

            // 총 매입금액
            document.getElementById('totalPurchase').textContent =
                formatCurrency(data.total_purchase);

            // 총 평가금액
            document.getElementById('totalEval').textContent =
                formatCurrency(data.total_eval);

            // 총 평가손익
            const plElement = document.getElementById('totalPL');
            const rateElement = document.getElementById('profitRate');
            const plCard = plElement.closest('.summary-card');

            plElement.textContent = formatCurrency(data.total_pl);
            rateElement.textContent = formatPercent(data.profit_rate);

            // 수익/손실에 따라 클래스 변경
            plCard.classList.remove('positive', 'negative');
            if (data.total_pl >= 0) {
                plCard.classList.add('positive');
            } else {
                plCard.classList.add('negative');
            }

            // 보유 종목 수
            document.getElementById('holdingsCount').textContent =
                `${data.holdings_count}개`;
        }
    } catch (error) {
        console.error('계좌 요약 로드 실패:', error);
    }
}

// 보유 종목 리스트 로드
// 보유 종목 리스트 로드
async function loadHoldings() {
    try {
        const response = await fetch(`${API_BASE}/api/account/balance`);
        const result = await response.json();

        if (result.success) {
            const holdings = result.data.holdings;
            displayHoldings(holdings);

            // 1. 캐시된 감성 정보가 있으면 즉시 복구 (화면 깜빡임 방지)
            if (typeof restoreSentimentsFromCache === 'function') {
                restoreSentimentsFromCache(holdings);
            }

            // 2. 감성 정보 업데이트 (5분마다)
            if (typeof updateAllSentiments === 'function') {
                const now = Date.now();
                // 첫 로드 감지: lastSentimentUpdate가 없으면 첫 로드
                const isFirst = !window.lastSentimentUpdate;
                const interval = window.SENTIMENT_REFRESH_INTERVAL || (5 * 60 * 1000);

                if (isFirst || now - (window.lastSentimentUpdate || 0) > interval) {
                    console.log('🎗️ 리본 정보 업데이트 시작', isFirst ? '(첫 로드)' : '(주기적 갱신)');
                    updateAllSentiments(holdings);
                    window.lastSentimentUpdate = now;
                }
            }
        }
    } catch (error) {
        console.error('보유 종목 로드 실패:', error);
    }
}

// 보유 종목 표시
function displayHoldings(holdings) {
    const grid = document.getElementById('holdingsGrid');
    grid.innerHTML = '';

    if (!holdings || holdings.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">보유 종목이 없습니다</div>';
        return;
    }

    holdings.forEach(stock => {
        const card = createHoldingCard(stock);
        grid.appendChild(card);
    });
}

// 종목 카드 생성
function createHoldingCard(stock) {
    const card = document.createElement('div');
    card.className = 'holding-card';
    card.onclick = () => openStockModal(stock); // Add click event

    // 숫자 변환
    const stockCode = stock.stk_cd || '';
    const stockName = stock.stk_nm || 'Unknown';
    const quantity = parseInt(stock.rmnd_qty) || 0;
    const purchasePrice = parseInt(stock.pur_pric) || 0;
    const currentPrice = parseInt(stock.cur_prc) || 0;
    const profitLoss = parseInt(stock.evltv_prft) || 0;
    const profitRate = parseFloat(stock.prft_rt) || 0;
    const evalAmount = parseInt(stock.evlt_amt) || 0;

    const plClass = profitLoss >= 0 ? 'positive' : 'negative';
    const plSign = profitLoss >= 0 ? '+' : '';

    // 손익에 따른 배경색과 테두리 색상 설정 (관심 종목과 동일)
    const isProfit = profitLoss >= 0;
    const bgColor = isProfit ? 'rgba(255, 100, 100, 0.05)' : 'rgba(100, 100, 255, 0.05)';
    const borderColor = isProfit ? '#e53e3e' : '#3b82f6';

    card.style.background = bgColor;
    card.style.borderLeft = `4px solid ${borderColor}`;

    const sentimentElements = typeof createSentimentElements === 'function' ?
        createSentimentElements(stockCode) :
        { ribbonHtml: '', footerHtml: '' };
    card.innerHTML = `
        ${sentimentElements.ribbonHtml}
        <div class="holding-header">
            <div>
                <div class="holding-name">${stockName}</div>
                <div class="holding-code">${stockCode.replace('A', '')}</div>
            </div>
            <div>
                <div class="holding-pl ${plClass}">${plSign}${formatCurrency(profitLoss)}</div>
                <div class="holding-pl ${plClass}">${plSign}${profitRate.toFixed(2)}%</div>
            </div>
        </div>
        <div class="holding-body">
            <div class="holding-info">
                <div class="holding-info-label">보유</div>
                <div class="holding-info-value">${formatNumber(quantity)}주</div>
            </div>
            <div class="holding-info">
                <div class="holding-info-label">평가금액</div>
                <div class="holding-info-value">${formatCurrency(evalAmount)}</div>
            </div>
            <div class="holding-info">
                <div class="holding-info-label">매입가</div>
                <div class="holding-info-value">${formatCurrency(purchasePrice)}</div>
            </div>
            <div class="holding-info">
                <div class="holding-info-label">현재가</div>
                <div class="holding-info-value">${formatCurrency(currentPrice)}</div>
            </div>
        </div>
        ${sentimentElements.footerHtml}
    `;
    return card;
}

// 종목 검색 필터
function filterHoldings() {
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.holding-card');

    cards.forEach(card => {
        const name = card.querySelector('.holding-name').textContent.toLowerCase();
        const code = card.querySelector('.holding-code').textContent.toLowerCase();

        if (name.includes(searchText) || code.includes(searchText)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// 모달 닫기
function closeModal() {
    document.getElementById('stockModal').style.display = 'none';
}

// 데이터 새로고침
function refreshData() {
    console.log('🔄 데이터 새로고침...');
    const btn = document.querySelector('.btn-refresh');
    btn.style.transform = 'rotate(360deg)';
    btn.style.transition = 'transform 0.5s ease';

    setTimeout(() => {
        btn.style.transform = '';
    }, 500);

    loadAccountSummary();
    loadHoldings();
    loadMarketIndices();
    checkAuth();
}

// 시장 지수 로드
async function loadMarketIndices() {
    try {
        const response = await fetch(`${API_BASE}/api/market/indices`);
        const result = await response.json();

        if (result.success) {
            const data = result.data;
            updateMarketIndex('kospi', data.kospi);
            updateMarketIndex('kosdaq', data.kosdaq);
        }
    } catch (error) {
        console.error('시장 지수 로드 실패:', error);
    }
}

// 시장 지수 UI 업데이트
function updateMarketIndex(type, data) {
    if (!data) return;

    const priceElem = document.getElementById(`${type}Price`);
    const changeElem = document.getElementById(`${type}Change`);

    if (priceElem && changeElem) {
        // API 데이터에서 기존 + 기호 제거
        const cleanPrice = String(data.price).replace(/^\+/, '');
        const cleanChange = String(data.change).replace(/^\+/, '');
        const cleanRate = String(data.rate).replace(/^\+/, '');

        priceElem.textContent = cleanPrice;

        const rateNum = parseFloat(cleanRate);
        const sign = rateNum > 0 ? '+' : '';

        changeElem.className = ''; // 기존 클래스 초기화
        if (rateNum > 0) {
            changeElem.classList.add('positive');
        } else if (rateNum < 0) {
            changeElem.classList.add('negative');
        }

        changeElem.textContent = `${sign}${cleanChange} (${sign}${cleanRate}%)`;

        // 색상 적용
        if (rateNum > 0) {
            changeElem.style.color = 'var(--success)';
        } else if (rateNum < 0) {
            changeElem.style.color = 'var(--danger)';
        } else {
            changeElem.style.color = 'var(--text-secondary)';
        }
    }
}

// 모달 열기 및 종합 분석 로드
async function openStockModal(stock) {
    // 클릭 시 해당 종목 감성 정보 즉시 갱신
    if (typeof updateSingleSentiment === 'function') {
        updateSingleSentiment(stock.stk_cd);
    }
    const modal = document.getElementById('stockModal');
    const title = document.getElementById('modalTitle');
    const spinner = document.getElementById('loadingSpinner');
    const tabs = document.getElementById('analysisTabs');

    title.textContent = `${stock.stk_nm} (${stock.stk_cd}) 상세 분석`;
    modal.style.display = 'flex'; // block -> flex로 변경하여 중앙 정렬 유지
    spinner.style.display = 'block';
    tabs.style.display = 'none';

    // 이전 데이터 초기화
    document.getElementById('overviewContent').innerHTML = '';
    document.getElementById('supplyContent').innerHTML = '';
    document.getElementById('newsContent').innerHTML = '';
    document.getElementById('technicalContent').innerHTML = '';

    // 탭 초기화 (종합 탭으로)
    switchTab('overview');

    // 종합 분석 로드
    await loadFullAnalysis(stock.stk_cd);

    spinner.style.display = 'none';
    tabs.style.display = 'flex';
}

// 종합 분석 데이터 로드
async function loadFullAnalysis(code) {
    try {
        const response = await fetch(`${API_BASE}/api/analysis/full/${code}`);
        const result = await response.json();

        if (result.success) {
            const data = result.data;
            renderOverview(data);
            renderSupplyDemand(data.supply_demand);
            renderNews(data.news_analysis);
            renderTechnical(data.technical, data.stock_info);
        } else {
            document.getElementById('overviewContent').innerHTML =
                `<div class="error">분석 데이터를 불러올 수 없습니다: ${result.message}</div>`;
        }
    } catch (error) {
        console.error('분석 로드 중 오류:', error);
        document.getElementById('overviewContent').innerHTML =
            `<div class="error">오류가 발생했습니다: ${error.message}</div>`;
    }
}

// 종합 탭 렌더링
function renderOverview(data) {
    const { stock_info, supply_demand, news_analysis, outlook } = data;

    const recommendationClass =
        outlook.recommendation === '매수' ? 'buy' :
            outlook.recommendation === '매도' ? 'sell' : 'neutral';

    const html = `
        <div class="analysis-section">
            <h3>주가 정보</h3>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">현재가</span>
                    <span class="value">${formatCurrency(stock_info.current_price)}</span>
                </div>
                <div class="info-item">
                    <span class="label">전일대비</span>
                    <span class="value ${stock_info.change_rate >= 0 ? 'positive' : 'negative'}">
                        ${formatCurrency(stock_info.change)} (${stock_info.change_rate}%)
                    </span>
                </div>
            </div>
        </div>

        <div class="analysis-section">
            <h3>AI 투자 의견</h3>
            <div class="outlook-card ${recommendationClass}">
                <div class="outlook-header">
                    <span class="recommendation">${outlook.recommendation}</span>
                    <span class="confidence">신뢰도 ${outlook.confidence}%</span>
                </div>
                <p class="reasoning">${outlook.reasoning}</p>
            </div>
        </div>

        <div class="analysis-section">
            <h3>수급 현황</h3>
            <div class="supply-summary">
                <div class="supply-item ${supply_demand.foreign_net >= 0 ? 'positive' : 'negative'}">
                    <span class="label">외국인</span>
                    <span class="value">${formatNumber(supply_demand.foreign_net)}주</span>
                </div>
                <div class="supply-item ${supply_demand.institution_net >= 0 ? 'positive' : 'negative'}">
                    <span class="label">기관</span>
                    <span class="value">${formatNumber(supply_demand.institution_net)}주</span>
                </div>
                <div class="trend">${supply_demand.trend}</div>
            </div>
        </div>

        <div class="analysis-section">
            <h3>뉴스 요약</h3>
            <div class="news-summary">
                <div class="sentiment ${news_analysis.sentiment}">${news_analysis.sentiment}</div>
                <div class="news-box">
                    ${formatNewsText(news_analysis.reason)}
                </div>
            </div>
        </div>
    `;

    document.getElementById('overviewContent').innerHTML = html;
}

// 수급 탭 렌더링
function renderSupplyDemand(data) {
    const html = `
        <div class="analysis-section">
            <h3>외국인 매매</h3>
            <div class="supply-detail">
                <div class="detail-row">
                    <span>매수</span>
                    <span class="positive">${formatNumber(data.foreign_buy)}주</span>
                </div>
                <div class="detail-row">
                    <span>매도</span>
                    <span class="negative">${formatNumber(data.foreign_sell)}주</span>
                </div>
                <div class="detail-row total">
                    <span>순매수</span>
                    <span class="${data.foreign_net >= 0 ? 'positive' : 'negative'}">
                        ${formatNumber(data.foreign_net)}주
                    </span>
                </div>
            </div>
        </div>

        <div class="analysis-section">
            <h3>기관 매매</h3>
            <div class="supply-detail">
                <div class="detail-row">
                    <span>매수</span>
                    <span class="positive">${formatNumber(data.institution_buy)}주</span>
                </div>
                <div class="detail-row">
                    <span>매도</span>
                    <span class="negative">${formatNumber(data.institution_sell)}주</span>
                </div>
                <div class="detail-row total">
                    <span>순매수</span>
                    <span class="${data.institution_net >= 0 ? 'positive' : 'negative'}">
                        ${formatNumber(data.institution_net)}주
                    </span>
                </div>
            </div>
        </div>

        <div class="analysis-section">
            <h3>수급 트렌드</h3>
            <div class="trend-box">
                <p>${data.trend}</p>
            </div>
        </div>
    `;

    document.getElementById('supplyContent').innerHTML = html;
}

// 뉴스 탭 렌더링
function renderNews(data) {
    const formattedSummary = formatNewsText(data.summary);
    const formattedReason = formatNewsText(data.reason);

    const html = `
        <div class="analysis-section">
            <div class="sentiment-badge ${data.sentiment}">
                <span>뉴스 분위기: ${data.sentiment}</span>
            </div>
        </div>

        <div class="analysis-section">
            <h3>뉴스 요약</h3>
            <div class="news-box">
                ${formattedSummary}
            </div>
        </div>

        <div class="analysis-section">
            <h3>등락 원인 분석</h3>
            <div class="reason-box">
                ${formattedReason}
            </div>
        </div>
    `;

    document.getElementById('newsContent').innerHTML = html;
}

// 기술적 분석 탭 렌더링
function renderTechnical(data, stockInfo) {
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


// 탭 전환 함수
function switchTab(tabName) {
    // 모든 탭 버튼에서 active 제거
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // 클릭된 탭 버튼에 active 추가
    event.target.classList.add('active');

    // 모든 탭 콘텐츠 숨기기
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });

    // 선택된 탭 콘텐츠 표시
    document.getElementById(tabName).classList.remove('hidden');
}

// 분봉 차트 로드
async function loadMinuteChart(code) {
    try {
        const response = await fetch(`${API_BASE}/api/chart/minute/${code}`);
        const result = await response.json();

        if (result.success) {
            renderChart(result.data);
        } else {
            console.error('차트 데이터 로드 실패:', result.message);
        }
    } catch (error) {
        console.error('차트 로드 중 오류:', error);
    }
}

// 차트 렌더링
function renderChart(data) {
    const ctx = document.getElementById('minuteChart').getContext('2d');

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
}

// 유틸리티 함수들

// 뉴스 텍스트 포맷팅 함수
function formatNewsText(text) {
    if (!text) return '';

    // 0. Pre-process: Split embedded titles into new lines
    // Look for " * **" or " * [" patterns and replace with newline
    let processedText = text.replace(/\s+[\*•]\s+(?=\*\*|\[)/g, '\n');

    // Split into lines
    const lines = processedText.split('\n');
    let html = '';

    lines.forEach(line => {
        line = line.trim();
        if (!line) return;

        // 1. Remove leading special chars (*, -, bullets, digits)
        let cleanLine = line.replace(/^[-*•\d\.]+\s*/, '');

        // 2. Identify Title and Body
        let title = '';
        let body = '';

        // Check for **Title**
        const boldMatch = cleanLine.match(/\*\*(.*?)\*\*/);

        if (boldMatch) {
            title = boldMatch[1];
            // Body is everything after the bold part (and optional colon)
            body = cleanLine.replace(/\*\*.*?\*\*\s*:?\s*/, '');
        } else {
            // Check for Colon separator if no bold title found
            const colonIndex = cleanLine.indexOf(':');
            if (colonIndex > -1 && colonIndex < 50) {
                title = cleanLine.substring(0, colonIndex);
                body = cleanLine.substring(colonIndex + 1);
            } else {
                // Fallback: Check for [Keyword] at start
                if (cleanLine.startsWith('[')) {
                    const bracketEnd = cleanLine.indexOf(']');
                    if (bracketEnd > -1) {
                        title = cleanLine.substring(0, bracketEnd + 1);
                        body = cleanLine.substring(bracketEnd + 1);
                    }
                }

                if (!title) {
                    body = cleanLine;
                }
            }
        }

        // 3. Clean Title (remove [ ] if present inside, per user request to remove special chars)
        if (title) {
            title = title.replace(/[\[\]]/g, '').trim();
            // Also remove any leading/trailing * just in case
            title = title.replace(/^\*+|\*+$/g, '').trim();
        }

        // 4. Clean Body (remove leading * or : if any)
        if (body) {
            body = body.replace(/^\s*[:*]\s*/, '').trim();
        }

        // 5. Construct HTML
        if (title) {
            html += `
                <div class="news-item">
                    <span class="news-title">${title}</span>
                    <div class="news-body">${body}</div>
                </div>`;
        } else {
            // Just body
            html += `
                <div class="news-item">
                    <div class="news-body">${body}</div>
                </div>`;
        }
    });

    return html;
}

// 통화 포맷
function formatCurrency(value) {
    if (value === null || value === undefined) return '0원';
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// 숫자 포맷
function formatNumber(value) {
    if (value === null || value === undefined) return '0';
    return new Intl.NumberFormat('ko-KR').format(value);
}

// 퍼센트 포맷
function formatPercent(value) {
    if (value === null || value === undefined) return '0.00%';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
}
// 감성 분석 및 리본 로직
const sentimentCache = {};

function createSentimentElements(stockCode) {
    // 리본 HTML 생성 (초기에는 로딩 상태 또는 숨김)
    const ribbonHtml = `<div id="ribbon-${stockCode}" class="ribbon" style="display: none;"><span>분석중</span></div>`;
    const footerHtml = `<div id="footer-${stockCode}" class="sentiment-footer" style="display: none;"></div>`;

    return { ribbonHtml, footerHtml };
}

async function updateAllSentiments(holdings) {
    for (const stock of holdings) {
        await updateSingleSentiment(stock.stk_cd);
    }
}

async function updateSingleSentiment(code) {
    try {
        // 캐시 확인 (5분 유효)
        const now = Date.now();
        if (sentimentCache[code] && (now - sentimentCache[code].timestamp < 5 * 60 * 1000)) {
            renderRibbon(code, sentimentCache[code].data);
            return;
        }

        const response = await fetch(`${API_BASE}/api/analysis/sentiment/${code}`);
        const result = await response.json();

        if (result.success) {
            const data = result.data;
            sentimentCache[code] = {
                timestamp: now,
                data: data
            };
            renderRibbon(code, data);
        }
    } catch (error) {
        console.error(`감성 분석 로드 실패 (${code}):`, error);
    }
}

function renderRibbon(code, data) {
    const ribbon = document.getElementById(`ribbon-${code}`);
    const footer = document.getElementById(`footer-${code}`);

    if (!ribbon) return;

    // AI 추천에 따른 리본 스타일
    const recommendation = data.ai_recommendation; // 매수, 매도, 관망
    let ribbonClass = 'neutral';
    let ribbonText = recommendation;

    if (recommendation === '매수') {
        ribbonClass = 'buy';
    } else if (recommendation === '매도') {
        ribbonClass = 'sell';
    }

    ribbon.className = `ribbon ${ribbonClass}`;
    ribbon.innerHTML = `<span>${ribbonText}</span>`;
    ribbon.style.display = 'block';

    // 푸터 정보 (뉴스 감성 등)
    if (footer) {
        footer.innerHTML = `
            <span class="sentiment-tag ${data.news_sentiment}">${data.news_sentiment}</span>
            <span class="confidence-tag">신뢰도 ${data.ai_confidence}%</span>
        `;
        footer.style.display = 'flex';
    }
}

function restoreSentimentsFromCache(holdings) {
    holdings.forEach(stock => {
        const code = stock.stk_cd;
        if (sentimentCache[code]) {
            renderRibbon(code, sentimentCache[code].data);
        }
    });
}

// 관심종목 로드 및 표시
async function loadWatchlist() {
    try {
        const response = await fetch(`${API_BASE}/api/watchlist/prices`);
        const result = await response.json();

        if (result.success && result.data) {
            displayWatchlist(result.data);
        }
    } catch (error) {
        console.error('관심종목 로드 실패:', error);
    }
}


// 관심종목 카드 표시
function displayWatchlist(stocks) {
    const grid = document.getElementById('watchlistGrid');
    if (!grid) return;

    if (stocks.length === 0) {
        grid.innerHTML = '<p style="text-align: center; padding: 2rem; color: #888;">관심종목이 없습니다. 위에서 종목 코드를 입력하여 추가하세요.</p>';
        return;
    }

    // 기존 카드 코드 목록
    const existingCodes = Array.from(grid.querySelectorAll('.watchlist-card')).map(card => card.getAttribute('data-code'));

    // 새로운 코드 목록
    const newCodes = stocks.map(item => item.code);

    // 제거된 카드 삭제
    existingCodes.forEach(code => {
        if (!newCodes.includes(code)) {
            const card = grid.querySelector(`[data-code="${code}"]`);
            if (card) card.remove();
        }
    });

    // 새로운 카드만 추가
    stocks.forEach(item => {
        if (item.data && !existingCodes.includes(item.code)) {
            const card = createWatchlistCard(item.code, item.data);
            grid.appendChild(card);
        }
    });

    // 감성 분석 자동 업데이트
    if (typeof updateAllSentiments === 'function') {
        const watchlistItems = stocks.map(item => ({ stk_cd: item.code }));

        if (typeof restoreSentimentsFromCache === 'function') {
            restoreSentimentsFromCache(watchlistItems);
        }

        const now = Date.now();
        const isFirst = !window.lastWatchlistSentimentUpdate;
        const interval = 5 * 60 * 1000;

        if (isFirst || now - (window.lastWatchlistSentimentUpdate || 0) > interval) {
            console.log('🎗️ 관심종목 리본 정보 업데이트');
            updateAllSentiments(watchlistItems);
            window.lastWatchlistSentimentUpdate = now;
        }
    }
}

// 관심종목 카드 생성
function createWatchlistCard(code, stockData) {
    const card = document.createElement('div');
    card.className = 'watchlist-card';
    card.setAttribute('data-code', code);
    card.setAttribute('data-supply-loaded', 'false');

    const name = stockData.name || code;
    const price = parseInt(stockData.price || 0);
    const change = parseInt(stockData.change || 0);
    const rate = parseFloat(stockData.rate || 0);

    const isUp = rate >= 0;
    const bgColor = isUp ? 'rgba(255, 100, 100, 0.05)' : 'rgba(100, 100, 255, 0.05)';
    const textColor = isUp ? '#e53e3e' : '#3b82f6';
    const sign = isUp ? '+' : '';

    card.style.background = bgColor;
    card.style.borderLeft = `4px solid ${isUp ? '#e53e3e' : '#3b82f6'}`;
    card.style.marginBottom = '1.5rem';

    const sentimentElements = typeof createSentimentElements === 'function' ?
        createSentimentElements(code) :
        { ribbonHtml: '', footerHtml: '' };

    card.innerHTML = `
        ${sentimentElements.ribbonHtml}
        <div class="watchlist-card-content">
            <div style="margin-bottom: 1.5rem;">
                <div class="watchlist-header">
                    <div>
                        <div class="watchlist-name">${name}</div>
                        <div class="watchlist-code">${code}</div>
                    </div>
                    <div class="watchlist-rate" style="color: ${textColor};">${sign}${rate.toFixed(2)}%</div>
                </div>
            </div>
            <div class="watchlist-price-row">
                <div class="watchlist-price">${formatCurrency(price)}</div>
                <div class="watchlist-change" style="color: ${textColor};">${sign}${formatCurrency(change)}</div>
            </div>
            <div style="padding-top: 1rem; margin-top: 1rem;">
                <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <div style="font-size: 0.75rem; color: #888; margin-bottom: 0.4rem; font-weight: 600;">수급 정보</div>
                        <div id="supply-${code}" style="font-size: 0.85rem; min-height: 24px;">
                            <span style="color: #888;">분석중...</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #888; margin-bottom: 0.4rem; font-weight: 600;">등락 원인</div>
                        <div id="reason-${code}" style="font-size: 0.85rem; color: var(--text-primary); line-height: 1.4; min-height: 24px;">
                            로딩중...
                        </div>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.05); display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                    <button onclick="removeFromWatchlist('${code}'); event.stopPropagation();" 
                        style="flex: 0 0 auto; padding: 0.5rem 1.2rem; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.9rem; line-height: 1.5;">
                        삭제
                    </button>
                    <div id="footer-${code}" class="sentiment-footer" style="display: none; margin-left: auto; align-items: center; justify-content: flex-end; gap: 0.5rem;"></div>
                </div>
            </div>
        `;

    card.onclick = (e) => {
        if (e.target.tagName !== 'BUTTON') {
            openStockModal({ code, name, price: stockData.price, stk_cd: code, stk_nm: name });
        }
    };

    setTimeout(() => loadSupplyInfoOnce(card, code), 100);

    return card;
}

// 수급 정보를 한 번만 로드
async function loadSupplyInfoOnce(cardElement, code) {
    if (cardElement.getAttribute('data-supply-loaded') === 'true') {
        return;
    }

    const supplyElem = document.getElementById(`supply-${code}`);
    const reasonElem = document.getElementById(`reason-${code}`);

    if (!supplyElem || !reasonElem) return;

    try {
        const response = await fetch(`${API_BASE}/api/analysis/full/${code}`);
        const result = await response.json();

        if (result.success && result.data) {
            const data = result.data;

            if (data.supply_demand) {
                const foreigner = data.supply_demand.foreign_net || 0;
                const institution = data.supply_demand.institution_net || 0;

                let badge = '';
                if (foreigner > 0) {
                    badge = '<span style="display: inline-block; background: #10b981; color: white; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">외인 매수중 📈</span>';
                } else if (foreigner < 0) {
                    badge = '<span style="display: inline-block; background: #ef4444; color: white; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">외인 매도중 📉</span>';
                } else if (institution > 0) {
                    badge = '<span style="display: inline-block; background: #6366f1; color: white; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">기관 매수중 🏢</span>';
                } else {
                    badge = '<span style="color: #888; font-size: 0.8rem;">수급 보합</span>';
                }
                supplyElem.innerHTML = badge;
            }

            if (data.news_analysis && data.news_analysis.reason) {
                const reason = data.news_analysis.reason.split('\n')[0].substring(0, 60);
                reasonElem.textContent = reason + (reason.length >= 60 ? '...' : '');
                reasonElem.style.color = 'var(--text-primary)';
            }
            else {
                reasonElem.innerHTML = '<span style="color: #888;">-</span>';
            }

            cardElement.setAttribute('data-supply-loaded', 'true');
        }
    }
    catch (error) {
        console.error(`수급 정보 로드 실패 (${code}):`, error);
        supplyElem.innerHTML = '<span style="color: #888; font-size: 0.75rem;">-</span>';
        reasonElem.innerHTML = '<span style="color: #888;">-</span>';
    }
}


// 관심종목 추가
async function addToWatchlist() {
    const input = document.getElementById('watchlistInput');
    const code = input.value.trim();

    if (!code) {
        alert('종목 코드를 입력하세요');
        return;
    }

    if (!/^\d{6}$/.test(code)) {
        alert('올바른 종목 코드를 입력하세요 (6자리 숫자)');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/watchlist/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });

        const result = await response.json();

        if (result.success) {
            alert(`종목 ${code}가 추가되었습니다`);
            input.value = '';
            loadWatchlist();
        } else {
            alert(result.message || '추가 실패');
        }
    } catch (error) {
        console.error('추가 오류:', error);
        alert('종목 추가 중 오류가 발생했습니다');
    }
}

// 관심종목 삭제
async function removeFromWatchlist(code) {
    if (!confirm(`종목 ${code}를 관심종목에서 삭제하시겠습니까?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/watchlist/remove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });

        const result = await response.json();

        if (result.success) {
            loadWatchlist();
        } else {
            alert(result.message || '삭제 실패');
        }
    } catch (error) {
        console.error('삭제 오류:', error);
        alert('종목 삭제 중 오류가 발생했습니다');
    }
}