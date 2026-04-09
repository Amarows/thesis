# THESIS QUALITY CONSTRAINTS — DIAGNOSTIC TESTS AND HARD RULES

This document defines reusable diagnostic tests and hard constraints for reviewing thesis chapters. Tests are designed to be run repeatedly on different chapters. Each test produces a pass/fail result per paragraph or section.

---

## SECTION A: HARD RULES (ALL CHAPTERS)

These constraints must never be violated during any revision or review pass.

**HR-1: Reference preservation.** No existing citation, DOI, URL, or in-text reference may be removed, replaced, or consolidated.

**HR-2: Meaning preservation.** The semantic content of every paragraph must remain unchanged after revision. No new claims added, no existing claims removed, no altered positioning.

**HR-3: No scope expansion.** Revisions must not introduce new literature, new constructs, or new theoretical claims beyond what exists in the current draft.

**HR-4: Academic register.** Formal academic tone must be maintained throughout. No colloquial, didactic, or introductory-level language.

---

## SECTION B: UNIVERSAL DIAGNOSTIC TESTS (ALL CHAPTERS)

Run these tests on each paragraph. Flag violations; do not auto-correct.

### B-1: Unsupported claim detection

Scan each sentence for substantive claims — any statement asserting a relationship, mechanism, empirical regularity, definition, or consequence. Flag sentences where such a claim appears without an accompanying citation.

### B-2: Epistemic framing test

In chapters preceding empirical analysis, scan for declarative causal statements (e.g., "X affects Y," "X leads to Y"). Flag any sentence that presents a relationship under investigation as an established fact rather than using investigative framing (e.g., "this study examines whether," "the hypothesis that").

### B-3: Assumption-vs-literature test

Scan for phrases such as "this thesis assumes," "this study assumes," "it is assumed that." For each, determine whether the assumed relationship is already established or proposed in the literature. If so, flag — the sentence should cite the literature rather than frame the relationship as an assumption.

### B-4: Original-vs-established boundary test

For each construct, method, or framework mentioned, determine whether it is the author's original contribution or drawn from existing literature. Flag any instance where this distinction is ambiguous — i.e., the reader cannot tell whether the construct is original or cited.

### B-5: Forward-reference integrity test

Identify all constructs that are used in argumentation before being formally defined. Flag any construct that is assigned a role or function without either (a) a prior definition in the text, or (b) an explicit forward reference to the chapter and section where it is defined.

### B-6: Data source specificity test

For each variable, scale, or measurement instrument mentioned, verify that the text explicitly states its data source — primary (survey), secondary (market data), or both. Flag any instance where the source is ambiguous.

### B-7: Cross-reference precision test

Scan for vague structural references such as "theory," "later chapters," "subsequent analysis," "as discussed." Flag any that lack a specific chapter and section number.

### B-8: Empirical illustration sourcing test

For each practical example or case illustration, verify that at least one external reference (data provider, news source, academic study) supports the factual claims. Flag unsourced illustrations — these read as subjective interpretation.

---

## SECTION C: LITERATURE REVIEW DIAGNOSTIC TESTS

These tests apply specifically to literature review chapters or sections. Run in addition to Section B.

### C-1: Attribution layer separation

For each paragraph, classify every sentence into one of four epistemic layers:
- (a) Literature-established fact (single source)
- (b) Multi-source synthesis
- (c) Author interpretation or commentary
- (d) Novel contribution or gap claim

Flag any sentence where the layer is ambiguous or where layers (a)/(b) and (c)/(d) are blended without clear signalling.

### C-2: Standard term attribution test

Identify established domain-specific terms (e.g., "risk-adjusted performance," "market inefficiency," "return predictability," "procyclical rebalancing"). Flag any such term that appears without a citation to the foundational literature that defines it.

### C-3: Literature-to-construct reasoning chain test

For each passage that connects a literature concept to an original construct, verify that three elements are present: (a) what the literature establishes, (b) why it is relevant to the construct, (c) how the construct addresses or operationalizes it. Flag passages where any element is missing — the reasoning chain must be explicit.

### C-4: Gap claim calibration test

Identify all statements claiming a gap, limitation, or insufficiency in the existing literature. For each, verify that the claim is (a) supported by the review evidence presented, (b) framed cautiously rather than as absolute, and (c) logically connected to the thesis contribution. Flag overclaimed or unsupported gap statements.

---

## EXECUTION PROTOCOL

When running diagnostics on a chapter:

1. **Specify scope** — state which chapter or section is under review.
2. **Run Section B tests** — report flagged items per test, with paragraph or sentence references.
3. **If literature review, run Section C tests** — report flagged items separately.
4. **Do not auto-correct** — present flags as a diagnostic report. Corrections are made in a separate step under the master revision prompt constraints.
5. **Hard rules (Section A)** — verify compliance only when revisions have been made; not during diagnostic-only passes.