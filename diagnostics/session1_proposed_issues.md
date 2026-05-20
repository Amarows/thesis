# Session 1 – Proposed Issues
**Protocol:** `thesis_structure_protocol.md` V2  
**Source report:** `diagnostics/session1_structure_report.md`  
**Generated:** 2026-05-21

---

## [STRUCT-1D] Appendices – SBS mandatory sequence violated; Turn-In Checklist absent

## Finding
The SBS-mandated appendix sequence is violated: Appendix 3 (Turn-In Checklist) is entirely absent and replaced with "Blank Questionnaire / Instrument"; the survey questionnaire content (Appendix 4 per Back Matter) is physically placed in the document before Back Matter and before Appendices 1 and 2.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Back Matter / Appendix sequence  
Line context: 1574 (survey content misplaced), 1839–1846 (Back Matter list), 1849 (Appendix 1), 1904 (Appendix 2)

## Evidence
```
# Appendix 4. Survey Questionnaire (Block 1 – Representative Example)   [line 1574]
…
# Back Matter                                                              [line 1839]
- Appendix 1. Thesis Approval Form
- Appendix 2. AI Disclosure Statement
- Appendix 3. Blank Questionnaire / Instrument
- Appendix 4. Additional Supporting Material
```
Required SBS sequence: Appendix 1 = Approval Form; Appendix 2 = AI Disclosure; Appendix 3 = Turn-In Checklist; Appendix 4 = Survey Questionnaire.

## Proposed fix
1. Remove the `# Appendix 4. Survey Questionnaire` block from its current position (before Back Matter).
2. Add an `## Appendix 3. Turn-In Checklist` section containing the SBS Appendix 11 template content (obtain from Program Manager).
3. Move the survey questionnaire to `## Appendix 4. Survey Questionnaire` after Appendix 3.
4. Correct the Back Matter bullet list to reflect the proper titles and sequence.
5. Update all in-text cross-references to Appendix numbers accordingly.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 4.2

---

## [STRUCT-4A] References – No dedicated reference list rendered in thesis_final.md

## Finding
No standalone `# References` section exists in thesis_final.md. All citations appear inline as hyperlinks but are never collected into a formatted, alphabetically sorted APA 7 reference list. The back matter entry `- References` is a placeholder only.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Back Matter  
Line context: 1839–1842 (placeholder only; no populated section anywhere in document)

## Evidence
```
# Back Matter
- Glossary
- References      ← placeholder bullet only; no rendered reference list section
```

## Proposed fix
Integrate `references.md` into the `9_compile_thesis.py` compilation pipeline so that the reference list is appended to `thesis_final.md` as a `# References` section after Chapter 6 and before the Appendices. The heading must read "References" (not "Bibliography" and not numbered as a chapter).

## Target file for correction
9_compile_thesis.py (integration change); references.md (source content)

## Protocol reference
thesis_structure_protocol.md § 4.1

---

## [STRUCT-5A] Executive Summary – stale figures contradict Chapter 5 results

## Finding
The Executive Summary reports N = 67 respondents, 536 observations, β₁ = −0.2836 (p < 0.0001), and τ = 0.0076 (p = 0.3770). Chapter 5 reports N = 53 respondents, 424 observations, β₁ = −0.4874 (p < 0.0001), and τ = −0.1584 (p = 0.7428). The discrepancy indicates the Executive Summary was not updated when pipeline results were last regenerated. A stale caveat note ("Final results will be updated upon completion of data collection") also remains.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Executive Summary  
Line context: 99–107

## Evidence
```
The analysis is based on a sample of 67 respondents yielding 536 scenario-level observations.
Results support Hypothesis H1: … β₁ = -0.2836, p < 0.0001 …
τ = 0.0076, p = 0.3770 …
*Note: Results reported above are based on the sample available at the time of writing.
Final results will be updated upon completion of data collection.*
```

## Proposed fix
Update the Executive Summary figures to match Chapter 5: N = 53, 424 observations, β₁ = −0.4874, τ = −0.1584 (p = 0.7428). Remove the stale caveat note. If the Executive Summary is a `<!-- PLACEHOLDER -->` block, update the corresponding block in results/thesis_results.md; if manually authored, edit thesis.md directly.

## Target file for correction
thesis.md (Executive Summary section) and/or results/thesis_results.md (if pipeline-generated)

