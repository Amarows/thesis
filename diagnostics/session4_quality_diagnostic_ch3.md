# Session 4 Quality Diagnostic — Chapter 3

**Scope:** thesis.md lines 401 – 680 (Ch.3 Literature Review).
**Tests executed:** Section A (A-1 – A-8), Section B (B-1 – B-10), Section C (C-1 – C-5), Part 4 hallucination spot-check (5 high-risk citations).
**Diagnostic only — no edits made to thesis.md.**

---

## Section A flags

### A-1 — Unsupported claim detection
- **L459**: stray closing parenthesis at sentence end — *"…consistent with investor overreaction rather than efficient price adjustment)."* — orphan `)` indicates a punctuation error from prior edits. Minor. P3.

### A-2 — Epistemic framing test
- **L411**: *"Barberis & Thaler (2002) and Hirshleifer (2015) establish that information shocks influence market prices through behavioral and emotional biases."* — declarative causal statement using "establish". The cited sources are surveys; the language overstates. Reframe as "argue", "discuss", or "synthesize evidence that". P2.
- **L424**: *"Behavioral finance theory documents how cognitive biases such as overconfidence … shape investor behavior and amplify short-term market reactions to information shocks."* — declarative; could be reframed as "Research in behavioral finance has examined how cognitive biases such as overconfidence…" P3.
- **L475**: *"In sum, the literature establishes that behavioral biases shape short-term price dynamics and introduce persistent frictions into portfolio decision-making."* — declarative synthesis; reframe with cautious language ("The literature reviewed in this section indicates that…"). P3.

### A-3 — Assumption-vs-literature test
- **L447**: *"these findings are synthesized in this thesis to support the assumption that negative financial information shocks tend to provoke more immediate and emotionally amplified responses…"* — the "assumption" framing is acceptable here because it sets up the rationale for the H1 study design. Borderline. **No flag.**

### A-4 — Original-vs-established boundary test
- **L599, L601, L603**: Shock Score is consistently presented as a novel construct ("Chapter 4 introduces the Shock Score as a novel composite indicator…"). **No flag.**

### A-5 — Forward-reference integrity test
No flags. Forward references to Ch.4 use specific section numbers.

### A-6 — Data source specificity test
Not directly applicable in Ch.3 (literature review). No flags.

### A-7 — Cross-reference precision test
No flags. References point to specific chapters and sections.

### A-8 — Empirical illustration sourcing test
No flags.

---

## Section B flags

### B-1 — Named citation rule (vague attribution)
- **L417**: *"Taken together, the studies reviewed below are interpreted in this thesis as implying a causal pathway…"* — this is acceptable author commentary (Section C-1 attribution).
- **L429**: *"Theoretical models show that overconfident investors can introduce excess volatility into markets…"* — vague attribution; the supporting citation Gervais & Odean (2001) follows but the lead clause could attribute directly: "Gervais & Odean (2001) show theoretically that…". P3.
- **L471**: *"The reviewed literature shows that behavioral biases—particularly overconfidence, availability heuristics, herding, and loss aversion—distort professional investors' judgment during information shocks."* — vague "the reviewed literature" with no specific named reference in the closing sentence. P3.

### B-2 — Hyperlink completeness / missing references

