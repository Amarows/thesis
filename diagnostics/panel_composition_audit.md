# Panel Composition Audit
Date: 2026-05-19
Commit investigated: e59b357d (fix: ES_e = r_shock / m_e)
Prior authoritative file: f976474e (survey/metadata/scenario_shock_score.csv)

---

## A. scenario_shock_score.csv Changes

**Scenarios added or removed:** None. All 24 scenario_ids are present in both the old
(f976474e) and new (e59b357d) versions. No scenarios were added or dropped.

**Nature of the change:** In the old file, `es_raw` held a coarse categorical mapping
{0.6, 0.8, 1.0}. In the new file it holds the continuous ratio `r_shock / m_e`, ranging
from ~4.1 to 10.0. All 24 `sc_total` values changed as a result of the corrected PCA
re-run. Four `severity_level` labels changed and two `protocol_recommendation` labels
changed.

| scenario_id | es_raw_old | es_raw_new | sc_total_old | sc_total_new | delta_sc | severity_old | severity_new | tier_changed | proto_old | proto_new | proto_changed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1_S01 | 0.6 | 9.7927 | -1.1348 | -0.5843 | +0.5505 | Low | Medium | YES | Standard Process | Standard Process | No |
| B1_S02 | 0.6 | 6.9479 | -0.1254 | -0.2026 | -0.0772 | Medium | Medium | No | Enhanced Review | Standard Process | YES |
| B1_S03 | 1.0 | 6.9761 | -0.8805 | -1.0480 | -0.1675 | Low | Low | No | Standard Process | Standard Process | No |
| B1_S04 | 0.8 | 4.2990 | -1.3270 | -1.8231 | -0.4961 | Low | Low | No | Standard Process | Standard Process | No |
| B1_S05 | 1.0 | 5.4162 | +2.2601 | +1.6628 | -0.5973 | High | High | No | Cooling-Off and Second Review | Cooling-Off and Second Review | No |
| B1_S06 | 0.8 | 8.3740 | -0.6429 | -0.6176 | +0.0253 | Medium | Medium | No | Standard Process | Standard Process | No |
| B1_S07 | 1.0 | 10.0000 | -0.2623 | -0.0516 | +0.2107 | Medium | Medium | No | Standard Process | Enhanced Review | YES |
| B1_S08 | 0.8 | 10.0000 | -1.7047 | -1.2276 | +0.4771 | Low | Low | No | Standard Process | Standard Process | No |
| B2_S01 | 1.0 | 5.7519 | +0.8337 | +0.3277 | -0.5060 | High | High | No | Enhanced Review | Enhanced Review | No |
| B2_S02 | 0.6 | 8.8855 | -0.3949 | -0.1934 | +0.2015 | Medium | Medium | No | Standard Process | Standard Process | No |
| B2_S03 | 0.6 | 7.5286 | +1.0480 | +1.0107 | -0.0373 | High | High | No | Enhanced Review | Enhanced Review | No |
| B2_S04 | 1.0 | 10.0000 | +0.0106 | +0.1932 | +0.1826 | Medium | Medium | No | Enhanced Review | Enhanced Review | No |
| B2_S05 | 1.0 | 7.5846 | -0.8631 | -0.9613 | -0.0982 | Low | Low | No | Standard Process | Standard Process | No |
| B2_S06 | 0.8 | 4.1893 | -1.7372 | -2.1832 | -0.4460 | Low | Low | No | Standard Process | Standard Process | No |
| B2_S07 | 1.0 | 10.0000 | +1.0789 | +1.2337 | +0.1548 | High | High | No | Enhanced Review | Enhanced Review | No |
| B2_S08 | 0.6 | 10.0000 | -0.8495 | -0.2541 | +0.5954 | Low | Medium | YES | Standard Process | Standard Process | No |
| B3_S01 | 0.6 | 6.9911 | -0.5678 | -0.6654 | -0.0976 | Medium | Low | YES | Standard Process | Standard Process | No |
| B3_S02 | 0.6 | 7.1520 | -0.2092 | -0.2520 | -0.0428 | Medium | Medium | No | Standard Process | Standard Process | No |
| B3_S03 | 1.0 | 8.3995 | +0.1847 | +0.2608 | +0.0761 | High | High | No | Enhanced Review | Enhanced Review | No |
| B3_S04 | 0.8 | 8.6174 | -1.5064 | -1.2902 | +0.2162 | Low | Low | No | Standard Process | Standard Process | No |
| B3_S05 | 0.8 | 4.0807 | -0.5329 | -1.1107 | -0.5778 | Medium | Low | YES | Standard Process | Standard Process | No |
| B3_S06 | 1.0 | 8.7643 | +1.4121 | +1.3808 | -0.0313 | High | High | No | Cooling-Off and Second Review | Cooling-Off and Second Review | No |
| B3_S07 | 1.0 | 10.0000 | +1.5427 | +1.6822 | +0.1395 | High | High | No | Cooling-Off and Second Review | Cooling-Off and Second Review | No |
| B3_S08 | 0.6 | 10.0000 | +4.3677 | +4.7132 | +0.3455 | High | High | No | Cooling-Off and Second Review | Cooling-Off and Second Review | No |

