# Reducing Emotional Biases in Investment Portfolio Management

Executive MBA thesis — **SBS Swiss Business School**, Kloten-Zurich.
**Author:** Aliaksei Malashonak · **Mentor:** Dr. Stefano Canossa · **September 2026**

---

## Overview

This research examines whether external financial information shocks cause systematic shifts in
professional equity portfolio managers' decisions, and whether a structured decision-support tool —
the **Shock Score** — can moderate those responses. It bridges behavioral-finance theory with
operational decision support, moving from explanation toward intervention.

The **Shock Score** is a PCA-based composite index built entirely from public secondary data
(intraday prices from Interactive Brokers, headline news from Benzinga, FinBERT sentiment). It
combines four standardized event-level components — article count, sentiment extremity, attention
intensity, and event-type severity — into a single, *ex-ante* measure of information-shock intensity,
and is also presented to managers as a four-signal dashboard (sentiment direction, severity,
persistence horizon, pre-commitment protocol).

## Hypotheses and headline findings

- **H1 — supported.** Shock Score intensity is a statistically significant predictor of managers'
  Net Risk Stance (β₁ = −0.4874, *p* = 0.0015): higher shock intensity is associated with a
  risk-reducing shift, even when the underlying news is favorable.
- **H2 — not supported (informative null).** Displaying the Shock Score dashboard did not
  significantly change simulated portfolio risk–return outcomes (τ = −0.1584, *p* = 0.7428), a result
  bounded by limited statistical power rather than a confirmed absence of effect.

**Design:** within-subject quasi-experimental scenario survey; 53 professional respondents across
24 scenarios (424 scenario-level observations); panel OLS with two-way cluster-robust standard errors,
HC3 and respondent fixed-effects robustness checks.

## Repository layout

```
thesis.md                 Authored thesis text (Markdown, APA) — the only hand-edited content file
thesis_final.md           Compiled output (generated; never edit by hand)
references.md             Reference list with local PDF filenames
references_apa.md          APA-formatted reference table (source of the compiled bibliography)
config.py                 Single source of truth for all pipeline constants
CLAUDE.md                 Full project specification and conventions

1_download.py             Download prices + news via the Interactive Brokers API
2_prepare_data.py         Merge news, compute coverage statistics
3_survey_assembly.py      Build survey assets (charts, dashboards, scenario metadata)
4_deploy_google_forms.py  Create/update the Google Forms
5_append_pilot_feedback.py  Append pilot responses to the live forms
6_process_survey_data.py  Download responses, normalize, join Shock Score, apply exclusions
7_verification.py         Pipeline verification checks
8_statistical_analysis.py H1 OLS + robustness, H2 portfolio simulation, descriptives, normality
9_compile_thesis.py       Merge results into thesis.md -> thesis_final.md (+ DOCX)

data/        Market 30-min bars and Benzinga news; portfolio.csv; scenario_manifest.csv
survey/      Generated survey assets (charts, dashboards, metadata, counterbalancing)
results/     Analysis outputs — analysis_panel.csv, tables/, figures/, thesis_results.md
toolkits/    Market-data, news-sentiment, and event-selection toolkits
src_api_*/   Interactive Brokers and Yahoo Finance connectors
documents/   Compiled thesis (PDF/DOCX), approval forms, defense deck, handbook
```

## How the thesis is compiled

`thesis.md` is the single authored content file. It contains machine-readable placeholders
(`<!-- PLACEHOLDER:id -->`) that `9_compile_thesis.py` replaces with the matching result blocks from
`results/thesis_results.md`, producing `thesis_final.md` (and a DOCX).

> **`thesis_final.md` is generated output — never edit it by hand.** All prose edits go to `thesis.md`,
> then run `9_compile_thesis.py` to regenerate. Final APA page formatting is applied manually in Word.

## Reproducing the analysis

```bash
python -m venv .venv
.venv/Scripts/activate            # Windows;  source .venv/bin/activate on macOS/Linux
pip install pandas numpy statsmodels scipy matplotlib   # core analysis stack
# (FinBERT sentiment additionally needs transformers + torch; Google/IBKR APIs for data collection)

# Statistical analysis (H1, H2, descriptives, normality) from the response panel:
python 8_statistical_analysis.py

# Regenerate the compiled thesis from thesis.md + results:
python 9_compile_thesis.py
```

The full data-collection pipeline (`1_`–`6_`) requires Interactive Brokers / Google API credentials
in `credentials/` and is not needed to reproduce the analysis from the committed `results/`.

## Documents

The compiled final thesis lives in `documents/` (`thesis_final_v1.3.pdf`, `thesis_final_v1.3.docx`).

## More

- [Research Plan](https://github.com/Amarows/thesis/blob/main/research_plan.md) (root directory)
- [Teams Community](https://teams.live.com/l/community/FEAklGR8GFEnEYwqwQ):
  [Application form](https://1drv.ms/w/c/52025583bffa8bdb/IQBnEGfFxuPHRpdWh0ejZQMBAd0dkjGBlPVfe_yRO_4bvio) ·
  [One pager](https://1drv.ms/w/c/52025583bffa8bdb/IQClC5g0erNsQ69dLNSYJB9rAaOi7Q8epbXjAGOKNwRKaVY)
