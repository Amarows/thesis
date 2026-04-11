# Task 1 – Structural Blueprint for Chapter 4 Restructure (LOCKED)

## Issue: #93 | Branch: 93-chapter4-restructure

---

## A. Final Chapter 4 Table of Contents

```
# Chapter 4. Research Data and Primary Data Collection

  ## 4.1 Chapter Introduction
  ## 4.2 Research Design
    ### 4.2.1 Research Paradigm
    ### 4.2.2 Conceptual Framework

  ## 4.3 Market and Events Data
    ### 4.3.1 Portfolio Scope and Stock Selection
    ### 4.3.2 Market Price Data
    ### 4.3.3 News Data
    ### 4.3.4 Event Screening and Scenario Selection
    ### 4.3.5 Shock Score Component Definitions
    ### 4.3.6 Shock Score Dashboard Design

  ## 4.4 Design of the Survey
    ### 4.4.1 Overall Survey Structure
    ### 4.4.2 Scenario Presentation Format
    ### 4.4.3 Treatment Implementation
    ### 4.4.4 Counterbalancing Strategy
    ### 4.4.5 Net Risk Stance Response Measure
    ### 4.4.6 Confound Controls
    ### 4.4.7 Population, Sample, and Recruitment
    ### 4.4.8 Survey Administration and Response Rates
    ### 4.4.9 Pilot Test

  ## 4.5 Analytical Framework
    ### 4.5.1 Regression Specifications
    ### 4.5.2 Inference and Clustering

  ## 4.6 Chapter Conclusion
```

---

## B. Content Migration Map

### INTO Chapter 4

| Source | Thesis Lines | Content | Target |
|--------|-------------|---------|--------|
| Ch 2 Technical Appendix 2 | 303–317 | Event screening algorithm (3 stages) | 4.3.4 |
| Ch 2 Technical Appendix 3 | 319–337 | AC_e, SE_e, AI_e, ES_e definitions; PCA | 4.3.5 |
| Ch 2 Section 2.6.3 | 165–172 | SC_total PCA formula | 4.3.5 |
| Ch 2 Section 2.6.3 | 182–190 | Persistence score and horizon buckets | 4.3.5 |
| Ch 2 Section 2.6.3 | 174–180 | Dashboard signals (4 bullets) | 4.3.6 |
| Ch 2 Section 2.6.3 | 192–200 | Protocol trigger definitions | 4.3.6 |
| Ch 2 Technical Appendix 1 | 271–301 | Regression specifications (H1, H2, interaction, FE) | 4.5.1 |
| Ch 2 Technical Appendix 1 | 284 | Two-way clustering | 4.5.2 |
| protocols/ | scenario_selection_protocol.md | Selection criteria and balance constraints | 4.3.4 |
| protocols/ | presentation_protocol.md | Visual presentation design | 4.4.2 |
| 1_download.py | Script logic | IBKR price and news download procedures | 4.3.2, 4.3.3 |

### Within Chapter 4 – Reorganisation

| Current Location | Thesis Lines | Content | New Target |
|-----------------|-------------|---------|------------|
| 4.2.3 Portfolio construction and stock selection | 688–701 | Stock universe, S&P scope | 4.3.1 |
| 4.2.3 Portfolio weighting | 702–705 | 1/N equal weight paragraph | 4.3.1 (fold in) |
| 4.2.3 Scenario design | 706–740 | Selection criteria, balance constraints | 4.3.4 |
| 4.2.3 Scenario presentation format | 742–766 | Chart layout, news display | 4.4.2 |

### OUT OF Chapter 4

| Source | Thesis Lines | Content | Target |
|--------|-------------|---------|--------|
| 4.4 Descriptive Statistics | 872 | Section header | Ch 5.2 |
| 4.4.1 Respondent Descriptive Statistics | 874–893 | Demographics, experience | Ch 5.2.1 |
| 4.4.2 Descriptive Analysis of Data | 895–921 | Summary stats, distributions, figures | Ch 5.2.2 |

### NEW Content to Write

| Task | Section | Source Material |
|------|---------|-----------------|
| Task 2 | 4.3.2 Market Price Data | 1_download.py, IBKR API |
| Task 2 | 4.3.3 News Data | 1_download.py, Benzinga via IBKR |
| Task 3 | 4.3.1 Portfolio Scope and Stock Selection | portfolio.csv, scenario_manifest.csv |
| Task 3 | 4.3.2 (summary paragraphs) | Assembly report data |

---

## C. Chapter 2 Residual After Migration

Section 2.6.3 (Shock Score) retains:
- Opening definitional paragraph (line 163)
- Treatment indicator ShowSC definition (lines 202–208)
- New forward reference: "The construction methodology, component definitions,
  and Shock Score dashboard design are documented in Section 4.3."

Technical Appendices 1–3 (lines 271–337): removed entirely from Chapter 2.
Section 2.9 (Chapter Conclusion): forward reference updated.

---

## D. Chapter 5 Impact

```
# Chapter 5. Analysis and Conclusions

  ## 5.1 Chapter Introduction
  ## 5.2 Descriptive Statistics              <- from old 4.4
    ### 5.2.1 Respondent Descriptive Statistics  <- from old 4.4.1
    ### 5.2.2 Descriptive Analysis of Data       <- from old 4.4.2
  ## 5.3 Tests for Normality and Reliability
  ## 5.4 Hypothesis Testing
    ### 5.4.1 Testing of Hypothesis H1
    ### 5.4.2 Testing of Hypothesis H2
  ## 5.5 Results Interpretation
    ### 5.5.1 Impact of Information Shocks on Risk-Return
    ### 5.5.2 Incremental Effect of the Shock Score
  ## 5.6 Interim Conclusions
  ## 5.7 Chapter Conclusion
```

---

## E. Handbook Compliance (SBS Section 3.6.1)

| Handbook Requirement | Location | Status |
|---------------------|----------|--------|
| 4.1 Chapter introduction | 4.1 | Compliant |
| 4.2.1 Research Paradigm | 4.2.1 | Compliant |
| 4.2.2 Conceptual framework | 4.2.2 | Compliant (Task 8) |
| 4.2.3 Design of research instrument | 4.4 | Compliant (renumbered) |
| 4.2.4 Pilot test | 4.4.9 | Compliant (Task 7) |
| 4.2.5 Population and sample | 4.4.7 | Compliant (renumbered) |
| 4.2.6 Sampling technique | 4.4.7 | Merged into Population |
| 4.3.1 Key dates | 4.4.8 | Compliant (merged) |
| 4.3.2 Return rates | 4.4.8 | Compliant (merged) |
| 4.4.1 Respondent descriptive statistics | 5.2.1 | Moved per #93 decision |
| 4.4.2 Descriptive analysis of data | 5.2.2 | Moved per #93 decision |

---

## F. Removal Log for OneDrive Shared Document

To be populated during Task 4 execution. Will contain exact section headers
and line ranges removed from Chapters 2 and 3, for manual deletion in Word.
