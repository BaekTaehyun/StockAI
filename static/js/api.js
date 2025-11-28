// api.js - API communication

const API_BASE = '';

const API = {
    // 계좌 요약 정보 로드
    async fetchAccountSummary() {
        try {
            const response = await fetch(`${API_BASE}/api/account/summary`);
            return await response.json();
        } catch (error) {
            console.error('계좌 요약 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 보유 종목 리스트 로드
    async fetchHoldings() {
        try {
            const response = await fetch(`${API_BASE}/api/account/balance`);
            return await response.json();
        } catch (error) {
            console.error('보유 종목 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 시장 지수 로드
    async fetchMarketIndices() {
        try {
            const response = await fetch(`${API_BASE}/api/market/indices`);
            return await response.json();
        } catch (error) {
            console.error('시장 지수 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 종합 분석 데이터 로드 (강제 갱신 지원)
    async fetchFullAnalysis(code, forceRefresh = false) {
        try {
            let url = `${API_BASE}/api/analysis/full/${code}`;
            if (forceRefresh) {
                url += '?refresh=true';
                console.log(`🔄 강제 갱신 요청: ${code}`);
            }
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('분석 로드 중 오류:', error);
            return { success: false, message: error.message };
        }
    },

    // 분봉 차트 데이터 로드
    async fetchMinuteChart(code) {
        try {
            const response = await fetch(`${API_BASE}/api/chart/minute/${code}`);
            return await response.json();
        } catch (error) {
            console.error('차트 로드 중 오류:', error);
            return { success: false, message: error.message };
        }
    },

    // 감성 분석 (단일 종목)
    async fetchSentiment(code) {
        try {
            const response = await fetch(`${API_BASE}/api/analysis/sentiment/${code}`);
            return await response.json();
        } catch (error) {
            console.error('감성 분석 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 관심종목 가격 로드
    async fetchWatchlistPrices() {
        try {
            const response = await fetch(`${API_BASE}/api/watchlist/prices`);
            return await response.json();
        } catch (error) {
            console.error('관심종목 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 관심종목 추가
    async addToWatchlist(code) {
        try {
            const response = await fetch(`${API_BASE}/api/watchlist/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            return await response.json();
        } catch (error) {
            console.error('추가 오류:', error);
            return { success: false, message: error.message };
        }
    },

    // 관심종목 삭제
    async removeFromWatchlist(code) {
        try {
            const response = await fetch(`${API_BASE}/api/watchlist/remove`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            return await response.json();
        } catch (error) {
            console.error('삭제 오류:', error);
            return { success: false, message: error.message };
        }
    }
};
