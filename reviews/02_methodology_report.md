# Peer Review Report

## Manuscript Information
- **Title**: Reducing Emotional Biases in Investment Portfolio Management
- **Manuscript ID**: SBS-EMBA-THESIS (thesis_final.md)
- **Review Date**: 2026-05-29
- **Review Round**: Round 1

---

## Reviewer Information

### Reviewer Role *
Peer Reviewer 1 (Methodology)

### Reviewer Identity *
Applied econometrician / quantitative psychometrician with experience refereeing empirical finance and survey-experimental work. My remit is to **re-compute the numbers, not merely read how they are reported**: I independently reloaded `results/analysis_panel.csv`, merged the authoritative Shock Score from `survey/metadata/scenario_shock_score.csv` (the panel's SC columns are NaN by design and merged at runtime), and re-estimated the PCA composite, the H1 OLS with alternative standard errors, the component decomposition, and the descriptive statistics. All values below are reported to 4 decimal places with no intermediate rounding.

### Review Focus *
Statistical correctness and inferential validity: (1) reproduction of SC_total / H1 / H2; (2) the standard-error specification (HC3 vs the two-way cluster-robust SE the design promised); (3) construct/statistical coherence of the PCA composite, especially the event-type-severity component; (4) the H2 power and the Sortino estimate; (5) residual normality and reliability reporting.

---

## Overall Assessment *

### Recommendation *
- [ ] **Accept**
- [ ] **Minor Revision**
- [x] **Major Revision** — Substantial revisions needed, re-review required after revision
- [ ] **Reject**

### Confidence Score *
**5** — Squarely within my expertise; I reproduced the headline numbers directly from the data.

### Summary Assessment *
This thesis estimates the effect of an information-shock index (SC_total, the first principal component of four standardised event features) on managers' Net Risk Stance (H1) and the effect of a decision-support dashboard on simulated portfolio risk–return (H2). I independently reproduced the core results and they are **arithmetically correct**: the PCA (eigenvalue 2.1027, 50.38% variance, loadings 0.6120/0.3990/0.6161/0.2944), the SC_total reconstruction (correlation 1.0000 with the stored index), the H1 primary coefficient (β = −0.4874, HC3 SE 0.0551, t = −8.8452, p < 0.0001, R² = 0.3571), and all descriptive statistics replicate to 4 decimals. This is a credit to the pipeline's reproducibility. However, the inference rests on a standard-error choice the design did not promise: under the **two-way cluster-robust SE** specified in the project's own documentation, β(SC_total)'s SE nearly triples (0.0551 → 0.1532) and t falls from −8.8452 to −3.1825 — still significant (p = 0.0015) but far less precise, so the headline statistic overstates confidence roughly threefold. Three further issues — the event-severity component carrying the *opposite* sign inside the composite, the H2 Sortino estimate being effectively uninformative (SE 36.2226), and two unmet SBS diagnostic requirements (Cronbach's alpha, skewness/kurtosis) — push this to Major Revision. None overturns H1's substantive conclusion; all require correction before the inference can be reported as it currently stands.

---

## Strengths *

### S1: Full numerical reproducibility *
Every headline statistic I attempted to reproduce matched to 4 decimals. PCA eigenvalue (2.1027), variance explained (50.38%), all four loadings, the H1 coefficient vector, and the NRS condition means (control 4.0849, n = 212; treatment 4.0189, n = 212; Δ = −0.0660) reproduced exactly from the raw panel + authoritative SC file. SC_total equals w₁′z to a correlation of 1.0000. Reproducibility at this level is rare at any level of scholarship.

### S2: Appropriate primary estimator and honest H2 reporting *
Panel OLS with controls and block fixed effects is a defensible primary specification for the design, and the five-spec robustness suite (quintiles, within-respondent FE, component decomposition, SC×ShowSC interaction, direction interaction) is the right battery. The within-estimator (β = −0.1846, SE 0.0549, p = 0.0008, Table 5.8) shows the SC_total–NRS relation survives removal of all time-invariant respondent heterogeneity — a strong robustness result. H2's non-significance is reported plainly, with the Option A collective portfolio correctly flagged as descriptive/non-independent.

### S3: Sound treatment of the repeated-measures structure (partially) *
Reporting ICCs (0.8425 / 0.9026 / 0.9369, Table 5.5) correctly signals heavy within-respondent clustering. This makes the diagnosis of the problem visible — which paradoxically is why the HC3-only inference (W1) is hard to defend: the author has already documented the clustering that HC3 ignores.

---

## Weaknesses *

### W1: Standard errors do not match the pre-specified design and overstate precision *
**Problem**: CLAUDE.md and the design specify "panel OLS, HC3 / two-way cluster-robust SEs," yet every delivered table reports HC3 only. Re-estimating the primary H1 model, I obtain:
- HC3: SE = 0.0551, t = −8.8452, p < 0.0001
- Two-way cluster (respondent × scenario): SE = **0.1532**, t = **−3.1825**, p = **0.0015**
- Respondent-only cluster: SE = 0.0369, p < 0.0001

The very high reported ICCs (≈0.84–0.94) confirm the data are heavily clustered within respondents, and there are only 24 scenario clusters. HC3 treats the 424 observations as quasi-independent and therefore understates the SE by roughly a factor of three.
**Why it matters**: The headline "t = −8.8452" conveys near-impossible precision that the design's own promised estimator does not deliver. The *conclusion* (H1 supported) is robust — it survives the conservative SE — but the reported *strength of evidence* is materially inflated, which a methods examiner will catch.
**Suggestion**: Make two-way cluster-robust SEs (respondent + scenario) the primary specification, as the design promised, and demote HC3 to a robustness row. Re-report β(SC_total) as −0.4874 (SE 0.1532, t −3.1825, p 0.0015). State explicitly that the conclusion is unchanged. Apply the same correction to every coefficient in Tables 5.7–5.8.
**Severity**: Critical

### W2: The event-severity component carries the opposite sign inside the composite *
**Problem**: In the component-decomposition robustness model (Table 5.8), the four components do not move NRS in a common direction: se_e (β = −1.2904, p < 0.0001) and ai_e (β = −0.5668, p < 0.0001) are negative, ac_e is non-significant (β = 0.0235, p = 0.1585), and **es_raw is positive (β = +0.3102, p < 0.0001)**. I reproduce the same sign pattern using the z-scored components (es_z β = +0.6095, p < 0.0001). Yet es_raw loads *positively* (0.2944) on PC1, and PC1 (SC_total) relates *negatively* to NRS. So the severity component's own association with NRS is the reverse of the direction it contributes to the composite.
**Why it matters**: It undermines the interpretation of SC_total as a unidimensional "shock intensity" construct. A higher composite is supposed to mean a more intense shock that pulls risk-taking down; but its severity ingredient, taken alone, pulls risk-taking *up*. This is a construct-validity problem, not just a curiosity. It also interacts with W3 (the composite is only weakly unidimensional) and with the project note that es_raw uses a placeholder severity mapping "requiring manual review."
**Why it matters (data signal)**: In `scenario_shock_score.csv`, es_raw is capped/clustered at 10.0000 for 7 of 24 scenarios — a clear ceiling artefact in the severity mapping, which likely drives the anomalous sign.
**Suggestion**: (a) Re-examine and document the es_raw construction (resolve the 10.0000 ceiling); (b) report whether SC_total's H1 result holds when es_raw is excluded from the PCA; (c) discuss the opposite-sign finding as a substantive result about which dimensions of a shock actually move managers (sentiment extremity and attention, not nominal severity).
**Severity**: Major

### W3: The composite is only weakly unidimensional *
**Problem**: PC1 explains 50.38% of variance (eigenvalue 2.1027), but the full eigenvalue spectrum I recompute is [2.1027, 1.1703, 0.6747, 0.2261]. PC2's eigenvalue exceeds 1.0, so a Kaiser criterion would retain **two** components, and the PCA is estimated on only **24** scenario-level observations for four variables (≈6 observations per variable) — sampling uncertainty on the loadings is large.
**Why it matters**: Using PC1 alone discards a second dimension that the data say is non-trivial, and with n = 24 the loadings themselves are imprecisely estimated. Combined with W2, the "single shock index" framing is on shaky psychometric footing.
**Suggestion**: Report the full eigenvalue table, justify the one-component retention explicitly (e.g., scree/parallel analysis, or theory), and add a sensitivity check using PC1+PC2 or the raw components. Acknowledge the n = 24 limitation on PCA stability.
**Severity**: Major

### W4: The H2 Sortino estimate is effectively uninformative, with an internal n discrepancy *
**Problem**: For the Sortino outcome (Table 5.9), τ = 9.4847 with SE = 36.2226 (t = 0.2618, p = 0.7934). The 95% CI spans [−61.5102, 80.4797] — the estimate carries essentially no information. The reported regression n = 29, while the accompanying note states the Sortino was "Computed for 97 of 106 respondent-condition pairs with at least one negative return." The 29-vs-97/106 mismatch is unexplained.
**Why it matters**: An estimate with that SE cannot support any inference, yet it is presented alongside the (also non-significant but better-behaved) return and Sharpe results as if comparable. The n discrepancy suggests either a filtering step or a data-availability issue that is not documented.
**Suggestion**: Reconcile the n (state exactly which pairs enter the Sortino regression and why), and either stabilise the Sortino (e.g., winsorise extreme downside-deviation denominators, or report it descriptively only) or drop it from the inferential table with a clear note. Frame the H2 result on return and Sharpe.
**Severity**: Major

### W5: Residual non-normality and missing SBS diagnostics *
**Problem**: Shapiro–Wilk on the H1 residuals rejects normality (W = 0.9849, p = 0.0002, Table 5.6). Separately, no Cronbach's alpha is reported (ICC is used instead) and no skewness/kurtosis values appear — both expected by the SBS handbook (Ch. 5 reliability; Ch. 4 distributional diagnostics).
**Why it matters**: With N = 424 the CLT makes non-normality a minor threat to the OLS inference, but HC3/cluster SEs address *heteroskedasticity*, not non-normality, so the manuscript should not imply the robust SEs "handle" it. The missing alpha and skewness/kurtosis are rubric-compliance gaps (see EIC W1/W2).
**Suggestion**: State that non-normality is mitigated by sample size and is orthogonal to the robust-SE choice; add skewness/kurtosis to the descriptives; and either report Cronbach's alpha or justify its non-applicability for a single-item DV.
**Severity**: Minor

---

## Detailed Comments *

### Methodology / Research Design
- Primary OLS specification, controls, and block FE are appropriate and reproduced exactly. The exclusion logic being applied once (in `6_process_survey_data.py`) and the analysis receiving a clean panel is good practice.
- The merge architecture (panel SC columns NaN, authoritative values merged at runtime from `scenario_shock_score.csv`) is defensible but means **the published `analysis_panel.csv` alone cannot reproduce H1** — a reader must know to merge the metadata file. Recommend either persisting the merged SC into the panel artefact or documenting the merge step in the methods so the result is reproducible from the deposited data.

### Results / Findings
- H1 (Table 5.7): reproduced exactly. The strong control coefficients (e.g., evt_management β = −1.7726; scenario_position β = +0.1929, p < 0.0001) are plausible; note scenario_position's significance implies an order/fatigue effect worth a sentence in limitations.
- Robustness (Table 5.8): within-estimator (−0.1846, p = 0.0008) and direction split (positive-event main effect b1 = −0.4283, p < 0.0001; ×D_neg b3 = +0.1954, p = 0.5957) reproduce; the interaction spec (−0.0067, p = 0.9358) confirms ShowSC does not moderate the SC–NRS slope.
- H2 (Table 5.9): return τ = −0.1584 (p = 0.7428, d = −0.0591), Sharpe τ = 0.8790 (p = 0.6050); both correctly reported as not supporting H2. With n = 106 pairs and d ≈ −0.06, the design has very low power to detect small effects — the result is best framed as "no detectable effect," not "no effect."

### Conclusion
- Statistically, the safe claims are: H1 supported under conservative SEs; ShowSC does not move NRS; H2 not supported (with low power). The manuscript should not let the inflated HC3 t-statistics color the strength language.

---

## Questions for Authors *

1. The design specifies two-way cluster-robust SEs, but the tables report HC3. Was the cluster specification estimated and set aside? Under it, β(SC_total) is −0.4874 (SE 0.1532, t −3.1825, p 0.0015) — do you agree this should be the primary reported inference?
2. Why does the event-severity component (es_raw) relate *positively* to NRS (β = +0.3102, p < 0.0001) while loading positively on a composite that relates negatively to NRS? Does H1 survive excluding es_raw from the PCA, and how was the es_raw 10.0000 ceiling (7 of 24 scenarios) generated?
3. For the Sortino regression, why is n = 29 when the note reports 97 of 106 pairs computed, and how should an estimate with SE = 36.2226 be interpreted?
4. Given PC2's eigenvalue (1.1703) exceeds 1 and the PCA uses only 24 observations, what justifies retaining a single component?

---

## Minor Issues

### Citation Format
- N/A (Reviewer 2).

### Figures and Tables
- Table 5.9: add the exact n entering each H2 regression in a footnote; reconcile the Sortino 29/97 figures.
- Table 5.8: label whether the component decomposition uses raw or z-scored components (I reproduced the sign pattern under both; the magnitudes differ).
- pca_diagnostics.json: report the full eigenvalue spectrum, not only PC1.

### Reproducibility
- Document or persist the runtime SC merge so `analysis_panel.csv` is self-contained.

---

## Dimension Scores *

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 74 | Adequate–Strong | Instrument is novel; composite coherence is questionable (W2/W3) |
| Methodological Rigor (25%) | 64 | Weak–Adequate | Correct arithmetic; SE specification overstates precision (W1) |
| Evidence Sufficiency (25%) | 66 | Adequate | H1 robust; H2 underpowered; Sortino uninformative (W4) |
| Argument Coherence (15%) | 68 | Adequate | Sound where it tracks the conservative inference |
| Writing Quality (15%) | 80 | Strong | Tables clear; needs SE/footnote corrections |
| Methodological Rigor (re-weighted focus) | 64 | Weak–Adequate | Primary dimension for this reviewer |
| **Weighted Average** | **69.0** | **Major Revision** | Numbers reproduce; inference and composite need correction |
