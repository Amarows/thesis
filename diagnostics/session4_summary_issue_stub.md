# [QUAL-DIAG] Diagnostic summary

**Session:** 4 (diagnostic pass — Parts 3 and 4 of the quality diagnostics protocol).
**Scope:** thesis.md Chapters 1 – 6; Section C additionally for Ch.3 and any literature-review sections.
**Date of pass:** 2026-05-21.
**Branch:** `diagnostics/session4-quality-diag`.
**Output artefacts:** six per-chapter diagnostic reports (`diagnostics/session4_quality_diagnostic_ch1.md` through `…ch6.md`), one staged-issues file (`diagnostics/session4_proposed_issues.md`), this summary stub.

---

## Flag counts per protocol code

| Code | Description | Total flags | Per-chapter breakdown |
|---|---|---|---|
| A-1 | Unsupported claim / typo / broken fragment | 5 | Ch.3: 1; Ch.4: 1; Ch.5: 1; Ch.6: 2 |
| A-2 | Epistemic framing (declarative causal) | 4 | Ch.2: 1; Ch.3: 3 |
| A-3 | Assumption-vs-literature | 1 | Ch.2: 1 |
| A-4 | Original-vs-established boundary | 0 | — |
| A-5 | Forward-reference integrity | 1 | Ch.1: 1 |
| A-6 | Data source specificity | 0 | — |
| A-7 | Cross-reference precision | 1 | Ch.6: 1 |
| A-8 | Empirical illustration sourcing | 1 | Ch.2: 1 |
| B-1 | Named citation rule (vague attribution) | 5 | Ch.1: 2; Ch.2: 1; Ch.3: 2 |
| B-2 | Hyperlink completeness / missing reference | 11 | Ch.2: 1; Ch.3: 5; Ch.4: 2; Ch.5: 3 |
| B-3 | Duplicate prose+bracket citation | 9 | Ch.3: 9 |
| B-4 | Citation year / URL inconsistency | 8 | Ch.1: 3 (Lim); Ch.2: 4 (Charness × 3, Lim × 1); Ch.3: 1 (Hirshleifer URL) — plus Lim normalisation cluster |
| B-5 | "Information shock" terminology | 0 | — |
| B-6 | Shock Score placement (Ch.3) | 0 | — |
| B-7 | Subsection length / bold-as-header | 3 | Ch.3: 1; Ch.5: 1; Ch.6: 1 |
| B-8 | Bias-to-study link | 0 | — |
| B-9 | Objectives-to-RQ mapping | 0 | — |
| B-10 | SC_total construct-validity framing | 1 | Ch.5: 1 |
| HR-6 | Prose citation without hyperlink (cluster) | ~25 | Ch.3: ~22; Ch.5: 2; Ch.4: 1 |
| C-1 | Attribution layer separation | 1 | Ch.3: 1 |
| C-2 | Standard term attribution | 2 | Ch.3: 2 |
| C-3 | Literature-to-construct chain | 1 | Ch.3: 1 |
| C-4 | Gap claim calibration | 0 | — |
| C-5 | Section intro paragraph rule | 3 | Ch.3: 3 |

---

## Flag counts per chapter

| Chapter | Section A | Section B | Section C | Part 4 verdicts |
|---|---|---|---|---|
| Ch.1 Introduction | 1 (A-5) | 5 (2×B-1, 3×B-4) | n/a | 3 SUPPORTED, 2 PARTIAL, 0 UNSUPPORTED |
| Ch.2 Objectives | 3 (A-2, A-3, A-8) | 5 (1×B-1, 1×B-2, 3×B-4) | n/a | 3 SUPPORTED, 2 PARTIAL, 0 UNSUPPORTED |
| Ch.3 Literature Review | 4 (1×A-1, 3×A-2) | 50+ items: 5×B-2, ~25×HR-6, 9×B-3, 5×B-4, 1×B-7 | 5 (1×C-1, 2×C-2, 1×C-3, 3×C-5) | 3 SUPPORTED, 1 PARTIAL, **1 UNSUPPORTED (P1)** |
| Ch.4 Data Collection | 1 (A-1) | 4 (1×B-2 P1, 1×B-2 P2, 2×HR-6) | n/a | 4 SUPPORTED, **1 UNSUPPORTED (P1)** |
| Ch.5 Analysis | 2 (A-1, A-2) | 5 (2×B-2, 1×B-7, 1×B-10, 1 cluster HR-6) | n/a | 1 SUPPORTED, 1 PARTIAL, 2 UNSUPPORTED-at-reference-level (P2) |
| Ch.6 Conclusions | 3 (2×A-1, 1×A-7) | 2 (1×B-2, 1×B-7) | n/a | 4 SUPPORTED, 1 PARTIAL, 0 UNSUPPORTED |

---

## Part 4 hallucination spot-check — UNSUPPORTED verdicts (P1)

Two UNSUPPORTED verdicts confirmed in this diagnostic pass:

1. **Huang, Roesler & Reske (2020) — FinBERT** (Ch.4 L800, L812). The cited author triple does not correspond to any verifiable FinBERT paper; the bracket DOI `10.1145/3583780.3615272` does not resolve to a FinBERT publication. references.md has Yang et al. (2020) for FinBERT. Issue #1 in the staged-issues file.

