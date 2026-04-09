# Survey Assembly Report

Generated: 2026-04-09 23:22:14

---

## Overview

This report documents the assembly of survey materials for the thesis *"Influence of External Information Shocks on Equity Portfolio Manager Decision-Making"* (Executive MBA, Swiss Business School). The survey presents equity portfolio managers with real-world financial event scenarios and asks them to indicate their intended risk stance -- whether they would increase, maintain, or reduce exposure to the affected stock. Each scenario is based on an actual news event for an S&P 500 stock and is accompanied by a trailing price chart. In treatment conditions, respondents also see a **Shock Score dashboard** -- a quantitative decision-support tool that summarises the event's intensity across multiple dimensions.

The survey uses a **within-subject quasi-experimental design**: each respondent sees 8 scenarios (4 control, 4 treatment), with treatment assignment counterbalanced across form versions so that every scenario appears as both control and treatment across the full sample.

---

## 1. Scenario Counts

- **Total scenarios:** 24
- Block 1: 8 scenarios
- Block 2: 8 scenarios
- Block 3: 8 scenarios

Each respondent completes one block (8 scenarios). Three blocks exist so that a larger pool of events can be tested while keeping individual survey length manageable.

### Sector Coverage

The 24 scenarios span **10 GICS sectors**, ensuring broad industry representation:

| GICS Sector | Count | Tickers |
|---|---|---|
| Health Care | 4 | JNJ, MRK, PFE, UNH |
| Consumer Staples | 3 | KO, PG, WMT |
| Information Technology | 3 | AMAT, ORCL, QCOM |
| Communication Services | 2 | NFLX, T |
| Consumer Discretionary | 2 | HD, MCD |
| Energy | 2 | COP, CVX |
| Financials | 2 | BAC, JPM |
| Industrials | 2 | CAT, GE |
| Materials | 2 | APD, LIN |
| Real Estate | 2 | AMT, PLD |

### Event-Type Distribution

Each scenario is classified by the type of news event that triggered the information shock:

| Event Type | Count | Share |
|---|---|---|
| Earnings | 10 | 41.7% |
| Analyst | 8 | 33.3% |
| Management | 6 | 25.0% |

Earnings events dominate, reflecting their real-world prevalence as the most common source of significant information shocks for S&P 500 stocks.

### Event Date Range

- **Earliest event:** 2025-03-04 (PG)
- **Latest event:** 2026-02-11 (ORCL)
- Span: approximately 11 months of real market events

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

Each raw component is z-standardised (mean = 0, std = 1) across all 24 scenarios before entering PCA. In the shock score file, these appear as `ac_z`, `se_z`, `ai_z`, `es_z`.

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

Principal Component Analysis was applied to the four z-standardised shock components across all 24 scenarios. The first principal component (PC1) is retained as SC_total.

- **PC1 explained variance: 0.4827 (48.3%)**

This means PC1 captures nearly 48% of the total variation across the four components -- a strong single-factor summary.

- **Loadings (w_1):**

| Component | Loading | Interpretation |
|---|---|---|
| AC (Article Count) | **0.6602** | Media coverage breadth |
| AI (Attention Intensity) | **0.5818** | Abnormal trading volume |
| SE (Sentiment Extremity) | **0.4682** | Emotional intensity of news |
| ES (Event-Type Severity) | **0.0797** | Historical category volatility |

All four loadings are positive, confirming that SC_total increases when any dimension of shock intensity increases.

---

## 4. SC_total Distribution (All 24 Scenarios)

| Statistic | Value |
|-----------|-------|
| Mean      | -0.0000 |
| Std       | 1.4194 |
| Min       | -1.7372 |
| Q1        | -0.8675 |
| Median    | -0.3286 |
| Q3        | 0.8873 |
| Max       | 4.3677 |
| Skewness  | 1.40 (positive -- right tail from high-intensity outliers) |

The distribution is centred near zero (by construction, since PCA operates on z-standardised inputs) but right-skewed: a small number of scenarios have very high shock scores.

### Extreme Scenarios

| Rank | Scenario | Ticker | SC_total | Key Drivers |
|---|---|---|---|---|
| Highest | B3_S08 | AMAT | **4.3677** | 22 articles, volume 7.4x normal |
| 2nd highest | B1_S05 | HD | **2.2601** | 18 articles, volume 3.0x normal |
| 3rd highest | B3_S07 | MCD | **1.5427** | 12 articles, volume 2.9x normal |
| Lowest | B2_S06 | KO | **-1.7372** | 3 articles, sentiment 0.08 |
| 2nd lowest | B1_S08 | QCOM | **-1.7047** | 1 article, sentiment 0.01 |

### SC_total by Severity Bucket

Scenarios are split into terciles to create the severity_level dashboard signal:

| Bucket | n | Mean SC_total | Range |
|--------|---|---------------|-------|
| **Low** | 8 | -1.2504 | [-1.7372, -0.8495] |
| **Medium** | 8 | -0.3406 | [-0.6429, 0.0106] |
| **High** | 8 | 1.5910 | [0.1847, 4.3677] |

### SC_total by Block

