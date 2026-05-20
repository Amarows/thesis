# Independent Verification Prompt – Thesis Results Consistency Review

## Purpose

This prompt is for an independent reviewer to verify that all numerical
results, coefficients, and interpretive claims in `thesis_final.md`
(Chapters 5 and 6) are consistent with the pipeline-generated results in
`results/thesis_results.md` and `results/tables/*.csv`.

The reviewer has no prior context about the thesis. Read only what the
files contain. Do not assume anything is correct.

---

## Step 1 – Fetch all source files

Fetch the following files from `https://api.github.com/repos/Amarows/thesis/contents/`:

1. `thesis_final.md` – the compiled thesis document (Chapters 5 and 6 only)
2. `results/thesis_results.md` – pipeline-generated results
3. `results/tables/tbl_h1_main.csv` – primary H1 regression table
4. `results/tables/tbl_h1_robustness.csv` – H1 robustness specifications
5. `results/tables/tbl_h2_portfolio.csv` – H2 portfolio results
6. `results/tables/tbl_nrs_sentiment_alignment.csv` – alignment diagnostic
7. `results/tables/tbl_descriptive_respondents_freq.csv` – respondent descriptives

Use the GitHub API with Authorization header. All files are base64-encoded
in the `content` field of the API response.

---

## Step 2 – Extract ground-truth values from pipeline files

From the pipeline files, extract and record the following values exactly
as they appear. These are the ground truth.

### From `thesis_results.md`

- Total respondents (N)
- Total observations
- Primary β₁ on SC_total (from s5_5_1_h1 block)
- Primary SE, t, p, CI for β₁
- H2 tau (return), SE, t, p, CI, Cohen's d (option_b_individual, portfolio_return)
- H2 tau (Sharpe), SE, t, p, CI, Cohen's d (option_b_individual, sharpe_ratio)
- H2 verdict (supported / not supported)
- Overall NRS–sentiment alignment rate
- Lowest alignment category and its rate
- ICC(2,1) values for Block 1, 2, 3
- Residual normality Shapiro-Wilk W and p

### From `tbl_h1_robustness.csv`

For each spec, record: spec name, beta1, se, t, p, ci_lo, ci_hi, r2

- spec_1_quintiles (r2 only)
- spec_2_within
- spec_3_component_ac_e
- spec_3_component_se_e
- spec_3_component_ai_e
- spec_3_component_es_raw
- spec_4_interaction
- spec_5_direction_b1
- spec_5_direction_b3

Also compute: spec_5 compound effect = spec_5_direction_b1_beta +
spec_5_direction_b3_beta. Note whether spec_5_direction_b3 is
statistically significant at α = 0.05.

---

## Step 3 – Extract claims from thesis_final.md

Locate and extract every numerical claim in the following sections.
Record the exact value stated and the line or paragraph context.

### Sections to check

- Section 5.2.1 – respondent N, mean experience, median experience
- Section 5.2.2 – mean NRS overall, by condition; SC_total range
- Section 5.3 – scenario count (24 scenarios, 3 blocks)
- Section 5.4 – Table 5.4a NRS totals; ICC values per block; Shapiro-Wilk W and p
- Section 5.5.1 – primary β₁; SE; t; p; CI; R²; N
  - Spec 2 β₁ and p
  - Spec 3: all four component betas and p-values
  - Spec 4 interaction beta and p
  - Spec 5 β₁, β₃, compound effect, and significance statement
- Section 5.5.2 – H2 tau (return), p, Cohen's d; H2 tau (Sharpe), p, Cohen's d
- Section 5.6.1 – β₁ cited in narrative; ES_raw beta cited; alignment rate cited
- Section 5.6.1.1 – overall alignment rate; lowest category and its rate
- Section 5.7 / Interim Conclusions – β₁; H2 tau; H2 p; H2 verdict;
  any Sharpe significance claim
- Section 5.9.2 – N respondents
- Section 5.9.4 – reliability metric type (ICC or Cronbach); values per block;
  whether a sub-threshold limitation is claimed
- Chapter 6 (6.2, 6.3, 6.9) – β₁; H2 verdict and p-value cited

---

## Step 4 – Compare and flag inconsistencies

For each value extracted in Step 3, compare it against the ground truth
from Step 2. Flag any discrepancy as follows:

**CRITICAL** – value is wrong AND interpretation is affected
(e.g., a significant result is described as not significant, or vice versa;
a sign is reversed; a wrong statistic is cited)

**MINOR** – value is numerically wrong but interpretation is unaffected
(e.g., rounding difference, minor magnitude change)

**STALE** – value appears to come from an earlier pipeline run
(e.g., N=456 when pipeline reports 424)

**STRUCTURAL** – text references a statistic or methodology that no longer
exists (e.g., Cronbach alpha after replacement with ICC)

---

## Step 5 – Check interpretive claims

Beyond numerical accuracy, verify the following interpretive claims
against the pipeline results:

1. **Spec 5 direction asymmetry claim**: Does the thesis claim a
   statistically significant difference between positive- and
   negative-sentiment shocks? If so, is β₃ actually significant
   at α = 0.05 in the pipeline output?

2. **Loss-aversion amplification claim**: Does the thesis claim that
   negative shocks trigger risk-seeking or risk-amplification behaviour?
   Is the sign and significance of β₃ consistent with this claim?

3. **Sharpe ratio significance claim**: Does the thesis claim a
   statistically significant Sharpe ratio treatment effect? Is the
   H2 Sharpe p-value actually < 0.05 in the pipeline?

4. **H2 verdict**: Does the thesis correctly state H2 as not supported?
   Is this consistent with all H2 p-values in the pipeline?

5. **Alignment lowest category**: Does the thesis correctly identify
   the sentiment category with the lowest alignment rate?

6. **ICC vs Cronbach**: Does Section 5.9.4 correctly describe ICC(2,1)
   and report ICC values? Or does it still reference Cronbach alpha?

7. **Limitation claim on reliability**: Does Section 5.9.4 claim
   sub-threshold reliability as a limitation? If so, is this consistent
   with the ICC values exceeding 0.70?

---

## Step 6 – Produce a structured report

Output a report with three sections:

### A. CRITICAL inconsistencies
List each one with: location | thesis claim | pipeline value | impact

### B. MINOR / STALE inconsistencies
List each one with: location | thesis claim | pipeline value

### C. Verification passed
List all claims that were verified as correct.

If there are no inconsistencies, state "ALL RESULTS VERIFIED" explicitly.