**Missing from references.md (most serious):**
- **L432**: *"Bikhchandani & Sharma (2001) and Brown et al. (2014) document that even professional investors may follow the crowd…"* — **Bikhchandani & Sharma (2001)** is not in references.md and has no in-text hyperlink. P2.
- **L432**: bracket citation `[Bikhchandani et al., 1992](https://doi.org/10.1086/261849)` — DOI is correct for Bikhchandani, Hirshleifer & Welch (1992) "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades" — but **the reference is not in references.md**. P2.
- **L454**: *"Da, Engelberg, and Gao (2011) show…"* — this is the same as Da et al. (2011) which is in references.md; here it's the same paper with full author list — **not a flag**, just stylistic.
- **L552**: bracket citation `[Rigobon, 2003](https://doi.org/10.1162/003465303772815727)` — **Rigobon (2003) "Identification through heteroskedasticity"** is not in references.md. P2.
- **L563**: prose *"Huber, Huber, and Kirchler (2022)"* — Kirchler is the third author of Huber et al. (2022), which IS in references.md. **Not a missing-reference flag**, but the full author listing without a corresponding entry change is acceptable if the surrounding bracket citation `[Huber et al., 2022]` resolves to the right entry, which it does.
- **L654**: *"Based on Baker and Wurgler (2006), Da et al. (2015), RavenPack (2023), Statman (2019)…"* — **RavenPack (2023)** is not in references.md. references.md (line 58) has **RavenPack, 2017**. Either update the date in the prose mention or add a 2023 entry. P2.

**Prose-only citations without hyperlinks (HR-6 violations):**

The following prose mentions in Ch.3 have no accompanying markdown bracket link with URL in the same paragraph:
- L411 (5 instances: Barberis & Thaler, Hirshleifer, Meng et al., Barber & Odean, Meng et al.)
- L432 (Bikhchandani & Sharma)
- L441 (Tetlock — but markdown form at start of sentence; check)
- L445 (Neel)
- L454 (Daniel et al., Frazzini, Da Engelberg Gao)
- L459 (De Bondt & Thaler — not in refs as plain "Bondt"; actually entry is "De Bondt & Thaler, 1985" which is fine; missing hyperlink in paragraph)
- L463 (Cremers, Pareek, and Sautner — full-author list refers to Cremers et al., 2021 which is hyperlinked at end of sentence — **no flag**)
- L465 (Ben-Rephael et al. — hyperlinked at end of sentence — **no flag**)
- L467 (Harvey, Mazzoleni, and Melone — full-author list refers to Harvey et al., 2025 hyperlinked at end — **no flag**)
- L486 (Hodgkinson et al. duplicate prose; Harvey is third author of Ben-David et al., 2013 not a separate paper — **not flags**)
- L488 (Frazzini — already hyperlinked at L452)
- L490 (Kahneman et al. 2021 — no hyperlink in paragraph)
- L494 (March and Shapira, Kahneman & Tversky — both have references; missing hyperlinks in paragraph)
- L502 (Elkind et al. — hyperlinked at end of paragraph — **no flag**)
- L504 (Bianchi et al. — no hyperlink in paragraph)
- L525 (Lim 2026 — hyperlinked at end of paragraph — **no flag**)
- L531 (Thaler & Sunstein, Kahneman et al. 2021 — no hyperlinks in paragraph)
- L542 (Lo and Repin (2002) — hyperlinked at end of paragraph — **no flag**)
- L561 (Bhandari et al. — no hyperlink in paragraph)
- L563 (Kirchler reference is part of Huber et al. — **not a flag**)
- L571 (Song et al. — hyperlinked elsewhere; check paragraph)
- L584 – L593 (Table 3.1 — see B-3/B-4 sub-issue: rows mix "Lim (2025)" L591 and "Lim (2026)" L592)
- L601 (Lim (2025) — already flagged B-4)
- L654 (Baker and Wurgler, Da et al., RavenPack, Statman — table note; no hyperlinks)
- L664 (Hirshleifer, Barberis & Thaler, Henderson et al., Statman, Bianchi et al. — closing synthesis paragraph, no hyperlinks)

Severity: each individual instance P3; **the pattern across §3.6 / §3.7 is a P2 cluster** because of frequency.

### B-3 — Duplicate citation rule
Confirmed B-3 violations (same author + year as both prose mention AND markdown bracket link in the same sentence):

