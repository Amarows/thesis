# Session 4 Quality Diagnostic — Chapter 2

**Scope:** thesis.md lines 222 – 400 (Ch.2 Objectives of the Study).
**Tests executed:** Section A (A-1 – A-8), Section B (B-1 – B-10), Part 4 hallucination spot-check (5 high-risk citations).
**Diagnostic only — no edits made to thesis.md.**

---

## Section A flags

### A-1 — Unsupported claim detection
No flags. Substantive claims are supported by inline citations.

### A-2 — Epistemic framing test
- **L230**: *"…emotionally salient external information shocks can increase cognitive load and compress the time available for deliberation."* — declarative, framed as established fact. While the relationship is well-established, the sentence opens with an "in such environments" qualifier so framing is borderline acceptable. P3.

### A-3 — Assumption-vs-literature test
- **L368 – L370** (Section 2.7): *"The study assumes that:* … *Random assignment of scenarios to conditions is assumed to mitigate systematic learning and order effects ([Charness et al., 2012])."* — the relationship cited (random assignment mitigates order effects) is established methodologically; rephrasing as a literature-supported design choice ("follows the convention established by Charness et al., 2012") rather than an assumption would be more accurate. P3.

### A-4 — Original-vs-established boundary test
No flags. Shock Score and SC_total are consistently flagged as "an original composite indicator developed in this thesis" (L255, L265).

### A-5 — Forward-reference integrity test
No flags. Forward references identify section numbers (e.g., "Section 4.3.5", "Section 2.6.3").

### A-6 — Data source specificity test
No flags.

### A-7 — Cross-reference precision test
No flags. Cross-references precise.

### A-8 — Empirical illustration sourcing test
- **L236**: the Meta Platforms 2 February 2026 illustration states that the announcement "was widely interpreted as outperforming market expectations" — this empirical claim about market interpretation is not sourced; the only attribution is to Interactive Brokers as the price-data provider (L245). P3.

---

## Section B flags

### B-1 — Named citation rule
- **L253**: *"Empirical research in behavioral finance documents evidence that such information shocks can affect decision behavior…"* — vague attribution. Should name Hirshleifer or Elkind directly. P3.

### B-2 — Hyperlink completeness / missing reference
- **L245**: *"From Interactive Brokers (2026)."* — prose mention of a data-source citation that is not in references.md and has no hyperlink. Either add Interactive Brokers as a data-source entry in references.md (with URL `https://www.interactivebrokers.co.uk`) or reframe the figure note to non-citation form ("Source: Interactive Brokers data, retrieved via the IBKR API"). P2.

### B-3 — Duplicate citation rule
No flags.

### B-4 — Citation year / URL consistency
- **L288, L370, L382**: *"[Charness et al., 2012](https://doi.org/10.1016/j.jebo.2011.08.006)"* — the DOI ends in `.08.006`. The correct DOI (verified from publisher Elsevier and matching references.md line 63) is `10.1016/j.jebo.2011.08.009`. Three identical instances of the wrong-DOI URL. **P2.**
- **L255**: cites **Lim, 2025** — references.md has **Lim, 2026**. P2 (cross-document recurring issue tracked once globally).

### B-5 — "Information shock" terminology
No flags.

### B-6 — Shock Score placement rule
Not applicable.

### B-7 — Subsection length rule
- **Section 2.5.1 (L303 – L309)** and **2.5.2 (L311 – L317)** are short two-paragraph subsections containing the hypothesis text plus one explanatory paragraph each — borderline three substantive sentences but the H₀/Hₐ pair is required formatting. **No flag** — the content is structurally necessary.
- **Section 2.7 (L363 – L370)** is two bulleted assumption items; each item is a substantive multi-sentence statement. **No flag.**

### B-8 — Bias-to-study link rule
Not applicable in Ch.2 (no per-bias subsections).

### B-9 — Objectives-to-RQ mapping
**No flag.** Mapping is explicitly stated at L293: *"RQ1 addresses Objective 1 by evaluating both the immediate decision response to information shocks and its downstream portfolio outcome. RQ2 addresses Objective 2 by evaluating the moderating role of the Shock Score on that response."*

### B-10 — SC_total construct validity
Not applicable (Ch.5 test).

---

## Part 4 hallucination spot-check (5 citations)

| # | Citation | Claim location | Claim made | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | Charness et al. (2012), DOI `…08.006` | L288, L370, L382 | within-subject experimental design support; random assignment mitigates order effects | **PARTIAL** | The paper (Gary Charness, Uri Gneezy, Michael A. Kuhn, JEBO 81, 1–8, 2012) supports the claim. The DOI used in the in-text link is incorrect — should be `…08.009`. Reframe as a B-4 URL fix. |
| 2 | Loewenstein et al. (2001) | L249, L378 | "information shocks… activate affective responses that may diverge from, and override, deliberative cognitive assessments of risk" | **SUPPORTED** | The "Risk as Feelings" paper specifically argues that emotional reactions often diverge from cognitive assessments and that when divergence occurs, emotion drives behavior. The thesis phrasing matches the paper. |
| 3 | Jolliffe & Cadima (2016) | L378 | PCA methodology for composite construction | **SUPPORTED** | Comprehensive PCA review that explicitly covers index construction use cases. Methodology citation is fully appropriate. |
| 4 | Angelova et al. (2023) | L265 | "discretionary human overrides of algorithmic recommendations typically degrade rather than improve decision accuracy" | **PARTIAL** | The paper (NBER w31747; Angelova, Dobbie, Yang) is conducted in the **bail / judicial-decision context**, not investment. The paper's main finding — that 90% of judges underperform the algorithm when they make a discretionary override — supports the underlying claim. However, the thesis presents this as a general motivating result without acknowledging the domain. Cross-domain generalisation is plausible but should be flagged in the text. |
| 5 | Doronila (2024) | L275 | "established Likert-type measurement conventions" | **SUPPORTED** | Doronila (2024) is a Likert-scale methodological paper. Citation is appropriate as a methodology reference for single-item Likert design. |

---

## Summary
- Section A flags: 3 (A-2, A-3, A-8).
- Section B flags: 5 (1 × B-1, 1 × B-2, 3 × B-4 — three Charness DOI fixes plus one Lim, tracked globally).
- Part 4: 0 UNSUPPORTED, 2 PARTIAL (Charness DOI, Angelova domain), 3 SUPPORTED.
- No P1 verdicts in Ch.2.
