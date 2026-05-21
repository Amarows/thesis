# Session 4 Proposed Issues — Quality Diagnostic

Issue stubs prepared for opening as GitHub issues in the revision session (Session 5).
**Do not open issues from this diagnostic session** — per protocol Session 4 is diagnostic only, no API calls to GitHub issues.

Each entry uses the format:
- **Title**: `[<protocol_code>] Ch.<chapter>.<section> <short description>`
- **Priority**: P1 / P2 / P3
- **Body**: shared template from Session 1.

---

## P1 issues (2)

### Issue 1
**Title:** `[B-2] Ch.4.3 Replace fabricated FinBERT citation (Huang, Roesler & Reske, 2020)`
**Priority:** P1
**Body:**
> **Protocol code:** B-2 (also Part 4 UNSUPPORTED)
> **Location:** thesis.md L800 (Table 4.2 row "Sentiment scores"), L812 (Section 4.3.3 prose paragraph)
> **Issue:** The in-text citation "Huang, Roesler & Reske, 2020" with bracket DOI `https://doi.org/10.1145/3583780.3615272` does not correspond to any verifiable FinBERT paper. The author triple is not in references.md and the DOI does not resolve to a FinBERT publication.
> **Source check:** No paper by Huang/Roesler/Reske on FinBERT exists in the published record. The established FinBERT references are Araci (2019, arXiv:1908.10063), Liu/Huang/Xu (2020, IJCAI), Yang/Huang/Mayo (2020), and Huang/Wang/Yang (2023, *Contemporary Accounting Research*). references.md (line 79) has "Yang et al., 2020" with arXiv URL `https://arxiv.org/abs/2006.08097` for FinBERT.
> **Proposed fix (HR-1/HR-2/HR-5 compliant):**
> - Replace the in-text citation in both L800 (Table 4.2) and L812 (Section 4.3.3) with `[Yang et al., 2020](https://arxiv.org/abs/2006.08097)`, matching the existing entry in references.md.
> - Alternatively, if the author intended a different FinBERT variant, add the correct reference to references.md and update the bracket link DOI to a resolvable URL.
> **Acceptance criteria:** Both in-text instances cite a FinBERT paper that exists in references.md with a working URL. No claim about FinBERT is removed.

### Issue 2
**Title:** `[B-2] Ch.3.2 Add missing references — Bikhchandani & Sharma (2001) and Bikhchandani, Hirshleifer & Welch (1992)`
**Priority:** P1
**Body:**
> **Protocol code:** B-2 (also Part 4 UNSUPPORTED-at-reference-level)
> **Location:** thesis.md L432 (Section 3.2.1, herding paragraph)
> **Issue:** Two citations appear in the herding paragraph: prose mention "Bikhchandani & Sharma (2001)" without hyperlink, and bracket citation `[Bikhchandani et al., 1992](https://doi.org/10.1086/261849)`. Neither author/year combination is in references.md.
> **Source check:** Bikhchandani, Hirshleifer & Welch (1992) "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades" — *Journal of Political Economy* 100(5), 992–1026 — DOI `10.1086/261849` is correct. Bikhchandani & Sharma (2001) — most likely "Herd Behavior in Financial Markets" — *IMF Staff Papers* Vol. 47, No. 3, pp. 279–310; DOI `10.2307/3867650` (or via JSTOR).
> **Proposed fix (HR-1 compliant — no citations removed):**
> - Add both references to references.md with hyperlinks.
> - Add a hyperlink to the prose mention "Bikhchandani & Sharma (2001)" in L432: `[Bikhchandani & Sharma, 2001](https://doi.org/10.5089/9781451846324.024)` or appropriate JSTOR URL.
> **Acceptance criteria:** Both references appear in references.md with verifiable URLs; both in-text citations are hyperlinked.

---

## P2 issues (10)

### Issue 3
**Title:** `[B-4] Cross-document normalisation of Lim 2025 vs Lim 2026`
**Priority:** P2
**Body:**
> **Protocol code:** B-4
> **Location:** thesis.md L156, L168, L180 (Ch.1); L255 (Ch.2); L571, L576, L591, L592, L601 (Ch.3); plus references.md line 55.
> **Issue:** The same paper by Tristan Lim (DOI `10.1080/15427560.2025.2609644`) is cited inconsistently as **Lim (2025)** in eight in-text instances and as **Lim (2026)** in three in-text instances and in references.md. Internal Table 3.1 inconsistency: row 6 (L591) "Lim (2025)" vs row 7 (L592) "Lim (2026)" describe the same paper.
> **Source check:** SSRN preprint date September 2025; published in *Journal of Behavioral Finance* online 30 January 2026 (volume/issue not yet assigned). APA convention uses the publication year; references.md correctly uses 2026.
> **Proposed fix:**
> - Normalise all in-text instances to **Lim, 2026**, matching references.md.
> - Use targeted `str_replace` per line; do not paraphrase surrounding text (HR-5).
> **Acceptance criteria:** All in-text mentions of this paper read "Lim, 2026" or "Lim (2026)"; references.md unchanged.

