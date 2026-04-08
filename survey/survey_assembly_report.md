# Survey Assembly Report

Generated: 2026-04-08 23:09:54

---

## Overview

This report documents the assembly of survey materials for the thesis *"Influence of External Information Shocks on Equity Portfolio Manager Decision-Making"* (Executive MBA, Swiss Business School). The survey presents equity portfolio managers with real-world financial event scenarios and asks them to indicate their intended risk stance -- whether they would increase, maintain, or reduce exposure to the affected stock. Each scenario is based on an actual news event for an S&P 500 stock and is accompanied by a trailing price chart. In treatment conditions, respondents also see a **Shock Score dashboard** -- a quantitative decision-support tool that summarises the event's intensity across multiple dimensions.

The survey uses a **within-subject quasi-experimental design**: each respondent sees 8 scenarios (4 control, 4 treatment), with treatment assignment counterbalanced across form versions so that every scenario appears as both control and treatment across the full sample.

---

## 1. Scenario Counts

- **Total scenarios:** 24 *(reduced from 36 by SURVEY-05)*
- Block 1: 8 scenarios
- Block 2: 8 scenarios
- Block 3: 8 scenarios

Each respondent completes one block (8 scenarios). Three blocks exist so that a larger pool of events can be tested while keeping individual survey length manageable. Scenarios were reduced from 12 to 8 per block per mentor feedback (SURVEY-05); selection criteria: SC_total spread (2 low + 2 high + 4 middle), sector non-repetition, direction balance, and event-type diversity.

### Sector Coverage

The 24 retained scenarios span **10 GICS sectors**:

| GICS Sector | Count | Tickers | Note |
|---|---|---|---|
| Consumer Discretionary | 3 | DIS, LOW, MCD | |
| Consumer Staples | 3 | COST, PG, WMT | B2: WMT+COST duplicate (unavoidable — only 2 pos. scenarios in block) |
| Energy | 3 | COP, CVX, XOM | B3: COP+CVX duplicate (needed for ≥3 positive scenarios) |
| Health Care | 2 | MRK, UNH | |
| Industrials | 2 | CAT, HON | B1: duplicate (7 distinct sectors across 12 → forced) |
| Information Technology | 3 | AMAT, ORCL, QCOM | |
| Materials | 2 | LIN, SHW | |
| Real Estate | 2 | AMT, PLD | |
| Financials | 2 | GS, V | |
| Utilities | 1 | NEE | |

**Dropped scenarios (12 total):** APD, NFLX, GE, TMUS (Block 1); BAC, HD, JNJ, SO (Block 2); JPM, KO, VZ, PFE (Block 3).

### Event-Type Distribution

Each scenario is classified by the type of news event that triggered the information shock:

| Event Type | Count | Share |
|---|---|---|
| Earnings | 16 | 66.7% |
| Analyst | 5 | 20.8% |
| Management | 2 | 8.3% |
| Regulatory | 1 | 4.2% |

Each block contains all 3+ event types: analyst, earnings, management/regulatory.

### Event Date Range

- **Earliest event:** 2025-03-13 (PLD)
- **Latest event:** 2026-03-09 (XOM)
- Span: approximately 12 months of real market events

---

## 2. Glossary of Measures

Before interpreting the statistics below, the following definitions describe each measure used in the Shock Score (SC_total) construction and the scenario metadata.

### Raw Component Measures

| Measure | Full Name | Definition |
|---|---|---|
| **AC_raw** | Article Count | Number of news articles published within the 30-minute bar in which the event occurs. Higher values indicate broader media coverage of the event. |
| **SE_raw** | Sentiment Extremity | Maximum absolute FinBERT sentiment score across all articles on the event day. Ranges from 0 (neutral) to 1 (extreme positive or negative). Captures the emotional intensity of the news, regardless of direction. |
| **AI_raw** | Attention Intensity | Trading volume in the 30-minute event bar divided by the 60-trading-day trailing average of 30-minute bar volume. Values above 1.0 indicate abnormally high trading activity. |
| **ES_raw** | Event-Type Severity | Category-level severity ratio: the historical return volatility of the event category (e.g., earnings) divided by the overall return volatility across all categories. Higher values indicate event types that historically cause larger price moves. |

### Z-Standardised Components

