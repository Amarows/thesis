# Peer Review Report

## Manuscript Information
- **Title**: Reducing Emotional Biases in Investment Portfolio Management
- **Manuscript ID**: SBS-EMBA-THESIS (thesis_final.md)
- **Review Date**: 2026-05-29
- **Review Round**: Round 1

---

## Reviewer Information

### Reviewer Role *
Peer Reviewer 3 (Cross-disciplinary Perspective — Decision-Support Systems & Buy-Side Practice)

### Reviewer Identity *
Researcher in decision-support systems and human–automation interaction who has also worked on the buy side (portfolio construction and risk). I read the thesis as a practitioner-facing artefact: would this instrument survive contact with a real investment process, and are its claims about real-world impact (including the SDG implications) credible? My remit is assumptions, external validity, and practical feasibility — not the internal statistics (Reviewer 1) or the behavioural-finance literature (Reviewer 2).

### Review Focus *
(1) The stated-intention vs revealed-behaviour gap and what it means for a buy-side decision-support claim; (2) human–automation factors (algorithm aversion / advice utilisation) as the natural reading of the null; (3) practical feasibility of the four dashboard signals and their data dependencies; (4) the credibility of the SDG-10 (reduced-inequality) claim.

---

## Overall Assessment *

### Recommendation *
- [ ] **Accept**
- [x] **Minor Revision** — Minor revisions needed, no re-review after revision
- [ ] **Major Revision**
- [ ] **Reject**

### Confidence Score *
**3** — The DSS/human-automation and buy-side-feasibility angles are within my expertise; the SBS-rubric and econometric specifics are better judged by the EIC and Reviewer 1, so I temper my confidence accordingly.

### Summary Assessment *
From a decision-support and practitioner standpoint, this thesis does something valuable that many DSS papers skip: it actually tests whether a proposed signal changes a professional's decision, and reports honestly that it did not. The Shock Score is a thoughtfully engineered artefact, and the within-subject scenario design is a reasonable proxy for a controlled trial of a dashboard. My core reservation is one of external validity and framing rather than execution: the dependent variable is a *stated intention* elicited in a hypothetical scenario, not a real-money allocation under P&L pressure, mandate constraints, and committee governance — so both the supported H1 and the null H2 should be read as evidence about *stated risk intention in a survey*, not about trading behaviour on a desk. Read through a human–automation lens, the null is unsurprising and even informative: experienced professionals frequently discount algorithmic advice (algorithm aversion), which the manuscript could foreground rather than treat as a let-down. I also find the SDG-10 (reduced-inequality) claim weakly supported and possibly backwards, given the instrument's reliance on licensed news, intraday data, and an NLP model. These are mostly framing/scoping fixes that do not require new analysis, so I recommend Minor Revision — while noting I expect colleagues focused on rubric compliance and statistics to land on Major.

---

## Strengths *

### S1: It actually tests the intervention, and reports the null honestly *
Much DSS scholarship proposes a tool and stops at a usability demo. This thesis runs a controlled (counterbalanced, within-subject) test of whether the signal changes decisions and reports that it did not. From an evidence-standards view this is exactly right and more valuable than a glossy positive result that would not replicate.

### S2: The artefact is concrete and decision-oriented *
The dashboard reduces a complex event into four decision-relevant signals (sentiment direction, severity, persistence horizon, and a rules-based Monitor/Review/Halt pre-commitment protocol at the 60th/85th percentiles). Pre-commitment protocols are a sound debiasing design choice grounded in the self-control literature, and tying them to percentile thresholds is operationally sensible.

