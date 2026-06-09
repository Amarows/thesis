# Review 01 — Inline Author-Comment Audit

**Branch:** `review/final-review` · **File audited:** `thesis.md` (authored) and `thesis_final.md` (generated)
**Date:** 2026-06-09 · **Reviewer:** independent pre-merge examiner (read-only)

## Convention detected

Author comments use the Markdown null-link form:

```
[//]: # ( ...comment text... )
```

This is distinct from the pipeline markers `<!-- PLACEHOLDER:id -->` / `<!-- RESULTS:id -->`, which are **excluded** from this audit. A total of **49** author comments exist in `thesis.md`: 41 in the front matter / Chapter 1–2 region (lines 32–397) and 8 in Chapter 6 (lines 1420–1464).

## Headline findings

| # | Finding | Severity |
|---|---------|----------|
| 1 | **All 49 comments leak verbatim into `thesis_final.md`** (grep count = 49). The compiler (`9_compile_thesis.py`) copies them through unchanged. They include candid internal notes ("H2 effectively is not statistically significant"), informal asides ("hey hey…", "wow wow…"), and spelling errors. | **MAJOR** |
| 2 | One comment is **malformed**: `thesis.md:1420` / `thesis_final.md:1651` — `[//]: # ( Instead of "summarizes" I would use word "connects"` has **no closing `)`**. A link-reference definition is single-line, so the title is left unterminated — a latent rendering bug. | MINOR |
| 3 | **Substantive content:** every one of the 49 comments is substantively ADDRESSED or N/A in the prose that follows it. **No NOT-ADDRESSED comment leaves an incorrect or unsupported claim standing.** Two are PARTIAL (a missing citation; residual repetition concerns) — neither is a blocker. | — |

### On render risk (examiner judgment)

`[//]: # (...)` is the standard CommonMark/pandoc comment idiom: it parses as an *unused link-reference definition* and is normally **not rendered** to PDF/DOCX. So if the committee-facing document was compiled through pandoc, the comments most likely do **not** appear in the printed thesis. The author's manual Word `.docx` is out of scope (not committed), so this cannot be verified here.

However, per the review brief these comments "must be REMOVED before submission," and merging this branch to `main` bakes 49 internal review notes into the canonical source files. Anyone reading `thesis.md` / `thesis_final.md` directly (e.g., on GitHub) sees the full internal commentary. **Recommendation: strip all 49 before merge** (a project memory notes the author may have intended to keep them for a later editing round — confirm intent with the author; if intentional, this drops to a non-blocking note, but it should not ship in the merged-to-main state without a decision).

**Net Stage-1 verdict:** No CRITICAL blocker from comment *content*. The leakage of 49 internal comments into the generated file is a **MAJOR** cleanliness issue to resolve before merge.

---

## Per-comment detail

Classification key: **ADDRESSED** / **PARTIAL** / **NOT ADDRESSED** / **N/A** (praise or no action implied) / **UNCLEAR**. Line numbers are `thesis.md`.

### Front matter, Foreword, Executive Summary

| Line | Comment (gist) | Class | Evidence in following text |
|---|---|---|---|
| 32 | Foreword: focus on H1 first; H2 not significant; simplify | ADDRESSED | "central and most robust result … this indicator predicts a systematic shift"; "did not produce a statistically significant effect" |
| 84 | Exec summary: more formal; H1 first | ADDRESSED | Leads with measuring/predicting; "measures how intense such an event is and predicts how strongly it will move a manager's risk decisions" |
| 88 | Too complex; simplify/split | ADDRESSED | Para now plain: "motivated by a gap between behavioral finance theory and practice" |
| 92 | "NRS" unknown to reader; SC does not *change* NRS, it predicts/measures; H2 is *intended* not actual | ADDRESSED | NRS defined inline ("seven-point measure of how much the manager intends to reduce or increase exposure"); framed "predict", and "change that intended decision" |
| 96 | Drop "quasi-experiment"/"within-subject" jargon | ADDRESSED | "Because every manager saw both conditions, the design separates the effect…" — jargon removed in exec summary |
| 100 | Mention secondary data; under-reaction not over-; component heterogeneity | ADDRESSED | "situational risk aversion under stress rather than … over-reaction"; "components do not act uniformly" |
| 104 | Recommendations: intended vs real decisions on trading floor | ADDRESSED | "measures managers' intended decisions … future research should examine actual decisions on a trading floor" |

