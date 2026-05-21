# Session 4 Quality Diagnostic — Chapter 4

**Scope:** thesis.md lines 681 – 1158 (Ch.4 Research Data and Primary Data Collection).
**Tests executed:** Section A (A-1 – A-8), Section B (B-1 – B-10), Part 4 hallucination spot-check (5 high-risk citations).
**Diagnostic only — no edits made to thesis.md.**

---

## Section A flags

### A-1 — Unsupported claim detection
- **L1139**: *"HC3 robust standard errors are applied throughout; the HC3 correction provides a finite-sample improvement over HC1/HC2 and is the recommended default for small-to-medium samples (MacKinnon and White, 1985)."* — substantive methodological claim with a prose citation to **MacKinnon and White (1985)** which is **not in references.md** and has no hyperlink. P2 (also B-2).

### A-2 — Epistemic framing test
No flags. Ch.4 is methodological/design and uses appropriately neutral framing.

### A-3 — Assumption-vs-literature test
No flags.

### A-4 — Original-vs-established boundary test
- Shock Score, SC_total, Persistence score and Protocol trigger are consistently presented as original ("developed in this thesis", "designed for this thesis", L921, L929). **No flag.**

### A-5 — Forward-reference integrity test
No flags. Forward and back references precise (e.g., "as defined in Section 2.3.1", "Section 4.5", "Section 4.4.4").

### A-6 — Data source specificity test
**No flag.** Each variable is mapped to its data source: market data → Interactive Brokers (Table 4.2); news → Benzinga (Table 4.2); sentiment → FinBERT (Table 4.2/4.4); survey → primary (Section 4.4); event-type severity baseline → IBKR intraday (Section 4.3.5).

### A-7 — Cross-reference precision test
No flags. References specify section numbers throughout.

### A-8 — Empirical illustration sourcing test
Not directly applicable in Ch.4 (no case illustrations).

---

## Section B flags

### B-1 — Named citation rule
No flags. Ch.4 uses direct prose citations or markdown citations throughout; vague attribution phrases are absent.

### B-2 — Hyperlink completeness / missing references
- **L800, L812** (Table 4.2 row and Section 4.3.3): citation to **"FinBERT (Huang, Roesler & Reske, 2020)"** with bracket-link DOI `10.1145/3583780.3615272`. The author triple "Huang, Roesler & Reske" is **not in references.md**. The DOI does not resolve to any known FinBERT paper. references.md (line 79) has **Yang et al., 2020** with arXiv URL `https://arxiv.org/abs/2006.08097` for FinBERT. Either:
  - (a) replace the in-text citation with **Yang et al. (2020)** matching references.md; or
  - (b) add a verified FinBERT reference (e.g., Araci, 2019 arXiv:1908.10063; Liu, Huang & Xu, 2020 IJCAI; or Huang, Wang & Yang, 2023 *Contemporary Accounting Research*) to references.md and correct the in-text citation accordingly.

**This is a P1 issue:** the cited author/DOI combination has no resolvable source. Two in-text instances. Fix the source attribution and the bracket DOI together.

- **L854**: prose *"following the established approach of using PCA to derive composite indices in finance (Baker & Wurgler, 2006)"* — Baker & Wurgler (2006) IS in references.md (line 61); the in-text citation has no hyperlink. P3.
- **L1139**: prose *"(Cameron, Gelbach, & Miller, 2011; Petersen, 2009)"* and *"(MacKinnon and White, 1985)"* — Cameron et al. (2011) and Petersen (2009) are in references.md but the prose citations lack hyperlinks. **MacKinnon & White (1985)** is not in references.md and has no hyperlink. P2 (missing reference).

### B-3 — Duplicate citation rule
No flags.

### B-4 — Citation year / URL consistency
- **L800 / L812** FinBERT DOI fabrication — overlaps with B-2 finding.
- **L1139** Cameron/Gelbach/Miller cited as 2011 — references.md has "Cameron, Gelbach & Miller, 2011" — consistent. **No flag.**

