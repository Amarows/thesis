# Session 4 Quality Diagnostic — Chapter 1

**Scope:** thesis.md lines 106 – 221 (Ch.1 Introduction).
**Tests executed:** Section A (A-1 – A-8), Section B (B-1 – B-10), Part 4 hallucination spot-check (5 high-risk citations).
**Diagnostic only — no edits made to thesis.md.**

---

## Section A flags

### A-1 — Unsupported claim detection
No flags. All substantive claims in Ch.1 are supported by inline markdown citations.

### A-2 — Epistemic framing test
No flags. Ch.1 paragraphs consistently frame relationships under investigation using "may", "is associated with", "is interpreted as", or "examines whether" — investigative framing is preserved.

### A-3 — Assumption-vs-literature test
No flags. No "this study assumes" phrasing in Ch.1.

### A-4 — Original-vs-established boundary test
No flags. Shock Score is appropriately deferred to Ch.4 ("the detailed construction and operationalisation of the indicator are presented in Chapter 4", L174).

### A-5 — Forward-reference integrity test
- **L120 ("information shock")**: the term is used substantively before being formally defined in Ch.2 L325 and Ch.3 L409. The first use at L120 has no explicit forward pointer. Severity P3.

### A-6 — Data source specificity test
No flags. Ch.1 does not introduce variables or measurement instruments.

### A-7 — Cross-reference precision test
No flags. Cross-references in Ch.1 specify chapter and section ("Section 4.3.5", "Chapter 5").

### A-8 — Empirical illustration sourcing test
No flags. Ch.1 contains no specific case illustrations.

---

## Section B flags

### B-1 — Named citation rule (vague attribution)
- **L120**: *"Empirical research on attention-driven trading shows that…"* — vague attribution. Replace with named attribution; reference list already includes Da et al. (2011) and Engelberg & Parsons (2009) which are cited later in the sentence; promote one to named subject of the clause. P3.
- **L130**: *"institutional trading data shows that institutions tend to trade in the direction…"* — replace with "Ben-Rephael et al. (2024) show that…". Source already cited. P3.

### B-2 — Hyperlink completeness
No flags. Every citation in Ch.1 is in markdown bracket form `[Author, Year](URL)`.

### B-3 — Duplicate citation rule
No flags. No prose mention + bracket-link duplicate of the same author/year in any sentence.

### B-4 — Citation year consistency
- **L156, L168, L180**: cite **Lim, 2025** with DOI `10.1080/15427560.2025.2609644`. references.md (line 55) lists this same DOI as **Lim, 2026**. The published version (Journal of Behavioral Finance) was online 30 January 2026. Either every in-text instance must be normalised to **Lim, 2026** (matching references.md) or references.md must be changed to 2025. Three instances in Ch.1; further instances in Ch.2 (L255), Ch.3 (L525, L571, L576, L601, plus Table 3.1 rows L591 vs L592 internal mismatch), Ch.6 (L1378). Severity P2 — recurring across the document.

### B-5 — "Information shock" terminology
No flags. Ch.1 consistently uses "information shock" or "external information shock".

### B-6 — Shock Score placement rule
Not applicable (Ch.1 is not Ch.3).

### B-7 — Subsection length rule
No flags. Each level-3 subsection in Ch.1 contains at least three substantive sentences.

### B-8 — Bias-to-study link rule
Not applicable in Ch.1 (no per-bias subsections; bias discussion is at thematic level).

### B-9 — Objectives-to-RQ mapping
Not applicable (Ch.2 test).

### B-10 — SC_total construct validity
Not applicable (Ch.5 test).

---

## Part 4 hallucination spot-check (5 citations)

| # | Citation | Claim location | Claim made | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | Tetlock (2007) | L114 | "loss-averse market participants react more strongly to negative news than to comparable positive news" | **SUPPORTED** | Paper documents that negative media sentiment predicts temporary decline in market returns with subsequent rebound, consistent with asymmetric reaction. |
| 2 | Coates & Herbert (2008) | L114 | "emotional and physiological responses to market stress can measurably degrade decision quality even among experienced traders" | **SUPPORTED** | Paper specifically measures endogenous steroids on a London trading floor and links cortisol levels to risk-taking. |
| 3 | Henderson et al. (2018) | L158, L172 | "structured pre-commitment mechanisms… can reduce emotional reactivity and improve decision consistency" | **PARTIAL** | Paper is a continuous-time optimal-stopping model with prospect-theory preferences under pre-commitment; it models stop-loss strategies and disposition effect implications, not an empirical or behavioral debiasing study. "Pre-commitment" is a modelling assumption, not an intervention demonstrated to reduce emotional reactivity. Match is conceptual, not empirical. Severity P3. |
| 4 | Statman (2019) | L114, L158, L168 | "structured pre-commitment mechanisms… can reduce emotional reactivity and improve decision consistency" | **PARTIAL** | The "Second Generation" monograph treats normal investors and offers guidance on avoiding errors broadly; it discusses pre-commitment and IPS-style frameworks but does not present empirical evidence that they reduce emotional reactivity. Cited as if it supplies operational empirical support; the support is conceptual. Severity P3. |
| 5 | Lim, 2025 (DOI `10.1080/15427560.2025.2609644`) | L156, L168, L180 | "transparent, interpretable decision logic as a precondition for trust and for productive human–AI interaction" (L156) | **SUPPORTED** for the claim, but **B-4 year inconsistency** with references.md (Lim, 2026). The Lim paper supports the broader claim about XAI / behavioral AI advisory; the year discrepancy is a separate B-4 flag. |

---

## Summary
- Section A flags: 1 (A-5).
- Section B flags: 5 (2 × B-1, 3 × B-4 — same Lim normalisation across three lines).
- Part 4: 0 UNSUPPORTED, 2 PARTIAL (Henderson 2018, Statman 2019), 3 SUPPORTED.
- No P1 verdicts in Ch.1.