### Chapter 1

| Line | Comment (gist) | Class | Evidence |
|---|---|---|---|
| 114 | Start too complex; simplify | ADDRESSED | "Investment decisions are often described as exercises in rational calculation." |
| 118 | Bridge behavioral theory → investment decisions | ADDRESSED | Para 120 ties bias to "investment portfolio management" consequences |
| 122 | Need reference? | ADDRESSED | Shefrin (2002) citation added in para 124 |
| 128 | When did we switch to financial markets? (flow) | ADDRESSED | Transition added: "do not arise in isolation; they are activated by the environment in which managers work" |
| 138 | Add examples for information events; we detect under-reaction | ADDRESSED (examples) | "for example, an earnings surprise, an analyst rating change, a regulatory ruling…". Under-reaction FYI reconciled in results/Ch6, not locally |
| 145 | Introduce business value; value-oriented; simplify | ADDRESSED | "that measure has direct operational value: it allows an investment process to anticipate bias before a decision is made" |
| 153 | Too complex/AI-ish; simplify | ADDRESSED | "Modern portfolio management was built on the assumption that investors are rational." |
| 157 | Reference required for the first statement | **PARTIAL** | Para 161 EMH claim ("public information is incorporated into prices rapidly and accurately") still uncited; EMH *is* cited in adjacent para 155 (Fama, 1970). Minor. |
| 159 | Global: extend results to decision-making generally (EMBA) | ADDRESSED | Para 205 + §6.3.1 argue transferability "to other settings in which professionals make high-stakes decisions" |
| 163 | "well known"? academic style? | ADDRESSED | Reworded to "widely recognized" |
| 171 | "survive"/"persist in professional contexts" repeated; simplify | ADDRESSED | Single use: "whether such biases persist among professionals, and finds that they do" |
| 175 | Drop jargon (IPS, rule-based protocols); plain examples | ADDRESSED | "from the written rules a firm sets for itself, to the checks applied at the moment a decision is made" |
| 181 | What is "computational analytics"? = BI? | ADDRESSED | Changed to "business analytics" |
| 191 | Change header; this is about measuring biases | ADDRESSED | 1.3.1 = "Measuring Behavioral Responses…"; 1.3.2 = "Moderating…" — split as suggested |
| 195 | Primary goal = understand/manage; changing is 1.3.2 | ADDRESSED | "The principal purpose … is to measure whether, and how strongly…" |
| 199 | "good. very good." | N/A | Praise, no action |
| 203 | Unclear; cautiously extend to other areas | ADDRESSED | "the underlying approach … is, in principle, transferable to other settings" |
| 211 | Simplify; we moderate decisions | ADDRESSED | "as a tool to moderate decisions rather than to forecast returns" |
| 217 | Need word "Literature" in header? | ADDRESSED | Header 1.4.1 = "Academic Contribution to Behavioral Finance" — no "Literature" |
| 225 | Mention Chapter 3 here? avoid | ADDRESSED | Reworded to "within the reviewed literature" (no explicit Ch3 ref) |
| 231 | Too bold; algo funds do use sentiment; "exclusively" bad | ADDRESSED | "Quantitative and algorithmic funds increasingly apply news-sentiment analytics, but these tools are generally built to identify return opportunities" |
| 235 | IPS argument — add reference | ADDRESSED | Statman (2019) added |
| 249 | Scope order: financial decisions → international large-firm managers → scenario/stock; S&P = large not mid | ADDRESSED | Para 253 reordered exactly: "international population … rather than individual or retail investors … U.S. large-capitalization equities (S&P 500 constituents)" |
| 251 | Mention U.S. stocks + international managers in foreword/exec summary | ADDRESSED | Exec summary: "53 international professional equity portfolio managers … large-capitalization U.S. equities" |
| 257 | Simplify | ADDRESSED | Para 259 reads cleanly; primary vs secondary data delineated |
| 263 | Horizon = hours | ADDRESSED | "those made within hours of a discrete information event" |
| 273 | We DO use proprietary feeds (IBKR/Benzinga); "anchored in" too complex; link data↔method | ADDRESSED | "publicly available secondary data – market prices and news obtained from Interactive Brokers and Benzinga"; "anchored in" removed; data→method link added |

