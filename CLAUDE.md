# CLAUDE.md – Thesis Project Context

## Project Overview

This repository supports an Executive MBA thesis at Swiss Business School:
**"Reducing Emotional Biases in Investment Portfolio Management"**
*(Research framing: "Influence of External Information Shocks on Equity Portfolio Manager Decision-Making")*

The research examines whether external financial information shocks cause systematic shifts in portfolio managers' decision-making, and whether a structured decision-support tool – the Shock Score – can moderate those responses. The thesis bridges behavioural finance theory with operational decision support, moving from explanation to intervention in professional investment contexts.

## Research Design Summary

- **Design:** Within-subject quasi-experimental using survey scenarios
- **Participants:** Equity portfolio managers with 5+ years of experience (target N = 100)
- **Scenarios:** 8 per manager (4 control, 4 treatment), 2-version (V1/V2) counterbalanced
- **Primary DV:** Net Risk Stance (NRS) – 7-point scale (1 = strongly reduce to 7 = strongly increase exposure)
- **Treatment indicator:** ShowSC (0 = control, 1 = Shock Score dashboard shown)
- **Hypotheses:**
  - H1: SC_total is significantly associated with NRS (panel OLS, HC3 / two-way cluster-robust SEs)
  - H2: ShowSC moderates the risk-return profile of simulated portfolios (Sharpe and Sortino ratios)

## Shock Score (SC_total) – Construction

The composite Shock Score is a PCA-based index constructed from four standardised event-level components:

1. **Article Count (AC_e):** Number of news articles within the shock's 30-minute bar
2. **Sentiment Extremity (SE_e):** Max absolute FinBERT sentiment score within the shock bar
3. **Attention Intensity (AI_e):** 30-minute shock bar volume / 60-trading-day trailing average 30-minute bar volume
4. **Event-Type Severity (ES_e):** Category-level severity ratio (sigma_k / sigma_all), where sigma is computed from 30-minute bar returns

Each component is z-standardised. PCA extracts the first principal component (loading vector w_1). The score is: SC_total_e = w_1' * z_e. Sign convention: higher values = higher shock intensity.

The Shock Score dashboard displays four signals: sentiment direction, shock severity, persistence horizon buckets, and rules-based pre-commitment protocols triggered by shock intensity (Monitor / Review / Halt thresholds at 60th/85th percentiles).

## H2 Portfolio Simulation

Two complementary approaches:

**Option B – Individual portfolios (primary H2 test):**
- Each respondent manages their assigned 4-scenario block per condition
- Weight adjustment: delta_w = (NRS − 4) × 0.02 per scenario
- Horizon-matched returns: Intraday = 1 day, Several Days = 5 days, Several Weeks = 20 trading days
- Sharpe and Sortino ratios annualised via sqrt(252); portfolio returns are raw holding-period returns (not annualised)
- Sortino computed only for respondent-condition pairs with at least one negative return
- H2 regression: Outcome_j = α + τ·ShowSC_j + exp_cat dummies + block FE; HC3 standard errors

**Option A – Collective portfolios (secondary, descriptive only):**
- Two collective portfolios: one per ShowSC condition, drawing from the same respondent pool
- **Non-independence warning:** both portfolios draw from the same respondent pool; no causal inference
- Dollar impact computed at AUM = $100M (raw cumulative return, not annualised)

**Key constants (8_statistical_analysis.py):**

| Constant | Value |
|---|---|
| NRS_NEUTRAL | 4 |
| WEIGHT_STEP | 0.02 |
| RF_ANNUAL | 0.05 |
| HORIZON_DAYS | {"Intraday": 1, "Several Days": 5, "Several Weeks": 20} |
| AUM | 100_000_000 |
| ALPHA | 0.05 |

## Repository Structure

