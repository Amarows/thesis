# Peer Review Report

## Manuscript Information
- **Title**: Reducing Emotional Biases in Investment Portfolio Management
- **Manuscript ID**: SBS-EMBA-THESIS (thesis_final.md)
- **Review Date**: 2026-05-29
- **Review Round**: Round 1

---

## Reviewer Information

### Reviewer Role *
EIC (Editor-in-Chief / Defense Committee Chair)

### Reviewer Identity *
Chair of an SBS Swiss Business School EMBA thesis defense committee who also serves as an Associate Editor for a behavioural-finance journal. Responsible for the gatekeeping decision: does the manuscript meet the SBS Master's Thesis Handbook (v1.8, AY 2025–26) grading standard, hold together as a coherent piece of scholarship, and make a defensible contribution? Calibrated to a *strong EMBA behavioural-finance thesis*, **not** to an A-journal acceptance bar.

### Review Focus *
Overall scholarly coherence and gatekeeping. Three priorities: (1) compliance with the SBS handbook's prescriptive chapter structure and grading rubric (Applied Knowledge 45%, Written 25%); (2) the originality and significance of the Shock Score contribution; (3) coherence between the title's promise ("Reducing Emotional Biases") and what the evidence actually shows. I do not re-verify statistics (Reviewer 1's remit) or adjudicate the literature in depth (Reviewer 2).

---

## Overall Assessment *

### Recommendation *
- [ ] **Accept**
- [ ] **Minor Revision**
- [x] **Major Revision** — Substantial revisions needed, re-review required after revision
- [ ] **Reject**

### Confidence Score *
**4** — Mostly within my area of expertise (thesis governance + behavioural finance); high confidence. The detailed statistical reproduction sits with Reviewer 1.

### Summary Assessment *
This thesis investigates whether external financial information shocks systematically move equity portfolio managers' risk-taking, and whether a structured decision-support instrument — the Shock Score (SC_total), a PCA composite of article count, sentiment extremity, attention intensity, and event-type severity — moderates that response. Using a within-subject counterbalanced scenario survey (N = 53 managers, 424 observations), the author tests H1 (SC_total → Net Risk Stance) via panel OLS and H2 (the dashboard's effect on simulated portfolio risk–return) via Sharpe/Sortino comparison. The work is methodologically ambitious for an EMBA thesis, transparently reports a null intervention result, and is generally well organised and well written; it comfortably clears the SBS minimum of 50 valid returns and follows the prescribed paradigm, hypothesis-format, and chapter scaffolding. Its central strength is the honest, fully-reproducible empirical pipeline; its central weakness is a coherence gap between the intervention-flavoured title/abstract and the data, which show the dashboard did **not** measurably change behaviour (ShowSC → NRS non-significant; H2 not supported). Two SBS rubric items are also unmet: the handbook's Chapter 5 expectation of a reliability coefficient (Cronbach's alpha) and the Chapter 4 expectation of skewness/kurtosis reporting. None of these is fatal — the underlying scholarship is sound and the null is legitimate — but together they require substantive reframing and two supplementary analyses, so I recommend Major Revision with re-review.

---

## Strengths *

### S1: Fully reproducible, auto-generated results pipeline *
The thesis is backed by a results pipeline (`8_statistical_analysis.py` → `thesis_results.md` → `9_compile_thesis.py` → `thesis_final.md`) in which no numbers are hand-typed. Every table (5.2, 5.7, 5.8, 5.9) and figure traces to a regenerable artefact. For a master's thesis this is an unusually high standard of research integrity and directly satisfies the handbook's "Research Integration" written-competency criterion. The author should foreground this in the defense.

### S2: Intellectual honesty in reporting a null intervention result *
The manuscript does not bury or spin the non-significant treatment effect. The ShowSC coefficient on NRS is reported as non-significant (Table 5.7), and H2 is explicitly stated as *not supported* (Table 5.9). Reporting a clean null without p-hacking or HARKing is exactly the behaviour the "Strong Argument & Defense" and "Ethical/Social Responsibility" rubric items reward. This is a genuine scholarly virtue and should be protected, not apologised for.

