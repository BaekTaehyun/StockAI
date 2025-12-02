# Bollinger Bands Integration Plan

## Goal
Integrate Bollinger Bands into the stock monitoring dashboard to provide volatility analysis (Squeeze detection) for both the user (Visualization) and the AI (Analysis).

## 1. Backend & Data Strategy (Python)
**Objective:** Efficiently fetch and serve 120 days of daily chart data.

-   **Data Fetching (`kis_api.py`):**
    -   Ensure `get_daily_chart_data` fetches at least **120 records** (currently it seems to fetch a default amount, likely sufficient, but needs verification).
    -   *Optimization:* If the API allows, request exactly 120-150 days to minimize overhead.

-   **Data Processing (`stock_analysis_service.py`):**
    -   Implement the `calculate_bollinger_features` logic (from R&D) into the service.
    -   Calculate: SMA 20, Upper/Lower Bands, %B, Bandwidth, Squeeze status.

-   **Server-Side Caching:**
    -   **Strategy:** Cache the processed Bollinger data for **1 day** (or until next market open).
    -   **Why:** Daily chart data does not change during the day (for closed markets) or changes slowly.
    -   **Implementation:** Use a simple in-memory cache (dictionary) with a timestamp or integrate with the existing caching mechanism.

## 2. AI Integration (Gemini)
**Objective:** Enable AI to recognize trends and squeezes using the 120-day context.

-   **Prompt Engineering (`prompts.py`):**
    -   Update `OUTLOOK_GENERATION_PROMPT` to accept the new JSON structure.
    -   Add instructions to analyze "Volatility Squeeze" and "Momentum" based on the provided history.

-   **Context Generation (`gemini_service.py`):**
    -   Update `generate_outlook` to call the Bollinger calculation logic.
    -   Format the output to include:
        1.  **Summary:** Current %B, Bandwidth, Squeeze Status.
        2.  **History:** Last 5-10 days of data (Price, %B, Bandwidth) for trend analysis.

## 3. Frontend Visualization (JavaScript/Chart.js)
**Objective:** Fast, interactive rendering with client-side caching.

-   **API Endpoint:**
    -   Reuse `/api/stock/{code}/daily` or create a dedicated `/api/stock/{code}/technical` if the payload is too large.
    -   *Recommendation:* Embed technical data in the main analysis response to reduce HTTP requests.

-   **Client-Side Caching (`api.js`):**
    -   **Storage:** Use `sessionStorage` to store the technical data for each stock.
    -   **Key:** `stock_tech_{code}_{date}`.
    -   **Logic:** Check cache before fetching. If valid, render immediately.

-   **UI Implementation (`ui_details.js` & `Charts.js`):**
    -   **Location:** "Technical Analysis" (기술적 분석) tab.
    -   **Rendering:** Use the Chart.js logic from the prototype (`test_bollinger_chart.html`).
    -   **Features:** Toggle button for Bands, Tooltips showing values.

## 4. Execution Roadmap

### Phase 1: Core Logic & Data
- [ ] Update `kis_api.py` to guarantee 120 days data.
- [ ] Implement `calculate_bollinger_features` in `stock_analysis_service.py`.
- [ ] Create/Update API endpoint to return this data.

### Phase 2: AI Integration
- [ ] Update `prompts.py` with Bollinger instructions.
- [ ] Update `gemini_service.py` to inject Bollinger context.

### Phase 3: Frontend & Visualization
- [ ] Update `api.js` with client-side caching for technical data.
- [ ] Implement Chart.js rendering in `ui_details.js` (using prototype code).
- [ ] Add "Bollinger Bands" toggle in the UI.

### Phase 4: Verification
- [ ] Verify AI mentions "Squeeze" or "Volatility" in its analysis.
- [ ] Verify Chart renders correctly and loads instantly on second view (Cache hit).
