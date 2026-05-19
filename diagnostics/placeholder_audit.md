# Placeholder & Implementation Audit

**Issue:** [#172](https://github.com/Amarows/thesis/issues/172)  
**Branch:** fix/es-raw-computation  
**Date:** 2026-05-19  
**Scope:** All Python files + thesis_final.md + SC component distributions

---

## 1. Code-level findings

### CONFIRMED BUG (fixed in this branch)

#### ES_e formula mismatch — `event_selection_toolkit.py`

| | Before this branch | After this branch |
|:--|:--|:--|
| Function | `_compute_es_severity()` | `_compute_es_severity()` |
| Formula | `sigma_k / sigma_all` (cross-event category std ratio) | `r_shock / m_e` (per-event shock bar return / 20-day trailing median) |
| Unique values | 3 (one per event_type) | 24 (one per scenario) |
| Thesis §4.3.5 | ✗ Mismatch | ✓ Matches |

The cross-event formula was a transitional implementation introduced when replacing the lookup table. It computed the standard deviation of max-abs-30min-returns across events of the same type and divided by the cross-event standard deviation — producing one value per event_type rather than one per event. This did not match the thesis formula and produced near-constant es_z within each event type.

**Status: Fixed.** `_compute_es_severity()` now implements `r_shock / m_e` as specified. All 24 scenarios compute successfully with unique per-event values (0 fallbacks triggered; 7/24 hit the 10.0 cap, consistent with genuine shock events selected by the screening algorithm).

---

### ACCEPTABLE STUBS / FALLBACKS (no action required)

#### `event_selection_toolkit.py`
- **`EVENT_TYPE_SEVERITY` dict (L2030):** Retained as the documented fallback for `_compute_es_severity()` when intraday price data are unavailable. Now clearly a fallback, not the primary computation.
- **`se_raw = 0.0` initialisation (L2223):** Overwritten when FinBERT processes articles. Warning printed if FinBERT unavailable.
- **`ai_raw = 0.0` initialisation (L2243):** Overwritten when price data available. Warning printed if not.

#### `news_processor_toolkit.py`
- `"[TO BE GENERATED]"` placeholder for news summaries when Anthropic API is unavailable — documented graceful fallback.

#### `news_sentiment_toolkit.py`
- `se_raw = 0.0` when FinBERT not installed — documented with install instruction.

#### `data_aggregation_toolkit.py`
- `pd.NA` column initialisations filled by subsequent merge operations — correct design pattern.

#### `src_api_yahoo/market_data_toolkit.py`
- `fillna(1.0)` for missing ticker returns — documented with log output listing affected tickers.

#### `4_deploy_google_forms.py`
- `"[TO BE GENERATED]"` summary fallback for survey deployment — acceptable.

---

### STALE DOCUMENTATION (fixed in this branch)

#### `survey_design_toolkit.py` — two locations

| Location | Old text | Updated text |
|:---------|:---------|:-------------|
| L653–655 (assembly report body) | "currently based on a placeholder severity mapping and requires manual review" | Describes r_shock/m_e formula and fallback condition |
| L794–798 (section 9a of report) | "Uses a placeholder category-level severity mapping… **Requires manual review**" | Describes r_shock/m_e formula and fallback condition |

These comments referenced the old lookup-table approach. Updated to accurately describe the current implementation.

---

## 2. Thesis text — residual placeholders

### `thesis_final.md`
**Zero residual placeholders.** Searched for: `[To be populated`, `[placeholder`, `[TBD`, `[insert`, `[verify`, `TODO`, `FIXME`, `To be populated` (bare). No matches found.

### `thesis.md`
**15 `[To be populated by 8_statistical_analysis.py]` blocks present.** These are intentional template markers for the `9_compile_thesis.py` placeholder-replacement system (PLACEHOLDER:/PLACEHOLDER: comment pairs). Not an error. All 15 are replaced in `thesis_final.md` during compilation.

---

## 3. Thesis formula cross-check

| Component | Thesis §4.3.5 formula | Code implementation | Status |
|:----------|:---------------------|:--------------------|:-------|
| AC_e | Count of articles in shock bar | `len(day_articles)` | ✓ Matches |
| SE_e | max_j \|sentiment_j\| | `max(abs(s) for s in sentiment_scores)` | ✓ Matches |
| AI_e | V_e / V̄_e (event volume / 20-day avg daily volume) | event_day_vol / trailing_20["volume"].mean() | ✓ Matches |
| ES_e | r_shock / m_e (capped at 10.0) | `_compute_es_severity()` | ✓ Matches (fixed in this branch) |

---

## 4. SC component distributions (post-fix)

After the r_shock/m_e fix, ES_raw has 24 unique values — one per scenario:

| Component | Unique values | Std | CV | Min | Max | Assessment |
|:----------|:-------------|:----|:----|:----|:----|:-----------|
| ac_raw | 11 | 5.76 | 1.05 | 1 | 22 | Normal for article counts |
| se_raw | 24 | 0.36 | 0.52 | 0.009 | 0.966 | Full range ✓ |
| ai_raw | 24 | 1.44 | 0.68 | 0.59 | 7.37 | Full range ✓ |
| **es_raw (old sigma_k/sigma_all)** | **3** | 0.54 | 0.66 | 0.44 | 1.56 | **Suspicious — 3 unique values** |
| **es_raw (new r_shock/m_e)** | **24** | — | — | — | — | **Full range ✓** |

The old sigma_k/sigma_all produced only 3 unique values because the statistic was computed once per event_type and broadcast to all scenarios of that type. The thesis formula produces a genuinely per-event measure.

**PCA loading impact (prospective, from earlier analysis in this branch):**

| | ES_e loading | PC1 variance explained |
|:--|:--|:--|
| Old sigma_k/sigma_all | 0.2545 | 49.80% |
| New r_shock/m_e | TBD (requires step 3 re-run) | TBD |

---

## 5. No new child issues required

The only confirmed implementation error (ES_e formula mismatch) is resolved in this branch. All other findings are either acceptable fallbacks with documented behaviour or stale documentation (updated in this branch). No P1 child issues created.

---

## Files modified in this audit

| File | Change |
|:-----|:-------|
| `toolkits/event_selection_toolkit.py` | `_compute_es_severity()` reimplemented as r_shock/m_e; `compute_raw_components()` passes `event_time`; docstrings updated |
| `toolkits/survey_design_toolkit.py` | Two stale "placeholder" comments updated to describe actual formula |
| `diagnostics/placeholder_audit.md` | This file (new) |