### Issue 4
**Title:** `[B-4] Ch.2.3/2.7/2.8 Correct Charness et al. (2012) DOI from .08.006 to .08.009`
**Priority:** P2
**Body:**
> **Protocol code:** B-4
> **Location:** thesis.md L288, L370, L382
> **Issue:** In-text bracket citation `[Charness et al., 2012](https://doi.org/10.1016/j.jebo.2011.08.006)` — DOI ends in `.08.006`. references.md (line 63) has `.08.009`. Publisher record (ScienceDirect) confirms `10.1016/j.jebo.2011.08.009` is the correct DOI.
> **Proposed fix:** Three targeted `str_replace` calls, one per line. Replace `2011.08.006` with `2011.08.009`.
> **Acceptance criteria:** All three in-text instances match references.md and resolve to the correct paper.

### Issue 5
**Title:** `[B-4] Ch.3.2 Normalise Hirshleifer (2015) URL to annurev DOI`
**Priority:** P2
**Body:**
> **Protocol code:** B-4
> **Location:** thesis.md L430
> **Issue:** Bracket citation `[Hirshleifer, 2015](https://dx.doi.org/10.2139/ssrn.2480892)` uses the SSRN preprint URL. All other Hirshleifer 2015 instances in the thesis (L146, L230, L236, L249, L253, L263, L323, L424, L1376) use `https://doi.org/10.1146/annurev-financial-092214-043752` (the published *Annual Review* DOI). references.md uses the annurev DOI.
> **Proposed fix:** Single targeted `str_replace` replacing the SSRN URL with the annurev DOI URL.
> **Acceptance criteria:** All Hirshleifer 2015 in-text URLs match.

### Issue 6
**Title:** `[B-2] Ch.4.5 Add missing reference MacKinnon & White (1985)`
**Priority:** P2
**Body:**
> **Protocol code:** B-2 (and A-1 unsupported substantive methodological claim)
> **Location:** thesis.md L1139 (Section 4.5.2 Inference and Clustering)
> **Issue:** Prose citation "(MacKinnon and White, 1985)" supports the methodological claim that HC3 provides a finite-sample improvement over HC1/HC2 and is the recommended default for small-to-medium samples. The reference is not in references.md and has no hyperlink.
> **Source check:** MacKinnon & White (1985) "Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties" — *Journal of Econometrics* 29(3), 305–325 — DOI `10.1016/0304-4076(85)90158-7`.
> **Proposed fix:** Add MacKinnon & White (1985) to references.md with verified URL; add hyperlink to the in-text prose citation.
> **Acceptance criteria:** Reference exists in references.md; in-text mention has working hyperlink.

### Issue 7
**Title:** `[B-2] Ch.5.5.1 Replace or add reference for Mason et al. (1986)`
**Priority:** P2
**Body:**
> **Protocol code:** B-2
> **Location:** thesis.md L1227 (Section 5.5.1 Step 2)
> **Issue:** Prose citation "(Mason et al., 1986)" attributed to "SBS research standards" for the α = 0.05 significance threshold. Reference not in references.md and the attribution as SBS standards is unusual.
> **Proposed fix:** Either (a) add Mason, Lind & Marchal (1986) "Statistics: An Introduction" to references.md with hyperlink, or (b) replace the prose citation with `[Swiss Business School, 2025](C_S_4__Masters_Thesis_Handbook_v_1_8_Ver_1.pdf)` (the SBS handbook entry in references.md line 86) if the threshold is in fact specified in the SBS handbook.
> **Acceptance criteria:** Whichever source is referenced exists in references.md with verifiable identifier.

