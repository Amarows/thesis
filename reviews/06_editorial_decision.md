# Editorial Decision

## Manuscript Information
- **Title**: Reducing Emotional Biases in Investment Portfolio Management
- **Manuscript ID**: SBS-EMBA-THESIS (thesis_final.md)
- **Submission Date**: 2026 (EMBA thesis, SBS Swiss Business School)
- **Decision Date**: 2026-05-29
- **Review Round**: Round 1

> **Synthesis basis.** This decision was produced from the five independent reviewer reports only (`reviews/01`–`05`); the synthesiser did not re-read the manuscript in the same context, preserving the separation of review and synthesis. **Calibration:** the manuscript was judged as a *strong EMBA behavioural-finance thesis* against the SBS Master's Thesis Handbook (v1.8, AY 2025–26), whose grading rubric (Applied Knowledge 45%, Written 25%) and chapter requirements were located and used in Phase 0 — the rubric was **available**, not missing. References to `shared/`, `.claude/`, `scripts/`, `docs/`, and the sibling skills were treated as absent per instruction and caused no failures; the JSON sprint-contract scoring gate was replaced by ordinary interpretive synthesis.

---

## Decision *

### Major Revision

The underlying empirical work is sound and the central finding (including a well-defended null) is legitimate; this is **not** a Reject. But the Devil's Advocate confirmed one CRITICAL issue (the title/value-proposition contradicts the evidence), which under the iron rule means the manuscript **cannot be Accepted** as written, and two of the required fixes (clustered-SE re-reporting and the SBS reliability/distribution diagnostics) entail re-analysis and therefore re-review. Hence Major Revision.

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|----------|------|---------------|------------|
| EIC | SBS defense chair / behavioural-finance AE | Major Revision | 4 |
| Reviewer 1 | Econometrics / psychometrics (methodology) | Major Revision | 5 |
| Reviewer 2 | Behavioural-finance scholar (domain) | Major Revision | 4 |
| Reviewer 3 | DSS / human-automation + buy-side (perspective) | Minor Revision | 3 |
| Devil's Advocate | Adversarial stress-test | 1 CRITICAL (forces non-Accept); advises Major | — |

---

## Consensus Analysis *

### Points of Agreement (Consensus)

**[CONSENSUS — 4 of 5 reviewers + DA]** The title/abstract/conclusions over-claim relative to the evidence and must be reframed.
1. EIC W3 ("the title… makes an implicit causal-intervention promise the evidence does not meet").
2. R2 W3 (contribution "positioned around the intervention that failed, not the association that held").
3. R3 W1 (claims must be bounded; "what was measured is stated risk intention").
4. DA C1 (CRITICAL: "the single empirical claim the title makes… is precisely the claim the study fails to support").
*Convergent, from four different vantage points — this is the decision's centre of gravity.*

**[CONSENSUS — 4/5]** The null result is legitimate and should be foregrounded as the contribution, not treated as a failure.
1. EIC S2 (intellectual honesty in reporting the null).
2. R2 W2 (frame the null as evidence on a named mechanism).
3. R3 S1/W2 (the honest intervention test is a strength; read the null via algorithm aversion).
4. DA steelman ("the null is the honest, hard-won result, and honesty is the contribution").

**[CONSENSUS — 3/5]** Behavioural/outcome claims should be explicitly bounded to "stated intention," and the single-item NRS needs a stronger validity footing.
1. R2 W1 (construct validity of the single-item DV).
2. R3 W1 (stated intention ≠ revealed behaviour).
3. DA C4 (the edifice rests on one self-reported item).

**[CONSENSUS — 3/5]** The standard-error specification should move from HC3 to the pre-specified two-way cluster-robust SE.
1. R1 W1 (Critical: under clustered SE, t falls −8.8452 → −3.1825, p = 0.0015).
2. DA C5 (precision overstated).
3. EIC detailed comment + Q3 (HC3 vs promised cluster SE flagged for defense).

### Points of Disagreement

