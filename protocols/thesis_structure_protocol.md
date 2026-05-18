# THESIS_VERIFICATION_PROTOCOL_V1
# ROLE: Structural Compliance Auditor
# TARGET: SBS Swiss Business School EMBA/Master’s Thesis (AY 2025–26)

## 0. MISSION
Verify structural completeness, mandatory components, and APA/SBS alignment. This is a procedural audit; do not evaluate academic quality or statistical depth unless specified.

[RESULT_CODES]
- PASS: All [REQUIRED] and [MUST] conditions met.
- WARNING: Minor formatting or [RECOMMENDED] items missing; structural integrity intact.
- FAIL: One or more [REQUIRED] elements missing or [FORBIDDEN] elements present.
- HARD_FAIL: Violation of [CRITICAL_CHECKS] or [HARD_FAILURE_CRITERIA]. Escalation required.

## 1. MANDATORY_ARCHITECTURE
The thesis MUST follow this exact sequence:
1. Front Matter (Cover, Authentication, TOC, Lists, Executive Summary)
2. Main Body (Chapters 1-6)
3. References
4. Appendices

---

## 2. FRONT_MATTER_REQUIREMENTS

### 2.1 COVER_PAGE [REQUIRED]
- [MUST] Match SBS standard template.
- [REQUIRED_ELEMENTS]:
  - "SBS Swiss Business School"
  - Thesis title (Must match approval form)
  - Degree program
  - Student full name
  - Mentor full name
  - Submission date
- [FORBIDDEN]: Page number on cover.

### 2.2 AUTHENTICATION_PAGE [REQUIRED]
- [MUST]: Declaration of originality.
- [MUST]: Mentor authentication/signature placeholder.
- [REQUIRED]: Exact wording from SBS template.
- [CONDITION]: Signed only after plagiarism approval.

### 2.3 FOREWORD [OPTIONAL]
- [LIMIT]: Concise, no academic argumentation, no literature review.

### 2.4 ACKNOWLEDGEMENTS [OPTIONAL]
- [LIMIT]: Personal only, no research claims.

### 2.5 TABLE_OF_CONTENTS [REQUIRED]
- [CHECK]: All headings included.
- [CHECK]: Pagination accuracy.
- [CHECK]: Consistent numbering and hierarchy.
- [CHECK]: Appendices listed.

### 2.6 LIST_OF_TABLES [CONDITIONAL]
- [REQUIRED]: If tables exist.
- [CHECK]: Every table referenced; numbering consistent; titles match in-text.

### 2.7 LIST_OF_FIGURES [CONDITIONAL]
- [REQUIRED]: If figures exist.
- [CHECK]: Every figure referenced; numbering consistent; titles match in-text.

### 2.8 LIST_OF_ABBREVIATIONS [RECOMMENDED]
- [CHECK]: Acronyms defined once; alphabetical order.

### 2.9 EXECUTIVE_SUMMARY [REQUIRED]
- [REQUIRED_CONTENT]: Research problem, Objectives, Methodology, Main findings, Conclusions, Recommendations.
- [FORBIDDEN]: Citations, detailed literature review, extensive statistics.
- [LENGTH]: 1–3 pages.

---

## 3. MAIN_BODY_REQUIREMENTS

### CHAPTER_1: INTRODUCTION
- **1.1 Background of the Problem**: Business problem, practical relevance, industry context.
- **1.2 Background of the Study**: Academic context, literature links, rationale.
- **1.3 Purpose of the Study**: Explicit purpose, managerial/academic contribution.
- **1.4 Significance**: Academic, practical, and managerial relevance.
- **1.5 Scope and Delimitations**: Geographic, industry, time, data, and methodological boundaries.
- **1.6 Structure**: Sequential chapter overview.

### CHAPTER_2: OBJECTIVES_OF_THE_STUDY
- **2.2 Problem Statement**: Research gap clearly stated; operational problem defined.
- **2.3 Objectives**: Measurable; aligned with hypotheses and methodology.
- **2.4 Research Questions**: Must identify IV, DV, Industry, and Geography. Must align with hypotheses.
- **2.5 Hypothesis Statements [STRICT_SBS_COMPLIANCE]**:
  - [FORMAT]: Use Hₒ and Hₐ notation (not just H1/H0).
  - [ORDER]: Null hypothesis (Hₒ) MUST be listed first.
  - [WORDING_NULL]: "{IV} has no statistically significant effect on {DV}."
  - [WORDING_ALT]: "{IV} has a statistically significant effect on {DV}."
- **2.6 Definitions**: Operational, measurable definitions.
- **2.7 Assumptions**: Explicit and relevant.
- **2.8 Limitations**: Generalizability, measurement, and methodological constraints.