2. **Bikhchandani & Sharma (2001) and Bikhchandani et al. (1992)** (Ch.3 L432). Neither reference is in references.md. The bracket DOI for the 1992 paper resolves correctly but the reference has no `file` column and cannot be verified offline; the 2001 reference has no DOI or entry at all. Issue #2 in the staged-issues file.

The Hirshleifer (2015), Henderson (2018), Statman (2019), Loewenstein (2001), Angelova (2023), Charness (2012), and Lim (2026) cases are all addressed as Section B flags (B-2 / B-4) or as PARTIAL verdicts requiring claim-language reframing rather than citation removal (per HR-1). The Loewenstein (2001) "complement vs override" risk flagged in the protocol is **not present** — the thesis uses "diverge from, and override" which matches the paper.

---

## Per-finding issue titles (29 staged)

P1 (2):
1. `[B-2] Ch.4.3 Replace fabricated FinBERT citation (Huang, Roesler & Reske, 2020)`
2. `[B-2] Ch.3.2 Add missing references — Bikhchandani & Sharma (2001) and Bikhchandani, Hirshleifer & Welch (1992)`

P2 (12):
3. `[B-4] Cross-document normalisation of Lim 2025 vs Lim 2026`
4. `[B-4] Ch.2.3/2.7/2.8 Correct Charness et al. (2012) DOI from .08.006 to .08.009`
5. `[B-4] Ch.3.2 Normalise Hirshleifer (2015) URL to annurev DOI`
6. `[B-2] Ch.4.5 Add missing reference MacKinnon & White (1985)`
7. `[B-2] Ch.5.5.1 Replace or add reference for Mason et al. (1986)`
8. `[B-2] Ch.5.9.4 Correct author name and add reference for ICC guideline (Koo & Mae → Koo & Li, 2016)`
9. `[B-2] Ch.3.6.3 Reconcile RavenPack reference year (2017 vs 2023)`
10. `[B-2] Ch.3.5 Add missing reference Rigobon (2003)`
11. `[B-10] Ch.5.6.1 Add construct-validity framing for SC_total β₁ coefficient`
12. `[A-1] Ch.6.3.1 Repair broken sentence at L1394`
13. `[A-1/C-2] Ch.6.7.2 Add citation for automation bias claim`
14. `[B-2] Ch.2.2 Reframe or cite Interactive Brokers (2026) figure-note attribution`

P3 (15 representative — full backlog deeper):
15. `[A-7] Ch.6.8 Correct cross-reference from Chapter 2 to Chapter 3`
16. `[B-3] Ch.3.2 Remove duplicate prose+bracket citations (9 instances)`
17. `[HR-6] Ch.3 Add hyperlinks to prose citations across §3.2–§3.6 (cluster)`
18. `[C-5] Ch.3 Add intro paragraphs to §3.3, §3.4, and §3.5`
19. `[C-1] Ch.3.1 Clarify attribution layer in causal-pathway synthesis paragraph`
20. `[B-7] Ch.3.6.3 Convert bold-as-header subsections to proper headers or remove bold`
21. `[B-2] Ch.4.3.5 Add hyperlink to prose Baker & Wurgler (2006) citation`
22. `[A-1] Ch.5.2.3 Cite Kaiser criterion or Jolliffe & Cadima for PCA diagnostic threshold`
23. `[B-7] Ch.5.9.3 Expand "Stated Preference Validity" subsection or merge into §5.9.1`
24. `[A-5] Ch.1.1 Add forward reference for first use of "information shock"`
25. `[A-8] Ch.2.2 Source the Meta 2 Feb 2026 market-interpretation claim`
26. `[B-7] Ch.6.3.1 Demote header level from ## to ###`
27. `[B-1] Ch.3.1 Replace vague "the literature reviewed" closing in §3.2.5`
28. `[C-2] Ch.2/Ch.3 Cite foundational source for "procyclical rebalancing" on first use`
29. `[A-1] Ch.3.2 Repair stray closing parenthesis at L459`

---

## Notes for the revision pass (Session 5)

- All proposed fixes in `session4_proposed_issues.md` are written to respect HR-1 (no citation removal), HR-2 (meaning preservation), HR-3 (no scope expansion), and HR-5 (minimal intervention).
- Two P1 items require new references.md entries (FinBERT replacement; Bikhchandani × 2) and corresponding in-text fixes — these should be addressed first.
- The Lim 2025/2026 cluster is a single batchable edit (~10 targeted `str_replace` calls) and would close five distinct line-level flags at once.
- The HR-6 prose-without-hyperlink cluster in Ch.3 is the largest single revision workload and is best executed in section-grouped batches (§3.2, §3.3, §3.4, §3.5, §3.6) with one commit per section.
- B-10 construct-validity framing in Ch.5 is a one-sentence addition with high reader-visible impact.
- Compilation discipline reminder: edits go to `thesis.md` only; `9_compile_thesis.py` regenerates `thesis_final.md` from `thesis.md` + `results/thesis_results.md`. Per CLAUDE.md, never edit `thesis_final.md` directly.
