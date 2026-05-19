# THESIS_VERIFICATION_PROTOCOL_V2
# ROLE: Structural Compliance Auditor
# TARGET: SBS Swiss Business School EMBA/Master's Thesis (AY 2025–26)
# VERSION HISTORY:
#   V1 – Initial draft
#   V2 – 2026-05-19: Gap analysis against Handbook v1.8 applied. Corrections:
#        Foreword reclassified as REQUIRED; Chapter 1 SBS subsection scope corrected;
#        Ch.2 sections 2.6 and 2.9 added; Pilot test added to Ch.4; Ch.5 Interim
#        Conclusion added; Mandatory appendix order corrected to SBS sequence;
#        Executive Summary length corrected to 1 page; Ch.6 subsections 6.5–6.7 added;
#        Normality tests made explicit in Ch.5; Pagination scheme added; first-person
#        voice requirement added for Ch.6; "Dr. Wolfs" name check added.

## 0. MISSION
Verify structural completeness, mandatory components, and APA/SBS alignment. This is a
procedural audit; do not evaluate academic quality or statistical depth unless specified.

[RESULT_CODES]
- PASS: All [REQUIRED] and [MUST] conditions met.
- WARNING: Minor formatting or [RECOMMENDED] items missing; structural integrity intact.
- FAIL: One or more [REQUIRED] elements missing or [FORBIDDEN] elements present.
- HARD_FAIL: Violation of [CRITICAL_CHECKS] or [HARD_FAILURE_CRITERIA]. Escalation required.

## 1. MANDATORY_ARCHITECTURE
The thesis MUST follow this exact sequence:
1. Front Matter (Cover, Title Page, Authentication, Foreword, TOC, Lists, Executive Summary)
2. Main Body (Chapters 1–6)
3. References (NOT numbered as a chapter)
4. Appendices (mandatory sequence: Approval Form, AI Disclosure, Turn-In Checklist, Survey)

# NOTE (V2): The handbook (Appendix 3) prescribes this sequence precisely. Any deviation
# from the front matter order, or from the mandatory appendix sequence in section 3.9, is
# a structural violation reportable as FAIL.

---

## 2. FRONT_MATTER_REQUIREMENTS

### 2.1 COVER_PAGE [REQUIRED]
- [MUST] Match SBS standard template (Appendix 1 of Handbook).
- [REQUIRED_ELEMENTS]:
  - "SBS Swiss Business School" (not "Swiss Business School")
  - Thesis title (must match the approved thesis approval form exactly)
  - Degree program
  - Student full name and student number
  - Mentor full name
  - Submission year
- [FORBIDDEN]: Page number on cover page.
- [FORBIDDEN]: Running head on cover page.

# NOTE (V2): The title page is identical to the cover page with one exception: it carries
# neither a page number nor a running head. Both cover and title page must use the SBS
# standard template. Do not auto-populate the example title shown in the template.

### 2.2 AUTHENTICATION_PAGE [REQUIRED]
- [MUST]: Declaration of originality signed by the student.
- [MUST]: Mentor authentication and signature placeholder.
- [REQUIRED]: Exact wording from SBS standard template (Appendix 2 of Handbook).
- [CONDITION]: Page is signed only after the Program Manager has approved the plagiarism scan.

# NOTE (V2): Authentication is signed after plagiarism clearance, not before submission
# to the Program Manager. Confirm sign-off sequence with the Program Manager.

### 2.3 FOREWORD [REQUIRED]
- [MUST]: Include a justification for the thesis (why this topic, why now).
- [MUST]: Include an Acknowledgements sub-section (family, mentor, Program Manager, etc.).
- [LIMIT]: No academic argumentation, no literature citations, no statistical claims.
- [SPELLING]: "Foreword" (with an "e") — NOT "Forward".

# NOTE (V2): V1 classified Foreword as [OPTIONAL]. This is incorrect. The handbook
# standard layout (Section 3.2 and Appendix 3) lists Foreword as a required front matter
# element. The Acknowledgements section is a sub-component of the Foreword, not a
# separate page.

### 2.4 TABLE_OF_CONTENTS [REQUIRED]
- [CHECK]: All Level 1, 2, and 3 headings included with correct page numbers.
- [FORBIDDEN]: Level 4 and Level 5 headers listed in the TOC.
- [CHECK]: Pagination accuracy — every listed page number must match the printed page.
- [CHECK]: Consistent numbering and hierarchy throughout.
- [CHECK]: Appendices listed by number and title.

