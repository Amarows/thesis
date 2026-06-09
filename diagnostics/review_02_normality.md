# Review 02 — Normality-Testing Section (defense-critical)

**Branch:** `review/final-review` · **Section:** §5.4 "Tests for Normality and Reliability" (`thesis.md:1257–1275`), with §5.5.1/§5.5.2 inference and §5.8 limitations.
**Date:** 2026-06-09 · **Reviewer:** independent pre-merge examiner (read-only; no recompute, consistency-check only)

## 1. Location and scope

- §5.4 (`thesis.md:1257`) introduces normality + reliability; residual-normality result is stated in prose at `thesis.md:1265`.
- Table 5.6 (residual normality) and Figure 5.6 (histogram + Q-Q) are injected from `results/thesis_results.md` block `tbl_5_6_residuals` (lines 152–171).
- Authoritative result files cross-checked: `results/tables/tbl_normality.csv`, `tbl_h1_main.csv`, `tbl_h2_portfolio.csv`, `tbl_h1_robustness.csv`, and the generated `results/thesis_results.md`.

## 2. Numerical consistency — PASS (all figures reconcile)

| Quantity | Thesis prose | Committed result file | Match |
|---|---|---|---|
| Shapiro-Wilk W (residuals) | 0.9849 (`:1265`) | `tbl_normality.csv` = 0.9849; `thesis_results.md:160` = 0.9849 | ✓ |
| Shapiro-Wilk p (residuals) | 0.0002 | 0.0002 (both) | ✓ |
| N | 424 | 424 | ✓ |
| Residual skew / excess kurtosis | (Table 5.6) 0.0205 / 0.5096 | `thesis_results.md:160` 0.0205 / 0.5096 | ✓ |
| H1 β₁ (Shock Score) | −0.4874 | `tbl_h1_main.csv` −0.4874 | ✓ |
| H1 cluster-robust SE / t / p | 0.1532 / −3.1825 / 0.0015 | 0.1532 / −3.1825 / 0.0015 | ✓ |
| H1 95% CI | [−0.7876, −0.1872] | [−0.7876, −0.1872] | ✓ |
| H1 HC3 SE | 0.0551 (`:1301`) | `tbl_h1_robustness.csv` spec_6_hc3 = 0.0551 | ✓ |
| ShowSC main effect on NRS / p | −0.0787 / 0.4994 (Ch6 `:1454`, Table 5.7) | `tbl_h1_main.csv` show_sc −0.0787 / 0.4994 | ✓ |
| SC×ShowSC interaction p | 0.9358 (`:1454`) | `tbl_h1_robustness.csv` spec_4 = 0.9358 | ✓ |
| H2 τ / SE / t / p | −0.1584 / 0.4826 / −0.3281 / 0.7428 | `tbl_h2_portfolio.csv` option_b portfolio_return identical | ✓ |
| H2 Cohen's d | −0.0591 | −0.0591 | ✓ |
| H2 Option A returns / differential / $ | 1.8986% / 1.4642% / −0.4344% / −$434,400 | `tbl_h2_portfolio.csv` identical | ✓ |

**No numerical error and no internal inconsistency among the figures actually reported in the thesis.** The β₁, SE, t, CI, HC3 SE, τ, and H2 p all match the committed files to four decimals.

### Minor provenance gaps (not blockers)

1. **Table 5.6 vs `tbl_normality.csv` row mismatch.** The generated Table 5.6 (`thesis_results.md:159–160`) shows **two** rows — *Raw NRS response* (W = 0.9455, p < 0.0001) and *Primary H1 residuals* (W = 0.9849, p = 0.0002). The committed `tbl_normality.csv` contains **only** the residuals row. The raw-NRS Shapiro figures (W = 0.9455) are therefore not backed by any committed CSV. The number used in the §5.4 prose (residual W = 0.9849) is fully consistent everywhere, so this is a data-provenance gap, **MINOR**.
2. **Prose/table asymmetry.** The §5.4 prose (`:1265`) cites only the residual test; Table 5.6 additionally reports the raw-NRS test. Harmless, but the prose does not mention the raw-NRS row it sits above. **MINOR.**
3. **`tbl_h2_portfolio.csv` option_a artifact.** In the descriptive Option A row, `sharpe_sc1 = 1.4642` is identical to `return_sc1 = 1.4642` — a probable column-fill artifact in the generator. **Not surfaced in the thesis** (prose cites only Option A returns and dollar impact), so no thesis impact. **MINOR / data hygiene.**