```
thesis/                             # Root directory
├── thesis.md                       # Main thesis text (Markdown, APA style)
├── thesis_final.md                 # Compiled output — DO NOT edit manually
├── research_plan.md                # Internal notes and workflow (not published)
├── references.md                   # Reference list: author, year, link, local filename
├── demo.py                         # End-to-end demo: runs stages 1–5 via subprocess
├── README.md                       # Repo readme
│
│── 1_download.py                   # Live IBKR connectors: download prices + news to data/
├── 2_prepare_data.py               # Load data/, merge news, coverage stats, price chart
├── 3_survey_assembly.py            # Survey asset pipeline: orchestrates toolkits → survey/ outputs
├── 4_deploy_google_forms.py        # Google Forms API: create/update forms, upload images, manage IDs
├── 5_append_pilot_feedback.py      # Append Block 1 pilot responses to Google Forms
├── 6_process_survey_data.py        # Download Google Sheets; parse, normalise, join metadata + SC;
│                                   # apply exclusions; write results/analysis_panel.csv + _comments.md
├── 7_augment_data.py               # TEMPORARY: inflate real response count to target N (default 60);
│                                   # draws demographics from realistic population distributions;
│                                   # adds calibrated NRS noise; overwrites analysis_panel.csv in place;
│                                   # --target-respondents 0 disables; delete when real N >= target
├── 8_statistical_analysis.py       # Full analysis pipeline (reads files only, no upstream calls);
│                                   # descriptives, normality, H1 OLS (primary + 4 robustness specs),
│                                   # H2 Option B + A portfolio simulation, NRS/sentiment alignment;
│                                   # writes results/thesis_results.md, tables/*.csv, figures/*.png
├── 9_compile_thesis.py             # Merges thesis_results.md into thesis.md via placeholder markers;
│                                   # writes thesis_final.md; optional Pandoc → documents/thesis_final.docx;
│                                   # NEVER modifies thesis.md
│
├── data/                           # Portfolio data, market data, news files (per month)
│   ├── portfolio.csv               # Portfolio holdings (39 stocks)
│   ├── scenario_manifest.csv       # Single source of truth for scenario selection
│   ├── *_30min_360D.csv            # Intraday price data (30-minute bars, 360 days)
│   └── *_BZ_YYYY-MM-*.csv         # Benzinga news data per ticker per month
│
├── results/                        # Analytical outputs (generated — do not edit manually)
│   ├── analysis_panel.csv          # Master response panel (real + synthetic respondents)
│   ├── analysis_panel_comments.md  # QC and run report from 6_process_survey_data.py
│   ├── excluded_respondents.csv    # Respondents failing exclusion criteria
│   ├── thesis_results.md           # Auto-generated thesis content (14 result blocks)
│   ├── tables/                     # Machine-readable CSV tables
│   │   ├── tbl_descriptive_respondents.csv
│   │   ├── tbl_descriptive_respondents_freq.csv
│   │   ├── tbl_descriptive_nrs.csv
│   │   ├── tbl_descriptive_scenarios.csv
│   │   ├── tbl_normality.csv
│   │   ├── tbl_h1_main.csv
│   │   ├── tbl_h1_robustness.csv
│   │   ├── tbl_h2_portfolio.csv
│   │   ├── tbl_data_sufficiency.csv
│   │   └── tbl_nrs_sentiment_alignment.csv
│   └── figures/                    # PNG figures (generated by 8_statistical_analysis.py)
│       ├── fig_demographics.png
│       ├── fig_nrs_distribution.png
│       ├── fig_nrs_by_condition.png
│       ├── fig_sc_distribution.png
│       └── fig_sharpe_comparison.png
│
├── diagnostics/                    # Quality checks and diagnostic outputs
│   ├── chapter2_citation_inventory.md
│   ├── deep-research-report.md
│   ├── references_age_report.md
│   ├── survey_assembly_report.md   # Assembly QC report (generated by 3_survey_assembly.py)
│   └── task1_blueprint.md          # Task planning document
│
├── documents/                      # Formal documents (Word, PDF); not for coding
│   ├── thesis.docx                 # Word version of thesis
│   └── *.doc, *.docx, *.pdf       # Approval forms, templates, one-pager
│
├── images/                         # All images (thesis figures, diagrams)
│   ├── img_casual_logic.svg        # Causal logic diagram
│   ├── img_framework.svg           # Conceptual framework figure
│   └── img_shock_example.png       # Example shock visualisation
│
├── papers/                         # Local copies of referenced papers (PDF)
│   └── *.pdf                       # Named by author/year or SSRN ID
│
├── protocols/                      # Research and operational protocols
│   ├── scenario_selection_protocol.md  # 2-stage scenario screening rules + balance constraints
│   ├── presentation_protocol.md        # Mentor meeting presentation guide
│   ├── 1_quality_review.md             # Diagnostic tests for thesis quality (B1–B8, C1–C4)
│   └── 2_master_revision.md            # Revision rules and hard constraints
│
├── survey/                         # Survey assembly outputs (generated by 3_survey_assembly.py)
│   ├── charts/                     # Trailing price chart PNGs (pre-event window)
│   ├── dashboards/                 # Shock Score dashboard PNGs
│   ├── metadata/                   # Per-scenario authoritative data tables
│   │   ├── scenario_metadata.csv       # Event metadata for all 24 scenarios
│   │   ├── scenario_shock_score.csv    # Authoritative SC_total and components (all 24 scenarios)
│   │   ├── scenario_news_text.csv      # Scenario news headline text
│   │   └── scenario_price_reaction.csv # 2-hour post-event price snapshot
│   └── counterbalancing/           # Counterbalancing assignment tables
│       ├── counterbalancing_matrix.csv # ShowSC ground truth per respondent × scenario
│       └── form_assembly_guide.csv     # Form assembly reference
│
├── src_api_google/                 # Google API connector (currently empty placeholder)
│
├── src_api_ibkr/                   # Interactive Brokers API connector
│   ├── ibkr_tws_api.py             # TWS API connection layer
│   ├── ibkr_webapi.py              # Web API connection layer
│   ├── ibkr_news_toolkit.py        # News retrieval (Benzinga via IB)
│   └── historical_data_toolkit.py  # Historical market data retrieval
│
├── src_api_yahoo/                  # Yahoo Finance API connector
│   └── market_data_toolkit.py      # Market data retrieval via Yahoo
│
└── toolkits/                       # Data processing and analysis toolkits
    ├── service_functions.py              # Utility functions: word count, reference analysis, MD→DOCX
    ├── data_aggregation_toolkit.py       # Google Sheets auth, tab download, response parsing,
    │                                     # exclusion logic, metadata merging, QC report generation
    ├── market_data_processor_toolkit.py  # Market data cleaning and transformation
    ├── news_sentiment_toolkit.py         # FinBERT sentiment scoring pipeline
    ├── event_selection_toolkit.py        # 3-stage shock identification; SC raw components, PCA, CAR
    ├── visualization_toolkit.py          # Bloomberg-style price charts + Shock Score dashboard PNGs
    ├── news_processor_toolkit.py         # FinBERT init, headline selection, Claude API summaries
    └── survey_design_toolkit.py          # Latin square design, manifest population, QC report
```

