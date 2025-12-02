/**
 * ui_core.js - 핵심 UI 기능 모듈
 * ================================================================
 * 대시보드의 핵심 UI 기능을 제공합니다.
 * 
 * 주요 기능:
 * - 인증 상태 업데이트 (연결/실패 표시)
 * - 시장 지수 업데이트 (KOSPI/KOSDAQ)
 * - 탭 전환 기능
 * - 모달 닫기
 * - 종목 검색 필터
 * - 데이터 새로고침
 * 
 * 특징:
 * - UI 모듈은 window.UI 객체에 통합되어 관리됨
 * - 모든 함수는 전역에서 접근 가능
 * ================================================================
 */

window.UI = window.UI || {};

Object.assign(window.UI, {
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

            // 등락에 따른 색상 결정 (지수 값은 흰색 유지, 비율에만 색상 적용)
            const textColor = rateNum > 0 ? '#e53e3e' : (rateNum < 0 ? '#3b82f6' : 'var(--text-secondary)');

            // 변동 비율에 색상 적용 (CSS 우선순위를 위해 setProperty 사용)
            changeElem.style.setProperty('color', textColor, 'important');

            // 시장 지수 카드에 역동적인 스타일 적용
            const indexCard = priceElem.closest('.index-card');
            if (indexCard) {
                const isUp = rateNum >= 0;
                const bgColor = isUp ? 'rgba(255, 100, 100, 0.05)' : 'rgba(100, 100, 255, 0.05)';
                const borderColor = isUp ? '#e53e3e' : '#3b82f6';

                indexCard.style.background = bgColor;
                indexCard.style.borderLeft = `4px solid ${borderColor}`;
            }
        }
        // Note: Market indices don't have technical analysis data
        // Charts.renderTechnical is only for individual stock analysis
    },

    // 탭 전환
    switchTab(tabName) {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // 현재 클릭된 탭 찾기
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
        // 진행 중인 분석 요청 취소
        if (this.currentAnalysisController) {
            this.currentAnalysisController.abort();
            this.currentAnalysisController = null;
            console.log('⏹️ 모달 닫기 - 분석 요청 취소');
        }

        document.getElementById('stockModal').style.display = 'none';

    },

    // 글로벌 마켓 모달 열기
    async openMarketModal() {
        const modal = document.getElementById('marketModal');
        const modalBody = document.getElementById('marketModalBody');

        modal.style.display = 'flex'; // Fix: Center the modal
        modalBody.innerHTML = `
            <div class="market-loading-container" style="text-align: center; padding: 2rem;">
                <div class="loading-spinner"></div>
                <div class="loading-text" style="margin-top: 1rem; color: var(--text-secondary);">글로벌 마켓 데이터 수집 중...</div>
            </div>
            <div id="marketHeadlines" style="display:none;"></div>
            <div id="marketAnalysis" style="display:none;"></div>
        `;

        // 스트리밍 데이터 처리
        await API.fetchGlobalMarketStreaming(
            (type, data) => {
                // 진행 상태 업데이트
                if (type === 'basic') {
                    // 1단계: 헤드라인 및 기본 정보 표시
                    const loadingText = modalBody.querySelector('.loading-text');
                    if (loadingText) loadingText.textContent = 'AI가 시장 이벤트를 분석 중입니다...';

                    this.renderMarketHeadlines(data.headlines);
                } else if (type === 'events') {
                    // 2단계: 이벤트 분석 완료
                    const loadingText = modalBody.querySelector('.loading-text');
                    if (loadingText) loadingText.textContent = '한국 증시 영향 분석 중...';
                } else if (type === 'impact') {
                    // 3단계: 최종 분석 완료
                    const loadingContainer = modalBody.querySelector('.market-loading-container');
                    if (loadingContainer) loadingContainer.style.display = 'none';

                    this.renderMarketAnalysis(data);
                }
            },
            () => {
                console.log('✅ 글로벌 마켓 분석 완료');
            },
            (errorMessage) => {
                console.error('Market Modal Error:', errorMessage);
                const loadingContainer = modalBody.querySelector('.market-loading-container');
                if (loadingContainer) {
                    loadingContainer.innerHTML = `<div class="error-message">오류 발생: ${errorMessage}</div>`;
                }
            }
        );
    },

    // 글로벌 마켓 모달 닫기
    closeMarketModal() {
        document.getElementById('marketModal').style.display = 'none';
    },

    // 헤드라인 렌더링 (New)
    renderMarketHeadlines(headlines) {
        const container = document.getElementById('marketHeadlines');
        if (!container) return;

        if (!headlines || headlines.length === 0) return;

        let html = `
            <div class="headlines-section" style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                <h4 style="color: var(--text-secondary); margin-bottom: 0.8rem; font-size: 0.9rem;">📰 주요 시장 뉴스</h4>
                <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.9rem; color: var(--text-primary);">
        `;

        // 최대 5개만 표시
        headlines.slice(0, 5).forEach(headline => {
            html += `<li style="margin-bottom: 0.5rem; padding-left: 1rem; position: relative;">
                <span style="position: absolute; left: 0; color: var(--accent-1);">•</span>
                ${headline}
            </li>`;
        });

        html += `</ul></div>`;

        container.innerHTML = html;
        container.style.display = 'block';
    },

    // 분석 결과 렌더링 (Renamed from renderMarketModal)
    renderMarketAnalysis(koreaImpact) {
        const container = document.getElementById('marketAnalysis');
        if (!container) return;

        if (!koreaImpact || !koreaImpact.market_outlook) {
            container.innerHTML = '<div class="error-message">분석 데이터가 없습니다.</div>';
            container.style.display = 'block';
            return;
        }

        const outlook = koreaImpact.market_outlook;
        const supply = koreaImpact.foreigner_supply_forecast;
        const strategy = koreaImpact.sector_strategy;
        const insight = koreaImpact.actionable_insight;

        const sentimentClass =
            outlook.sentiment.includes('긍정') ? 'buy' :
                outlook.sentiment.includes('부정') ? 'sell' : 'neutral';

        const html = `
            <div class="analysis-section market-impact-section" style="border: none; background: transparent; padding: 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span class="badge-supply ${sentimentClass}" style="font-size: 1rem; padding: 4px 12px;">${outlook.sentiment}</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">AI 분석 완료</span>
                </div>
                
                <div class="impact-grid" style="display: grid; gap: 1rem;">
                    <!-- 1. 시장 전망 -->
                    <div class="impact-card">
                        <h4 style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">📉 시장 예상</h4>
                        <p style="font-weight: bold; color: var(--text-primary); margin-bottom: 0.3rem; font-size: 1.1rem;">${outlook.predicted_movement}</p>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5;">${outlook.reason}</p>
                    </div>

                    <!-- 2. 외국인 수급 -->
                    <div class="impact-card">
                        <h4 style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">👽 외국인 수급</h4>
                        <p style="font-weight: bold; color: var(--text-primary); margin-bottom: 0.3rem;">${supply.direction}</p>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5;">${supply.logic}</p>
                    </div>

                    <!-- 3. 섹터 전략 -->
                    <div class="impact-card">
                        <h4 style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">🎯 섹터 전략</h4>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.9rem;">
                            <div>
                                <span style="color: #e53e3e; font-weight: bold;">▲ 호재 섹터:</span> 
                                <span style="color: var(--text-primary);">${strategy.positive_sectors.join(', ')}</span>
                            </div>
                            <div>
                                <span style="color: #3b82f6; font-weight: bold;">▼ 악재 섹터:</span> 
                                <span style="color: var(--text-primary);">${strategy.negative_sectors.join(', ')}</span>
                            </div>
                        </div>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.8rem; padding-top: 0.5rem; border-top: 1px solid var(--border-color);">
                            💡 ${strategy.coupling_note}
                        </p>
                    </div>

                    <!-- 4. 행동 가이드 -->
                    <div class="impact-card" style="background: rgba(var(--accent-rgb), 0.1); border-left: 4px solid var(--accent);">
                        <h4 style="color: var(--accent); font-size: 1rem; margin-bottom: 0.5rem;">⚡ Actionable Insight</h4>
                        <p style="font-size: 1rem; color: var(--text-primary); line-height: 1.6;">${insight}</p>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        container.style.display = 'block';
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
        console.log('🔄 데이터 새로고침 (강제 리로드)...');
        const btn = document.querySelector('.btn-refresh');
        if (btn) {
            btn.style.transform = 'rotate(360deg)';
            btn.style.transition = 'transform 0.5s ease';
        }

        // 모바일 캐시 문제 해결을 위해 페이지 전체 리로드 수행
        setTimeout(() => {
            window.location.reload(true);
        }, 300);
    }
});