### Issue 8
**Title:** `[B-2] Ch.5.9.4 Correct author name and add reference for ICC guideline (Koo & Mae → Koo & Li, 2016)`
**Priority:** P2
**Body:**
> **Protocol code:** B-2
> **Location:** thesis.md L1355, L1357 (Section 5.9.4 Instrument Internal Consistency)
> **Issue:** Two prose citations "(Koo and Mae, 2016)" reference the ICC(2,1) methodological guideline. The author name "Mae" appears to be a typo — the widely-cited reference is **Koo & Li (2016)** "A Guideline of Selecting and Reporting Intraclass Correlation Coefficients for Reliability Research" (*Journal of Chiropractic Medicine* 15(2):155–163, DOI `10.1016/j.jcm.2016.02.012`).
> **Proposed fix:** Correct author name from "Mae" to "Li" in both in-text instances; add Koo & Li (2016) to references.md with verified URL.
> **Acceptance criteria:** Correct author name in text and matching reference entry in references.md.

### Issue 9
**Title:** `[B-2] Ch.3.6.3 Reconcile RavenPack reference year (2017 vs 2023)`
**Priority:** P2
**Body:**
> **Protocol code:** B-2 / B-4
> **Location:** thesis.md L654 (Table 3.2 source note)
> **Issue:** Table note states *"Based on Baker and Wurgler (2006), Da et al. (2015), RavenPack (2023), Statman (2019), and the present study design."* — references.md (line 58) lists **RavenPack, 2017**. If the cited RavenPack content is the 2017 sentiment-index whitepaper, change the table note to 2017. If a 2023 RavenPack source is in fact used, add it to references.md.
> **Proposed fix:** Change in-text "RavenPack (2023)" to "RavenPack (2017)" matching references.md (HR-1/HR-2/HR-5 compliant).
> **Acceptance criteria:** Year in text matches references.md.

### Issue 10
**Title:** `[B-2] Ch.3.5 Add missing reference Rigobon (2003)`
**Priority:** P2
**Body:**
> **Protocol code:** B-2
> **Location:** thesis.md L552 (Section 3.5)
> **Issue:** Bracket citation `[Rigobon, 2003](https://doi.org/10.1162/003465303772815727)` — DOI resolves to Rigobon (2003) "Identification through Heteroskedasticity" *Review of Economics and Statistics* 85(4):777–792 — but the reference is not in references.md.
> **Proposed fix:** Add Rigobon (2003) to references.md with the DOI URL already present in the in-text bracket link.
> **Acceptance criteria:** Reference exists in references.md.

### Issue 11
**Title:** `[B-10] Ch.5.6.1 Add construct-validity framing for SC_total β₁ coefficient`
**Priority:** P2
**Body:**
> **Protocol code:** B-10
> **Location:** thesis.md §5.6.1 (around L1297)
> **Issue:** Per protocol B-10, the significant coefficient on SC_total (β₁) must be explicitly framed in Ch.5 as empirical evidence of construct validity for the Shock Score (not merely as a hypothesis-test result). Ch.5 currently presents β₁ = −0.4874 only as a hypothesis test outcome with interpretive notes. The construct-validity framing appears only in Ch.6 (L1394).
> **Proposed fix:** Add a single bridging sentence in §5.6.1 immediately after the H1 result interpretation, along the lines of: *"Because SC_total is a novel composite constructed in this thesis, the statistically significant coefficient β₁ constitutes empirical evidence of construct validity — the index systematically predicts NRS in the theoretically expected direction across all robustness specifications."* HR-2/HR-5 compliant: minimal, no scope expansion.
> **Acceptance criteria:** Ch.5 contains an explicit construct-validity framing sentence for β₁; existing hypothesis-test interpretation preserved.

### Issue 12
**Title:** `[A-1] Ch.6.3.1 Repair broken sentence at L1394`
**Priority:** P2
**Body:**
> **Protocol code:** A-1
> **Location:** thesis.md L1394 (Section 6.3.1 Theoretical and Methodological Contributions)
> **Issue:** Sentence reads *"…before the decision is made.ion and overconfidence into a quantifiable indicator, responding to calls for tools that integrate psychological insights into investment practice and enabling these concepts to be monitored and managed in real time."* — orphan fragment "made.ion and overconfidence into a quantifiable indicator" makes the paragraph ungrammatical.
> **Proposed fix:** Reconstruct the missing sentence. Most likely intended reading: *"…before the decision is made. The Shock Score translates concepts such as loss aversion and overconfidence into a quantifiable indicator, responding to calls for tools that integrate psychological insights into investment practice and enabling these concepts to be monitored and managed in real time."* HR-2: meaning preservation; HR-5: minimal repair.
> **Acceptance criteria:** Paragraph reads grammatically; no new claims introduced beyond what context implies.