## Protocol reference
thesis_structure_protocol.md § 2.8; § 5 [CRITICAL_CHECKS]

---

## [STRUCT-2.3] Foreword – Acknowledgements sub-section absent

## Finding
The Foreword contains only a professional justification for the thesis topic. The required Acknowledgements sub-section (family, mentor, Program Manager) is entirely absent.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Foreword  
Line context: 72–81

## Evidence
```
## Foreword

This thesis examines whether a structured, quantitative decision-support indicator can moderate
behavioral bias in professional equity portfolio management. The research question emerged from
direct professional experience … [three paragraphs of justification, no Acknowledgements]
```

## Proposed fix
Add an `### Acknowledgements` sub-section at the end of the Foreword section in thesis.md with acknowledgement of family, Dr. Stefano Canossa (mentor), the Program Manager, and any others who contributed.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 2.3

---

## [STRUCT-2.3-COVER] Cover page content duplicated

## Finding
The cover page `<div>` block is duplicated in full: the same content appears twice in the front matter.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Cover Page  
Line context: 3–22 (first instance) and 24–43 (duplicate)

## Evidence
```
<div style="text-align:center; margin-top:180px;">
**REDUCING EMOTIONAL BIASES IN INVESTMENT PORTFOLIO MANAGEMENT**
…
**MENTOR: DR. STEFANO CANOSSA**
</div>

<div style="text-align:center; margin-top:180px;">
**REDUCING EMOTIONAL BIASES IN INVESTMENT PORTFOLIO MANAGEMENT**
…
**MENTOR: DR. STEFANO CANOSSA**
</div>
```

## Proposed fix
Remove the second `<div>` block (lines 24–43). Verify whether the two instances were intended to represent the cover page and title page respectively; if so, differentiate them clearly (title page should carry no page number or running head, per protocol §2.1).

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 2.1

---

## [STRUCT-3.C] Sections 2.4/2.6/2.7/2.8 – Body paragraphs rendered as malformed Level 2 headings

## Finding
Research questions (Section 2.4), key term definitions (Section 2.6), assumption paragraphs (Section 2.7), and limitation paragraphs (Section 2.8) are all formatted with a bare `##` prefix without a section label, causing the entire paragraph to render as a Level 2 heading in the compiled output rather than as numbered body text.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 2, Sections 2.4, 2.6, 2.7, 2.8  
Line context: 300–302 (RQs); 328–387 (definitions, assumptions, limitations)

## Evidence
```
##Do external financial information shocks lead to statistically significant differences …  [line 300]
##Does providing the Shock Score to portfolio managers affect investment decision …          [line 302]
##Emotional bias refers to systematic deviations in judgment and choice …                   [line 328]
##An external financial information shock is a discrete public information event …          [line 330]
##The Shock Score is a quantitative decision-support indicator …                            [line 333]
##Risk – return ratio refers to a risk-adjusted measure of portfolio performance …          [line 345]
##The study assumes that the timing of external information shocks …                        [line 373]
##Findings may not generalize …                                                             [line 385]
```

## Proposed fix
For research questions (lines 300, 302): add labels `**RQ1:**` and `**RQ2:**` as bold run-in text preceding each question, and change `##` to plain body text (no heading markup).  
For definitions (lines 328–345): use `**Term:**` bold run-in labels followed by the definition as body text.  
For assumptions and limitations (lines 373–387): remove the `##` prefix; retain as body paragraphs.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 2 layout); § 4.3 [FORMATTING_RULES]

---

## [STRUCT-3.D] Appendix 1 – Hypothesis notation H1o/H2o instead of H1₀/H2₀

## Finding
The Thesis Approval Form (Appendix 1) uses non-compliant H1o/H1a/H2o/H2a notation instead of the required subscript characters H1₀/H1ₐ/H2₀/H2ₐ, creating a notation inconsistency between the approval form and the thesis body.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Appendix 1. Thesis Proposal Approval Form  
Line context: 1867–1874

## Evidence
```
- H1o: The intensity of external financial information shocks has no statistically significant
  effect on managers' Net Risk Stance responses.
- H1a: The intensity of external financial information shocks has a statistically significant
  effect on managers' Net Risk Stance responses.
```

## Proposed fix
Replace `H1o` → `H1₀`, `H1a` → `H1ₐ`, `H2o` → `H2₀`, `H2a` → `H2ₐ` in the Appendix 1 section of thesis.md.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 2.5 [STRICT_SBS_COMPLIANCE]