| Block | n | Mean | Std | Min | Max |
|-------|---|------|-----|-----|-----|
| Block 1 | 8 | -0.4772 | 1.2256 | -1.7047 | 2.2601 |
| Block 2 | 8 | -0.1092 | 1.0353 | -1.7372 | 1.0789 |
| Block 3 | 8 | 0.5864 | 1.8382 | -1.5064 | 4.3677 |

### Protocol Distribution

The protocol recommendation is a rules-based action tier triggered by the scenario's shock intensity:

| Protocol | SC_total Threshold | Count | Share |
|---|---|---|---|
| Standard Process | Below 60th percentile | 14 | 58.3% |
| Enhanced Review | 60th--85th percentile | 6 | 25.0% |
| Cooling-Off and Second Review | Above 85th percentile | 4 | 16.7% |

---

## 5. Raw Component Descriptive Statistics

### AC_raw (Article Count)

| Statistic | Value |
|-----------|-------|
| Mean | 5.5 |
| Median | 3.0 |
| Std | 5.8 |
| Min | 1 |
| Max | 22 (AMAT) |

Most events have 1--3 articles; a few high-profile events have 20+.

### SE_raw (Sentiment Extremity)

| Statistic | Value |
|-----------|-------|
| Mean | 0.6819 |
| Median | 0.9144 |
| Min | 0.0094 |
| Max | 0.9660 |

Most events carry strongly non-neutral sentiment (median 0.91). A few events have notably low sentiment extremity.

### AI_raw (Attention Intensity)

| Statistic | Value |
|-----------|-------|
| Mean | 2.12 |
| Median | 1.78 |
| Min | 0.59 |
| Max | 7.37 (AMAT) |

A value of 1.0 means normal volume. The median of 1.78 means the typical event-bar volume is roughly 78% above its trailing average.

### ES_raw (Event-Type Severity)

| Value | Count |
|-------|-------|
| 0.6 | 8 |
| 0.8 | 6 |
| 1.0 | 10 |

Most scenarios map to the baseline severity (1.0). This component is currently based on a placeholder severity mapping and requires manual review.

---

## 6. Price Reaction Statistics

Each scenario records the immediate price reaction in the 2-hour window following the event.

| Statistic | Value |
|-----------|-------|
| Mean | +0.33% |
| Median | -0.09% |
| Std | 4.33% |
| Min | -13.11% |
| Max | +12.73% |
| Positive reactions | 11 (45.8%) |
| Negative reactions | 13 (54.2%) |

### Largest Price Reactions

| Scenario | Ticker | Reaction | Direction |
|---|---|---|---|
| B2_S07 | CAT | +12.73% | Up |
| B1_S08 | QCOM | +4.86% | Up |
| B1_S01 | APD | +3.41% | Up |
| B3_S08 | AMAT | -13.11% | Down |
| B3_S03 | AMT | -2.45% | Down |
| B3_S05 | PLD | -2.32% | Down |

### Price Reaction by Severity Level

| Severity | Mean Reaction | Std |
|---|---|---|
| Low | +1.58% | 1.89% |
| Medium | -0.37% | 2.20% |
| High | -0.21% | 7.10% |

High-severity scenarios show the widest dispersion in price reactions, consistent with the interpretation that intense shocks create uncertainty rather than a uniform directional move.

---

## 7. Sentiment Direction Distribution

| Sentiment Label | Count | Share |
|---|---|---|
| Strongly Negative | 1 | 4.2% |
| Negative | 1 | 4.2% |
| Mildly Negative | 3 | 12.5% |
| Neutral | 7 | 29.2% |
| Mildly Positive | 5 | 20.8% |
| Positive | 4 | 16.7% |
| Strongly Positive | 3 | 12.5% |

Negative-leaning sentiment accounts for 20.8% of scenarios; positive-leaning for 50.0%.

---

## 8. Counterbalancing Design

- **Form versions per block:** 2 (V1, V2)
- **Total form versions:** 6 (2 per block x 3 blocks)
- **Scenarios per form:** 8 (4 treatment, 4 control)
- **Treatment assignment:** Each scenario appears as treatment (ShowSC = 1) in 1 of 2 versions and as control (ShowSC = 0) in the other
- **Presentation order:** Treatment and control scenarios are interleaved (alternating T-C or C-T), preventing order-based response patterns

This design ensures that:
1. Every scenario is seen with and without the Shock Score dashboard across the sample
2. No respondent sees the same scenario twice
3. Treatment and control alternate within each form

---

## 9. Notes and Caveats

### 9a. ES_raw (Event-Type Severity)
Uses a placeholder category-level severity mapping (see `EVENT_TYPE_SEVERITY` in `toolkits/event_selection_toolkit.py`). **Requires manual review** against actual event characteristics before finalising SC_total for the thesis.

### 9b. Sentiment Scoring
Scores use **FinBERT** (`ProsusAI/finbert`) via HuggingFace Transformers. The sentiment score is `positive_prob - negative_prob` in [-1, 1]. See `toolkits/news_processor_toolkit.py` for the shared scorer.

