# Review 03 — Content & Grade-Rubric Review

**Branch:** `review/final-review` · **Against:** Issues #200, #201, #204
**Date:** 2026-06-09 · **Reviewer:** independent pre-merge examiner (read-only)

## 1. Six-chapter structure — PASS (jury hot-button)

| Chapter | Title in `thesis.md` | Standard? |
|---|---|---|
| 1 | Introduction | ✓ |
| 2 | Objectives of the Study | ✓ |
| 3 | Literature Review | ✓ |
| 4 | Research Data and Primary Data Collection | ✓ (descriptive variant of "methodology/data") |
| 5 | Analysis and Conclusions | ✓ (see MINOR note) |
| 6 | Conclusions and Recommendations | ✓ |

- **References** (`# References`, line 1566) and **Appendices 1–4** (lines 1572+) are **not numbered as chapters** — satisfies the #200 jury hot-button.
- **MINOR:** Chapter 5 is titled "Analysis and **Conclusions**", which overlaps the Chapter 6 title "**Conclusions** and Recommendations". Not a structural violation, but a sharp jury may note the duplicated "Conclusions". Title was signed off under the closed #202; flagging only.

### Chapter 6 required subchapters — all present and correctly ordered

6.1 Chapter Introduction · 6.2 Summary of Findings (6.2.1 Secondary, 6.2.2 Primary) · 6.3 Overall Conclusions (+6.3.1 Theoretical/Methodological Contributions) · 6.4 Recommendations · 6.5 Areas for Future Research · 6.6 Lessons Learned · 6.7 Ethical Considerations (6.7.1, 6.7.2) · 6.8 SDG Implications (6.8.1 SDG 8, 6.8.2 SDG 10) · 6.9 Chapter Conclusion. **No missing required subchapter.**

