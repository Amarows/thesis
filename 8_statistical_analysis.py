"""
8_statistical_analysis.py
Statistical analysis pipeline: H1 and H2 regressions, descriptives, figures.
Reads all inputs from files; writes results/thesis_results.md, tables, figures.

Usage:
    python 8_statistical_analysis.py                  # default
    python 8_statistical_analysis.py --no-augment     # alias (same behaviour)
    python 8_statistical_analysis.py --skip-figures   # skip PNG generation
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
import warnings
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from config import (
    PANEL_PATH, SHOCK_SCORE_PATH, METADATA_PATH, PRICE_REACTION_PATH,
    COUNTERBALANCING_PATH, DATA_DIR, RESULTS_DIR, FIGURES_DIR, TABLES_DIR,
    THESIS_RESULTS_PATH as RESULTS_MD_PATH,
    RF_ANNUAL, NRS_NEUTRAL, NRS_MIN, NRS_MAX, WEIGHT_STEP, ALPHA, AUM,
    SEED, HORIZON_DAYS, MIN_YEARS_EXPERIENCE,
    append_run_log, _sha256_file,
)

SENTIMENT_TO_EXPECTED = {
    "Negative": "sell",
    "Positive": "buy",
    "Neutral":  "neutral",
}

TRADING_DAYS_PER_YEAR = 252

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trading_days_between(start: pd.Timestamp, end: pd.Timestamp,
                           all_dates: pd.DatetimeIndex) -> int:
    """Count trading days between start and end (exclusive start, inclusive end)."""
    return int(((all_dates > start) & (all_dates <= end)).sum())


def _nth_trading_day(base: pd.Timestamp, n: int,
                     all_dates: pd.DatetimeIndex) -> pd.Timestamp | None:
    """Return the n-th trading day strictly after base."""
    future = all_dates[all_dates > base]
    if len(future) < n:
        return None
    return future[n - 1]


def _apa_style(ax: plt.Axes) -> None:
    """Remove top and right spines (APA style)."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _round4(x: float) -> str:
    """Format a float to 4 decimal places."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "N/A"
    return f"{x:.4f}"


def _sig_stars(p: float) -> str:
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


# ---------------------------------------------------------------------------
# Section 1 – Load and enrich
# ---------------------------------------------------------------------------

def load_and_enrich() -> pd.DataFrame:
    """Returns enriched panel. Assumes analysis_panel.csv is already clean (filtering done in stage 6)."""
    df = pd.read_csv(PANEL_PATH, low_memory=False)

    # Drop rows where NRS was manually flagged as invalid
    df = df[df["nrs_invalid"].astype(str).str.lower() != "true"].copy()

    # Overwrite SC columns from authoritative shock score file
    ss = pd.read_csv(SHOCK_SCORE_PATH)
    overwrite_cols = [
        "sc_total", "ac_e", "se_e", "ai_e", "es_raw",
        "horizon_bucket", "sentiment_direction", "severity_level",
        "protocol_recommendation",
    ]
    ss_rename = {}
    if "ac_raw" in ss.columns and "ac_e" not in ss.columns:
        ss_rename["ac_raw"] = "ac_e"
    if "se_raw" in ss.columns and "se_e" not in ss.columns:
        ss_rename["se_raw"] = "se_e"
    if "ai_raw" in ss.columns and "ai_e" not in ss.columns:
        ss_rename["ai_raw"] = "ai_e"
    ss = ss.rename(columns=ss_rename)

    # Drop the overwrite columns from df before merge so they are replaced
    drop_cols = [c for c in overwrite_cols if c in df.columns]
    df = df.drop(columns=drop_cols)
    ss_keep = ["scenario_id"] + [c for c in overwrite_cols if c in ss.columns]
    df = df.merge(ss[ss_keep], on="scenario_id", how="left")

    # Ensure numeric types
    for col in ["nrs", "sc_total", "show_sc", "block_id", "years_experience", "is_synthetic"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Experience category dummies (5-10yr is reference, dropped from matrices)
    EXP_BINS   = [0, 5, 10, 15, 20, np.inf]
    EXP_LABELS = ["<5yr", "5-10yr", "10-15yr", "15-20yr", "20+yr"]
    df["exp_cat"] = pd.cut(df["years_experience"], bins=EXP_BINS,
                           labels=EXP_LABELS, right=False)

    return df


# ---------------------------------------------------------------------------
# Section 2 – Price data and horizon returns
# ---------------------------------------------------------------------------

def _load_ibkr_prices(ticker: str) -> pd.DataFrame | None:
    """Load 30-min IBKR CSV for ticker. Returns tz-naive UTC close series or None."""
    pattern = str(DATA_DIR / f"{ticker}_*30min*.csv")
    matches = glob.glob(pattern, recursive=False)
    if not matches:
        # Case-insensitive fallback
        pattern_ci = str(DATA_DIR / f"{ticker.upper()}_*30min*.csv")
        matches = glob.glob(pattern_ci)
    if not matches:
        return None
    path = matches[0]
    df = pd.read_csv(path)
    # First column is datetime, last numeric column is close
    df.columns = [c.strip() for c in df.columns]
    time_col = df.columns[0]
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    df = df.set_index(time_col).sort_index()
    # Use 'close' column if present, else last numeric
    if "close" in df.columns:
        prices = df["close"].dropna()
    else:
        num_cols = df.select_dtypes(include=[np.number]).columns
        prices = df[num_cols[-1]].dropna()
    return prices.to_frame("close")


def _load_yahoo_prices(ticker: str, event_date: pd.Timestamp) -> pd.DataFrame | None:
    """Fallback: daily close via Yahoo Finance."""
    try:
        sys.path.insert(0, "src_api_yahoo")
        from market_data_toolkit import fetch_prices  # noqa: F401
        tickers_df = pd.DataFrame({"ticker": [ticker], "isin": [ticker], "ccy": ["USD"]})
        start = str((event_date - pd.Timedelta(days=10)).date())
        end   = str((event_date + pd.Timedelta(days=35)).date())
        result = fetch_prices(tickers_df, start=start, end=end)
        prices = result.raw_prices  # daily close, indexed by date, columns by ISIN
        # raw_prices columns may be tickers or ISINs; try ticker first
        col = None
        for c in prices.columns:
            if str(c).upper() == ticker.upper():
                col = c
                break
        if col is None and len(prices.columns) == 1:
            col = prices.columns[0]
        if col is None:
            return None
        s = prices[col].dropna()
        s.index = pd.to_datetime(s.index, utc=True)
        return s.to_frame("close")
    except Exception as e:
        warnings.warn(f"Yahoo fallback failed for {ticker}: {e}")
        return None


def load_horizon_returns(scenarios: pd.DataFrame) -> pd.DataFrame:
    """
    Returns DataFrame indexed by scenario_id with columns:
    horizon_days, horizon_return_pct, price_at_event,
    price_at_horizon, data_source, data_sufficient
    """
    rows = []
    for _, row in scenarios.iterrows():
        sid         = row["scenario_id"]
        ticker      = row["ticker"]
        event_date  = pd.Timestamp(row["event_date"], tz="America/New_York")
        event_time_str = str(row.get("event_time", "09:30")).strip()
        hbucket     = row.get("horizon_bucket", "Several Weeks")
        n_days      = HORIZON_DAYS.get(hbucket, 20)

        # Parse event timestamp in ET
        try:
            hh, mm = [int(x) for x in event_time_str.split(":")]
            event_ts = event_date.replace(hour=hh, minute=mm, second=0)
            event_ts_utc = event_ts.tz_convert("UTC")
        except Exception:
            event_ts_utc = event_date.tz_convert("UTC")

        result = {
            "scenario_id": sid, "ticker": ticker,
            "horizon_bucket": hbucket, "horizon_days": n_days,
            "price_at_event": np.nan, "price_at_horizon": np.nan,
            "horizon_return_pct": np.nan,
            "data_source": "none", "data_sufficient": False,
        }

        # Try IBKR 30-min data
        prices = _load_ibkr_prices(ticker)
        if prices is not None:
            # Resample to daily for horizon counting
            prices_utc = prices.copy()
            prices_utc.index = prices_utc.index.tz_convert("UTC")

            # Find price at or immediately after event timestamp
            after_event = prices_utc[prices_utc.index >= event_ts_utc]
            if len(after_event) == 0:
                # Try fallback
                prices = None
            else:
                price_at_event = float(after_event.iloc[0]["close"])
                # Convert to ET for daily-date counting
                prices_et = prices_utc.copy()
                prices_et.index = prices_et.index.tz_convert("America/New_York")
                daily_dates = prices_et.resample("D").last().dropna().index
                trading_dates = daily_dates[daily_dates.weekday < 5]
                # n-th trading day after event_date
                event_date_only = event_date.date()
                trading_dates_after = trading_dates[
                    pd.to_datetime(trading_dates).date > event_date_only
                    if hasattr(trading_dates[0], 'date') else
                    [d.date() > event_date_only for d in trading_dates]
                ]
                # rebuild properly
                td_series = pd.DatetimeIndex([
                    d for d in trading_dates
                    if pd.Timestamp(d).date() > event_date_only
                ])
                if len(td_series) >= n_days:
                    horizon_date = td_series[n_days - 1]
                    # Get last 30-min bar on or before horizon_date end-of-day
                    horizon_end_utc = pd.Timestamp(horizon_date.date(),
                                                    tz="America/New_York").replace(
                                                    hour=20).tz_convert("UTC")
                    horizon_prices = prices_utc[prices_utc.index <= horizon_end_utc]
                    horizon_prices = horizon_prices[
                        horizon_prices.index >= pd.Timestamp(horizon_date.date(),
                                                              tz="UTC")
                    ]
                    if len(horizon_prices) > 0:
                        price_at_horizon = float(horizon_prices.iloc[-1]["close"])
                        ret = (price_at_horizon - price_at_event) / price_at_event * 100
                        result.update({
                            "price_at_event": round(price_at_event, 4),
                            "price_at_horizon": round(price_at_horizon, 4),
                            "horizon_return_pct": round(ret, 4),
                            "data_source": "ibkr",
                            "data_sufficient": True,
                        })
                    else:
                        warnings.warn(f"No horizon bar data for {sid} ({ticker})")
                else:
                    warnings.warn(
                        f"Insufficient trading days post-event for {sid} ({ticker}): "
                        f"need {n_days}, have {len(td_series)}"
                    )
                    result["price_at_event"] = round(price_at_event, 4)
                    result["data_source"] = "ibkr"

        if prices is None or not result["data_sufficient"]:
            # Yahoo fallback – daily prices
            yprices = _load_yahoo_prices(ticker, event_date)
            if yprices is not None:
                yprices.index = pd.to_datetime(yprices.index, utc=True)
                yprices_et = yprices.copy()
                yprices_et.index = yprices_et.index.tz_convert("America/New_York")
                event_date_only = event_date.date()
                # Price at event = close on event_date
                event_day_prices = yprices_et[
                    [d.date() == event_date_only for d in yprices_et.index]
                ]
                if len(event_day_prices) == 0:
                    rows.append(result)
                    continue
                price_at_event = float(event_day_prices.iloc[-1]["close"])
                td_all = pd.DatetimeIndex([
                    d for d in yprices_et.index
                    if d.date() > event_date_only and d.weekday() < 5
                ])
                if len(td_all) >= n_days:
                    horizon_day = td_all[n_days - 1].date()
                    horizon_prices_y = yprices_et[
                        [d.date() == horizon_day for d in yprices_et.index]
                    ]
                    if len(horizon_prices_y) > 0:
                        price_at_horizon = float(horizon_prices_y.iloc[-1]["close"])
                        ret = (price_at_horizon - price_at_event) / price_at_event * 100
                        result.update({
                            "price_at_event": round(price_at_event, 4),
                            "price_at_horizon": round(price_at_horizon, 4),
                            "horizon_return_pct": round(ret, 4),
                            "data_source": "yahoo",
                            "data_sufficient": True,
                        })
                else:
                    warnings.warn(
                        f"Yahoo: insufficient data for {sid} ({ticker})"
                    )
                    result["price_at_event"] = round(price_at_event, 4)
                    result["data_source"] = "yahoo"

        rows.append(result)

    out = pd.DataFrame(rows).set_index("scenario_id")
    n_suff = out["data_sufficient"].sum()
    n_total = len(out)
    print(f"\nData sufficiency: {n_suff}/{n_total} scenarios have sufficient horizon price data.")
    insuff = out[~out["data_sufficient"]].index.tolist()
    if insuff:
        print(f"Insufficient: {insuff}")

    # Write sufficiency table
    suff_df = out.reset_index()[
        ["scenario_id", "ticker", "horizon_bucket", "horizon_days",
         "price_at_event", "price_at_horizon", "horizon_return_pct",
         "data_source", "data_sufficient"]
    ]
    suff_df.to_csv(TABLES_DIR / "tbl_data_sufficiency.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# Section 3 – Descriptive statistics
# ---------------------------------------------------------------------------

def compute_descriptives(df: pd.DataFrame, skip_figures: bool = False) -> dict:
    """Compute and save descriptive statistics."""
    desc = {}

    # --- Respondent level ---
    resp_cols = [
        "respondent_id", "years_experience",
        "aum_category", "institution_type", "investment_mandate",
        "geographic_focus", "discretionary_authority", "certifications",
    ]
    resp_avail = [c for c in resp_cols if c in df.columns]
    rdf = df[resp_avail].drop_duplicates(subset=["respondent_id"]) if "respondent_id" in df.columns else df[resp_avail].drop_duplicates()

    n_total_resp = len(rdf)
    exp          = pd.to_numeric(rdf["years_experience"], errors="coerce").dropna()

    desc["n_respondents"] = n_total_resp
    desc["exp_mean"]      = round(exp.mean(), 4)
    desc["exp_median"]    = round(exp.median(), 4)
    desc["exp_sd"]        = round(exp.std(), 4)
    desc["exp_min"]       = round(exp.min(), 4)
    desc["exp_max"]       = round(exp.max(), 4)

    # Frequency tables for categorical fields
    cat_fields = [
        "aum_category", "institution_type", "investment_mandate",
        "geographic_focus", "discretionary_authority", "certifications",
    ]
    freq_rows = []
    for field in cat_fields:
        if field not in rdf.columns:
            continue
        vc = rdf[field].value_counts(dropna=False)
        for val, cnt in vc.items():
            freq_rows.append({
                "field": field, "value": val,
                "count": cnt, "pct": round(cnt / n_total_resp * 100, 2),
            })
    desc["freq_demographics"] = pd.DataFrame(freq_rows)

    # Save respondent table
    resp_summary = pd.DataFrame([{
        "n_total":   n_total_resp,
        "exp_mean":  desc["exp_mean"],
        "exp_median": desc["exp_median"],
        "exp_sd":    desc["exp_sd"],
        "exp_min":   desc["exp_min"],
        "exp_max":   desc["exp_max"],
    }])
    resp_summary.to_csv(TABLES_DIR / "tbl_descriptive_respondents.csv", index=False)
    desc["freq_demographics"].to_csv(
        TABLES_DIR / "tbl_descriptive_respondents_freq.csv", index=False
    )

    # --- NRS observation level ---
    nrs = pd.to_numeric(df["nrs"], errors="coerce").dropna()
    sc0 = pd.to_numeric(df.loc[df["show_sc"] == 0, "nrs"], errors="coerce").dropna()
    sc1 = pd.to_numeric(df.loc[df["show_sc"] == 1, "nrs"], errors="coerce").dropna()

    nrs_summary = pd.DataFrame([{
        "condition": "overall", "n": len(nrs),
        "mean": round(nrs.mean(), 4), "median": round(nrs.median(), 4),
        "sd": round(nrs.std(), 4), "min": nrs.min(), "max": nrs.max(),
    }, {
        "condition": "ShowSC=0", "n": len(sc0),
        "mean": round(sc0.mean(), 4), "median": round(sc0.median(), 4),
        "sd": round(sc0.std(), 4), "min": sc0.min() if len(sc0) else np.nan,
        "max": sc0.max() if len(sc0) else np.nan,
    }, {
        "condition": "ShowSC=1", "n": len(sc1),
        "mean": round(sc1.mean(), 4), "median": round(sc1.median(), 4),
        "sd": round(sc1.std(), 4), "min": sc1.min() if len(sc1) else np.nan,
        "max": sc1.max() if len(sc1) else np.nan,
    }])
    nrs_summary.to_csv(TABLES_DIR / "tbl_descriptive_nrs.csv", index=False)
    desc["nrs_summary"] = nrs_summary
    desc["nrs_mean_diff"] = round(sc1.mean() - sc0.mean(), 4) if len(sc0) > 0 and len(sc1) > 0 else np.nan

    # Manipulation check & usefulness
    if "manipulation_check" in df.columns:
        mc_df = df.drop_duplicates(subset=["respondent_id"]) if "respondent_id" in df.columns else df
        mc_vc = mc_df["manipulation_check"].value_counts(dropna=False)
        desc["manipulation_check"] = mc_vc.to_dict()
    if "usefulness_rating" in df.columns:
        ur_df = df.loc[df["show_sc"] == 1].drop_duplicates(subset=["respondent_id"]) if "respondent_id" in df.columns else df.loc[df["show_sc"] == 1]
        ur = pd.to_numeric(ur_df["usefulness_rating"], errors="coerce").dropna()
        desc["usefulness_mean"]   = round(ur.mean(), 4) if len(ur) > 0 else np.nan
        desc["usefulness_median"] = round(ur.median(), 4) if len(ur) > 0 else np.nan
        desc["usefulness_sd"]     = round(ur.std(), 4) if len(ur) > 0 else np.nan

    # --- Scenario level ---
    sc_vals = pd.to_numeric(df["sc_total"], errors="coerce").dropna().unique()
    # Use scenario-level unique values
    scen_df = df.drop_duplicates(subset=["scenario_id"]) if "scenario_id" in df.columns else df
    sc_col = pd.to_numeric(scen_df["sc_total"], errors="coerce").dropna()
    ac_col = pd.to_numeric(scen_df.get("ac_e", pd.Series(dtype=float)), errors="coerce").dropna()
    se_col = pd.to_numeric(scen_df.get("se_e", pd.Series(dtype=float)), errors="coerce").dropna()
    ai_col = pd.to_numeric(scen_df.get("ai_e", pd.Series(dtype=float)), errors="coerce").dropna()
    es_col = pd.to_numeric(scen_df.get("es_raw", pd.Series(dtype=float)), errors="coerce").dropna()

    scen_summary = pd.DataFrame([{
        "metric": "sc_total", "n": len(sc_col),
        "mean": round(sc_col.mean(), 4) if len(sc_col) else np.nan,
        "median": round(sc_col.median(), 4) if len(sc_col) else np.nan,
        "sd": round(sc_col.std(), 4) if len(sc_col) else np.nan,
        "min": round(sc_col.min(), 4) if len(sc_col) else np.nan,
        "max": round(sc_col.max(), 4) if len(sc_col) else np.nan,
    }, {
        "metric": "ac_e", "n": len(ac_col),
        "mean": round(ac_col.mean(), 4) if len(ac_col) else np.nan,
        "median": np.nan, "sd": round(ac_col.std(), 4) if len(ac_col) else np.nan,
        "min": np.nan, "max": np.nan,
    }, {
        "metric": "se_e", "n": len(se_col),
        "mean": round(se_col.mean(), 4) if len(se_col) else np.nan,
        "median": np.nan, "sd": round(se_col.std(), 4) if len(se_col) else np.nan,
        "min": np.nan, "max": np.nan,
    }, {
        "metric": "ai_e", "n": len(ai_col),
        "mean": round(ai_col.mean(), 4) if len(ai_col) else np.nan,
        "median": np.nan, "sd": round(ai_col.std(), 4) if len(ai_col) else np.nan,
        "min": np.nan, "max": np.nan,
    }, {
        "metric": "es_raw", "n": len(es_col),
        "mean": round(es_col.mean(), 4) if len(es_col) else np.nan,
        "median": np.nan, "sd": round(es_col.std(), 4) if len(es_col) else np.nan,
        "min": np.nan, "max": np.nan,
    }])
    scen_summary.to_csv(TABLES_DIR / "tbl_descriptive_scenarios.csv", index=False)
    desc["scen_summary"] = scen_summary

    if "horizon_bucket" in scen_df.columns:
        desc["horizon_dist"] = scen_df["horizon_bucket"].value_counts().to_dict()

    # --- Figures ---
    if not skip_figures:
        _fig_demographics(rdf, desc)
        _fig_nrs_distribution(nrs)
        _fig_nrs_by_condition(sc0, sc1)
        _fig_sc_distribution(scen_df)

    return desc


def _fig_demographics(rdf: pd.DataFrame, desc: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax1, ax2 = axes

    # Experience histogram
    exp = pd.to_numeric(rdf["years_experience"], errors="coerce").dropna()
    ax1.hist(exp, bins=max(5, int(len(exp) ** 0.5)), color="#2c7bb6", edgecolor="white")
    ax1.set_xlabel("Years of experience")
    ax1.set_ylabel("Count")
    ax1.set_title("(a) Distribution of respondent experience")
    _apa_style(ax1)

    # Institution type bar chart
    if "institution_type" in rdf.columns:
        it = rdf["institution_type"].value_counts()
        ax2.barh(it.index[::-1], it.values[::-1], color="#2c7bb6")
        ax2.set_xlabel("Count")
        ax2.set_title("(b) Institution type")
        _apa_style(ax2)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_demographics.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _fig_nrs_distribution(nrs: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(nrs, bins=7, range=(0.5, 7.5), color="#2c7bb6", edgecolor="white")
    ax.set_xlabel("Net Risk Stance (NRS)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of NRS responses")
    ax.set_xticks(range(1, 8))
    _apa_style(ax)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_nrs_distribution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _fig_nrs_by_condition(sc0: pd.Series, sc1: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    data = [sc0.values, sc1.values]
    bp = ax.boxplot(data, labels=["ShowSC = 0 (Control)", "ShowSC = 1 (Treatment)"],
                    patch_artist=True,
                    boxprops=dict(facecolor="#abd9e9", color="#2c7bb6"),
                    medianprops=dict(color="#d7191c", linewidth=2))
    ax.set_ylabel("Net Risk Stance (NRS)")
    ax.set_title("NRS by condition")
    _apa_style(ax)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_nrs_by_condition.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _fig_sc_distribution(scen_df: pd.DataFrame) -> None:
    sc = pd.to_numeric(scen_df["sc_total"], errors="coerce").dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(sc, bins=10, color="#abd9e9", edgecolor="#2c7bb6", density=True)
    # Normal overlay
    x = np.linspace(sc.min() - 1, sc.max() + 1, 200)
    ax.plot(x, stats.norm.pdf(x, sc.mean(), sc.std()), color="#d7191c", linewidth=2, label="Normal")
    # Label points
    if "ticker" in scen_df.columns:
        for _, row in scen_df.dropna(subset=["sc_total"]).iterrows():
            ax.annotate(row["ticker"], (float(row["sc_total"]), 0),
                        textcoords="offset points", xytext=(0, 5),
                        fontsize=6, ha="center", rotation=45)
    ax.set_xlabel("SC_total")
    ax.set_ylabel("Density")
    ax.set_title("SC_total distribution across scenarios")
    ax.legend()
    _apa_style(ax)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_sc_distribution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Section 4 – Normality and reliability
# ---------------------------------------------------------------------------

def compute_normality(df: pd.DataFrame) -> dict:
    nrs_all = pd.to_numeric(df["nrs"], errors="coerce").dropna()
    sc0     = pd.to_numeric(df.loc[df["show_sc"] == 0, "nrs"], errors="coerce").dropna()
    sc1     = pd.to_numeric(df.loc[df["show_sc"] == 1, "nrs"], errors="coerce").dropna()

    def _sw(series: pd.Series) -> tuple[float, float]:
        if len(series) < 3:
            return np.nan, np.nan
        try:
            w, p = stats.shapiro(series)
            return round(float(w), 4), round(float(p), 4)
        except Exception:
            return np.nan, np.nan

    rows = []
    for label, s in [("overall", nrs_all), ("ShowSC=0", sc0), ("ShowSC=1", sc1)]:
        w, p = _sw(s)
        rows.append({
            "group": label, "n": len(s),
            "skewness": round(float(stats.skew(s)), 4) if len(s) >= 3 else np.nan,
            "excess_kurtosis": round(float(stats.kurtosis(s)), 4) if len(s) >= 3 else np.nan,
            "shapiro_w": w, "shapiro_p": p,
            "normal_rejected": (p < 0.05) if not np.isnan(p) else None,
        })

    norm_df = pd.DataFrame(rows)
    norm_df.to_csv(TABLES_DIR / "tbl_normality.csv", index=False)

    # Unique respondent count for CLT flag
    n_resp = df["respondent_id"].nunique() if "respondent_id" in df.columns else len(nrs_all)
    clt_applies = n_resp >= 30

    # Inter-scenario consistency (mean pairwise Pearson, not Cronbach's alpha)
    consistency = np.nan
    if "respondent_id" in df.columns and "scenario_id" in df.columns:
        try:
            pivot = df.pivot_table(
                index="respondent_id", columns="scenario_id", values="nrs", aggfunc="mean"
            )
            corr_matrix = pivot.corr()
            np.fill_diagonal(corr_matrix.values, np.nan)
            consistency = round(float(np.nanmean(corr_matrix.values)), 4)
        except Exception:
            pass

    result = {
        "norm_df": norm_df,
        "clt_applies": clt_applies,
        "n_respondents": n_resp,
        "mean_pairwise_corr": consistency,
    }
    return result


# ---------------------------------------------------------------------------
# Section 4b – NRS / sentiment alignment diagnostic (Issue #116)
# ---------------------------------------------------------------------------

def compute_nrs_sentiment_alignment(df: pd.DataFrame) -> dict:
    """Compute alignment between NRS direction and sentiment-expected direction."""
    if "sentiment_direction" not in df.columns or "nrs" not in df.columns:
        return {"alignment_df": pd.DataFrame(), "overall_alignment_rate": np.nan}

    work = df[["nrs", "sentiment_direction", "show_sc"]].copy()
    work["nrs"] = pd.to_numeric(work["nrs"], errors="coerce")
    work = work.dropna(subset=["nrs", "sentiment_direction"])

    work["nrs_direction"] = np.where(
        work["nrs"] > NRS_NEUTRAL, "buy",
        np.where(work["nrs"] < NRS_NEUTRAL, "sell", "neutral"),
    )
    work["expected_direction"] = work["sentiment_direction"].map(SENTIMENT_TO_EXPECTED).fillna("neutral")
    work["aligned"] = work["nrs_direction"] == work["expected_direction"]

    rows = []
    overall_rate = round(float(work["aligned"].mean()), 4)
    rows.append({"group": "overall", "n": len(work),
                 "n_aligned": int(work["aligned"].sum()),
                 "alignment_rate": overall_rate})
    for cond in sorted(work["show_sc"].dropna().unique()):
        sub = work[work["show_sc"] == cond]
        rate = round(float(sub["aligned"].mean()), 4) if len(sub) > 0 else np.nan
        rows.append({"group": f"ShowSC={int(cond)}", "n": len(sub),
                     "n_aligned": int(sub["aligned"].sum()),
                     "alignment_rate": rate})
    for sent in sorted(work["sentiment_direction"].dropna().unique()):
        sub = work[work["sentiment_direction"] == sent]
        rate = round(float(sub["aligned"].mean()), 4) if len(sub) > 0 else np.nan
        rows.append({"group": f"sentiment={sent}", "n": len(sub),
                     "n_aligned": int(sub["aligned"].sum()),
                     "alignment_rate": rate})

    alignment_df = pd.DataFrame(rows)
    alignment_df.to_csv(TABLES_DIR / "tbl_nrs_sentiment_alignment.csv", index=False)
    return {"alignment_df": alignment_df, "overall_alignment_rate": overall_rate}


# ---------------------------------------------------------------------------
# Section 5 – H1 Regression
# ---------------------------------------------------------------------------

def run_h1_regression(df: pd.DataFrame) -> dict:
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    h1 = {}

    # Prepare data – drop rows missing core vars
    reg_cols = ["nrs", "sc_total", "show_sc", "exp_cat", "block_id"]
    reg = df[[c for c in reg_cols if c in df.columns]].copy()
    reg["nrs"]      = pd.to_numeric(reg["nrs"],      errors="coerce")
    reg["sc_total"] = pd.to_numeric(reg["sc_total"], errors="coerce")
    reg["show_sc"]  = pd.to_numeric(reg["show_sc"],  errors="coerce")
    reg["block_id"] = pd.to_numeric(reg["block_id"], errors="coerce")
    reg = reg.dropna(subset=["nrs", "sc_total", "show_sc", "block_id"])

    # Experience dummies (5-10yr reference, explicitly dropped)
    exp_dummies = pd.get_dummies(reg["exp_cat"], prefix="exp", drop_first=False)
    exp_dummies = exp_dummies.drop(columns=["exp_5-10yr"], errors="ignore").astype(float)

    # Block fixed effects
    block_dummies = pd.get_dummies(reg["block_id"], prefix="block", drop_first=True).astype(float)
    X = pd.concat([reg[["sc_total", "show_sc"]].astype(float), exp_dummies, block_dummies], axis=1)
    X = sm.add_constant(X)
    y = reg["nrs"].astype(float)

    # Try two-way cluster-robust SE via linearmodels
    TWO_WAY = False
    try:
        from linearmodels.panel import PanelOLS
        TWO_WAY = True
    except ImportError:
        pass

    def _fit_ols_hc3(X_: pd.DataFrame, y_: pd.Series) -> dict:
        model = sm.OLS(y_, X_).fit(cov_type="HC3")
        sc_idx = list(X_.columns).index("sc_total") if "sc_total" in X_.columns else None
        if sc_idx is None:
            return {"model": model, "beta1": np.nan, "se": np.nan, "t": np.nan,
                    "p": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                    "r2": round(model.rsquared, 4), "n_obs": int(model.nobs),
                    "clustering": "HC3"}
        beta = model.params.iloc[sc_idx]
        se   = model.bse.iloc[sc_idx]
        t    = model.tvalues.iloc[sc_idx]
        p    = model.pvalues.iloc[sc_idx]
        ci   = model.conf_int().iloc[sc_idx]
        return {"model": model, "beta1": round(beta, 4), "se": round(se, 4),
                "t": round(t, 4), "p": round(p, 4),
                "ci_lo": round(ci[0], 4), "ci_hi": round(ci[1], 4),
                "r2": round(model.rsquared, 4), "n_obs": int(model.nobs),
                "clustering": "HC3"}

    primary = _fit_ols_hc3(X, y)
    primary["n_respondents"] = df["respondent_id"].nunique() if "respondent_id" in df.columns else np.nan
    primary["n_scenarios"]   = df["scenario_id"].nunique() if "scenario_id" in df.columns else np.nan
    h1["primary"] = primary

    # --- Robustness ---
    rob_rows = []

    # Spec 1: SC_total quintile dummies
    try:
        reg_r1 = reg.copy()
        reg_r1["sc_quintile"] = pd.qcut(reg_r1["sc_total"], q=5, labels=False, duplicates="drop")
        q_dummies = pd.get_dummies(reg_r1["sc_quintile"], prefix="q", drop_first=True)
        X_r1 = pd.concat(
            [reg_r1[["show_sc"]].astype(float), q_dummies, exp_dummies, block_dummies], axis=1
        ).astype(float)
        X_r1 = sm.add_constant(X_r1)
        m_r1 = sm.OLS(y, X_r1).fit(cov_type="HC3")
        rob_rows.append({
            "spec": "spec_1_quintiles", "note": "SC_total quintile dummies",
            "beta1": "see quintile coefficients", "se": np.nan, "t": np.nan,
            "p": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
            "r2": round(m_r1.rsquared, 4), "n_obs": int(m_r1.nobs), "clustering": "HC3",
        })
    except Exception as e:
        rob_rows.append({"spec": "spec_1_quintiles", "note": str(e)})

    # Spec 2: Respondent fixed effects (within estimator via demeaning)
    try:
        if "respondent_id" in df.columns:
            reg_r2 = df[["respondent_id", "nrs", "sc_total", "show_sc"]].copy()
            for col in ["nrs", "sc_total", "show_sc"]:
                reg_r2[col] = pd.to_numeric(reg_r2[col], errors="coerce")
            reg_r2 = reg_r2.dropna()
            # Demean by respondent
            for col in ["nrs", "sc_total", "show_sc"]:
                reg_r2[f"{col}_dm"] = reg_r2[col] - reg_r2.groupby("respondent_id")[col].transform("mean")
            X_r2 = sm.add_constant(reg_r2[["sc_total_dm", "show_sc_dm"]])
            m_r2 = sm.OLS(reg_r2["nrs_dm"], X_r2).fit(cov_type="HC3")
            b = m_r2.params.get("sc_total_dm", np.nan)
            se_= m_r2.bse.get("sc_total_dm", np.nan)
            t_ = m_r2.tvalues.get("sc_total_dm", np.nan)
            p_ = m_r2.pvalues.get("sc_total_dm", np.nan)
            ci_ = m_r2.conf_int().loc["sc_total_dm"] if "sc_total_dm" in m_r2.conf_int().index else [np.nan, np.nan]
            rob_rows.append({
                "spec": "spec_2_within", "note": "Respondent FE (within)",
                "beta1": round(b, 4), "se": round(se_, 4), "t": round(t_, 4),
                "p": round(p_, 4), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
                "r2": round(m_r2.rsquared, 4), "n_obs": int(m_r2.nobs), "clustering": "HC3",
            })
    except Exception as e:
        rob_rows.append({"spec": "spec_2_within", "note": str(e)})

    # Spec 3: SC components separately
    try:
        comp_cols = [c for c in ["ac_e", "se_e", "ai_e", "es_raw"] if c in df.columns]
        if comp_cols:
            reg_r3 = df[["nrs", "show_sc", "block_id"] + comp_cols].copy()
            for col in reg_r3.columns:
                reg_r3[col] = pd.to_numeric(reg_r3[col], errors="coerce")
            reg_r3 = reg_r3.dropna()
            bd3 = pd.get_dummies(reg_r3["block_id"], prefix="block", drop_first=True)
            X_r3 = sm.add_constant(pd.concat([reg_r3[["show_sc"] + comp_cols], bd3], axis=1).astype(float))
            m_r3 = sm.OLS(reg_r3["nrs"].astype(float), X_r3).fit(cov_type="HC3")
            for cc in comp_cols:
                b = m_r3.params.get(cc, np.nan)
                se_ = m_r3.bse.get(cc, np.nan)
                t_ = m_r3.tvalues.get(cc, np.nan)
                p_ = m_r3.pvalues.get(cc, np.nan)
                ci_ = m_r3.conf_int().loc[cc] if cc in m_r3.conf_int().index else [np.nan, np.nan]
                rob_rows.append({
                    "spec": f"spec_3_component_{cc}", "note": f"Component: {cc}",
                    "beta1": round(b, 4), "se": round(se_, 4), "t": round(t_, 4),
                    "p": round(p_, 4), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
                    "r2": round(m_r3.rsquared, 4), "n_obs": int(m_r3.nobs), "clustering": "HC3",
                })
    except Exception as e:
        rob_rows.append({"spec": "spec_3_components", "note": str(e)})

    # Spec 4: Interaction SC_total × ShowSC
    try:
        reg_r4 = reg.copy()
        reg_r4["sc_x_showsc"] = reg_r4["sc_total"] * reg_r4["show_sc"]
        X_r4 = pd.concat(
            [reg_r4[["sc_total", "show_sc", "sc_x_showsc"]].astype(float),
             exp_dummies, block_dummies], axis=1
        ).astype(float)
        X_r4 = sm.add_constant(X_r4)
        m_r4 = sm.OLS(y, X_r4).fit(cov_type="HC3")
        b = m_r4.params.get("sc_x_showsc", np.nan)
        se_ = m_r4.bse.get("sc_x_showsc", np.nan)
        t_ = m_r4.tvalues.get("sc_x_showsc", np.nan)
        p_ = m_r4.pvalues.get("sc_x_showsc", np.nan)
        ci_ = m_r4.conf_int().loc["sc_x_showsc"] if "sc_x_showsc" in m_r4.conf_int().index else [np.nan, np.nan]
        rob_rows.append({
            "spec": "spec_4_interaction", "note": "SC_total × ShowSC interaction",
            "beta1": round(b, 4), "se": round(se_, 4), "t": round(t_, 4),
            "p": round(p_, 4), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
            "r2": round(m_r4.rsquared, 4), "n_obs": int(m_r4.nobs), "clustering": "HC3",
        })
    except Exception as e:
        rob_rows.append({"spec": "spec_4_interaction", "note": str(e)})

    rob_df = pd.DataFrame(rob_rows)
    h1["robustness"] = rob_df

    # Save tables – include all covariates from primary model
    primary_model = primary.get("model")
    main_rows = []
    if primary_model is not None:
        for covariate in primary_model.params.index:
            row = {
                "spec": "primary", "covariate": covariate,
                "beta": round(primary_model.params[covariate], 4),
                "se":   round(primary_model.bse[covariate], 4),
                "t":    round(primary_model.tvalues[covariate], 4),
                "p":    round(primary_model.pvalues[covariate], 4),
                "ci_lo": round(primary_model.conf_int().loc[covariate, 0], 4),
                "ci_hi": round(primary_model.conf_int().loc[covariate, 1], 4),
                "r2": primary["r2"], "n_obs": primary["n_obs"],
                "n_respondents": primary["n_respondents"],
                "n_scenarios": primary["n_scenarios"],
                "clustering": primary["clustering"],
            }
            main_rows.append(row)
    else:
        main_rows = [{"spec": "primary", "covariate": "sc_total",
                      "beta": primary["beta1"], "se": primary["se"],
                      "t": primary["t"], "p": primary["p"],
                      "ci_lo": primary["ci_lo"], "ci_hi": primary["ci_hi"],
                      "r2": primary["r2"], "n_obs": primary["n_obs"],
                      "clustering": primary["clustering"]}]
    pd.DataFrame(main_rows).to_csv(TABLES_DIR / "tbl_h1_main.csv", index=False)
    rob_df.to_csv(TABLES_DIR / "tbl_h1_robustness.csv", index=False)

    return h1


# ---------------------------------------------------------------------------
# Section 6 – H2 Portfolio simulation
# ---------------------------------------------------------------------------

def _sharpe(returns: np.ndarray) -> float:
    if len(returns) < 2 or np.std(returns) == 0:
        return np.nan
    return float(np.mean(returns) / np.std(returns, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))


def _sortino(returns: np.ndarray) -> float:
    neg = returns[returns < 0]
    if len(neg) < 2:
        return np.nan
    ds = np.std(neg, ddof=1)
    if ds == 0:
        return np.nan
    return float(np.mean(returns) / ds * np.sqrt(TRADING_DAYS_PER_YEAR))


def run_h2_analysis(df: pd.DataFrame, horizon_returns: pd.DataFrame,
                    skip_figures: bool = False) -> dict:
    import statsmodels.api as sm

    h2 = {}
    suff = horizon_returns[horizon_returns["data_sufficient"]]
    n_excluded_insuff = (~horizon_returns["data_sufficient"]).sum()
    print(f"\nH2: Excluding {n_excluded_insuff} scenarios with insufficient price data.")

    # Merge horizon returns into df
    hr_merge = horizon_returns.reset_index()[["scenario_id", "horizon_return_pct",
                                               "data_sufficient"]].copy()
    df_h2 = df.merge(hr_merge, on="scenario_id", how="left")
    df_h2 = df_h2[df_h2["data_sufficient"] == True].copy()
    df_h2["nrs"] = pd.to_numeric(df_h2["nrs"], errors="coerce")
    df_h2["delta_w"] = (df_h2["nrs"] - NRS_NEUTRAL) * WEIGHT_STEP
    df_h2["weighted_return"] = df_h2["delta_w"] * df_h2["horizon_return_pct"]

    # ---- Option B: individual portfolios ----
    records_b = []
    if "respondent_id" in df_h2.columns:
        for resp_id, grp in df_h2.groupby("respondent_id"):
            for cond, cgrp in grp.groupby("show_sc"):
                cgrp = cgrp.dropna(subset=["weighted_return"])
                if len(cgrp) < 2:
                    continue
                wr = cgrp["weighted_return"].values
                block_id = int(cgrp["block_id"].mode()[0]) if "block_id" in cgrp.columns else np.nan
                exp_cat  = str(cgrp["exp_cat"].iloc[0]) if "exp_cat" in cgrp.columns else np.nan
                records_b.append({
                    "respondent_id": resp_id,
                    "show_sc": int(cond),
                    "portfolio_return": round(float(np.mean(wr)), 4),
                    "sharpe_ratio": round(_sharpe(wr), 4),
                    "sortino_ratio": round(_sortino(wr), 4),
                    "n_scenarios": len(cgrp),
                    "block_id": block_id,
                    "exp_cat": exp_cat,
                })

    opt_b_df = pd.DataFrame(records_b)
    h2["opt_b_df"] = opt_b_df

    # Count sortino-eligible pairs (at least one negative return per respondent-condition)
    n_sortino_eligible = 0
    if not opt_b_df.empty and "respondent_id" in df_h2.columns:
        for resp_id, grp in df_h2.groupby("respondent_id"):
            for cond, cgrp in grp.groupby("show_sc"):
                wr = cgrp.dropna(subset=["weighted_return"])["weighted_return"].values
                if len(wr) >= 2 and np.any(wr < 0):
                    n_sortino_eligible += 1
    h2["n_sortino_eligible"] = n_sortino_eligible
    h2["n_option_b_pairs"]   = len(opt_b_df) if not opt_b_df.empty else 0

    # H2 regression (Option B) – per outcome
    opt_b_reg_rows = []
    for outcome in ["portfolio_return", "sharpe_ratio", "sortino_ratio"]:
        if opt_b_df.empty or outcome not in opt_b_df.columns:
            continue
        reg_h2 = opt_b_df[["show_sc", "exp_cat", "block_id", outcome]].dropna(
            subset=["show_sc", "block_id", outcome]
        )
        if len(reg_h2) < 5:
            continue
        bd = pd.get_dummies(reg_h2["block_id"], prefix="block", drop_first=True).astype(float)
        exp_d = pd.get_dummies(reg_h2["exp_cat"], prefix="exp", drop_first=False).astype(float)
        exp_d = exp_d.drop(columns=["exp_5-10yr"], errors="ignore")
        X = sm.add_constant(pd.concat(
            [reg_h2[["show_sc"]].astype(float), exp_d, bd], axis=1
        ))
        y_out = reg_h2[outcome].astype(float)
        try:
            m = sm.OLS(y_out, X).fit(cov_type="HC3")
            tau = m.params.get("show_sc", np.nan)
            se_ = m.bse.get("show_sc", np.nan)
            t_  = m.tvalues.get("show_sc", np.nan)
            p_  = m.pvalues.get("show_sc", np.nan)
            ci_ = m.conf_int().loc["show_sc"] if "show_sc" in m.conf_int().index else [np.nan, np.nan]
            # Cohen's d
            grp0 = reg_h2.loc[reg_h2["show_sc"] == 0, outcome]
            grp1 = reg_h2.loc[reg_h2["show_sc"] == 1, outcome]
            pooled_sd = np.sqrt((grp0.std() ** 2 + grp1.std() ** 2) / 2) if len(grp0) > 1 and len(grp1) > 1 else np.nan
            cohens_d  = round((grp1.mean() - grp0.mean()) / pooled_sd, 4) if not np.isnan(pooled_sd) and pooled_sd > 0 else np.nan
            opt_b_reg_rows.append({
                "method": "option_b_individual", "outcome": outcome,
                "tau": round(tau, 4), "se": round(se_, 4), "t": round(t_, 4),
                "p": round(p_, 4), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
                "cohens_d": cohens_d, "r2": round(m.rsquared, 4),
                "n": int(m.nobs), "h2_supported": p_ < ALPHA,
            })
        except Exception as e:
            opt_b_reg_rows.append({"method": "option_b_individual", "outcome": outcome,
                                    "note": str(e)})

    h2["opt_b_reg"] = pd.DataFrame(opt_b_reg_rows)

    # ---- Option A: collective portfolios ----
    # Load counterbalancing matrix
    cb = pd.read_csv(COUNTERBALANCING_PATH)
    # Per scenario, per condition: mean NRS across respondents assigned to that condition
    opt_a_rows = []
    for sid, sgrp in df_h2.groupby("scenario_id"):
        for cond in [0, 1]:
            cgrp = sgrp[sgrp["show_sc"] == cond].dropna(subset=["nrs"])
            if len(cgrp) == 0:
                continue
            mean_nrs = float(cgrp["nrs"].mean())
            delta_w  = (mean_nrs - NRS_NEUTRAL) * WEIGHT_STEP
            hr = horizon_returns.loc[sid, "horizon_return_pct"] if sid in horizon_returns.index else np.nan
            opt_a_rows.append({
                "scenario_id": sid, "show_sc": cond,
                "mean_nrs": round(mean_nrs, 4), "delta_w": round(delta_w, 4),
                "horizon_return_pct": hr,
                "weighted_return": round(delta_w * hr, 4) if not np.isnan(hr) else np.nan,
            })

    opt_a_df = pd.DataFrame(opt_a_rows)
    h2["opt_a_df"] = opt_a_df

    for cond in [0, 1]:
        cgrp = opt_a_df[opt_a_df["show_sc"] == cond].dropna(subset=["weighted_return"])
        wr = cgrp["weighted_return"].values
        label = f"sc{cond}"
        h2[f"collective_return_{label}"] = round(float(np.mean(wr)), 4) if len(wr) > 0 else np.nan
        h2[f"sharpe_{label}"] = round(_sharpe(wr), 4)
        h2[f"sortino_{label}"] = round(_sortino(wr), 4)

    ret_diff = h2.get("collective_return_sc1", np.nan) - h2.get("collective_return_sc0", np.nan) \
        if not (np.isnan(h2.get("collective_return_sc1", np.nan)) or np.isnan(h2.get("collective_return_sc0", np.nan))) \
        else np.nan
    h2["return_differential"] = round(ret_diff, 4) if not np.isnan(ret_diff) else np.nan
    h2["dollar_impact"] = round(ret_diff / 100 * AUM, 0) if not np.isnan(ret_diff) else np.nan

    # Compile all rows for output table
    n_sortino_elig = h2.get("n_sortino_eligible", 0)
    n_b_pairs      = h2.get("n_option_b_pairs", 0)
    all_rows = []
    for r in opt_b_reg_rows:
        r2 = dict(r)
        if r2.get("outcome") == "sortino_ratio":
            r2["sortino_n_note"] = (
                f"Computed for {n_sortino_elig} of {n_b_pairs} "
                f"respondent-condition pairs with at least one negative return"
            )
        else:
            r2["sortino_n_note"] = ""
        all_rows.append(r2)
    all_rows.append({
        "method": "option_a_collective", "outcome": "portfolio_return",
        "return_sc0": h2.get("collective_return_sc0"),
        "return_sc1": h2.get("collective_return_sc1"),
        "sharpe_sc0": h2.get("sharpe_sc0"),
        "sharpe_sc1": h2.get("collective_return_sc1"),
        "return_differential": h2.get("return_differential"),
        "dollar_impact": h2.get("dollar_impact"),
        "sortino_n_note": "",
        "warning": "NON-INDEPENDENCE: both portfolios draw from same respondent pool. Descriptive only.",
    })
    pd.DataFrame(all_rows).to_csv(TABLES_DIR / "tbl_h2_portfolio.csv", index=False)

    if not skip_figures:
        _fig_sharpe_comparison(opt_b_df, h2)

    return h2


def _fig_sharpe_comparison(opt_b_df: pd.DataFrame, h2: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax1, ax2 = axes

    # Option B mean Sharpe by condition
    if not opt_b_df.empty and "sharpe_ratio" in opt_b_df.columns:
        for cond, color in [(0, "#abd9e9"), (1, "#2c7bb6")]:
            cgrp = opt_b_df[opt_b_df["show_sc"] == cond]["sharpe_ratio"].dropna()
            if len(cgrp) > 0:
                ax1.bar(
                    f"ShowSC={cond}", cgrp.mean(), yerr=cgrp.sem(),
                    color=color, capsize=5, edgecolor="white"
                )
    ax1.set_ylabel("Mean Sharpe ratio (annualised)")
    ax1.set_title("(a) Option B: Mean Sharpe by condition")
    _apa_style(ax1)

    # Option A collective return comparison
    for i, (label, key, color) in enumerate([
        ("Control (SC=0)", "collective_return_sc0", "#abd9e9"),
        ("Treatment (SC=1)", "collective_return_sc1", "#2c7bb6"),
    ]):
        val = h2.get(key, 0) or 0
        ax2.bar(label, val, color=color, edgecolor="white")
    dollar_impact = h2.get("dollar_impact")
    if dollar_impact is not None and not np.isnan(dollar_impact):
        ax2.annotate(
            f"Dollar impact:\n${dollar_impact:,.0f}",
            xy=(0.5, 0.9), xycoords="axes fraction", ha="center",
            fontsize=9, color="#d7191c",
        )
    ax2.set_ylabel("Portfolio return (%)")
    ax2.set_title("(b) Option A: Collective portfolio return")
    _apa_style(ax2)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_sharpe_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Section 7 – Conclusions engine
# ---------------------------------------------------------------------------

def generate_conclusions(h1: dict, h2: dict, desc: dict, norm: dict) -> dict:
    conc = {}

    # H1
    primary = h1.get("primary", {})
    beta1 = primary.get("beta1", np.nan)
    h1_p  = primary.get("p", np.nan)
    h1_t  = primary.get("t", np.nan)
    h1_ci_lo = primary.get("ci_lo", np.nan)
    h1_ci_hi = primary.get("ci_hi", np.nan)
    h1_supported = (not np.isnan(h1_p)) and (h1_p < ALPHA)

    if np.isnan(beta1):
        _h1_direction_sentence = "The direction of the effect cannot be determined (estimation failed)."
    elif beta1 < 0:
        _h1_direction_sentence = (
            "Higher shock intensity is associated with lower mean NRS responses, "
            "indicating a risk-reducing shift in portfolio managers' stance."
        )
    else:
        _h1_direction_sentence = (
            "Higher shock intensity is associated with higher mean NRS responses, "
            "indicating a risk-taking shift in portfolio managers' stance."
        )

    conc["h1_supported"]  = h1_supported
    conc["h1_verdict"]    = "Supported" if h1_supported else "Not supported"
    conc["h1_direction"]  = ("negative" if (not np.isnan(beta1) and beta1 < 0)
                              else ("positive" if not np.isnan(beta1) else "unknown"))
    conc["h1_narrative"] = (
        f"The primary OLS regression examines whether SC_total – the composite "
        f"Shock Score – is significantly associated with Net Risk Stance (NRS) after "
        f"controlling for the ShowSC treatment indicator, years of experience, and block "
        f"fixed effects. The estimated coefficient on SC_total is "
        f"β₁ = {_round4(beta1)} (robust SE = {_round4(primary.get('se', np.nan))}, "
        f"t = {_round4(h1_t)}, p = {_round4(h1_p)}, "
        f"95% CI [{_round4(h1_ci_lo)}, {_round4(h1_ci_hi)}]). "
        f"{_h1_direction_sentence} "
        f"{'At the α = 0.05 significance level, H1 is supported: SC_total is a statistically significant predictor of NRS.' if h1_supported else 'At the α = 0.05 significance level, H1 is not supported: the evidence does not suggest a statistically significant association between SC_total and NRS in this sample.'} "
        f"Robustness checks using quintile dummies, respondent fixed effects, "
        f"decomposed components, and an interaction term are reported in Table 5.3."
    )

    # H2
    opt_b_reg = h2.get("opt_b_reg", pd.DataFrame())
    h2_primary = {}
    if not opt_b_reg.empty:
        pr_row = opt_b_reg[
            (opt_b_reg.get("method", pd.Series()) == "option_b_individual") &
            (opt_b_reg.get("outcome", pd.Series()) == "portfolio_return")
        ]
        if len(pr_row) > 0:
            h2_primary = pr_row.iloc[0].to_dict()

    tau = h2_primary.get("tau", np.nan)
    h2_p = h2_primary.get("p", np.nan)
    h2_supported = (not np.isnan(h2_p)) and (h2_p < ALPHA)
    conc["h2_supported"] = h2_supported
    conc["h2_verdict"]   = "Supported" if h2_supported else "Not supported"
    conc["tau"]          = tau
    conc["h2_p"]         = h2_p

    ret_diff    = h2.get("return_differential", np.nan)
    dollar_imp  = h2.get("dollar_impact", np.nan)
    ret_sc0     = h2.get("collective_return_sc0", np.nan)
    ret_sc1     = h2.get("collective_return_sc1", np.nan)

    if h2_supported and not np.isnan(tau):
        if tau > 0:
            _h2_support_sentence = (
                "H2 is supported: the Shock Score dashboard is associated with a statistically "
                "significant improvement in risk-adjusted portfolio outcomes, supporting the case "
                "for structured decision support during information shocks."
            )
        else:
            _h2_support_sentence = (
                "H2 is statistically significant (p < 0.05) but the sign of the treatment effect "
                "is negative (tau < 0), indicating that dashboard exposure is associated with worse "
                "portfolio outcomes in the current sample. This unexpected result warrants further "
                "investigation before any deployment recommendation is made."
            )
    else:
        _h2_support_sentence = (
            "H2 is not supported in this sample: the evidence does not suggest a statistically "
            "significant difference in portfolio outcomes between the treatment and control conditions. "
            "Validation on a larger professional sample is recommended."
        )

    _dollar_part = (
        f" On an assumed AUM of $100M, the ShowSC=1 collective portfolio generated a "
        f"dollar return differential of ${dollar_imp:,.0f} relative to the ShowSC=0 "
        f"portfolio over the evaluation window."
    ) if not np.isnan(dollar_imp) else ""

    conc["h2_narrative"] = (
        f"Hypothesis H2 is tested using individual-portfolio regressions (Option B). "
        f"Per respondent, portfolio returns are constructed from NRS-weighted horizon "
        f"returns across the four scenarios assigned to each condition. The estimated "
        f"treatment effect on portfolio return is tau = {_round4(tau)} "
        f"(robust SE = {_round4(h2_primary.get('se', np.nan))}, "
        f"t = {_round4(h2_primary.get('t', np.nan))}, p = {_round4(h2_p)}, "
        f"95% CI [{_round4(h2_primary.get('ci_lo', np.nan))}, "
        f"{_round4(h2_primary.get('ci_hi', np.nan))}]; "
        f"Cohen's d = {_round4(h2_primary.get('cohens_d', np.nan))}). "
        f"{_h2_support_sentence} "
        f"The collective portfolio analysis (Option A, descriptive only; "
        f"**caution: both portfolios draw from the same respondent pool – inference is non-independent**) "
        f"yields a return of {_round4(ret_sc0)}% for the control condition and "
        f"{_round4(ret_sc1)}% for the treatment condition, corresponding to a "
        f"return differential of {_round4(ret_diff)}%.{_dollar_part}"
    )

    return conc


# ---------------------------------------------------------------------------
# Section 8 – Write thesis_results.md
# ---------------------------------------------------------------------------

def _md_table(df: pd.DataFrame, round_dp: int = 4) -> str:
    """Convert DataFrame to markdown pipe table."""
    df = df.copy()
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].apply(lambda x: round(x, round_dp) if pd.notna(x) else "")
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep    = "| " + " | ".join("---" for _ in df.columns) + " |"
    rows   = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row.values) + " |")
    return "\n".join([header, sep] + rows)


def write_results_md(
    df: pd.DataFrame,
    desc: dict,
    norm: dict,
    h1: dict,
    h2: dict,
    conc: dict,
    horizon_returns: pd.DataFrame,
    scenarios: pd.DataFrame,
    alignment: dict | None = None,
) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    n_total     = desc["n_respondents"]
    n_obs       = len(df)
    n_suff      = int(horizon_returns["data_sufficient"].sum())
    h1_v        = conc["h1_verdict"]
    h2_v        = conc["h2_verdict"]

    # Shared derived values used across multiple blocks
    _beta1     = h1.get("primary", {}).get("beta1", np.nan)
    _h1_supp   = conc["h1_supported"]
    _h1_dir    = conc.get("h1_direction", "unknown")
    _tau       = conc.get("tau", np.nan)
    _h2_p      = conc.get("h2_p", np.nan)
    _h2_supp   = conc["h2_supported"]
    _ret_diff  = h2.get("return_differential", np.nan)
    _dollar    = h2.get("dollar_impact", np.nan)
    _dollar_v  = _dollar if not np.isnan(_dollar) else 0

    lines = [
        "# Thesis Results – Auto-generated",
        f"**Generated:** {ts}",
        f"**Panel:** {n_total} respondents ({n_obs} observations)",
        f"**Data sufficiency:** {n_suff}/24 scenarios",
        f"**H1 verdict:** {h1_v}",
        f"**H2 verdict:** {h2_v}",
        "",
    ]

    def block(section_id: str, content: str) -> str:
        return (
            f"<!-- RESULTS:BEGIN:{section_id} -->\n"
            f"{content}\n"
            f"<!-- RESULTS:END:{section_id} -->"
        )

    # ---- s5_2_1_respondents ----
    freq_df = desc.get("freq_demographics", pd.DataFrame())
    inst_rows = freq_df[freq_df["field"] == "institution_type"] if not freq_df.empty else pd.DataFrame()
    aum_rows  = freq_df[freq_df["field"] == "aum_category"]    if not freq_df.empty else pd.DataFrame()

    resp_lines = [
        f"The final analysis sample comprises {n_total} respondents "
        f"yielding {n_obs} scenario-level observations across three blocks.",
        "",
        f"Table 5.1 presents the demographic profile of the achieved sample. "
        f"Respondents report a mean of {_round4(desc['exp_mean'])} years of experience "
        f"(median = {_round4(desc['exp_median'])}, SD = {_round4(desc['exp_sd'])}, "
        f"range = {_round4(desc['exp_min'])}–{_round4(desc['exp_max'])}). ",
        "",
        "**Table 5.1: Respondent Demographics**",
        "",
        "| Characteristic | Metric | Value |",
        "|---|---|---|",
        f"| Years of experience | Mean | {_round4(desc['exp_mean'])} |",
        f"| Years of experience | Median | {_round4(desc['exp_median'])} |",
        f"| Years of experience | SD | {_round4(desc['exp_sd'])} |",
        f"| Years of experience | Range | {_round4(desc['exp_min'])}–{_round4(desc['exp_max'])} |",
    ]
    for _, row in inst_rows.iterrows():
        resp_lines.append(f"| Institution type | {row['value']} | {row['count']} ({row['pct']}%) |")
    for _, row in aum_rows.iterrows():
        resp_lines.append(f"| AUM category | {row['value']} | {row['count']} ({row['pct']}%) |")
    resp_lines.append("")
    resp_lines.append("![Respondent demographics](figures/fig_demographics.png)")
    s521 = block("s5_2_1_respondents", "\n".join(resp_lines))

    # ---- s5_2_2_data ----
    nrs_s = desc.get("nrs_summary", pd.DataFrame())
    mc = desc.get("manipulation_check", {})
    mc_str = "; ".join(f"{k}: {v}" for k, v in mc.items()) if mc else "N/A"
    ur_mean = _round4(desc.get("usefulness_mean", np.nan))
    ur_med  = _round4(desc.get("usefulness_median", np.nan))
    ur_sd   = _round4(desc.get("usefulness_sd", np.nan))

    s522_lines = []
    if not nrs_s.empty:
        ov = nrs_s[nrs_s["condition"] == "overall"].iloc[0]
        c0 = nrs_s[nrs_s["condition"] == "ShowSC=0"].iloc[0]
        c1 = nrs_s[nrs_s["condition"] == "ShowSC=1"].iloc[0]
        s522_lines += [
            f"Across all {n_obs} observations, the mean NRS is {_round4(ov['mean'])} "
            f"(median = {_round4(ov['median'])}, SD = {_round4(ov['sd'])}, "
            f"range = {int(ov['min'])}–{int(ov['max'])}). "
            f"In the control condition (ShowSC = 0), the mean NRS is {_round4(c0['mean'])} "
            f"(SD = {_round4(c0['sd'])}, n = {int(c0['n'])}). "
            f"In the treatment condition (ShowSC = 1), the mean NRS is {_round4(c1['mean'])} "
            f"(SD = {_round4(c1['sd'])}, n = {int(c1['n'])}). "
            f"The mean NRS difference (ShowSC=1 minus ShowSC=0) is {_round4(desc.get('nrs_mean_diff', np.nan))}.",
            "",
        ]
    sc_s = desc.get("scen_summary", pd.DataFrame())
    if not sc_s.empty:
        sc_row = sc_s[sc_s["metric"] == "sc_total"]
        if len(sc_row) > 0:
            r = sc_row.iloc[0]
            s522_lines.append(
                f"SC_total is a standardised PCA composite score (first principal component of "
                f"AC_e, SE_e, AI_e, and ES_raw). By construction, the sample mean is approximately zero. "
                f"The meaningful descriptive statistics are the range "
                f"(min = {_round4(r['min'])}, max = {_round4(r['max'])}) and standard deviation "
                f"(SD = {_round4(r['sd'])}), which characterise the spread of shock intensity "
                f"across the twenty-four scenarios. "
                f"Manipulation check responses: {mc_str}. "
                f"For ShowSC = 1 respondents, the mean usefulness rating is {ur_mean} "
                f"(median = {ur_med}, SD = {ur_sd})."
            )
    s522_lines += [
        "",
        "![NRS distribution](figures/fig_nrs_distribution.png)",
        "![NRS by condition](figures/fig_nrs_by_condition.png)",
        "![SC_total distribution](figures/fig_sc_distribution.png)",
    ]
    s522 = block("s5_2_2_data", "\n".join(s522_lines))

    # ---- s5_3_scenarios ----
    scen_tbl_cols = [
        "scenario_id", "block_id", "ticker", "company_name", "gics_sector",
        "event_date", "event_type", "sc_total", "horizon_bucket",
        "sentiment_direction",
    ]
    scen_avail = [c for c in scen_tbl_cols if c in scenarios.columns]
    scen_tbl = scenarios[scen_avail].copy()
    if "sc_total" in scen_tbl.columns:
        scen_tbl["sc_total"] = pd.to_numeric(scen_tbl["sc_total"], errors="coerce").round(4)
    s523_lines = [
        "Table 5.2 documents the final scenario selection across the three survey blocks.",
        "", _md_table(scen_tbl), "",
    ]
    s523 = block("s5_3_scenarios", "\n".join(s523_lines))

    # ---- s5_4_normality ----
    norm_df = norm.get("norm_df", pd.DataFrame())
    clt     = norm.get("clt_applies", False)
    cons    = norm.get("mean_pairwise_corr", np.nan)
    n_resp_norm = norm.get("n_respondents", 0)
    s54_lines = []
    if not norm_df.empty:
        for _, row in norm_df.iterrows():
            rejected = row.get("normal_rejected")
            s54_lines.append(
                f"For the {row['group']} group (n = {int(row['n'])}): "
                f"skewness = {_round4(row['skewness'])}, excess kurtosis = {_round4(row['excess_kurtosis'])}, "
                f"Shapiro-Wilk W = {_round4(row['shapiro_w'])}, p = {_round4(row['shapiro_p'])} "
                f"({'normality rejected' if rejected else 'normality not rejected'} at α = 0.05)."
            )
    s54_lines += [
        "",
        f"Central limit theorem applicability: the sample comprises {n_resp_norm} respondents, "
        f"{'exceeding' if clt else 'below'} the N = 30 threshold. "
        f"{'Parametric inference is therefore warranted even if the NRS distribution departs from normality.' if clt else 'Given the small sample size, parametric inference should be interpreted with caution.'}",
        "",
        f"Inter-scenario consistency (mean pairwise Pearson correlation across respondent × scenario "
        f"response matrix): r̄ = {_round4(cons)}. Note: this is not Cronbach's alpha. The NRS is a "
        f"single-item measure; traditional internal consistency coefficients do not apply. "
        f"The mean pairwise correlation is reported as a descriptive consistency proxy only.",
    ]
    s54 = block("s5_4_normality", "\n".join(s54_lines))

    # ---- s5_5_1_h1 ----
    primary = h1.get("primary", {})
    rob_df  = h1.get("robustness", pd.DataFrame())
    s551_lines = [conc.get("h1_narrative", ""), "", "**Table 5.3: H1 Main Regression Results**", ""]
    if not rob_df.empty:
        s551_lines += [_md_table(rob_df), ""]
    s551 = block("s5_5_1_h1", "\n".join(s551_lines))

    # ---- s5_5_2_h2 ----
    n_sortino_elig = h2.get("n_sortino_eligible", 0)
    n_b_pairs_     = h2.get("n_option_b_pairs", 0)
    s552_lines = [conc.get("h2_narrative", ""), "", "**Table 5.4: H2 Portfolio Analysis Results**", ""]
    opt_b_reg = h2.get("opt_b_reg", pd.DataFrame())
    if not opt_b_reg.empty:
        s552_lines += [_md_table(opt_b_reg), ""]
    s552_lines.append(
        f"**Note on Sortino ratio:** The Sortino ratio is computed only for respondent-condition "
        f"pairs that yield at least one negative portfolio return. In the current sample, this "
        f"applies to {n_sortino_elig} of {n_b_pairs_} respondent-condition pairs."
    )
    s552_lines += [
        "",
        "**Non-independence warning (Option A):** The collective portfolios in the descriptive "
        "Option A analysis are constructed from the same respondent pool. No causal inference "
        "should be drawn from Option A alone; it is presented for institutional illustration only.",
        "",
        "![Sharpe comparison](figures/fig_sharpe_comparison.png)",
    ]
    s552 = block("s5_5_2_h2", "\n".join(s552_lines))

    # ---- s5_6_1_impact ----
    if np.isnan(_beta1):
        _impact_effect_sentence = "The regression estimate for SC_total could not be computed."
    elif _h1_supp and _beta1 < 0:
        _impact_effect_sentence = (
            f"The statistically significant negative association (beta1 = {_round4(_beta1)}) "
            f"indicates that higher shock intensity shifts managers toward reduced risk exposure "
            f"(lower NRS), consistent with loss-aversion predictions from prospect theory "
            f"(Kahneman and Tversky, 1979)."
        )
    elif _h1_supp and _beta1 > 0:
        _impact_effect_sentence = (
            f"The statistically significant positive association (beta1 = {_round4(_beta1)}) "
            f"indicates that higher shock intensity shifts managers toward elevated risk exposure "
            f"(higher NRS), potentially reflecting attention-based overreaction or overconfidence biases."
        )
    else:
        _impact_effect_sentence = (
            f"The association between SC_total and NRS is not statistically significant in the "
            f"current sample (beta1 = {_round4(_beta1)}, p = {_round4(primary.get('p', np.nan))}). "
            f"The absence of significance may reflect insufficient statistical power, heterogeneous "
            f"response patterns, or genuine non-linearity that a linear model does not capture."
        )
    s561 = block("s5_6_1_impact", (
        f"The results are evaluated against the behavioural finance literature suggesting that "
        f"external information shocks exert a systematic influence on portfolio managers' "
        f"risk-stance decisions. {_impact_effect_sentence} "
        f"This result is interpreted cautiously given the sample composition and potential "
        f"survivorship effects in the volunteer sample. "
        f"Prospect theory (Kahneman and Tversky, 1979) would predict asymmetric responses to "
        f"negative versus positive shocks; the current analysis does not decompose effects by "
        f"shock direction, which is noted as an avenue for future research."
    ))

    # ---- s5_6_2_incremental ----
    if _h2_supp and not np.isnan(_tau):
        if _tau > 0:
            _incremental_sentence = (
                "The results support the incremental value of the Shock Score dashboard: "
                "dashboard exposure is associated with statistically significantly better portfolio "
                "outcomes (tau > 0), consistent with structured decision support moderating "
                "behavioural biases during information shocks."
            )
        else:
            _incremental_sentence = (
                "The results are statistically significant but the treatment effect is negative "
                "(tau < 0), indicating that dashboard exposure is associated with worse portfolio "
                "outcomes in the current sample. This unexpected result warrants further "
                "investigation before deployment is considered."
            )
    else:
        _incremental_sentence = (
            "The results do not support a statistically significant incremental effect of the "
            "Shock Score dashboard on portfolio outcomes in the current sample. "
            "Validation on a larger, fully recruited professional sample is the recommended next step."
        )

    if not np.isnan(_ret_diff):
        if _ret_diff > 0:
            _option_a_sentence = (
                f"The Option A collective portfolio analysis (descriptive only; non-independence caveat applies) "
                f"shows a positive return differential of {_round4(_ret_diff)}% in favour of the treatment "
                f"condition, corresponding to a dollar impact of ${_dollar_v:,.0f} on an assumed AUM of $100M."
            )
        else:
            _option_a_sentence = (
                f"The Option A collective portfolio analysis (descriptive only; non-independence caveat applies) "
                f"shows a non-positive return differential of {_round4(_ret_diff)}% for the treatment condition, "
                f"corresponding to a dollar impact of ${_dollar_v:,.0f} on an assumed AUM of $100M. "
                f"The treatment portfolio did not outperform the control portfolio in the descriptive collective analysis."
            )
    else:
        _option_a_sentence = "The Option A collective return differential could not be computed."

    s562 = block("s5_6_2_incremental", (
        f"The incremental effect of the Shock Score dashboard (ShowSC) on simulated portfolio "
        f"outcomes is evaluated through the Option B individual-portfolio regression. "
        f"{_incremental_sentence} "
        f"{_option_a_sentence} "
        f"This figure is presented for descriptive illustration and is subject to the "
        f"non-independence caveat noted in Section 5.5.2."
    ))

    # ---- s5_7_interim ----
    if _h1_supp:
        _h1_interim = (
            f"**{conc['h1_verdict'].lower()}** "
            f"(beta1 = {_round4(_beta1)}, p = {_round4(primary.get('p', np.nan))}; "
            f"direction: {'risk-reducing' if _h1_dir == 'negative' else 'risk-taking'})"
        )
    else:
        _h1_interim = (
            f"**{conc['h1_verdict'].lower()}** "
            f"(beta1 = {_round4(_beta1)}, p = {_round4(primary.get('p', np.nan))})"
        )

    if _h2_supp and not np.isnan(_tau):
        if _tau > 0:
            _h2_interim = (
                f"**{conc['h2_verdict'].lower()}** "
                f"(tau = {_round4(_tau)}, p = {_round4(_h2_p)}; direction: performance-improving)"
            )
        else:
            _h2_interim = (
                f"**{conc['h2_verdict'].lower()}** but with a negative treatment effect "
                f"(tau = {_round4(_tau)}, p = {_round4(_h2_p)}; see caution in Section 5.6.2)"
            )
    else:
        _h2_interim = (
            f"**{conc['h2_verdict'].lower()}** "
            f"(tau = {_round4(_tau)}, p = {_round4(_h2_p)})"
        )

    s57 = block("s5_7_interim", (
        f"The interim conclusions for Chapter 5 are as follows. "
        f"H1 – that SC_total is significantly associated with NRS – is {_h1_interim}. "
        f"H2 – that the Shock Score dashboard moderates the risk-return profile of simulated portfolios – "
        f"is {_h2_interim} in the Option B individual-portfolio regression. "
        f"Both findings are contingent on the current sample composition and are subject to revision "
        f"upon completion of the full survey. Robustness checks for H1 and the Option A descriptive "
        f"analysis for H2 are consistent in direction with the primary results."
    ))

    # ---- s5_8_conclusion ----
    s58 = block("s5_8_conclusion", (
        f"Chapter 5 has presented the empirical results of the within-subject survey experiment "
        f"designed to examine the influence of external information shocks on equity portfolio "
        f"manager decision-making and the moderating effect of the Shock Score decision-support tool. "
        f"Descriptive statistics characterise the achieved sample and the SC_total distribution "
        f"across the twenty-four scenarios. Normality assessments confirm "
        f"{'that parametric inference is appropriate given the sample size.' if norm.get('clt_applies') else 'that the sample size warrants caution in parametric inference.'} "
        f"H1 is {conc['h1_verdict'].lower()} and H2 is {conc['h2_verdict'].lower()} at the α = 0.05 "
        f"significance level. Chapter 6 synthesises these findings within the broader research context "
        f"and develops recommendations for practice."
    ))

    # ---- s6_2_summary ----
    s62 = block("s6_2_summary", (
        f"The primary research contributes empirical evidence on two hypotheses. "
        f"H1 posits that SC_total – a PCA-based composite of article count, sentiment extremity, "
        f"attention intensity, and event-type severity – is a statistically significant predictor "
        f"of portfolio managers' Net Risk Stance. The evidence {('supports' if conc['h1_supported'] else 'does not support')} this hypothesis "
        f"(β₁ = {_round4(primary.get('beta1', np.nan))}, p = {_round4(primary.get('p', np.nan))}). "
        f"H2 posits that exposure to the Shock Score dashboard improves the risk-return profile "
        f"of simulated portfolios. The Option B individual-portfolio regression {('supports' if conc['h2_supported'] else 'does not support')} "
        f"this hypothesis at the α = 0.05 level. "
        f"These findings are based on {n_total} respondents ({n_obs} observations)."
    ))

    # ---- s6_3_conclusions ----
    s63 = block("s6_3_conclusions", (
        f"This research set out to investigate whether external financial information shocks cause "
        f"systematic shifts in equity portfolio managers' decision-making, and whether a structured "
        f"decision-support tool – the Shock Score – can moderate those responses. "
        f"The evidence {'is consistent with' if conc['h1_supported'] else 'does not strongly support'} "
        f"the proposition that shock intensity, as measured by SC_total, is associated with changes "
        f"in risk stance. The evidence {'is consistent with' if conc['h2_supported'] else 'does not strongly support'} "
        f"the proposition that the Shock Score dashboard improves portfolio-level outcomes. "
        f"Collectively, the results are "
        f"{'directionally consistent with the thesis framework and provide a basis for cautious optimism about structured decision support in professional investment contexts.' if (conc['h1_supported'] or conc['h2_supported']) else 'inconclusive in the current sample. Replication with a larger, fully real respondent pool is the primary recommended next step.'}"
    ))

    # ---- s6_4_recommendations ----
    if _h1_supp:
        _rec_manager = (
            "The results are consistent with the view that information shock intensity is "
            "associated with shifts in risk stance. Managers are encouraged to adopt structured "
            "pre-commitment protocols for periods of elevated shock intensity, as operationalised "
            "by the Monitor, Review, and Halt thresholds embedded in the Shock Score dashboard. "
            "The dashboard's three-tier protocol structure provides an operationally tractable "
            "debiasing mechanism that does not require extensive behavioural training to implement."
        )
    else:
        _rec_manager = (
            "While the current evidence does not establish a statistically significant association "
            "between shock intensity and risk stance, behavioural finance theory and directional "
            "evidence suggest that structured pre-commitment protocols may be prudent during periods "
            "of elevated shock intensity. The Monitor, Review, and Halt thresholds operationalise "
            "this in a tractable, low-training format."
        )

    if _h2_supp and not np.isnan(_tau) and _tau > 0:
        _rec_deployment = (
            "The current evidence is consistent with the value of the Shock Score dashboard in "
            "moderating portfolio managers' responses to information shocks. Prior to full deployment, "
            "the dashboard should be validated on a larger, independently recruited sample of "
            "professional portfolio managers with a pre-registered design and a target N >= 100 "
            "verified professionals. Platform integration (e.g., embedding the dashboard in existing "
            "OMS or EMS interfaces) is recommended over standalone survey administration for "
            "ecological validity."
        )
    elif _h2_supp and not np.isnan(_tau) and _tau < 0:
        _rec_deployment = (
            "The current evidence does not support deployment: the treatment effect is statistically "
            "significant but negative, indicating that dashboard exposure is associated with worse "
            "portfolio outcomes in the current sample. Further investigation is required before any "
            "deployment recommendation is made. A redesign and validation on a larger independent "
            "sample is the recommended next step."
        )
    else:
        _rec_deployment = (
            "Prior to deployment, the Shock Score dashboard should be validated on a larger, "
            "independently recruited sample of professional portfolio managers. The current "
            "study's limitations – including the sample size and volunteer composition – should be "
            "addressed through a pre-registered replication with a target N >= 100 verified "
            "professionals. Platform integration (e.g., OMS or EMS interfaces) is recommended "
            "over standalone survey administration for ecological validity."
        )

    s64 = block("s6_4_recommendations", (
        f"**For individual portfolio managers.** {_rec_manager}\n\n"
        f"**For risk governance.** Risk committees and Chief Investment Officers may consider "
        f"integrating real-time shock monitoring – indexed by a composite such as SC_total – "
        f"into existing risk oversight frameworks. The Shock Score provides a transparent, "
        f"auditable rationale for discretionary trading restrictions during high-intensity events, "
        f"supporting governance accountability without removing managerial discretion.\n\n"
        f"**For institutional deployment.** {_rec_deployment}"
    ))

    # ---- s5_diagnostic_alignment ----
    alignment = alignment or {}
    aln_df   = alignment.get("alignment_df", pd.DataFrame())
    aln_rate = alignment.get("overall_alignment_rate", np.nan)
    if not aln_df.empty:
        _aln_lines = [
            f"As a diagnostic check, the alignment between respondents' NRS direction "
            f"(buy: NRS > 4; sell: NRS < 4; neutral: NRS = 4) and the sentiment-expected "
            f"direction (Negative sentiment expected sell; Positive expected buy) is assessed "
            f"across all {n_obs} observations.",
            "",
            f"Overall alignment rate: {_round4(aln_rate)} "
            f"({int(aln_df.loc[aln_df['group'] == 'overall', 'n_aligned'].iloc[0]) if 'overall' in aln_df['group'].values else 'N/A'} "
            f"of {int(aln_df.loc[aln_df['group'] == 'overall', 'n'].iloc[0]) if 'overall' in aln_df['group'].values else 'N/A'} observations).",
            "",
            "**Table 5.5: NRS–Sentiment Alignment by Group**",
            "",
            _md_table(aln_df),
            "",
            "An alignment rate above 0.50 indicates that respondents' risk-stance direction "
            "is more often consistent with the implied sentiment direction than not. Rates "
            "substantially below 0.50 would suggest systematic contrarian reactions or "
            "misalignment between the shock characterisation and respondent interpretation.",
        ]
        s5_diag = block("s5_diagnostic_alignment", "\n".join(_aln_lines))
    else:
        s5_diag = block("s5_diagnostic_alignment",
                        "Alignment diagnostic could not be computed (missing sentiment_direction or nrs column).")

    # Assemble file
    sections = [s521, s522, s523, s54, s551, s552, s561, s5_diag, s562, s57, s58, s62, s63, s64]
    lines.extend(sections)

    RESULTS_MD_PATH.write_text("\n\n".join(lines), encoding="utf-8")
    print(f"\nResults written to {RESULTS_MD_PATH}")


# ---------------------------------------------------------------------------
# Section 9 – Stdout summary
# ---------------------------------------------------------------------------

def print_summary(desc: dict, h1: dict, h2: dict, conc: dict,
                  horizon_returns: pd.DataFrame,
                  n_figs: int, n_tables: int) -> None:
    primary = h1.get("primary", {})
    opt_b_reg = h2.get("opt_b_reg", pd.DataFrame())
    tau, h2_p = np.nan, np.nan
    if not opt_b_reg.empty:
        pr_row = opt_b_reg[opt_b_reg.get("outcome", pd.Series()) == "portfolio_return"]
        if len(pr_row) > 0:
            tau  = pr_row.iloc[0].get("tau", np.nan)
            h2_p = pr_row.iloc[0].get("p", np.nan)

    n_suff = int(horizon_returns["data_sufficient"].sum())
    ret_diff   = h2.get("return_differential", np.nan)
    dollar_imp = h2.get("dollar_impact", np.nan)

    print("\n" + "=" * 61)
    print("Statistical Analysis Complete")
    print("=" * 61)
    print(f"  Respondents       : {desc['n_respondents']} total")
    print(f"  Observations      : {desc['nrs_summary'].loc[desc['nrs_summary']['condition'] == 'overall', 'n'].values[0] if not desc.get('nrs_summary', pd.DataFrame()).empty else 'N/A'}")
    print(f"  Data sufficiency  : {n_suff}/24 scenarios (H2 only)")
    print(f"  H1 (SC_total->NRS): beta1 = {_round4(primary.get('beta1', np.nan))}, p = {_round4(primary.get('p', np.nan))} -> {conc['h1_verdict']}")
    print(f"  H2 Option B       : tau  = {_round4(tau)}, p = {_round4(h2_p)} -> {conc['h2_verdict']}")
    diff_str = f"{_round4(ret_diff)}%" if not np.isnan(ret_diff) else "N/A"
    dol_str  = f"${dollar_imp:,.0f}" if not np.isnan(dollar_imp) else "N/A"
    print(f"  H2 Option A       : Return differential = {diff_str}, Dollar impact = {dol_str}")
    print(f"  Outputs           : {RESULTS_MD_PATH}")
    print(f"                      {FIGURES_DIR}/ ({n_figs} files)")
    print(f"                      {TABLES_DIR}/  ({n_tables} files)")
    print("=" * 61)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-augment",    action="store_true")
    parser.add_argument("--skip-figures",  action="store_true")
    args = parser.parse_args()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading and enriching panel data...")
    df = load_and_enrich()
    print(f"  {len(df)} rows loaded.")

    print("\nLoading scenario metadata...")
    scenarios = pd.read_csv(METADATA_PATH)
    # Enrich scenarios with shock score data
    ss = pd.read_csv(SHOCK_SCORE_PATH)
    scenarios = scenarios.merge(ss, on=["scenario_id", "ticker", "event_date"], how="left")

    print("\nComputing horizon returns from price data...")
    horizon_returns = load_horizon_returns(scenarios)

    print("\nComputing descriptive statistics...")
    desc = compute_descriptives(df, skip_figures=args.skip_figures)

    print("\nComputing normality and reliability...")
    norm = compute_normality(df)

    print("\nRunning H1 regression...")
    h1 = run_h1_regression(df)

    print("\nRunning H2 portfolio analysis...")
    h2 = run_h2_analysis(df, horizon_returns, skip_figures=args.skip_figures)

    print("\nGenerating conclusions...")
    conc = generate_conclusions(h1, h2, desc, norm)

    print("\nComputing NRS/sentiment alignment diagnostic...")
    alignment = compute_nrs_sentiment_alignment(df)

    print("\nWriting thesis_results.md...")
    write_results_md(df, desc, norm, h1, h2, conc, horizon_returns, scenarios, alignment=alignment)

    n_figs   = len(list(FIGURES_DIR.glob("*.png")))
    n_tables = len(list(TABLES_DIR.glob("*.csv")))
    print_summary(desc, h1, h2, conc, horizon_returns, n_figs, n_tables)

    primary = h1.get("primary", {})
    opt_b_rows = h2.get("opt_b_reg", pd.DataFrame())
    sharpe_row = (
        opt_b_rows[opt_b_rows["outcome"] == "sharpe_ratio"].iloc[0].to_dict()
        if not opt_b_rows.empty and "outcome" in opt_b_rows.columns
           and (opt_b_rows["outcome"] == "sharpe_ratio").any()
        else {}
    )
    append_run_log(
        script="8_statistical_analysis.py",
        parameters={
            "alpha": ALPHA, "nrs_neutral": NRS_NEUTRAL,
            "weight_step": WEIGHT_STEP, "rf_annual": RF_ANNUAL,
            "aum": AUM, "horizon_days": HORIZON_DAYS,
            "min_years_experience": MIN_YEARS_EXPERIENCE,
            "seed": SEED,
        },
        inputs=[
            {"file": str(PANEL_PATH),       "sha256": _sha256_file(PANEL_PATH)},
            {"file": str(SHOCK_SCORE_PATH), "sha256": _sha256_file(SHOCK_SCORE_PATH)},
        ],
        outputs=[
            {"file": str(RESULTS_MD_PATH), "rows": None,
             "sha256": _sha256_file(RESULTS_MD_PATH)},
            {"file": str(TABLES_DIR),      "rows": None, "sha256": "dir"},
            {"file": str(FIGURES_DIR),     "rows": None, "sha256": "dir"},
        ],
        notes=(
            f"H1: beta1={primary.get('beta1', 'n/a')}, p={primary.get('p', 'n/a')} "
            f"({'supported' if primary.get('p', 1) < ALPHA else 'not supported'}). "
            f"H2: tau={sharpe_row.get('tau', 'n/a')}, p={sharpe_row.get('p', 'n/a')} "
            f"({'supported' if sharpe_row.get('h2_supported') else 'not supported'})."
        ),
    )


if __name__ == "__main__":
    main()
