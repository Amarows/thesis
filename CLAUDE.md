# CLAUDE.md – Thesis Project Context

## Project Overview

This repository supports an Executive MBA thesis at Swiss Business School:
**"Influence of External Information Shocks on Equity Portfolio Manager Decision-Making"**

The research examines whether external financial information shocks cause systematic shifts in portfolio managers' decision-making, and whether a structured decision-support tool – the Shock Score – can moderate those responses. The thesis bridges behavioral finance theory with operational decision support, moving from explanation to intervention in professional investment contexts.

## Research Design Summary

- **Design:** Within-subject quasi-experimental using survey scenarios
- **Participants:** Equity portfolio managers with 5+ years of experience (target N = 100)
- **Scenarios:** 12 per manager (6 control, 6 treatment), Latin square counterbalanced
- **Primary DV:** Net Risk Stance (NRS) – 7-point scale (1 = strongly reduce to 7 = strongly increase exposure)
- **Treatment indicator:** ShowSC (0 = control, 1 = Shock Score dashboard shown)
- **Hypotheses:**
  - H1: SC_total is significantly associated with NRS (panel regression with two-way cluster-robust SEs)
  - H2: ShowSC moderates the risk-return profile of simulated portfolios (Sharpe and Sortino ratios)

## Shock Score (SC_total) – Construction

The composite Shock Score is a PCA-based index constructed from four standardised event-level components:

1. **Article Count (AC_e):** Number of news articles within the shock's 30-minute bar
2. **Sentiment Extremity (SE_e):** Max absolute FinBERT sentiment score within the shock bar
3. **Attention Intensity (AI_e):** 30-minute shock bar volume / 60-trading-day trailing average 30-minute bar volume
4. **Event-Type Severity (ES_e):** Category-level severity ratio (sigma_k / sigma_all), where sigma is computed from 30-minute bar returns

Each component is z-standardised. PCA extracts the first principal component (loading vector w_1). The score is: SC_total_e = w_1' * z_e. Sign convention: higher values = higher shock intensity.

The Shock Score dashboard displays four signals: sentiment direction, shock severity, persistence horizon buckets, and rules-based pre-commitment protocols triggered by shock intensity (Monitor / Review / Halt thresholds at 60th/85th percentiles).

## Portfolio Simulation

- NRS responses are translated to weight adjustments: step = 2 percentage points per NRS unit from neutral (NRS = 4)
- Equal-weight (1/N) baseline portfolio
- 20-day evaluation window per event
- Sharpe ratio: (R_p - R_f) / sigma_p, annualised with sqrt(252); R_f = 3-month US T-bill
- Sortino ratio: (R_p - MAR) / sigma_downside; MAR = R_f

## Repository Structure

