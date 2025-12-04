/**
 * ui_cards.js - 카드 UI 렌더링 모듈
 * ================================================================
 * 보유 종목 카드 및 관심종목 카드의 생성과 업데이트를 담당합니다.
 * 
 * 주요 기능:
 * - 보유 종목 카드 생성 및 업데이트
 * - 관심종목 카드 생성 및 표시
 * - 수급 정보 로드 (외국인/기관 순매수)
 * - AI 매매 전략 표시 (진입가/목표가/손절가)
 * 
 * 특징:
 * - 카드 재사용: 기존 카드는 데이터만 업데이트하여 깜빡임 방지
 * - 비동기 전략 로드: 카드 생성 후 100ms 후 전략 정보 로드
 * ================================================================
 */

window.UI = window.UI || {};

Object.assign(window.UI, {
    // 보유 종목 리스트 표시
    displayHoldings(holdings) {
        const grid = document.getElementById('holdingsGrid');

        if (!holdings || holdings.length === 0) {
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">보유 종목이 없습니다</div>';
            return;
        }

        // 기존 카드 코드 목록
        const existingCards = Array.from(grid.querySelectorAll('.holding-card'));
        const existingCodes = existingCards.map(card => card.getAttribute('data-code'));
        const newCodes = holdings.map(stock => stock.stk_cd);

        // 없어진 종목 카드 제거
        existingCards.forEach(card => {
            const code = card.getAttribute('data-code');
            if (!newCodes.includes(code)) {
                card.remove();
            }
        });

        // 카드 업데이트 또는 생성
        holdings.forEach((stock, index) => {
            const stockCode = stock.stk_cd || '';
            const existingCard = grid.querySelector(`[data-code="${stockCode}"]`);

            if (existingCard) {
                // 기존 카드 데이터만 업데이트 (수급/전략 섹션은 건드리지 않음)
                this.updateHoldingCardData(existingCard, stock);

                // 수급 정보 업데이트 (경량 모드로 활성화)
                this.updateSupplyInfo(existingCard, stockCode);
            } else {
                const card = this.createHoldingCard(stock);
                grid.appendChild(card);

                // 순차적으로 100ms씩 지연하여 요청 (경량 모드)
                setTimeout(() => this.loadStrategyInfo(null, stockCode, true), index * 100);
            }
        });
    },

    // 종목 카드 생성
    createHoldingCard(stock) {
        const card = document.createElement('div');
        card.className = 'holding-card';
        card.setAttribute('data-code', stock.stk_cd || '');
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
            <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 1rem;">
                    <div>
                        <div class="section-header-title">수급 정보</div>
                        <div id="supply-${stockCode}" style="min-height: 24px;">
                            <span class="badge-supply neutral">분석중...</span>
                        </div>
                    </div>
                    <div>
                        <div class="section-header-title">AI 매매 전략</div>
                        <div id="strategy-${stockCode}" style="min-height: 24px;">
                            <div class="strategy-loading">
                                <span class="strategy-loading-pill">로딩중...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            </div>
            ${sentimentElements.footerHtml}
        `;

        return card;
    },

    // 보유 종목 카드 데이터 업데이트 (수급/전략 섹션 유지)
    updateHoldingCardData(card, stock) {
        const quantity = parseInt(stock.rmnd_qty) || 0;
        const purchasePrice = parseInt(stock.pur_pric) || 0;
        const currentPrice = parseInt(stock.cur_prc) || 0;
        const profitLoss = parseInt(stock.evltv_prft) || 0;
        const profitRate = parseFloat(stock.prft_rt) || 0;
        const evalAmount = parseInt(stock.evlt_amt) || 0;

        const plClass = profitLoss >= 0 ? 'positive' : 'negative';
        const plSign = profitLoss >= 0 ? '+' : '';
        const isProfit = profitLoss >= 0;
        const textColor = isProfit ? '#e53e3e' : '#3b82f6';

        // 손익 업데이트
        const plElements = card.querySelectorAll('.holding-pl');
        if (plElements.length >= 2) {
            plElements[0].textContent = `${plSign}${formatCurrency(profitLoss)}`;
            plElements[0].className = `holding-pl ${plClass}`;
            plElements[0].style.color = textColor;

            plElements[1].textContent = `${plSign}${profitRate.toFixed(2)}%`;
            plElements[1].className = `holding-pl ${plClass}`;
            plElements[1].style.color = textColor;
        }

        // 보유수량, 평가금액, 현재가 업데이트
        const infoValues = card.querySelectorAll('.holding-info-value');
        if (infoValues.length >= 4) {
            infoValues[0].textContent = `${formatNumber(quantity)}주`;
            infoValues[1].textContent = formatCurrency(evalAmount);
            infoValues[1].style.color = textColor;
            infoValues[2].textContent = formatCurrency(purchasePrice);
            infoValues[3].textContent = formatCurrency(currentPrice);
            infoValues[3].style.color = textColor;
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
            if (item.data) {
                if (!existingCodes.includes(item.code)) {
                    const card = this.createWatchlistCard(item.code, item.data);
                    grid.appendChild(card);
                } else {
                    // 기존 카드 업데이트 시에도 수급 정보 갱신 시도
                    const card = grid.querySelector(`[data-code="${item.code}"]`);
                    if (card) {
                        this.updateSupplyInfo(card, item.code);
                    }
                }
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
        // marginBottom은 CSS에서 관리 (모바일 반응형 적용 위해)

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
                            <div class="section-header-title">수급 정보</div>
                            <div id="supply-${code}" style="min-height: 24px;">
                                <span class="badge-supply neutral">분석중...</span>
                            </div>
                        </div>
                        <div>
                            <div class="section-header-title">AI 매매 전략</div>
                            <div id="strategy-${code}" style="min-height: 24px;">
                                <div class="strategy-loading">
                                    <span class="strategy-loading-pill">로딩중...</span>
                                </div>
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
        const strategyElem = document.getElementById(`strategy-${code}`);

        if (!supplyElem || !strategyElem) return;

        try {
            // 경량 모드로 로드 (초기 로딩 최적화)
            const result = await API.fetchFullAnalysis(code, false, true, false);
            // lightweight=true, forceRefresh=false, highPriority=false

            if (result.success && result.data) {
                const data = result.data;

                if (data.supply_demand) {
                    const foreigner = data.supply_demand.foreign_net || 0;
                    const institution = data.supply_demand.institution_net || 0;

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

                if (data.outlook && data.outlook.price_strategy) {
                    const strategy = data.outlook.price_strategy;
                    const entry = strategy.entry || '-';
                    const target = strategy.target || '-';
                    const stopLoss = strategy.stop_loss || '-';

                    strategyElem.innerHTML = `
                        <div class="strategy-grid">
                            <div class="strategy-row">
                                <span class="strategy-label">진입</span>
                                <span class="strategy-value entry">${entry}</span>
                            </div>
                            <div class="strategy-row">
                                <span class="strategy-label">목표</span>
                                <span class="strategy-value target">${target}</span>
                            </div>
                            <div class="strategy-row">
                                <span class="strategy-label">손절</span>
                                <span class="strategy-value stop">${stopLoss}</span>
                            </div>
                        </div>
                    `;
                } else {
                    strategyElem.innerHTML = '<span class="badge-supply neutral">전략 수립 중...</span>';
                }

                cardElement.setAttribute('data-supply-loaded', 'true');
            }
        } catch (error) {
            Logger.error('UI_Cards', `수급 정보 로드 실패 (${code}):`, error);
            supplyElem.innerHTML = '<span style="color: #888; font-size: 0.75rem;">-</span>';
            strategyElem.innerHTML = '<span style="color: #888;">-</span>';
        }
    },

    // 전략 정보 로드 (보유종목용) - 경량 모드 지원
    async loadStrategyInfo(cardElement, code, lightweight = false) {
        const strategyElem = document.getElementById(`strategy-${code}`);
        const supplyElem = document.getElementById(`supply-${code}`);

        if (!strategyElem) return;

        try {
            const result = await API.fetchFullAnalysis(code, false, lightweight, false);
            // lightweight: 초기 로딩 시 true, forceRefresh: false, highPriority: false

            if (result.success && result.data) {
                const data = result.data;

                // 수급 정보 업데이트
                if (supplyElem && data.supply_demand) {
                    const foreigner = data.supply_demand.foreign_net || 0;
                    const institution = data.supply_demand.institution_net || 0;

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

                // 전략 정보 업데이트
                if (data.outlook && data.outlook.price_strategy) {
                    const strategy = data.outlook.price_strategy;
                    const entry = strategy.entry || '-';
                    const target = strategy.target || '-';
                    const stopLoss = strategy.stop_loss || '-';

                    strategyElem.innerHTML = `
                        <div class="strategy-grid">
                            <div class="strategy-row">
                                <span class="strategy-label">진입</span>
                                <span class="strategy-value entry">${entry}</span>
                            </div>
                            <div class="strategy-row">
                                <span class="strategy-label">목표</span>
                                <span class="strategy-value target">${target}</span>
                            </div>
                            <div class="strategy-row">
                                <span class="strategy-label">손절</span>
                                <span class="strategy-value stop">${stopLoss}</span>
                            </div>
                        </div>
                    `;
                } else {
                    strategyElem.innerHTML = '<span class="badge-supply neutral">전략 수립 중...</span>';
                }
            }
        } catch (error) {
            Logger.error('UI_Cards', `전략 정보 로드 실패 (${code}):`, error);
            if (supplyElem) supplyElem.innerHTML = '<span style="color: #888;">-</span>';
            strategyElem.innerHTML = '<span style="color: #888;">-</span>';
        }
    },

    // 수급 정보 업데이트 (스로틀링 적용)
    async updateSupplyInfo(cardElement, code) {
        const now = Date.now();
        const lastUpdate = parseInt(cardElement.getAttribute('data-last-supply-update') || '0');
        const throttleTime = 60 * 1000; // 60초

        if (now - lastUpdate < throttleTime) {
            return; // 스로틀링
        }

        const supplyElem = document.getElementById(`supply-${code}`);
        if (!supplyElem) return;

        try {
            const result = await API.fetchSupplyDemand(code);
            if (result.success && result.data) {
                const data = result.data;
                const foreigner = data.foreign_net || 0;
                const institution = data.institution_net || 0;

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

                // 업데이트 시간 기록
                cardElement.setAttribute('data-last-supply-update', now.toString());
            }
        } catch (error) {
            Logger.error('UI_Cards', `수급 정보 업데이트 실패 (${code}):`, error);
        }
    }
});
