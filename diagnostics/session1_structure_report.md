# Thesis Structure Diagnostic Report – Session 1
**Protocol:** `thesis_structure_protocol.md` V2 (2026-05-19)  
**Audit target:** `thesis_final.md` (commit `4a375568`, 2026-05-20T21:44:47Z)  
**Pipeline freshness check:** last `9_compile_thesis.py` run 2026-05-20T21:40:46Z → thesis_final.md committed 2026-05-20T21:44:47Z → **CURRENT** (not stale).  
**Auditor:** Claude Sonnet 4.6, 2026-05-21

---

## Summary Counts

| Result | Count |
|--------|-------|
| HARD_FAIL | 4 |
| FAIL | 13 |
| WARNING | 7 |
| PASS | 22 |
| **Total findings** | **46** |

---

## Section 1 – Mandatory Architecture

### 1.A Front Matter Sequence
**FAIL** – The physical document places `Appendix 4. Survey Questionnaire` (line 1574) *before* the Back Matter list and before Appendices 1, 2 in the compiled output. The SBS sequence (Cover → Title → Authentication → Foreword → TOC → Lists → Executive Summary) is broadly respected in the front matter, but the survey content appears mid-document, out of sequence.

### 1.B Main Body Sequence (Chapters 1–6)
**PASS** – Chapters 1 through 6 appear in correct order.

### 1.C References placement
**FAIL** – No standalone `# References` heading exists in `thesis_final.md`. The back matter block (line 1839) contains a bullet `- References` as a placeholder, but no actual reference list section is rendered. The references are embedded inline as hyperlinks throughout the text but are never collected under a dedicated `References` heading. This also constitutes a breach of the HARD_FAILURE_CRITERIA ("Reference list numbered as a chapter" is not the issue; the issue is that no reference list exists as a rendered section at all).

### 1.D Appendix Sequence
**HARD_FAIL** – The SBS-mandated appendix sequence is violated in two ways. First, `Appendix 4. Survey Questionnaire` is physically located at line 1574, *before* Back Matter and before the rendered Appendix 1 (line 1849) and Appendix 2 (line 1904). Second, the Back Matter list identifies `Appendix 3` as "Blank Questionnaire / Instrument" — the Turn-In Checklist (required as Appendix 3 per protocol §4.2) is absent from the document entirely.

---

## Section 2 – Front Matter Requirements

### 2.1 Cover Page
**PASS** – Title, degree program, student name, student ID, mentor name (Dr. Stefano Canossa), and submission year (September 2026) are present. Institutional name reads "SBS SWISS BUSINESS SCHOOL" — correct.

**WARNING** – The cover page content is duplicated: the same `<div>` block appears twice (lines 3–22 and 24–43). One instance will be redundant in the rendered Word document. Edit target: `thesis.md`, front matter cover section.

### 2.2 Authentication Page
**PASS** – Declaration of originality with student name, ID, and matriculation number is present (line 58). Mentor certification placeholder with Dr. Stefano Canossa is present (line 64). Signature lines are present.

**WARNING** – The authentication section is rendered under the heading `## Authentication of Work` which is a Level 2 sub-heading under the title heading, not a standalone page heading. In the compiled Word document this may not force a new page. Verify that the compilation script inserts a page break before this section.

### 2.3 Foreword
**PASS** – Heading spelt "Foreword" (correct, not "Forward"). Contains justification for the thesis topic and professional motivation.

**FAIL** – Acknowledgements sub-section is absent. The Foreword contains no thanks to family, mentor, or Program Manager. Per protocol §2.3, Acknowledgements is a required sub-component of the Foreword. Edit target: `thesis.md`, Foreword section.

### 2.4 Table of Contents
**WARNING** – The TOC is represented only as a bullet list placeholder (`- Table of Contents`, line 83). No populated TOC with page numbers is visible in `thesis_final.md`. A proper TOC with Level 1–3 headings and page numbers must be present in the submitted Word document. This is a compilation/Word formatting step, not a thesis.md content gap, but must be verified before submission.

### 2.5 List of Tables / List of Figures
**WARNING** – Both Lists of Tables and Figures are present only as placeholder bullets in the front matter (lines 84–85). No populated lists are rendered. As with the TOC, these must be complete and accurate in the submitted Word document. Verify that `9_compile_thesis.py` or the Word formatting step populates them.