### S3: Design sophistication relative to EMBA norms *
The within-subject quasi-experimental design with V1/V2 counterbalancing — each scenario serving as treatment in one version and control in the other — controls for scenario-level confounds far better than the between-subjects designs typical at this level. Block fixed effects and an explicit positivist–deductive paradigm statement (§ around line 743) align with the handbook's Chapter 4 requirements.

### S4: A genuinely original measurement instrument *
The Shock Score operationalises "information shock" as a single, defensible, data-driven index rather than an ad-hoc dummy. The construction is principled (z-standardise four event-level components → first principal component). Whether or not the dashboard changes behaviour, the *measurement* contribution — a reusable shock-intensity index for equity events — is original and has standalone value.

---

## Weaknesses *

### W1: SBS rubric gap — no reliability coefficient (Cronbach's alpha) *
**Problem**: The SBS handbook's Chapter 5 guidance expects a reliability coefficient for survey instruments, naming Cronbach's alpha explicitly (with α ≤ 0.5 to be flagged as a limitation). The thesis reports intraclass correlation coefficients (ICC: Block 1 = 0.8425, Block 2 = 0.9026, Block 3 = 0.9369, Table 5.5) but no Cronbach's alpha; a text search returns no instance of "Cronbach."
**Why it matters**: This is a checklist item the defense committee will mechanically verify against the rubric. ICC answers a different question (between-respondent clustering) than internal consistency of the instrument. Its absence is an easy, avoidable mark-down on the "Written / Research Integration" axis.
**Suggestion**: Either (a) add Cronbach's alpha for any multi-item scale used, or (b) if NRS is a single-item DV (which it appears to be), state explicitly in §5 that internal-consistency alpha is not applicable to a single-item measure and justify the ICC as the appropriate reliability statistic for the repeated-measures design. A two-sentence justification closes the gap.
**Severity**: Major

### W2: SBS rubric gap — skewness/kurtosis not reported *
**Problem**: The handbook's Chapter 4 expects distributional diagnostics including skewness and kurtosis for the key variables. The thesis reports the Shapiro–Wilk test (W = 0.9849, p = 0.0002, Table 5.6) but I find no skewness/kurtosis values.
**Why it matters**: Same rubric-compliance logic as W1; it is a low-cost omission with a disproportionate grading impact, and skewness/kurtosis would also substantiate the (correct) decision to treat the 7-point NRS as approximately continuous.
**Suggestion**: Add skewness and kurtosis for NRS and SC_total to the descriptive tables (already computable from the existing panel) and reference them when justifying OLS.
**Severity**: Minor