**Summary:**
- Scenarios added or removed: **0**
- sc_total changed: **all 24** (no scenario was unaffected by the ES_e correction)
- severity_level changed: **4** (B1_S01, B2_S08, B3_S01, B3_S05)
- protocol_recommendation changed: **2** (B1_S02: Enhanced Review → Standard Process; B1_S07: Standard Process → Enhanced Review)
- delta_sc range: −0.597 to +0.595 (max absolute change ≈ 0.60 SC units)

**Survey integrity:** The deployed Google Forms were assembled before the ES_e fix. The
charts and dashboards shown to respondents used the old SC_total values and the old
severity labels. The sc_total column in `analysis_panel.csv` is stored as null for all rows
(confirmed by inspection); `8_statistical_analysis.py` re-derives it at runtime from
`scenario_shock_score.csv`. Therefore all statistical outputs already use the corrected
SC_total. However, the _displayed_ Shock Score dashboard images used in the live survey
reflect the old es_raw = {0.6, 0.8, 1.0} values — the visual treatment (severity label,
protocol threshold) shown to ShowSC = 1 respondents may differ from the labels now in the
authoritative file for 4 scenarios (tier changes) and 2 scenarios (protocol changes).

---

## B. analysis_panel.csv Composition

| Metric | Value |
|---|---|
| Total rows | 456 |
| Unique respondents | 57 |
| Real respondents | 6 |
| Synthetic respondents | 51 |
| Real rows | 48 |
| Synthetic rows | 408 |
| Block 2 observations | 0 (no respondents — real or synthetic — assigned to Block 2) |

**How real vs synthetic identified:** Real respondents have IDs matching the pattern
`block_X_vY_rowNNNN` (e.g., `block_1_v1_row0001`). Synthetic respondents generated by
`7_augment_data.py` have IDs with prefix `persona_N_block_X_vY`.

**Real respondent IDs and timestamps:**

| respondent_id | block | version | timestamp |
|---|---|---|---|
| block_1_v1_row0001 | 1 | 1 | 2026-04-15 21:14:52 |
| block_1_v1_row0002 | 1 | 1 | 2026-05-04 10:31:56 |
| block_1_v2_row0001 | 1 | 2 | 2026-04-17 14:29:48 |
| block_1_v2_row0002 | 1 | 2 | 2026-04-29 14:26:26 |
| block_1_v2_row0003 | 1 | 2 | 2026-05-04 10:28:45 |
| block_3_v1_row0001 | 3 | 1 | 2026-05-15 13:16:54 |

**Timestamp range (all respondents):** 2026-04-15 to 2026-05-19