## Data Pipeline

```
Benzinga (via IB API) → Raw news JSON → news_sentiment_toolkit.py (FinBERT) → Scored articles
                                                                                    ↓
Yahoo / IB Historical → Market prices → market_data_processor_toolkit.py → Aligned market data
                                                                                    ↓
                                                            PCA construction → SC_total per event
                                                                                    ↓
                     Survey (Google Forms) → Google Sheets → 6_process_survey_data.py
                                                                                    ↓
                                                 7_augment_data.py (if real N < target)
                                                                                    ↓
                                              8_statistical_analysis.py → thesis_results.md
                                                                                    ↓
                                                   9_compile_thesis.py → thesis_final.md
```

## Refresh Cycle (when new survey responses arrive)

```
1. python 6_process_survey_data.py      # download and process responses
2. python 7_augment_data.py             # augment if real N < 60; skip otherwise
3. python 8_statistical_analysis.py    # recompute all analysis → thesis_results.md
4. python 9_compile_thesis.py           # compile → thesis_final.md

Disable augmentation: python 7_augment_data.py --target-respondents 0
Skip figures in step 3: python 8_statistical_analysis.py --skip-figures
```

No manual writing of numbers or results is required. Only `thesis.md` structure and prose are edited by hand.

## CRITICAL EDITING RULE

> **All edits to thesis text — by any person or AI — must be made to `thesis.md` ONLY.**
> `thesis_final.md` is generated output. Never edit it directly.
> It is always regenerated by running `9_compile_thesis.py`.
> Any direct edit to `thesis_final.md` will be silently overwritten on the next pipeline run.

## Thesis Compilation Architecture

`thesis.md` uses machine-readable placeholder markers:
```
<!-- PLACEHOLDER:section_id -->
[To be populated by 8_statistical_analysis.py]
<!-- /PLACEHOLDER:section_id -->
```