### S3: A realistic respondent pool *
Recruiting 53 actual portfolio managers (2+ years' experience) rather than students gives the test far more ecological credibility than the typical lab sample, even though the *task* remains hypothetical (see W1).

---

## Weaknesses *

### W1: Stated intention is not revealed behaviour — claims must be bounded accordingly *
**Problem**: NRS is a self-reported intention in a hypothetical scenario. Real buy-side decisions are made under capital-at-risk, benchmark and mandate constraints, liquidity, drawdown limits, and committee oversight — none of which operate in the survey. The H2 portfolio outcomes are *simulated* from NRS-weighted horizon returns, so they inherit this gap and add a modelling layer on top.
**Why it matters**: The title and parts of the discussion imply conclusions about managerial *behaviour* and portfolio *outcomes*. What was measured is stated risk intention. The intention–action gap is large and well-documented, especially under real incentives.
**Suggestion**: Systematically bound every behavioural/outcome claim to "stated risk intention under hypothetical scenarios," add this as a primary limitation, and frame real-money validation as the key piece of future work. (Reinforces the EIC's and Reviewer 2's reframing points from a practitioner angle.)
**Severity**: Major

### W2: The null is under-explained as a human–automation result (algorithm aversion) *
**Problem**: The manuscript treats the non-effect of the dashboard largely as an empirical disappointment, without engaging the most likely explanation from human–automation research: experienced professionals systematically under-weight or reject algorithmic advice, particularly when it conflicts with their own judgement (algorithm aversion; advice-discounting).
**Why it matters**: This reframes the null from "the tool didn't work" to "consistent with known barriers to expert adoption of decision aids" — a genuine, citable contribution about *when* decision support fails to move professionals.
**Suggestion**: Add a short subsection interpreting the null via algorithm aversion / trust-calibration, and note design implications (e.g., explanation/transparency, opt-in framing, integration into workflow) for future iterations. (Coordinates with Reviewer 2's call for a theoretical layer.)
**Severity**: Major

### W3: Feasibility and data-dependency of the signals are not costed *
**Problem**: The four signals depend on a non-trivial data and modelling stack: licensed real-time news (Benzinga), intraday market data (IBKR), and an NLP sentiment model (FinBERT), plus rolling-window baselines for attention intensity and category-severity calibration. The manuscript does not address latency, licensing cost, vendor lock-in, or governance/compliance for deploying an automated "Halt" recommendation in a regulated firm.
**Why it matters**: A practitioner reading this will immediately ask "what would it take to run this live, and who signs off on a Halt?" Without that, the practical-contribution claim is incomplete.
**Suggestion**: Add a short feasibility/deployment subsection covering data licensing, latency, model-maintenance, and the compliance status of an automated trade-halt recommendation. Frame the current artefact as a research prototype.
**Severity**: Minor

### W4: The SDG-10 claim is weakly supported and may be backwards *
**Problem**: §6.8 (lines ~1662–1682) frames the instrument as advancing SDG 10 (reduced inequalities). But a tool requiring licensed news feeds, intraday data, and an NLP pipeline is more readily accessible to well-resourced institutions than to retail or under-resourced participants, so it could *widen* rather than narrow the information gap.
**Why it matters**: An over-reaching SDG claim is an easy target at defense and slightly undercuts the otherwise sober tone. The SBS rubric rewards a credible Ethical/Social-Responsibility treatment, not an aspirational one.
**Suggestion**: Either soften to a conditional claim (the *approach* could reduce inequality *if* delivered through an accessible channel) or re-anchor on SDG 8 / governance-of-decision-quality, and explicitly acknowledge the access-asymmetry risk.
**Severity**: Minor

---

## Detailed Comments *

### Methodology / Research Design (perspective lens)
- The counterbalanced within-subject design is a strong proxy for an A/B test of the dashboard; the limiting factor is the hypothetical task, not the design. Consider a small field or trading-simulator pilot as the natural next step.

### Results / Findings
- The non-significant ShowSC effect and unsupported H2 are, from a human–automation standpoint, plausible and worth interpreting (W2), not just reporting.

### Discussion
- Practical implications should distinguish "what we learned about managers" (H1: shock intensity tracks stated intention) from "what we learned about the tool" (it did not move intentions here). Both are useful; conflating them weakens each.

### Conclusion
- Avoids over-claiming on H2 numerically, but the surrounding intervention framing (and SDG-10) outruns the evidence; see W1/W4.

---

## Questions for Authors *

1. What is the strongest reason to expect stated NRS in a hypothetical scenario to predict real allocation changes under live P&L, mandate, and committee constraints — and how would you validate that link?
2. The dashboard's effect is null. Do you read this as algorithm aversion / advice-discounting by experienced professionals, and if so what design changes (transparency, workflow integration, opt-in) might change adoption?
3. For SDG 10 specifically: what delivery channel would make this instrument *reduce* rather than widen information inequality, given its licensed-data and NLP dependencies?

---

## Minor Issues

### Layout
- §6.8 SDG subsection is present and handbook-compliant; the claim strength (not its presence) is the issue.

### Figures and Tables
- A simple deployment/architecture diagram (data sources → signals → recommendation) would strengthen the practical-contribution chapter.

### Practical Framing
- Label the dashboard explicitly as a research prototype to pre-empt feasibility objections.

---

## Dimension Scores *

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 75 | Strong | Decision-oriented artefact + honest intervention test |
| Methodological Rigor (25%) | 71 | Adequate | Design fine; external-validity bounding needed (R1 owns stats) |
| Evidence Sufficiency (25%) | 69 | Adequate | Stated-intention evidence; real-money link untested |
| Argument Coherence (15%) | 70 | Adequate | Strong except intervention/SDG over-reach |
| Writing Quality (15%) | 80 | Strong | Clear and practitioner-readable |
| Significance & Impact (optional) | 73 | Adequate | High potential; bound the claims to realise it |
| **Weighted Average** | **72.6** | **Minor → Major boundary** | Mostly framing/scoping fixes; I recommend Minor |