Each raw component is z-standardised (mean = 0, std = 1) across all 36 scenarios before entering PCA. In the shock score file, these appear as `ac_z`, `se_z`, `ai_z`, `es_z`.

### Composite Score

| Measure | Definition |
|---|---|
| **SC_total** | The composite **Shock Score**. Computed as the first principal component (PC1) of the four z-standardised components. A single number summarising overall shock intensity. Higher values = more intense shocks (more articles, more extreme sentiment, higher abnormal volume, more severe event type). |

### Dashboard Signals

These are derived from SC_total and its components to populate the visual Shock Score dashboard shown to treatment-group respondents:

| Signal | Definition |
|---|---|
| **sentiment_direction** | Qualitative label for the dominant sentiment of event-day news (e.g., "Strongly Negative", "Neutral", "Mildly Positive"). Based on the FinBERT positive-minus-negative probability score. |
| **severity_level** | Categorical shock intensity bucket: **Low** (bottom third of SC_total), **Medium** (middle third), **High** (top third). |
| **horizon_bucket** | Estimated persistence of the price impact: "Intraday", "Several Days", or "Several Weeks". Derived from 5-day post-event return decay. |
| **protocol_recommendation** | Rules-based pre-commitment action triggered by shock intensity: **Standard Process** (below 60th percentile of SC_total), **Enhanced Review** (60th--85th percentile), or **Cooling-Off and Second Review** (above 85th percentile). |

---

## 3. PCA Results -- SC_total Construction

Principal Component Analysis was applied to the four z-standardised shock components across all 36 scenarios. The first principal component (PC1) is retained as SC_total.

- **PC1 explained variance: 0.5925 (59.2%)**

This means PC1 captures nearly 59% of the total variation across the four components -- a strong single-factor summary.

- **Loadings (w_1):**

| Component | Loading | Interpretation |
|---|---|---|
| AC (Article Count) | **0.5787** | Media coverage breadth |
| AI (Attention Intensity) | **0.5553** | Abnormal trading volume |
| SE (Sentiment Extremity) | **0.4720** | Emotional intensity of news |
| ES (Event-Type Severity) | **0.3659** | Historical category volatility |

All four loadings are positive, confirming that SC_total increases when any dimension of shock intensity increases.

---

## 4. SC_total Distribution (All 36 Scenarios)

| Statistic | Value |
|-----------|-------|
| Mean      | -0.0000 |
| Std       | 1.5613 |
| Min       | -2.4272 |
| Q1        | -1.0005 |
| Median    | -0.0933 |
| Q3        | 0.7904 |
| Max       | 4.9518 |
| Skewness  | 0.93 (positive -- right tail from high-intensity outliers) |

The distribution is centred near zero (by construction, since PCA operates on z-standardised inputs) but right-skewed: a small number of scenarios have very high shock scores.

### Extreme Scenarios

| Rank | Scenario | Ticker | SC_total | Key Drivers |
|---|---|---|---|---|
| Highest | B3_S11 | UNH | **4.9518** | 35 articles, volume 11.7x normal |
| 2nd highest | B2_S09 | DIS | **2.8193** | 24 articles, volume 6.4x normal |
| 3rd highest | B2_S02 | HD | **2.2470** | 23 articles, volume 4.3x normal |
| Lowest | B1_S01 | SHW | **-2.4272** | 1 article, sentiment 0.14 |
| 2nd lowest | B3_S05 | PG | **-2.1403** | 2 articles, sentiment 0.16 |

### SC_total by Severity Bucket

Scenarios are split into terciles to create the severity_level dashboard signal:

| Bucket | n | Mean SC_total | Range |
|--------|---|---------------|-------|
| **Low** | 12 | -1.5598 | [-2.4272, -0.6485] |
| **Medium** | 12 | -0.1353 | [-0.4073, 0.2480] |
| **High** | 12 | 1.6952 | [0.4424, 4.9518] |

### SC_total by Block (retained 8 scenarios)

| Block | n | SC_total range | Retained |
|-------|---|----------------|---------|
| Block 1 | 8 | -2.4272 to +1.2227 | SHW, V, AMT, T, QCOM, MCD, CAT, HON |
| Block 2 | 8 | -1.8975 to +2.8193 | MRK, GS, PLD, XOM, DIS, COST, WMT, AMAT |
| Block 3 | 8 | -2.1403 to +4.9518 | ORCL, LIN, COP, PG, NEE, LOW, UNH, CVX |

