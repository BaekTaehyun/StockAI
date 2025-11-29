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

            if (rateNum > 0) {
                changeElem.style.color = 'var(--success)';
            } else if (rateNum < 0) {
                changeElem.style.color = 'var(--danger)';
            } else {
                changeElem.style.color = 'var(--text-secondary)';
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