`results/thesis_results.md` contains matching result blocks:
```
<!-- RESULTS:BEGIN:section_id -->
[auto-generated content]
<!-- RESULTS:END:section_id -->
```

`9_compile_thesis.py` replaces each placeholder with the corresponding result block. `thesis.md` is **never** manually edited for numbers or results. `thesis_final.md` is the compiled output — never edit manually.

**Current placeholder count: 14**

Sections auto-populated: §5.2.1, §5.2.2, §5.3, §5.4, §5.5.1, §5.5.2, §5.6.1, §5.6.1.1 (NRS/sentiment alignment diagnostic), §5.6.2, §5.7, §5.8, §6.2.2, §6.3, §6.4

## Survey Deployment

- **3 Google Forms** — one per scenario block (Block 1, Block 2, Block 3), 8 scenarios each
- **Counterbalancing:** 2 versions per form (V1 and V2); each scenario appears as treatment (ShowSC = 1) in one version and control (ShowSC = 0) in the other
- **Randomization:** respondents assigned to blocks via timed distribution or random link routing
- **Image hosting:** chart and dashboard PNGs hosted on Google Drive (public read); referenced by direct URL in Forms API
- **Deployment script:** `4_deploy_google_forms.py` uses Google Forms API v1 + Google Drive API v3; update-or-create pattern preserves form IDs across re-runs
- **Pilot feedback:** `5_append_pilot_feedback.py` appends Block 1 pilot responses to the live form without duplicates
- **Response collection:** `6_process_survey_data.py` downloads Google Sheets linked per form; merges with block/version identifiers and authoritative shock score data

## Coding Conventions

- **Language:** Python 3.x (virtual environment in `.venv`, excluded from repo)
- **IDE:** PyCharm with Git integration
- **Style:** PEP 8; descriptive variable names matching thesis notation (e.g., `sc_total`, `nrs`, `show_sc`)
- **Statistics:** No rounding during computation; final numeric results rounded to 4 decimal places
- **Data files:** CSV for tabular data; naming convention for news: `{TICKER}_BZ_{start}_to_{end}.csv`
- **Thesis text:** Markdown in `thesis.md`; APA citation style; en dash with spaces ( – ) for punctuation
- **References:** Managed in `references.md` with local PDF copies in `papers/`
- **Exclusion logic:** applied once, in `6_process_survey_data.py` only; `8_statistical_analysis.py` receives a clean panel and applies no further filtering

## Key Academic References

- Tetlock (2007) – Media content predicts market activity
- Bhandari and Hassanein (2008) – Information shocks framework
- Kahneman and Tversky (1979) – Prospect theory
- Lo (2002, 2005) – Adaptive markets hypothesis
- Cameron, Gelbach, and Miller (2011) – Multi-way clustering
- Petersen (2009) – Panel finance data, clustered standard errors

## Important Notes

- The thesis follows Swiss Business School's prescriptive handbook structure
- Chapter 4 distinguishes between directly observed survey data (NRS) and model-dependent simulated outcomes (portfolio returns)
- The Shock Score is both: (a) a measurement instrument (independent variable for H1) and (b) a treatment component (the dashboard shown in ShowSC = 1 condition for H2)
- All statistical inference uses Johnston and DiNardo's Econometric Methods as methodological authority where applicable
- Survey assets in `survey/` are generated outputs — do not edit manually; re-run `3_survey_assembly.py` to regenerate
- Assembly QC report is written to `diagnostics/survey_assembly_report.md` (not inside `survey/`)
- Google Forms deployment requires OAuth credentials in `credentials/client_secret.json` (not committed to git)
- Chart and dashboard images must be uploaded to Google Drive before form creation (the deploy script handles this)
- `survey/metadata/scenario_shock_score.csv` is the authoritative source for SC_total; `8_statistical_analysis.py` merges it into the panel at runtime, overwriting any stale shock score columns

## Known Technical Debt

Open GitHub issues — do not address in Claude Code sessions without explicit instruction:

- **#112** – H2 methodology description in `thesis.md` not yet updated (portfolio simulation uses horizon-matched returns, Option A/B architecture)
- **#113** – Parameters scattered across scripts; centralise into `config.py`
- **#114** – No global pipeline run log; implement append-only run log
