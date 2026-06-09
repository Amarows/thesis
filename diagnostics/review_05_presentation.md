# Review 05 — Presentation Review

**Branch:** `review/final-review` · **Against:** Issue #203 criteria
**Deck:** `Defense_Presentation_Malashonak.pptx` (780 KB), attached in the single comment on issue #203 (author Amarows, 2026-06-09). Downloaded and parsed with `python-pptx` 1.0.2. **17 slides.**
**Date:** 2026-06-09 · **Reviewer:** independent pre-merge examiner (read-only)

## Verification status

Download **succeeded**; all checks below are EVIDENCE-BASED from the deck XML, not MANUAL — except font family (Calibri) and on-screen contrast rendering, which python-pptx cannot fully resolve and are marked accordingly.

## 1. Format compliance

| #203 rule | Result | Evidence |
|---|---|---|
| 16:9 aspect ratio (not 4:3) | **PASS** | 13.33 × 7.50 in → ratio 1.7778 (= 16:9) |
| No dark / low-contrast backgrounds | **PASS** | Master background = scheme `bg1` (theme background-1, i.e., white/light); no slide overrides it. No dark fills found. |
| ~3–4 bullets per slide; no paragraphs | **PASS** | Content slides (2, 5, 8, 9, 10, 11, 12) each carry 4 short bullets; no paragraph blocks. |
| No animations / transitions | **PASS** | `transition=False` and no `<p:timing>`/anim on **all 17 slides**. |
| 24 pt minimum body text (28 default) | **MOSTLY PASS** | Master body defaults: lvl1 = **28 pt**, lvl2 = 24 pt, lvl3 = 20 pt; title = 38 pt. Main content bullets inherit 28 pt. **Exceptions below.** |
| Left-aligned, end-of-bullet periods | **PASS (observed)** | Bullets end with periods consistently (e.g., slides 2, 8–12). |
| Calibri type style | **NOT VERIFIED** | Font family not resolvable from runs; presumed template default. Confirm on the SBS machine. |

### Font-size exceptions (the only real format defects)

1. **Slide 15 (Appendix 1 — Normality): body text is 8 pt.** This is far below the 24 pt floor and unreadable from the back row if projected. It is a backup/appendix slide (intended for the anticipated normality Q&A), but #203 flags normality as a likely jury topic, so if it is shown it must be legible. **MAJOR (scoped to a backup slide):** split the content across two slides at ≥24 pt, or treat it strictly as a printed leave-behind and answer verbally.
2. **Slide 1 (Title): author/ID/mentor/date block is 20 pt.** Below the 24 pt minimum, though this is conventional title-slide metadata. **MINOR.**

## 2. Required content (Handbook p.28 — all seven present)

| Required point | Slide | 
|---|---|
| What did you study (topic)? | 2 — Topic and Motivation |
| Why did you pick it? | 2 — "grounded in professional risk-management practice, where this gap is persistently observed" |
| What was your hypothesis? | 4 — H1 and H2 stated |
| What did you find out? | 8 (H1) and 9 (H2) |
| What are your conclusions? | 10 — Conclusions and Recommendations |
| Personal lessons learned? | 12 — Personal Lessons Learned |
| Ethical implications of conclusions? | 11 — Ethical Implications |

**All seven covered.**

## 3. H1 / H2 reported honestly — PASS

- **Slide 8 "Finding 1: H1 Supported":** "Shock Score coefficient = −0.4874 (p = 0.0015)" — matches `tbl_h1_main.csv`. ✓
- **Slide 9 "Finding 2: H2 Not Supported":** "Dashboard treatment effect = −0.1584 (p = 0.7428), not statistically significant … attributed primarily to limited statistical power, not to an absence of effect." Matches `tbl_h2_portfolio.csv` and the thesis framing. ✓ Honest, non-overclaimed.

**MINOR caveat on Slide 9 wording:** the bullet displays the portfolio-return coefficient (τ = −0.1584, *negative*) and also states the estimate is "directionally consistent with the hypothesized moderation mechanism." The directional-consistency claim actually rests on the *Sharpe-ratio* outcome (τ = +0.8790, per thesis §5.7), not on the negative return coefficient shown. A sharp jury could note the displayed coefficient is negative. Recommend either citing the Sharpe direction explicitly or dropping the "directionally consistent" phrase. Not a blocker.

## 4. Structure & supporting slides

- Title slide (1): title, name, student ID, matriculation, mentor, degree, date — **complete**.
- Supporting graphics: Slide 3 (Meta intraday shock example), Slide 6 (Research Framework), Slide 7 (Scenario/Dashboard example), plus appendix graphics (16 return-prediction, 17 SC decomposition).
- **References slide (13):** present, with at least one APA citation (FinBERT, Yang et al., 2020). Since citations appear on slides, a references slide is required — and it is present. **PASS.** (Confirm the reference uses a hanging indent on the SBS machine — not resolvable here.)
- **Closing slide (14 "Thank You"):** present to leave displayed during Q&A. **PASS.**

## 5. Deck ↔ thesis numeric consistency — PASS

Slide 15 appendix figures match Table 5.6 exactly: Raw NRS (skew −0.1846, excess kurtosis −0.2561, W = 0.9455, p < 0.0001) and Primary H1 residuals (skew 0.0205, excess kurtosis 0.5096, W = 0.9849, p = 0.0002). Slide 8/9 coefficients match the result files. No drift between deck and thesis.

## 6. Blocker assessment

- **No CRITICAL blocker** in the deck: 16:9, light backgrounds, no motion, all seven content points, honest H1/H2, references + closing slides present, 28 pt main body.
- **MAJOR (backup slide):** Slide 15 normality appendix at 8 pt is unreadable if projected — enlarge/split or use as a printed leave-behind.
- **MINOR:** Slide 1 author block at 20 pt; Slide 9 "directionally consistent" phrasing vs the negative displayed coefficient; Calibri font and references-slide hanging indent not machine-verifiable here (confirm on the SBS PowerPoint setup, per #203).
