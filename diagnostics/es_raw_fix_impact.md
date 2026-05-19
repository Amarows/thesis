# ES_raw Fix Impact Assessment

**Branch:** fix/es-raw-computation  
**Date:** 2026-05-19  
**Scope:** Prospective analysis — `event_selection_toolkit.py` fix applied; `scenario_shock_score.csv` NOT regenerated (step 3 frozen).  

## What changed

`_compute_es_severity()` replaces the hardcoded `EVENT_TYPE_SEVERITY` lookup table with a data-derived ratio:

```
ES_raw = sigma_k / sigma_all
sigma_k   = std(max-abs-30min-return) for events of type k across manifest
sigma_all = std(max-abs-30min-return) across all 24 manifest events
```

Fallback to lookup applies when sigma_all = 0 or fewer than 2 events of a given type exist.

## Event-type severity: old vs new

| event_type | es_raw_old (lookup) | es_raw_new (data-derived) | direction |
|:-----------|--------------------:|-------------------------:|:---------:|
| analyst    | 0.6000              | 1.5605                   | ↑ +0.9605 |
| earnings   | 1.0000              | 0.4393                   | ↓ −0.5607 |
| management | 0.8000              | 0.4557                   | ↓ −0.3443 |

*Interpretation:* Analyst events in the data have higher intraday return dispersion (sigma_k) relative to the cross-event baseline than earnings or management events. The lookup table assumed the opposite ordering.

## Scenario-level comparison table

| scenario_id | ticker | event_type | es_raw_old | es_raw_new | sc_total_old | sc_total_new | delta_sc | tier_old | tier_new | tier_changed |
|:------------|:-------|:-----------|----------:|-----------:|-------------:|-------------:|---------:|:---------|:---------|:-------------|
| B1_S01 | APD | analyst | 0.6000 | 1.5605 | −1.1348 | −0.5771 | +0.5577 | Low | **Medium** | YES |
| B1_S02 | COP | analyst | 0.6000 | 1.5605 | −0.1254 | +0.3204 | +0.4458 | Medium | **High** | YES |
| B1_S03 | LIN | earnings | 1.0000 | 0.4393 | −0.8805 | −1.1090 | −0.2285 | Low | Low | no |
| B1_S04 | UNH | management | 0.8000 | 0.4557 | −1.3270 | −1.4686 | −0.1416 | Low | Low | no |
| B1_S05 | HD | earnings | 1.0000 | 0.4393 | +2.2601 | +1.8922 | −0.3679 | High | High | no |
| B1_S06 | GE | management | 0.8000 | 0.4557 | −0.6429 | −0.8304 | −0.1875 | Medium | **Low** | YES |
| B1_S07 | T | earnings | 1.0000 | 0.4393 | −0.2622 | −0.5293 | −0.2671 | Medium | Medium | no |
| B1_S08 | QCOM | management | 0.8000 | 0.4557 | −1.7048 | −1.7818 | −0.0770 | Low | Low | no |
| B2_S01 | MRK | earnings | 1.0000 | 0.4393 | +0.8337 | +0.5044 | −0.3293 | High | High | no |
| B2_S02 | JPM | analyst | 0.6000 | 1.5605 | −0.3950 | +0.0467 | +0.4417 | Medium | Medium | no |
| B2_S03 | CVX | analyst | 0.6000 | 1.5605 | +1.0480 | +1.4540 | +0.4060 | High | High | no |
| B2_S04 | BAC | earnings | 1.0000 | 0.4393 | +0.0106 | −0.2780 | −0.2886 | Medium | Medium | no |
| B2_S05 | JNJ | earnings | 1.0000 | 0.4393 | −0.8631 | −1.1128 | −0.2497 | Low | Low | no |
| B2_S06 | KO | management | 0.8000 | 0.4557 | −1.7372 | −1.8468 | −0.1096 | Low | Low | no |
| B2_S07 | CAT | earnings | 1.0000 | 0.4393 | +1.0789 | +0.7653 | −0.3136 | High | High | no |
| B2_S08 | WMT | analyst | 0.6000 | 1.5605 | −0.8495 | −0.2864 | +**0.5631** | Low | **Medium** | YES |
| B3_S01 | ORCL | analyst | 0.6000 | 1.5605 | −0.5678 | −0.1345 | +0.4333 | Medium | Medium | no |
| B3_S02 | PG | analyst | 0.6000 | 1.5605 | −0.2092 | +0.2434 | +0.4526 | Medium | Medium | no |
| B3_S03 | AMT | earnings | 1.0000 | 0.4393 | +0.1847 | −0.0262 | −0.2109 | High | **Medium** | YES |
| B3_S04 | NFLX | management | 0.8000 | 0.4557 | −1.5063 | −1.6162 | −0.1099 | Low | Low | no |
| B3_S05 | PLD | management | 0.8000 | 0.4557 | −0.5329 | −0.6967 | −0.1638 | Medium | **Low** | YES |
| B3_S06 | PFE | earnings | 1.0000 | 0.4393 | +1.4122 | +1.0938 | −0.3184 | High | High | no |
| B3_S07 | MCD | earnings | 1.0000 | 0.4393 | +1.5427 | +1.2145 | −0.3282 | High | High | no |
| B3_S08 | AMAT | analyst | 0.6000 | 1.5605 | +4.3677 | +4.7590 | +0.3913 | High | High | no |

