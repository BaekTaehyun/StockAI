// ui_details.js - Detail view rendering functions
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
    },

    // 수급 탭 렌더링
    renderSupplyDemand(data) {
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
    },

    // 뉴스 탭 렌더링
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
        loading.style.display = 'block';
        tabs.style.display = 'none';
        body.style.display = 'none';

        // 데이터 로드
        this.loadStockAnalysis(stock.stk_cd);
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
                loading.style.display = 'none';
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
    }
});
