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
    // 설정 로드
    async fetchConfig() {
        try {
            const response = await fetch(`${API_BASE}/api/config`);
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    window.SENTIMENT_REFRESH_MINUTES = result.data.sentiment_refresh_minutes;
                    window.SENTIMENT_UPDATE_DELAY_SECONDS = result.data.sentiment_update_delay_seconds;

                    // 갱신 주기 계산 (밀리초)
                    window.SENTIMENT_REFRESH_INTERVAL = window.SENTIMENT_REFRESH_MINUTES * 60 * 1000;
                    Logger.info('API', `설정 로드 완료: 감성 갱신 주기 ${window.SENTIMENT_REFRESH_MINUTES}분, 카드 갱신 간격 ${window.SENTIMENT_UPDATE_DELAY_SECONDS}초`);
                }
                return result;
            }
            return { success: false, message: '설정 로드 실패' };
        } catch (error) {
            Logger.error('API', '설정 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 계좌 요약 정보 로드
    async fetchAccountSummary() {
        try {
            const response = await fetch(`${API_BASE}/api/account/summary`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '계좌 요약 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 보유 종목 리스트 로드
    async fetchHoldings() {
        try {
            const response = await fetch(`${API_BASE}/api/account/balance`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '보유 종목 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 글로벌 마켓 데이터 조회 (상세 모달용)
    async fetchGlobalMarket() {
        try {
            const response = await fetch(`${API_BASE}/api/market/global`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '글로벌 마켓 데이터 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 시장 지수 로드
    async fetchMarketIndices() {
        try {
            const response = await fetch(`${API_BASE}/api/market/indices`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '시장 지수 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 시장 세션 정보 로드
    async fetchMarketSession() {
        try {
            const response = await fetch(`${API_BASE}/api/market/session`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '시장 세션 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // L1 캐시 (메모리) - 10분
    memoryCache: {},
    MEMORY_TTL: 10 * 60 * 1000,

    // L2 캐시 (LocalStorage) - 30분
    STORAGE_KEY_PREFIX: 'stock_analysis_',
    STORAGE_TTL: 30 * 60 * 1000,

    // 요청 큐 시스템 (동시 요청 제한)
    requestQueue: [],
    activeRequests: 0,
    MAX_CONCURRENT_REQUESTS: 2, // 동시 요청 최대 2개로 제한

    // 스트리밍 요청 관리
    activeStreamingRequests: new Map(), // code -> { controller, timestamp }
    streamingQueue: [],

    // 캐시 직접 확인 함수 (API 호출 없이, 큐 대기 없이 즉시 반환)
    getCachedAnalysis(code, lightweight = false) {
        const now = Date.now();
        const cacheKey = lightweight ? `${code}_light` : code;

        // 1. L1 캐시 확인 (메모리)
        if (this.memoryCache[cacheKey]) {
            const cached = this.memoryCache[cacheKey];
            if (now - cached.timestamp < this.MEMORY_TTL) {
                Logger.debug('API', `L1 캐시 히트 (메모리): ${code}`);
                return {
                    success: true,
                    data: cached.data,
                    source: 'memory'
                };
            }
        }

        // 2. L2 캐시 확인 (LocalStorage)
        try {
            const storageKey = `${this.STORAGE_KEY_PREFIX}${cacheKey}`;
            const stored = localStorage.getItem(storageKey);
            if (stored) {
                const parsed = JSON.parse(stored);
                if (now - parsed.timestamp < this.STORAGE_TTL) {
                    Logger.debug('API', `L2 캐시 히트 (스토리지): ${code}`);
                    // L1 캐시 복구
                    this.memoryCache[cacheKey] = { data: parsed.data, timestamp: parsed.timestamp };
                    return {
                        success: true,
                        data: parsed.data,
                        source: 'localStorage'
                    };
                }
            }
        } catch (e) {
            Logger.warn('API', 'LocalStorage 읽기 실패:', e);
        }

        // 캐시 미스
        return null;
    },

    // 요청 큐 처리 함수
    processQueue() {
        // 대기 중인 요청이 있고 여유가 있으면 처리
        while (this.requestQueue.length > 0 && this.activeRequests < this.MAX_CONCURRENT_REQUESTS) {
            const request = this.requestQueue.shift();
            this.activeRequests++;

            this._executeAnalysisRequest(request)
                .then(result => {
                    request.resolve(result);
                })
                .catch(error => {
                    request.reject(error);
                })
                .finally(() => {
                    this.activeRequests--;
                    this.processQueue(); // 다음 요청 처리
                });
        }
    },

    // 종합 분석 데이터 로드 (큐 시스템 적용)
    async fetchFullAnalysis(code, forceRefresh = false, lightweight = false, highPriority = false, abortController = null) {
        return new Promise((resolve, reject) => {
            const request = {
                code,
                forceRefresh,
                lightweight,
                highPriority,
                abortController,
                resolve,
                reject,
                timestamp: Date.now()
            };

            if (highPriority) {
                // 우선순위 높은 요청은 큐 앞에 추가
                this.requestQueue.unshift(request);
                Logger.debug('API', `우선 요청 추가: ${code}`);
            } else {
                // 일반 요청은 큐 뒤에 추가
                this.requestQueue.push(request);
            }

            this.processQueue();
        });
    },

    // 수동으로 캐시 설정 (스트리밍 완료 후 저장용)
    setManualCache(code, data) {
        const now = Date.now();
        // L1 저장
        this.memoryCache[code] = { data, timestamp: now };

        // L2 저장
        try {
            const storageKey = `${this.STORAGE_KEY_PREFIX}${code}`;
            localStorage.setItem(storageKey, JSON.stringify({ data, timestamp: now }));
            Logger.debug('API', `수동 캐시 저장 완료: ${code}`);
        } catch (e) {
            Logger.warn('API', 'L2 Save Error:', e);
        }
    },

    // 실제 분석 요청 실행 (내부 함수)
    async _executeAnalysisRequest(request) {
        // 수급 정보 요청인 경우 별도 처리
        if (request.type === 'supply') {
            try {
                const response = await fetch(`${API_BASE}/api/analysis/supply-demand/${request.code}`);
                return await response.json();
            } catch (error) {
                Logger.error('API', '수급 정보 로드 실패:', error);
                return { success: false, message: error.message };
            }
        }

        const { code, forceRefresh, lightweight } = request;
        const startTime = performance.now();
        const now = Date.now();

        // 캐시 키에 lightweight 여부 포함
        const cacheKey = lightweight ? `${code}_light` : code;

        // 1. 캐시 확인 (강제 갱신이 아닐 경우)
        if (!forceRefresh) {
            // L1 확인 (메모리)
            if (this.memoryCache[cacheKey]) {
                const { data, timestamp } = this.memoryCache[cacheKey];
                if (now - timestamp < this.MEMORY_TTL) {
                    Logger.debug('API', `L1 Cache Hit (Memory): ${code} [${lightweight ? 'light' : 'full'}]`);
                    return data;
                } else {
                    delete this.memoryCache[cacheKey]; // 만료됨
                }
            }

            // L2 확인 (LocalStorage)
            try {
                const storageKey = `${this.STORAGE_KEY_PREFIX}${cacheKey}`;
                const stored = localStorage.getItem(storageKey);
                if (stored) {
                    const { data, timestamp } = JSON.parse(stored);
                    if (now - timestamp < this.STORAGE_TTL) {
                        Logger.debug('API', `L2 Cache Hit (Storage): ${code} [${lightweight ? 'light' : 'full'}]`);
                        // L1으로 승격
                        this.memoryCache[cacheKey] = { data, timestamp: now };
                        return data;
                    } else {
                        localStorage.removeItem(storageKey); // 만료됨
                    }
                }
            } catch (e) {
                Logger.warn('API', 'L2 Cache Error:', e);
            }
        }

        try {
            let url = `${API_BASE}/api/analysis/full/${code}`;
            const params = [];
            if (forceRefresh) {
                params.push('refresh=true');
            }
            if (lightweight) {
                params.push('lightweight=true');
            }
            if (params.length > 0) {
                url += '?' + params.join('&');
            }

            if (forceRefresh) {
                Logger.info('API', `강제 갱신 요청: ${code}`);
            }
            if (lightweight) {
                Logger.debug('API', `경량 모드 요청: ${code}`);
            }

            // AbortController 처리 (외부에서 전달된 것 우선 사용)
            const controller = request.abortController || new AbortController();
            const timeoutId = request.abortController ? null : setTimeout(() => controller.abort(), 90000);

            let response;
            try {
                response = await fetch(url, { signal: controller.signal });

                if (timeoutId) {
                    clearTimeout(timeoutId);
                }

                if (!response.ok) {
                    Logger.error('API', `HTTP Error: ${response.status}`);
                    return {
                        success: false,
                        message: `서버 오류 (${response.status}). 잠시 후 다시 시도해주세요.`
                    };
                }
            } catch (error) {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }

                // AbortError는 정상적인 취소이므로 에러로 처리하지 않음
                if (error.name === 'AbortError') {
                    Logger.debug('API', `요청 취소됨: ${code}`);
                    return { success: false, message: '요청이 취소되었습니다' };
                }

                throw error; // 다른 에러는 외부 catch로 전달
            }

            const data = await response.json();

            const elapsed = (performance.now() - startTime).toFixed(0);

            // 캐싱 정보 확인 및 출력
            if (data.success && data.data) {
                const newsCache = data.data.news_analysis?._cache_info;
                const outlookCache = data.data.outlook?._cache_info;

                if (newsCache) {
                    const cacheStatus = newsCache.cached ? `✅ Server Cache HIT (${newsCache.age_seconds.toFixed(1)}s old)` : `❌ Server Cache MISS (${newsCache.reason})`;
                    Logger.debug('API', `뉴스 분석: ${cacheStatus}`);
                }

                if (outlookCache) {
                    const cacheStatus = outlookCache.cached ? `✅ Server Cache HIT (${outlookCache.age_seconds.toFixed(1)}s old)` : `❌ Server Cache MISS (${outlookCache.reason})`;
                    Logger.debug('API', `AI 전망: ${cacheStatus}`);
                }

                // 클라이언트 캐시에 저장 (lightweight 여부 구분)
                // L1 저장
                this.memoryCache[cacheKey] = { data, timestamp: now };

                // L2 저장
                try {
                    const storageKey = `${this.STORAGE_KEY_PREFIX}${cacheKey}`;
                    localStorage.setItem(storageKey, JSON.stringify({ data, timestamp: now }));
                } catch (e) {
                    Logger.warn('API', 'L2 Save Error:', e);
                }
            }

            Logger.info('API', `분석 로드 완료: ${code} (${elapsed}ms)`);

            return data;
        } catch (error) {
            Logger.error('API', '분석 로드 중 오류:', error);
            return { success: false, message: error.message };
        }
    },

    // 분봉 차트 데이터 로드
    async fetchMinuteChart(code) {
        try {
            const response = await fetch(`${API_BASE}/api/chart/minute/${code}`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '차트 로드 중 오류:', error);
            return { success: false, message: error.message };
        }
    },

    // 감성 분석 (단일 종목)
    async fetchSentiment(code) {
        try {
            const response = await fetch(`${API_BASE}/api/analysis/sentiment/${code}`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '감성 분석 로드 실패:', error);
            return { success: false, message: error.message };
        }
    },

    // 수급 정보 (단일 종목)
    // 수급 정보 (단일 종목) - 큐 시스템 적용
    async fetchSupplyDemand(code) {
        return new Promise((resolve, reject) => {
            const request = {
                code,
                type: 'supply',
                resolve,
                reject,
                timestamp: Date.now()
            };
            this.requestQueue.push(request);
            this.processQueue();
        });
    },

    // 관심종목 가격 로드
    async fetchWatchlistPrices() {
        try {
            const response = await fetch(`${API_BASE}/api/watchlist/prices`);
            return await response.json();
        } catch (error) {
            Logger.error('API', '관심종목 로드 실패:', error);
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
            Logger.error('API', '추가 오류:', error);
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
            Logger.error('API', '삭제 오류:', error);
            return { success: false, message: error.message };
        }
    },
    // 스트리밍 분석 (Server-Sent Events)  ← 여기부터 새로 추가
    async fetchFullAnalysisStreaming(code, onProgress, onComplete, onError, highPriority = false) {
        try {
            // 우선순위 처리: 기존 요청 중단
            if (highPriority) {
                Logger.debug('API', `우선순위 스트리밍 요청: ${code}, 기존 요청 취소`);
                // 다른 모든 스트리밍 요청 중단
                for (const [existingCode, info] of this.activeStreamingRequests.entries()) {
                    if (existingCode !== code) {
                        Logger.debug('API', `  중단: ${existingCode}`);
                        info.controller.abort();
                        this.activeStreamingRequests.delete(existingCode);
                    }
                }
            }

            // AbortController 생성 및 등록
            const controller = new AbortController();
            this.activeStreamingRequests.set(code, {
                controller,
                timestamp: Date.now()
            });

            const response = await fetch(`${API_BASE}/api/analysis/stream/${code}`, {
                signal: controller.signal
            });

            if (!response.ok) {
                this.activeStreamingRequests.delete(code);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value);
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    // 빈 줄 무시
                    if (!line.trim()) continue;

                    // SSE 형식: "data: {...}" 에서 "data: " 제거
                    if (line.startsWith('data: ')) {
                        const jsonStr = line.substring(6); // "data: " 제거
                        const data = JSON.parse(jsonStr);

                        if (data.type === 'basic') {
                            onProgress('basic', {
                                price: data.data.price,
                                supply: data.data.supply
                            });
                        } else if (data.type === 'technical') {
                            onProgress('technical', data.data);
                        } else if (data.type === 'news') {
                            onProgress('news', data.data);
                        } else if (data.type === 'outlook') {
                            onProgress('outlook', data.data);
                        } else if (data.type === 'complete') {
                            onComplete();
                            return;
                        } else if (data.type === 'error') {
                            onError(data.message);
                            return;
                        }
                    }
                }
            }

            // 완료 시 등록 해제
            this.activeStreamingRequests.delete(code);
        } catch (error) {
            // 중단된 요청은 에러로 처리하지 않음
            if (error.name === 'AbortError') {
                Logger.debug('API', `스트리밍 요청 취소됨: ${code}`);
                return;
            }
            this.activeStreamingRequests.delete(code);
            onError(error.message);
        }
    },

    // 글로벌 마켓 데이터 스트리밍 조회
    async fetchGlobalMarketStreaming(onProgress, onComplete, onError) {
        try {
            const response = await fetch(`${API_BASE}/api/market/global/stream`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // 마지막 불완전한 라인은 버퍼에 유지

                for (const line of lines) {
                    if (!line.trim()) continue;
                    if (line.startsWith('data: ')) {
                        try {
                            const jsonStr = line.substring(6);
                            const data = JSON.parse(jsonStr);

                            if (data.type === 'error') {
                                onError(data.message);
                                return;
                            } else if (data.type === 'complete') {
                                onComplete();
                                return;
                            } else {
                                onProgress(data.type, data.data);
                            }
                        } catch (e) {
                            Logger.error('API', 'JSON Parse Error:', e);
                        }
                    }
                }
            }
        } catch (error) {
            onError(error.message);
        }
    }
};
