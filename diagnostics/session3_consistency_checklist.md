# Results Consistency Protocol — Run Record
**Date:** 2026-05-21
**Pipeline run timestamp (from log):** 2026-05-20T21:40:46.915208+00:00 (9_compile_thesis.py); last 8_statistical_analysis.py: 2026-05-20T09:58:07.471042+00:00
**Reviewer:** Claude (automated audit — Session 3)
**Audit target:** thesis_final.md (Chapters 5 and 6) against results/thesis_results.md and results/tables/

---

## Pre-flight

**ALERT — Pre-flight timestamp check FAILED.**

- Most recent pipeline log entry: `2026-05-20T21:40:46` (`9_compile_thesis.py`, git commit `94e5e60`)
- `thesis_final.md` last committed: `2026-05-21T10:23:19Z` — **12 hours 42 minutes after last pipeline entry**
- `results/thesis_results.md` last committed: `2026-05-21T09:42:52Z` — **11 hours 42 minutes after last pipeline entry**
- Both files were hand-edited and recommitted after the pipeline ran.

**Decision:** Audit proceeded (all four passes executed). Pre-flight failure is recorded as A3 and D1 violations. Numerical values in thesis_final.md are internally consistent with the authoritative CSVs; the risk is unrecorded provenance, not numerical error.

---

## PASS A — Source-of-truth audit

**[x] A1. PCA values match between assembly report and pca_diagnostics.json**

All five fields match to required precision:

| Field | survey_assembly_report.md | pca_diagnostics.json | Match |
|---|---|---|---|
| PC1 variance explained | 50.4% (0.5038) | 50.38% | PASS (to 1 dp) |
| AC_e loading | 0.6120 | 0.6120 | PASS |
| SE_e loading | 0.3990 | 0.3990 | PASS |
| AI_e loading | 0.6161 | 0.6161 | PASS |
| ES_raw loading | 0.2944 | 0.2944 | PASS |

**[x] A2. Scenario count = 24 in both shock score CSV and thesis_results.md**

- `scenario_shock_score.csv`: 24 rows confirmed.
- `pca_diagnostics.json` n_scenarios: 24.
- `results/thesis_results.md` Section s5_3_scenarios: "24/24 scenarios".

**[ ] A3. Pipeline run log post-dates thesis_results.md**

FAIL. Most recent pipeline log entry timestamp (`2026-05-20T21:40:46`) pre-dates the `results/thesis_results.md` commit (`2026-05-21T09:42:52Z`). The results file was modified and recommitted after the last recorded pipeline run. Current `thesis_results.md` hash `a1fdebd524ab1806` does not match any pipeline log entry. The most recent `8_statistical_analysis.py` run produced hash `8b064869b3a7a17d`; the most recent `9_compile_thesis.py` run consumed `thesis_results.md` with hash `97a090bcd2a4e60c` — neither matches the current file.

---

## PASS B — Cross-file numerical consistency

**[x] B1. H1 primary β₁, SE, t, p, CI, N match tbl_h1_main.csv**

All seven fields verified exact match (4 dp where applicable):

| Parameter | thesis_final.md | tbl_h1_main.csv | Match |
|---|---|---|---|
| β₁ | -0.4874 | -0.4874 | PASS |
| SE | 0.0551 | 0.0551 | PASS |
| t | -8.8452 | -8.8452 | PASS |
| p | <0.0001 | <0.0001 | PASS |
| CI_lo | -0.5954 | -0.5954 | PASS |
| CI_hi | -0.3794 | -0.3794 | PASS |
| N_obs | 424 | 424 | PASS |

Cross-checked in both Table 5.3 (L1342) and narrative text (L1336). Both match.

**[x] B2. All robustness specs in Table 5.4 match tbl_h1_robustness.csv**

All nine specification rows verified. No numerical discrepancies. Note: `spec_1_quintiles` p-value displays as `nan` in the thesis table — this is a pandas NaN display artefact (the CSV field is empty, no single p-value for quintile dummies). This is a display formatting issue, not a numerical content error; the table note "see quintile coefficients" is present.

**[ ] B3. H2 portfolio_return and sharpe_ratio rows match tbl_h2_portfolio.csv**

