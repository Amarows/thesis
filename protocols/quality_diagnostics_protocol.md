# Quality Diagnostics Protocol — EMBA Thesis
**Version:** 2.0  
**Replaces:** `protocols/1_quality_review.md`, `protocols/2_master_revision.md`  
**Last updated:** 2026-05-16 (incorporating Stefano Canossa feedback, April 2026)

---

## HOW TO USE THIS DOCUMENT

This protocol governs two sequential activities:

1. **Diagnostic pass** — run tests in Parts 3–4, flag violations, produce a diagnostic report. Do not correct during this pass.
2. **Revision pass** — use rules in Part 2 to correct flagged items only. Do not run diagnostics during this pass.

Always specify scope before running: state which chapter or section is under review. Tests are designed to be re-run after each revision cycle.

---

## PART 1 — HARD RULES

These constraints must never be violated. They apply during both diagnostic and revision passes, without exception.

**HR-1: Reference preservation.** No existing citation, DOI, URL, or in-text reference may be removed, replaced, or consolidated unless explicitly instructed as part of a named revision task.

**HR-2: Meaning preservation.** The semantic content of every paragraph must remain unchanged after revision. No new claims added, no existing claims removed, no altered positioning.

**HR-3: No scope expansion.** Revisions must not introduce new literature, new constructs, or new theoretical claims beyond what exists in the current draft.

**HR-4: Academic register.** Formal academic tone must be maintained throughout. No colloquial, didactic, or introductory-level language.

**HR-5: Minimal intervention.** Do not paraphrase extensively. Do not rewrite sections wholesale. Target the smallest string that resolves the violation.

**HR-6: Hyperlink requirement.** Every citation must include a hyperlink URL in markdown format `[Author, Year](URL)`. Citations without hyperlinks are incomplete regardless of APA compliance.

**HR-7: Shock Score novelty.** The Shock Score and SC_total are original constructs introduced in this thesis. They must never be attributed to prior literature as if borrowed. Any citation alongside them covers a component or method, not the composite construct itself.

---

## PART 2 — REVISION RULES

Apply these rules when correcting items flagged in the diagnostic pass.

### Permitted actions
- Reorder sentences within a paragraph to improve logical flow
- Split overly long sentences into two shorter sentences
- Remove duplicated phrases or clauses
- Clean syntax, spacing, punctuation, and formatting inconsistencies
- Replace verbose constructions with academically equivalent compact phrasing
- Reduce rhetorical padding ("it is important to note that", "it can be observed that")
- Add minimal bridging sentences that explicitly link literature to hypotheses or clarify causal pathways already implied in the text
- Add missing citations where a claim is unsupported

### Prohibited actions
- Rewriting paragraphs in substantially new wording
- Changing sentence structure where no clarity benefit exists
- Changing tone from academic to explanatory or didactic
- Introducing new interpretations, claims, or emphases not present in the current draft
- Removing or consolidating references
- Expanding scope beyond current draft content

### Reader context
Assume the reader is a senior finance professional, reading under time pressure, highly literate but impatient with redundancy. Optimize for: clarity on first read, compact expression, logical flow.

### Output format
- Show exact before/after for each corrected sentence
- Never replace an entire section unless explicitly instructed
- Separate recommendations from actual text edits
- Ask before making any change that is uncertain in scope

---

## PART 3 — DIAGNOSTIC TESTS

### SECTION A: Universal tests (all chapters)

Run on every paragraph in the chapter under review.

**A-1: Unsupported claim detection.**  
Scan each sentence for substantive claims — any statement asserting a relationship, mechanism, empirical regularity, definition, or consequence. Flag sentences where such a claim appears without an accompanying citation. Exception: claims that are original contributions of this thesis, which must instead be framed as such ("this thesis proposes", "the present study finds").