---

## [STRUCT-3.F] Section 2.3.3 – Empty body

## Finding
Section 2.3.3 "Measuring Changes in Portfolio Risk – Return Characteristics" has a heading but no body text.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 2, Section 2.3.3  
Line context: 293–295

## Evidence
```
### 2.3.3 Measuring Changes in Portfolio Risk – Return Characteristics


## 2.4 Research Questions
```

## Proposed fix
Either populate Section 2.3.3 with a brief statement of the objective (measuring Sharpe/Sortino ratio changes between ShowSC=1 and ShowSC=0 conditions as specified in Section 2.6.4), or merge its content into Section 2.3.2 and remove the empty heading.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 2 / Objectives layout)

---

## [STRUCT-3.I] Section 4.6 – Numerical inconsistency: portfolio universe 39/36 vs 24

## Finding
The Chapter 4 Conclusion states the portfolio universe comprises 39 candidate stocks with 36 assigned to blocks. Every other reference in Chapter 4 and Table 4.1 establishes 24 stocks across 3 blocks of 8. The 39/36 figures appear to be stale artefacts from a prior design iteration.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 4, Section 4.6  
Line context: 1147

## Evidence
```
The portfolio universe comprises 39 candidate U.S.-listed equities drawn from the S&P 500,
with 36 assigned to three mutually exclusive scenario blocks.
```
Contradicts Section 4.3.1: "The study requires 24 unique stocks" and Table 4.1 which lists exactly 24 stocks.

## Proposed fix
Change "39 candidate U.S.-listed equities" to "24 U.S.-listed equities" and "36 assigned to three mutually exclusive scenario blocks" to "assigned to three mutually exclusive scenario blocks of eight".

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 4 internal consistency); § 6 [CONSISTENCY]

---

## [STRUCT-3.K] Figure 4.3 – Unfilled placeholder

## Finding
Figure 4.3 (Example Scenario Presentation in the Treatment Condition) is a placeholder with the Note: "To be inserted upon survey deployment." The survey has been deployed; this figure was never populated.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 4, Section 4.4.2  
Line context: 977–979

## Evidence
```
*Figure 4.3*
*Example Scenario Presentation in the Treatment Condition (Placeholder)*
*Note.* The figure will display a complete scenario as seen by a respondent in the ShowSC = 1
condition … To be inserted upon survey deployment.
```

## Proposed fix
Replace the placeholder with an actual screenshot or mock-up of a treatment-condition scenario as presented to respondents (showing the stock header, intraday chart, news summary, Shock Score dashboard, and NRS response item). The image file should be saved to `images/` and the figure caption and Note updated accordingly.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 4.3 [TABLES_AND_FIGURES]; § 3 (Chapter 4 / Instrument section)

---

## [STRUCT-3.M] Section 5.6.1 – Duplicate paragraph

## Finding
Section 5.6.1 contains two consecutive near-identical paragraphs. The first uses plain-text beta notation (beta1 = -0.4874); the second uses Unicode (β₁ = −0.4874) and adds the Spec 5 direction-interaction finding. The first paragraph is a residual draft.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 5, Section 5.6.1  
Line context: 1367–1371

## Evidence
```
The results are evaluated against the behavioural finance literature … The statistically significant
negative association (beta1 = -0.4874) … the current analysis does not decompose effects by shock
direction, which is noted as an avenue for future research.

The results are evaluated against the behavioural finance literature … The statistically significant
negative association (β₁ = −0.4874) … The direction-interaction specification (Spec 5) does not
yield a statistically significant asymmetry …
```

## Proposed fix
Delete the first paragraph (plain-text beta notation, ending "…noted as an avenue for future research.") and retain the second paragraph which is more complete and uses correct notation.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 5 / Results Interpretation)

---

## [STRUCT-3.N] Sections 5.5.1/5.5.2 – Five-step hypothesis testing sequence not explicitly structured

## Finding
The SBS five-step hypothesis testing procedure (state hypotheses → select significance level → identify test statistic → formulate decision rule → arrive at decision) is not explicitly laid out as five labelled steps in Sections 5.5.1 or 5.5.2.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 5, Sections 5.5.1 and 5.5.2  
Line context: 1314–1361

