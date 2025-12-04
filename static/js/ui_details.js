/**
 * ui_details.js - 상세 정보 모달 렌더링 모듈
 * ================================================================
 * 종목 클릭 시 표시되는 상세 분석 모달을 관리합니다.
 * 
 * 주요 기능:
 * - 계좌 요약 정보 업데이트
 * - 종합 분석 탭 렌더링 (AI 투자의견, 수급, 뉴스)
 * - 수급 현황 탭 렌더링 (외국인/기관 매매)
 * - 뉴스 분석 탭 렌더링
 * - 탭 전환 기능
 * 
 * 탭 구성:
 * - 종합: 주가정보, AI투자의견, 수급요약, 뉴스요약
 * - 수급: 상세 수급 데이터 및 트렌드
 * - 뉴스: 뉴스 감성 분석 및 등락 원인
 * - 기술적분석: 차트 및 기술적 지표 (charts.js)
 * ================================================================
 */

window.UI = window.UI || {};

Object.assign(window.UI, {
    // 현재 진행 중인 분석 요청 컨트롤러
    currentAnalysisController: null,

    // 계좌 요약 업데이트
    updateAccountSummary(data) {
        if (!data) {
            console.warn('⚠️ [계좌요약 UI] 데이터가 없습니다');
            return;
        }

        console.log('🎨 [계좌요약 UI] DOM 업데이트 시작:', data);

        // 총 매입금액
        const totalPurchaseEl = document.getElementById('totalPurchase');
        if (totalPurchaseEl) {
            totalPurchaseEl.textContent = formatCurrency(data.total_purchase);
            console.log('  ✓ 총 매입금액:', totalPurchaseEl.textContent);
        }

        // 총 평가금액
        const totalEvalEl = document.getElementById('totalEval');
        if (totalEvalEl) {
            totalEvalEl.textContent = formatCurrency(data.total_eval);
            console.log('  ✓ 총 평가금액:', totalEvalEl.textContent);
        }

        // 총 평가손익
        const plElement = document.getElementById('totalPL');
        const rateElement = document.getElementById('profitRate');
        const plCard = plElement ? plElement.closest('.summary-card') : null;

        if (plElement && rateElement) {
            plElement.textContent = formatCurrency(data.total_pl);
            rateElement.textContent = formatPercent(data.profit_rate);
            console.log('  ✓ 총 평가손익:', plElement.textContent, rateElement.textContent);

            // 수익/손실에 따라 클래스 및 역동적인 스타일 적용
            if (plCard) {
                plCard.classList.remove('positive', 'negative');
                const isProfit = data.total_pl >= 0;

                if (isProfit) {
                    plCard.classList.add('positive');
                } else {
                    plCard.classList.add('negative');
                }

                // 카드에 적용된 역동적인 스타일과 동일하게 배경색과 테두리 적용
                const bgColor = isProfit ? 'rgba(255, 100, 100, 0.05)' : 'rgba(100, 100, 255, 0.05)';
                const borderColor = isProfit ? '#e53e3e' : '#3b82f6';
                const textColor = isProfit ? '#e53e3e' : '#3b82f6';

                plCard.style.background = bgColor;
                plCard.style.borderLeft = `4px solid ${borderColor}`;

                // 금액과 수익률 텍스트 색상 적용
                plElement.style.color = textColor;
                rateElement.style.color = textColor;
            }
        }

        // 보유 종목 수
        const holdingsCountEl = document.getElementById('holdingsCount');
        if (holdingsCountEl) {
            holdingsCountEl.textContent = `${data.holdings_count}개`;
            console.log('  ✓ 보유 종목:', holdingsCountEl.textContent);
        }

        console.log('✅ [계좌요약 UI] DOM 업데이트 완료');
    },

    // 종합 탭 렌더링
    renderOverview(data) {
        console.log('renderOverview called with:', data);

        if (!data) {
            console.error('Data is null or undefined');
            return;
        }

        const { stock_info, supply_demand, news_analysis, outlook } = data;

        // 데이터 유효성 검사
        if (!stock_info) console.warn('stock_info is missing');
        if (!supply_demand) console.warn('supply_demand is missing');
        if (!news_analysis) console.warn('news_analysis is missing');
        if (!outlook) console.warn('outlook is missing');

        const safeOutlook = outlook || { recommendation: '중립', confidence: 0, trading_scenario: '', reasoning: '' };
        const safeStockInfo = stock_info || { current_price: 0, change: 0, change_rate: 0 };
        const safeSupply = supply_demand || { foreign_net: 0, institution_net: 0, trend: '' };
        const safeNews = news_analysis || { sentiment: '중립', reason: '' };

        const recommendationClass =
            safeOutlook.recommendation === '매수' ? 'buy' :
                safeOutlook.recommendation === '매도' ? 'sell' : 'neutral';

        const changeRate = parseFloat(safeStockInfo.change_rate) || 0;
        const isUp = changeRate >= 0;
        const priceColor = isUp ? '#e53e3e' : '#3b82f6';

        // 수급 트렌드 로직 (카드와 동일하게)
        const fNet = safeSupply.foreign_net;
        const iNet = safeSupply.institution_net;
        let trendBadge = '';

        if (fNet > 0 && iNet > 0) {
            trendBadge = '<span class="badge-supply buy">쌍끌이 매수 🚀</span>';
        } else if (fNet < 0 && iNet < 0) {
            trendBadge = '<span class="badge-supply sell">양매도 📉</span>';
        } else if (fNet > 0 && iNet < 0) {
            trendBadge = `<div style="display: flex; flex-direction: column; gap: 4px;">
                <span class="badge-supply buy" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">외인 매수</span>
                <span class="badge-supply sell" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">기관 매도</span>
            </div>`;
        } else if (fNet < 0 && iNet > 0) {
            trendBadge = `<div style="display: flex; flex-direction: column; gap: 4px;">
                <span class="badge-supply sell" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">외인 매도</span>
                <span class="badge-supply buy" style="font-size: 0.85em; padding: 2px 8px; width: fit-content;">기관 매수</span>
            </div>`;
        } else if (fNet > 0) {
            trendBadge = '<span class="badge-supply buy">외인 매수중 📈</span>';
        } else if (fNet < 0) {
            trendBadge = '<span class="badge-supply sell">외인 매도중 📉</span>';
        } else if (iNet > 0) {
            trendBadge = '<span class="badge-supply buy">기관 매수중 🏢</span>';
        } else if (iNet < 0) {
            trendBadge = '<span class="badge-supply sell">기관 매도중 📉</span>';
        } else {
            trendBadge = '<span class="badge-supply neutral">수급 보합</span>';
        }

        try {
            const html = `
                <div id="section-price" class="analysis-section">
                    <h3>주가 정보</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">현재가</span>
                            <span class="value" style="color: ${priceColor};">${formatCurrency(safeStockInfo.current_price)}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">전일대비</span>
                            <span class="value ${changeRate >= 0 ? 'positive' : 'negative'}">
                                ${formatCurrency(safeStockInfo.change)} (${safeStockInfo.change_rate}%)
                            </span>
                        </div>
                    </div>
                </div>

                <div id="section-ai" class="analysis-section">
                    <h3>AI 투자 의견</h3>
                    <div class="outlook-card ${recommendationClass}">
                        <div class="outlook-header">
                            <span class="recommendation">${safeOutlook.recommendation}</span>
                            <span class="confidence">신뢰도 ${safeOutlook.confidence}%</span>
                        </div>
                        
                        <!-- [NEW] 핵심 논리 (3줄 요약) -->
                        <div class="key-logic" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                             <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">핵심 논리</h4>
                             <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6; white-space: pre-line;">${formatAIText(safeOutlook.key_logic || '논리 정보 없음')}</div>
                        </div>

                        <div class="trading-scenario" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                             <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">매매 시나리오</h4>
                             <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6; white-space: pre-line;">${formatAIText(safeOutlook.trading_scenario || '시나리오 정보 없음')}</div>
                        </div>
                        
                        <!-- [NEW] 상세 분석 (Reasoning 대체) -->
                        <div class="detailed-analysis" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                             <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">상세 분석</h4>
                             <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6; white-space: pre-line;">${formatAIText(safeOutlook.detailed_analysis || safeOutlook.reasoning || '분석 내용 없음')}</div>
                        </div>
                    </div>
                </div>

                <div id="section-supply" class="analysis-section">
                    <h3>수급 현황</h3>
                    <div class="supply-summary">
                        <div class="supply-item ${safeSupply.foreign_net >= 0 ? 'positive' : 'negative'}">
                            <span class="label">외국인</span>
                            <span class="value">${formatNumber(safeSupply.foreign_net)}주</span>
                        </div>
                        <div class="supply-item ${safeSupply.institution_net >= 0 ? 'positive' : 'negative'}">
                            <span class="label">기관</span>
                            <span class="value">${formatNumber(safeSupply.institution_net)}주</span>
                        </div>
                        <div class="trend">${trendBadge}</div>
                    </div>
                </div>

                <div id="section-news" class="analysis-section">
                    <h3>뉴스 요약</h3>
                    <div class="news-summary">
                        <div class="sentiment ${safeNews.sentiment}">${safeNews.sentiment}</div>
                        <div class="news-box">
                            ${formatNewsText(safeNews.reason)}
                        </div>
                    </div>
                </div>
            `;

            const contentEl = document.getElementById('overviewContent');
            if (contentEl) {
                contentEl.innerHTML = html;
                console.log('overviewContent updated successfully');
            } else {
                console.error('overviewContent element not found');
            }
        } catch (e) {
            console.error('Error in renderOverview HTML generation:', e);
        }
    },

    // 수급 탭 렌더링
    renderSupplyDemand(data) {
        const fNet = data.foreign_net;
        const iNet = data.institution_net;
        let trendHtml = `<p>${data.trend}</p>`;

        if (fNet > 0 && iNet > 0) {
            trendHtml = `
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
                    <span class="badge-supply buy" style="font-size: 1.2rem; padding: 0.5rem 1rem;">쌍끌이 매수 🚀</span>
                    <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">외국인과 기관이 동시에 매수하고 있습니다</p>
                </div>`;
        } else if (fNet < 0 && iNet < 0) {
            trendHtml = `
                <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
                    <span class="badge-supply sell" style="font-size: 1.2rem; padding: 0.5rem 1rem;">양매도 📉</span>
                    <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">외국인과 기관이 동시에 매도하고 있습니다</p>
                </div>`;
        }

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
                    ${trendHtml}
                </div>
            </div>
        `;

        document.getElementById('supplyContent').innerHTML = html;
    },
    renderNews(data) {
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
    },

    // 종목 상세 모달 열기 (ui_cards.js에서 호출됨)
    openStockModal(stock) {
        const modal = document.getElementById('stockModal');
        const title = document.getElementById('modalTitle');
        const loading = document.getElementById('loadingSpinner');
        const tabs = document.getElementById('analysisTabs');
        const body = document.getElementById('modalBody');

        // 초기화
        title.textContent = `${stock.stk_nm} (${stock.stk_cd})`;
        modal.style.display = 'flex';

        // 전역 로딩 스피너 숨김 (존재할 경우)
        if (loading) loading.style.display = 'none';

        // 탭과 본문 즉시 표시
        tabs.style.display = 'flex';
        body.style.display = 'block';

        // 초기 데이터(주가 정보) 렌더링 및 로딩 상태 표시
        // 캐시 확인
        const cached = API.getCachedAnalysis(stock.stk_cd);
        if (cached && cached.success) {
            console.log('💾 캐시 히트! 즉시 표시 (openStockModal):', stock.stk_cd);

            // 전역 로딩 스피너 숨김
            if (loading) loading.style.display = 'none';
            tabs.style.display = 'flex';
            body.style.display = 'block';

            this.renderFullAnalysis(cached.data);
            this.switchTab('overview');
        } else {
            // 캐시 없음: 로딩 상태 표시 후 데이터 로드
            this.renderInitialOverview(stock);

            // 기본 탭 활성화
            this.switchTab('overview');

            // 데이터 로드
            this.loadStockAnalysis(stock.stk_cd);
        }
    },

    // 초기 개요 렌더링 (주가 정보 즉시 표시 + 로딩 인디케이터)
    renderInitialOverview(stock) {
        const currentPrice = parseInt(stock.price || stock.cur_prc || 0);
        // 포맷팅
        const formattedPrice = formatCurrency(currentPrice);

        const html = `
            <div id="section-price" class="analysis-section">
                <h3>주가 정보</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">현재가</span>
                        <span class="value" style="color: var(--text-primary);">${formattedPrice}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">전일대비</span>
                        <span class="value">
                            <span style="font-size: 0.9rem; color: var(--text-secondary);">데이터 로딩중...</span>
                        </span>
                    </div>
                </div>
            </div>

            <div id="section-ai" class="analysis-section">
                <h3>AI 투자 의견</h3>
                <div class="outlook-card neutral" style="min-height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px; margin-bottom: 0.5rem;"></div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">분석 중...</p>
                </div>
            </div>


            <div id="section-supply" class="analysis-section">
                <h3>수급 현황</h3>
                <div class="supply-summary" style="display: flex; justify-content: center; padding: 1rem;">
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">분석 중...</span>
                </div>
            </div>

            <div id="section-news" class="analysis-section">
                <h3>뉴스 요약</h3>
                <div class="news-summary" style="display: flex; justify-content: center; padding: 1rem;">
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">분석 중...</span>
                </div>
            </div>
        `;

        document.getElementById('overviewContent').innerHTML = html;

        // 다른 탭들도 로딩 상태로 초기화
        document.getElementById('supplyContent').innerHTML = '<div style="padding: 3rem; text-align: center; color: var(--text-secondary);">데이터를 불러오는 중입니다...</div>';
        document.getElementById('newsContent').innerHTML = '<div style="padding: 3rem; text-align: center; color: var(--text-secondary);">데이터를 불러오는 중입니다...</div>';
    },

    // 전체 분석 데이터 렌더링 (캐시 히트 시 사용)
    renderFullAnalysis(data) {
        const code = data.stock_info?.code || data.code; // 코드 확인

        // 기본 정보
        if (data.stock_info && data.supply_demand) {
            this.renderBasicInfoOnly(
                {
                    price: data.stock_info.current_price,
                    change: data.stock_info.change,
                    rate: data.stock_info.change_rate
                },
                data.supply_demand
            );
        }

        // 전체 종합 탭
        this.renderOverview(data);

        // 수급 탭
        if (data.supply_demand) {
            this.renderSupplyDemand(data.supply_demand);
        }

        // 뉴스 탭
        if (data.news_analysis) {
            this.renderNews(data.news_analysis);
        }

        // 기술적 분석 탭
        if (data.technical && typeof Charts !== 'undefined' && Charts.renderTechnical) {
            Charts.renderTechnical(data.technical, data.stock_info, data.fundamental_data, data.bollinger);
        }

        // 리본 캐시 동기화
        if (window.updateSentimentFromAnalysis && data.outlook && data.news_analysis && code) {
            window.updateSentimentFromAnalysis(code, {
                outlook: data.outlook,
                news_analysis: data.news_analysis,
                supply_demand: data.supply_demand
            });
        }
    },

    // 종목 상세 분석 데이터 로드
    async loadStockAnalysis(code) {
        const loading = document.getElementById('loadingSpinner');
        const tabs = document.getElementById('analysisTabs');
        const body = document.getElementById('modalBody');

        try {
            // 이전 요청 취소
            if (this.currentAnalysisController) {
                this.currentAnalysisController.abort();
                console.log('⏹️ 이전 분석 요청 취소');
            }

            // 새 AbortController 생성
            this.currentAnalysisController = new AbortController();

            // 1. 먼저 캐시 확인 (빠른 응답)
            const cached = API.getCachedAnalysis(code);

            if (cached && cached.success) {
                console.log('💾 캐시 히트! (loadStockAnalysis):', code);
                // 캐시된 데이터로 전체 UI 한 번에 업데이트
                this.renderFullAnalysis(cached.data);

                // 로딩 상태 해제
                if (loading) loading.style.display = 'none';
                tabs.style.display = 'flex';
                body.style.display = 'block';
                this.switchTab('overview');

                return; // 캐시로 처리 완료, 스트리밍 필요 없음
            }

            // 2. 캐시 미스 - 스트리밍 방식으로 데이터 수신
            console.log('🌐 캐시 미스, 스트리밍 시작:', code);

            // 2-1. 경량 캐시라도 있으면 먼저 표시 (사용자 경험 향상)
            const lightCache = API.getCachedAnalysis(code, true);
            if (lightCache && lightCache.success && lightCache.data && lightCache.data.stock_info) {
                console.log('⚡ 경량 캐시 발견, 초기 데이터로 표시:', code);
                this.renderBasicInfoOnly(
                    {
                        price: lightCache.data.stock_info.current_price,
                        change: lightCache.data.stock_info.change,
                        rate: lightCache.data.stock_info.change_rate
                    },
                    lightCache.data.supply_demand
                );
            } else {
                if (lightCache && lightCache.success && !lightCache.data.stock_info) {
                    console.warn('⚠️ 경량 캐시 데이터 불완전 (stock_info 누락):', lightCache);
                }
            }

            let allData = {}; // 전체 데이터 누적

            API.fetchFullAnalysisStreaming(
                code,
                // onProgress: 단계별 데이터 수신 시 호출됨
                (type, data) => {
                    console.log(`📥 [${type}] 데이터 수신`, data);

                    if (type === 'basic') {
                        // 1단계: 기본 정보 (주가 + 수급) - 즉시 표시
                        allData.price = data.price;
                        allData.supply = data.supply;

                        // 즉시 종합 탭에 기본 정보 렌더링
                        this.renderBasicInfoOnly(data.price, data.supply);
                        // market_impact는 별도 이벤트로 수신됨
                    }
                    else if (type === 'market_impact') {
                        // 1.5단계: 시장 영향 분석
                        allData.market_impact = data;
                        this.renderMarketImpact(data);
                    }
                    else if (type === 'news') {
                        // 3단계: 뉴스 분석
                        allData.news_analysis = data;
                        this.renderNews(data);  // 뉴스 탭 업데이트
                        this.updateOverviewWithNews(data);  // 종합 탭 뉴스 섹션 업데이트
                    }
                    else if (type === 'outlook') {
                        // 4단계: AI 전망
                        allData.outlook = data;
                        this.updateOverviewWithOutlook(data);
                    }
                    else if (type === 'technical') {
                        // 2단계: 기술적 지표 & 펀더멘털
                        // data structure: { indicators: {...}, fundamental: {...} }
                        // 하위 호환성: data.indicators가 없으면 data 자체가 indicators임
                        const indicators = data.indicators || data;
                        const fundamental = data.fundamental || {};

                        allData.technical = indicators;
                        allData.fundamental_data = fundamental;
                        allData.bollinger = data.bollinger;

                        if (typeof Charts !== 'undefined' && Charts.renderTechnical) {
                            // stockInfo 구성 (allData.price는 {name, code, price, change, rate} 형태)
                            const stockInfo = {
                                current_price: allData.price ? allData.price.price : 0,
                                change: allData.price ? allData.price.change : 0,
                                change_rate: allData.price ? allData.price.rate : 0
                            };

                            Charts.renderTechnical(indicators, stockInfo, fundamental, data.bollinger);
                        }
                    }
                },
                // onComplete: 모든 단계 완료
                (completedData) => {
                    console.log('✅ 스트리밍 분석 완료');

                    // 수급 탭 렌더링
                    if (allData.supply) {
                        this.renderSupplyDemand(allData.supply);
                    }

                    // 시장 영향 렌더링 (혹시 누락되었을 경우)
                    if (allData.market_impact) {
                        this.renderMarketImpact(allData.market_impact);
                    }

                    // 리본 캐시 동기화
                    if (window.updateSentimentFromAnalysis && allData.outlook && allData.news_analysis) {
                        window.updateSentimentFromAnalysis(code, {
                            outlook: allData.outlook,
                            news_analysis: allData.news_analysis,
                            supply_demand: allData.supply
                        });
                    }

                    // 캐시 저장 (다음 번 로딩 속도 향상)
                    // 스트리밍으로 받은 데이터를 캐시 구조에 맞게 재구성
                    const cacheData = {
                        stock_info: {
                            code: code,
                            current_price: allData.price?.price,
                            change: allData.price?.change,
                            change_rate: allData.price?.rate
                        },
                        supply_demand: allData.supply,
                        news_analysis: allData.news_analysis,
                        outlook: allData.outlook,
                        technical: allData.technical,
                        market_impact: allData.market_impact, // 캐시에도 저장
                        fundamental_data: allData.fundamental_data, // 펀더멘털 데이터 저장
                        bollinger: allData.bollinger
                    };

                    if (allData.outlook && allData.news_analysis) {
                        API.setManualCache(code, cacheData);
                    }

                    // UI 최종 정리
                    if (loading) loading.style.display = 'none';
                    tabs.style.display = 'flex';
                    body.style.display = 'block';
                    this.switchTab('overview');
                },
                // onError: 오류 처리
                (error) => {
                    console.error('❌ 스트리밍 분석 오류:', error);
                    this.showErrorInModal(error, code);
                }
            );

        } catch (error) {
            console.error('상세 분석 로드 실패:', error);
            // 네트워크 오류 등의 경우
            const errorMsg = error.message === 'Failed to fetch'
                ? '서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.'
                : `오류가 발생했습니다: ${error.message}`;
            this.showErrorInModal(errorMsg, code);
        }
    },
    // 기본 정보만 먼저 렌더링 (주가 + 수급)
    renderBasicInfoOnly(priceInfo, supplyDemand) {
        if (!priceInfo) return;
        const changeRate = parseFloat(priceInfo.rate) || 0;
        const isUp = changeRate >= 0;
        const priceColor = isUp ? '#e53e3e' : '#3b82f6';
        // 수급 트렌드 뱃지
        let trendBadge = '';
        if (supplyDemand) {
            const fNet = supplyDemand.foreign_net || 0;
            const iNet = supplyDemand.institution_net || 0;
            if (fNet > 0 && iNet > 0) {
                trendBadge = '<span class="badge-supply buy">쌍끌이 매수 🚀</span>';
            } else if (fNet < 0 && iNet < 0) {
                trendBadge = '<span class="badge-supply sell">양매도 📉</span>';
            } else if (fNet > 0) {
                trendBadge = '<span class="badge-supply buy">외인 매수중 📈</span>';
            } else if (fNet < 0) {
                trendBadge = '<span class="badge-supply sell">외인 매도중 📉</span>';
            } else if (iNet > 0) {
                trendBadge = '<span class="badge-supply buy">기관 매수중 🏢</span>';
            } else if (iNet < 0) {
                trendBadge = '<span class="badge-supply sell">기관 매도중 📉</span>';
            } else {
                trendBadge = '<span class="badge-supply neutral">수급 보합</span>';
            }
        }
        const html = `
            <div id="section-price" class="analysis-section">
                <h3>주가 정보</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">현재가</span>
                        <span class="value" style="color: ${priceColor};">${formatCurrency(priceInfo.price)}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">전일대비</span>
                        <span class="value ${changeRate >= 0 ? 'positive' : 'negative'}">
                            ${formatCurrency(priceInfo.change)} (${priceInfo.rate}%)
                        </span>
                    </div>
                </div>
            </div>
            <div id="section-supply" class="analysis-section">
                <h3>수급 현황</h3>
                <div class="supply-summary">
                    ${supplyDemand ? `
                        <div class="supply-item ${supplyDemand.foreign_net >= 0 ? 'positive' : 'negative'}">
                            <span class="label">외국인</span>
                            <span class="value">${formatNumber(supplyDemand.foreign_net)}주</span>
                        </div>
                        <div class="supply-item ${supplyDemand.institution_net >= 0 ? 'positive' : 'negative'}">
                            <span class="label">기관</span>
                            <span class="value">${formatNumber(supplyDemand.institution_net)}주</span>
                        </div>
                        <div class="trend">${trendBadge}</div>
                    ` : '<span style="color: var(--text-secondary);">수급 정보 로딩중...</span>'}
                </div>
            </div>
            <div id="section-ai" class="analysis-section">
                <h3>AI 투자 의견</h3>
                <div class="outlook-card neutral" style="min-height: 120px; display: flex; align-items: center; justify-content: center;">
                    <div style="text-align: center;">
                        <div class="spinner" style="width: 24px; height: 24px; border-width: 3px; margin: 0 auto 0.5rem;"></div>
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">AI 분석 중...</p>
                    </div>
                </div>
            </div>
            <div id="section-news" class="analysis-section">
                <h3>뉴스 요약</h3>
                <div class="news-summary" style="display: flex; justify-content: center; padding: 1rem;">
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">뉴스 분석 중...</span>
                </div>
            </div>
        `;
        document.getElementById('overviewContent').innerHTML = html;
    },

    // AI 전망 부분만 업데이트 (기존 내용 유지)
    updateOverviewWithOutlook(outlook) {
        if (!outlook) return;
        const recommendationClass =
            outlook.recommendation === '매수' ? 'buy' :
                outlook.recommendation === '매도' ? 'sell' : 'neutral';
        const outlookHtml = `
            <div class="outlook-card ${recommendationClass}">
                <div class="outlook-header">
                    <span class="recommendation">${outlook.recommendation}</span>
                    <span class="confidence">신뢰도 ${outlook.confidence}%</span>
                </div>
                
                <!-- [NEW] 핵심 논리 -->
                <div class="key-logic" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">핵심 논리</h4>
                    <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6; white-space: pre-line;">${formatAIText(outlook.key_logic || '논리 정보 없음')}</div>
                </div>

                <div class="trading-scenario" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">매매 시나리오</h4>
                    <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6; white-space: pre-line;">${formatAIText(outlook.trading_scenario || '시나리오 정보 없음')}</div>
                </div>
                
                <!-- [NEW] 상세 분석 -->
                <div class="detailed-analysis" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">상세 분석</h4>
                    <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6; white-space: pre-line;">${formatAIText(outlook.detailed_analysis || outlook.reasoning || '분석 내용 없음')}</div>
                </div>
            </div>
        `;
        // AI 투자 의견 섹션만 선택적으로 업데이트 (ID 사용)
        const aiSection = document.getElementById('section-ai');
        if (aiSection) {
            aiSection.innerHTML = `<h3>AI 투자 의견</h3>${outlookHtml}`;
        }
    },

    // 뉴스 요약 부분만 업데이트 (기존 내용 유지)
    updateOverviewWithNews(newsData) {
        if (!newsData) return;

        const newsHtml = `
            <div class="news-summary">
                <div class="sentiment ${newsData.sentiment}">${newsData.sentiment}</div>
                <div class="news-box">
                    ${formatNewsText(newsData.reason)}
                </div>
            </div>
        `;

        // 뉴스 요약 섹션만 선택적으로 업데이트 (ID 사용)
        const newsSection = document.getElementById('section-news');
        if (newsSection) {
            newsSection.innerHTML = `<h3>뉴스 요약</h3>${newsHtml}`;
        }
    },

    // 한국 증시 영향 분석 렌더링 (New)
    renderMarketImpact(data) {
        if (!data || !data.market_outlook) return;

        const outlook = data.market_outlook;
        const supply = data.foreigner_supply_forecast;
        const strategy = data.sector_strategy;
        const insight = data.actionable_insight;

        // 감성 색상 결정
        const sentimentClass =
            outlook.sentiment.includes('긍정') ? 'buy' :
                outlook.sentiment.includes('부정') ? 'sell' : 'neutral';

        const html = `
            <div id="section-market-impact" class="analysis-section market-impact-section" style="border: 1px solid var(--border-color); background: rgba(255, 255, 255, 0.02);">
                <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                    🇺🇸 미국장 영향 분석 (Korea Impact)
                    <span class="badge-supply ${sentimentClass}" style="font-size: 0.8rem; padding: 2px 8px;">${outlook.sentiment}</span>
                </h3>
                
                <div class="impact-grid" style="display: grid; gap: 1rem; margin-top: 1rem;">
                    <!-- 1. 시장 전망 -->
                    <div class="impact-card">
                        <h4 style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">📉 시장 예상</h4>
                        <p style="font-weight: bold; color: var(--text-primary); margin-bottom: 0.3rem;">${outlook.predicted_movement}</p>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4;">${outlook.reason}</p>
                    </div>

                    <!-- 2. 외국인 수급 -->
                    <div class="impact-card">
                        <h4 style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">👽 외국인 수급</h4>
                        <p style="font-weight: bold; color: var(--text-primary); margin-bottom: 0.3rem;">${supply.direction}</p>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4;">${supply.logic}</p>
                    </div>

                    <!-- 3. 섹터 전략 -->
                    <div class="impact-card">
                        <h4 style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">🎯 섹터 전략</h4>
                        <div style="display: flex; gap: 1rem; font-size: 0.85rem;">
                            <div style="flex: 1;">
                                <span style="color: #e53e3e;">▲ 호재:</span> ${strategy.positive_sectors.join(', ')}
                            </div>
                            <div style="flex: 1;">
                                <span style="color: #3b82f6;">▼ 악재:</span> ${strategy.negative_sectors.join(', ')}
                            </div>
                        </div>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem;">💡 ${strategy.coupling_note}</p>
                    </div>

                    <!-- 4. 행동 가이드 -->
                    <div class="impact-card" style="background: rgba(var(--accent-rgb), 0.1); border-left: 3px solid var(--accent);">
                        <h4 style="color: var(--accent); font-size: 0.9rem; margin-bottom: 0.3rem;">⚡ Actionable Insight</h4>
                        <p style="font-size: 0.9rem; color: var(--text-primary);">${insight}</p>
                    </div>
                </div>
            </div>
        `;

        // 종합 탭의 맨 위에 추가하거나, 적절한 위치에 삽입
        // 여기서는 "주가 정보" 섹션 바로 다음(두 번째 위치)에 삽입
        const overviewContent = document.getElementById('overviewContent');

        // 이미 렌더링된 섹션이 있는지 확인 (ID 사용)
        const existingSection = document.getElementById('section-market-impact');
        if (existingSection) {
            existingSection.outerHTML = html;
        } else {
            // 주가 정보 섹션 찾기 (ID 사용)
            const priceSection = document.getElementById('section-price');
            if (priceSection) {
                priceSection.insertAdjacentHTML('afterend', html);
            } else {
                // 섹션이 없으면 그냥 맨 위에 추가
                overviewContent.insertAdjacentHTML('afterbegin', html);
            }
        }
    },

    // 모달에 에러 메시지 표시
    showErrorInModal(message, code) {
        const html = `
            <div class="analysis-section" style="text-align: center; padding: 3rem 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h3 style="color: var(--text-primary); margin-bottom: 1rem;">분석 실패</h3>
                <p style="color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">${message}</p>
                <button onclick="UI.retryAnalysis('${code}')" style="
                    background: var(--accent);
                    color: white;
                    border: none;
                    padding: 0.75rem 2rem;
                    border-radius: 8px;
                    font-size: 1rem;
                    cursor: pointer;
                    margin-right: 1rem;
                ">다시 시도</button>
                <button onclick="UI.closeModal()" style="
                    background: var(--bg-secondary);
                    color: var(--text-primary);
                    border: 1px solid var(--border-color);
                    padding: 0.75rem 2rem;
                    border-radius: 8px;
                    font-size: 1rem;
                    cursor: pointer;
                    margin-right: 1rem;
                ">닫기</button>
            </div>
        `;
        document.getElementById('overviewContent').innerHTML = html;
        document.getElementById('supplyContent').innerHTML = '';
        document.getElementById('newsContent').innerHTML = '';
    },

    // 분석 재시도
    async retryAnalysis(code) {
        // 로딩 상태로 재설정
        document.getElementById('overviewContent').innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <div class="spinner" style="width: 24px; height: 24px; border-width: 3px; margin: 0 auto 0.5rem;"></div>
                <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">다시 시도하고 있습니다...</p>
            </div>
        `;
        // 강제 새로고침으로 재시도
        await this.loadStockAnalysis(code);
    },

    // 탭 전환
    switchTab(tabName) {
        console.log('Switching to tab:', tabName);

        // 모든 탭 버튼 비활성화
        document.querySelectorAll('.analysis-tabs .tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // 모든 탭 콘텐츠 숨김
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        // 선택된 탭 활성화 (data-tab 속성 사용)
        const activeTab = document.querySelector(`.analysis-tabs .tab[data-tab="${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        } else {
            console.warn(`Tab button for ${tabName} not found`);
        }

        // 선택된 콘텐츠 표시
        const activeContent = document.getElementById(tabName);
        if (activeContent) {
            activeContent.classList.remove('hidden');
        } else {
            console.warn(`Content for ${tabName} not found`);
        }
    }
});
