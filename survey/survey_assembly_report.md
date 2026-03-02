# Survey Assembly Report

Generated: 2026-03-01 19:55:57

---

## 1. Scenario Counts
- **Total scenarios:** 35
- Block 1: 12 scenarios
- Block 2: 12 scenarios
- Block 3: 11 scenarios

## 2. PCA Results - SC_total Construction
- PC1 explained variance: **0.5451** (54.5%)
- Loadings (w_1):
  - ac: 0.5874
  - se: 0.4154
  - ai: 0.5820
  - es: 0.3790

## 3. SC_total Distribution (all scenarios)
| Statistic | Value |
|-----------|-------|
| Mean      | 0.0000 |
| Std       | 1.4981 |
| Min       | -3.1542 |
| Q1        | -0.8184 |
| Median    | -0.2798 |
| Q3        | 0.6230 |
| Max       | 4.7117 |

### SC_total by Severity Bucket
- **Low**: n=12, mean=-1.3386, range=[-3.1542, -0.5700]
- **Medium**: n=11, mean=-0.2254, range=[-0.4814, 0.0321]
- **High**: n=12, mean=1.5453, range=[0.2411, 4.7117]

### Protocol Distribution
- Standard Process: 21 scenarios
- Enhanced Review: 8 scenarios
- Cooling-Off and Second Review: 6 scenarios

## 4. Notes and Caveats

### 4a. ES_raw (Event-Type Severity)
Uses a placeholder category-level severity mapping (see `EVENT_TYPE_SEVERITY` in `3_survey_assembly.py`). **Requires manual review** against actual event characteristics before finalising SC_total for the thesis.

### 4b. Sentiment Scoring
Scores use **VADER** (from `nltk`) as a proxy for FinBERT. VADER compound scores range from -1 to +1. Replace with FinBERT (transformers/torch) for thesis-quality computation; see `toolkits/news_sentiment_toolkit.py` for integration point.

### 4c. Persistence Horizon
`horizon_bucket` requires 5-day post-event return data and is currently set to `[REQUIRES POST-EVENT DATA]`. Extend price data coverage and re-run the script.

### 4d. Summary Paragraphs
ANTHROPIC_API_KEY was not set - `summary_paragraph` contains `[TO BE GENERATED]` placeholders. Set the environment variable and re-run, or populate manually.

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
- `survey/dashboards\dashboard_B1_S01.png` (28.6 KB)
- `survey/dashboards\dashboard_B1_S02.png` (27.6 KB)
- `survey/dashboards\dashboard_B1_S03.png` (29.5 KB)
- `survey/dashboards\dashboard_B1_S04.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S05.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S06.png` (28.2 KB)
- `survey/dashboards\dashboard_B1_S07.png` (28.6 KB)
- `survey/dashboards\dashboard_B1_S08.png` (29.0 KB)
- `survey/dashboards\dashboard_B1_S09.png` (28.6 KB)
- `survey/dashboards\dashboard_B1_S10.png` (27.5 KB)
- `survey/dashboards\dashboard_B1_S11.png` (28.2 KB)
- `survey/dashboards\dashboard_B1_S12.png` (29.9 KB)
- `survey/dashboards\dashboard_B2_S01.png` (27.4 KB)
- `survey/dashboards\dashboard_B2_S02.png` (28.6 KB)
- `survey/dashboards\dashboard_B2_S03.png` (26.9 KB)
- `survey/dashboards\dashboard_B2_S04.png` (28.2 KB)
- `survey/dashboards\dashboard_B2_S05.png` (28.0 KB)
- `survey/dashboards\dashboard_B2_S06.png` (26.7 KB)
- `survey/dashboards\dashboard_B2_S07.png` (27.2 KB)
- `survey/dashboards\dashboard_B2_S08.png` (28.6 KB)
- `survey/dashboards\dashboard_B2_S09.png` (28.6 KB)
- `survey/dashboards\dashboard_B2_S10.png` (28.8 KB)
- `survey/dashboards\dashboard_B2_S11.png` (28.4 KB)
- `survey/dashboards\dashboard_B2_S12.png` (29.2 KB)
- `survey/dashboards\dashboard_B3_S01.png` (28.6 KB)
- `survey/dashboards\dashboard_B3_S02.png` (27.6 KB)
- `survey/dashboards\dashboard_B3_S03.png` (29.9 KB)
- `survey/dashboards\dashboard_B3_S04.png` (27.3 KB)
- `survey/dashboards\dashboard_B3_S05.png` (26.9 KB)
- `survey/dashboards\dashboard_B3_S06.png` (28.2 KB)
- `survey/dashboards\dashboard_B3_S07.png` (28.6 KB)
- `survey/dashboards\dashboard_B3_S08.png` (28.2 KB)
- `survey/dashboards\dashboard_B3_S09.png` (28.6 KB)
- `survey/dashboards\dashboard_B3_S10.png` (26.7 KB)
- `survey/dashboards\dashboard_B3_S11.png` (28.1 KB)
- `survey/metadata\scenario_metadata.csv` (2.5 KB)
- `survey/metadata\scenario_news_text.csv` (4.6 KB)
- `survey/metadata\scenario_price_reaction.csv` (2.5 KB)
- `survey/metadata\scenario_shock_score.csv` (5.0 KB)

## 7. Completion Checklist
- [x] `scenario_metadata.csv`
- [x] `scenario_news_text.csv`
- [x] `scenario_price_reaction.csv`
- [x] `scenario_shock_score.csv`
- [x] Price charts: 35/35
- [x] Dashboard images: 35/35
- [x] `counterbalancing_matrix.csv`
- [x] `form_assembly_guide.csv`