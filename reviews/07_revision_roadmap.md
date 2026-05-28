# Revision Roadmap — thesis_final.md

**Decision**: Major Revision · **Round**: 1 · **Date**: 2026-05-29
**Calibration**: Strong EMBA behavioural-finance thesis, SBS Handbook v1.8 (AY 2025–26).

This roadmap is prioritised by severity (CRITICAL → MAJOR → MINOR). Each item states **what is wrong**, the **exact location**, and the **proposed fix**. Items are traceable to the reviewer reports (`reviews/01`–`05`) and the editorial decision (`reviews/06`).

> **Editor's framing note (binding on all items below):** The non-significant ShowSC→NRS effect and the non-supported H2 are **legitimate, honestly-reported findings**, not defects. Nothing in this roadmap asks the author to manufacture a positive result. The CRITICAL is a *framing* fix: align the claims with the evidence. The contribution to foreground is **"evidence on when a decision-support signal does and does not change professional behaviour, plus a validated shock-measurement instrument."**

---

## CRITICAL (must fix before acceptance)

### CR-1 · Title/value-proposition contradicts the evidence
- **What is wrong**: The title *Reducing Emotional Biases in Investment Portfolio Management* and the abstract promise a demonstrated debiasing intervention, but the dashboard's effect is null: ShowSC → NRS β = −0.0787, p = 0.4795 (Table 5.7); SC_total × ShowSC β = −0.0067, p = 0.9358 (Table 5.8); H2 not supported on return (p = 0.7428), Sharpe (p = 0.6050), Sortino (p = 0.7934) (Table 5.9).
- **Location**: Title; Abstract; Chapter 1 (framing); Chapter 6 (conclusions).
- **Proposed fix**: Reframe to a measurement + conditional-evidence study. Suggested title direction: *"Measuring Information Shocks and Testing a Decision-Support Signal for Emotional Bias in Portfolio Management."* Abstract leads with the supported H1 association and presents the dashboard result as an **informative null**. Conclusions state the contribution explicitly (instrument + conditional behavioural evidence). **No claim of demonstrated bias reduction or outcome improvement may remain.**
- **Source**: DA C1 (CRITICAL); EIC W3; R2 W3; R3 W1. **Resolves the iron-rule CRITICAL.**

---

## MAJOR (strongly required; entail re-analysis or substantive rewrite)