### Chapter 2

| Line | Comment (gist) | Class | Evidence |
|---|---|---|---|
| 289 | Not every PM faces pressure; use neutral term | PARTIAL | Softened with "may need to reassess … often under considerable time pressure"; retained "portfolio managers" rather than "financial decision makers" |
| 293 | "good. measure → decompose → change" | N/A | Framing approval; para 295 follows the structure |
| 326 | Objectives repeated ("emotionally salient … activate biases") | PARTIAL | Restructured around "three links"; some restatement remains — subjective, minor |
| 340 | Objectives repeated; jump to core message | PARTIAL | "The first objective is to measure whether the intensity…"; restructured but still builds up — minor |
| 354 | Title needs refinement (value added from dashboard?) | ADDRESSED | 2.3.2 = "Evaluating the Effect of Displaying the Shock Score" |
| 378 | Add intuitive interpretation — SC = a measure of bias | ADDRESSED | "the Shock Score can be read as a measure of how strongly an event is likely to provoke emotionally driven, biased decision-making" |
| 397 | Explain what the dashboard is / contains | ADDRESSED | Bullet defines dashboard + its four signals (sentiment, severity, persistence, protocol) |

### Chapter 6

| Line | Comment (gist) | Class | Evidence |
|---|---|---|---|
| 1420 | "summarizes" → "connects" (**comment is malformed — no closing `)`**) | ADDRESSED | "Section 6.2 **connects** the findings…" |
| 1430 | Most important paragraph in 6.2.1 — polish | ADDRESSED | Para 1432 sharpened: states the gap and how the Shock Score fills it |
| 1434 | Too complex; β repeated; move coefficient to 6.2.2 | ADDRESSED | 6.2.1 now qualitative; β₁ appears in 6.2.2 (para 1442) — moved as suggested |
| 1440 | Intuitive interpretation for β₁ | ADDRESSED | "each one-unit increase in the Shock Score is associated with roughly a half-point reduction in Net Risk Stance" |
| 1446 | Objectives repeated; SC independent of NRS; decompose; literature over/under-reaction | ADDRESSED | "independent of the manager's response; it does not act on the decision, but anticipates it"; decomposition in 1450; "situational risk aversion … rather than to overreact" |
| 1452 | Intuitive interpretation for β₂; which table is p=0.4994? | ADDRESSED | "about one-sixteenth of a scale point … (p = 0.4994; **Table 5.7**)" |
| 1456 | Don't mention initial design / 12 unimplemented questions | ADDRESSED | No mention of 12 questions; "eight scenarios per block and a realized sample of 53 respondents" |
| 1464 | SC is shock-level not stock-level; transferable; simplify | ADDRESSED | "defined at the level of the shock, not the stock … which makes the approach portable, in principle, to other settings" |

## Summary counts

- ADDRESSED: 42
- PARTIAL: 4 (lines 157, 289, 326, 340 — all MINOR, none alter a substantive claim)
- N/A (praise/framing): 3 (lines 199, 293; plus 1420 instruction satisfied)
- NOT ADDRESSED: 0
- UNCLEAR: 0

## Blocker assessment

- **No CRITICAL blocker** arises from comment content: zero NOT-ADDRESSED items; no comment flags a substantive claim that remains wrong.
- **MAJOR (pre-merge):** 49 internal author comments persist in `thesis.md` and leak verbatim into `thesis_final.md`. Remove before merge to `main` (or obtain explicit author decision to retain).
- **MINOR:** malformed comment at `thesis.md:1420` (missing closing `)`); residual repetition flagged by the author at lines 326/340; uncited EMH sentence at para 161 (line 157).