**Disagreement 1: Overall severity — Minor (R3) vs Major (EIC, R1, R2, DA)**
- **R3 view**: its concerns are framing/scoping fixes "that do not require new analysis," so Minor Revision; R3 explicitly anticipated that rubric/statistics-focused colleagues would land on Major.
- **EIC/R1/R2/DA view**: reframing changes the thesis's central claim, and the clustered-SE re-reporting plus the SBS reliability/distribution diagnostics require new analysis and re-review.
- **Disagreement type**: Severity disagreement.
- **Editor's Resolution**: **Major Revision.**
- **Resolution Rationale**: R3 (confidence 3) deferred the statistical and rubric items to the EIC and R1, who own them; R1 (confidence 5) is decisive on the SE re-analysis, and the EIC on rubric compliance. Two required items entail new analysis, which by definition triggers re-review. Conservative principle + expertise-weighting both point to Major.

**Disagreement 2: Is the SE issue Critical (R1) or Major (DA)?**
- **R1 view**: Critical — "the reported inference is wrong as stated."
- **DA view**: Major — it does not refute H1 (which survives the conservative SE), so it cannot be decision-fatal.
- **Disagreement type**: Severity disagreement (the substance is agreed; only the label differs).
- **Editor's Resolution**: Treat as a **Required (Priority 1)** fix that is **not, by itself, decision-fatal**.
- **Resolution Rationale**: Both reviewers agree (a) the misreported precision must be corrected and (b) the H1 conclusion holds. Labelling it "Required but conclusion-preserving" honours R1's substance and DA's logic simultaneously.

**Disagreement 3: Weight on the single-item DV — substantive construct flaw (R2) vs resolvable by bounding claims (R3/DA)**
- **R2 view**: a genuine construct-validity weakness (Major).
- **R3/DA view**: acceptable provided every claim is bounded to "stated intention."
- **Disagreement type**: Perspective/direction difference.
- **Editor's Resolution**: Require **both** — bound the claims (framing) *and* add whatever convergent/validity evidence exists (manipulation-check / usefulness items already in the panel).
- **Resolution Rationale**: The fixes are complementary, not competing; combining them resolves the concern at minimal cost.

---

## Decision Rationale *

Four of five reviewers, plus the Devil's Advocate, converge on a single core issue: the manuscript's title and framing promise a bias-*reducing intervention*, while the evidence shows the Shock Score dashboard did not move the dependent variable (ShowSC → NRS non-significant) and did not improve simulated risk–return (H2 not supported). The Devil's Advocate classified this as a CRITICAL, which under the iron rule precludes Acceptance. Critically, however, all reviewers — including the Devil's Advocate's mandatory steelman — agree the null is a *legitimate, honestly reported, and valuable* finding, and that the supported H1 association (Reviewer 1 reproduced β = −0.4874 and confirmed it survives the conservative two-way cluster SE at p = 0.0015, as well as the within-respondent estimator) plus the reusable shock-measurement instrument constitute a real contribution. The problem is therefore *packaging*, not science: no data are wrong and no analysis must be discarded. This is why the decision is Major Revision rather than Reject — a well-defended null must not be penalised as if it were a flaw. It is more than Minor because (i) the reframing alters the thesis's central claim, (ii) Reviewer 1's required move from HC3 to the pre-specified clustered SEs is a re-analysis, and (iii) two SBS rubric items (a reliability coefficient and skewness/kurtosis) are unmet and must be added — all of which warrant a second look. Reviewer 3's Minor recommendation was weighed but overridden, since R3 explicitly deferred the statistical and rubric items to the reviewers who own them and who assessed them as requiring re-review.

---

## Required Revisions * (Must Fix)