*Note: SC_total values were computed from the original 36-scenario PCA; they are unchanged by the scenario reduction.*

### Protocol Distribution

The protocol recommendation is a rules-based action tier triggered by the scenario's shock intensity:

| Protocol | SC_total Threshold | Count | Share |
|---|---|---|---|
| Standard Process | Below 60th percentile | 21 | 58.3% |
| Enhanced Review | 60th--85th percentile | 9 | 25.0% |
| Cooling-Off and Second Review | Above 85th percentile | 6 | 16.7% |

---

## 5. Raw Component Descriptive Statistics

### AC_raw (Article Count)

| Statistic | Value |
|-----------|-------|
| Mean | 6.7 |
| Median | 3.0 |
| Std | 8.1 |
| Min | 1 |
| Max | 35 (UNH) |

Most events have 1--3 articles; a few high-profile events have 20+.

### SE_raw (Sentiment Extremity)

| Statistic | Value |
|-----------|-------|
| Mean | 0.6799 |
| Median | 0.8434 |
| Min | 0.0091 |
| Max | 0.9655 |

Most events carry strongly non-neutral sentiment (median 0.84). A few events have notably low sentiment extremity.

### AI_raw (Attention Intensity)

| Statistic | Value |
|-----------|-------|
| Mean | 2.72 |
| Median | 1.96 |
| Min | 0.56 |
| Max | 11.73 (UNH) |

A value of 1.0 means normal volume. The median of 1.96 means the typical event-bar volume is roughly 96% above its trailing average.

### ES_raw (Event-Type Severity)

| Value | Count |
|-------|-------|
| 0.6 | 7 |
| 0.8 | 5 |
| 1.0 | 23 |
| 1.1 | 1 |

Most scenarios map to the baseline severity (1.0). This component is currently based on a placeholder severity mapping and requires manual review.

---

## 6. Price Reaction Statistics

Each scenario records the immediate price reaction in the 2-hour window following the event.

| Statistic | Value |
|-----------|-------|
| Mean | +0.96% |
| Median | +1.26% |
| Std | 4.14% |
| Min | -13.11% |
| Max | +12.73% |
| Positive reactions | 21 (58.3%) |
| Negative reactions | 15 (41.7%) |

### Largest Price Reactions

| Scenario | Ticker | Reaction | Direction |
|---|---|---|---|
| B1_S11 | CAT | +12.73% | Up |
| B1_S06 | GE | +9.73% | Up |
| B3_S12 | CVX | +5.46% | Up |
| B2_S12 | AMAT | -13.11% | Down |
| B1_S12 | HON | -5.47% | Down |
| B2_S06 | PLD | -2.32% | Down |

### Price Reaction by Severity Level

| Severity | Mean Reaction | Std |
|---|---|---|
| Low | +0.99% | 2.06% |
| Medium | +1.61% | 3.44% |
| High | +0.28% | 6.12% |

High-severity scenarios show the widest dispersion in price reactions, consistent with the interpretation that intense shocks create uncertainty rather than a uniform directional move.

---

## 7. Sentiment Direction Distribution

| Sentiment Label | Count | Share |
|---|---|---|
| Strongly Negative | 1 | 2.8% |
| Negative | 7 | 19.4% |
| Mildly Negative | 6 | 16.7% |
| Neutral | 12 | 33.3% |
| Mildly Positive | 4 | 11.1% |
| Positive | 2 | 5.6% |
| Strongly Positive | 4 | 11.1% |

Negative-leaning sentiment accounts for 38.9% of scenarios; positive-leaning for 27.8%.

---

## 8. Counterbalancing Design

*(Rebuilt for 8-scenario blocks per SURVEY-05)*

- **Form versions per block:** 2 (V1, V2)
- **Total form versions:** 6 (2 per block × 3 blocks)
- **Scenarios per form:** 8 (4 treatment, 4 control)
- **Group A:** scenario_ids ranked 1–4 (by scenario_id sort order within block)
- **Group B:** scenario_ids ranked 5–8
- **V1:** Group A = ShowSC=1, Group B = ShowSC=0; interleaved A-B order (A1, B1, A2, B2, …)
- **V2:** Group A = ShowSC=0, Group B = ShowSC=1; same interleaved order

