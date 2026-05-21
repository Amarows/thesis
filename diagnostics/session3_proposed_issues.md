# Session 3 — Proposed Issues
**Generated:** 2026-05-21
**Branch:** diagnostics/session3-consistency
**Audit source:** session3_consistency_checklist.md

All issues follow the shared issue body template. Priority mapping: CR-1 through CR-8 violations → P1; numeric mismatches in Pass B → P1 if interpretation affected, P2 if rounding-only; Pass D hash mismatches → P1; other → P2.

---

## Issue 1

**Title:** [D1] D1 – thesis_results.md and thesis_final.md hash mismatch with pipeline log
**Priority:** P1
**Pass:** D
**Check:** D1

**Description:**
Both `results/thesis_results.md` and `thesis_final.md` were committed to the repository after the most recent recorded pipeline run, and their current SHA-256 hashes do not match any pipeline log entry.

| File | Log hash | Current hash |
|---|---|---|
| results/thesis_results.md | 8b064869b3a7a17d (8_statistical_analysis.py, 2026-05-20T09:58:07) | a1fdebd524ab1806 |
| thesis_final.md | 5d97cb0ed3b1e728 (9_compile_thesis.py, 2026-05-20T21:40:46) | bc8729b719fa712c |

Additionally, the last `9_compile_thesis.py` run consumed `thesis_results.md` with hash `97a090bcd2a4e60c`, which does not match the output of the last `8_statistical_analysis.py` run (`8b064869b3a7a17d`). This is a potential CR-1 (single-pipeline-run) violation: the compiled thesis was generated from a hand-edited intermediate `thesis_results.md`, not from the pipeline output.

**Mitigating finding:** Pass B numerical verification confirms all figures in the current `thesis_final.md` match the authoritative CSVs exactly. The provenance gap does not introduce numerical errors in the current state, but it breaks the auditability chain.

**Recommended action:** Re-run `8_statistical_analysis.py` (after resolving Issue 2 re: shock score CSV), then re-run `9_compile_thesis.py` against the fresh `thesis_results.md` output, and commit both. Do not hand-edit `results/thesis_results.md` between pipeline runs.

**Edit target:** Pipeline scripts `8_statistical_analysis.py` and `9_compile_thesis.py` (re-run); `results/thesis_results.md` and `thesis_final.md` (outputs to be regenerated).

---

## Issue 2

**Title:** [D2] D2 – scenario_shock_score.csv modified after last 8_statistical_analysis.py run
**Priority:** P1
**Pass:** D
**Check:** D2

**Description:**
The current `survey/metadata/scenario_shock_score.csv` has hash `aaef37c46e6947de`, which does not match the hash `56bbed017abaac2f` recorded in the last `8_statistical_analysis.py` log entry (2026-05-20T09:58:07). The shock score CSV — the upstream input to both `3_survey_assembly.py` and `8_statistical_analysis.py` — has been modified since the last analysis run.

Per protocol D2: if the shock score CSV is newer than the analysis output, `8_statistical_analysis.py` must be re-run.

**Recommended action:** Run `8_statistical_analysis.py` against the current `scenario_shock_score.csv`. Then run `3_survey_assembly.py` to regenerate `diagnostics/survey_assembly_report.md` and re-verify Pass A1. Then run `9_compile_thesis.py`. Commit all outputs with a single run-log record.

**Edit target:** Pipeline re-run sequence; no edits to thesis text required pending re-run results.

---

## Issue 3

**Title:** [A3] A3 – Pipeline run log does not post-date thesis_results.md commit
**Priority:** P1
**Pass:** A
**Check:** A3

**Description:**
Protocol pre-flight (and A3) requires the most recent pipeline log timestamp to post-date the mtime of `results/thesis_results.md`. The most recent log entry is `2026-05-20T21:40:46` (`9_compile_thesis.py`), but `results/thesis_results.md` was committed at `2026-05-21T09:42:52Z` — approximately 12 hours later.

This violation is the observable symptom of the hand-edit described in Issue 1. It means the pipeline log cannot serve as evidence that the currently committed `thesis_results.md` was machine-generated from the current `scenario_shock_score.csv`.

**Recommended action:** Resolve by re-running the full pipeline in sequence (Issues 1 and 2). After the re-run, the log timestamp will post-date all output file commits.

**Edit target:** Pipeline re-run (no thesis text edit).

---

## Issue 4

**Title:** [C3] Section 5.7 – sharpe_ratio secondary H2 outcome absent from Interim Conclusions
**Priority:** P2
**Pass:** C
**Check:** C3

**Description:**
Protocol C3 requires that when H2 is not supported on the primary outcome (`portfolio_return`) but a secondary outcome (`sharpe_ratio`) exists, both facts must appear in Section 5.7 Interim Conclusions.

Section 5.7 (L1466, `thesis_final.md`) currently states only:

> "H2 – that the Shock Score dashboard moderates the risk-return profile of simulated portfolios: **the null hypothesis H2₀ was not rejected** (τ = −0.1584, p = 0.7428) in the Option B individual-portfolio regression."

