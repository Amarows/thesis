# Framing Brief — Issue #201 (whole-thesis content/clarity round)

Working reference governing every prose edit in this round. The 49 inline `[//]: # ()`
comments in `thesis.md` are resolved against these canonical claims. State each the SAME
way in the Introduction, Executive Summary, and Chapter 6 so the thesis tells one story.

## Canonical claims
1. **Primary contribution = measure / predict / decompose behavioral bias (H1).** Lead with
   it. β₁ = −0.4874, p = 0.0015 (Shock Score significantly associated with Net Risk Stance).
2. **H2 is null, stated honestly.** Showing the dashboard (ShowSC) does not significantly
   moderate the simulated risk-return profile. The tool measures/predicts bias well; it does
   not change behavior in this design. No overclaiming.
3. **Shock Score measures/predicts NRS — it does not change it.** The dashboard is the
   (failed) intervention; H1 is measurement, not intervention.
4. **Direction = risk reduction.** Higher shock intensity → managers reduce exposure.
5. **Canonical interpretation = situational risk aversion under stress** (Huber et al., 2022):
   a measured, risk-reducing response even on positive-sentiment shocks. NOT "under-reaction",
   NOT panic-driven over-reaction.
6. **Components act on NRS, heterogeneously** (H1 robustness Spec 3 / Figure 5.6): Sentiment
   Extremity and Attention Intensity significantly negative, Event-Type Severity positive,
   Article Count non-significant.
7. **Data is secondary** — downloaded from Interactive Brokers and Benzinga; never "proprietary."
8. **Scope order:** financial decisions → international portfolio managers at large firms (not
   retail/individual investors) → S&P 500 large-cap (not mid-cap) → scenario/stock. Surface
   "U.S. stocks, international managers" in the Foreword / Executive Summary.
9. **Shock Score is shock-level, not stock-level** — quantifies a piece of information plus its
   price reaction; potentially transferable beyond finance.
10. **Register = EMBA, accessible.** Plain English; keep required methodology terms but
    introduce them plainly; extend implications cautiously to decision-making generally.
11. **Population caveat:** measures *intended* decisions of managers with no incentive to follow
    the protocol; future work = real decisions on a trading floor where the protocol is mandated.
12. **Neutral framing of pressure:** "financial decision-makers," not "every manager faces pressure."

## Resolved comment edits
- B-122 → cite Shefrin (2002) for the IPS/risk-target deviation claim.
- B-157 → attach Markowitz (1952) to the rational-premise sentence (no new reference).
- B-163 → "are well known" → "are widely recognized".
- B-181 → use "business analytics" throughout (replace "computational analytics").
- B-217 → §1.4.1 header → "Academic Contribution to Behavioral Finance" (drop "Literature").
- B-225 → keep the contribution paragraph; cut only the "As discussed in Chapter 3" cross-ref.
- B-235 → soften "comparatively rare"; cite Bhandari et al. (2008).
- B-354 → §2.3.2 header → "Evaluating the Effect of Displaying the Shock Score".
- B-1459 → render the full Table 5.7 (substantive coefficients only — drop N/A reference rows);
  generator change in `8_statistical_analysis.py` (`s551_main_lines`), re-run 8 then 9; Ch 6
  §6.2.2 cross-references Table 5.7.

## Process
- Edit section-by-section in document order, one reviewable pass at a time.
- Preserve placeholders, generated numbers/tables, and the user's `[//]: # ()` markers
  (removed only in a final cleanup pass after sign-off).
- Recompile `thesis_final.md` via `9_compile_thesis.py` after each pass (8 then 9 for the
  B-1459 table change).