- §6.6 Lessons Learned correctly uses the **first person** (required by handbook p.14 / #201) and covers both the subject matter and the research/writing process (data-engineering reality, LLM-as-instrument, the 12→8 scenario reduction and its power cost). Note: the author comment at line 1456 ("do not mention initial design") referred to §6.3 — and §6.3 indeed does not; mentioning the 12→8 reduction in §6.6 is appropriate and not a conflict.
- §6.7 Ethical Considerations addresses the ethics of the **findings** (algorithmic decision support, automation bias) — **not** the survey process — exactly as #201 requires.
- §6.8 SDG: SDG 8 and SDG 10 explicit, cited to the UN 2030 Agenda.

## 2. Null-H2 integrity — PASS (no residual overclaim in the body)

The prior CRITICAL item (align title/abstract/exec-summary/conclusions with H1 supported, H2 null) is satisfied throughout the body:

| Location | Quote | Honest? |
|---|---|---|
| Foreword (`:36`) | "did not produce a statistically significant effect in the present sample" | ✓ |
| Exec Summary (`:102`) | "not resolved in this sample … attributed mainly to limited statistical power rather than to a confirmed absence of effect" | ✓ |
| §5.6.2 (`:1387`) | "do not support a statistically significant incremental effect" | ✓ |
| §5.7 (`:1392`) | "**the null hypothesis H2₀ was not rejected** (τ = −0.1584, p = 0.7428)" | ✓ |
| §6.3 (`:1454`) | "The dashboard … showed no measurable value … an informative null" | ✓ |
| §6.4 (`:1484`) | "The H2 null counsels caution: no behavioral value of the dashboard was demonstrated" | ✓ |
| §6.8.1 (`:1545`) | "The SDG 8 contribution is therefore **prospective rather than demonstrated**" | ✓ |
| §6.8.2 (`:1555`) | "given the H2 null, did not establish a behavioral benefit even in the professional setting" | ✓ |
| §6.9 (`:1559`) | "does not show a statistically significant effect … no detectable effect … this informative null" | ✓ |

**No residual overclaim quote was found in the body.** H1 language stays associational/predictive ("statistically significant negative predictor", "associated with"), appropriate for a regression on an ex-ante measured regressor.

### One residual tension (MINOR, defensible — recommend Q&A readiness)

The **title** — *"Reducing Emotional Biases in Investment Portfolio Management"* — uses "Reducing", whereas the *reduction/moderation* hypothesis (H2) is null. The title reads as the research **aim/topic** (the thesis measures and predicts bias as a precondition to reducing it, and tests a reduction tool that did not show an effect), and the body never claims the tool succeeded. This is defensible and #201 ("title reconciled with null H2") is closed. However, a jury can fairly ask "your title promises reduction but H2 is null." Recommend a prepared answer; not a blocker.

## 3. Executive Summary

- Previews H1 (supported, β₁ = −0.4874, p = 0.0015) and H2 (null, τ = −0.1584, p = 0.7428) **accurately** (`:86`–`:106`).
- Self-contained; states problem, two research questions, method, results, conclusion, and headline recommendation.
- **MINOR (verify in Word, out of scope here):** the summary runs ~5 substantial paragraphs (~550 words). At the handbook's double-spacing this may exceed a single page; #201's "fits on one page" box is checked and final layout was done manually in Word, which this review cannot inspect. Flag for the author to confirm one-page fit in the `.docx`.

## 4. Academic-writing spot-check (#204)

Scans run over `thesis.md` prose (author `[//]` comments excluded from prose judgments):

| Check | Count | Notes |
|---|---|---|
| "the author" / "the researcher" (self-reference) | **0** | Clean |
| Contractions (don't/isn't/it's/…) | **0** in prose | Only appear inside `[//]` author comments |
| Sentence-initial FANBOYS | **0** | "For example,"/"For each"/"For this reason" are prepositional, not conjunctions; one line-initial "And" is inside a comment |
| "like" used for "such as" | **0** in prose | Both hits are inside `[//]` comments |
| First person outside Ch6 lessons learned | **0** improper | Only Authentication (`:16`,`:22`) and AI Disclosure (`:1580`,`:1592`) declarations + §6.6 (required); line 908 "Type-**I** error" is a false positive |
| Non-US spelling | **1** | "catalogue" (`:169`) → US "catalog" |
| Unhedged absolutes / hype ("clearly evident", "seminal", "proves", …) | **0** | Interpretation is consistently hedged ("interpreted cautiously", "noted as an avenue", "contingent on the current sample") |

Additional MINOR mechanics:
- **Notation drift:** §5.6.1 uses plain-text "beta1 = -0.4874" / "beta3" / "beta = +0.3102" (`:1363`,`:1365`) whereas the rest of the thesis uses β₁/β₃. The project convention (#198) is LaTeX symbols in prose. Cosmetic.
- **Typo:** "p = <0.0001" (`:1365`) — stray "= <".

These #204 items are **MINOR and not pervasive** (the brief itself classes such items minor unless pervasive). Overall the prose is clean, US-English, hedged, third-person, with first person correctly confined to declarations and the lessons-learned section.

## 5. Rubric coverage (#200/#201 Applied Knowledge)

- **Critical thinking / conclusions validity:** strong — honest null, decomposed-component sign heterogeneity interpreted, contrarian-judgment diagnostic (alignment 0.2618) tied to the ES_raw sign. ✓
- **Strategy formulation:** §6.4 gives concrete, tiered recommendations (individual managers / risk governance / institutional deployment / research prototype). ✓
- **Ethical & social responsibility:** §6.7 + §6.8. ✓
- **Management theory application:** prospect theory, mean–variance, algorithm aversion (Dietvorst 2015; Angelova 2023), dual-process. ✓
- **Managing technologies:** Shock Score positioned explicitly as a research prototype (FinBERT, PCA, dashboard). ✓
- **Diversity in communications:** gender-neutral throughout; accessible framing. ✓

## 6. Blocker assessment

- **No CRITICAL blocker.** Six-chapter structure correct; all Chapter 6 subchapters present; null-H2 integrity holds with no residual overclaim in the body.
- **MINOR:** title-vs-null-H2 tension (defensible, prep a Q&A answer); Ch5/Ch6 "Conclusions" wording overlap; exec-summary one-page fit to confirm in Word; "catalogue" non-US spelling (`:169`); plain-text beta notation in §5.6.1; "p = <0.0001" typo (`:1365`).