## Evidence
Section 5.5.1 begins directly with the regression result narrative without a structured five-step preamble. Steps 1–2 (hypotheses restated, α = 0.05) are implied but not labelled. Step 3 (test statistic = OLS with HC3) is named inline. Steps 4–5 (decision rule and decision) are not formally separated.

## Proposed fix
Restructure Section 5.5.1 and 5.5.2 to explicitly label the five steps. Example:  
**Step 1 – State hypotheses:** H1₀: …; H1ₐ: …  
**Step 2 – Significance level:** α = 0.05  
**Step 3 – Test statistic:** OLS with HC3 heteroscedasticity-robust standard errors, block fixed effects  
**Step 4 – Decision rule:** Reject H1₀ if |t| > critical value at α = 0.05 (two-tailed), equivalently p < 0.05  
**Step 5 – Decision:** [result]  

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 5 / [FIVE_STEP_SEQUENCE])

---

## [STRUCT-3.P] Table 5.x – Unfilled placeholder label

## Finding
Table 5.x "SC_total PCA Diagnostics" retains a placeholder label "5.x" instead of a sequential number.

## Location
File: results/thesis_results.md (pipeline-generated) | thesis_final.md (where observed)  
Section: Chapter 5, Section 5.2.3  
Line context: 1214

## Evidence
```
**Table 5.x: SC_total PCA Diagnostics — First Principal Component**
```

## Proposed fix
Assign the correct sequential table number (e.g., Table 5.2 — noting that Table 5.1 is used in Section 5.2.1). Update the label in results/thesis_results.md and recompile.

## Target file for correction
results/thesis_results.md (pipeline source)

## Protocol reference
thesis_structure_protocol.md § 4.3 [NUMBERING]

---

## [STRUCT-3.R] Section 6.2.1 – Empty body

## Finding
Section 6.2.1 "Summary of Secondary Research" has a heading but no body text.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 6, Section 6.2.1  
Line context: 1456–1457

## Evidence
```
### 6.2.1 Summary of Secondary Research
### 6.2.2 Summary of Primary Research
```
No content between the two headings.

## Proposed fix
Populate Section 6.2.1 with a concise summary of the literature review findings from Chapter 3: the three streams (behavioral bias mechanisms, managerial decision-making under uncertainty, decision-support tools and pre-commitment mechanisms) and the identified gap that this thesis addresses.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 6 / 6.2.1)

---

## [STRUCT-3.S] Sections 6.4.1 and 6.4.2 – Empty sub-section bodies

## Finding
Sections 6.4.1 "Recommendations for Portfolio Managers" and 6.4.2 "Recommendations for Risk Governance" are empty headings. The general recommendations content is present in the parent Section 6.4 but has not been moved into the labelled sub-sections.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 6, Sections 6.4.1 and 6.4.2  
Line context: 1494–1495

## Evidence
```
### 6.4.1 Recommendations for Portfolio Managers
### 6.4.2 Recommendations for Risk Governance
```
Immediately following these headings is Section 6.5 with no intervening content.

## Proposed fix
Distribute the three recommendation paragraphs currently in Section 6.4 ("For individual portfolio managers", "For risk governance", "For institutional deployment") into the appropriate sub-sections: the first two into 6.4.1 and 6.4.2 respectively, and the institutional deployment paragraph as a third sub-section (6.4.3) or appended to 6.4.2.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 6 / 6.4)

---

## [STRUCT-4.D] Appendix 4 – Not referenced by number in main text

## Finding
The survey questionnaire (Appendix 4 per Back Matter) is not referenced by number at any point in the main text (Chapters 1–6). Chapter 4 discusses the survey instrument extensively but never directs the reader to "Appendix 4" or "the survey questionnaire in Appendix 4."

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 4, Sections 4.4.1 or 4.4.9 (appropriate insertion points)  
Line context: 943–1095 (survey description sections)

## Evidence
No instance of "Appendix 4" appears in Chapters 1–6 of thesis_final.md.

## Proposed fix
Add a cross-reference in Section 4.4.9 (Pilot Test) or Section 4.4.1 (Overall Survey Structure), e.g.: "The full Block 1 survey instrument as presented to respondents is reproduced in Appendix 4."

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 4.2 [APPENDIX_LINKAGE]

---

## [STRUCT-4.F] Mixed US/UK English spelling throughout thesis