**Block 2 observations:** Zero. The augmentation script (`7_augment_data.py`) did not
assign synthetic personas to Block 2 scenarios. Block 2 is entirely absent from the panel.

---

## C. Data Loading Logic in 8_statistical_analysis.py

**Function:** `load_and_enrich()` (line 101)

**File read for respondent data:** `results/analysis_panel.csv` (PANEL_PATH). No filter
applied — all 57 respondents (6 real + 51 synthetic) are loaded.

**Synthetic respondent handling:** No flag or filter exists in `load_and_enrich()`. The
function loads the full panel unconditionally. Synthetic respondents (`persona_*` IDs) are
included in all descriptive statistics, regression models, and portfolio simulations
produced by `8_statistical_analysis.py`.

**SC_total enrichment:** After loading the panel, the function drops any pre-existing
`sc_total`, `ac_e`, `se_e`, `ai_e`, `es_raw`, `horizon_bucket`, `sentiment_direction`,
`severity_level`, and `protocol_recommendation` columns, then left-joins the authoritative
values from `survey/metadata/scenario_shock_score.csv` on `scenario_id`. This ensures
that the corrected SC_total from e59b357d is used in all analysis — even for rows that
were added to the panel before the fix.

**Join key:** `scenario_id`

**Implication:** The sc_total column in `analysis_panel.csv` is null for all rows (stored
empty by stage 6); the actual values are always sourced from `scenario_shock_score.csv` at
runtime. Corrected ES_e values are therefore automatically applied to all 456 rows
(including the 48 real-respondent rows) without any re-run of stages 1–6.

---

## D. Real-Only Regression Results

Filter applied: `respondent_id NOT LIKE 'persona_%'`

Specification mirrors the primary H1 OLS in `8_statistical_analysis.py`: OLS with HC3
standard errors; regressors = sc_total, show_sc, block FE dummies, experience-category
dummies (reference = <5 yr, given the real sample distribution).

| Metric | Value |
|---|---|
| N respondents (real) | 6 |
| N observations | 48 |
| β₁ (sc_total) | −0.1012 |
| SE (HC3) | 0.1059 |
| p-value | 0.3393 |
| R² | 0.0367 |

The negative sign is directionally consistent with the thesis hypothesis (higher shock
intensity → respondent reduces exposure, i.e. lower NRS), but the result is not
statistically significant. With only 6 respondents contributing 48 observations the model
is severely underpowered; the synthetic augmentation (51 personas) provides the statistical
weight in the current published results.

**Published results (mixed panel, N = 57):** These are produced by `8_statistical_analysis.py`
using the full 456-row panel and should be consulted in `results/thesis_results.md` for
the current β₁ and p-value used in the thesis. The real-only numbers above are a
diagnostic estimate, not a revision.

---

## Conclusion

| Question | Finding |
|---|---|
| Were deployed survey scenarios changed? | **No.** All 24 scenario_ids are intact. Tickers, event dates, and scenario positions are unchanged. The fix altered SC_total values and 4 severity labels / 2 protocol labels in the metadata, but respondents had already completed the survey with the old dashboard images. |
| Is the analysis panel mixed (real + synthetic)? | **Yes.** The panel contains 6 real respondents (48 observations) and 51 synthetic personas (408 observations). No filter separates them in `8_statistical_analysis.py`. All published thesis results reflect the mixed panel. |
| Does the ES_e fix affect runtime analysis? | **Yes, automatically.** `load_and_enrich()` always overwrites sc_total from the authoritative file at runtime, so corrected SC_total values are used for all 456 rows including the real respondents' rows. No re-run of stages 1–6 was needed for the fix to propagate to the analysis. |
| Is H1 supported in real respondents only? | **No** (at current sample size). β₁ = −0.1012, p = 0.34. The sample is too small (N = 6) to draw inference. Real-data replication is the primary recommended next step. |
