/**
 * main.js - 메인 애플리케이션 초기화 및 이벤트 리스너
 * ================================================================
 * 주식 모니터링 대시보드의 메인 JavaScript 파일입니다.
 * 
 * 주요 기능:
 * - 페이지 로드 시 초기화
 * - 실시간 데이터 갱신 (2초마다 자동 새로고침)
 * - 감성 분석 및 AI 리본 표시 (30분 주기)
 * - 관심종목 추가/삭제
 * - 시장 지수 모니터링
 * 
 * 의존성:
 * - api.js: 서버 API 통신
 * - ui_core.js, ui_cards.js, ui_details.js: UI 렌더링
 * ================================================================
 */


// 감성 분석 및 리본 로직 (전역 상태)
const sentimentCache = {};

// 전역 함수로 노출 (HTML에서 호출되는 경우)
window.addToWatchlist = async () => {
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

    const result = await API.addToWatchlist(code);
    if (result.success) {
        alert(`종목 ${code}가 추가되었습니다`);
        input.value = '';
        loadWatchlist();
    } else {
        alert(result.message || '추가 실패');
    }
};

window.removeFromWatchlist = async (code) => {
    if (!confirm(`종목 ${code}를 관심종목에서 삭제하시겠습니까?`)) {
        return;
    }

    const result = await API.removeFromWatchlist(code);
    if (result.success) {
        loadWatchlist();
    } else {
        alert(result.message || '삭제 실패');
    }
};

// UI에서 호출하는 탭 전환 함수 전역 노출
window.switchTab = (tabName) => UI.switchTab(tabName);
window.closeModal = () => UI.closeModal();
window.refreshData = () => UI.refreshData();
window.filterHoldings = () => UI.filterHoldings();

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 키움 주식 대시보드 시작');
    checkAuth();
    loadAccountSummary();
    loadHoldings();
    loadMarketIndices();
    loadWatchlist();

    // 10초마다 자동 새로고침 (리소스 절약)
    setInterval(() => {
        loadAccountSummary();
        loadHoldings();
        loadMarketIndices();
        loadWatchlist();
    }, 10000);
});

// 데이터 로드 함수들 (UI와 API 연결)
async function checkAuth() {
    const result = await API.fetchAccountSummary(); // 계좌 정보로 연결 확인
    UI.updateAuthStatus(result.success);
}

async function loadAccountSummary() {
    console.log('🔄 [계좌요약] API 호출 중...');
    const result = await API.fetchAccountSummary();
    console.log('📊 [계좌요약] API 응답:', result);

    if (result.success) {
        console.log('✅ [계좌요약] 데이터 수신:', {
            매입금액: result.data.total_purchase,
            평가금액: result.data.total_eval,
            평가손익: result.data.total_pl,
            보유종목: result.data.holdings_count
        });
        UI.updateAccountSummary(result.data);
    } else {
        console.error('❌ [계좌요약] API 실패:', result.message);
    }
}

async function loadHoldings() {
    const result = await API.fetchHoldings();
    if (result.success) {
        const holdings = result.data.holdings;
        UI.displayHoldings(holdings);

        // 감성 정보 복구 및 업데이트
        restoreSentimentsFromCache(holdings);

        const now = Date.now();
        const isFirst = !window.lastSentimentUpdate;
        const interval = window.SENTIMENT_REFRESH_INTERVAL || (2 * 60 * 60 * 1000); // 2시간

        if (isFirst || now - (window.lastSentimentUpdate || 0) > interval) {
            console.log('🎗️ 리본 정보 업데이트 시작', isFirst ? '(첫 로드)' : '(주기적 갱신)');
            updateAllSentiments(holdings);
            window.lastSentimentUpdate = now;
        }
    }
}

async function loadMarketIndices() {
    const result = await API.fetchMarketIndices();
    if (result.success) {
        const data = result.data;
        UI.updateMarketIndex('kospi', data.kospi);
        UI.updateMarketIndex('kosdaq', data.kosdaq);
        UI.updateMarketIndex('usdkrw', data.usdkrw);
    }
}