| # | Revision Item | Source Reviewer | Severity | Section | Estimated Effort |
|---|--------------|----------------|----------|---------|-----------------|
| R1 | Reframe title, abstract, and conclusions to match the evidence (measurement + conditional-evidence framing, not demonstrated debiasing) | DA (CRITICAL), EIC, R2, R3 | Critical | Title, Abstract, Ch.1, Ch.6 | 3–4 days |
| R2 | Re-report H1 with two-way cluster-robust SEs (respondent × scenario) as the primary specification; demote HC3 | R1 (Critical), DA | Critical/Major | §5 (Tables 5.7–5.8) | 2 days |
| R3 | Add SBS reliability diagnostic (Cronbach's α or justified non-applicability for single-item DV) and skewness/kurtosis | EIC, R1 | Major | §4–§5 | 1–2 days |
| R4 | Address composite coherence: document es_raw construction & 10.0 ceiling, report H1 sensitivity excluding es_raw, justify single-component retention (PC2 eigenvalue > 1) | R1, DA | Major | §5.2 | 2–3 days |
| R5 | Bound all behavioural/outcome claims to "stated intention"; add NRS validity argument using available manipulation/usefulness items | R2, R3, DA | Major | §2.3, §4, §6 | 2 days |
| R6 | Reconcile H2 Sortino n (29 vs 97/106) and either stabilise it or demote to descriptive; frame H2 on return & Sharpe | R1 | Major | §5 (Table 5.9) | 1 day |

### Required Item Details

**R1: Reframe to the evidence (resolves the CRITICAL)**
- **Problem**: Title/abstract promise bias reduction; ShowSC → NRS p = 0.4795 and H2 not supported.
- **Source**: DA C1 (CRITICAL); EIC W3; R2 W3; R3 W1.
- **Requirement**: New title oriented to measurement/diagnostic + conditional evidence; abstract leads with supported H1 and the *informative null*; conclusions state the contribution as "evidence on when a decision-support signal does and does not change professional behaviour, plus a validated shock-measurement instrument."
- **Acceptance criteria**: No sentence in title/abstract/conclusions asserts a demonstrated reduction in bias or improvement in outcomes; the null is presented as a finding, not an apology.

**R2: Clustered SEs as primary**
- **Problem**: HC3 ignores documented clustering (ICCs ≈ 0.84–0.94); precision overstated ~3×.
- **Source**: R1 W1; DA C5.
- **Requirement**: Report β(SC_total) = −0.4874 with two-way cluster SE = 0.1532 (t = −3.1825, p = 0.0015) as primary across Tables 5.7–5.8; HC3 becomes a robustness row; state the conclusion is unchanged.
- **Acceptance criteria**: Primary tables show clustered SEs; the strength language matches the clustered inference.

**R3: SBS rubric diagnostics**
- **Problem**: No Cronbach's α; no skewness/kurtosis (handbook Ch.4/Ch.5).
- **Source**: EIC W1/W2; R1 W5.
- **Requirement**: Add α (or a two-sentence justification of non-applicability for a single-item DV, retaining ICC) and skewness/kurtosis for NRS and SC_total.
- **Acceptance criteria**: Both diagnostics appear in the descriptive/reliability sections with interpretation.

**R4: Composite coherence**
- **Problem**: PC1 = 50.38%; PC2 eigenvalue > 1; es_raw opposite-signed (β = +0.3102) and capped at 10.0 for 7/24 scenarios.
- **Source**: R1 W2/W3; DA C3.
- **Requirement**: Document and (if needed) repair the es_raw mapping; report H1 with es_raw excluded from the PCA; justify one-component retention (scree/parallel analysis or theory); acknowledge n = 24 PCA limitation.
- **Acceptance criteria**: Reader can see why a single component is retained and that H1 is not driven solely by the anomalous component.

**R5: Bound claims + DV validity**
- **Problem**: Single-item stated-intention DV underwrites H1, H2, and the simulation, with no revealed-behaviour anchor.
- **Source**: R2 W1; R3 W1; DA C4.
- **Requirement**: Bound every behavioural/outcome claim to "stated intention"; marshal manipulation-check/usefulness items and the Bergkvist–Rossiter rationale into an explicit validity argument; flag real-money validation as future work.
- **Acceptance criteria**: No claim implies realised trading behaviour; a dedicated validity paragraph exists.

**R6: H2 Sortino reconciliation**
- **Problem**: Sortino n = 29 vs note's 97/106; SE = 36.2226 (uninformative).
- **Source**: R1 W4.
- **Requirement**: State exactly which pairs enter and why; stabilise (winsorise) or report Sortino descriptively only.
- **Acceptance criteria**: H2 table is internally consistent; no uninterpretable estimate is presented as inferential.

---

## Suggested Revisions (Should Fix)

| # | Revision Item | Source Reviewer | Priority | Section | Expected Improvement |
|---|--------------|----------------|----------|---------|---------------------|
| S1 | Theorise the predicted debiasing mechanism; interpret the null via algorithm aversion / advice-discounting | R2 W2, R3 W2 | P2 | §3, §6 | Converts the null into a named-mechanism contribution |
| S2 | Add feasibility/deployment subsection (data licensing, latency, compliance of an automated "Halt") | R3 W3 | P2 | §6 | Credible practical-contribution claim |
| S3 | Soften/re-anchor the SDG-10 claim (access-asymmetry caveat or shift to SDG 8) | R3 W4 | P2 | §6.8 | Avoids over-reach at defense |
| S4 | Fix citations: Lim 2026a/b (l.644–645); Koo & Li vs Koo & Mae (l.1361 vs 1566); Doronila 2024/2025 (l.323 vs 1755) | R2 W4, EIC | P3 | Refs | Reference integrity / rubric points |
| S5 | Persist or document the runtime SC merge so `analysis_panel.csv` is self-contained | R1 detailed | P2 | Methods/data | Reproducibility from deposited data |

---

## Revision Roadmap *

A standalone, prioritised, location-cited roadmap is provided in `reviews/07_revision_roadmap.md`. Summary:

### Priority 1 — Structural (≈ 8–10 days)
- [ ] R1 Reframe title/abstract/conclusions (resolves CRITICAL)
- [ ] R2 Clustered SEs as primary
- [ ] R4 Composite coherence (es_raw + component retention)
- [ ] R5 Bound claims + DV validity

### Priority 2 — Content (≈ 4–5 days)
- [ ] R3 Cronbach's α / skewness-kurtosis
- [ ] R6 H2 Sortino reconciliation
- [ ] S1 Mechanism + algorithm-aversion interpretation
- [ ] S2 Feasibility subsection; S3 SDG-10 re-anchor; S5 reproducibility

### Priority 3 — Text & Formatting (≈ 1–2 days)
- [ ] S4 Citation fixes
- [ ] Appendix 4 inconsistencies (24 stocks vs 35 holdings; "+1.08" missing %)
- [ ] Architecture diagram; label dashboard a research prototype

### Total Estimated Effort
- **Major Revision**: ≈ 2.5–3.5 weeks.

---

## Revision Deadline
- **Recommended deadline**: 6 weeks from receipt (≈ 2026-07-10).
- **Basis**: Major Revision (6–8 weeks); the work is corrective/reframing rather than new data collection, so the lower bound applies.
- **Extension policy**: Notify the committee at least 1 week before the deadline if an extension is required.

---

## Response Letter Instructions
Respond to every Required and Suggested item point-by-point (adopted, or reason for not adopting), with change-marked manuscript and a cross-reference table of new section/line numbers. Coordinate the H1 standard-error answer between the author's response to R2 (this decision) and Reviewer 1's W1.

---

## Closing

### Major Revision Version
This is a competent and intellectually honest EMBA thesis whose principal issue is framing, not substance. We encourage the author to carefully reframe the contribution around the validated shock-measurement instrument and the *informative null* on the dashboard, implement the required statistical and rubric corrections, and resubmit for a second round of review. The honest reporting of a non-supported intervention is a strength to be foregrounded, not minimised.

---

## Appendix: Full Reviewer Reports
- `reviews/01_eic_report.md`
- `reviews/02_methodology_report.md`
- `reviews/03_domain_report.md`
- `reviews/04_perspective_report.md`
- `reviews/05_devils_advocate_report.md`