### B-5 — "Information shock" terminology
Ch.4 uses technical terms ("shock bar", "shock timestamp", "shock return", "Shock Score") which the protocol explicitly preserves. Standalone conceptual "shock" usage is acceptable in Ch.4 per the B-5 exception. **No flag.**

### B-6 — Shock Score placement rule
Not applicable (Ch.4 is the authoritative definition location).

### B-7 — Subsection length rule
- **§4.4.6 "Confound Controls"** (L1034 – L1038): contains two substantive paragraphs. **No flag.**
- All other Ch.4 subsections contain multiple substantive paragraphs.

### B-8 — Bias-to-study link rule
Not applicable in Ch.4.

### B-9 — Objectives-to-RQ mapping
Not applicable.

### B-10 — SC_total construct validity
Not applicable (Ch.5 test).

---

## Part 4 hallucination spot-check (5 citations)

| # | Citation | Claim location | Claim made | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | Huang, Roesler & Reske (2020), DOI `10.1145/3583780.3615272` | L800 (Table 4.2), L812 (Section 4.3.3) | FinBERT pre-trained financial language model used for sentiment scoring | **UNSUPPORTED / P1** | No paper by "Huang, Roesler & Reske (2020)" on FinBERT exists. The DOI does not resolve to a FinBERT paper. The established FinBERT references are Araci (2019, arXiv:1908.10063), Liu, Huang & Xu (2020, IJCAI), Yang/Huang/Mayo (2020), and Huang/Wang/Yang (2023, *Contemporary Accounting Research*). references.md has Yang et al. (2020) for FinBERT. The Ch.4 in-text citation appears to be fabricated or misattributed. **P1.** |
| 2 | DeMiguel, Garlappi, & Uppal (2009) | L775 | "the 1/N portfolio performs competitively with optimized strategies in out-of-sample evaluation" | **SUPPORTED** | DeMiguel, Garlappi, Uppal (2009) *Review of Financial Studies* "Optimal Versus Naive Diversification: How Inefficient Is the 1/N Portfolio Strategy?" — the paper's headline finding matches. Reference is in references.md (line 76). |
| 3 | Cameron, Gelbach & Miller (2011) | L1139 | two-way clustering approach for inference | **SUPPORTED** | Cameron, Gelbach, Miller (2011) "Robust Inference with Multiway Clustering" (*JBES*) is the canonical reference for two-way clustering. Reference in references.md (line 80). |
| 4 | Petersen (2009) | L1139 | clustering in panel data | **SUPPORTED** | Petersen (2009) "Estimating Standard Errors in Finance Panel Data Sets" (*RFS*) is the canonical reference for clustering approaches in finance panel data. Reference in references.md (line 81). |
| 5 | Loewenstein et al. (2001) | L901 | "tone polarity of news language activates emotional responses that may diverge from, and override, deliberative cognitive assessments of risk, as established by Loewenstein et al. (2001)" | **SUPPORTED** | The risk-as-feelings paper explicitly argues that "emotional reactions to risky situations often diverge from cognitive assessments of those risks. When such divergence occurs, emotional reactions often drive behavior." The thesis phrasing matches the paper. (Protocol's known-risk-case caveat about "complement vs override" wording is addressed — the thesis uses "override", not "complement".) |

---

## Summary
- Section A flags: 1 (A-1 / overlaps with B-2 on MacKinnon & White).
- Section B flags: 4 (Huang/Roesler/Reske P1; MacKinnon & White P2; 2 × prose-without-hyperlink P3).
- Part 4: **1 UNSUPPORTED / P1 (Huang/Roesler/Reske FinBERT)**, 4 SUPPORTED.
- B-6 (Shock Score placement) is fully respected — authoritative definition appears in §4.3.5 / §4.3.6 with all formulas and component definitions in this chapter.