## Finding
The thesis systematically mixes US English and UK English spellings. UK forms (behaviour/behavioural, realise/realisation, organisation, programme) appear across most chapters alongside US forms (behavior/behavioral, realize, organization, program) in adjacent sentences.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Pervasive across Chapters 1–6  
Line context: Examples at lines 117, 119, 131, 133, 135, 143, 149, 151, 157, 161, 167, 171, 177 and many others

## Evidence
Line 117: "the tendency to realise gains too early" (UK)  
Line 119: "cumulative effect of small behavioural distortions" (UK)  
Line 98 (Executive Summary): "reduces emotional biases" — no spelling marker here; body uses both forms freely.  
Line 152: "engage in herding behaviour around analyst recommendation changes" (UK)  
Line 267: "moderating emotional and behavioral responses" (US)

## Proposed fix
Global find-and-replace in thesis.md to standardise to US English: behaviour→behavior, behavioural→behavioral, realise→realize, realisation→realization, organisation→organization, programme→program (where not a proper noun), recognise→recognize, analyse→analyze, optimise→optimize. A regex sweep is most efficient.

## Target file for correction
thesis.md (global)

## Protocol reference
thesis_structure_protocol.md § 4.3 [ENGLISH]

---

## [STRUCT-4.G] "the author" / "the researcher" voice violations in main chapters

## Finding
Three instances of "to the author's knowledge" appear in Chapters 1, 3, and 6. One instance of "the researcher's professional network" appears in Chapter 4. All are outside Section 6.6 and therefore violate the voice register requirement.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapters 1, 3, 4, 6  
Line context: 185 (Ch.1), 605 (Ch.3), 1051 (Ch.4), 1469 (Ch.6.3.1)

## Evidence
Line 185: "…has not, to the author's knowledge, been attempted in prior research"  
Line 605: "To the author's knowledge, prior research has not proposed a comparable behavioral risk index"  
Line 1051: "direct outreach to portfolio managers within the researcher's professional network"  
Line 1469: "…has not, to the author's knowledge, been implemented in prior work"

## Proposed fix
Replace each instance with an impersonal construction:  
- "to the author's knowledge" → "to the best of current knowledge" or "no prior study has, to the researcher's knowledge" → "No prior study has" (drop self-reference entirely)  
- "the researcher's professional network" → "the study's professional network" or "a professional network of equity portfolio managers"

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 4.3 [VOICE] and § 3 [VOICE_REGISTER_CHECK]

---

## [STRUCT-3.O] Sections 5.5/5.7/5.8 – Hypothesis result wording not SBS-compliant

## Finding
Results use "H1 is supported" / "H2 is not supported" rather than the two SBS-permitted formulations: "Fail to reject the null hypothesis" (for null) or "Support for the alternative hypothesis Hₐ was found" (for alternative).

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 5, Sections 5.5.1, 5.5.2, 5.7, 5.8  
Line context: 1316, 1346, 1413, 1417

## Evidence
Line 1316: "H1 is supported: SC_total is a statistically significant predictor of NRS."  
Line 1346: "H2 is not supported in this sample"  
Line 1413: "H1 – that SC_total is significantly associated with NRS – is **supported** (…). H2 … is **not supported**"

## Proposed fix
Replace "H1 is supported" with "Support for the alternative hypothesis H1ₐ was found" and "H2 is not supported" with "The evidence fails to reject the null hypothesis H2₀" (or "Fail to reject H2₀"). Apply consistently across all four locations.

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 5 / [STRICT_SBS_WORDING])

---

## [STRUCT-2.7] Executive Summary – stale "results pending" caveat note

## Finding
A parenthetical caveat note at the end of the Executive Summary states: "Note: Results reported above are based on the sample available at the time of writing. Final results will be updated upon completion of data collection." The study is complete (N = 53 final sample per Chapter 5) and this note is now both factually incorrect and inappropriate for a final submission document.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Executive Summary  
Line context: 107

## Evidence
```
*Note: Results reported above are based on the sample available at the time of writing.
Final results will be updated upon completion of data collection.*
```

## Proposed fix
Delete the Note paragraph. (This is part of the broader Executive Summary data reconciliation required by finding [STRUCT-5A], but is tracked separately as a standalone clean-up item.)

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 2.8 [FORBIDDEN: Extensive statistical output / inconsistent content]

---

## [STRUCT-3.G] Section 3.1 – Chapter introduction does not describe chapter layout