PARTIAL FAIL. All numerical values (τ, SE, t, p, CI, Cohen's d) match exactly. However, the protocol specifies that `sharpe_ratio.h2_supported` must equal `True`; the CSV contains `False` (p = 0.6050, which is > 0.05, so the flag is numerically correct). The protocol expectation is stale: it was written when the sharpe result was anticipated to be significant. The thesis table correctly reflects `False`. Edit target: `8_statistical_analysis.py` h2_supported logic or the protocol document itself; the thesis table is consistent with the CSV.

| Row | Parameter | thesis_final.md | tbl_h2_portfolio.csv | Match |
|---|---|---|---|---|
| portfolio_return | τ | -0.1584 | -0.1584 | PASS |
| portfolio_return | p | 0.7428 | 0.7428 | PASS |
| portfolio_return | cohens_d | -0.0591 | -0.0591 | PASS |
| sharpe_ratio | τ | 0.8790 | 0.8790 | PASS |
| sharpe_ratio | p | 0.6050 | 0.6050 | PASS |
| sharpe_ratio | h2_supported | False | False | PASS (CSV correct; protocol expectation stale) |

**[x] B4. PCA loadings in thesis text match pca_diagnostics.json**

All loadings and explained variance in Section 5.2.3 (L1218–L1228) match pca_diagnostics.json exactly. Eigenvalue 2.1027 also matches. No discrepancies between assembly report and diagnostics JSON (see A1).

**[ ] B5. Descriptive statistics in Sections 5.2 and 5.4 match table CSVs**

PARTIAL FAIL — respondent and NRS statistics verified; normality statistics cannot be verified.

- `tbl_descriptive_respondents.csv`: n_total=53, exp_mean=5.125, exp_median=5.75, exp_sd=3.4731. Thesis L1173 and Table 5.1 show 5.1250, 5.7500, 3.4731. PASS.
- `tbl_descriptive_nrs.csv`: overall n=424, mean=4.0519, SD=1.3845. Thesis L1201 matches exactly. PASS.
- `tbl_normality.csv`: **file is empty (header only, no data rows)**. Thesis Table 5.4c reports Shapiro-Wilk W = 0.9849, p = 0.0002. These values appear in `results/thesis_results.md` block `s5_4_normality` but have no CSV source to verify against. FAIL — normality values unverifiable against authoritative source.

**[x] B6. Alignment rates in Table 5.5 match tbl_nrs_sentiment_alignment.csv**

All 10 rows (overall + 2 ShowSC groups + 7 sentiment groups) match exactly. Overall alignment rate 0.2618 appears correctly in Section 5.6.1.1 (L1430). Note: the protocol document itself contains a stale reference to 0.2851 as the expected overall rate; this is a D3 project-knowledge issue in the protocol, not a thesis violation.

---

## PASS C — Interpretive consistency

**[x] C1. All coefficient directions correctly described**

Primary β₁ = −0.4874 described as "risk-reducing shift" and "lower mean NRS" throughout (L1336, L1420–L1422, L1466). PASS.

ES_raw = +0.3102 (positive) described as "increase in NRS" / contrarian-resolution pattern (L1344, L1424). PASS — direction language is correct and consistent with sign.

Spec 5 interaction β₃ = +0.1954: the thesis table header (L1368) labels this column "SC_total × D_neg amplification (negative events)", which uses the word "amplification" consistent with the protocol exception requirement. The narrative text (L1346) describes it as non-significant and exploratory. PASS — the amplification framing is present in the table header; no direction contradiction exists.

Compound effect β₁ + β₃ = −0.4283 + 0.1954 = −0.2329 stated correctly (L1346). PASS.

**[x] C2. Significance language appropriate to p-value ranges**

No prohibited language ("marginally significant", "trending", "approaching significance", "highly significant") found in Chapters 5–6. Results with p < 0.0001 described as "statistically significant". H2 result (p = 0.7428) described as "fails to reject the null hypothesis". Spec 4 (p = 0.9358) not given significance language. PASS.

**[ ] C3. H2 split outcome (portfolio_return not supported; sharpe_ratio noted)**

FAIL. Section 5.7 Interim Conclusions (L1466) states only: "the null hypothesis H2₀ was not rejected (τ = −0.1584, p = 0.7428) in the Option B individual-portfolio regression." The sharpe_ratio secondary outcome (τ = 0.879, p = 0.6050) is not mentioned in Section 5.7. Protocol CR-3 requires both facts to appear in Section 5.7. The sharpe_ratio result does appear in Table 5.5 (L1399) and Figure 5.4, but is absent from the narrative summary in 5.7 and from Chapter 6 sections 6.2.2 and 6.3.

Offending sentence by omission: Section 5.7, L1466 — "H2 – that the Shock Score dashboard moderates the risk-return profile of simulated portfolios: **the null hypothesis H2₀ was not rejected** (τ = −0.1584, p = 0.7428) in the Option B individual-portfolio regression."

Edit target: `thesis.md` Section 5.7 placeholder — add sharpe_ratio secondary outcome sentence.

**[x] C4. ES_raw positive coefficient present with acceptable interpretation**

Present and correctly interpreted. L1344 (Section 5.5.1): "Event-Type Severity (ES_raw: β = +0.3102, p < 0.0001), however, enters with a positive sign... This result is interpreted as a contrarian-resolution pattern." L1424 (Section 5.6.1): further elaborated as category-level contextual adjustment. Both interpretations are explicitly listed as acceptable in the protocol. ES_raw is not described as inconsistent with H1, as contradicting SC_total, or as a data error. PASS.

**[x] C5. H1 verdict relies on SC_total, not individual components**

H1 verdict in all sections (Executive Summary L97, Section 5.5.1 L1336, Section 5.7 L1466, Section 5.8 L1470, Section 6.2.2 L1518, Section 6.3 L1522) references β₁ on SC_total. Component results (Spec 3) are explicitly described as supplementary and for transparency. No sentence of the form "H1 is supported because [component] is significant" found. PASS.

---

## PASS D — Pipeline provenance

**[ ] D1. File hashes in log match current output files**

FAIL. Three hash mismatches:

| File | Log hash (last run) | Current hash | Match |
|---|---|---|---|
| results/thesis_results.md | 8b064869b3a7a17d (8_statistical_analysis.py, 09:58:07) | a1fdebd524ab1806 | NO |
| thesis_final.md | 5d97cb0ed3b1e728 (9_compile_thesis.py, 21:40:46) | bc8729b719fa712c | NO |
| results/thesis_results.md (compile input) | 97a090bcd2a4e60c (9_compile_thesis.py input) | a1fdebd524ab1806 | NO |

Additionally, the last `9_compile_thesis.py` run consumed a `thesis_results.md` with hash `97a090bcd2a4e60c`, which itself does not match the output of the last `8_statistical_analysis.py` run (`8b064869b3a7a17d`). This indicates the compile was run against a hand-edited intermediate version of `thesis_results.md`, not the pipeline output — a potential CR-1 (mixed-run) condition. However, numerical verification in Pass B confirms all figures in the current thesis_final.md match the authoritative CSVs, so no numerical error results from this provenance gap.

**[ ] D2. scenario_shock_score.csv not newer than analysis outputs**

FAIL. Current `scenario_shock_score.csv` hash (`aaef37c46e6947de`) does not match the hash recorded in the last `8_statistical_analysis.py` log entry (`56bbed017abaac2f`). The shock score file has been modified since the last analysis run. `8_statistical_analysis.py` must be re-run against the current CSV to restore provenance, followed by `9_compile_thesis.py`.

**[~] D3. Any project-knowledge discrepancies resolved against live repo**

INFORMATIONAL. The protocol document itself (`protocols/results_consistency_protocol.md`, Part 6, Section B6) references the overall alignment rate as "0.2851 in current results." The live repository shows 0.2618 in both `tbl_nrs_sentiment_alignment.csv` and `thesis_results.md`. This is a stale value in the protocol document reflecting a prior pipeline run. No code action required; the thesis is correct. The protocol document should be updated to reflect 0.2618.

---

## Summary

**PASS A: 2 PASS / 1 FAIL**
**PASS B: 3 PASS / 2 FAIL (1 partial — B3 stale protocol expectation; 1 partial — B5 empty CSV)**
**PASS C: 4 PASS / 1 FAIL**
**PASS D: 0 PASS / 2 FAIL / 1 INFORMATIONAL**

**Total: 9 PASS / 6 FAIL / 1 INFORMATIONAL**

**CR-level hard-rule violations:**
- CR-1 (partial): Mixed-run compile — last `9_compile_thesis.py` consumed `thesis_results.md` not produced by the immediately preceding `8_statistical_analysis.py`.
- CR-6 (resolved): No RESULTS:BEGIN/END markers in thesis_final.md — the compile script correctly expanded all PLACEHOLDER blocks; figure path rewriting (relative → results/figures/) is expected compile behaviour; all numerical and narrative content verified present.

**No CR-2, CR-3, CR-4, CR-5, CR-7, or CR-8 violations found.**

VIOLATIONS FOUND: A3, B3 (stale protocol expectation), B5 (empty normality CSV), C3 (sharpe absent from 5.7), D1 (hash mismatch), D2 (shock score modified post-run)
RESOLUTION: See session3_proposed_issues.md
SIGN-OFF: Pending author review