- **L432**: *"Jiang & Verardo (2018) and Brown et al. (2014) show that herding-induced price pressures can be short-lived… ([Jiang & Verardo, 2018](…); [Brown et al., 2014](…))"* — both pairs duplicated.
- **L435**: *"Lo et al. (2005) document that acute stress and arousal can impair decision-making even in expert traders ([Lo et al., 2005](…); [Coates & Herbert, 2008](…))."* — Lo et al. duplicated.
- **L465**: *"Ben-Rephael et al. (2024) document that institutional trading around earnings announcements… ([Ben-Rephael et al., 2024](…))."* — duplicated.
- **L496**: *"[Huber et al. (2022)](…) find that during the COVID-19 market crash… ([Huber et al., 2022](…))"* — duplicated.
- **L500**: *"[Lo and Repin (2002)](…) show through physiological measurement… ([Lo & Repin, 2002](…))"* — duplicated.
- **L538**: *"Ben-David et al. (2013) show that managers display overconfidence and miscalibration in their expectations, leading to distorted risk assessments and suboptimal decisions ([Ben-David et al., 2013](…))"* — duplicated.
- **L552**: *"[Engelberg and Parsons (2009)](…) demonstrate the value of operationalizing news intensity… ([Engelberg & Parsons, 2009](…))"* — duplicated.
- **L565**: *"[Frazzini (2006)](…) and [Daniel et al. (1998)](…) are representative examples… ([Frazzini, 2006](…); [Daniel et al., 1998](…))."* — both duplicated.
- **L569**: *"Bhandari et al. (2008) show that prevailing decision-support systems are largely designed for computational analysis… ([Bhandari et al., 2008](…))."* — duplicated.

Per protocol B-3 rule: if the prose mention exists, remove the markdown bracket; if only a markdown citation exists, keep it. Each instance P3.

### B-4 — Citation year / URL consistency
- **L430**: bracket citation `[Hirshleifer, 2015](https://dx.doi.org/10.2139/ssrn.2480892)` — uses the SSRN preprint URL. All other Hirshleifer 2015 instances in the thesis (L146, L230, L236, L249, L253, L263, L323, L424, L1376) use `https://doi.org/10.1146/annurev-financial-092214-043752` (the published-version DOI). references.md uses the published DOI. Normalise L430 to match. P2.
- **L591 vs L592** (Table 3.1): row 6 is *"Lim (2025)"* and row 7 is *"Lim (2026)"* — same paper, internal inconsistency within a single table. P2.
- **L571, L601** (prose): *"Lim (2025)"* — should match references.md *"Lim, 2026"*. Tracked globally; P2.
- **L525, L576** (prose): *"Lim (2026)"* — correctly uses 2026. (Indicates the author has been inconsistent within the chapter; standardising to 2026 also addresses Ch.1 / Ch.2 instances.)

### B-5 — "Information shock" terminology
No flags. Ch.3 consistently uses "information shock(s)" or "external information shock". Standalone "shock" appears only in compound terms ("market shock", L435 — borderline, but "market shock" is conventional). **No flag.**

### B-6 — Shock Score placement rule
**No flag.** Ch.3 forward-references the Shock Score to Ch.4 (L413: *"The Shock Score, introduced in Chapter 4, is motivated by research on sentiment, attention, and volatility-based measures…"*; L599: *"its construction is detailed in Chapter 4"*; L601: *"the Shock Score (defined in Chapter 4)"*; L603: *"the Shock Score (defined in Chapter 4)"*). Definitional content is absent from Ch.3.

### B-7 — Subsection length rule
- **§3.4.3 "Quantifying Bias: Metrics and Behavioral Factor Models"** (L527 – L531): contains two substantive paragraphs. Borderline acceptable (each paragraph multi-sentence). **No flag.**
- **§3.6.4 "Relevance of Reviewed Literature to Research Hypotheses"** (L662 – L664): single paragraph of three sentences. Borderline. **No flag.**
- The bold-text subsections inside §3.6.3 (e.g., *"Category 1: Composite Sentiment Indices…"*, *"Technical Distinction: PCA Application"*) are formatted as bold rather than as proper level-3/4 headers — per protocol B-7 note, bold text at paragraph start should not substitute for a level-3/4 header. Either promote to headers or remove bold. **P3.**

