// utils.js - Formatting and helper functions

// 통화 포맷
function formatCurrency(value) {
    if (value === null || value === undefined) return '0원';
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// 숫자 포맷
function formatNumber(value) {
    if (value === null || value === undefined) return '0';
    return new Intl.NumberFormat('ko-KR').format(value);
}

// 퍼센트 포맷
function formatPercent(value) {
    if (value === null || value === undefined) return '0.00%';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
}

// 뉴스 텍스트 포맷팅 함수
function formatNewsText(text) {
    if (!text) return '';

    // 0. Pre-process: Split embedded titles into new lines
    // Look for " * **" or " * [" patterns and replace with newline
    let processedText = text.replace(/\s+[\*•]\s+(?=\*\*|\[)/g, '\n');

    // Split into lines
    const lines = processedText.split('\n');
    let html = '';

    lines.forEach(line => {
        line = line.trim();
        if (!line) return;

        // 1. Remove leading special chars (*, -, bullets, digits)
        let cleanLine = line.replace(/^[-*•\d\.]+\s*/, '');

        // 2. Identify Title and Body
        let title = '';
        let body = '';

        // Check for **Title**
        const boldMatch = cleanLine.match(/\*\*(.*?)\*\*/);

        if (boldMatch) {
            title = boldMatch[1];
            // Body is everything after the bold part (and optional colon)
            body = cleanLine.replace(/\*\*.*?\*\*\s*:?\s*/, '');
        } else {
            // Check for Colon separator if no bold title found
            const colonIndex = cleanLine.indexOf(':');
            if (colonIndex > -1 && colonIndex < 50) {
                title = cleanLine.substring(0, colonIndex);
                body = cleanLine.substring(colonIndex + 1);
            } else {
                // Fallback: Check for [Keyword] at start
                if (cleanLine.startsWith('[')) {
                    const bracketEnd = cleanLine.indexOf(']');
                    if (bracketEnd > -1) {
                        title = cleanLine.substring(0, bracketEnd + 1);
                        body = cleanLine.substring(bracketEnd + 1);
                    }
                }

                if (!title) {
                    body = cleanLine;
                }
            }
        }

        // 3. Clean Title (remove [ ] if present inside, per user request to remove special chars)
        if (title) {
            title = title.replace(/[\[\]]/g, '').trim();
            // Also remove any leading/trailing * just in case
            title = title.replace(/^\*+|\*+$/g, '').trim();
        }

        // 4. Clean Body (remove leading * or : if any)
        if (body) {
            body = body.replace(/^\s*[:*]\s*/, '').trim();
        }

        // 5. Construct HTML
        if (title) {
            html += `
                <div class="news-item">
                    <span class="news-title">${title}</span>
                    <div class="news-body">${body}</div>
                </div>`;
        } else {
            // Just body
            html += `
                <div class="news-item">
                    <div class="news-body">${body}</div>
                </div>`;
        }
    });

    return html;
}

// AI 분석 텍스트 포맷팅
function formatAIText(text) {
    if (!text) return '';

    // 1. **Bold** 처리 -> 색상 및 줄바꿈 적용
    // 앞뒤 줄바꿈을 위해 block 요소로 만들거나 margin을 줌
    let formatted = text.replace(/\*\*(.*?)\*\*/g, (match, p1) => {
        return `<div style="color: #93c5fd; font-weight: 700; font-size: 1.05em; margin-top: 1.2rem; margin-bottom: 0.5rem;">${p1}</div>`;
    });

    // 2. - (하이픈)으로 시작하는 리스트 아이템 처리
    formatted = formatted.replace(/^- /gm, '• ');

    // 3. 줄바꿈을 <br>로 변환 (div에서 사용할 경우)
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}