### 2.6 List of Abbreviations
**WARNING** – Present only as a placeholder bullet (line 86). Must be verified as populated in the final Word document.

### 2.7 Executive Summary Length and Completeness
**PASS** – Required content elements (research problem, objectives, methodology, main findings, conclusions, recommendations) are all present.

**FAIL** – The Executive Summary contains the footnote: *"Note: Results reported above are based on the sample available at the time of writing. Final results will be updated upon completion of data collection."* (line 107). This caveat is inconsistent with thesis_final.md representing the completed study (N = 53 per Chapter 5). Additionally, the Executive Summary reports N = 67 respondents and β₁ = −0.2836, while Chapter 5 reports N = 53 and β₁ = −0.4874. The figures are contradictory (see finding 5.A below). The stale caveat note should be removed from thesis.md; the figures must be reconciled.

### 2.8 Pagination Scheme
**WARNING** – `thesis_final.md` is a Markdown source file; pagination cannot be verified at this stage. Pagination compliance (Roman numerals for front matter, Arabic from Chapter 1, consistent placement) must be confirmed in the compiled Word document before submission.

---

## Section 3 – Main Body Requirements

### 3.A Chapter 1 – Introduction
**PASS** – Sections 1.1 (Background of the Problem) and 1.2 (Background of the Study) are present and correctly structured. The thesis also includes Sections 1.3 through 1.6 (Purpose, Significance, Scope, Structure), which the protocol notes as permissible with mentor agreement and not to be flagged as FAIL. No content duplication with Chapter 2 is observed that would constitute a structural violation.

### 3.B Chapter 2 – Structure
**PASS** – Sections 2.1 through 2.9 are present and the SBS-mandated layout is followed. Section 2.6 (Additional Research Questions / Definitions of Key Terms) and 2.9 (Chapter Conclusion) are both present.

### 3.C Chapter 2 – Research Question Formatting
**FAIL** – The two research questions (lines 300–302) are rendered with a bare `##` prefix and no section label (e.g., `## RQ1` or `## Research Question 1`). The resulting Markdown parses as Level 2 headings whose text is the question itself, rather than properly labelled numbered questions set out in body text. The same malformed `##` prefix is applied to all entries in Section 2.6 (Definitions, lines 328–345) and Section 2.8 (Limitations/Assumptions, lines 373–387), rendering paragraphs as headings. This is a pervasive formatting error in thesis.md affecting Sections 2.4, 2.6, 2.7, and 2.8.

### 3.D Chapter 2 – Hypothesis Notation
**PASS** – In Section 2.5 the null and alternative hypotheses use correct subscript notation (H1₀/H1ₐ, H2₀/H2ₐ, lines 310–320). Null hypothesis precedes alternative hypothesis. Wording is compliant with SBS format.

**FAIL** – Appendix 1 (Thesis Approval Form, lines 1867–1874) reproduces hypothesis statements using the non-compliant H1o/H1a/H2o/H2a notation (plain Latin letters) rather than the required subscript characters H1₀/H1ₐ/H2₀/H2ₐ. The approval form is an official SBS document, and notation inconsistency between the form and the body may trigger a format review flag. Edit target: thesis.md, Appendix 1 section.

### 3.E Chapter 2 – Cross-Chapter Linkage (H to Ch.4/Ch.5/Ch.6)
**PASS** – H1 and H2 are operationalised in Chapter 4 (Section 4.5). Both IVs/DVs appear in Chapter 5 testing. Both RQs are answered in Chapter 6.

### 3.F Chapter 2 – Section 2.3.3 Empty
**FAIL** – Section 2.3.3 "Measuring Changes in Portfolio Risk – Return Characteristics" (line 293) has a heading but no body text. The section is immediately followed by Section 2.4, leaving 2.3.3 as an empty sub-section. Edit target: thesis.md, Section 2.3.3.

### 3.G Chapter 3 – Literature Review Structure
**PASS** – Chapter Introduction (3.1), thematic subchapters (3.2–3.5), gap analysis and limitations (3.6), and Chapter Conclusion (3.7) are all present. Literature is synthesised thematically, not chronologically. APA 7 citations are used throughout.

