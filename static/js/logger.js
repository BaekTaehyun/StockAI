/**
 * Logger 유틸리티
 * ================================================================
 * 디버그 모드에 따라 콘솔 로그 출력을 제어합니다.
 * - localStorage의 DEBUG_MODE 값으로 제어
 * - 브라우저 콘솔에서 Logger.toggleDebug()로 전환 가능
 * ================================================================
 */

const Logger = {
    /**
     * localStorage에서 디버그 모드 확인
     * 기본값: true (개발 중)
     */
    get DEBUG() {
        const stored = localStorage.getItem('DEBUG_MODE');
        // 처음 사용 시 기본값 true
        if (stored === null) {
            // 서버 설정값 우선 사용, 없으면 true
            const defaultMode = (typeof window.SERVER_DEBUG_MODE !== 'undefined')
                ? window.SERVER_DEBUG_MODE
                : true;

            localStorage.setItem('DEBUG_MODE', defaultMode.toString());
            return defaultMode;
        }
        return stored === 'true';
    },

    /**
     * 디버그 로그 (DEBUG 모드에서만 출력)
     */
    debug: function (tag, message, ...args) {
        if (this.DEBUG) {
            console.log(`[${tag}]`, message, ...args);
        }
    },

    /**
     * 정보 로그 (항상 출력)
     */
    info: function (tag, message, ...args) {
        console.log(`ℹ️ [${tag}]`, message, ...args);
    },

    /**
     * 경고 로그 (항상 출력)
     */
    warn: function (tag, message, ...args) {
        console.warn(`⚠️ [${tag}]`, message, ...args);
    },

    /**
     * 에러 로그 (항상 출력)
     */
    error: function (tag, message, ...args) {
        console.error(`❌ [${tag}]`, message, ...args);
    },

    /**
     * 디버그 모드 토글 (페이지 새로고침 필요)
     */
    toggleDebug: function () {
        const current = this.DEBUG;
        const newValue = !current;
        localStorage.setItem('DEBUG_MODE', newValue.toString());
        console.log(`🔧 Debug mode will be ${newValue ? 'ON' : 'OFF'} after page reload`);
        console.log('   → Reloading page...');
        setTimeout(() => location.reload(), 500);
    },

    /**
     * 디버그 모드 설정 (페이지 새로고침 필요)
     */
    setDebugMode: function (enabled) {
        localStorage.setItem('DEBUG_MODE', enabled.toString());
        console.log(`🔧 Debug mode will be ${enabled ? 'ON' : 'OFF'} after page reload`);
    }
};

// 전역으로 노출
window.Logger = Logger;

// 초기 상태 표시
console.log(`%c🔧 Logger Initialized`, 'font-weight: bold; color: #4CAF50;');
console.log(`   Debug mode: ${Logger.DEBUG ? '✅ ON' : '❌ OFF'}`);
console.log(`   Toggle: Logger.toggleDebug()`);