### MA-1 · Standard errors must match the pre-specified design (HC3 → two-way cluster)
- **What is wrong**: Design/CLAUDE.md specify "HC3 / two-way cluster-robust SEs," but all tables report HC3 only. HC3 ignores the heavy clustering the thesis documents (ICCs ≈ 0.8425 / 0.9026 / 0.9369, Table 5.5), overstating precision ~3×. Independently reproduced: under two-way cluster (respondent × scenario), β(SC_total) = −0.4874, SE = 0.1532, t = −3.1825, p = 0.0015 (vs HC3 SE 0.0551, t −8.8452).
- **Location**: §5, Tables 5.7 and 5.8; methods SE description.
- **Proposed fix**: Make two-way cluster-robust SEs the **primary** specification across Tables 5.7–5.8; demote HC3 to a robustness row; restate the (unchanged) conclusion in clustered terms. Align all "strength of evidence" language to the clustered t.
- **Source**: R1 W1 (Critical-severity in R1's report); DA C5. *Conclusion-preserving (per editorial Disagreement 2).*

### MA-2 · Composite coherence: severity component sign + ceiling + dimensionality
- **What is wrong**: (a) In the component decomposition, es_raw relates **positively** to NRS (β = +0.3102, p < 0.0001) while se_e (−1.2904) and ai_e (−0.5668) are negative and ac_e is n.s. (0.0235, p = 0.1585) — yet es_raw loads +0.2944 on a PC1 that relates negatively to NRS. (b) es_raw is capped at 10.0000 for 7 of 24 scenarios (ceiling artefact). (c) PC1 explains only 50.38% variance; the second eigenvalue (≈1.17) exceeds 1, and the PCA uses only n = 24 scenarios.
- **Location**: §5.2 (PCA diagnostics, Table 5.2); §5 robustness (Table 5.8); `survey/metadata/scenario_shock_score.csv` (es_raw).
- **Proposed fix**: Document and, if needed, repair the es_raw severity mapping (resolve the 10.0 ceiling); report H1 with es_raw excluded from the PCA; justify single-component retention (scree/parallel analysis or theory) and report the full eigenvalue spectrum; acknowledge the n = 24 stability limitation. Discuss the opposite-sign result substantively (which shock dimensions actually move managers).
- **Source**: R1 W2/W3; DA C3.

### MA-3 · Bound all claims to "stated intention"; strengthen NRS validity
- **What is wrong**: H1, H2, and the simulated portfolios all rest on a single-item, study-specific 7-point stated-intention DV (NRS) elicited in hypothetical scenarios, with no revealed-behaviour anchor and no convergent-validity check.
- **Location**: §2.3.1 (line 323, NRS definition); §4 (measurement); §6 (discussion/conclusions).
- **Proposed fix**: Bound every behavioural/outcome statement to "stated risk intention under hypothetical scenarios." Build an explicit validity paragraph using the available manipulation-check and usefulness-rating items plus the Bergkvist & Rossiter (2007) rationale, and clarify whether NRS is doubly-concrete (direction *and* intensity). Flag real-money validation as primary future work.
- **Source**: R2 W1; R3 W1; DA C4.

### MA-4 · Re-position the contribution around what held (and theorise the null)
- **What is wrong**: The contribution is currently built around the intervention that did not work, under-selling the robust H1 association and the reusable instrument; the null is treated defensively rather than as a named-mechanism result.
- **Location**: Chapter 1 (contribution statement); Chapter 3 (theoretical framing); Chapter 6 (discussion).
- **Proposed fix**: State the contribution as (i) a validated continuous shock index and (ii) evidence that shock intensity tracks stated risk intention, with the dashboard null as bounded secondary evidence. Add a short theoretical account of the predicted debiasing mechanism, then interpret the null via algorithm aversion / advice-discounting in experienced professionals.
- **Source**: EIC W4; R2 W2/W3; R3 W2; DA steelman.

### MA-5 · SBS rubric diagnostics — reliability coefficient + skewness/kurtosis
- **What is wrong**: No Cronbach's alpha (ICC is reported instead; no "Cronbach" in text) and no skewness/kurtosis, both expected by the SBS Handbook (Ch.5 reliability; Ch.4 distribution). Shapiro–Wilk rejects residual normality (W = 0.9849, p = 0.0002, Table 5.6), which the robust SEs do not address.
- **Location**: §4 (distributional diagnostics); §5 (reliability, around Table 5.5/5.6).
- **Proposed fix**: Add Cronbach's α for any multi-item scale, or a two-sentence justification that α is inapplicable to a single-item DV (retaining ICC as the correct repeated-measures statistic). Add skewness/kurtosis for NRS and SC_total. State that non-normality is mitigated by N = 424 (CLT) and is orthogonal to the SE choice.
- **Source**: EIC W1/W2; R1 W5.

### MA-6 · H2 Sortino — reconcile n and stabilise or demote
- **What is wrong**: Sortino regression n = 29, but the note states "Computed for 97 of 106 respondent-condition pairs"; the estimate is uninformative (τ = 9.4847, SE = 36.2226, 95% CI [−61.5102, 80.4797]).
- **Location**: §5, Table 5.9 (and footnote).
- **Proposed fix**: State exactly which pairs enter the Sortino regression and why (reconcile 29 vs 97/106); winsorise extreme downside-deviation denominators or report Sortino descriptively only; frame H2 inference on return and Sharpe.
- **Source**: R1 W4.

---

## MINOR (improves quality; not decision-fatal)

### MI-1 · Citation inconsistencies
- **What is wrong / Location / Fix**:
  - "Lim (2026)" used for two distinct works → lines 644 & 645 → disambiguate as Lim (2026a)/(2026b).
  - ICC guideline cited as "Koo & Mae, 2016" (line 1361) vs "Koo & Li, 2016" (line 1566) → standardise to the correct **Koo & Li (2016)**.
  - Doronila year mismatch: in-text "2024" (line 323) vs reference "2025" (line 1755) → reconcile in-text and reference-list years.
- **Source**: R2 W4; EIC minor.

### MI-2 · Appendix 4 (survey instrument) internal inconsistencies
- **What is wrong / Location / Fix**: "24 stocks" (line ~2027) vs "remaining 35 holdings" (line ~2029) → reconcile the holdings count; stray "+1.08" missing its percent sign (line ~2089) → add "%".
- **Source**: EIC minor.

### MI-3 · Feasibility / deployment subsection
- **What is wrong / Location / Fix**: Data-dependency, latency, licensing (Benzinga/IBKR/FinBERT) and the compliance status of an automated "Halt" recommendation are not addressed → add a short deployment subsection in Chapter 6; label the dashboard a research prototype; consider an architecture diagram (sources → signals → recommendation).
- **Source**: R3 W3.

### MI-4 · SDG-10 claim
- **What is wrong / Location / Fix**: The reduced-inequality claim (§6.8, lines ~1662–1682) may be backwards given the instrument's licensed-data/NLP dependencies → soften to a conditional ("could reduce inequality *if* delivered through an accessible channel"), add the access-asymmetry caveat, or re-anchor on SDG 8.
- **Source**: R3 W4.

### MI-5 · Reproducibility of the deposited panel
- **What is wrong / Location / Fix**: `results/analysis_panel.csv` stores SC columns as all-NaN; the authoritative values are merged at runtime from `survey/metadata/scenario_shock_score.csv`, so the panel alone cannot reproduce H1 → persist the merged SC into the deposited panel, or document the merge step in the methods.
- **Source**: R1 detailed comments.

---

## Sign-off checklist (for the revised submission)
- [ ] CR-1 resolved: no title/abstract/conclusion sentence claims demonstrated bias reduction or outcome improvement.
- [ ] MA-1–MA-6 addressed with change-marked text and updated tables.
- [ ] MI-1–MI-5 corrected.
- [ ] Point-by-point response letter (adopted / reason-not-adopted) with new section/line cross-references.
- [ ] The informative null is foregrounded as a contribution, not minimised.