### B-8 — Bias-to-study link rule
Verified. Every bias subsection in §3.2 closes with the required "in this study" / "the Shock Score" link sentence:
- L428 (overconfidence): *"the Shock Score is intended to provide a structured reference point…"* — OK.
- L430 (availability/recency): *"the Shock Score counteracts this by aggregating multiple objective information shock dimensions…"* — OK.
- L432 (herding): *"by presenting the Shock Score individually to each respondent in a controlled scenario design…"* — OK.
- L435 (emotional/physiological): *"the Shock Score is intended to provide a stabilising informational anchor…"* — OK.
- L454 (disposition effect): *"the disposition effect represents a potential source of asymmetric bias in the Net Risk Stance variable…"* — OK.

**No flag.**

### B-9 — Objectives-to-RQ mapping
Not applicable (Ch.2 test).

### B-10 — SC_total construct validity
Not applicable (Ch.5 test).

---

## Section C flags

### C-1 — Attribution layer separation
- **L417**: *"Taken together, the studies reviewed below are interpreted in this thesis as implying a causal pathway from external information shocks to portfolio-level outcomes."* — opens with author-interpretation marker, then the paragraph continues with a sequence of causally-framed claims that read as established facts. The boundary between layer (c) author interpretation and layers (a)/(b) literature-established fact is not explicit; subsequent sentences should be hedged with "the reviewed literature suggests" or similar. P2.

### C-2 — Standard term attribution
- **L230 / L498**: *"procyclical rebalancing"* — established domain-specific term used without citation to a foundational source. Could be linked to Cremers et al. (2021) or Harvey et al. (2025) where the mechanism is documented. P3.
- **L432**: *"informational cascades"* (implied via the Bikhchandani citation) — covered by the citation if Bikhchandani is added to references.md (B-2).
- **L501** / Ch.5 elsewhere: *"disposition effect"* is correctly attributed to Shefrin & Statman in spirit but Ch.3 cites Frazzini (2006) and Grinblatt & Keloharju (2001) — both appropriate operational sources; the foundational Shefrin & Statman (1985) is not cited but Shefrin (2002) "Beyond Greed and Fear" is in references.md. P3.

### C-3 — Literature-to-construct reasoning chain
- **§3.2.5 (L469 – L475)** synthesizes biases and portfolio implications but the closing paragraph (L475) does not explicitly chain back to the Shock Score construct. The link is provided in individual subsection closings (B-8) but a section-level chain — (a) what literature establishes → (b) why relevant → (c) how Shock Score addresses — is implicit rather than stated. P3.

### C-4 — Gap claim calibration
- **L578**: *"…no prior research integrates all four elements in a controlled setting."* — strong gap claim. Supported by the Table 3.1 systematic mapping which lists six studies and shows that none integrates all four. The claim is calibrated by the table evidence. **No flag.**
- **L660**: *"None operationalizes information shock intensity as a real-time behavioral risk mitigation trigger for discretionary portfolio managers."* — strong "none" claim; calibrated by Table 3.2 and accompanying narrative. **No flag.**
- **L676**: *"existing tools are predominantly designed for quantitative analytics and algorithmic execution, with limited provision for ex-ante identification and moderation of bias at the point of decision"* — appropriately cautious framing. **No flag.**

### C-5 — Section intro paragraph rule
- **§3.3 "Managerial Decision-Making Under Uncertainty"** (L478 – L480) has no intro paragraph at all — the section opens directly with the §3.3.1 sub-heading. P3.
- **§3.4 "Tools to Mitigate Emotional and Behavioral Bias"** (L507 – L509) has no intro paragraph; opens directly with §3.4.1. P3.
- **§3.5 "Implications for Portfolio Management"** (L534 – L536) has a single-paragraph intro (L536) but it names no specific papers; per protocol C-5 the intro should name at least two reviewed sources. P3.
- **§3.2** opens with a sub-heading §3.2.1 immediately (L420 → L422); the §3.2.1 first paragraph (L424) does cite multiple papers, so functions as an effective intro. **No flag.**
- **§3.6** opens with §3.6.1 directly; §3.6.1 first paragraph (L561) cites Barberis & Thaler. Acceptable.