```
thesis/                         # Root directory
├── thesis.md                   # Main thesis text (Markdown)
├── research_plan.md            # Internal notes, ideas, workflow (not published)
├── references.md               # Reference list: author, year, link, local filename
├── 1_download.py               # Live IBKR connectors: download prices + news to data/
├── 2_prepare.py                # Load data/, merge news, coverage stats, price chart
├── 3_survey_assembly.py        # Survey asset pipeline: charts, dashboards, SC_total, counterbalancing
├── 4_deploy_google_forms.py    # Google Forms API: programmatic form creation and image upload (future)
├── 5_analysis.py               # SC_total construction, H1/H2 regressions (future)
├── 6_report.py                 # Thesis-ready tables and figures (future)
├── drafts.py                   # Scratch/draft code
├── README.md                   # Repo readme
├── repo_tree.txt               # Generated directory listing
│
├── data/                       # Portfolio data, market data, news files (per month)
│   ├── portfolio.csv           # Portfolio holdings
│   ├── *_30min_90D.csv         # Intraday price data (30-minute bars, 90 days)
│   └── *_BZ_YYYY-MM-*.csv     # Benzinga news data per ticker per month
│
├── diagnostics/                # Quality checks and diagnostic results for thesis text
│   ├── 1_quality_review.md
│   ├── 2_master_revision.md
│   ├── chapter2_citation_inventory.md
│   ├── deep-research-report.md
│   ├── references_age.xlsx
│   └── references_age_report.md
│
├── documents/                  # Formal documents (Word, PDF); not for coding
│   ├── thesis.docx             # Word version of thesis
│   └── *.doc, *.docx, *.pdf   # Approval forms, templates, one-pager
│
├── images/                     # All images (thesis figures, diagrams)
│   ├── img_casual_logic.svg    # Causal logic diagram
│   ├── img_framework.svg       # Conceptual framework figure
│   └── img_shock_example.png   # Example shock visualisation
│
├── papers/                     # Local copies of referenced papers (PDF)
│   └── *.pdf                   # Named by author/year or SSRN ID
│
├── protocols/                  # Research and operational protocols
│   ├── scenario_selection_protocol.md   # 2-stage screening, balance constraints
│   └── presentation_protocol.md        # Mentor meeting presentation guide
├── survey/                     # Survey assembly outputs (generated by 3_survey_assembly.py)
│   ├── metadata/
│   │   ├── scenario_metadata.csv          # Scenario master table
│   │   ├── scenario_news_text.csv         # Headlines and summary paragraphs
│   │   ├── scenario_price_reaction.csv    # Immediate price reactions
│   │   └── scenario_shock_score.csv       # SC_total and 4 dashboard signals
│   ├── charts/                            # trailing price chart PNGs
│   ├── dashboards/                        # Shock Score dashboard PNGs
│   ├── counterbalancing/
│   │   ├── counterbalancing_matrix.csv    # Latin square treatment assignment
│   │   └── form_assembly_guide.csv        # Per-block scenario order + show_sc flag
│   └── survey_assembly_report.md          # Assembly QC report
├── src_api_ibkr/               # Interactive Brokers API connector
│   ├── ibkr_tws_api.py        # TWS API connection layer
│   ├── ibkr_webapi.py         # Web API connection layer
│   ├── ibkr_news_toolkit.py   # News retrieval (Benzinga via IB)
│   └── historical_data_toolkit.py  # Historical market data retrieval
│
├── src_api_yahoo/              # Yahoo Finance API connector
│   └── market_data_toolkit.py  # Market data retrieval via Yahoo
│
└── toolkits/                   # Data processing and analysis toolkits
    ├── service_functions.py              # Utility functions: word count, reference analysis, MD→DOCX, bibliography XML
    ├── market_data_processor_toolkit.py  # Market data cleaning and transformation
    └── news_sentiment_toolkit.py         # FinBERT sentiment scoring pipeline
```

## Data Pipeline

```
Benzinga (via IB API) → Raw news JSON → news_sentiment_toolkit.py (FinBERT) → Scored articles
                                                                                    ↓
Yahoo / IB Historical → Market prices → market_data_processor_toolkit.py → Aligned market data
                                                                                    ↓
                                                            PCA construction → SC_total per event
                                                                                    ↓
                                                          Survey scenarios → NRS responses (primary data)
                                                                                    ↓
                                                     Portfolio simulation → Sharpe / Sortino (H2 outcomes)
```
## Survey Deployment

- **3 Google Forms** -- one per scenario block (Block 1, Block 2, Block 3), 12 scenarios each
- **Counterbalancing**: 2 sub-blocks per form (A/B); each scenario appears as treatment for ~50% of respondents
- **Randomization**: respondents assigned to blocks via timed distribution or random link routing
- **Image hosting**: chart and dashboard PNGs hosted on Google Drive (public read); referenced by direct URL in Forms API
- **Deployment script**: `4_deploy_google_forms.py` uses Google Forms API v1 + Google Drive API v3
- **Response collection**: Google Sheets linked per form; merged post-collection with block/sub-block identifiers

## Coding Conventions

- **Language:** Python 3.x (virtual environment in .venv, excluded from repo)
- **IDE:** PyCharm with Git integration
- **Style:** PEP 8; descriptive variable names matching thesis notation (e.g., `sc_total`, `nrs`, `show_sc`)
- **Statistics:** No rounding during computation; final numeric results rounded to 4 decimal places
- **Data files:** CSV for tabular data; naming convention for news: `{TICKER}_BZ_{start}_to_{end}.csv`
- **Thesis text:** Markdown in `thesis.md`; APA citation style; en dash with spaces ( – ) for punctuation
- **References:** Managed in `references.md` with local PDF copies in `papers/`

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
- Survey assets in `survey/` are generated outputs -- do not edit manually; re-run `3_survey_assembly.py` to regenerate
- Google Forms deployment requires OAuth credentials in `credentials/client_secret.json` (not committed to git)
- Chart and dashboard images must be uploaded to Google Drive before form creation (the deploy script handles this)orm; merged post-collection with block/sub-block identifiers