## Finding
Section 3.1 is titled "Link Between Literature and Research Hypotheses" and discusses the connection between prior literature and the hypotheses. It does not explicitly describe the layout of Chapter 3. The protocol requires 3.1 to describe the chapter layout.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Chapter 3, Section 3.1  
Line context: 412–425

## Evidence
Section 3.1 begins: "The research hypotheses draw on key concepts from behavioral finance (Barberis & Thaler, 2002)…" No statement of chapter structure is present.

## Proposed fix
Add 2–3 sentences at the opening of Section 3.1 describing the chapter layout, e.g.: "Chapter 3 is organised as follows. Section 3.2 reviews behavioural biases in investment decision-making. Section 3.3 examines managerial decision-making under uncertainty. Section 3.4 surveys tools designed to mitigate behavioural bias. Section 3.5 draws implications for portfolio management. Section 3.6 identifies limitations in existing research and the gap addressed by this thesis. Section 3.7 concludes the chapter."

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 3 / 3.1 Chapter Introduction)

---

## [STRUCT-4.E] Formatting compliance not verifiable from Markdown source

## Finding
Typography (Calibri 11pt), line spacing (double), alignment (left), and paragraph indentation compliance cannot be verified from thesis_final.md as a Markdown source file. These must be explicitly confirmed in the compiled Word document before submission.

## Location
File: thesis_final.md (Markdown cannot encode these properties)  
Section: All chapters  
Line context: N/A

## Evidence
N/A – absence of evidence from source.

## Proposed fix
During the Word formatting stage: verify Calibri 11pt font, double-spacing, left-aligned text (not justified), and indented first lines throughout. Confirm that chapters begin on new pages and that sub-chapters do not. Verify heading hierarchy (Level 1 = centred bold, Level 2 = flush-left bold, Level 3 = flush-left bold italic) is consistent with APA 7 and SBS requirements.

## Target file for correction
Compiled Word document (formatting step)

## Protocol reference
thesis_structure_protocol.md § 4.3 [FORMATTING_RULES]

---

## [STRUCT-2.2] Authentication page heading level may not force new page

## Finding
The Authentication page is rendered as a Level 2 heading (`## Authentication of Work`) under the cover page heading. Depending on the Word conversion settings, this may not force a new page, causing the declaration text to run on from the cover content.

## Location
File: thesis.md (target for fix) | thesis_final.md (where observed)  
Section: Authentication of Work  
Line context: 56–68

## Evidence
```
# Reducing Emotional Biases in Investment Portfolio Management
## Authentication of Work
```

## Proposed fix
Ensure that a page break is inserted before the Authentication of Work section in the compiled Word document. This may require a custom heading style or an explicit `\newpage` / Word section break in the compilation script.

## Target file for correction
9_compile_thesis.py (page-break handling) or thesis.md (if explicit break is supported in compilation)

## Protocol reference
thesis_structure_protocol.md § 2.2

---

## [STRUCT-2.4] TOC, Lists of Tables/Figures, and Abbreviations are unpopulated placeholders

## Finding
The Table of Contents, List of Tables, List of Figures, and List of Abbreviations are present in the front matter only as bullet-point placeholders and contain no actual content.

## Location
File: thesis_final.md (where observed) | Compiled Word document (where fix must be applied)  
Section: Front matter  
Line context: 83–87

## Evidence
```
- Table of Contents
- List of Tables
- List of Figures
- List of Abbreviations and Acronyms
- Executive Summary
```

## Proposed fix
During the Word formatting / compilation stage: generate the TOC from Heading styles (Levels 1–3 only; Level 4–5 must be excluded). Generate List of Tables and List of Figures from caption styles. Populate the List of Abbreviations alphabetically. Verify all page numbers are accurate after final layout.

## Target file for correction
Compiled Word document (Word auto-generation step)

## Protocol reference
thesis_structure_protocol.md § 2.4, 2.5, 2.6, 2.7

---

## [STRUCT-3.J-LIKERT] NRS scale anchor deviation from SBS Appendix 6

## Finding
The seven-point NRS scale uses risk-stance anchors ("Strongly reduce exposure" to "Strongly increase exposure") rather than the SBS Appendix 6 standard anchors ("Strongly disagree" to "Strongly agree"). The justification is provided in Section 4.4.5 but no explicit mentor pre-approval cross-reference is cited.

