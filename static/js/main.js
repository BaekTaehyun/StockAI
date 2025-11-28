// main.js - Initialization and event listeners

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

    // 1초마다 자동 새로고침 (실시간)
    setInterval(() => {
        loadAccountSummary();
        loadHoldings();
        loadMarketIndices();
        loadWatchlist();
    }, 1000);
});

// 데이터 로드 함수들 (UI와 API 연결)
async function checkAuth() {
    const result = await API.fetchAccountSummary(); // 계좌 정보로 연결 확인
    UI.updateAuthStatus(result.success);
}

async function loadAccountSummary() {
    const result = await API.fetchAccountSummary();
    if (result.success) {
        UI.updateAccountSummary(result.data);
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
        const interval = window.SENTIMENT_REFRESH_INTERVAL || (30 * 60 * 1000); // 30분

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
    const ribbonHtml = `<div id="ribbon-${stockCode}" class="ribbon" style="display: none;"><span>분석중</span></div>`;
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
                await new Promise(resolve => setTimeout(resolve, 7000));
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

    if (!ribbon) return;

    const recommendation = data.ai_recommendation;
    let ribbonClass = 'neutral';

    if (recommendation === '매수') {
        ribbonClass = 'buy';
    } else if (recommendation === '매도') {
        ribbonClass = 'sell';
    }

    ribbon.className = `ribbon ${ribbonClass}`;
    ribbon.innerHTML = `<span>${recommendation}</span>`;
    ribbon.style.display = 'block';

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
    const interval = 30 * 60 * 1000; // 30분

    if (isFirst || now - (window.lastWatchlistSentimentUpdate || 0) > interval) {
        console.log('🎗️ 관심종목 리본 정보 업데이트');
        updateAllSentiments(watchlistItems);
        window.lastWatchlistSentimentUpdate = now;
    }
};
