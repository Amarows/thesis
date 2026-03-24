# Survey Assembly Report

Generated: 2026-03-24 17:12:25

---

## 1. Scenario Counts
- **Total scenarios:** 35
- Block 1: 12 scenarios
- Block 2: 12 scenarios
- Block 3: 11 scenarios

## 2. PCA Results - SC_total Construction
- PC1 explained variance: **0.5662** (56.6%)
- Loadings (w_1):
  - ac: 0.6000
  - se: 0.4496
  - ai: 0.5733
  - es: 0.3304

## 3. SC_total Distribution (all scenarios)
| Statistic | Value |
|-----------|-------|
| Mean      | 0.0000 |
| Std       | 1.5269 |
| Min       | -2.6069 |
| Q1        | -0.8144 |
| Median    | -0.2229 |
| Q3        | 0.7083 |
| Max       | 4.8351 |

### SC_total by Severity Bucket
- **Low**: n=12, mean=-1.4155, range=[-2.6069, -0.5867]
- **Medium**: n=11, mean=-0.2190, range=[-0.5799, 0.1872]
- **High**: n=12, mean=1.6163, range=[0.3007, 4.8351]

### Protocol Distribution
- Standard Process: 21 scenarios
- Enhanced Review: 8 scenarios
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
- `survey/charts\chart_B1_S01.png` (136.5 KB)
- `survey/charts\chart_B1_S02.png` (150.6 KB)
- `survey/charts\chart_B1_S03.png` (132.7 KB)
- `survey/charts\chart_B1_S04.png` (145.4 KB)
- `survey/charts\chart_B1_S05.png` (158.4 KB)
- `survey/charts\chart_B1_S06.png` (142.5 KB)
- `survey/charts\chart_B1_S07.png` (136.9 KB)
- `survey/charts\chart_B1_S08.png` (140.7 KB)
- `survey/charts\chart_B1_S09.png` (142.3 KB)
- `survey/charts\chart_B1_S10.png` (132.8 KB)
- `survey/charts\chart_B1_S11.png` (129.9 KB)
- `survey/charts\chart_B1_S12.png` (139.6 KB)
- `survey/charts\chart_B2_S01.png` (149.4 KB)
- `survey/charts\chart_B2_S02.png` (135.4 KB)
- `survey/charts\chart_B2_S03.png` (145.0 KB)
- `survey/charts\chart_B2_S04.png` (134.7 KB)
- `survey/charts\chart_B2_S05.png` (136.4 KB)
- `survey/charts\chart_B2_S06.png` (146.2 KB)
- `survey/charts\chart_B2_S07.png` (136.9 KB)
- `survey/charts\chart_B2_S08.png` (144.5 KB)
- `survey/charts\chart_B2_S09.png` (138.1 KB)
- `survey/charts\chart_B2_S10.png` (135.2 KB)
- `survey/charts\chart_B2_S11.png` (134.1 KB)
- `survey/charts\chart_B2_S12.png` (133.1 KB)
- `survey/charts\chart_B3_S01.png` (149.9 KB)
- `survey/charts\chart_B3_S02.png` (139.6 KB)
- `survey/charts\chart_B3_S03.png` (138.6 KB)
- `survey/charts\chart_B3_S04.png` (139.4 KB)
- `survey/charts\chart_B3_S05.png` (156.2 KB)
- `survey/charts\chart_B3_S06.png` (142.6 KB)
- `survey/charts\chart_B3_S07.png` (161.6 KB)
- `survey/charts\chart_B3_S08.png` (152.6 KB)
- `survey/charts\chart_B3_S09.png` (137.8 KB)
- `survey/charts\chart_B3_S10.png` (140.5 KB)
- `survey/charts\chart_B3_S11.png` (127.1 KB)
- `survey/counterbalancing\counterbalancing_matrix.csv` (3.4 KB)
- `survey/counterbalancing\form_assembly_guide.csv` (4.4 KB)
- `survey/dashboards\dashboard_B1_S01.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S02.png` (27.9 KB)
- `survey/dashboards\dashboard_B1_S03.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S04.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S05.png` (27.1 KB)
- `survey/dashboards\dashboard_B1_S06.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S07.png` (27.2 KB)
- `survey/dashboards\dashboard_B1_S08.png` (28.4 KB)
- `survey/dashboards\dashboard_B1_S09.png` (26.7 KB)
- `survey/dashboards\dashboard_B1_S10.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S11.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S12.png` (28.0 KB)
- `survey/dashboards\dashboard_B2_S01.png` (26.8 KB)
- `survey/dashboards\dashboard_B2_S02.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S03.png` (25.2 KB)
- `survey/dashboards\dashboard_B2_S04.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S05.png` (27.3 KB)
- `survey/dashboards\dashboard_B2_S06.png` (27.5 KB)
- `survey/dashboards\dashboard_B2_S07.png` (28.3 KB)
- `survey/dashboards\dashboard_B2_S08.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S09.png` (28.3 KB)
- `survey/dashboards\dashboard_B2_S10.png` (29.0 KB)
- `survey/dashboards\dashboard_B2_S11.png` (28.7 KB)
- `survey/dashboards\dashboard_B2_S12.png` (28.0 KB)
- `survey/dashboards\dashboard_B3_S01.png` (27.5 KB)
- `survey/dashboards\dashboard_B3_S02.png` (28.4 KB)
- `survey/dashboards\dashboard_B3_S03.png` (28.7 KB)
- `survey/dashboards\dashboard_B3_S04.png` (27.5 KB)
- `survey/dashboards\dashboard_B3_S05.png` (25.6 KB)
- `survey/dashboards\dashboard_B3_S06.png` (26.7 KB)
- `survey/dashboards\dashboard_B3_S07.png` (28.6 KB)
- `survey/dashboards\dashboard_B3_S08.png` (27.5 KB)
- `survey/dashboards\dashboard_B3_S09.png` (27.2 KB)
- `survey/dashboards\dashboard_B3_S10.png` (26.3 KB)
- `survey/dashboards\dashboard_B3_S11.png` (28.3 KB)
- `survey/metadata\scenario_metadata.csv` (2.5 KB)
- `survey/metadata\scenario_news_text.csv` (29.5 KB)
- `survey/metadata\scenario_price_reaction.csv` (2.5 KB)
- `survey/metadata\scenario_shock_score.csv` (4.9 KB)

## 7. Completion Checklist
- [x] `scenario_metadata.csv`
- [x] `scenario_news_text.csv`
- [x] `scenario_price_reaction.csv`
- [x] `scenario_shock_score.csv`
- [x] Price charts: 35/35
- [x] Dashboard images: 35/35
- [x] `counterbalancing_matrix.csv`
- [x] `form_assembly_guide.csv`