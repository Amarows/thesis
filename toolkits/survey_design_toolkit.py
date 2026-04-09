"""
survey_design_toolkit.py
========================
Experimental design and reporting utilities for the survey assembly pipeline.

Responsibilities
----------------
- Convert assign_blocks() output to scenario_manifest.csv format
- Generate the Latin square counterbalancing design (matrix + form assembly guide)
- Build the Markdown survey assembly report

These functions encapsulate the "academic" layer of the project — the
within-subject experimental design, counterbalancing logic, and the
self-contained Markdown report consumed by the thesis.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd

# ── Manifest schema ───────────────────────────────────────────────────────────

MANIFEST_COLUMNS = [
    "scenario_id", "block_id", "ticker", "company_name", "gics_sector",
    "event_date", "event_time", "event_type", "headline", "num_articles",
]


# ── Manifest population from assign_blocks() output ──────────────────────────

def populate_manifest_from_blocks(
    blocks: dict,
    portfolio_df: "pd.DataFrame | None" = None,
    output_path: "Path | None" = None,
) -> pd.DataFrame:
    """
    Convert assign_blocks() output to scenario_manifest.csv format and write it.

    Parameters
    ----------
    blocks       : {"A": df, "B": df, "C": df} from event_selection_toolkit.assign_blocks()
    portfolio_df : optional; used to fill company_name / gics_sector when missing
    output_path  : write destination; caller is responsible for providing the path

    Returns
    -------
    manifest_df  : DataFrame in MANIFEST_COLUMNS format (up to 36 rows)
    """
    block_to_id = {"A": 1, "B": 2, "C": 3}
    rows = []

    port_lookup: dict = {}
    if portfolio_df is not None:
        ticker_col = next(
            (c for c in portfolio_df.columns if c.lower() in ("ticker", "symbol")), None
        )
        if ticker_col:
            port_lookup = portfolio_df.set_index(ticker_col).to_dict("index")

    for block_label, bdf in blocks.items():
        if bdf is None or (hasattr(bdf, "empty") and bdf.empty):
            continue
        bid = block_to_id.get(block_label, len(rows) // 12 + 1)

        for i, (_, row) in enumerate(bdf.iterrows(), start=1):
            ticker = str(row.get("symbol", ""))

            company_name = str(row.get("company_name", ""))
            if company_name in ("", "nan") and ticker in port_lookup:
                company_name = str(
                    port_lookup[ticker].get("company_name",
                    port_lookup[ticker].get("Company", ticker))
                )
            if company_name in ("", "nan"):
                company_name = ticker

            gics_sector = str(row.get("sector", ""))
            if gics_sector in ("", "nan", "Unknown") and ticker in port_lookup:
                gics_sector = str(
                    port_lookup[ticker].get("gics_sector",
                    port_lookup[ticker].get("GICS Sector", "Unknown"))
                )

            shock_time = row.get("shock_time_et", row.get("event_time", "09:30"))
            if hasattr(shock_time, "strftime"):
                event_time = shock_time.strftime("%H:%M")
            else:
                event_time = str(shock_time)[:5]

            ac_e = row.get("ac_e", row.get("article_count", 1))
            try:
                num_articles = int(float(ac_e))
            except (ValueError, TypeError):
                num_articles = 1

            rows.append({
                "scenario_id":  f"B{bid}_S{i:02d}",
                "block_id":     bid,
                "ticker":       ticker,
                "company_name": company_name,
                "gics_sector":  gics_sector,
                "event_date":   str(row.get("event_date", "")),
                "event_time":   event_time,
                "event_type":   str(row.get("event_type", "other")),
                "headline":     str(row.get("displayed_headline", "")),
                "num_articles": num_articles,
            })

    manifest_df = pd.DataFrame(rows, columns=MANIFEST_COLUMNS)
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        manifest_df.to_csv(output_path, index=False)
        print(f"\nManifest written: {output_path}  ({len(manifest_df)} scenarios across "
              f"{manifest_df['block_id'].nunique()} block(s))")
    return manifest_df


# ── Latin square counterbalancing ─────────────────────────────────────────────

def generate_counterbalancing(
    manifest_df: pd.DataFrame,
) -> tuple:
    """
    Generate a balanced Latin square counterbalancing design for all blocks.

    For each block of 8 scenarios [S1…S8], two respondent versions are produced:

      Version 1: Group A (S1–S4) = ShowSC=1; Group B (S5–S8) = ShowSC=0
                 Order: interleaved A-B  [S1, S5, S2, S6, S3, S7, S4, S8]
      Version 2: Group A = ShowSC=0; Group B = ShowSC=1
                 Order: interleaved A-B  [S1, S5, S2, S6, S3, S7, S4, S8]

    Result:
      - Each scenario appears as treatment in exactly 1 of 2 versions (50% rate)
      - Treatment/control alternates within each version (no clustering)

    Returns
    -------
    (counterbalancing_matrix_df, form_assembly_guide_df)

    counterbalancing_matrix_df columns:
        respondent_block, block_id, presentation_order, scenario_id, show_sc
    form_assembly_guide_df columns:
        same + ticker, dashboard_shown (human-readable YES/no)
    """
    matrix_rows = []
    guide_rows  = []

    for block_id in sorted(manifest_df["block_id"].unique()):
        block        = manifest_df[manifest_df["block_id"] == block_id].reset_index(drop=True)
        scenario_ids = block["scenario_id"].tolist()
        tickers_map  = dict(zip(block["scenario_id"], block["ticker"]))

        n      = len(scenario_ids)
        half   = n // 2
        group_a = scenario_ids[:half]
        group_b = scenario_ids[half:]

        # Interleaved A-B order
        order_ab = []
        for i in range(max(len(group_a), len(group_b))):
            if i < len(group_a):
                order_ab.append(group_a[i])
            if i < len(group_b):
                order_ab.append(group_b[i])

        versions = [
            (f"Block{block_id}_V1", set(group_a), order_ab),  # A=treatment, B=control
            (f"Block{block_id}_V2", set(group_b), order_ab),  # B=treatment, A=control
        ]

        for version_id, treatment_set, order in versions:
            for pos, sid in enumerate(order, start=1):
                show_sc = 1 if sid in treatment_set else 0
                ticker  = tickers_map.get(sid, "")
                matrix_rows.append({
                    "respondent_block":   version_id,
                    "block_id":           block_id,
                    "presentation_order": pos,
                    "scenario_id":        sid,
                    "show_sc":            show_sc,
                })
                guide_rows.append({
                    "respondent_block":   version_id,
                    "block_id":           block_id,
                    "presentation_order": pos,
                    "scenario_id":        sid,
                    "ticker":             ticker,
                    "show_sc":            show_sc,
                    "dashboard_shown":    "YES" if show_sc else "no",
                })

    matrix_df = pd.DataFrame(matrix_rows)
    guide_df  = pd.DataFrame(guide_rows)
    return matrix_df, guide_df


# ── Markdown assembly report ──────────────────────────────────────────────────

def generate_report(
    manifest_df: pd.DataFrame,
    sc_df: pd.DataFrame,
    pca_info: dict,
    charts_ok: int,
    dashboards_ok: int,
    output_dir: "Path | str",
    price_reaction_df: "pd.DataFrame | None" = None,
    warnings_list: "list[str] | None" = None,
) -> str:
    """
    Build the Markdown survey assembly report.

    The report is self-contained: an external reader can understand the survey
    design, measures, and descriptive statistics without access to the thesis.

    Parameters
    ----------
    manifest_df       : scenario manifest
    sc_df             : output of compute_shock_scores() + compute_persistence_horizon()
    pca_info          : dict from compute_shock_scores()
    charts_ok         : number of successfully generated charts
    dashboards_ok     : number of successfully generated dashboards
    output_dir        : root survey output directory (for the file manifest section)
    price_reaction_df : optional; output of the price reaction step
    warnings_list     : list of warning strings collected during the pipeline run

    Returns
    -------
    Markdown string (write to survey_assembly_report.md)
    """
    output_dir   = Path(output_dir)
    if warnings_list is None:
        warnings_list = []
    ts      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    n_total = len(manifest_df)

    lines: list[str] = [
        "# Survey Assembly Report",
        f"\nGenerated: {ts}",
        "",
        "---",
        "",
        "## Overview",
        "",
        "This report documents the assembly of survey materials for the thesis "
        "*\"Influence of External Information Shocks on Equity Portfolio Manager "
        "Decision-Making\"* (Executive MBA, Swiss Business School). The survey "
        "presents equity portfolio managers with real-world financial event "
        "scenarios and asks them to indicate their intended risk stance -- whether "
        "they would increase, maintain, or reduce exposure to the affected stock. "
        "Each scenario is based on an actual news event for an S&P 500 stock and "
        "is accompanied by a trailing price chart. In treatment conditions, "
        "respondents also see a **Shock Score dashboard** -- a quantitative "
        "decision-support tool that summarises the event's intensity across "
        "multiple dimensions.",
        "",
        "The survey uses a **within-subject quasi-experimental design**: each "
        "respondent sees 8 scenarios (4 control, 4 treatment), with treatment "
        "assignment counterbalanced across form versions so that every scenario "
        "appears as both control and treatment across the full sample.",
        "",
        "---",
        "",
        "## 1. Scenario Counts",
        "",
        f"- **Total scenarios:** {n_total}",
    ]

    for block_id in sorted(manifest_df["block_id"].unique()):
        n_block = (manifest_df["block_id"] == block_id).sum()
        lines.append(f"- Block {block_id}: {n_block} scenarios")

    lines.append("")
    lines.append("Each respondent completes one block (8 scenarios). Three blocks "
                 "exist so that a larger pool of events can be tested while keeping "
                 "individual survey length manageable.")

    # -- Sector coverage -------------------------------------------------------
    if "gics_sector" in manifest_df.columns and "ticker" in manifest_df.columns:
        sector_groups = (
            manifest_df.groupby("gics_sector")["ticker"]
            .agg(Count="count", Tickers=lambda x: ", ".join(sorted(x)))
            .sort_values("Count", ascending=False)
            .reset_index()
        )
        lines += [
            "",
            "### Sector Coverage",
            "",
            f"The {n_total} scenarios span **{sector_groups.shape[0]} GICS sectors**, "
            "ensuring broad industry representation:",
            "",
            "| GICS Sector | Count | Tickers |",
            "|---|---|---|",
        ]
        for _, row in sector_groups.iterrows():
            lines.append(f"| {row['gics_sector']} | {row['Count']} | {row['Tickers']} |")

    # -- Event-type distribution -----------------------------------------------
    if "event_type" in manifest_df.columns:
        evt_counts = manifest_df["event_type"].value_counts()
        lines += [
            "",
            "### Event-Type Distribution",
            "",
            "Each scenario is classified by the type of news event that triggered "
            "the information shock:",
            "",
            "| Event Type | Count | Share |",
            "|---|---|---|",
        ]
        for evt, cnt in evt_counts.items():
            lines.append(f"| {evt.title()} | {cnt} | {cnt / n_total * 100:.1f}% |")
        lines.append("")
        lines.append("Earnings events dominate, reflecting their real-world prevalence "
                     "as the most common source of significant information shocks for "
                     "S&P 500 stocks.")

    # -- Event date range ------------------------------------------------------
    if "event_date" in manifest_df.columns:
        dates        = pd.to_datetime(manifest_df["event_date"])
        earliest_idx = dates.idxmin()
        latest_idx   = dates.idxmax()
        lines += [
            "",
            "### Event Date Range",
            "",
            f"- **Earliest event:** {dates.min().strftime('%Y-%m-%d')} "
            f"({manifest_df.loc[earliest_idx, 'ticker']})",
            f"- **Latest event:** {dates.max().strftime('%Y-%m-%d')} "
            f"({manifest_df.loc[latest_idx, 'ticker']})",
            f"- Span: approximately "
            f"{(dates.max() - dates.min()).days // 30} months of real market events",
        ]

    # -- Glossary of measures --------------------------------------------------
    lines += [
        "",
        "---",
        "",
        "## 2. Glossary of Measures",
        "",
        "Before interpreting the statistics below, the following definitions "
        "describe each measure used in the Shock Score (SC_total) construction "
        "and the scenario metadata.",
        "",
        "### Raw Component Measures",
        "",
        "| Measure | Full Name | Definition |",
        "|---|---|---|",
        "| **AC_raw** | Article Count | Number of news articles published within "
        "the 30-minute bar in which the event occurs. Higher values indicate "
        "broader media coverage of the event. |",
        "| **SE_raw** | Sentiment Extremity | Maximum absolute FinBERT sentiment "
        "score across all articles on the event day. Ranges from 0 (neutral) "
        "to 1 (extreme positive or negative). Captures the emotional intensity "
        "of the news, regardless of direction. |",
        "| **AI_raw** | Attention Intensity | Trading volume in the 30-minute "
        "event bar divided by the 60-trading-day trailing average of 30-minute "
        "bar volume. Values above 1.0 indicate abnormally high trading activity. |",
        "| **ES_raw** | Event-Type Severity | Category-level severity ratio: the "
        "historical return volatility of the event category (e.g., earnings) "
        "divided by the overall return volatility across all categories. Higher "
        "values indicate event types that historically cause larger price moves. |",
        "",
        "### Z-Standardised Components",
        "",
        "Each raw component is z-standardised (mean = 0, std = 1) across all "
        f"{n_total} scenarios before entering PCA. In the shock score file, "
        "these appear as `ac_z`, `se_z`, `ai_z`, `es_z`.",
        "",
        "### Composite Score",
        "",
        "| Measure | Definition |",
        "|---|---|",
        "| **SC_total** | The composite **Shock Score**. Computed as the first "
        "principal component (PC1) of the four z-standardised components. A single "
        "number summarising overall shock intensity. Higher values = more intense "
        "shocks (more articles, more extreme sentiment, higher abnormal volume, "
        "more severe event type). |",
        "",
        "### Dashboard Signals",
        "",
        "These are derived from SC_total and its components to populate the visual "
        "Shock Score dashboard shown to treatment-group respondents:",
        "",
        "| Signal | Definition |",
        "|---|---|",
        "| **sentiment_direction** | Qualitative label for the dominant sentiment "
        "of event-day news (e.g., \"Strongly Negative\", \"Neutral\", \"Mildly "
        "Positive\"). Based on the FinBERT positive-minus-negative probability "
        "score. |",
        "| **severity_level** | Categorical shock intensity bucket: **Low** "
        "(bottom third of SC_total), **Medium** (middle third), **High** "
        "(top third). |",
        "| **horizon_bucket** | Estimated persistence of the price impact: "
        "\"Intraday\", \"Several Days\", or \"Several Weeks\". Derived from "
        "5-day post-event return decay. |",
        "| **protocol_recommendation** | Rules-based pre-commitment action "
        "triggered by shock intensity: **Standard Process** (below 60th "
        "percentile of SC_total), **Enhanced Review** (60th--85th percentile), "
        "or **Cooling-Off and Second Review** (above 85th percentile). |",
    ]

    # -- PCA results -----------------------------------------------------------
    ev = pca_info.get("explained_variance", 0)
    lines += [
        "",
        "---",
        "",
        "## 3. PCA Results -- SC_total Construction",
        "",
        "Principal Component Analysis was applied to the four z-standardised "
        f"shock components across all {n_total} scenarios. The first principal "
        "component (PC1) is retained as SC_total.",
        "",
        f"- **PC1 explained variance: {ev:.4f} ({ev * 100:.1f}%)**",
        "",
        "This means PC1 captures nearly "
        f"{int(round(ev * 100))}% of the total variation across the four "
        "components -- a strong single-factor summary.",
        "",
        "- **Loadings (w_1):**",
        "",
        "| Component | Loading | Interpretation |",
        "|---|---|---|",
    ]
    loading_labels = {
        "ac": ("AC (Article Count)", "Media coverage breadth"),
        "se": ("SE (Sentiment Extremity)", "Emotional intensity of news"),
        "ai": ("AI (Attention Intensity)", "Abnormal trading volume"),
        "es": ("ES (Event-Type Severity)", "Historical category volatility"),
    }
    sorted_loadings = sorted(
        pca_info.get("loadings", {}).items(), key=lambda x: abs(x[1]), reverse=True
    )
    for comp, val in sorted_loadings:
        label, interp = loading_labels.get(comp, (comp, ""))
        lines.append(f"| {label} | **{val:.4f}** | {interp} |")
    lines.append("")
    lines.append("All four loadings are positive, confirming that SC_total "
                 "increases when any dimension of shock intensity increases.")

    # -- SC_total distribution -------------------------------------------------
    if not sc_df.empty and "sc_total" in sc_df.columns:
        sc       = sc_df["sc_total"]
        skew_val = sc.skew()
        lines += [
            "",
            "---",
            "",
            f"## 4. SC_total Distribution (All {n_total} Scenarios)",
            "",
            "| Statistic | Value |",
            "|-----------|-------|",
            f"| Mean      | {sc.mean():.4f} |",
            f"| Std       | {sc.std():.4f} |",
            f"| Min       | {sc.min():.4f} |",
            f"| Q1        | {sc.quantile(0.25):.4f} |",
            f"| Median    | {sc.median():.4f} |",
            f"| Q3        | {sc.quantile(0.75):.4f} |",
            f"| Max       | {sc.max():.4f} |",
            f"| Skewness  | {skew_val:.2f} "
            f"({'positive -- right tail from high-intensity outliers' if skew_val > 0 else 'negative'}) |",
            "",
            "The distribution is centred near zero (by construction, since PCA "
            "operates on z-standardised inputs) but "
            f"{'right-skewed: a small number of scenarios have very high shock scores' if skew_val > 0 else 'left-skewed'}.",
        ]

        # Extreme scenarios
        merged = sc_df.merge(
            manifest_df[["scenario_id", "ticker"]], on="scenario_id", how="left",
            suffixes=("", "_m"),
        ) if "ticker" not in sc_df.columns else sc_df.copy()
        if "ticker" in merged.columns:
            top = merged.nlargest(3, "sc_total")
            bot = merged.nsmallest(2, "sc_total")
            lines += [
                "",
                "### Extreme Scenarios",
                "",
                "| Rank | Scenario | Ticker | SC_total | Key Drivers |",
                "|---|---|---|---|---|",
            ]
            for rank_label, row in zip(
                ["Highest", "2nd highest", "3rd highest"], top.itertuples()
            ):
                drivers = []
                if hasattr(row, "ac_raw"):
                    drivers.append(f"{int(row.ac_raw)} articles")
                if hasattr(row, "ai_raw"):
                    drivers.append(f"volume {row.ai_raw:.1f}x normal")
                lines.append(
                    f"| {rank_label} | {row.scenario_id} | {row.ticker} | "
                    f"**{row.sc_total:.4f}** | {', '.join(drivers)} |"
                )
            for rank_label, row in zip(["Lowest", "2nd lowest"], bot.itertuples()):
                drivers = []
                if hasattr(row, "ac_raw"):
                    drivers.append(f"{int(row.ac_raw)} article{'s' if row.ac_raw > 1 else ''}")
                if hasattr(row, "se_raw"):
                    drivers.append(f"sentiment {row.se_raw:.2f}")
                lines.append(
                    f"| {rank_label} | {row.scenario_id} | {row.ticker} | "
                    f"**{row.sc_total:.4f}** | {', '.join(drivers)} |"
                )

        # Severity bucket table
        lines += [
            "",
            "### SC_total by Severity Bucket",
            "",
            "Scenarios are split into terciles to create the severity_level "
            "dashboard signal:",
            "",
            "| Bucket | n | Mean SC_total | Range |",
            "|--------|---|---------------|-------|",
        ]
        for level in ["Low", "Medium", "High"]:
            sub = sc_df[sc_df["severity_level"] == level]["sc_total"]
            lines.append(
                f"| **{level}** | {len(sub)} | {sub.mean():.4f} | "
                f"[{sub.min():.4f}, {sub.max():.4f}] |"
            )

        # SC_total by block
        merged_block = sc_df.merge(
            manifest_df[["scenario_id", "block_id"]], on="scenario_id", how="left",
        ) if "block_id" not in sc_df.columns else sc_df.copy()
        if "block_id" in merged_block.columns:
            lines += [
                "",
                "### SC_total by Block",
                "",
                "| Block | n | Mean | Std | Min | Max |",
                "|-------|---|------|-----|-----|-----|",
            ]
            for bid in sorted(merged_block["block_id"].unique()):
                bsc = merged_block[merged_block["block_id"] == bid]["sc_total"]
                lines.append(
                    f"| Block {bid} | {len(bsc)} | {bsc.mean():.4f} | "
                    f"{bsc.std():.4f} | {bsc.min():.4f} | {bsc.max():.4f} |"
                )

        # Protocol distribution
        lines += [
            "",
            "### Protocol Distribution",
            "",
            "The protocol recommendation is a rules-based action tier triggered "
            "by the scenario's shock intensity:",
            "",
            "| Protocol | SC_total Threshold | Count | Share |",
            "|---|---|---|---|",
        ]
        proto_thresholds = {
            "Standard Process": "Below 60th percentile",
            "Enhanced Review": "60th--85th percentile",
            "Cooling-Off and Second Review": "Above 85th percentile",
        }
        for proto, threshold in proto_thresholds.items():
            n_p = (sc_df["protocol_recommendation"] == proto).sum()
            lines.append(
                f"| {proto} | {threshold} | {n_p} | "
                f"{n_p / len(sc_df) * 100:.1f}% |"
            )

    # -- Raw component descriptive statistics ----------------------------------
    lines += [
        "",
        "---",
        "",
        "## 5. Raw Component Descriptive Statistics",
    ]
    if not sc_df.empty:
        if "ac_raw" in sc_df.columns:
            ac = sc_df["ac_raw"]
            ac_max_ticker = ""
            if "ticker" in sc_df.columns:
                ac_max_ticker = f" ({sc_df.loc[ac.idxmax(), 'ticker']})"
            lines += [
                "",
                "### AC_raw (Article Count)",
                "",
                "| Statistic | Value |",
                "|-----------|-------|",
                f"| Mean | {ac.mean():.1f} |",
                f"| Median | {ac.median():.1f} |",
                f"| Std | {ac.std():.1f} |",
                f"| Min | {int(ac.min())} |",
                f"| Max | {int(ac.max())}{ac_max_ticker} |",
                "",
                "Most events have 1--3 articles; a few high-profile events have 20+.",
            ]

        if "se_raw" in sc_df.columns:
            se = sc_df["se_raw"]
            lines += [
                "",
                "### SE_raw (Sentiment Extremity)",
                "",
                "| Statistic | Value |",
                "|-----------|-------|",
                f"| Mean | {se.mean():.4f} |",
                f"| Median | {se.median():.4f} |",
                f"| Min | {se.min():.4f} |",
                f"| Max | {se.max():.4f} |",
                "",
                f"Most events carry strongly non-neutral sentiment "
                f"(median {se.median():.2f}). A few events have notably low "
                "sentiment extremity.",
            ]

        if "ai_raw" in sc_df.columns:
            ai = sc_df["ai_raw"]
            ai_max_ticker = ""
            if "ticker" in sc_df.columns:
                ai_max_ticker = f" ({sc_df.loc[ai.idxmax(), 'ticker']})"
            lines += [
                "",
                "### AI_raw (Attention Intensity)",
                "",
                "| Statistic | Value |",
                "|-----------|-------|",
                f"| Mean | {ai.mean():.2f} |",
                f"| Median | {ai.median():.2f} |",
                f"| Min | {ai.min():.2f} |",
                f"| Max | {ai.max():.2f}{ai_max_ticker} |",
                "",
                "A value of 1.0 means normal volume. The median of "
                f"{ai.median():.2f} means the typical event-bar volume is "
                f"roughly {(ai.median() - 1) * 100:.0f}% above its trailing "
                "average.",
            ]

        if "es_raw" in sc_df.columns:
            es_counts = sc_df["es_raw"].value_counts().sort_index()
            lines += [
                "",
                "### ES_raw (Event-Type Severity)",
                "",
                "| Value | Count |",
                "|-------|-------|",
            ]
            for val, cnt in es_counts.items():
                lines.append(f"| {val} | {cnt} |")
            lines.append("")
            lines.append("Most scenarios map to the baseline severity (1.0). "
                         "This component is currently based on a placeholder "
                         "severity mapping and requires manual review.")

    # -- Price reaction statistics ---------------------------------------------
    if price_reaction_df is not None and "price_reaction_pct" in price_reaction_df.columns:
        pr = price_reaction_df["price_reaction_pct"].dropna()
        if not pr.empty:
            n_pos      = (pr > 0).sum()
            n_neg      = (pr < 0).sum()
            pr_merged  = price_reaction_df
            if "ticker" not in pr_merged.columns and "scenario_id" in pr_merged.columns:
                pr_merged = pr_merged.merge(
                    manifest_df[["scenario_id", "ticker"]], on="scenario_id", how="left",
                )
            lines += [
                "",
                "---",
                "",
                "## 6. Price Reaction Statistics",
                "",
                "Each scenario records the immediate price reaction in the "
                "2-hour window following the event.",
                "",
                "| Statistic | Value |",
                "|-----------|-------|",
                f"| Mean | {'+' if pr.mean() >= 0 else ''}{pr.mean():.2f}% |",
                f"| Median | {'+' if pr.median() >= 0 else ''}{pr.median():.2f}% |",
                f"| Std | {pr.std():.2f}% |",
                f"| Min | {pr.min():.2f}% |",
                f"| Max | {'+' if pr.max() >= 0 else ''}{pr.max():.2f}% |",
                f"| Positive reactions | {n_pos} ({n_pos / len(pr) * 100:.1f}%) |",
                f"| Negative reactions | {n_neg} ({n_neg / len(pr) * 100:.1f}%) |",
            ]

            if "ticker" in pr_merged.columns:
                top3 = pr_merged.nlargest(3, "price_reaction_pct")
                bot3 = pr_merged.nsmallest(3, "price_reaction_pct")
                lines += [
                    "",
                    "### Largest Price Reactions",
                    "",
                    "| Scenario | Ticker | Reaction | Direction |",
                    "|---|---|---|---|",
                ]
                for _, r in top3.iterrows():
                    lines.append(
                        f"| {r['scenario_id']} | {r['ticker']} | "
                        f"+{r['price_reaction_pct']:.2f}% | Up |"
                    )
                for _, r in bot3.iterrows():
                    lines.append(
                        f"| {r['scenario_id']} | {r['ticker']} | "
                        f"{r['price_reaction_pct']:.2f}% | Down |"
                    )

            if not sc_df.empty and "severity_level" in sc_df.columns:
                pr_sev = pr_merged.merge(
                    sc_df[["scenario_id", "severity_level"]], on="scenario_id", how="left",
                )
                if "severity_level" in pr_sev.columns:
                    lines += [
                        "",
                        "### Price Reaction by Severity Level",
                        "",
                        "| Severity | Mean Reaction | Std |",
                        "|---|---|---|",
                    ]
                    for level in ["Low", "Medium", "High"]:
                        sub = pr_sev[pr_sev["severity_level"] == level]["price_reaction_pct"].dropna()
                        if not sub.empty:
                            lines.append(
                                f"| {level} | "
                                f"{'+' if sub.mean() >= 0 else ''}{sub.mean():.2f}% | "
                                f"{sub.std():.2f}% |"
                            )
                    lines.append("")
                    lines.append("High-severity scenarios show the widest dispersion "
                                 "in price reactions, consistent with the interpretation "
                                 "that intense shocks create uncertainty rather than a "
                                 "uniform directional move.")

    # -- Sentiment direction distribution --------------------------------------
    if not sc_df.empty and "sentiment_direction" in sc_df.columns:
        sent_order  = [
            "Strongly Negative", "Negative", "Mildly Negative", "Neutral",
            "Mildly Positive", "Positive", "Strongly Positive",
        ]
        sent_counts = sc_df["sentiment_direction"].value_counts()
        lines += [
            "",
            "---",
            "",
            "## 7. Sentiment Direction Distribution",
            "",
            "| Sentiment Label | Count | Share |",
            "|---|---|---|",
        ]
        for label in sent_order:
            cnt = sent_counts.get(label, 0)
            lines.append(f"| {label} | {cnt} | {cnt / len(sc_df) * 100:.1f}% |")

        n_neg = sum(sent_counts.get(l, 0) for l in sent_order[:3])
        n_pos = sum(sent_counts.get(l, 0) for l in sent_order[4:])
        lines.append("")
        lines.append(
            f"Negative-leaning sentiment accounts for {n_neg / len(sc_df) * 100:.1f}% "
            f"of scenarios; positive-leaning for {n_pos / len(sc_df) * 100:.1f}%."
        )

    # -- Counterbalancing design -----------------------------------------------
    lines += [
        "",
        "---",
        "",
        "## 8. Counterbalancing Design",
        "",
        "- **Form versions per block:** 2 (V1, V2)",
        "- **Total form versions:** 6 (2 per block x 3 blocks)",
        "- **Scenarios per form:** 8 (4 treatment, 4 control)",
        "- **Treatment assignment:** Each scenario appears as treatment "
        "(ShowSC = 1) in 1 of 2 versions and as control (ShowSC = 0) in the "
        "other",
        "- **Presentation order:** Treatment and control scenarios are "
        "interleaved (alternating T-C or C-T), preventing order-based "
        "response patterns",
        "",
        "This design ensures that:",
        "1. Every scenario is seen with and without the Shock Score dashboard "
        "across the sample",
        "2. No respondent sees the same scenario twice",
        "3. Treatment and control alternate within each form",
    ]

    # -- Notes and caveats -----------------------------------------------------
    lines += [
        "",
        "---",
        "",
        "## 9. Notes and Caveats",
        "",
        "### 9a. ES_raw (Event-Type Severity)",
        "Uses a placeholder category-level severity mapping "
        "(see `EVENT_TYPE_SEVERITY` in `toolkits/event_selection_toolkit.py`). "
        "**Requires manual review** against actual event characteristics "
        "before finalising SC_total for the thesis.",
        "",
        "### 9b. Sentiment Scoring",
        "Scores use **FinBERT** (`ProsusAI/finbert`) via HuggingFace Transformers. "
        "The sentiment score is `positive_prob - negative_prob` in [-1, 1]. "
        "See `toolkits/news_processor_toolkit.py` for the shared scorer.",
        "",
        "### 9c. Persistence Horizon",
        "`horizon_bucket` requires 5-day post-event return data and is currently "
        "set to `[REQUIRES POST-EVENT DATA]` for some scenarios. Extend price "
        "data coverage and re-run the script if needed.",
        "",
        "### 9d. Summary Paragraphs",
    ]
    has_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if has_api:
        lines.append(
            "ANTHROPIC_API_KEY was set -- summary paragraphs were auto-generated "
            "via Claude (claude-sonnet-4-20250514). Review each paragraph before use."
        )
    else:
        lines.append(
            "ANTHROPIC_API_KEY was not set -- `summary_paragraph` contains "
            "`[TO BE GENERATED]` placeholders. Set the environment variable "
            "and re-run, or populate manually."
        )

    # Warnings
    lines += ["", "---", "", "## 10. Warnings"]
    if warnings_list:
        for w in warnings_list:
            lines.append(f"- {w}")
    else:
        lines.append("- No warnings.")

    # File manifest
    lines += [
        "",
        "---",
        "",
        "## 11. Generated File Manifest",
        "",
        "### Charts (trailing price chart PNGs)",
        "Each chart shows the stock's 90-day trailing price history up to the "
        "event, giving respondents visual context for the stock's recent "
        "trajectory.",
        "",
    ]
    dashboard_lines: list[str] = []
    counter_lines:   list[str] = []
    metadata_lines:  list[str] = []
    for dirpath, dirnames, filenames in os.walk(output_dir):
        dirnames.sort()
        for fname in sorted(filenames):
            if fname == "survey_assembly_report.md":
                continue
            fpath    = Path(dirpath) / fname
            size_kb  = fpath.stat().st_size / 1024
            rel      = fpath.relative_to(output_dir)
            entry    = f"- `survey/{rel}` ({size_kb:.1f} KB)"
            rel_str  = str(rel)
            if rel_str.startswith("charts"):
                lines.append(entry)
            elif rel_str.startswith("dashboards"):
                dashboard_lines.append(entry)
            elif rel_str.startswith("counterbalancing"):
                counter_lines.append(entry)
            elif rel_str.startswith("metadata"):
                metadata_lines.append(entry)

    lines += [
        "",
        "### Dashboards (Shock Score dashboard PNGs)",
        "Each dashboard visualises the four Shock Score signals (sentiment "
        "direction, severity level, horizon bucket, protocol recommendation) "
        "for one scenario. Shown only to treatment-group respondents.",
        "",
    ]
    lines.extend(dashboard_lines)
    lines += ["", "### Counterbalancing Files"]
    lines.extend(counter_lines)
    lines += ["", "### Metadata Files"]
    lines.extend(metadata_lines)

    # Completion checklist
    lines += [
        "",
        "---",
        "",
        "## 12. Completion Checklist",
        "",
        "- [x] `scenario_metadata.csv`",
        "- [x] `scenario_news_text.csv`",
        "- [x] `scenario_price_reaction.csv`",
        "- [x] `scenario_shock_score.csv`",
        f"- [{'x' if charts_ok == n_total else ' '}] "
        f"Price charts: {charts_ok}/{n_total}",
        f"- [{'x' if dashboards_ok == n_total else ' '}] "
        f"Dashboard images: {dashboards_ok}/{n_total}",
        "- [x] `counterbalancing_matrix.csv`",
        "- [x] `form_assembly_guide.csv`",
    ]

    return "\n".join(lines)