### Issue 13
**Title:** `[A-1/C-2] Ch.6.7.2 Add citation for automation bias claim`
**Priority:** P2
**Body:**
> **Protocol code:** A-1 (unsupported substantive claim) and C-2 (standard term attribution)
> **Location:** thesis.md L1453 (Section 6.7.2 Risk of Automation Bias)
> **Issue:** *"Automation bias is the documented tendency of human decision-makers to assign disproportionate weight to outputs that are presented as the product of an algorithm… The presence of automation bias has been observed across professional contexts, including aviation, medicine, and finance…"* — substantive empirical claims about an established phenomenon documented across multiple domains, with no supporting citation.
> **Proposed fix:** Add citation(s) for the term and the cross-domain evidence. Standard sources: Mosier & Skitka (1996) for the term; Parasuraman & Manzey (2010) "Complacency and Bias in Human Use of Automation" (*Human Factors* 52(3):381–410, DOI `10.1177/0018720810376055`) for cross-domain evidence. Add to references.md and add hyperlinked in-text citations.
> **Acceptance criteria:** L1453 substantive claims supported by named, hyperlinked citations; references.md updated.

### Issue 14
**Title:** `[B-2] Ch.2.2 Reframe or cite Interactive Brokers (2026) figure-note attribution`
**Priority:** P2
**Body:**
> **Protocol code:** B-2
> **Location:** thesis.md L245 (figure note for Figure 2.1)
> **Issue:** Figure note reads *"From Interactive Brokers (2026)."* — citation-style attribution without a corresponding entry in references.md and without a hyperlink.
> **Proposed fix:** Either (a) add an Interactive Brokers data-source entry to references.md with URL `https://www.interactivebrokers.co.uk`, or (b) reframe to non-citation form: *"Source: Interactive Brokers intraday price and volume data for Meta Platforms Inc. (ticker: META), retrieved via the Interactive Brokers API."* — HR-2 compliant (meaning preserved).
> **Acceptance criteria:** Figure note either has a valid references.md entry or is reframed to non-citation prose.

---

## P3 issues (selected — full set is voluminous; 15 representative items)

### Issue 15
**Title:** `[A-7] Ch.6.8 Correct cross-reference from Chapter 2 to Chapter 3`
**Priority:** P3
**Body:**
> **Protocol code:** A-7
> **Location:** thesis.md L1473
> **Issue:** *"The evidence base established in Chapter 2 demonstrates that overreaction, loss aversion, herding, and attention-driven trading around news events contribute to price overshooting…"* — the literature review is in Chapter 3, not Chapter 2.
> **Proposed fix:** Replace "Chapter 2" with "Chapter 3" in this sentence.
> **Acceptance criteria:** Cross-reference matches the chapter that contains the cited material.

### Issue 16
**Title:** `[B-3] Ch.3.2 Remove duplicate prose+bracket citations (9 instances)`
**Priority:** P3
**Body:**
> **Protocol code:** B-3
> **Location:** thesis.md L432, L435, L465, L496, L500, L538, L552, L565 (two), L569
> **Issue:** In nine sentences, the same author and year appear both as a prose mention ("Author (Year) show that…") AND as a markdown bracket citation at the end of the same sentence. Per B-3: remove the markdown bracket where the prose mention exists.
> **Proposed fix:** Per protocol B-3, remove the trailing markdown bracket citation in each of the nine instances. Targeted `str_replace` per instance.
> **Acceptance criteria:** Each affected sentence contains either the prose mention OR the markdown bracket, not both.

### Issue 17
**Title:** `[HR-6] Ch.3 Add hyperlinks to prose citations across §3.2–§3.6 (cluster)`
**Priority:** P3 (cluster — work as a batch)
**Body:**
> **Protocol code:** HR-6 (also B-2 hyperlink completeness)
> **Location:** thesis.md ~25 prose citations across Ch.3, especially §3.5, §3.6.1, §3.6.4, and Table 3.1/3.2 notes.
> **Issue:** Numerous prose mentions of the form "Author (Year)" appear without an accompanying markdown bracket link with URL in the same paragraph. All cited authors are in references.md.
> **Proposed fix:** Add a hyperlinked markdown citation at the appropriate place in each paragraph. Where the prose mention is the natural place to link, replace `Author (Year)` with `[Author (Year)](url)`. Targeted `str_replace` per instance. Work in commit batches grouped by section.
> **Acceptance criteria:** Every prose mention of a referenced work in Ch.3 has a hyperlink available within the same paragraph.

