# Final Pre-Merge Review — Verdict

# VERDICT: GO-WITH-FIXES — no CRITICAL blocker found; one MAJOR cleanup (remove 49 leaked author comments) must be done before merge to main.

**Branch reviewed:** `review/final-review` (tracking `origin/Amarows/thesis`), the branch slated for merge to `main` (9 commits ahead; diff touches `thesis.md`, `thesis_final.md`, `8_statistical_analysis.py`, `9_compile_thesis.py`, result files, and the residual-normality figure).
**Date:** 2026-06-09 · **Reviewer:** independent examiner (read-only; statistics consistency-checked against committed result files, not recomputed; pipeline not re-run).

## Decision rationale

By the per-stage blocker definitions in the review brief, **zero CRITICAL blockers exist**: no statistical error or internal numeric inconsistency, no missing required subchapter, no residual overclaim in the body, no unresolved placeholder, and no missing-reference citation. The six-chapter structure is correct, the null-H2 framing is honest throughout, the main body is ~29,354 words (>20,000), and the defense deck is 16:9, animation-free, light-background, with all seven required content points and honest H1/H2 reporting. The outstanding items are MAJOR/MINOR cleanups. Per the decision rule, that is **GO-WITH-FIXES**.

The one item that must not ship as-is: **49 internal `[//]:` author comments remain in `thesis.md` and leak verbatim into the generated `thesis_final.md`** (including candid asides and typos). They do not render in standard pandoc→DOCX output and no claim is wrong, so this is MAJOR rather than CRITICAL — but merging them into the canonical source is a professional defect and trivially fixable.

---

## Punch list (ordered by severity)

### MAJOR

1. **Remove all 49 `[//]:` author comments before merge.** `thesis.md` lines 32, 84, 88, 92, 96, 100, 104, 114, 118, 122, 128, 138, 145, 153, 157, 159, 163, 171, 175, 181, 191, 195, 199, 203, 211, 217, 225, 231, 235, 249, 251, 257, 263, 273, 289, 293, 326, 340, 354, 378, 397, 1420, 1430, 1434, 1440, 1446, 1452, 1456, 1464. All leak into `thesis_final.md`. *Fix:* delete the comment lines in `thesis.md` (content was already addressed — see review_01) and re-run `9_compile_thesis.py`. If the author deliberately keeps them for a later round (per project memory), make that an explicit decision; they should not enter `main` silently. (Stage 1)

2. **Few-clusters inference vulnerability (defense prep / optional text).** §5.4 grounds validity on "the number of clusters," but two-way clustering uses only **24 scenario clusters**. *Fix:* add one sentence noting H1 is also significant under HC3 (p < 0.0001) and the respondent within-FE estimator (β = −0.1846, p = 0.0008), and prepare a wild-cluster-bootstrap answer. (Stage 2)

3. **Deck slide 15 (normality appendix) is 8 pt — unreadable if projected.** *Fix:* split across two slides at ≥24 pt, or treat strictly as a printed leave-behind and answer verbally. (Stage 5)

### MINOR

4. **3 uncited references** — `French & Roll, 1986`; `Thaler & Benartzi, 2004`; `Swiss Business School, 2026`. Cite in text or remove from `references_apa.md` / `references.md` for APA list hygiene. (Stage 4)
5. **Title vs null H2** — *"Reducing Emotional Biases…"* with H2 null is defensible (research aim, body is honest) but invites a jury question; prepare a Q&A answer. (Stage 3)
6. **`thesis.md:169`** — "catalogue" → US "catalog". (Stage 3)
7. **`thesis.md:1363/1365`** — plain-text "beta1/beta3" vs β₁/β₃ used elsewhere; and "p = <0.0001" typo at 1365. (Stage 3)
8. **Table 5.6 provenance** — the "Raw NRS" row (W = 0.9455) in `thesis_results.md` is not backed by `tbl_normality.csv` (residuals row only). Harmless but inconsistent. (Stage 2)
9. **Collinear covariate labeling** — three perfectly collinear control dummies (blank SE in `tbl_h1_main.csv`) are dropped from Table 5.7 under "Reference categories omitted"; slightly imprecise wording (they are collinear-dropped, not reference categories). (Stage 2)
10. **Ch5/Ch6 title overlap** — Chapter 5 "Analysis and **Conclusions**" duplicates "Conclusions" with Chapter 6. (Stage 3)
11. **Exec-summary one-page fit** — ~550 words; confirm it fits one page in the Word `.docx` (out of scope here). (Stage 3)
12. **Deck slide 1** author block at 20 pt (title metadata, below 24 pt min); **deck slide 9** "directionally consistent" phrasing vs the displayed negative return coefficient (cite Sharpe direction instead). (Stage 5)
13. **Verify on the SBS PowerPoint machine** — Calibri font and the references-slide hanging indent (not resolvable by static parsing). (Stage 5)

---

## Stage-by-stage summary

| Stage | Focus | Result | Worst item |
|---|---|---|---|
| 1 | Inline comment audit | 49 comments, all substantively ADDRESSED (0 NOT-ADDRESSED), but all leak into `thesis_final.md` | MAJOR |
| 2 | Normality section | All figures reconcile with result files; interpretation sound | MAJOR (few-clusters, defense prep) |
| 3 | Content & grade rubric | 6-chapter structure ✓, Ch6 complete ✓, null-H2 integrity ✓, clean academic writing | MINOR |
| 4 | Compilation & citations | 0 unresolved placeholders, 0 missing-reference citations, 29,354 words | MINOR (3 uncited refs) |
| 5 | Presentation | 16:9, no motion, light bg, 7 content points, honest H1/H2 | MAJOR (8 pt appendix slide) |

**Bottom line:** the thesis is substantively sound and defensible. Clear the MAJOR comment-removal item (and ideally the few-clusters sentence and the 8 pt slide) and this is a clean GO.