## PCA loadings: before vs after

| Component | Loading OLD | Loading NEW | Change |
|:----------|------------:|------------:|:-------|
| AC_e | 0.6602 | 0.6222 | −0.0380 |
| SE_e | 0.4682 | 0.4324 | −0.0358 |
| AI_e | 0.5818 | 0.6009 | +0.0191 |
| **ES_e** | **0.0797** | **0.2545** | **+0.1748** |
| Variance explained (PC1) | 48.27% | 49.80% | +1.53 pp |

The ES_e loading increases 3.2× (0.08 → 0.25), indicating substantially more construct validity for the data-derived severity measure. The overall variance explained by PC1 improves by 1.53 percentage points.

## Summary statistics

| Metric | Value |
|:-------|:------|
| Scenario IDs changed | **0 of 24** (IDs are frozen; not affected by fix) |
| Intensity tier changes | **6 of 24** |
| Max \|delta_sc\| | **0.5631** (B2_S08 WMT, analyst) |
| Scenarios where tier increases | 3 (B1_S01, B1_S02, B2_S08 — all analyst) |
| Scenarios where tier decreases | 3 (B1_S06 GE, B3_S03 AMT, B3_S05 PLD) |

## Would assign_blocks have chosen different scenarios?

**Cannot be assessed from available data.** `scenario_manifest.csv` contains only the 24 final deployed scenarios (one per stock). The candidate pool from which `assign_blocks` originally selected these 24 is not preserved in the repo. Since all scenario IDs are unchanged — the fix affects only SC_total values after selection — the question is moot for the deployed survey: the 24 scenarios remain identical.

## Effect on H1 and H2 inference

The fix does NOT affect the deployed survey or any collected responses. `8_statistical_analysis.py` reads `survey/metadata/scenario_shock_score.csv` (authoritative, generated by step 3 which is frozen). The updated SC_total values would only take effect if step 3 were re-run — which is prohibited because the 24 scenarios are deployed and frozen.

The fix is therefore a code-quality improvement that ensures future runs of the pipeline use data-derived ES_raw rather than the placeholder lookup table.

## Current pca_diagnostics.json (from step 8 run on this branch)

The `results/tables/pca_diagnostics.json` written by step 8 reflects the **old** values (lookup-based ES_raw), because `8_statistical_analysis.py` reads from the frozen `scenario_shock_score.csv`:

```json
{
  "eigenvalue_pc1": 2.0147,
  "variance_explained_pc1": 0.4827,
  "variance_explained_pct": 48.27,
  "loadings": {
    "AC_e": 0.6602,
    "SE_e": 0.4682,
    "AI_e": 0.5818,
    "ES_raw": 0.0797
  },
  "n_scenarios": 24
}
```

Prospective (new code, if step 3 were re-run):

```json
{
  "eigenvalue_pc1": ~2.0720,
  "variance_explained_pc1": 0.4980,
  "variance_explained_pct": 49.80,
  "loadings": {
    "AC_e": 0.6222,
    "SE_e": 0.4324,
    "AI_e": 0.6009,
    "ES_raw": 0.2545
  },
  "n_scenarios": 24
}
```
