# Survey Assembly Report

Generated: 2026-04-03 10:56:50

---

## 1. Scenario Counts
- **Total scenarios:** 36
- Block 1: 12 scenarios
- Block 2: 12 scenarios
- Block 3: 12 scenarios

## 2. PCA Results - SC_total Construction
- PC1 explained variance: **0.5925** (59.2%)
- Loadings (w_1):
  - ac: 0.5787
  - se: 0.4720
  - ai: 0.5553
  - es: 0.3659

## 3. SC_total Distribution (all scenarios)
| Statistic | Value |
|-----------|-------|
| Mean      | -0.0000 |
| Std       | 1.5613 |
| Min       | -2.4272 |
| Q1        | -1.0005 |
| Median    | -0.0933 |
| Q3        | 0.7904 |
| Max       | 4.9518 |

### SC_total by Severity Bucket
- **Low**: n=12, mean=-1.5598, range=[-2.4272, -0.6485]
- **Medium**: n=12, mean=-0.1353, range=[-0.4073, 0.2480]
- **High**: n=12, mean=1.6952, range=[0.4424, 4.9518]

### Protocol Distribution
- Standard Process: 21 scenarios
- Enhanced Review: 9 scenarios
- Cooling-Off and Second Review: 6 scenarios

## 4. Notes and Caveats

### 4a. ES_raw (Event-Type Severity)
Uses a placeholder category-level severity mapping (see `EVENT_TYPE_SEVERITY` in `3_survey_assembly.py`). **Requires manual review** against actual event characteristics before finalising SC_total for the thesis.

### 4b. Sentiment Scoring
Scores use **FinBERT** (`ProsusAI/finbert`) via HuggingFace Transformers. The sentiment score is `positive_prob - negative_prob` in [-1, 1]. See `toolkits/news_sentiment_toolkit.py` for the shared scorer.

### 4c. Persistence Horizon
`horizon_bucket` requires 5-day post-event return data and is currently set to `[REQUIRES POST-EVENT DATA]`. Extend price data coverage and re-run the script.

### 4d. Summary Paragraphs
ANTHROPIC_API_KEY was set - summary paragraphs were auto-generated via Claude (claude-sonnet-4-6). Review each paragraph before use.

## 5. Warnings
- No warnings.

## 6. Generated File Manifest
- `survey/charts\chart_B1_S01.png` (160.7 KB)
- `survey/charts\chart_B1_S02.png` (161.7 KB)
- `survey/charts\chart_B1_S03.png` (157.8 KB)
- `survey/charts\chart_B1_S04.png` (146.6 KB)
- `survey/charts\chart_B1_S05.png` (157.2 KB)
- `survey/charts\chart_B1_S06.png` (166.4 KB)
- `survey/charts\chart_B1_S07.png` (159.3 KB)
- `survey/charts\chart_B1_S08.png` (148.2 KB)
- `survey/charts\chart_B1_S09.png` (144.4 KB)
- `survey/charts\chart_B1_S10.png` (151.1 KB)
- `survey/charts\chart_B1_S11.png` (137.8 KB)
- `survey/charts\chart_B1_S12.png` (151.0 KB)
- `survey/charts\chart_B2_S01.png` (162.9 KB)
- `survey/charts\chart_B2_S02.png` (145.2 KB)
- `survey/charts\chart_B2_S03.png` (145.3 KB)
- `survey/charts\chart_B2_S04.png` (166.1 KB)
- `survey/charts\chart_B2_S05.png` (148.9 KB)
- `survey/charts\chart_B2_S06.png` (148.2 KB)
- `survey/charts\chart_B2_S07.png` (153.2 KB)
- `survey/charts\chart_B2_S08.png` (164.0 KB)
- `survey/charts\chart_B2_S09.png` (151.4 KB)
- `survey/charts\chart_B2_S10.png` (148.8 KB)
- `survey/charts\chart_B2_S11.png` (149.9 KB)
- `survey/charts\chart_B2_S12.png` (138.1 KB)
- `survey/charts\chart_B3_S01.png` (145.0 KB)
- `survey/charts\chart_B3_S02.png` (155.9 KB)
- `survey/charts\chart_B3_S03.png` (145.0 KB)
- `survey/charts\chart_B3_S04.png` (149.8 KB)
- `survey/charts\chart_B3_S05.png` (151.0 KB)
- `survey/charts\chart_B3_S06.png` (151.3 KB)
- `survey/charts\chart_B3_S07.png` (144.3 KB)
- `survey/charts\chart_B3_S08.png` (148.0 KB)
- `survey/charts\chart_B3_S09.png` (163.8 KB)
- `survey/charts\chart_B3_S10.png` (153.0 KB)
- `survey/charts\chart_B3_S11.png` (144.7 KB)
- `survey/charts\chart_B3_S12.png` (144.6 KB)
- `survey/counterbalancing\counterbalancing_matrix.csv` (3.5 KB)
- `survey/counterbalancing\form_assembly_guide.csv` (4.5 KB)
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
- `survey/metadata\scenario_metadata.csv` (2.6 KB)
- `survey/metadata\scenario_news_text.csv` (30.3 KB)
- `survey/metadata\scenario_price_reaction.csv` (2.5 KB)
- `survey/metadata\scenario_shock_score.csv` (5.0 KB)

## 7. Completion Checklist
- [x] `scenario_metadata.csv`
- [x] `scenario_news_text.csv`
- [x] `scenario_price_reaction.csv`
- [x] `scenario_shock_score.csv`
- [x] Price charts: 36/36
- [x] Dashboard images: 36/36
- [x] `counterbalancing_matrix.csv`
- [x] `form_assembly_guide.csv`