### 9c. Persistence Horizon
`horizon_bucket` requires 5-day post-event return data and is currently set to `[REQUIRES POST-EVENT DATA]` for some scenarios. Extend price data coverage and re-run the script if needed.

### 9d. Summary Paragraphs
ANTHROPIC_API_KEY was set -- summary paragraphs were auto-generated via Claude (claude-sonnet-4-20250514). Review each paragraph before use.

---

## 10. Warnings
- No warnings.

---

## 11. Generated File Manifest

### Charts (trailing price chart PNGs)
Each chart shows the stock's 90-day trailing price history up to the event, giving respondents visual context for the stock's recent trajectory.

- `survey/charts\chart_B1_S01.png` (197.6 KB)
- `survey/charts\chart_B1_S02.png` (178.7 KB)
- `survey/charts\chart_B1_S03.png` (177.7 KB)
- `survey/charts\chart_B1_S04.png` (193.0 KB)
- `survey/charts\chart_B1_S05.png` (186.9 KB)
- `survey/charts\chart_B1_S06.png` (198.5 KB)
- `survey/charts\chart_B1_S07.png` (177.0 KB)
- `survey/charts\chart_B1_S08.png` (175.0 KB)
- `survey/charts\chart_B2_S01.png` (203.1 KB)
- `survey/charts\chart_B2_S02.png` (180.1 KB)
- `survey/charts\chart_B2_S03.png` (192.6 KB)
- `survey/charts\chart_B2_S04.png` (177.5 KB)
- `survey/charts\chart_B2_S05.png` (184.9 KB)
- `survey/charts\chart_B2_S06.png` (190.0 KB)
- `survey/charts\chart_B2_S07.png` (160.8 KB)
- `survey/charts\chart_B2_S08.png` (188.4 KB)
- `survey/charts\chart_B3_S01.png` (183.1 KB)
- `survey/charts\chart_B3_S02.png` (196.6 KB)
- `survey/charts\chart_B3_S03.png` (191.3 KB)
- `survey/charts\chart_B3_S04.png` (180.0 KB)
- `survey/charts\chart_B3_S05.png` (170.2 KB)
- `survey/charts\chart_B3_S06.png` (169.6 KB)
- `survey/charts\chart_B3_S07.png` (167.7 KB)
- `survey/charts\chart_B3_S08.png` (165.2 KB)

### Dashboards (Shock Score dashboard PNGs)
Each dashboard visualises the four Shock Score signals (sentiment direction, severity level, horizon bucket, protocol recommendation) for one scenario. Shown only to treatment-group respondents.

- `survey/dashboards\dashboard_B1_S01.png` (26.8 KB)
- `survey/dashboards\dashboard_B1_S02.png` (27.2 KB)
- `survey/dashboards\dashboard_B1_S03.png` (27.2 KB)
- `survey/dashboards\dashboard_B1_S04.png` (25.7 KB)
- `survey/dashboards\dashboard_B1_S05.png` (28.0 KB)
- `survey/dashboards\dashboard_B1_S06.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S07.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S08.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S01.png` (26.3 KB)
- `survey/dashboards\dashboard_B2_S02.png` (28.7 KB)
- `survey/dashboards\dashboard_B2_S03.png` (27.5 KB)
- `survey/dashboards\dashboard_B2_S04.png` (27.7 KB)
- `survey/dashboards\dashboard_B2_S05.png` (28.0 KB)
- `survey/dashboards\dashboard_B2_S06.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S07.png` (27.5 KB)
- `survey/dashboards\dashboard_B2_S08.png` (26.7 KB)
- `survey/dashboards\dashboard_B3_S01.png` (28.4 KB)
- `survey/dashboards\dashboard_B3_S02.png` (27.9 KB)
- `survey/dashboards\dashboard_B3_S03.png` (28.2 KB)
- `survey/dashboards\dashboard_B3_S04.png` (28.0 KB)
- `survey/dashboards\dashboard_B3_S05.png` (29.3 KB)
- `survey/dashboards\dashboard_B3_S06.png` (28.8 KB)
- `survey/dashboards\dashboard_B3_S07.png` (26.8 KB)
- `survey/dashboards\dashboard_B3_S08.png` (26.8 KB)

### Counterbalancing Files
- `survey/counterbalancing\counterbalancing_matrix.csv` (1.2 KB)
- `survey/counterbalancing\form_assembly_guide.csv` (1.6 KB)

### Metadata Files
- `survey/metadata\scenario_metadata.csv` (1.8 KB)
- `survey/metadata\scenario_news_text.csv` (13.4 KB)
- `survey/metadata\scenario_price_reaction.csv` (1.7 KB)
- `survey/metadata\scenario_shock_score.csv` (3.4 KB)

---

## 12. Completion Checklist

- [x] `scenario_metadata.csv`
- [x] `scenario_news_text.csv`
- [x] `scenario_price_reaction.csv`
- [x] `scenario_shock_score.csv`
- [x] Price charts: 24/24
- [x] Dashboard images: 24/24
- [x] `counterbalancing_matrix.csv`
- [x] `form_assembly_guide.csv`