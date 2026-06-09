# Review 04 — Compilation & Citation Integrity (static)

**Branch:** `review/final-review` · **Method:** static checks only (no pipeline run, no recompile)
**Date:** 2026-06-09 · **Reviewer:** independent pre-merge examiner (read-only)

## 1. Unresolved placeholders / empty result blocks — PASS

Scan of `thesis_final.md` for `<!-- PLACEHOLDER:… -->`, `[To be populated…]`, and `<!-- RESULTS:BEGIN -->` markers:

- **Zero** unresolved placeholders.
- **Zero** "To be populated" stubs.
- **Zero** leftover `RESULTS:BEGIN` markers.

All 20 placeholder sections were merged correctly. **No blocker.**

(Note from Stage 1: `thesis_final.md` does contain 49 `[//]:` author comments — those are a content-cleanliness issue tracked in `review_01_comments.md`, not a compilation failure.)

## 2. Three-touchpoint citation check

Reference files:

- `references_apa.md`: **100** entries.
- `references.md`: **100** entries.
- The first-column key set is **identical across both files** (every key in one is in the other) — the two reference lists are fully synchronized.

### Orphan citations (cited in text, missing a reference) — NONE

All **90** distinct markdown-link in-text citations (`[Author, Year](https://…)`) resolve to a matching key in **both** `references_apa.md` **and** `references.md`. **Zero missing references.** This is the blocker-relevant condition in the brief, and it passes.

### Orphan references (in the list, never cited) — 3 (MINOR)

| Reference entry | Status |
|---|---|
| French & Roll, 1986 | **Uncited** anywhere in the body — genuine orphan |
| Thaler & Benartzi, 2004 | **Uncited** anywhere in the body — genuine orphan |
| Swiss Business School, 2026 | **Uncited** as an in-text source (the SBS handbook; institution name appears in the title/declaration but not as a `(Swiss Business School, 2026)` citation) |

APA 7 expects the reference list to contain only works cited in text, so three uncited entries are a **MINOR** compliance issue. **Not a blocker** (no citation lacks a reference). Recommend either citing these works or removing them from the list before final submission. (Note: "Swiss Business School, 2026" may be retained deliberately as the governing handbook; confirm with the author.)

### False alarms resolved (no action needed)

Two entries initially flagged as uncited are in fact cited; they failed a literal match only because the in-text form uses the APA serial comma before the ampersand, which is **correct** APA 7:

- `DeMiguel, Garlappi & Uppal, 2009` → cited at `thesis.md:824` as "(DeMiguel, Garlappi, & Uppal, 2009)".
- `Weber, Siebenmorgen & Weber, 2005` → cited at `thesis.md:783` as "(Weber, Siebenmorgen, & Weber, 2005)".

## 3. Main-body word count — PASS

Counted on the compiled `thesis_final.md`, from "# Chapter 1" up to "# References", excluding front matter, references, appendices, and table-cell text:

- **Main-body prose: ≈ 29,354 words** (table cells, excluded, add ~1,665 more).
- Requirement (#202, Handbook): **≥ 20,000 words**, front matter and appendices excluded.

**Comfortably satisfied (~147% of the minimum).**

## 4. Blocker assessment

- **No CRITICAL blocker:** no unresolved placeholders, no missing-reference (orphan) citations, word count exceeds the minimum.
- **MINOR:** 3 uncited reference entries (French & Roll 1986; Thaler & Benartzi 2004; Swiss Business School 2026) — cite or remove for full APA list hygiene.

*Method note: the citation cross-check was performed with a throwaway extraction script under `diagnostics/`, since removed; results above were verified against `thesis.md` directly (lines 783, 824) for the two false alarms.*