# NOTE (V2): The handbook explicitly prohibits Level 4/5 headers from the TOC. Most
# Word-generated TOCs include all levels by default; this must be manually adjusted.

### 2.5 LIST_OF_TABLES [CONDITIONAL — REQUIRED if tables exist]
- [CHECK]: Every table in the thesis appears in this list.
- [CHECK]: Table numbering is sequential and consistent with in-text references.
- [CHECK]: Table titles in the list match the captions above the tables exactly.

### 2.6 LIST_OF_FIGURES [CONDITIONAL — REQUIRED if figures exist]
- [CHECK]: Every figure in the thesis appears in this list.
- [CHECK]: Figure numbering is sequential and consistent with in-text references.
- [CHECK]: Figure titles in the list match the captions above the figures exactly.

### 2.7 LIST_OF_ABBREVIATIONS [RECOMMENDED]
- [CHECK]: Acronyms defined on first use in the text AND listed here.
- [CHECK]: Alphabetical order.
- [NOTE]: Required if acronyms are present that may be unfamiliar to a general academic reader.

### 2.8 EXECUTIVE_SUMMARY [REQUIRED]
- [LENGTH]: Exactly one (1) page. Do not exceed one page.
- [REQUIRED_CONTENT]: Research problem, objectives, methodology, main findings,
  conclusions, and recommendations — all present.
- [FORBIDDEN]: In-text citations or reference list entries.
- [FORBIDDEN]: Detailed literature review.
- [FORBIDDEN]: Extensive statistical output.

# NOTE (V2): V1 specified 1–3 pages. The handbook (Section 3.2.2) defines the Executive
# Summary as a one-page summary. A two- or three-page executive summary is non-compliant.

### 2.9 PAGINATION_SCHEME [REQUIRED]
- [FRONT_MATTER]: Roman numerals (lowercase: i, ii, iii…). Cover page is counted but
  not numbered. Numbering begins visibly from the Title Page or Authentication Page.
- [MAIN_BODY]: Arabic numerals (1, 2, 3…) beginning at Chapter 1, page 1.
- [CHECK]: No mixing of pagination schemes within a section.
- [CHECK]: Page numbers positioned per Handbook formatting guidance (bottom centre or
  top right, consistent throughout).

# NOTE (V2): Pagination scheme was not a named compliance check in V1. The handbook
# references it under formatting guidance. Front matter/main body pagination boundary
# is a common formatting error caught during the Program Manager's format review.

---

## 3. MAIN_BODY_REQUIREMENTS

### CHAPTER_1: INTRODUCTION [REQUIRED — 2 subsections per SBS standard layout]

- **1.1 Background of the Problem**: Business problem, practical relevance, industry
  context, geographical scope, historical development. Cite as needed.
- **1.2 Background of the Study**: Author's personal academic interest in the question;
  how the investigator became engaged with the topic.

# NOTE (V2): The SBS standard layout (Section 3.3.1 and Appendix 3) defines Chapter 1
# with only two subsections: 1.1 and 1.2. V1 included 1.3 Purpose, 1.4 Significance,
# 1.5 Scope and Delimitations, and 1.6 Structure. These are valid in many thesis
# frameworks but are NOT prescribed by SBS. Including them is permissible with mentor
# agreement, but the protocol should not flag their absence as a FAIL. Conversely, their
# presence must not duplicate content that belongs in Chapter 2 (objectives, scope,
# limitations). If included, verify there is no content duplication with Chapter 2.

### CHAPTER_2: OBJECTIVES_OF_THE_STUDY [REQUIRED]

- **2.1 Chapter Introduction**: Describe the layout of the chapter.
- **2.2 Problem Statement**: Restate the research gap; define the operational problem.
- **2.3 Objectives of the Study**: State the intended goals; must be measurable and
  aligned with hypotheses and methodology.
- **2.4 Research Question**: One main research question. SBS preferred format:
  "Does [IV] have a statistically significant [positive/negative] effect on [DV]?"
  Identify IV, DV, industry, and geography explicitly.
