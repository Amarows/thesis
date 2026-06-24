# CLAUDE.md – Thesis Project Context

## Project Overview

This repository supports an Executive MBA thesis at Swiss Business School:
**"Reducing Emotional Biases in Investment Portfolio Management"**

The research examines whether external financial information shocks cause systematic shifts in portfolio managers' decision-making, and whether a structured decision-support tool – the Shock Score – can moderate those responses. The thesis bridges behavioural finance theory with operational decision support, moving from explanation to intervention in professional investment contexts.

## Behavioral Guidelines

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## Research Design Summary

- **Design:** Within-subject quasi-experimental using survey scenarios
- **Participants:** Equity portfolio managers with 2+ years of experience (target N = 100, realistic estimate N = 50). Total number of observations will reach (50 respondents) * (8 scenarios) = 400.
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

## H1 Regression
Hypothesis: SC_total is significantly associated with NRS.
Model: Panel OLS with HC3 standard errors. Primary specification regresses NRS on SC_total, ShowSC, experience category dummies, and block fixed effects, plus additional respondent and scenario-level controls.
Robustness: Five specifications – quintile dummies, respondent fixed effects (within estimator), decomposed SC_total components, SC_total × ShowSC interaction, and direction interaction (SC_total × D_neg).
Outputs: results/tables/tbl_h1_main.csv, results/tables/tbl_h1_robustness.csv, results/tables/pca_diagnostics.json

## H2 Portfolio Simulation
Hypothesis: ShowSC moderates the risk-return profile of simulated portfolios.
All constants are defined in config.py. Never redefine them locally in scripts.
Option B (primary): Per respondent × condition, portfolio returns are constructed from NRS-weighted horizon returns. Sharpe and Sortino ratios are computed per respondent-condition pair. A regression of each outcome on ShowSC with experience and block controls tests the treatment effect. HC3 standard errors throughout.
Option A (secondary, descriptive only): Two collective portfolios aggregated across all respondents, one per ShowSC condition. No causal inference – both portfolios draw from the same respondent pool.
Outputs: results/tables/tbl_h2_portfolio.csv, results/figures/fig_sharpe_comparison.png


## Repository Structure