**A-2: Epistemic framing test.**  
In chapters preceding empirical analysis (Ch.1–Ch.4), scan for declarative causal statements (e.g., "X affects Y", "X leads to Y"). Flag any sentence that presents a relationship under investigation as an established fact rather than using investigative framing (e.g., "this study examines whether", "the hypothesis that", "may affect").

**A-3: Assumption-vs-literature test.**  
Scan for phrases such as "this thesis assumes", "this study assumes", "it is assumed that". For each, determine whether the assumed relationship is already established in the literature. If so, flag — the sentence should cite the literature rather than frame the relationship as an assumption.

**A-4: Original-vs-established boundary test.**  
For each construct, method, or framework mentioned, determine whether it is the author's original contribution or drawn from existing literature. Flag any instance where this distinction is ambiguous — the reader cannot tell whether the construct is original or cited. Special case: Shock Score and SC_total must always be presented as novel contributions of this thesis.

**A-5: Forward-reference integrity test.**  
Identify all constructs used in argumentation before being formally defined. Flag any construct assigned a role or function without either (a) a prior definition in the text, or (b) an explicit forward reference to the chapter and section where it is defined.

**A-6: Data source specificity test.**  
For each variable, scale, or measurement instrument mentioned, verify the text explicitly states its data source — primary (survey), secondary (market data), or both. Flag any instance where the source is ambiguous.

**A-7: Cross-reference precision test.**  
Scan for vague structural references such as "later chapters", "subsequent analysis", "as discussed above". Flag any that lack a specific chapter and section number.

**A-8: Empirical illustration sourcing test.**  
For each practical example or case illustration, verify that at least one external reference supports the factual claims. Flag unsourced illustrations.

---

### SECTION B: Citation and reference tests (all chapters)

Run on every paragraph in the chapter under review. These tests were added following mentor feedback (April 2026).

**B-1: Named citation rule.**  
Flag any sentence containing a substantive empirical or theoretical claim that uses vague attribution in place of a named author citation. Prohibited phrases include but are not limited to:
- "empirical evidence suggests / indicates / shows / documents"
- "the literature suggests / indicates / shows"
- "research documents / demonstrates"
- "studies show / indicate"
- "the literature reviewed in this chapter"
- "as reviewed above / below"
- "recent work suggests"

Every such phrase must be replaced with a named author and year, e.g., "Kahneman & Tversky (1979) show that..." or "[Kahneman & Tversky, 1979](url)".

**B-2: Hyperlink completeness.**  
For every citation in the text — whether prose format (Author, Year) or markdown format ([Author, Year](URL)) — verify that a hyperlink URL is present. Flag any citation without a URL. Prose-only citations without hyperlinks are incomplete.

**B-3: Duplicate citation rule.**  
Flag any paragraph where the same author and year appear both as a prose mention at the start of a sentence (e.g., "Barber & Odean (2001) show that...") AND as a markdown citation at the end of the same sentence (e.g., "([Barber & Odean, 2001](url))"). Remove the duplicate: if the prose mention exists, remove the markdown; if only a markdown citation exists, keep it. Both forms are never needed in the same sentence.

**B-4: Citation year consistency.**  
Verify that the year used in every in-text citation matches the year in references.md. Key known risk: Barberis & Thaler should always be cited as 2002 (SSRN working paper), not 2003 (published version). Flag any mismatch between in-text year and references.md entry.

**B-5: "Information shock" terminology.**  
In narrative text (Ch.1, Ch.2, Ch.3, Ch.6), standalone "shock" or "shocks" in the conceptual sense must read as "information shock" or "information shocks". Exception: "Shock Score" is a proper noun and must never be changed. Exception: technical usage in Ch.4/Ch.5 (shock bar, shock characteristics, shock timestamp, shock return) must be preserved as-is. Flag any standalone conceptual use.

**B-6: Shock Score placement rule.**  
The Shock Score and SC_total must not be introduced or defined in Ch.3 (literature review). Ch.3 may reference alternative indices (Baker-Wurgler, FEARS, RavenPack, CNN Fear & Greed) and may include forward references such as "the Shock Score, introduced in Chapter 4...". Any definitional content about the Shock Score in Ch.3 is a violation. Authoritative definition belongs in Ch.4 s.4.3.