## Location
File: thesis.md (where observed)  
Section: Chapter 4, Section 4.4.5  
Line context: 1023–1030

## Evidence
"For each scenario, the manager selects a single response on the seven-point Net Risk Stance scale … 1. Strongly reduce exposure … 7. Strongly increase exposure"

## Proposed fix
Add a cross-reference in Section 4.4.5 stating that this purpose-built scale has been approved by the mentor as an appropriate adaptation of the SBS seven-point format for the specific decision-task context (citing Section 4.4.5 justification and referencing mentor approval if available).

## Target file for correction
thesis.md

## Protocol reference
thesis_structure_protocol.md § 3 (Chapter 4 / [LIKERT])

---

## [STRUCT] Diagnostic Summary

**Title:** [STRUCT] Diagnostic summary — Session 1 structure audit

### Counts by Priority

| Priority | Count | Basis |
|----------|-------|-------|
| P1 (HARD_FAIL) | 4 | Appendix sequence + Turn-In Checklist absent; References section absent; Executive Summary data contradiction |
| P2 (FAIL) | 13 | Foreword acknowledgements; Executive Summary stale note; Research question formatting; 2.3.3 empty; 2.3.3 portfolio count; Appendix 1 notation; Fig 4.3 placeholder; Ch.5 duplicate paragraph; 5-step procedure absent; Table 5.x label; 6.2.1 empty; 6.4.1/6.4.2 empty; Appendix 4 not cross-referenced; UK/US spelling; author/researcher voice; hypothesis result wording |
| P3 (WARNING) | 7 | Cover duplication; Authentication page break; TOC/Lists unpopulated; 3.1 layout description; Descriptive stats placement; NRS scale anchor; Formatting not verifiable |

### All Per-Finding Issue Titles

| # | Issue title |
|---|-------------|
| 1 | [STRUCT-1D] Appendices – SBS mandatory sequence violated; Turn-In Checklist absent |
| 2 | [STRUCT-4A] References – No dedicated reference list rendered in thesis_final.md |
| 3 | [STRUCT-5A] Executive Summary – stale figures contradict Chapter 5 results |
| 4 | [STRUCT-2.3] Foreword – Acknowledgements sub-section absent |
| 5 | [STRUCT-2.3-COVER] Cover page content duplicated |
| 6 | [STRUCT-3.C] Sections 2.4/2.6/2.7/2.8 – Body paragraphs rendered as malformed Level 2 headings |
| 7 | [STRUCT-3.D] Appendix 1 – Hypothesis notation H1o/H2o instead of H1₀/H2₀ |
| 8 | [STRUCT-3.F] Section 2.3.3 – Empty body |
| 9 | [STRUCT-3.I] Section 4.6 – Numerical inconsistency: portfolio universe 39/36 vs 24 |
| 10 | [STRUCT-3.K] Figure 4.3 – Unfilled placeholder |
| 11 | [STRUCT-3.M] Section 5.6.1 – Duplicate paragraph |
| 12 | [STRUCT-3.N] Sections 5.5.1/5.5.2 – Five-step hypothesis testing sequence not explicitly structured |
| 13 | [STRUCT-3.P] Table 5.x – Unfilled placeholder label |
| 14 | [STRUCT-3.R] Section 6.2.1 – Empty body |
| 15 | [STRUCT-3.S] Sections 6.4.1 and 6.4.2 – Empty sub-section bodies |
| 16 | [STRUCT-4.D] Appendix 4 – Not referenced by number in main text |
| 17 | [STRUCT-4.F] Mixed US/UK English spelling throughout thesis |
| 18 | [STRUCT-4.G] "the author" / "the researcher" voice violations in main chapters |
| 19 | [STRUCT-3.O] Sections 5.5/5.7/5.8 – Hypothesis result wording not SBS-compliant |
| 20 | [STRUCT-2.7] Executive Summary – stale "results pending" caveat note |
| 21 | [STRUCT-3.G] Section 3.1 – Chapter introduction does not describe chapter layout |
| 22 | [STRUCT-4.E] Formatting compliance not verifiable from Markdown source |
| 23 | [STRUCT-2.2] Authentication page heading level may not force new page |
| 24 | [STRUCT-2.4] TOC, Lists of Tables/Figures, and Abbreviations are unpopulated placeholders |
| 25 | [STRUCT-3.J-LIKERT] NRS scale anchor deviation from SBS Appendix 6 |