---

## Part 4 hallucination spot-check (5 citations)

| # | Citation | Claim location | Claim made | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | Hirshleifer (2015) | L411 | *"Barberis & Thaler (2002) and Hirshleifer (2015) establish that information shocks influence market prices through behavioral and emotional biases."* | **PARTIAL** | Verified abstract: the 2015 *Annual Review of Financial Economics* survey describes "judgment and decision biases, how they affect trading and market prices, the role of arbitrage…". It supports the general link between behavioral biases and prices but is a broad survey, not a study that "establishes" the specific information-shocks-to-prices channel. Reframe the claim to "review and synthesize evidence that…" rather than "establish that…". Severity P2 — known risk case from protocol. |
| 2 | Lim (2026) | L525, L576, L601 | technical-feasibility findings: FinBERT + DistilBERT + LLM emotion-aware advisory; ~44% panic-trade reduction in high-volatility scenario; bounded by simulation-only validation | **SUPPORTED** | Verified abstract and publication record (Journal of Behavioral Finance, online 30 January 2026, DOI 10.1080/15427560.2025.2609644). The thesis description matches the paper's content and acknowledged limitations. **Year/format inconsistency (Lim 2025 vs Lim 2026) is a B-4 finding, separate from the spot-check.** |
| 3 | Bikhchandani & Sharma (2001) and Bikhchandani et al. (1992) | L432 | herding by professional investors as career risk management; informational cascades | **UNSUPPORTED at reference level — P1** | Neither Bikhchandani & Sharma (2001) nor Bikhchandani et al. (1992) appears in references.md. The bracket DOI `10.1086/261849` is correctly the Journal of Political Economy 1992 paper by Bikhchandani, Hirshleifer & Welch on informational cascades, but it has no references.md entry, no `file` column, and cannot be verified offline. The 2001 reference (likely Bikhchandani & Sharma "Herd Behavior in Financial Markets", IMF Staff Papers Vol. 47) has no entry at all. Two missing references for the same paragraph. **P1.** |
| 4 | Brown et al. (2014) | L432, L578 (Table 3.1) | "stocks persistently bought by institutions tend to earn negative subsequent returns as prices correct, while persistently sold stocks tend to rebound" | **SUPPORTED** | Brown, Wei, Wermers (2014) "Analyst Recommendations, Mutual Fund Herding, and Overreaction in Stock Prices" (*Management Science*) — finding matches: persistent institutional herding around analyst recommendations produces subsequent reversals. Reference is in references.md (line 11). |
| 5 | Goodell et al. (2023) | L529 | "Recent systematic review evidence synthesizes findings on a broad set of behavioral anomalies, including the disposition effect, excessive trading, and attention-driven behavior" | **SUPPORTED** | Goodell, Kumar, Lim, Pattnaik (2023) "Emotions and stock market anomalies: A systematic review" (*Journal of Behavioral and Experimental Finance*) — confirmed as a systematic review covering the cited anomalies. |

---

## Summary
- Section A flags: 4 (1 × A-1 typo, 3 × A-2).
- Section B flags: ~50 individual line items, clustered into:
  - 5 missing references (Bikhchandani × 2, Rigobon, RavenPack 2023) — P2.
  - ~25 prose-without-hyperlink instances (HR-6) — P3 each, but cluster P2.
  - 9 × B-3 duplicate citations — P3.
  - 5 × B-4 (Hirshleifer URL inconsistency at L430; Lim year inconsistency at L571, L591/592, L601) — P2.
  - 1 × B-7 (bold-as-header in §3.6.3) — P3.
- Section C flags: 5 (1 × C-1, 2 × C-2, 1 × C-3, 3 × C-5).
- Part 4: **1 UNSUPPORTED / P1 (Bikhchandani — two missing references)**, 1 PARTIAL (Hirshleifer 2015 known-risk case), 3 SUPPORTED.