[DEPENDENCY_RULE]
- [CH2_TO_CH4]: Every hypothesis in 2.5 MUST be operationalized in Chapter 4 (Variable definitions).
- [CH2_TO_CH5]: Every IV/DV introduced in Chapter 2 MUST appear in Chapter 5 statistical testing.
- [CH2_TO_CH6]: Every research question in 2.4 MUST be answered in Chapter 6.

### CHAPTER_3: LITERATURE_REVIEW
- [REQUIRED]: Critical synthesis, theoretical foundation, hypothesis support.
- [FORBIDDEN]: Pure summaries, descriptive lists, chronological dumping.
- [CHECK]: Every hypothesis must be theoretically supported. APA 7 compliant.

### CHAPTER_4: COLLECTION_OF_PRIMARY_DATA
- **Research Design**: Quantitative (Experimental/Causal preferred).
- **Population/Sample**: Target defined, sampling method described, size justified.
- **Data Collection**: Instrument explained, ethics addressed.
- **Variables**: Identify IVs, DVs, and Moderators/Mediators.
- **Statistical Methods**: Define hypothesis testing, tools, and significance thresholds (p-values).
- **Instrument Design**: Likert scale (if used); survey must be in Appendix.

[STATISTICAL_VALIDATION]
- [SAMPLE]: Sample size justification required (e.g., G*Power, industry standard).
- [ASSUMPTIONS]: Statistical assumptions (Normality, Homoscedasticity, etc.) must be disclosed.
- [CONSISTENCY]: Variable operationalization and metric definitions must be identical in all chapters.

### CHAPTER_5: ANALYSIS_AND_CONCLUSIONS
- **Descriptive Statistics**: Sample characteristics, summary stats.
- **Hypothesis Testing [STRICT_SBS_WORDING]**:
  - [USE_ONLY]: "Fail to reject the null hypothesis" OR "Support for the alternative hypothesis Ha was found."
  - [FORBIDDEN]: "Accept the null", "Reject the alternative".
- **Findings Interpretation**: Linked to literature, objectives, and RQs.

### CHAPTER_6: CONCLUSIONS_AND_RECOMMENDATIONS
- **Conclusions**: Answers to RQs, summary, theoretical/practical implications.
- **Recommendations**: Managerial, Industry, and Future Research.
- **Sustainability [MANDATORY]**: Minimum one paragraph linking topic to UN SDGs/Sustainability.

---

## 4. TECHNICAL_REQUIREMENTS

### 4.1 REFERENCES [REQUIRED]
- [FORMAT]: APA 7, hanging indent.
- [VALIDATION]: 1:1 match between in-text citations and bibliography.
- [REQUIRED]: DOI where available.

### 4.2 APPENDICES [REQUIRED_STRUCTURE]
- **Appendix A**: Research Instruments (Survey, Interview protocol).
- **Appendix B**: Statistical Outputs (Regression, Correlation matrices, Robustness checks).
- **Appendix C [MANDATORY_IF_USED]**: AI Disclosure Statement (SBS wording).
- **[FINANCE_ADDITIONS]**: Model specs, Math derivations, Portfolio logic, Risk formulas.

[APPENDIX_LINKAGE]
- [CHECK]: Every appendix must be referenced at least once in the main text (Chapters 1-6).

[AI_USAGE_COMPLIANCE]
- [DISCLOSURE]: AI-assisted text generation must be explicitly disclosed in Appendix C.
- [VERIFICATION]: Author must state that AI-generated content was reviewed and verified.
- [INTEGRITY]: No uncited fabricated references (hallucinations).

### 4.3 FORMATTING_RULES
- [PAGINATION]: Front matter (Roman/Lower) vs Main body (Arabic).
- [LAYOUT]: Consistent margins, fonts, spacing, and heading hierarchy (no skipped levels).
- [TABLES/FIGURES]: APA captions, source attribution, referenced in-text BEFORE appearance.

[CROSS_REFERENCE_CHECK]
- [SEQUENCE]: Every table/figure must have sequential numbering.
- [PLACEMENT]: Every table/figure must be introduced in text before its appearance.
- [VALIDATION]: Every table/figure in the lists (2.6, 2.7) must be referenced in the main body text.

---

## 5. INTEGRITY_AND_FAILURE_CONDITIONS

### [CRITICAL_CHECKS]
1. **Originality**: Plagiarism score < SBS threshold.
2. **Primary Research**: MUST have original empirical/quantitative component.
3. **Hypothesis Testing**: MUST be explicitly tested with appropriate stats.

### [HARD_FAILURE_CRITERIA]
- Missing Hypothesis statements or incorrect wording.
- Missing Primary Quantitative Research.
- Missing Chapter 4 or 5.
- No Sustainability reference.
- No Mentor Authentication.
- Misalignment between Research Questions and Hypotheses.

---

## 6. QUANTITATIVE_FINANCE_ENHANCEMENTS
- Variable dictionary, model specs, robustness tests, factor construction, data preprocessing, reproducibility protocol.