- **2.5 Hypothesis Statements [STRICT_SBS_COMPLIANCE]**:
  - [FORMAT]: Use Hₒ and Hₐ subscript notation. SBS does NOT use H0/H1 notation.
  - [ORDER]: Null hypothesis (Hₒ) MUST be listed before the alternative (Hₐ).
  - [WORDING_NULL]: "{IV} has no statistically significant effect on {DV}."
  - [WORDING_ALT]: "{IV} has a statistically significant effect on {DV}."
  - Multiple hypotheses numbered: H1ₒ/H1ₐ, H2ₒ/H2ₐ, etc.
- **2.6 Additional Research Questions** [CONDITIONAL]: Sub-questions addressing
  moderating or mediating variables, if applicable.
- **2.8 Limitations** [CONDITIONAL]: Problems affecting generalizability, data
  collection, or hypothesis testing.
- **2.9 Chapter Conclusion** [REQUIRED]: Summarize and transition to Chapter 3.

# NOTE (V2): V1 omitted sections 2.6 (Additional Research Questions) and 2.9 (Chapter
# Conclusion). Both appear in the SBS standard layout (Section 3.4.1 and Appendix 3).
# Chapter Conclusion is required in every chapter — its absence in any chapter is a FAIL.
# Note also that the handbook numbers jump from 2.8 Limitations to 2.9 Conclusion,
# with no 2.7; this reflects the handbook's own numbering as published.

[DEPENDENCY_RULE — Ch.2 cross-chapter linkage]
- [CH2_TO_CH4]: Every hypothesis in 2.5 MUST be operationalized in Chapter 4
  (variable definitions, instrument design).
- [CH2_TO_CH5]: Every IV and DV introduced in Chapter 2 MUST appear in Chapter 5
  statistical testing with results reported.
- [CH2_TO_CH6]: Every research question in 2.4 (and 2.6) MUST be answered in Chapter 6.

### CHAPTER_3: LITERATURE_REVIEW [REQUIRED]

Standard layout:
- **3.1 Chapter Introduction**: Layout of the chapter.
- **3.n Thematic subchapters**: As many as needed; structured thematically, not
  chronologically. Compare and contrast peer-reviewed sources.
- **3.X Summary of Key Points** (final subsection): Summarize and transition to Chapter 4.

Content requirements:
- [REQUIRED]: Critical synthesis establishing theoretical foundation for each hypothesis.
- [REQUIRED]: APA 7 citations throughout.
- [FORBIDDEN]: Pure summaries or descriptive lists without analytical comment.
- [FORBIDDEN]: Chronological "shopping list" structure.
- [WARNING]: Non-academic sources (consultant reports, blogs) should be avoided or
  explicitly justified.
- [CHECK]: Every hypothesis must have direct theoretical support identifiable in the
  literature review.

### CHAPTER_4: COLLECTION_OF_PRIMARY_DATA [REQUIRED]