**WARNING** – Section 3.1 is titled "Link Between Literature and Research Hypotheses" which functions as a chapter introduction but does not explicitly describe the layout of Chapter 3. The protocol requires 3.1 to describe the chapter layout. This is a minor structural deviation.

### 3.H Chapter 4 – Mandatory Sub-Sections
**PASS** – Sections 4.1 (Introduction), 4.2.1 (Research Paradigm), 4.2.2 (Conceptual Framework), 4.3 (Market and Events Data), 4.4 (Survey Design), 4.4.9 (Pilot Test), 4.4.7 (Population and Sample), 4.4.8 (Administration/Return Rates), 4.5 (Analytical Framework/Regression Specifications), and 4.6 (Chapter Conclusion) are all present.

**WARNING** – Descriptive Statistics (Section 4.4 in the SBS template) are deferred to Chapter 5. The chapter conclusion (Section 4.6, line 1155) includes an explicit explanatory note justifying this placement with reference to "the SBS handbook template (section 3.6.1)". This placement is non-standard and departs from the SBS layout. The justification note itself is appropriate, but the deviation should be confirmed as acceptable with the mentor before submission.

### 3.I Chapter 4 – Numerical Inconsistency: Portfolio Universe
**FAIL** – Section 4.1 introduction states the survey uses 24 stocks; Table 4.1 lists 24 stocks. The Chapter 4 Conclusion (line 1147) states "the portfolio universe comprises 39 candidate U.S.-listed equities drawn from the S&P 500, with 36 assigned to three mutually exclusive scenario blocks." The numbers 39/36 contradict the 24-stock universe described throughout Chapter 4. Edit target: thesis.md, Section 4.6 conclusion paragraph.