This design ensures that:
1. Every scenario is seen with and without the Shock Score dashboard across the sample
2. No respondent sees the same scenario twice
3. Treatment and control scenarios alternate throughout the form

**Block 1 Groups:**
- Group A: B1_S01 (SHW), B1_S04 (V), B1_S05 (AMT), B1_S07 (T)
- Group B: B1_S08 (QCOM), B1_S10 (MCD), B1_S11 (CAT), B1_S12 (HON)

**Block 2 Groups:**
- Group A: B2_S03 (MRK), B2_S05 (GS), B2_S06 (PLD), B2_S08 (XOM)
- Group B: B2_S09 (DIS), B2_S10 (COST), B2_S11 (WMT), B2_S12 (AMAT)

**Block 3 Groups:**
- Group A: B3_S02 (ORCL), B3_S03 (LIN), B3_S04 (COP), B3_S05 (PG)
- Group B: B3_S09 (NEE), B3_S10 (LOW), B3_S11 (UNH), B3_S12 (CVX)

---

## 9. Notes and Caveats

### 9a. ES_raw (Event-Type Severity)
Uses a placeholder category-level severity mapping (see `EVENT_TYPE_SEVERITY` in `3_survey_assembly.py`). **Requires manual review** against actual event characteristics before finalising SC_total for the thesis.

### 9b. Sentiment Scoring
Scores use **FinBERT** (`ProsusAI/finbert`) via HuggingFace Transformers. The sentiment score is `positive_prob - negative_prob` in [-1, 1]. See `toolkits/news_sentiment_toolkit.py` for the shared scorer.

### 9c. Persistence Horizon
`horizon_bucket` requires 5-day post-event return data and is currently set to `[REQUIRES POST-EVENT DATA]` for some scenarios. Extend price data coverage and re-run the script if needed.

### 9d. Summary Paragraphs
ANTHROPIC_API_KEY was set -- summary paragraphs were auto-generated via Claude (claude-sonnet-4-6). Review each paragraph before use.

---

## 10. Warnings
- No warnings.

---

## 11. Generated File Manifest

### Charts (trailing price chart PNGs)
Each chart shows the stock's 90-day trailing price history up to the event, giving respondents visual context for the stock's recent trajectory.

- `survey/charts\chart_B1_S01.png` (179.3 KB)
- `survey/charts\chart_B1_S02.png` (180.8 KB)
- `survey/charts\chart_B1_S03.png` (180.0 KB)
- `survey/charts\chart_B1_S04.png` (172.3 KB)
- `survey/charts\chart_B1_S05.png` (168.4 KB)
- `survey/charts\chart_B1_S06.png` (191.9 KB)
- `survey/charts\chart_B1_S07.png` (177.0 KB)
- `survey/charts\chart_B1_S08.png` (175.0 KB)
- `survey/charts\chart_B1_S09.png` (169.4 KB)
- `survey/charts\chart_B1_S10.png` (167.7 KB)
- `survey/charts\chart_B1_S11.png` (160.8 KB)
- `survey/charts\chart_B1_S12.png` (167.9 KB)
- `survey/charts\chart_B2_S01.png` (189.8 KB)
- `survey/charts\chart_B2_S02.png` (179.0 KB)
- `survey/charts\chart_B2_S03.png` (173.6 KB)
- `survey/charts\chart_B2_S04.png` (188.0 KB)
- `survey/charts\chart_B2_S05.png` (188.0 KB)
- `survey/charts\chart_B2_S06.png` (170.2 KB)
- `survey/charts\chart_B2_S07.png` (181.5 KB)
- `survey/charts\chart_B2_S08.png` (180.8 KB)
- `survey/charts\chart_B2_S09.png` (168.4 KB)
- `survey/charts\chart_B2_S10.png` (176.0 KB)
- `survey/charts\chart_B2_S11.png` (188.4 KB)
- `survey/charts\chart_B2_S12.png` (165.2 KB)
- `survey/charts\chart_B3_S01.png` (180.1 KB)
- `survey/charts\chart_B3_S02.png` (183.1 KB)
- `survey/charts\chart_B3_S03.png` (167.6 KB)
- `survey/charts\chart_B3_S04.png` (175.3 KB)
- `survey/charts\chart_B3_S05.png` (190.1 KB)
- `survey/charts\chart_B3_S06.png` (188.7 KB)
- `survey/charts\chart_B3_S07.png` (172.2 KB)
- `survey/charts\chart_B3_S08.png` (169.6 KB)
- `survey/charts\chart_B3_S09.png` (167.8 KB)
- `survey/charts\chart_B3_S10.png` (179.3 KB)
- `survey/charts\chart_B3_S11.png` (162.0 KB)
- `survey/charts\chart_B3_S12.png` (166.6 KB)