**B-7: Subsection length rule.**  
Flag any subsection (level 3 or 4 header) that contains fewer than three substantive sentences. Such subsections should be collapsed into the parent section as plain paragraphs. Note: in APA style, bold text at paragraph start is equivalent to a level 3/4 header — do not use bold as a substitute.

**B-8: Bias-to-study link rule.**  
Each behavioral bias discussed in a subsection (overconfidence, availability heuristic, herding, emotional bias, disposition effect) must end with a closing sentence explicitly linking that bias to the study's research design — specifically to the Net Risk Stance variable, the information shock context, or the Shock Score moderation mechanism. Flag any bias subsection that ends without this link.

**B-9: Objectives-to-RQ mapping.**  
In Ch.2, the mapping between study objectives and research questions must be stated explicitly. Currently: RQ1 addresses Objective 1 (decision response to shocks + downstream portfolio outcome); RQ2 addresses Objective 2 (Shock Score moderation). Flag if this mapping is absent or ambiguous.

**B-10: SC_total construct validity statement.**  
In Ch.5, the significant coefficient on SC_total (β₁) must be explicitly framed as empirical evidence of construct validity — not merely as a hypothesis test result. The Shock Score is a novel metric and the regression result is the proof that it measures something real. Flag if Ch.5 presents the result without this framing.

---

### SECTION C: Literature review tests (Ch.3 and literature review sections in other chapters)

Run in addition to Sections A and B when reviewing Ch.3 or any section containing literature synthesis.

**C-1: Attribution layer separation.**  
For each paragraph, classify every sentence into one of four epistemic layers:
- (a) Literature-established fact (single source)
- (b) Multi-source synthesis
- (c) Author interpretation or commentary
- (d) Novel contribution or gap claim

Flag any sentence where the layer is ambiguous or where layers (a)/(b) and (c)/(d) are blended without clear signalling.

**C-2: Standard term attribution.**  
Identify established domain-specific terms (e.g., "risk-adjusted performance", "return predictability", "procyclical rebalancing", "disposition effect"). Flag any such term that appears without a citation to the foundational literature that defines it.

**C-3: Literature-to-construct reasoning chain.**  
For each passage that connects a literature concept to an original construct (especially the Shock Score), verify that three elements are present: (a) what the literature establishes, (b) why it is relevant to the construct, (c) how the construct addresses or operationalizes it. Flag passages where any element is missing.

**C-4: Gap claim calibration.**  
Identify all statements claiming a gap, limitation, or insufficiency in the existing literature. For each, verify: (a) the claim is supported by the review evidence presented, (b) it is framed cautiously rather than as absolute, (c) it is logically connected to the thesis contribution. Flag overclaimed or unsupported gap statements.

**C-5: Section intro paragraph rule.**  
Section introduction paragraphs (blockquote summaries at the start of each section) must include the main references to be discussed in that section. Flag any section intro that makes claims without naming at least two of the papers reviewed in that section.

---

## PART 4 — HALLUCINATION SPOT-CHECK PROTOCOL

This section defines a structured spot-check procedure to detect citation hallucinations — cases where a paper is cited for a claim it does not actually support. This is distinct from the full hallucination audit in `hallucination_testing_protocol.md`, which covers all 92 references.

### What constitutes a hallucination

A citation hallucination occurs when:
- The cited paper does not address the specific claim in the sentence (scope mismatch)
- The cited paper addresses the general topic but not the specific mechanism claimed
- The cited paper explicitly contradicts the claim made
- The author, year, or title does not match the cited DOI
- A broad survey paper is cited as if it originated a specific finding

### High-risk citation patterns

Prioritize the following patterns for spot-checking, as they carry the highest hallucination risk:

1. **Broad surveys cited for specific findings** — e.g., Hirshleifer (2015) or Barberis & Thaler (2002) cited for a specific empirical result rather than a general survey statement
2. **Mechanism claims** — e.g., "X shows that overconfident investors do Y under condition Z" — verify the paper actually tests that specific condition
3. **First-use citations** — the first time a paper is cited in a chapter, verify the claim is accurate
4. **Papers without local file** — papers where `file` column in references.md is empty cannot be verified offline; these require web_fetch verification

### Spot-check procedure (per chapter)

For each chapter under review:

1. Identify all citations in the chapter
2. Select the 5 highest-risk citations using the priority patterns above
3. For each selected citation:
   a. State the exact claim made in the thesis sentence
   b. Fetch the abstract and conclusion of the cited paper via its DOI URL
   c. Verify whether the abstract/conclusion supports the specific claim
   d. Return one of three verdicts: **SUPPORTED**, **PARTIAL** (general topic matches but specific claim is not stated), or **UNSUPPORTED**
4. Report all PARTIAL and UNSUPPORTED verdicts with the exact sentence and the correct characterization of what the paper actually says
5. For UNSUPPORTED verdicts, propose either: (a) a replacement citation that does support the claim, or (b) a reframing of the claim to match what the paper actually says

### Known risk cases (from prior review)

The following citations were flagged during the April 2026 review session as potentially overclaiming — verify these first in any spot-check pass:

| Citation | Claim made | Risk |
|----------|-----------|------|
| Hirshleifer (2015) | "establishes that information shocks influence market prices through behavioral biases" | Broad survey; verify it specifically addresses information shocks |
| Loewenstein et al. (2001) | "activate affective responses that complement deliberative reasoning" | Verify "complement" is accurate to the paper's framing vs. "compete with" or "override" |
| Jolliffe & Cadima (2016) | PCA methodology reference | Verify paper covers index construction use cases, not only statistical theory |
| Henderson et al. (2018) | "structured pre-commitment mechanisms reduce emotional bias in investment" | Verify paper specifically addresses investment contexts |
| Statman (2019) | "structured pre-commitment mechanisms reduce emotional bias" | Verify paper makes this claim explicitly |
| Angelova et al. (2023) | "limited frameworks for adaptive decision support under uncertainty" | Verify paper addresses this gap claim specifically |

---

## PART 5 — EXECUTION PROTOCOL

### Standard diagnostic run

1. **Specify scope** — state chapter and sections under review
2. **Run Section A** — universal tests; report flags with paragraph/line references
3. **Run Section B** — citation and reference tests; report flags
4. **If Ch.3 or literature section, run Section C** — report flags separately
5. **Run Part 4 spot-check** — select 5 high-risk citations; verify and report
6. **Do not auto-correct** — produce a diagnostic report only; corrections are made in a separate revision pass using Part 2 rules
7. **Hard rules (Part 1)** — verify compliance only when revisions have been made; not during diagnostic-only passes

### Full thesis diagnostic run

Run the above procedure chapter by chapter in the following order:
1. Ch.1 — Sections A, B, Part 4 spot-check
2. Ch.2 — Sections A, B, Part 4 spot-check
3. Ch.3 — Sections A, B, C, Part 4 spot-check
4. Ch.4 — Sections A, B (pay special attention to B-6 Shock Score placement), Part 4 spot-check
5. Ch.5 — Sections A, B (pay special attention to B-10 SC_total construct validity), Part 4 spot-check
6. Ch.6 — Sections A, B, Part 4 spot-check

### Commit discipline

- Commits group by theme: missing references, link-to-study sentences, structural fixes, global replacements, content moves
- Commit messages reference the specific item codes from this protocol (e.g., "B-1: replace vague attribution phrases in Ch.4")
- One logical change per str_replace call — do not replace entire paragraphs when only one sentence changes
- Each citation addition/change should be its own str_replace targeting the smallest unique string
