# Bollinger Bands R&D: Visualization & AI Data

## 1. Visualization Best Practices (UI/UX)

To effectively visualize Bollinger Bands for users, the following practices are recommended:

### A. Visual Components
1.  **Three Lines:**
    *   **Middle Band (SMA 20):** Solid line, distinct color (e.g., Orange or Blue). Represents the trend.
    *   **Upper & Lower Bands:** Dashed or thinner solid lines, same color but potentially lighter.
2.  **Channel Fill (Cloud):**
    *   Fill the area between the Upper and Lower bands with a translucent color (e.g., 10-20% opacity).
    *   This helps users instantly perceive the "volatility channel" and identify squeezes (narrowing) or expansions (widening).
3.  **Squeeze Indicator:**
    *   When the bandwidth is historically low (Squeeze), change the fill color (e.g., to Grey or Red) or add visual markers (dots) on the bands.
    *   This highlights potential breakout zones.

### B. Interaction
1.  **Tooltips:** Hovering over a specific date should show the exact values for Upper, Lower, and SMA.
2.  **Toggle:** Users should be able to toggle the bands on/off to declutter the chart.

## 2. AI Dataset & Feature Engineering

For an AI (LLM) to effectively analyze Bollinger Bands without "seeing" the chart, we need to provide derived features that capture the shape and state of the bands.

### Key Features to Extract
1.  **%B (Percent B):**
    *   **Formula:** `(Price - Lower Band) / (Upper Band - Lower Band)`
    *   **Interpretation:**
        *   `> 1.0`: Price is above the upper band (Strong uptrend or Overbought).
        *   `< 0.0`: Price is below the lower band (Strong downtrend or Oversold).
        *   `0.5`: Price is at the Middle Band (SMA).
    *   **AI Usage:** Determines the immediate position of the price relative to the bands.

2.  **Bandwidth (Volatility):**
    *   **Formula:** `(Upper Band - Lower Band) / Middle Band`
    *   **Interpretation:**
        *   High value: High volatility.
        *   Low value: Low volatility (Squeeze).
    *   **AI Usage:** Identifies market state (Consolidation vs. Expansion).

3.  **Squeeze Status:**
    *   **Logic:** Is current Bandwidth < Minimum Bandwidth of the last N periods (e.g., 120 days)?
    *   **AI Usage:** Critical signal for potential explosive moves (Breakouts).

4.  **Trend (SMA Slope):**
    *   **Logic:** Is the Middle Band rising or falling compared to N days ago?
    *   **AI Usage:** Identifies the prevailing trend direction.

### Proposed AI Context Format
To provide temporal context (trends, momentum), we must include a short history, not just the latest state.

```json
{
  "date": "2023-10-27",
  "price": 67000,
  "bollinger_summary": {
    "percent_b": 0.85,
    "bandwidth": 0.05,
    "is_squeeze": true,
    "trend": "upward"
  },
  "recent_history": [
    {"date": "10-23", "price": 66000, "percent_b": 0.60, "bandwidth": 0.06},
    {"date": "10-24", "price": 66500, "percent_b": 0.70, "bandwidth": 0.05},
    {"date": "10-25", "price": 66800, "percent_b": 0.80, "bandwidth": 0.05},
    {"date": "10-26", "price": 67000, "percent_b": 0.85, "bandwidth": 0.05}
  ]
}
```

### Why History Matters?
- **Momentum:** Is %B increasing rapidly? (Strong momentum)
- **Squeeze Duration:** How long has the bandwidth been low? (Longer squeeze = potentially stronger breakout)
- **Pattern Recognition:** Did it recently reject off the Upper Band?

## 3. Prototype Result
I have created a prototype (`test_bollinger_chart.html`) using Chart.js to verify the visualization strategy.

### Screenshot
![Bollinger Bands Prototype](/C:/Users/bak12/.gemini/antigravity/brain/b08da0f9-dda8-4d6e-b75a-3131c5a62c9a/bollinger_chart_fixed_1764713467924.png)

### Key Visual Features Verified:
1.  **Cloud Effect:** The area between Upper and Lower bands is filled with `rgba(0, 255, 255, 0.1)`, making the volatility channel instantly visible.
2.  **Squeeze Indicators:** Red dots appear on the middle line when the bandwidth is at a historical low (Squeeze), signaling potential breakouts.
3.  **Distinct Lines:**
    *   **Middle (Orange):** Clearly shows the trend direction.
    *   **Outer (Cyan):** Define the volatility boundaries.

## 4. Data Requirements
To effectively calculate and analyze Bollinger Bands (especially for Squeeze detection), the following data history is required:

| Purpose | Required Days | Reason |
| :--- | :--- | :--- |
| **Basic Calculation** | **20 Days** | Standard Bollinger Bands use a 20-day Moving Average (SMA 20). |
| **Squeeze Detection** | **120 Days** | To identify a "true squeeze," we compare current volatility to the **6-month (120 trading days) low**. |
| **Trend Context** | **120+ Days** | AI needs to see if the trend is long-term or just a short correction. |

**Recommendation:** Fetch **120 days (approx. 6 months)** of daily data minimum.