### Issue 18
**Title:** `[C-5] Ch.3 Add intro paragraphs to §3.3, §3.4, and §3.5`
**Priority:** P3
**Body:**
> **Protocol code:** C-5
> **Location:** thesis.md §3.3 (L478), §3.4 (L507), §3.5 (L534–L536)
> **Issue:** §3.3 and §3.4 have no intro paragraph between the level-2 header and the first level-3 subsection. §3.5 has an intro paragraph but it names no specific reviewed papers (C-5 requires naming at least two of the papers reviewed in the section).
> **Proposed fix:** Add a single short intro paragraph at the start of §3.3 and §3.4 naming two key papers reviewed in each section. For §3.5, add named references (e.g., Statman 2019, Bianchi et al. 2022) to the existing intro paragraph.
> **Acceptance criteria:** Each section intro names ≥ 2 papers reviewed in that section.

### Issue 19
**Title:** `[C-1] Ch.3.1 Clarify attribution layer in causal-pathway synthesis paragraph`
**Priority:** P3
**Body:**
> **Protocol code:** C-1
> **Location:** thesis.md L417 (Section 3.1 closing paragraph)
> **Issue:** Paragraph opens with author-interpretation marker *"Taken together, the studies reviewed below are interpreted in this thesis as implying…"* then transitions into a sequence of declaratively-framed claims that read as established facts.
> **Proposed fix:** Add hedging language ("the reviewed literature suggests", "may", "the proposed mechanism") to subsequent sentences in the paragraph, making it explicit which sentences are author interpretation and which are literature-established.
> **Acceptance criteria:** Paragraph distinguishes author interpretation from literature-established findings.

### Issue 20
**Title:** `[B-7] Ch.3.6.3 Convert bold-as-header subsections to proper headers or remove bold`
**Priority:** P3
**Body:**
> **Protocol code:** B-7
> **Location:** thesis.md L611, L619, L625, L629, L656 (bold subsection leads in §3.6.3)
> **Issue:** Subsections "Category 1: Composite Sentiment Indices for Return Forecasting", "Category 2: Volatility-Based Fear Gauges", "Category 3: Behavioral Risk Profiling Tools", "The Shock Score's Distinct Contribution", "Technical Distinction: PCA Application" use bold-text leads rather than proper level-4 headers.
> **Proposed fix:** Either promote to `#### Header` form or remove the bold and integrate the labels as the first phrase of each paragraph.
> **Acceptance criteria:** Bold-as-header pattern eliminated in §3.6.3.

### Issue 21
**Title:** `[B-2] Ch.4.3.5 Add hyperlink to prose Baker & Wurgler (2006) citation`
**Priority:** P3
**Body:**
> **Protocol code:** B-2 / HR-6
> **Location:** thesis.md L854 (Section 4.3.5 first paragraph)
> **Issue:** Prose *"(Baker & Wurgler, 2006)"* lacks markdown hyperlink. Reference is in references.md.
> **Proposed fix:** Replace `(Baker & Wurgler, 2006)` with `([Baker & Wurgler, 2006](https://doi.org/10.1111/j.1540-6261.2006.00885.x))` matching references.md.
> **Acceptance criteria:** Citation hyperlinked.

### Issue 22
**Title:** `[A-1] Ch.5.2.3 Cite Kaiser criterion or Jolliffe & Cadima for PCA diagnostic threshold`
**Priority:** P3
**Body:**
> **Protocol code:** A-1
> **Location:** thesis.md L1190
> **Issue:** *"The eigenvalue of 2.1027 exceeds 1.0, satisfying the Kaiser criterion."* — standard methodological criterion stated without citation.
> **Proposed fix:** Add inline citation `[Jolliffe & Cadima, 2016](https://doi.org/10.1098/rsta.2015.0202)` (already in references.md) after "Kaiser criterion".
> **Acceptance criteria:** Methodological criterion has a supporting citation.

### Issue 23
**Title:** `[B-7] Ch.5.9.3 Expand "Stated Preference Validity" subsection or merge into §5.9.1`
**Priority:** P3
**Body:**
> **Protocol code:** B-7
> **Location:** thesis.md §5.9.3 (L1349 – L1351)
> **Issue:** Subsection contains two sentences total — below the three-substantive-sentence threshold.
> **Proposed fix:** Either expand with one or two additional substantive sentences linking to the broader limitation in §5.9.1, or collapse §5.9.3 into a paragraph within §5.9.1.
> **Acceptance criteria:** Either ≥ 3 substantive sentences in §5.9.3 or content integrated into §5.9.1.

