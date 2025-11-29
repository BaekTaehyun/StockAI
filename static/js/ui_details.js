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

        // 수급 트렌드 로직 (쌍끌이 등)
        const fNet = safeSupply.foreign_net;
        const iNet = safeSupply.institution_net;
        let trendBadge = safeSupply.trend;

        if (fNet > 0 && iNet > 0) {
            trendBadge = '<span class="badge-supply buy">쌍끌이 매수 🚀</span>';
        } else if (fNet < 0 && iNet < 0) {
            trendBadge = '<span class="badge-supply sell">양매도 📉</span>';
        }

        try {
            const html = `
                <div class="analysis-section">
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

                <div class="analysis-section">
                    <h3>AI 투자 의견</h3>
                    <div class="outlook-card ${recommendationClass}">
                        <div class="outlook-header">
                            <span class="recommendation">${safeOutlook.recommendation}</span>
                            <span class="confidence">신뢰도 ${safeOutlook.confidence}%</span>
                        </div>
                        <div class="trading-scenario" style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                             <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">매매 시나리오</h4>
                             <div style="font-family: inherit; color: var(--text-secondary); line-height: 1.6;">${formatAIText(safeOutlook.trading_scenario || '시나리오 정보 없음')}</div>
                        </div>
                        <div class="reasoning" style="margin-top: 1rem; line-height: 1.6; color: var(--text-secondary);">${formatAIText(safeOutlook.reasoning)}</div>
                    </div>
                </div>

                <div class="analysis-section">
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

                <div class="analysis-section">
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
                <div class="outlook-card neutral" style="min-height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px; margin-bottom: 0.5rem;"></div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">분석 중...</p>
                </div>
            </div>


            <div class="analysis-section">
                <h3>수급 현황</h3>
                <div class="supply-summary" style="display: flex; justify-content: center; padding: 1rem;">
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">분석 중...</span>
                </div>
            </div>

            <div class="analysis-section">
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

                // UI 표시 업데이트 (이미 표시되어 있지만, 로딩 스피너가 있다면 확실히 숨김)
                if (loading) loading.style.display = 'none';
                tabs.style.display = 'flex';
                body.style.display = 'block';

                // 기본 탭 활성화
                this.switchTab('overview');
            } else {
                // 에러 메시지를 모달에 표시
                const errorMessage = result.message || '데이터를 불러오는데 실패했습니다.';
                this.showErrorInModal(errorMessage, code);
            }
        } catch (error) {
            console.error('상세 분석 로드 실패:', error);
            // 네트워크 오류 등의 경우
            const errorMsg = error.message === 'Failed to fetch'
                ? '서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.'
                : `오류가 발생했습니다: ${error.message}`;
            this.showErrorInModal(errorMsg, code);
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