Standard layout (all subsections below are [REQUIRED] unless marked [CONDITIONAL]):
- **4.1 Chapter Introduction**
- **4.2 Research Design**:
  - 4.2.1 Research Paradigm
  - 4.2.2 Conceptual Framework [CONDITIONAL at Master's level; include if present]
  - 4.2.3 Design of the Research Instrument
  - 4.2.4 Pilot Test [REQUIRED]
  - 4.2.5 Population and Sample
  - 4.2.6 Sampling Technique
- **4.3 Research Execution**:
  - 4.3.1 Key Dates (survey opening and closing dates)
  - 4.3.2 Return Rates (number sent vs. number returned vs. number valid)
- **4.4 Descriptive Statistics**:
  - 4.4.1 Respondent Descriptive Statistics
  - 4.4.2 Descriptive Analysis of Data
- **4.5 Chapter Conclusion**

# NOTE (V2): V1 omitted the Pilot Test (4.2.4) as a named required subsection. The
# handbook (Section 3.6.1) lists it explicitly. For this thesis, the pilot study covers
# Block 1 only; the protocol check should verify that pilot test results (Cronbach's
# alpha, item review, sample size) are documented in 4.2.4 and that any limitations
# arising from the pilot are carried forward to Chapter 1 or Chapter 5 as appropriate.

[STATISTICAL_VALIDATION checks for Chapter 4]
- [SAMPLE]: Sample size justification required (e.g., G*Power, industry standard,
  or analytical power argument).
- [ASSUMPTIONS]: Statistical assumptions (normality, homoscedasticity, independence)
  must be disclosed.
- [CONSISTENCY]: Variable operationalization and metric definitions must be identical
  across all chapters.
- [INSTRUMENT]: Survey instrument must be reproduced in full in the Appendices.
- [LIKERT]: If Likert scale used, confirm 7-point scale per SBS guidance (Appendix 6
  of Handbook: strongly disagree to strongly agree).

### CHAPTER_5: ANALYSIS_AND_CONCLUSIONS [REQUIRED]

Standard layout (all subsections [REQUIRED]):
- **5.1 Chapter Introduction**
- **5.2 Tests for Normality and Reliability** [REQUIRED]
- **5.3 Hypothesis Testing** [REQUIRED]
- **5.4 Interim Conclusion** [REQUIRED]
- **5.5 Chapter Conclusion** [REQUIRED]

# NOTE (V2): V1 omitted section 5.4 Interim Conclusion. The handbook standard layout
# (Section 3.7.1 and Appendix 3) lists it explicitly as a separate subsection distinct
# from 5.5 Chapter Conclusion. The Interim Conclusion summarizes the hypothesis testing
# results before the full chapter conclusion. Its absence is a FAIL.

Tests for Normality and Reliability (5.2) requirements:
- [REQUIRED]: Cronbach's alpha reliability test. Minimum sample size for Cronbach's
  alpha is 30. If pilot sample is below 30, flag as a limitation.
- [REQUIRED]: If data are non-normal, conduct and report a Shapiro-Wilk test.
- [CONDITION]: If Cronbach's alpha ≤ 0.5, the relevant survey questions must be
  questioned and the problem reported as a limitation in Chapter 1 (or Chapter 5).

Hypothesis Testing (5.3) requirements:
- [STRICT_SBS_WORDING]:
  - PERMITTED: "Fail to reject the null hypothesis."
  - PERMITTED: "Support for the alternative hypothesis Hₐ was found."
  - FORBIDDEN: "Accept the null hypothesis."
  - FORBIDDEN: "Reject the null hypothesis." (standalone, without "fail to")
  - FORBIDDEN: "Prove the hypothesis."
- [FIVE_STEP_SEQUENCE]: State hypotheses → select significance level → identify test
  statistic → formulate decision rule → arrive at decision.
- [TEST_SELECTION]: z-test if n ≥ 30 and population SD known; t-test otherwise.

Findings interpretation:
- [CHECK]: All findings linked back to literature in Chapter 3.
- [CHECK]: All findings linked back to objectives and research questions in Chapter 2.

### CHAPTER_6: CONCLUSIONS_AND_RECOMMENDATIONS [REQUIRED]

Standard layout (all subsections [REQUIRED]):
- **6.1 Chapter Introduction**
- **6.2 Summary of Findings**:
  - 6.2.1 Summary of Secondary Research
  - 6.2.2 Summary of Primary Research
- **6.3 Overall Conclusion**: Main conclusion answering the research question.
- **6.4 Recommendations**: Real-world application of conclusions.
- **6.5 Areas for Future Research** [REQUIRED]: Portions of the research that warrant
  further investigation; follow-on questions surfaced by the study.
- **6.6 Lessons Learned** [REQUIRED, FIRST-PERSON]: What the author personally learned
  from the writing process AND from the subject itself. MUST be written in first person.
- **6.7 Ethical Considerations** [REQUIRED]: Business and moral issues raised by the
  study's findings. NOT the ethics of the survey process itself.
- **6.8 SDG Implications** [REQUIRED]: Explicit link to relevant UN Sustainable
  Development Goals and their application to the study's findings.

# NOTE (V2): V1 omitted sections 6.5, 6.6, and 6.7. All three are required per the
# handbook standard layout (Section 3.8.1 and Appendix 3). Section 6.6 Lessons Learned
# is the only section in the entire thesis where first-person writing is not only
# permitted but mandatory. The handbook (Section 2.3) states: "In Chapter 6, however,
# you must use the first-person approach when discussing the lessons you have personally
# learned." Failure to use first person in 6.6 is a style non-compliance. Conversely,
# using first person in any other chapter is also a violation. Verify both directions.
# Section 6.7 covers the ethical implications of the findings (e.g., implications for
# investor behaviour, market integrity, regulatory considerations) — it is NOT a
# discussion of survey consent procedures or IRB considerations.

[VOICE_REGISTER_CHECK — Chapter 6 specific]
- [6.6]: First-person required ("I learned…", "This process taught me…").
- [6.1–6.5, 6.7–6.8]: Third-person required, consistent with all other chapters.
- [FORBIDDEN anywhere in thesis except 6.6]: "I", "we", "the author", "the researcher".

---

## 4. TECHNICAL_REQUIREMENTS

### 4.1 REFERENCES [REQUIRED]
- [FORMAT]: APA 7, hanging indent, alphabetical order by first author surname.
- [NOT A CHAPTER]: The reference list is not numbered as a chapter. It appears after
  Chapter 6 with the heading "References" only.
- [VALIDATION]: 1:1 match required between every in-text citation and the reference list.
  No orphan citations (in text but not in list); no ghost references (in list but not cited).
- [REQUIRED]: DOI or URL where available.
- [LABEL]: "References" or "Reference list" — NOT "Bibliography".

# NOTE (V2): A frequent error is numbering the reference list as "Chapter 7" or
# "7. References". The handbook Turn-In Checklist (Appendix 11) explicitly flags this.

### 4.2 APPENDICES — MANDATORY SBS SEQUENCE [REQUIRED]
The following appendices MUST appear in this order immediately after the References:

- **Appendix 1**: Signed thesis approval form.
- **Appendix 2**: AI Disclosure Statement (SBS template, Appendix 8 of Handbook).
- **Appendix 3**: Turn-In Checklist (SBS template, Appendix 11 of Handbook).
- **Appendix 4**: Blank copy of the survey questionnaire (research instrument).
- **Additional appendices** (numbered from 5 onward): Statistical outputs, regression
  tables, robustness checks, model specifications, portfolio logic, risk formulas,
  mathematical derivations, variable dictionaries, etc.

# NOTE (V2): V1 defined Appendix A as Research Instruments, Appendix B as Statistical
# Outputs, and Appendix C as AI Disclosure. This is incorrect. The handbook (Section 3.9)
# prescribes the first four appendix slots explicitly by content and in a fixed order.
# The AI Disclosure is Appendix 2 (not Appendix C), and it must use the SBS-provided
# template (obtainable from the Program Manager). Research instruments and statistical
# outputs follow after the mandatory four, numbered from Appendix 5 onward.

[APPENDIX_LINKAGE — applies to all appendices]
- [CHECK]: Every appendix must be referenced by name and number at least once in the
  main text (Chapters 1–6) before it appears.
- [FORBIDDEN]: Unreferenced appendices.

[AI_USAGE_COMPLIANCE]
- [DISCLOSURE]: All AI-assisted activities (text generation, data analysis support,
  language editing, idea structuring) must be itemised in the AI Disclosure Statement.
- [VERIFICATION]: The statement must affirm that AI-generated content was reviewed
  and verified by the author.
- [INTEGRITY]: No uncited or fabricated references. Hallucinated citations constitute
  academic dishonesty.

### 4.3 FORMATTING_RULES

**Typography and layout:**
- [FONT]: MS Word default Calibri, 11 pt.
- [SPACING]: Double-spaced throughout the main body.
- [ALIGNMENT]: Text align-left (not justified, not centred).
- [PARAGRAPHS]: Indented first line (not flush-left with space between paragraphs).
- [NEW_PAGE]: Only chapters begin on a new page. Subchapters do NOT start on a new page.
- [SUBCHAPTERS]: Must be numbered (e.g., 4.2.1), not merely titled without a number.

**APA heading hierarchy:**
- Level 1: Centred, Bold, Title Case (chapter titles).
- Level 2: Flush Left, Bold, Title Case.
- Level 3: Flush Left, Bold Italic, Title Case.
- Level 4: Indented, Bold, Title Case, ending with a period. Text follows on same line.
- Level 5: Indented, Bold Italic, Title Case, ending with a period. Text follows on same line.
- [FORBIDDEN]: Skipping heading levels (e.g., jumping from Level 2 to Level 4).
- [FORBIDDEN]: Using bold text at paragraph start as a substitute for Level 3/4 headers.

**Tables and figures:**
- [CAPTION_POSITION]: Caption (Table N / Figure N + descriptive title) appears ABOVE
  the table or figure.
- [SOURCE_ATTRIBUTION]: Source line appears BELOW the table or figure.
  Format: "From [full reference]" or "Based on [full reference]".
- [IN_TEXT_REFERENCE]: Every table and figure must be referenced in the running text
  BEFORE it appears on the page.
- [NUMBERING]: Sequential Arabic numerals throughout, or by chapter (e.g., Table 4.1).
- [LIST_CONSISTENCY]: Caption in Lists of Tables/Figures must match in-text caption exactly.

**Text-content checks:**
- [SBS_NAME]: "SBS Swiss Business School" — NOT "Swiss Business School".
- [MENTOR_NAME]: "Dr. Wolfs" — NOT "Dr. Wolf".

# NOTE (V2): Both name checks are listed in the handbook Turn-In Checklist (Appendix 11)
# as explicit student-initialled items. "Dr. Wolf" (without the s) is the most common
# error and will be flagged during the Program Manager's format review.

**Language and style:**
- [ENGLISH]: US English spelling only. UK English is non-compliant.
- [VOICE]: Third person throughout, except Chapter 6.6 (first person required).
- [TENSE]: Past tense for secondary research articles and completed primary research.
- [CONTRACTIONS]: Forbidden (e.g., "don't" → "do not").
- [ABBREVIATIONS]: Forbidden in running prose (except established acronyms defined
  on first use).
- [DICTION]: "such as" not "like"; "received/obtained" not "got". No colloquial language.
- [PRONOUNS]: Avoid second-person ("as you know", "as we can see").
- [GENDER_NEUTRAL]: Use "they/their" for individuals; avoid gendered occupational titles.
- [TONE]: Serious and formal. No irony, humour, or conversational register.

[CROSS_REFERENCE_CHECK]
- [SEQUENCE]: All tables and figures carry sequential numbering.
- [PLACEMENT]: All tables and figures introduced in text before their appearance.
- [LIST_VALIDATION]: Every item in Lists of Tables/Figures is referenced in the main body.

---

## 5. INTEGRITY_AND_FAILURE_CONDITIONS

### [CRITICAL_CHECKS]
1. **Originality**: Plagiarism score below the SBS threshold (confirmed by Program Manager).
2. **Primary Research**: MUST include an original empirical quantitative component
   (sample survey).
3. **Hypothesis Testing**: MUST be explicitly tested with appropriate statistical tests,
   using SBS-compliant wording.
4. **Word Count**: Main body must reach 20,000 words (Turn-In Checklist requirement).

### [HARD_FAILURE_CRITERIA]
The following conditions each independently trigger HARD_FAIL:
- Missing or incorrectly formatted hypothesis statements (wrong notation, wrong order,
  forbidden wording).
- Missing primary quantitative research component.
- Missing Chapter 4 or Chapter 5.
- No SDG implications paragraph in Chapter 6.8.
- No Mentor Authentication page.
- Misalignment between Research Questions (Ch.2) and Hypothesis Statements (Ch.2 and Ch.5).
- Missing Pilot Test documentation (Ch.4).
- Missing Interim Conclusion in Chapter 5 (5.4).
- Missing Lessons Learned section (Ch.6.6).
- Missing AI Disclosure Statement (Appendix 2).
- Reference list numbered as a chapter.

---

## 6. QUANTITATIVE_FINANCE_ENHANCEMENTS
For theses with quantitative finance methodology, verify the following in addition to
the above:
- Variable dictionary: every IV, DV, moderator, and control variable defined with
  units, source, and transformation applied.
- Model specifications: regression equations written out in full (not described verbally only).
- Robustness checks: alternative specifications, sub-sample tests, or sensitivity analyses
  documented.
- Factor construction: PCA, index construction, or composite score methods documented
  with sufficient detail for replication.
- Data preprocessing: outlier treatment, winsorization, missing data handling described.
- Reproducibility: data sources, access method, and processing pipeline described such
  that an independent researcher could replicate the dataset.
- Statistical significance thresholds: p-value cutoffs stated explicitly (e.g., p < 0.05,
  p < 0.01) and applied consistently throughout Chapter 5.