### W3: Title and abstract over-promise relative to the evidence *
**Problem**: The title "*Reducing* Emotional Biases in Investment Portfolio Management" and the abstract's framing imply a demonstrated intervention effect. The data do not support a behaviour-change claim: the dashboard's effect on NRS is non-significant and H2 (its effect on simulated risk–return) is not supported.
**Why it matters**: A defense committee will press hardest precisely on the gap between what the title sells and what the results deliver. Leaving it unreconciled invites the harshest line of questioning and weakens the "Strong Argument & Defense" score, even though the underlying work is sound.
**Suggestion**: Reframe — not retract. The honest, valuable contribution is *evidence on when a decision-support signal does and does not change behaviour*, plus a validated shock-measurement instrument (H1 strongly supported). Adjust the title toward a measurement/diagnostic framing (e.g., "Measuring Information Shocks and Testing a Decision-Support Signal for Emotional Bias in Portfolio Management"), and rewrite the abstract and conclusions so the headline is the SC_total → NRS association and the *informative null* on the dashboard. (Deferring the existential form of this critique to the Devil's Advocate; here it is a coherence/defense-readiness issue.)
**Severity**: Major

### W4: Significance/contribution is asserted more than positioned *
**Problem**: The contribution claims lean on the novelty of the instrument and the dashboard concept, but the manuscript does not fully convert the null into a stated contribution to knowledge (i.e., *that* and *why* a salient shock signal failed to move stated risk intentions is itself a finding worth theorising).
**Why it matters**: The handbook's "Critical Thinking / Decision-Making" (15 pts, the single largest rubric item) rewards turning results — including nulls — into reasoned implications. Currently the discussion under-mines the most interesting result.
**Suggestion**: In Chapter 6, develop a short theorised account of the null (e.g., algorithm aversion, ceiling effects on stated intentions, single-exposure salience) and state the contribution as conditional evidence on decision-support efficacy. Coordinate with Reviewer 3's external-validity points.
**Severity**: Major

---

## Detailed Comments *

### Title & Abstract
- Title is crisp and readable but, per W3, makes an implicit causal-intervention promise the evidence does not meet. The abstract should lead with the supported H1 association and explicitly frame the dashboard result as an informative null.

### Introduction
- Research motivation (bias in professional investing under information shocks) is persuasive and well-scoped. The research questions are clear and map cleanly onto H1/H2. The hypothesis format (H1₀/H1ₐ, H2₀/H2ₐ, lines ~353–363) follows the SBS multi-hypothesis convention and uses "fail to reject / support for the alternative" language — **compliant; no change needed.**

### Literature Review / Theoretical Framework
- Coverage looks adequate for the level (deferring depth and citation-accuracy adjudication to Reviewer 2). The IV→DV conceptual framing is present and aligns with Chapter 4 expectations.

### Methodology / Research Design
- Paradigm, design, counterbalancing, and exclusion logic are appropriate and well-documented (deferring statistical verification to Reviewer 1). The one governance flag from my chair: CLAUDE.md and the design promised "HC3 / two-way cluster-robust SEs," but the delivered tables report HC3 only — worth reconciling for defense (Reviewer 1 quantifies the impact).

### Results / Findings
- Presentation is clean and table/figure quality is good. The results honestly show H1 supported, ShowSC non-significant, H2 not supported. See W3/W4 on framing.

### Discussion
- Addresses the research questions but currently treats the null defensively rather than as a contribution. See W4.

### Conclusion
- Does not over-infer beyond the data on H2 (good), but the title/abstract create a top-of-document expectation the conclusion cannot satisfy. Reconcile via reframing.

### References
- Format is APA and broadly consistent; specific inconsistencies are Reviewer 2's remit.

---

## Questions for Authors *

1. The title frames the work as *reducing* emotional bias, yet the dashboard shows no measurable effect on NRS or on simulated risk–return. How do you wish to position the contribution at defense — as an intervention study (which the data do not support) or as a measurement + conditional-evidence study (which they do)?
2. The SBS rubric anticipates a reliability coefficient and distributional diagnostics. Was Cronbach's alpha considered and judged inapplicable (single-item DV), or simply omitted? Can skewness/kurtosis be added before defense?
3. The design documentation specifies two-way cluster-robust standard errors, but the tables report HC3. Which is the intended primary specification, and does the conclusion survive the more conservative choice? (Please coordinate your answer with Reviewer 1.)

---

## Minor Issues

### Language / Grammar
- Generally clean; defer to Reviewer 2 for citation-level prose issues.

### Citation Format
- Several author-name/year inconsistencies exist (Reviewer 2 itemises them); they should be reconciled for a clean reference list.

### Figures and Tables
- Appendix 4 (survey instrument) contains an internal inconsistency: "24 stocks" (line ~2027) vs "remaining 35 holdings" (line ~2029), and a stray "+1.08" missing its percent sign (line ~2089). These are cosmetic but visible to a committee.

### Layout
- Chapter scaffolding (including §6.6 Lessons Learned ~line 1629 and §6.8 SDG implications ~lines 1662–1682) is present and handbook-compliant.

---

## Dimension Scores *

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 76 | Strong | Original instrument + dashboard concept; honest null adds value |
| Methodological Rigor (25%) | 70 | Adequate | Strong design; SE-reporting and rubric gaps pull it down (R1) |
| Evidence Sufficiency (25%) | 70 | Adequate | N=53 meets SBS min; H2 underpowered; H1 robust |
| Argument Coherence (15%) | 64 | Weak–Adequate | Title↔result gap is the main coherence drag |
| Writing Quality (15%) | 80 | Strong | Clear, organised, APA; minor citation/appendix slips |
| Significance & Impact (optional) | 72 | Adequate | Contribution real but under-positioned (esp. the null) |
| **Weighted Average** | **71.6** | **Major Revision** | Sound thesis; reframing + two rubric additions required |