async function loadWatchlist() {
    const result = await API.fetchWatchlistPrices();
    if (result.success && result.data) {
        UI.displayWatchlist(result.data);
    }
}

// 전역으로 노출하여 UI.refreshData에서 호출 가능하게 함
window.loadAllData = () => {
    loadAccountSummary();
    loadHoldings();
    loadMarketIndices();
    checkAuth();
};

// 감성 분석 관련 함수들
function createSentimentElements(stockCode) {
    const ribbonHtml = `<div id="ribbon-${stockCode}" class="ai-ribbon" style="display: none;"><span>분석중</span></div>`;
    const footerHtml = `<div id="footer-${stockCode}" class="sentiment-footer" style="display: none;"></div>`;
    return { ribbonHtml, footerHtml };
}
// UI.js에서 사용할 수 있도록 전역 노출
window.createSentimentElements = createSentimentElements;

async function updateAllSentiments(holdings) {
    for (let i = 0; i < holdings.length; i++) {
        const stock = holdings[i];
        // holdings 배열의 요소가 객체인지 확인 (관심종목의 경우 {stk_cd: code} 형태로 전달됨)
        const code = stock.stk_cd || stock.code;

        if (code) {
            // 7초 딜레이 추가 (첫 번째 종목은 즉시 실행)
            if (i > 0) {
                // 설정된 딜레이 사용 (기본값 15초)
                const delay = (window.SENTIMENT_UPDATE_DELAY_SECONDS || 15) * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
            await updateSingleSentiment(code);
        }
    }
}

async function updateSingleSentiment(code) {
    try {
        const now = Date.now();
        // 캐시 확인 (30분)
        if (sentimentCache[code] && (now - sentimentCache[code].timestamp < 30 * 60 * 1000)) {
            renderRibbon(code, sentimentCache[code].data);
            return;
        }

        const result = await API.fetchSentiment(code);
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
// UI.js에서 호출 가능하도록 전역 노출
window.updateSingleSentiment = updateSingleSentiment;

function renderRibbon(code, data) {
    const ribbon = document.getElementById(`ribbon-${code}`);
    const footer = document.getElementById(`footer-${code}`);
    const strategyElem = document.getElementById(`strategy-${code}`);

    if (ribbon) {
        const recommendation = data.ai_recommendation || data.recommendation || '중립';
        let ribbonClass = 'neutral';  // 기본값

        // 5단계 투자의견 매핑
        if (recommendation === '강력매수') {
            ribbonClass = 'strong-buy';  // 🔥 진한 빨강/주황
        } else if (recommendation === '매수') {
            ribbonClass = 'buy';  // ✅ 빨강
        } else if (recommendation === '분할매수') {
            ribbonClass = 'split-buy';  // ⚠️ 노랑/주황
        } else if (recommendation === '관망') {
            ribbonClass = 'hold';  // ⏸️ 회색
        } else if (recommendation === '매도') {
            ribbonClass = 'sell';  // ❄️ 파랑
        }

        ribbon.className = `ai-ribbon ${ribbonClass}`;
        ribbon.innerHTML = `<span>${recommendation}</span>`;
        ribbon.style.display = 'block';
    }

    if (footer) {
        const sentiment = data.news_sentiment || '중립';
        const confidence = data.ai_confidence || data.confidence || 0;

        footer.innerHTML = `
            <span class="sentiment-tag ${sentiment}">${sentiment}</span>
            <span class="confidence-tag">신뢰도 ${confidence}%</span>
        `;
        footer.style.display = 'flex';
    }

    // 전략 정보 업데이트
    if (strategyElem && data.price_strategy) {
        const entry = data.price_strategy.entry || '-';
        const target = data.price_strategy.target || '-';
        const stopLoss = data.price_strategy.stop_loss || '-';

        strategyElem.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 4px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                    <span style="color: #aaa;">진입</span>
                    <span style="color: #fff; font-weight: 600;">${entry}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                    <span style="color: #aaa;">목표</span>
                    <span style="color: #f87171; font-weight: 600;">${target}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                    <span style="color: #aaa;">손절</span>
                    <span style="color: #60a5fa; font-weight: 600;">${stopLoss}</span>
                </div>
            </div>
        `;
    }
}

function restoreSentimentsFromCache(holdings) {
    holdings.forEach(stock => {
        const code = stock.stk_cd || stock.code;
        if (code && sentimentCache[code]) {
            renderRibbon(code, sentimentCache[code].data);
        }
    });
}
window.restoreSentimentsFromCache = restoreSentimentsFromCache;

// 관심종목 감성 업데이트 트리거 (UI.js에서 호출)
window.triggerWatchlistSentimentUpdate = (stocks) => {
    const watchlistItems = stocks.map(item => ({ stk_cd: item.code }));
    restoreSentimentsFromCache(watchlistItems);

    const now = Date.now();
    const isFirst = !window.lastWatchlistSentimentUpdate;
    const interval = 2 * 60 * 60 * 1000; // 2시간

    if (isFirst || now - (window.lastWatchlistSentimentUpdate || 0) > interval) {
        console.log('🎗️ 관심종목 리본 정보 업데이트');
        updateAllSentiments(watchlistItems);
        window.lastWatchlistSentimentUpdate = now;
    }
};

// 종합 분석 데이터로부터 감성 정보 업데이트 (UI.js에서 호출)
window.updateSentimentFromAnalysis = (code, analysisData) => {
    if (!analysisData || !analysisData.outlook || !analysisData.news_analysis) return;

    const sentimentData = {
        ai_recommendation: analysisData.outlook.recommendation,
        ai_confidence: analysisData.outlook.confidence,
        news_sentiment: analysisData.news_analysis.sentiment,
        supply_trend: analysisData.supply_demand ? analysisData.supply_demand.trend : '정보 없음',
        price_strategy: analysisData.outlook.price_strategy,
        supply_demand: analysisData.supply_demand
    };

    // 캐시 업데이트
    sentimentCache[code] = {
        timestamp: Date.now(),
        data: sentimentData
    };

    // 리본 렌더링
    renderRibbon(code, sentimentData);

    // 수급 정보 카드 업데이트 (추가된 로직)
    const supplyElem = document.getElementById(`supply-${code}`);
    if (supplyElem && analysisData.supply_demand) {
        const foreigner = analysisData.supply_demand.foreign_net || 0;
        const institution = analysisData.supply_demand.institution_net || 0;

        let badge = '';
        if (foreigner > 0 && institution > 0) {
            badge = '<span class="badge-supply buy">쌍끌이 매수 🚀</span>';
        } else if (foreigner < 0 && institution < 0) {
            badge = '<span class="badge-supply sell">양매도 📉</span>';
        } else if (foreigner > 0 && institution < 0) {
            badge = `<div style="display: flex; flex-direction: column; gap: 4px;">
                <span class="badge-supply buy" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">외인 매수</span>
                <span class="badge-supply sell" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">기관 매도</span>
            </div>`;
        } else if (foreigner < 0 && institution > 0) {
            badge = `<div style="display: flex; flex-direction: column; gap: 4px;">
                <span class="badge-supply sell" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">외인 매도</span>
                <span class="badge-supply buy" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">기관 매수</span>
            </div>`;
        } else if (foreigner > 0) {
            badge = '<span class="badge-supply buy">외인 매수중 📈</span>';
        } else if (foreigner < 0) {
            badge = '<span class="badge-supply sell">외인 매도중 📉</span>';
        } else if (institution > 0) {
            badge = '<span class="badge-supply buy">기관 매수중 🏢</span>';
        } else if (institution < 0) {
            badge = '<span class="badge-supply sell">기관 매도중 📉</span>';
        } else {
            badge = '<span class="badge-supply neutral">수급 보합</span>';
        }
        supplyElem.innerHTML = badge;
    }
};