The `sharpe_ratio` row in Table 5.5 (τ = 0.879, SE = 1.6994, p = 0.6050, Cohen's d = 0.0712, `h2_supported = False`) is not referenced in the Section 5.7 narrative, nor in Sections 6.2.2 or 6.3. The result is not suppressed (it appears in Table 5.5 and Figure 5.4) but the verbal summary omits it.

Note: in the current data, `sharpe_ratio` is also not statistically significant (p = 0.6050), so the protocol's framing of it as "the secondary finding is directionally supportive" is accurate (τ = +0.879, positive direction) even though p > 0.05.

**Recommended action:** Edit `thesis.md` Section 5.7 (the `s5_7_interim` placeholder block in `thesis.md`, or the corresponding block in `results/thesis_results.md` if auto-generated) to add a sentence such as: "On the secondary Sharpe ratio outcome, the treatment effect is directionally positive (τ = 0.879) but does not reach statistical significance in the current sample (p = 0.6050); this result is consistent in direction with the primary portfolio return finding."

**Edit target:** `thesis.md` — Section 5.7 narrative (or `results/thesis_results.md` block `s5_7_interim` if auto-generated by pipeline).

---

## Issue 5

**Title:** [B5] tbl_normality.csv empty – Shapiro-Wilk residual normality values unverifiable
**Priority:** P2
**Pass:** B
**Check:** B5

**Description:**
`results/tables/tbl_normality.csv` exists but contains only a header row — no data. Thesis Table 5.4c (L1304–L1310, `thesis_final.md`) reports:

| | Shapiro-Wilk W | p-value |
|---|---|---|
| Primary H1 residuals | 0.9849 | 0.0002 |

These values appear in `results/thesis_results.md` block `s5_4_normality` (L89–L128) and are transcribed correctly into `thesis_final.md`. However, because `tbl_normality.csv` is empty, the source-of-truth hierarchy (Part 1 of protocol) has no CSV file at rank 3 or 4 for normality statistics. The values can only be traced to `thesis_results.md` (rank 5), not to a table CSV.

**Recommended action:** Update `8_statistical_analysis.py` to write Shapiro-Wilk W and p-value for the primary H1 residuals to `results/tables/tbl_normality.csv`. Suggested schema: `test,statistic,p,normality_rejected`. After re-run, verify thesis values against CSV.

**Edit target:** `8_statistical_analysis.py` — add tbl_normality.csv output block.

---

## Issue 6

**Title:** [B3] tbl_h2_portfolio.csv – h2_supported flag for sharpe_ratio inconsistent with protocol expectation
**Priority:** P2
**Pass:** B
**Check:** B3

**Description:**
Protocol B3 specifies: "`sharpe_ratio` h2_supported — Must be `True`." The CSV contains `h2_supported = False` for the `sharpe_ratio` row (p = 0.6050 > 0.05, so the pipeline correctly set the flag to `False`).

The protocol expectation is stale: it was written when the sharpe_ratio result was anticipated to be statistically significant. In the current data the result is not significant. The thesis correctly reports `False`, consistent with the CSV.

This is a protocol-document maintenance issue, not a thesis error.

**Recommended action:** Update `protocols/results_consistency_protocol.md` Section B3 to remove the hard requirement that `h2_supported` must be `True` for `sharpe_ratio`, replacing it with: "must match CSV value." Also update the protocol's known-recurring-risks table (Part 8) to note that sharpe_ratio h2_supported reflects pipeline threshold logic, not a fixed expected outcome. Separately, consider whether the `8_statistical_analysis.py` h2_supported logic should be reviewed for correct threshold application.

**Edit target:** `protocols/results_consistency_protocol.md` — Part 4, Section B3.

---

## Summary Stub — [CONSIST] Diagnostic summary

**Title:** [CONSIST] Diagnostic summary — Session 3 consistency audit

**PASS/FAIL counts:**
- Pass A: 2 PASS / 1 FAIL
- Pass B: 3 PASS / 2 FAIL
- Pass C: 4 PASS / 1 FAIL
- Pass D: 0 PASS / 2 FAIL / 1 INFORMATIONAL
- **Total: 9 PASS / 6 FAIL / 1 INFORMATIONAL**

**CR-level hard-rule violations:**
- CR-1 (partial): `9_compile_thesis.py` was run against a `thesis_results.md` not produced by the immediately preceding `8_statistical_analysis.py`. See Issue 1.
- CR-6: Resolved — no RESULTS:BEGIN/END markers in `thesis_final.md` is correct compiled-output behaviour; all blocks verified present with figure path rewrite only.
- CR-2, CR-3, CR-4, CR-5, CR-7, CR-8: No violations.

**Per-finding issue titles:**
1. [D1] D1 – thesis_results.md and thesis_final.md hash mismatch with pipeline log (P1)
2. [D2] D2 – scenario_shock_score.csv modified after last 8_statistical_analysis.py run (P1)
3. [A3] A3 – Pipeline run log does not post-date thesis_results.md commit (P1)
4. [C3] Section 5.7 – sharpe_ratio secondary H2 outcome absent from Interim Conclusions (P2)
5. [B5] tbl_normality.csv empty – Shapiro-Wilk residual normality values unverifiable (P2)
6. [B3] tbl_h2_portfolio.csv – h2_supported flag for sharpe_ratio inconsistent with protocol expectation (P2)

**Additional findings (non-issue, informational):**
- Duplicate paragraph in Section 5.6.1 (L1420 and L1422 in thesis_final.md): stale paragraph not removed during editing; L1420 uses British spelling and an older Spec5 framing. No numerical impact. Edit target: `thesis.md` Section 5.6.1.
- `spec_1_quintiles` p-value displays as `nan` in Table 5.4 robustness rows: pandas NaN artefact. No numerical error; display only. Edit target: `8_statistical_analysis.py` table formatting.
- Protocol document itself contains stale alignment rate reference (0.2851 vs current 0.2618). D3 informational. Edit target: `protocols/results_consistency_protocol.md` Part 4 Section B6.