```
thesis/                             # Root directory
├── thesis.md                       # Main thesis text (Markdown, APA style)
├── thesis_final.md                 # Compiled output — DO NOT edit manually
├── references.md                   # Reference list: author, year, link, local filename
├── research_plan.md                # Internal notes — not published
├── config.py                       # Single source of truth for all pipeline constants
├── index.html                      # (purpose TBC)
├── demo.py                         # End-to-end demo
├── README.md                       # Repo readme
│
├── 1_download.py                   # Download prices + news via IBKR to data/
├── 2_prepare_data.py               # Load data/, merge news, coverage stats
├── 3_survey_assembly.py            # Survey asset pipeline → survey/ outputs
├── 4_deploy_google_forms.py        # Create/update Google Forms, upload images
├── 5_append_pilot_feedback.py      # Append Block 1 pilot responses to live forms
├── 6_process_survey_data.py        # Download Google Sheets; parse, normalise, join SC;
│                                   # apply exclusions; write results/analysis_panel.csv
├── 8_statistical_analysis.py       # H1 OLS + robustness, H2 portfolio simulation,
│                                   # descriptives, normality, NRS/sentiment alignment;
│                                   # writes results/thesis_results.md, tables/, figures/
├── 9_compile_thesis.py             # Merges thesis_results.md into thesis.md → thesis_final.md;
│                                   # NEVER modifies thesis.md
│
├── data/                           # Market prices (30-min bars) and Benzinga news CSVs
│   ├── portfolio.csv               # Portfolio holdings
│   └── scenario_manifest.csv       # Single source of truth for scenario selection
│
├── results/                        # All analytical outputs — do not edit manually
│   ├── analysis_panel.csv          # Master response panel
│   ├── analysis_panel_comments.md  # QC report from 6_process_survey_data.py
│   ├── excluded_respondents.csv    # Respondents failing exclusion criteria
│   ├── thesis_results.md           # Auto-generated thesis content (result blocks)
│   ├── pipeline_run_log.jsonl      # Append-only pipeline execution log
│   ├── tables/                     # CSV tables (descriptives, H1, H2, normality)
│   └── figures/                    # PNG figures
│
├── survey/                         # Survey assembly outputs — do not edit manually
│   ├── deployment_manifest.json    # Form IDs for all 6 deployed Google Forms
│   ├── charts/                     # Trailing price chart PNGs
│   ├── dashboards/                 # Shock Score dashboard PNGs
│   ├── metadata/                   # Authoritative per-scenario data (shock scores, news, prices)
│   └── counterbalancing/           # ShowSC assignment matrices and form assembly guide
│
├── diagnostics/                    # QC reports and diagnostic outputs
│
├── protocols/                      # Active QC and operational protocols
│
├── documents/                      # Approval forms and one-pager; not for coding
├── images/                         # SVG and PNG figures used in thesis
├── papers/                         # Local PDF copies of referenced papers
│
├── src_api_ibkr/                   # Interactive Brokers API connector
├── src_api_yahoo/                  # Yahoo Finance fallback connector
├── src_api_google/                 # Google API connector (placeholder)
│
└── toolkits/                       # Data processing and analysis toolkits
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
                                              8_statistical_analysis.py → thesis_results.md
                                                                                    ↓
                                                   9_compile_thesis.py → thesis_final.md
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

**Current placeholder count: 20**

Sections auto-populated: `tbl_4_7_counts`, §5.2.1, §5.2.2, §5.2.3 (PCA diagnostics), §5.3, §5.4, §5.5.1, §5.5.2, §5.6.1, §5.6.1.1 (NRS/sentiment alignment), §5.6.2, §5.7, §5.8, §6.1, §6.2.2, §6.3, §6.4, §6.6, §6.7.1, §6.7.2

## Survey Deployment

- **3 Google Forms** — one per scenario block (Block 1, Block 2, Block 3), 8 scenarios each
- **Counterbalancing:** 2 versions per form (V1 and V2); each scenario appears as treatment (ShowSC = 1) in one version and control (ShowSC = 0) in the other
- **Randomization:** respondents assigned to blocks via timed distribution or random link routing
- **Deployment script:** `4_deploy_google_forms.py` uses Google Forms API v1 + Google Drive API v3; update-or-create pattern preserves form IDs across re-runs
- **Pilot feedback:** `5_append_pilot_feedback.py` appends Block 1 pilot responses to the live form without duplicates
- **Response collection:** `6_process_survey_data.py` downloads Google Sheets linked per form; merges with block/version identifiers and authoritative shock score data

## Coding Conventions

- **Language:** Python 3.x (virtual environment in `.venv`, excluded from repo)
- **IDE:** PyCharm with Git integration
- **Style:** PEP 8; descriptive variable names matching thesis notation (e.g., `sc_total`, `nrs`, `show_sc`)
- **Statistics:** No rounding during computation; final numeric results rounded to 4 decimal places
- **Data files:** CSV for tabular data; naming convention for news: `{TICKER}_BZ_{start}_to_{end}.csv`
- **Thesis text:** Markdown in `thesis.md`; APA citation style. Dashes per APA 7: em dash (—, no spaces) for sentence breaks/separators; en dash (–, no spaces) for ranges and relationships between equals (e.g., risk–return, 165–198); hyphen (-) for compounds. No spaced dashes; never treat a hyphen inside a DOI/ISO date as a range.
- **References:** Managed in `references.md` with local PDF copies in `papers/`
- **Exclusion logic:** applied once, in `6_process_survey_data.py` only; `8_statistical_analysis.py` receives a clean panel and applies no further filtering


## Important Notes

- The thesis follows Swiss Business School's prescriptive handbook structure
- Chapter 4 distinguishes between directly observed survey data (NRS) and model-dependent simulated outcomes (portfolio returns)
- The Shock Score is both: (a) a measurement instrument (independent variable for H1) and (b) a treatment component (the dashboard shown in ShowSC = 1 condition for H2)
- Survey assets in `survey/` are generated outputs — do not edit manually; re-run `3_survey_assembly.py` to regenerate
- Google Forms deployment requires OAuth credentials in `credentials/client_secret.json` (not committed to git)
- `survey/metadata/scenario_shock_score.csv` is the authoritative source for SC_total; `8_statistical_analysis.py` merges it into the panel at runtime, overwriting any stale shock score columns