### Dashboards (Shock Score dashboard PNGs)
Each dashboard visualises the four Shock Score signals (sentiment direction, severity level, horizon bucket, protocol recommendation) for one scenario. Shown only to treatment-group respondents.

- `survey/dashboards\dashboard_B1_S01.png` (26.8 KB)
- `survey/dashboards\dashboard_B1_S02.png` (27.9 KB)
- `survey/dashboards\dashboard_B1_S03.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S04.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S05.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S06.png` (28.7 KB)
- `survey/dashboards\dashboard_B1_S07.png` (28.6 KB)
- `survey/dashboards\dashboard_B1_S08.png` (26.7 KB)
- `survey/dashboards\dashboard_B1_S09.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S10.png` (26.3 KB)
- `survey/dashboards\dashboard_B1_S11.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S12.png` (26.3 KB)
- `survey/dashboards\dashboard_B2_S01.png` (28.7 KB)
- `survey/dashboards\dashboard_B2_S02.png` (29.0 KB)
- `survey/dashboards\dashboard_B2_S03.png` (26.9 KB)
- `survey/dashboards\dashboard_B2_S04.png` (25.6 KB)
- `survey/dashboards\dashboard_B2_S05.png` (25.2 KB)
- `survey/dashboards\dashboard_B2_S06.png` (28.3 KB)
- `survey/dashboards\dashboard_B2_S07.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S08.png` (27.5 KB)
- `survey/dashboards\dashboard_B2_S09.png` (29.0 KB)
- `survey/dashboards\dashboard_B2_S10.png` (27.2 KB)
- `survey/dashboards\dashboard_B2_S11.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S12.png` (28.3 KB)
- `survey/dashboards\dashboard_B3_S01.png` (26.7 KB)
- `survey/dashboards\dashboard_B3_S02.png` (26.4 KB)
- `survey/dashboards\dashboard_B3_S03.png` (29.0 KB)
- `survey/dashboards\dashboard_B3_S04.png` (28.4 KB)
- `survey/dashboards\dashboard_B3_S05.png` (26.7 KB)
- `survey/dashboards\dashboard_B3_S06.png` (26.7 KB)
- `survey/dashboards\dashboard_B3_S07.png` (28.3 KB)
- `survey/dashboards\dashboard_B3_S08.png` (27.5 KB)
- `survey/dashboards\dashboard_B3_S09.png` (27.5 KB)
- `survey/dashboards\dashboard_B3_S10.png` (28.4 KB)
- `survey/dashboards\dashboard_B3_S11.png` (28.7 KB)
- `survey/dashboards\dashboard_B3_S12.png` (28.0 KB)

### Counterbalancing Files
- `survey/counterbalancing\counterbalancing_matrix.csv` (3.5 KB)
- `survey/counterbalancing\form_assembly_guide.csv` (4.5 KB)

### Metadata Files
- `survey/metadata\scenario_metadata.csv` (2.6 KB)
- `survey/metadata\scenario_news_text.csv` (29.8 KB)
- `survey/metadata\scenario_price_reaction.csv` (2.5 KB)
- `survey/metadata\scenario_shock_score.csv` (5.0 KB)

---

## 12. Completion Checklist

- [x] `scenario_metadata.csv`
- [x] `scenario_news_text.csv`
- [x] `scenario_price_reaction.csv`
- [x] `scenario_shock_score.csv`
- [x] Price charts: 36/36 (24 retained; 12 dropped scenarios' charts remain on disk but are no longer referenced)
- [x] Dashboard images: 36/36 (same — 24 active)
- [x] `counterbalancing_matrix.csv`
- [x] `form_assembly_guide.csv`