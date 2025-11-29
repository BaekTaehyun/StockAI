/**
 * api.js - 서버 API 통신 모듈
 * ================================================================
 * 백엔드 Flask 서버와의 모든 HTTP 통신을 담당합니다.
 * 
 * 주요 기능:
 * - 계좌 정보 조회
 * - 보유 종목 조회
 * - 시장 지수 조회
 * - 종합 분석 데이터 조회 (AI 포함)
 * - 관심종목 관리
 * 
 * 캐싱 전략:
 * - L1 캐시 (메모리): 10분 TTL
 * - L2 캐시 (LocalStorage): 60분 TTL
 * - 서버 캐시와 함께 3단계 캐싱 시스템 구현
 * ================================================================
 */


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

    // L1 캐시 (메모리) - 10분
    memoryCache: {},
    MEMORY_TTL: 10 * 60 * 1000,

    // L2 캐시 (LocalStorage) - 60분
    STORAGE_KEY_PREFIX: 'stock_analysis_',
    STORAGE_TTL: 60 * 60 * 1000,

    // 종합 분석 데이터 로드 (강제 갱신 지원)
    async fetchFullAnalysis(code, forceRefresh = false) {
        const startTime = performance.now();
        const now = Date.now();

        // 1. 캐시 확인 (강제 갱신이 아닐 경우)
        if (!forceRefresh) {
            // L1 확인 (메모리)
            if (this.memoryCache[code]) {
                const { data, timestamp } = this.memoryCache[code];
                if (now - timestamp < this.MEMORY_TTL) {
                    console.log(`🚀 L1 Cache Hit (Memory): ${code}`);
                    return data;
                } else {
                    delete this.memoryCache[code]; // 만료됨
                }
            }

            // L2 확인 (LocalStorage)
            try {
                const storageKey = `${this.STORAGE_KEY_PREFIX}${code}`;
                const stored = localStorage.getItem(storageKey);
                if (stored) {
                    const { data, timestamp } = JSON.parse(stored);
                    if (now - timestamp < this.STORAGE_TTL) {
                        console.log(`💾 L2 Cache Hit (Storage): ${code}`);
                        // L1으로 승격
                        this.memoryCache[code] = { data, timestamp: now };
                        return data;
                    } else {
                        localStorage.removeItem(storageKey); // 만료됨
                    }
                }
            } catch (e) {
                console.warn('L2 Cache Error:', e);
            }
        }

        try {
            let url = `${API_BASE}/api/analysis/full/${code}`;
            if (forceRefresh) {
                url += '?refresh=true';
                console.log(`🔄 강제 갱신 요청: ${code}`);
            }
            const response = await fetch(url);
            const data = await response.json();

            const elapsed = (performance.now() - startTime).toFixed(0);

            // 캐싱 정보 확인 및 출력
            if (data.success && data.data) {
                const newsCache = data.data.news_analysis?._cache_info;
                const outlookCache = data.data.outlook?._cache_info;

                if (newsCache) {
                    const cacheStatus = newsCache.cached ? `✅ Server Cache HIT (${newsCache.age_seconds.toFixed(1)}s old)` : `❌ Server Cache MISS (${newsCache.reason})`;
                    console.log(`📰 뉴스 분석: ${cacheStatus}`);
                }

                if (outlookCache) {
                    const cacheStatus = outlookCache.cached ? `✅ Server Cache HIT (${outlookCache.age_seconds.toFixed(1)}s old)` : `❌ Server Cache MISS (${outlookCache.reason})`;
                    console.log(`🔮 AI 전망: ${cacheStatus}`);
                }

                // 클라이언트 캐시에 저장
                // L1 저장
                this.memoryCache[code] = { data, timestamp: now };

                // L2 저장
                try {
                    const storageKey = `${this.STORAGE_KEY_PREFIX}${code}`;
                    localStorage.setItem(storageKey, JSON.stringify({ data, timestamp: now }));
                } catch (e) {
                    console.warn('L2 Save Error:', e);
                }
            }

            console.log(`📊 분석 로드 완료: ${code} (${elapsed}ms)`);

            return data;
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