### Issue 24
**Title:** `[A-5] Ch.1.1 Add forward reference for first use of "information shock"`
**Priority:** P3
**Body:**
> **Protocol code:** A-5
> **Location:** thesis.md L120 (Section 1.1.2)
> **Issue:** "information shocks" used substantively before being formally defined (Ch.2 L325, Ch.3 L409). No forward pointer.
> **Proposed fix:** At first use, add parenthetical "(formally defined in Section 2.6)" or similar.
> **Acceptance criteria:** First use of the term either has a forward reference or is preceded by a brief working definition.

### Issue 25
**Title:** `[A-8] Ch.2.2 Source the Meta 2 Feb 2026 market-interpretation claim`
**Priority:** P3
**Body:**
> **Protocol code:** A-8
> **Location:** thesis.md L236
> **Issue:** *"The announcement was widely interpreted as outperforming market expectations…"* — empirical claim about market interpretation is not sourced. The only attribution (Interactive Brokers) is for price data.
> **Proposed fix:** Add a citation to a news source covering the earnings announcement, or reframe to remove the empirical interpretation claim while preserving the price-pattern illustration.
> **Acceptance criteria:** Empirical interpretation claim either sourced or removed.

### Issue 26
**Title:** `[B-7] Ch.6.3.1 Demote header level from ## to ###`
**Priority:** P3
**Body:**
> **Protocol code:** B-7 (header structural consistency)
> **Location:** thesis.md L1392 (header `## 6.3.1 Theoretical and Methodological Contributions`)
> **Issue:** Section 6.3.1 should be a level-3 subsection of §6.3 (`### 6.3.1`) but is currently a level-2 header (`## 6.3.1`).
> **Proposed fix:** Change `## 6.3.1` to `### 6.3.1`.
> **Acceptance criteria:** Header level consistent with sibling §6.3 subsections.

### Issue 27
**Title:** `[B-1] Ch.3.1 Replace vague "the literature reviewed" closing in §3.2.5`
**Priority:** P3
**Body:**
> **Protocol code:** B-1
> **Location:** thesis.md L471 / L475
> **Issue:** *"The reviewed literature shows that behavioral biases—particularly overconfidence, availability heuristics, herding, and loss aversion—distort professional investors' judgment during information shocks."* and *"In sum, the literature establishes that behavioral biases shape short-term price dynamics…"* — vague "the literature".
> **Proposed fix:** Replace with named-author summary referring to ≥ 2 of the papers reviewed in §3.2 (e.g., "Barberis & Thaler (2002) and Hirshleifer (2015) document that…").
> **Acceptance criteria:** No remaining "the literature" attributions in the §3.2 closing paragraphs.

### Issue 28
**Title:** `[C-2] Ch.2/Ch.3 Cite foundational source for "procyclical rebalancing" on first use`
**Priority:** P3
**Body:**
> **Protocol code:** C-2
> **Location:** thesis.md L230 (Ch.2), L498 (Ch.3)
> **Issue:** Domain term "procyclical rebalancing" used without first-use foundational citation.
> **Proposed fix:** At first substantive use, add a citation to Cremers et al. (2021) or Harvey et al. (2025) (both already in references.md) that documents the mechanism.
> **Acceptance criteria:** First use of "procyclical rebalancing" has a foundational citation.

### Issue 29
**Title:** `[A-1] Ch.3.2 Repair stray closing parenthesis at L459`
**Priority:** P3
**Body:**
> **Protocol code:** A-1 (typo / minor)
> **Location:** thesis.md L459
> **Issue:** Sentence ends *"…consistent with investor overreaction rather than efficient price adjustment)."* — orphan `)` indicates a punctuation error.
> **Proposed fix:** Remove the orphan `)`.
> **Acceptance criteria:** Punctuation balanced.

---

**Note on completeness.** This staged-issues file covers the highest-priority items per protocol code and chapter. The full HR-6 prose-citation backlog in Ch.3 (~25 line items) is treated as a single P3 cluster issue (#17) for execution-time efficiency rather than itemised individually. Per protocol Part 4 verdicts: only the two confirmed UNSUPPORTED items (Huang/Roesler/Reske, Bikhchandani) escalate to P1. The Hirshleifer (2015), Henderson (2018), Statman (2019), and Angelova (2023) PARTIAL verdicts do not require citation removal (HR-1) — proposed fixes for them involve reframing the in-text claim language (e.g., "establish" → "review and discuss") rather than changing the cited source.
