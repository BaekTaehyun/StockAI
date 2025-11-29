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
    // 계좌 요약 업데이트
    updateAccountSummary(data) {
        if (!data) return;

        // 총 매입금액
        document.getElementById('totalPurchase').textContent = formatCurrency(data.total_purchase);

        // 총 평가금액
        document.getElementById('totalEval').textContent = formatCurrency(data.total_eval);

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
        document.getElementById('holdingsCount').textContent = `${data.holdings_count}개`;
    },

    // 종합 탭 렌더링
    renderOverview(data) {
        const { stock_info, supply_demand, news_analysis, outlook } = data;

        const recommendationClass =
            outlook.recommendation === '매수' ? 'buy' :
                outlook.recommendation === '매도' ? 'sell' : 'neutral';

        const changeRate = parseFloat(stock_info.change_rate) || 0;
        const isUp = changeRate >= 0;
        const priceColor = isUp ? '#e53e3e' : '#3b82f6';

        // 수급 트렌드 로직 (쌍끌이 등)
        const fNet = supply_demand.foreign_net;
        const iNet = supply_demand.institution_net;
        let trendBadge = supply_demand.trend;

        if (fNet > 0 && iNet > 0) {
            trendBadge = '<span class="badge-supply buy">쌍끌이 매수 🚀</span>';
        } else if (fNet < 0 && iNet < 0) {
            trendBadge = '<span class="badge-supply sell">양매도 📉</span>';
        }

        const html = `
            <div class="analysis-section">
                <h3>주가 정보</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">현재가</span>
                        <span class="value" style="color: ${priceColor};">${formatCurrency(stock_info.current_price)}</span>
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
                    <div class="trading-scenario" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                         <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">매매 시나리오</h4>
                         <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6;">${formatAIText(outlook.trading_scenario || '시나리오 정보 없음')}</div>
                    </div>
                    <div class="reasoning" style="margin-top: 1rem; line-height: 1.6; color: var(--text-secondary);">${formatAIText(outlook.reasoning)}</div>
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
                    <div class="trend">${trendBadge}</div>
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

        // 전역 로딩 스피너 숨김
        loading.style.display = 'none';

        // 탭과 본문 즉시 표시
        tabs.style.display = 'flex';
        body.style.display = 'block';

        // 초기 데이터(주가 정보) 렌더링 및 로딩 상태 표시
        this.renderInitialOverview(stock);

        // 기본 탭 활성화
        this.switchTab('overview');

        // 데이터 로드
        this.loadStockAnalysis(stock.stk_cd);
    },

    // 초기 개요 렌더링 (주가 정보 즉시 표시 + 로딩 인디케이터)
    renderInitialOverview(stock) {
        const currentPrice = parseInt(stock.price || stock.cur_prc || 0);
        // change, change_rate 정보가 stock 객체에 없을 수도 있음 (목록에서 넘겨받은 데이터에 따라 다름)
        // ui_cards.js에서 넘겨주는 데이터 구조 확인 필요. 보통 price만 넘겨주는 경우가 많음.
        // 여기서는 일단 있는 정보로 렌더링하고, 없는 정보는 '-'로 표시하거나 계산 시도

        // ui_cards.js의 openStockModal 호출부를 보면: 
        // { code, name, price: stockData.price, stk_cd: code, stk_nm: name } 형태로 넘김 (관심종목)
        // 보유종목은 전체 stock 객체를 넘김.

        // 포맷팅
        const formattedPrice = formatCurrency(currentPrice);

        const html = `
            <div class="analysis-section">
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

            <div class="analysis-section">
                <h3>AI 투자 의견</h3>
                <div class="outlook-card neutral" style="min-height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div class="spinner" style="width: 40px; height: 40px; border-width: 4px; margin-bottom: 1rem;"></div>
                    <p style="color: var(--text-secondary);">AI가 종목을 분석하고 있습니다...</p>
                </div>
            </div>

            <div class="analysis-section">
                <h3>수급 현황</h3>
                <div class="supply-summary" style="display: flex; justify-content: center; padding: 2rem;">
                    <span style="color: var(--text-secondary);">수급 데이터 분석 중...</span>
                </div>
            </div>

            <div class="analysis-section">
                <h3>뉴스 요약</h3>
                <div class="news-summary" style="display: flex; justify-content: center; padding: 2rem;">
                    <span style="color: var(--text-secondary);">최신 뉴스 분석 중...</span>
                </div>
            </div>
        `;

        document.getElementById('overviewContent').innerHTML = html;

        // 다른 탭들도 로딩 상태로 초기화
        document.getElementById('supplyContent').innerHTML = '<div style="padding: 3rem; text-align: center; color: var(--text-secondary);">데이터를 불러오는 중입니다...</div>';
        document.getElementById('newsContent').innerHTML = '<div style="padding: 3rem; text-align: center; color: var(--text-secondary);">데이터를 불러오는 중입니다...</div>';
    },

    // 종목 상세 분석 데이터 로드
    async loadStockAnalysis(code) {
        const loading = document.getElementById('loadingSpinner');
        const tabs = document.getElementById('analysisTabs');
        const body = document.getElementById('modalBody');

        try {
            const result = await API.fetchFullAnalysis(code, false); // 캐시 우선 사용

            if (result.success && result.data) {
                const data = result.data;

                // 각 탭 렌더링
                this.renderOverview(data);
                this.renderSupplyDemand(data.supply_demand);
                this.renderNews(data.news_analysis);

                // 기술적 분석 렌더링 (Charts.js 사용)
                if (typeof Charts !== 'undefined' && Charts.renderTechnical) {
                    Charts.renderTechnical(data.technical, data.stock_info, data.fundamental_data);
                }

                // UI 표시 업데이트
                // UI 표시 업데이트 (이미 표시되어 있지만, 로딩 스피너가 있다면 확실히 숨김)
                if (loading) loading.style.display = 'none';
                tabs.style.display = 'flex';
                body.style.display = 'block';

                // 기본 탭 활성화
                this.switchTab('overview');
            } else {
                alert('데이터를 불러오는데 실패했습니다.');
                this.closeModal();
            }
        } catch (error) {
            console.error('상세 분석 로드 실패:', error);
            alert('오류가 발생했습니다.');
            this.closeModal();
        }
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