### 3.J Chapter 4 – Statistical Validation Checks
**PASS** – Sample size justification (G*Power argument, Cohen's f² ≈ 0.05, power 0.80) is present. The seven-point NRS scale is confirmed as Likert-compliant. Latin square counterbalancing is documented.

**WARNING** – The SBS Appendix 6 guidance specifies a "strongly disagree to strongly agree" anchored Likert scale. The NRS scale uses different anchors ("Strongly reduce / Strongly increase"). The thesis acknowledges the NRS is a purpose-built scale rather than a generic Likert scale, and justification is provided (Section 4.4.5). However, no explicit cross-reference to SBS Appendix 6 is made. The mentor should confirm this deviation is pre-approved.

### 3.K Chapter 4 – Figure 4.3 Placeholder
**FAIL** – Figure 4.3 "Example Scenario Presentation in the Treatment Condition" (line 977) is a placeholder: the Note reads "To be inserted upon survey deployment." This placeholder has not been filled. The figure is referenced in the text but not present. Edit target: thesis.md, Section 4.4.2, Figure 4.3.

### 3.L Chapter 5 – Mandatory Sub-Sections
**PASS** – Sections 5.1 (Introduction), 5.2 (Descriptive Statistics), 5.4 (Tests for Normality and Reliability), 5.5 (Hypothesis Testing), 5.7 (Interim Conclusions), 5.8 (Chapter Conclusion), and 5.9 (Limitations) are all present. The protocol-required 5.4 Interim Conclusion maps to the thesis's Section 5.7.

### 3.M Chapter 5 – Duplicate Paragraph in Section 5.6.1
**FAIL** – Section 5.6.1 (lines 1367–1371) contains two consecutive near-identical paragraphs both beginning "The results are evaluated against the behavioural finance literature suggesting that external information shocks exert a systematic influence on portfolio managers' risk-stance decisions." The first (plain beta notation) and the second (Unicode β notation) cover substantially the same content with minor differences. One paragraph is a residual draft; the second, more complete version (with the Spec 5 direction-interaction result) should be retained. Edit target: thesis.md, Section 5.6.1.

### 3.N Chapter 5 – Five-Step Hypothesis Testing Sequence
**FAIL** – The SBS five-step procedure (state hypotheses → select significance level → identify test statistic → formulate decision rule → arrive at decision) is not explicitly structured as five labelled steps in Sections 5.5.1 or 5.5.2. The hypothesis text is presented in Section 2.5; the significance level (α = 0.05) is stated; the test statistic (OLS with HC3) is named; but the decision rule is not formally stated as a numbered step, and the "arrive at decision" step is written as an inline conclusion rather than a distinct procedural declaration. The SBS template requires the five steps to be explicitly visible. Edit target: thesis.md, Sections 5.5.1 and 5.5.2.

### 3.O Chapter 5 – SBS-Compliant Hypothesis Result Wording
**WARNING** – The thesis uses "H1 is supported" and "H2 is not supported" (lines 1316, 1346, 1413) rather than the SBS-preferred phrasing "Fail to reject the null hypothesis" (for H2) or "Support for the alternative hypothesis Hₐ was found" (for H1). Neither "Accept the null" nor "Reject the null" appears, so no forbidden phrase is used. However, "is supported"/"is not supported" is not one of the two SBS-permitted formulations listed in protocol §3.K. A closer alignment with the two permitted forms is recommended. Edit target: thesis.md, Sections 5.5.1, 5.5.2, 5.7, 5.8.

### 3.P Chapter 5 – Table 5.x Unnumbered
**FAIL** – Table 5.x (SC_total PCA Diagnostics, line 1214) retains a placeholder label "Table 5.x" rather than a sequential number (e.g., Table 5.2). This is an unfilled placeholder in thesis_results.md that was merged into thesis_final.md without correction. Edit target: results/thesis_results.md (pipeline-generated table label), or thesis.md if the table is manually authored.

### 3.Q Chapter 6 – Mandatory Sub-Sections
**PASS** – Sections 6.1 (Introduction), 6.2 (Summary of Findings), 6.3 (Overall Conclusions), 6.4 (Recommendations), 6.5 (Areas for Future Research), 6.6 (Lessons Learned), 6.7 (Ethical Considerations), 6.8 (SDG Implications), and 6.9 (Chapter Conclusion) are all present. This satisfies the HARD_FAILURE check for §6.5, §6.6, and §6.7.

### 3.R Chapter 6 – Section 6.2.1 Empty
**FAIL** – Section 6.2.1 "Summary of Secondary Research" (line 1456) has a heading but no body text. The content appears to have been omitted; 6.2.2 immediately follows with content. Edit target: thesis.md, Section 6.2.1.

### 3.S Chapter 6 – Sections 6.4.1 and 6.4.2 Empty
**FAIL** – Sections 6.4.1 "Recommendations for Portfolio Managers" and 6.4.2 "Recommendations for Risk Governance" (lines 1494–1495) are empty headings. The general recommendations content is present in the 6.4 parent section but the labelled sub-sections contain no body text. Edit target: thesis.md, Sections 6.4.1 and 6.4.2.

### 3.T Chapter 6 – Voice Register in Section 6.6
**PASS** – Section 6.6 Lessons Learned is written in first person ("The most consequential methodological lesson concerns…" uses third-person framing at the section level, but the section body uses "I" implicitly through authorial voice with sentences like "If the study were to be repeated, two further changes would be made."). On balance the first-person requirement is largely met. Sections 6.1–6.5 and 6.7–6.9 maintain third-person register.

**WARNING** – "the researcher's professional network" (line 1051, Chapter 4) uses "the researcher" as a third-person self-reference. The protocol explicitly flags this as FORBIDDEN ("the researcher" is in the same prohibited category as "the author"). Two additional instances of "to the author's knowledge" appear in Chapters 1 (line 185) and 3 (line 605). While "the author's knowledge" is a conventional academic hedging phrase, the protocol §3 VOICE_REGISTER_CHECK lists "the author" and "the researcher" as FORBIDDEN outside Section 6.6. Edit target: thesis.md, Sections 1.4.1, 3.6.3, 4.4.7.

---

## Section 4 – Technical Requirements

### 4.A References – No Dedicated Reference Section
**HARD_FAIL** – There is no standalone `# References` section in `thesis_final.md`. All citations appear inline as Markdown hyperlinks throughout the text but are never collected into a formatted, alphabetically sorted APA 7 reference list. The back matter bullet `- References` is a placeholder only. Per protocol §4.1, the reference list is required. Per the HARD_FAILURE_CRITERIA, a reference list that is absent (or numbered as a chapter) triggers HARD_FAIL. In this case, the list is entirely absent from the compiled output. The `references.md` file exists in the repository but has not been integrated into the `9_compile_thesis.py` compilation pipeline. Edit target: integrate `references.md` into compilation pipeline; this is already on the remaining-work list per project context.

### 4.B Appendices – SBS Mandatory Sequence
**HARD_FAIL** (same as finding 1.D above, providing technical detail) – Required sequence per protocol §4.2:  
- Appendix 1: Signed thesis approval form ✓ (present, line 1849)  
- Appendix 2: AI Disclosure Statement ✓ (present, line 1904)  
- Appendix 3: Turn-In Checklist ✗ **ABSENT** — replaced by "Blank Questionnaire / Instrument"  
- Appendix 4: Blank survey questionnaire ✗ **MISPLACED** — the survey content is at line 1574, before Appendices 1–2 in the compiled document  
  
The Turn-In Checklist (SBS Appendix 11 template) is not present anywhere in `thesis_final.md`. The survey questionnaire occupies Appendix 4's slot in Back Matter but is physically before Appendices 1 and 2 in the document body. This is a structural violation of protocol §4.2 and triggers HARD_FAIL.

### 4.C AI Disclosure Statement
**PASS** – Present as Appendix 2 (line 1904). All AI-assisted activities (FinBERT, Claude Sonnet for summaries, Claude Code for development, OpenAI deep search for literature, Claude Opus for style review) are itemised. The statement confirms author review and verification.

### 4.D Appendix Linkage
**FAIL** – Appendix 4 (Survey Questionnaire at line 1574, and in the Back Matter list at line 1845) is not referenced by number at any point in the main text (Chapters 1–6). Chapter 4 refers to survey content but does not state "see Appendix 4." Protocol §4.2 requires every appendix to be referenced by name and number in the main text before it appears. Edit target: thesis.md, Section 4.4.1 or 4.4.9 (add explicit cross-reference to Appendix 4).

### 4.E Formatting Rules – Typography
**WARNING** – `thesis_final.md` is the Markdown source; compliance with Calibri 11pt, double-spacing, left-alignment, and indented paragraphs cannot be verified from the source file. These must be confirmed in the compiled Word document. Flagged as WARNING to ensure explicit pre-submission verification.

### 4.F Language – Mixed US/UK English
**FAIL** – The thesis contains systematic mixing of US and UK English spellings. UK forms documented: "behaviour/behavioural" (lines 119, 131, 133, 135, 143, 151, 157, 161, 167, 171, 177, and many others), "realise/realisation" (line 117), "organisation" (implicitly). US forms are used in adjacent sentences: "behavior/behavioral" (lines 98, 152, 267, and many others). The protocol requires US English only throughout. The inconsistency is pervasive and affects dozens of lines. A global find-and-replace sweep in thesis.md is needed. Edit target: thesis.md, global.

### 4.G "the author" / "the researcher" Voice Violations
**FAIL** – See finding 3.T for instances. Three occurrences in main chapters: "to the author's knowledge" (lines 185, 605, 1469); "the researcher's professional network" (line 1051). All are outside Section 6.6 and are therefore non-compliant per the VOICE_REGISTER_CHECK. Edit target: thesis.md, Sections 1.4.1, 3.6.3, 4.4.7, 6.3.1.

### 4.H Tables and Figures – Captions
**PASS** – Tables and Figures use APA-compliant captions (title above, Note below) throughout.

**WARNING** – Figure 4.3 is a placeholder (see finding 3.K). Also, Table 5.x is an unfilled label (see finding 3.P).

---

## Section 5 – Integrity and Critical Checks

### 5.A Executive Summary vs. Chapter 5 Data Inconsistency
**FAIL** – The Executive Summary (line 99) reports N = 67 respondents, 536 observations, β₁ = −0.2836, and τ = 0.0076 (p = 0.3770). Chapter 5 (lines 1171, 1316, 1346) reports N = 53 respondents, 424 observations, β₁ = −0.4874, and τ = −0.1584 (p = 0.7428). These are irreconcilable discrepancies within the same document: the Executive Summary contains stale figures from a prior pipeline run, while Chapter 5 contains the current results. The Executive Summary also retains a caveat ("Final results will be updated upon completion of data collection") that is inconsistent with a completed study. Edit target: thesis.md Executive Summary section (all numerical findings must be updated to match Chapter 5 outputs, and the caveat note must be removed). This also affects results/thesis_results.md if the Executive Summary is pipeline-generated.

### 5.B Word Count
**PASS** – The main body (Chapters 1–6, estimated from thesis_final.md text between Chapter 1 heading and Appendix 4) is approximately 34,845 words, well above the 20,000-word minimum.

### 5.C Primary Research Component
**PASS** – Original empirical quantitative survey study with N = 53 professional equity portfolio managers is present.

### 5.D Hypothesis Testing
**PASS** – Hypotheses are explicitly tested with OLS regression (HC3) for H1 and individual-portfolio regression (Option B) for H2. Results are reported with test statistics, p-values, and confidence intervals.

### 5.E Pilot Test Documentation
**PASS** – Pilot test is documented in Section 4.4.9 (lines 1069–1095): dates (3–21 April 2026), instrument (Block 1, V1/V2), N = 12 completions, five feedback questions, and instrument modifications made before full deployment are all recorded.

### 5.F Interim Conclusion
**PASS** – Section 5.7 "Interim Conclusions" is present (line 1411) and summarises H1 supported, H2 not supported, with key statistics.

### 5.G SDG Implications
**PASS** – Section 6.8 is present with explicit linkage to SDG 8 (Decent Work and Economic Growth) and SDG 10 (Reduced Inequalities).

### 5.H AI Disclosure Statement
**PASS** – Present as Appendix 2.

### 5.I Mentor Authentication
**PASS** – Authentication page with Dr. Stefano Canossa's certification and signature placeholder is present (line 58–68).

---

## Section 6 – Quantitative Finance Enhancements

### 6.A Variable Dictionary
**PASS** – Table 4.4 (Shock Score Components, line 863) provides definitions with source and computation for all four SC_total components. Section 2.6 defines key terms including NRS, ShowSC, and risk-return ratio. Control variables (experience, block, ShowSC) are listed in the regression specifications.

### 6.B Model Specifications Written Out
**PASS** – Section 4.5.1 presents all regression equations in full mathematical notation. PCA composite formula is given in Section 4.3.5.

### 6.C Robustness Checks
**PASS** – Five robustness specifications (quintile dummies, respondent FE, decomposed components, SC×ShowSC interaction, direction-interaction) are documented in Section 4.5.1 and results reported in Table 5.3.

### 6.D Factor Construction / PCA Documentation
**PASS** – PCA construction is documented in Sections 4.3.5 and 5.2.3. PC1 eigenvalue (2.1027), variance explained (50.38%), and all four component loadings are reported.

### 6.E Data Preprocessing
**PASS** – Outlier treatment (ES_e capped at 10.0), fallback procedures, and uniform-response exclusion criterion are documented in Sections 4.3.4–4.3.5 and 4.4.8.

### 6.F Reproducibility
**PASS** – Data sources (IBKR, Benzinga, Yahoo Finance), access method (API), and processing pipeline (scripts 1–9 named) are described. The thesis provides sufficient detail for replication.

### 6.G Statistical Significance Thresholds
**PASS** – α = 0.05 is stated and applied consistently. Results report p-values explicitly. HC3 standard errors and two-way clustering approach are documented in Section 4.5.2.

---

## HARD_FAIL Items — Block Submission Until Fixed

1. **[STRUCT-1D/4B] Appendix sequence violated + Turn-In Checklist absent** — The mandatory SBS appendix order is broken; Appendix 3 (Turn-In Checklist) is absent.
2. **[STRUCT-1C/4A] No rendered References section** — `references.md` has not been integrated into the compilation pipeline; no APA 7 reference list appears in `thesis_final.md`.
3. **[STRUCT-1D-POS] Appendix 4 Survey misplaced** — Survey questionnaire content appears before Back Matter, violating the front-matter/body/references/appendices sequence.
4. **[STRUCT-5A] Executive Summary data inconsistency** — N = 67 / β₁ = −0.2836 in the Executive Summary contradicts N = 53 / β₁ = −0.4874 in Chapter 5; stale caveat note remains.