## 3. Interpretation quality for a defense

| Defense criterion | Verdict | Evidence |
|---|---|---|
| Raw bounded-variable normality vs OLS **residual** normality distinguished correctly | **YES** | "the scale is bounded and ordinal, normality testing on raw responses is not appropriate; the standard assumption … concerns residual normality" (`:1259`); reinforced `:1265`. |
| Shapiro rejection framed as a trivial departure, not fatal | **YES** | Inference "based on the asymptotic normality of the OLS estimator combined with two-way cluster-robust SEs"; Figure 5.6 note: "only mild departures from normality." Residual skew 0.0205 / excess kurtosis 0.5096 corroborate. |
| Cluster-robust SEs justified as valid under non-normality | **YES** | "remain valid under non-normal, heteroscedastic, and within-cluster-correlated errors" with appropriate citations (MacKinnon & White 1985; Cameron, Gelbach & Miller 2011; Petersen 2009). |
| HC3-vs-cluster-robust rationale coherent | **YES** | Cluster SE (0.1532) "materially larger than HC3 (0.0551) because it accounts for … within-manager and within-event correlation (ICC 0.84–0.94)"; the more conservative clustered estimate is adopted, and H1 survives the wider interval. Coherent and conservative. |

The section is, on its own terms, statistically sound and unusually careful: it explicitly **declines** the lazy "large-n + CLT makes Shapiro meaningless" move and instead grounds non-reliance on residual normality in the estimator's asymptotics. That is the correct and more defensible framing.

## 4. The three toughest jury questions this section invites

1. **Few-clusters problem (the strongest vulnerability — NOT pre-empted).** The thesis states cluster-robust validity "rests on the **number** of clusters rather than the distribution of the residuals" (`:1265`), but two-way clustering is on **53 respondents and only 24 scenarios**. With ~24 clusters in the event dimension, conventional CRVE asymptotics are in the small-G regime, where SEs can be biased downward and tests over-reject. The text does **not** address whether 24 clusters suffices, nor offer a wild-cluster bootstrap or a small-G correction. *Mitigant the author can deploy (but the text does not currently connect):* H1 is also significant under HC3 (p < 0.0001) and under the respondent within-FE estimator (β = −0.1846, p = 0.0008; Table 5.8), so the conclusion is robust to the SE choice. **Recommend pre-empting explicitly in defense prep.**
2. **Ordinal DV modeled by OLS (partially pre-empted).** NRS is a 7-point ordinal scale analysed with linear OLS. §5.4 correctly argues raw-NRS non-normality is irrelevant, but neither §5.4 nor §5.5 defends OLS over an ordered logit/probit. The justification exists upstream (§2.3.1: single-item Likert treated as interval, citing Bergkvist & Rossiter 2007; Doronila 2025) but is not recalled at the point of inference. A jury asking "why not ordered probit?" would not find a local answer.
3. **Meaning of the Shapiro rejection itself (well pre-empted).** "You reject residual normality at p = 0.0002 — does that not invalidate the t-tests?" The text answers this directly (asymptotic normality + cluster-robust SEs; mild departures shown in Figure 5.6). This question is handled well.

A related presentation point (feeds Stage 3): the three perfectly-collinear control dummies that carry blank SEs in `tbl_h1_main.csv` (`mand_Equity long-short`, `discr_Advisory only`, `discr_Partial`) are **dropped** from the displayed Table 5.7 under the note "Reference categories omitted." Calling collinear-dropped dummies "reference categories" is slightly imprecise; Issue #203 itself lists the "blank-standard-error artefact on the three control covariates" as a Q&A item, so the author is aware. The visible table is clean, but the labeling could invite a question.

## 5. Blocker assessment

- **No statistical error** in any reported figure; full reconciliation with committed result files.
- **No material internal inconsistency** in the thesis numbers (the Table 5.6 ↔ `tbl_normality.csv` row-count gap is MINOR provenance).
- **No CRITICAL blocker** in this section.
- **MAJOR (defense readiness, not a merge blocker):** the few-clusters question is un-pre-empted; strongly recommend adding one sentence tying the H1 conclusion's robustness to HC3 and within-FE estimates, and preparing a wild-cluster-bootstrap answer.
- **MINOR:** raw-NRS row not backed by a committed CSV; prose/table asymmetry; ordered-model rationale not recalled at §5.4/5.5; "reference categories omitted" labeling of collinear-dropped dummies.
