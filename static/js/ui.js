// ui.js - DOM manipulation and rendering

const UI = {
    // 인증 상태 업데이트
    updateAuthStatus(isConnected) {
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-dot');

        if (isConnected) {
            statusText.textContent = '연결됨';
            statusDot.style.background = 'var(--success)';
        } else {
            statusText.textContent = '연결 실패';
            statusDot.style.background = 'var(--danger)';
        }
    },

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

    // 보유 종목 리스트 표시
    displayHoldings(holdings) {
        const grid = document.getElementById('holdingsGrid');
        grid.innerHTML = '';

        if (!holdings || holdings.length === 0) {
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">보유 종목이 없습니다</div>';
            return;
        }

        holdings.forEach(stock => {
            const card = this.createHoldingCard(stock);
            grid.appendChild(card);
        });
    },

    // 종목 카드 생성
    createHoldingCard(stock) {
        const card = document.createElement('div');
        card.className = 'holding-card';
        card.onclick = () => this.openStockModal(stock);

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

        // 손익에 따른 배경색과 테두리 색상 설정
        const isProfit = profitLoss >= 0;
        const bgColor = isProfit ? 'rgba(255, 100, 100, 0.05)' : 'rgba(100, 100, 255, 0.05)';
        const borderColor = isProfit ? '#e53e3e' : '#3b82f6';

        card.style.background = bgColor;
        card.style.borderLeft = `4px solid ${borderColor}`;
        const textColor = isProfit ? '#e53e3e' : '#3b82f6';

        // 감성 분석 요소 (Main.js에서 주입된 함수 사용)
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
                    <div>
                        <div class="holding-pl ${plClass}" style="color: ${textColor};">${plSign}${formatCurrency(profitLoss)}</div>
                        <div class="holding-pl ${plClass}" style="color: ${textColor};">${plSign}${profitRate.toFixed(2)}%</div>
                    </div>
                </div>
            </div>
            <div class="holding-body">
                <div class="holding-info">
                    <div class="holding-info-label">보유</div>
                    <div class="holding-info-value">${formatNumber(quantity)}주</div>
                </div>
                <div class="holding-info">
                    <div class="holding-info-label">평가금액</div>
                    <div class="holding-info-value" style="color: ${textColor};">${formatCurrency(evalAmount)}</div>
                </div>
                <div class="holding-info">
                    <div class="holding-info-label">매입가</div>
                    <div class="holding-info-value">${formatCurrency(purchasePrice)}</div>
                </div>
                <div class="holding-info">
                    <div class="holding-info-label">현재가</div>
                    <div class="holding-info-value" style="color: ${textColor};">${formatCurrency(currentPrice)}</div>
                </div>
            </div>
            ${sentimentElements.footerHtml}
        `;
        return card;
    },

    // 시장 지수 업데이트
    updateMarketIndex(type, data) {
        if (!data) return;

        const priceElem = document.getElementById(`${type}Price`);
        const changeElem = document.getElementById(`${type}Change`);

        if (priceElem && changeElem) {
            const cleanPrice = String(data.price).replace(/^\+/, '');
            const cleanChange = String(data.change).replace(/^\+/, '');
            const cleanRate = String(data.rate).replace(/^\+/, '');

            priceElem.textContent = cleanPrice;

            const rateNum = parseFloat(cleanRate);
            const sign = rateNum > 0 ? '+' : '';

            changeElem.className = '';
            if (rateNum > 0) {
                changeElem.classList.add('positive');
            } else if (rateNum < 0) {
                changeElem.classList.add('negative');
            }

            changeElem.textContent = `${sign}${cleanChange} (${sign}${cleanRate}%)`;

            if (rateNum > 0) {
                changeElem.style.color = 'var(--success)';
            } else if (rateNum < 0) {
                changeElem.style.color = 'var(--danger)';
            } else {
                changeElem.style.color = 'var(--text-secondary)';
            }
        }
    },

    // 모달 열기 및 데이터 로드 (강제 갱신 적용)
    async openStockModal(stock) {
        // 클릭 시 해당 종목 감성 정보 즉시 갱신
        if (typeof updateSingleSentiment === 'function') {
            updateSingleSentiment(stock.stk_cd);
        }

        const modal = document.getElementById('stockModal');
        const title = document.getElementById('modalTitle');
        const spinner = document.getElementById('loadingSpinner');
        const tabs = document.getElementById('analysisTabs');

        title.textContent = `${stock.stk_nm} (${stock.stk_cd}) 상세 분석`;
        modal.style.display = 'flex';
        spinner.style.display = 'block';
        tabs.style.display = 'none';

        // 이전 데이터 초기화
        document.getElementById('overviewContent').innerHTML = '';
        document.getElementById('supplyContent').innerHTML = '';
        document.getElementById('newsContent').innerHTML = '';
        document.getElementById('technicalContent').innerHTML = '';

        // 탭 초기화
        this.switchTab('overview');

        try {
            // 종합 분석 로드 (강제 갱신 False -> 10분 캐시 사용)
            await this.loadFullAnalysis(stock.stk_cd, false);

            // 분봉 차트 로드
            const chartData = await API.fetchMinuteChart(stock.stk_cd);
            if (chartData.success) {
                Charts.renderMinuteChart(chartData.data);
            }
        } catch (error) {
            console.error('모달 데이터 로드 중 오류:', error);
        } finally {
            spinner.style.display = 'none';
            tabs.style.display = 'flex';
        }
    },

    // 종합 분석 데이터 로드 및 렌더링
    async loadFullAnalysis(code, forceRefresh = false) {
        try {
            const result = await API.fetchFullAnalysis(code, forceRefresh);

            if (result.success) {
                const data = result.data;
                this.renderOverview(data);
                this.renderSupplyDemand(data.supply_demand);
                this.renderNews(data.news_analysis);
                Charts.renderTechnical(data.technical, data.stock_info);
            } else {
                document.getElementById('overviewContent').innerHTML =
                    `<div class="error">분석 데이터를 불러올 수 없습니다: ${result.message}</div>`;
            }
        } catch (error) {
            console.error('분석 로드 중 오류:', error);
            document.getElementById('overviewContent').innerHTML =
                `<div class="error">오류가 발생했습니다: ${error.message}</div>`;
        }
    },

    // 탭 전환
    switchTab(tabName) {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // 현재 클릭된 탭 찾기 (이벤트 객체 사용 불가 시 수동 처리 필요할 수 있음)
        // 여기서는 onclick="UI.switchTab('name')" 형태로 호출된다고 가정하고
        // event.target을 사용하거나, 호출 시 요소를 넘겨받아야 함.
        // script.js에서는 event.target을 사용했음.
        if (event && event.target) {
            event.target.classList.add('active');
        } else {
            // 초기화 시 overview 탭 활성화
            const tabBtn = document.querySelector(`.tab[onclick*="'${tabName}'"]`);
            if (tabBtn) tabBtn.classList.add('active');
        }

        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        const targetContent = document.getElementById(tabName);
        if (targetContent) {
            targetContent.classList.remove('hidden');
        }
    },

    closeModal() {
        document.getElementById('stockModal').style.display = 'none';
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

    // 종목 검색 필터
    filterHoldings() {
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
    },

    // 데이터 새로고침 (버튼)
    refreshData() {
        console.log('🔄 데이터 새로고침...');
        const btn = document.querySelector('.btn-refresh');
        btn.style.transform = 'rotate(360deg)';
        btn.style.transition = 'transform 0.5s ease';

        setTimeout(() => {
            btn.style.transform = '';
        }, 500);

        // Main.js의 함수 호출 (전역으로 노출 필요)
        if (window.loadAllData) {
            window.loadAllData();
        }
    },

    // 관심종목 카드 표시
    displayWatchlist(stocks) {
        const grid = document.getElementById('watchlistGrid');
        if (!grid) return;

        if (stocks.length === 0) {
            grid.innerHTML = '<p style="text-align: center; padding: 2rem; color: #888;">관심종목이 없습니다. 위에서 종목 코드를 입력하여 추가하세요.</p>';
            return;
        }

        const existingCodes = Array.from(grid.querySelectorAll('.watchlist-card')).map(card => card.getAttribute('data-code'));
        const newCodes = stocks.map(item => item.code);

        existingCodes.forEach(code => {
            if (!newCodes.includes(code)) {
                const card = grid.querySelector(`[data-code="${code}"]`);
                if (card) card.remove();
            }
        });

        stocks.forEach(item => {
            if (item.data && !existingCodes.includes(item.code)) {
                const card = this.createWatchlistCard(item.code, item.data);
                grid.appendChild(card);
            }
        });

        // 감성 분석 업데이트 트리거 (Main.js에서 처리)
        if (window.triggerWatchlistSentimentUpdate) {
            window.triggerWatchlistSentimentUpdate(stocks);
        }
    },

    // 관심종목 카드 생성
    createWatchlistCard(code, stockData) {
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
            </div>
        `;

        card.onclick = (e) => {
            if (e.target.tagName !== 'BUTTON') {
                this.openStockModal({ code, name, price: stockData.price, stk_cd: code, stk_nm: name });
            }
        };

        setTimeout(() => this.loadSupplyInfoOnce(card, code), 100);

        return card;
    },

    // 수급 정보 로드 (관심종목용)
    async loadSupplyInfoOnce(cardElement, code) {
        if (cardElement.getAttribute('data-supply-loaded') === 'true') return;

        const supplyElem = document.getElementById(`supply-${code}`);
        const reasonElem = document.getElementById(`reason-${code}`);

        if (!supplyElem || !reasonElem) return;

        try {
            // 여기서는 강제 갱신 없이 로드
            const result = await API.fetchFullAnalysis(code, false);

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
                } else {
                    reasonElem.innerHTML = '<span style="color: #888;">-</span>';
                }

                cardElement.setAttribute('data-supply-loaded', 'true');
            }
        } catch (error) {
            console.error(`수급 정보 로드 실패 (${code}):`, error);
            supplyElem.innerHTML = '<span style="color: #888; font-size: 0.75rem;">-</span>';
            reasonElem.innerHTML = '<span style="color: #888;">-</span>';
        }
    }
};
