// ui_core.js - Core UI functions
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

            if (rateNum > 0) {
                changeElem.style.color = 'var(--success)';
            } else if (rateNum < 0) {
                changeElem.style.color = 'var(--danger)';
            } else {
                changeElem.style.color = 'var(--text-secondary)';
            }
        }

        // Charts 객체가 있으면 기술적 지표 렌더링
        if (typeof Charts !== 'undefined' && Charts.renderTechnical) {
            Charts.renderTechnical(data.technical, data.stock_info, data.fundamental_data);
        }

        // 감성 정보 및 리본 업데이트 (중복 API 호출 방지)
        if (typeof window.updateSentimentFromAnalysis === 'function') {
            // code 변수가 여기 없는데? ui.js 원본을 보니 updateMarketIndex에 code가 없음.
            // 원본: window.updateSentimentFromAnalysis(code, data);
            // 근데 code가 정의되지 않음. 원본 버그인가?
            // updateMarketIndex(type, data) -> type은 'kospi'/'kosdaq'.
            // 감성 분석은 종목 코드 필요. 지수는 감성 분석 대상 아님.
            // 원본 코드 254라인: window.updateSentimentFromAnalysis(code, data);
            // code는 어디서 옴? ReferenceError 가능성.
            // 일단 주석 처리하거나 안전하게 처리.
            // console.warn("updateSentimentFromAnalysis called in updateMarketIndex but code is undefined");
        }
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
        document.getElementById('stockModal').style.display = 'none';
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
        if (btn) {
            btn.style.transform = 'rotate(360deg)';
            btn.style.transition = 'transform 0.5s ease';
            setTimeout(() => {
                btn.style.transform = '';
            }, 500);
        }

        // Main.js의 함수 호출 (전역으로 노출 필요)
        if (window.loadAllData) {
            window.loadAllData();
        }
    }
});
