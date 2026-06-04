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
import json
import os
import re
import sys
import warnings

from datetime import datetime
from sklearn.decomposition import PCA as _PCA
from sklearn.preprocessing import StandardScaler as _StandardScaler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
from scipy import stats

try:
    import pingouin as pg
    _PINGOUIN_AVAILABLE = True
except ImportError:
    _PINGOUIN_AVAILABLE = False

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
    """Format a float to 4 decimal places. If 0 < x < 0.00005, returns '<0.0001'."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "N/A"
    # For very small positive p-values or coefficients
    if 0 < x < 0.00005:
        return "<0.0001"
    # For very small negative values (if applicable)
    if -0.00005 < x < 0:
        return ">-0.0001"
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
    for col in ["nrs", "sc_total", "show_sc", "block_id", "years_experience"]:
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
        "respondent_id", "years_experience", "years_experience_label",
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

    # Experience is an ordinal categorical band. The numeric years_experience
    # column is unreliable (most rows are NaN), so the label column is
    # authoritative and is reported as an ordered frequency distribution.
    _EXP_ORDER = ["less than 2", "2-5", "6-10", "11-20", "more than 20"]
    _EXP_DISPLAY = {
        "less than 2": "Less than 2", "2-5": "2–5", "6-10": "6–10",
        "11-20": "11–20", "more than 20": "More than 20",
    }

    def _norm_exp_label(s: object) -> str:
        return re.sub(r"[-‐‑‒–—―−﹣－]", "-", str(s)).strip().lower()

    exp_freq_rows = []
    if "years_experience_label" in rdf.columns:
        vc_exp = rdf["years_experience_label"].value_counts(dropna=False)
        ordered = sorted(
            vc_exp.items(),
            key=lambda kv: _EXP_ORDER.index(_norm_exp_label(kv[0]))
            if _norm_exp_label(kv[0]) in _EXP_ORDER else 99,
        )
        for lbl, cnt in ordered:
            disp = "Unknown" if pd.isna(lbl) else _EXP_DISPLAY.get(_norm_exp_label(lbl), str(lbl))
            exp_freq_rows.append({
                "label": disp, "count": int(cnt),
                "pct": round(cnt / n_total_resp * 100, 2),
            })
    desc["exp_freq"] = exp_freq_rows

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

    # Experience by band (categorical; the numeric column is unreliable)
    exp_freq = desc.get("exp_freq", [])
    if exp_freq:
        labels = [r["label"] for r in exp_freq]
        counts = [r["count"] for r in exp_freq]
        ax1.bar(labels, counts, color="#2c7bb6", edgecolor="white")
        ax1.set_ylabel("Count")
        ax1.set_title("(a) Distribution of respondent experience")
        ax1.tick_params(axis="x", labelrotation=20)
        for _lbl in ax1.get_xticklabels():
            _lbl.set_ha("right")
    ax1.set_xlabel("Years of experience")
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
    work = scen_df.copy()
    work["sc_total"] = pd.to_numeric(work["sc_total"], errors="coerce")
    work = work.dropna(subset=["sc_total"])
    sc = work["sc_total"]

    fig, ax = plt.subplots(figsize=(9, 6))
    counts, edges, _ = ax.hist(sc, bins=10, color="#abd9e9", edgecolor="#2c7bb6", density=True)
    # Normal overlay
    x = np.linspace(sc.min() - 1, sc.max() + 1, 200)
    ax.plot(x, stats.norm.pdf(x, sc.mean(), sc.std()), color="#d7191c", linewidth=2, label="Normal")

    # List each bin's scenarios as a vertical column inside the bar, instead of
    # labelling every point at y=0 (which overlapped badly around the mode).
    if "ticker" in work.columns:
        bin_idx = np.clip(np.digitize(sc.to_numpy(), edges[1:-1]), 0, len(edges) - 2)
        work = work.assign(_bin=bin_idx)
        for b, grp in work.groupby("_bin"):
            center = (edges[b] + edges[b + 1]) / 2
            tickers = grp.sort_values("sc_total")["ticker"].astype(str).tolist()
            ax.text(center, 0.005, "\n".join(tickers), fontsize=6.5, ha="center",
                    va="bottom", color="black", linespacing=1.3)

    ax.set_xlabel("Shock Score")
    ax.set_ylabel("Density")
    ax.set_title("Shock Score distribution across scenarios")
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
    sc0 = pd.to_numeric(df.loc[df["show_sc"] == 0, "nrs"], errors="coerce").dropna()
    sc1 = pd.to_numeric(df.loc[df["show_sc"] == 1, "nrs"], errors="coerce").dropna()

    def _freq_table(series: pd.Series, label: str) -> pd.DataFrame:
        counts = series.value_counts().reindex(range(1, 8), fill_value=0).sort_index()
        pct    = (counts / counts.sum() * 100).round(2)
        return pd.DataFrame({
            "scale_point": counts.index,
            "group":       label,
            "count":       counts.values,
            "pct":         pct.values,
        })

    freq_overall = _freq_table(nrs_all, "Overall")
    freq_sc0     = _freq_table(sc0,     "ShowSC=0 (Control)")
    freq_sc1     = _freq_table(sc1,     "ShowSC=1 (Treatment)")
    freq_df      = pd.concat([freq_overall, freq_sc0, freq_sc1], ignore_index=True)
    freq_df.to_csv(TABLES_DIR / "tbl_nrs_frequency.csv", index=False)


    # Unique respondent count for CLT flag
    n_resp = df["respondent_id"].nunique() if "respondent_id" in df.columns else len(nrs_all)
    clt_applies = n_resp >= 30

    # ── Inter-rater reliability: ICC(2,1) per block ──
    # For each block, compute mean NRS per scenario × version (V1/V2).
    # ICC(2,1) treats scenarios as targets and versions as raters.
    # This answers: do V1 and V2 respondents agree on the relative ordering
    # and absolute level of NRS responses across scenarios within a block?
    icc_per_block    = {}
    icc_per_scenario = {}
    n_per_block      = {}

    version_col = None
    for candidate in ["version", "survey_version", "form_version", "block_version"]:
        if candidate in df.columns:
            version_col = candidate
            break

    if (version_col is not None
            and "scenario_id" in df.columns
            and "block_id"    in df.columns
            and _PINGOUIN_AVAILABLE):

        for blk in sorted(df["block_id"].dropna().unique()):
            blk_df = df[df["block_id"] == blk].copy()
            if "respondent_id" in blk_df.columns:
                n_per_block[int(blk)] = blk_df["respondent_id"].nunique()

            # Mean NRS per scenario × version — long format for pingouin
            blk_df["nrs"] = pd.to_numeric(blk_df["nrs"], errors="coerce")
            summary = (
                blk_df.groupby(["scenario_id", version_col])["nrs"]
                .mean()
                .reset_index()
                .rename(columns={"nrs": "mean_nrs"})
                .dropna()
            )

            # Need ≥ 2 scenarios and exactly 2 versions each represented
            n_scenarios = summary["scenario_id"].nunique()
            n_versions  = summary[version_col].nunique()
            if n_scenarios < 2 or n_versions < 2:
                icc_per_block[int(blk)] = np.nan
                continue

            try:
                icc_result = pg.intraclass_corr(
                    data=summary,
                    targets="scenario_id",
                    raters=version_col,
                    ratings="mean_nrs",
                    nan_policy="omit",
                )
                icc2 = icc_result[icc_result["Type"] == "ICC(A,1)"]["ICC"].values
                icc_per_block[int(blk)] = (
                    round(float(icc2[0]), 4)
                    if len(icc2) > 0 and not np.isnan(icc2[0])
                    else np.nan
                )
            except Exception:
                icc_per_block[int(blk)] = np.nan

    elif ("respondent_id" in df.columns
          and "scenario_id" in df.columns
          and "block_id"    in df.columns):
        # version column not found — populate n_per_block, leave ICC as nan
        for blk in sorted(df["block_id"].dropna().unique()):
            n_per_block[int(blk)] = df[df["block_id"] == blk]["respondent_id"].nunique()
            icc_per_block[int(blk)] = np.nan

    return {
        "freq_df":            freq_df,
        "clt_applies":        clt_applies,
        "n_respondents":      n_resp,
        "icc_per_block":      icc_per_block,
        "icc_per_scenario":   icc_per_scenario,
        "n_per_block":        n_per_block,
        "residual_normality": {},   # populated by run_h1_regression()
        "norm_df":            pd.DataFrame(),
        "mean_pairwise_corr": np.nan,
        "cronbach_per_block": {},
    }


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
    reg_cols = [
        "nrs", "sc_total", "show_sc", "exp_cat", "block_id", "sentiment_direction",
        "investment_mandate", "discretionary_authority",
        "event_type", "market_regime", "scenario_position",
    ]
    reg = df[[c for c in reg_cols if c in df.columns]].copy()
    reg["nrs"]      = pd.to_numeric(reg["nrs"],      errors="coerce")
    reg["sc_total"] = pd.to_numeric(reg["sc_total"], errors="coerce")
    reg["show_sc"]  = pd.to_numeric(reg["show_sc"],  errors="coerce")
    reg["block_id"] = pd.to_numeric(reg["block_id"], errors="coerce")
    reg = reg.dropna(subset=["nrs", "sc_total", "show_sc", "block_id"])

    # Experience dummies (5-10yr reference, explicitly dropped)
    exp_dummies = pd.get_dummies(reg["exp_cat"], prefix="exp", drop_first=False)
    exp_dummies = exp_dummies.drop(columns=["exp_5-10yr"], errors="ignore").astype(float)

    # Normalise missing values in categorical controls to "Unknown" sentinel
    for _col in ["investment_mandate", "discretionary_authority", "event_type", "market_regime"]:
        if _col in reg.columns:
            reg[_col] = reg[_col].astype(str).replace(
                {"nan": "Unknown", "<NA>": "Unknown", "None": "Unknown", "": "Unknown"}
            )

    # Investment mandate dummies (Equity long-only reference, explicitly dropped)
    if "investment_mandate" in reg.columns:
        mandate_dummies = pd.get_dummies(reg["investment_mandate"], prefix="mand", drop_first=False)
        mandate_dummies = mandate_dummies.drop(
            columns=[c for c in mandate_dummies.columns if "long-only" in c or "long_only" in c],
            errors="ignore"
        ).astype(float)
    else:
        mandate_dummies = pd.DataFrame(index=reg.index)

    # Discretionary authority dummies (Full discretion reference, explicitly dropped)
    if "discretionary_authority" in reg.columns:
        discr_dummies = pd.get_dummies(reg["discretionary_authority"], prefix="discr", drop_first=False)
        discr_dummies = discr_dummies.drop(
            columns=[c for c in discr_dummies.columns if "Full" in c or "full" in c],
            errors="ignore"
        ).astype(float)
    else:
        discr_dummies = pd.DataFrame(index=reg.index)

    # Event type dummies (earnings reference, explicitly dropped)
    if "event_type" in reg.columns:
        evtype_dummies = pd.get_dummies(reg["event_type"], prefix="evt", drop_first=False)
        evtype_dummies = evtype_dummies.drop(
            columns=[c for c in evtype_dummies.columns if "earnings" in c],
            errors="ignore"
        ).astype(float)
    else:
        evtype_dummies = pd.DataFrame(index=reg.index)

    # Market regime dummies (neutral reference, explicitly dropped)
    if "market_regime" in reg.columns:
        regime_dummies = pd.get_dummies(reg["market_regime"], prefix="regime", drop_first=False)
        regime_dummies = regime_dummies.drop(
            columns=[c for c in regime_dummies.columns if "neutral" in c],
            errors="ignore"
        ).astype(float)
    else:
        regime_dummies = pd.DataFrame(index=reg.index)

    # Scenario position (linear order effect, 1–8)
    if "scenario_position" in reg.columns:
        scenario_pos = reg[["scenario_position"]].apply(pd.to_numeric, errors="coerce").fillna(4.5).astype(float)
    else:
        scenario_pos = pd.DataFrame({"scenario_position": 4.5}, index=reg.index)

    # Block fixed effects
    block_dummies = pd.get_dummies(reg["block_id"], prefix="block", drop_first=True).astype(float)
    X = pd.concat([
        reg[["sc_total", "show_sc"]].astype(float),
        exp_dummies,
        mandate_dummies,
        discr_dummies,
        evtype_dummies,
        regime_dummies,
        scenario_pos,
        block_dummies,
    ], axis=1)
    X = X.loc[:, X.nunique() > 1]
    X = sm.add_constant(X)
    y = reg["nrs"].astype(float)

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
        
        # Determine P-value display string
        p_str = _round4(p)
        
        return {"model": model, "beta1": round(beta, 4), "se": round(se, 4),
                "t": round(t, 4), "p": p_str,
                "ci_lo": round(ci[0], 4), "ci_hi": round(ci[1], 4),
                "r2": round(model.rsquared, 4), "n_obs": int(model.nobs),
                "clustering": "HC3"}

    def _fit_ols_cluster2(X_: pd.DataFrame, y_: pd.Series, groups_: np.ndarray) -> dict:
        model = sm.OLS(y_, X_).fit(
            cov_type="cluster",
            cov_kwds={"groups": groups_},
        )
        sc_idx = list(X_.columns).index("sc_total") if "sc_total" in X_.columns else None
        if sc_idx is None:
            return {"model": model, "beta1": np.nan, "se": np.nan, "t": np.nan,
                    "p": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                    "r2": round(model.rsquared, 4), "n_obs": int(model.nobs),
                    "clustering": "two-way cluster (respondent, scenario)"}
        beta = model.params.iloc[sc_idx]
        se   = model.bse.iloc[sc_idx]
        t    = model.tvalues.iloc[sc_idx]
        p    = model.pvalues.iloc[sc_idx]
        ci   = model.conf_int().iloc[sc_idx]

        # Determine P-value display string
        p_str = _round4(p)

        return {"model": model, "beta1": round(beta, 4), "se": round(se, 4),
                "t": round(t, 4), "p": p_str,
                "ci_lo": round(ci[0], 4), "ci_hi": round(ci[1], 4),
                "r2": round(model.rsquared, 4), "n_obs": int(model.nobs),
                "clustering": "two-way cluster (respondent, scenario)"}

    # Primary: two-way cluster-robust SEs on respondent_id and scenario_id.
    # Encode group labels as integer codes – statsmodels' two-way clustering
    # cannot .view() an object-dtype array; codes preserve group membership.
    cluster_groups = np.column_stack([
        pd.factorize(df.loc[reg.index, "respondent_id"])[0],
        pd.factorize(df.loc[reg.index, "scenario_id"])[0],
    ])
    primary = _fit_ols_cluster2(X, y, cluster_groups)
    primary["n_respondents"] = df["respondent_id"].nunique() if "respondent_id" in df.columns else np.nan
    primary["n_scenarios"]   = df["scenario_id"].nunique() if "scenario_id" in df.columns else np.nan
    h1["primary"] = primary

    # Residual normality test (Shapiro-Wilk on primary OLS residuals)
    resid_norm = {}
    primary_model = primary.get("model")
    if primary_model is not None:
        residuals = primary_model.resid
        if len(residuals) >= 3:
            try:
                w_stat, p_val = stats.shapiro(residuals)
                resid_norm = {
                    "w":        round(float(w_stat), 4),
                    "p":        round(float(p_val), 4),
                    "n":        int(len(residuals)),
                    "rejected": bool(p_val < 0.05),
                }
            except Exception:
                resid_norm = {}
    h1["residual_normality"] = resid_norm
    if resid_norm:
        pd.DataFrame([{
            "test":               "Shapiro-Wilk",
            "scope":              "primary H1 OLS residuals",
            "statistic":          resid_norm["w"],
            "p":                  resid_norm["p"],
            "n":                  resid_norm["n"],
            "normality_rejected": resid_norm["rejected"],
        }]).to_csv(TABLES_DIR / "tbl_normality.csv", index=False)
    else:
        pd.DataFrame(columns=["test", "scope", "statistic", "p", "n", "normality_rejected"]).to_csv(
            TABLES_DIR / "tbl_normality.csv", index=False
        )

    # --- Robustness ---
    rob_rows = []

    # Spec 1: SC_total quintile dummies
    try:
        reg_r1 = reg.copy()
        reg_r1["sc_quintile"] = pd.qcut(reg_r1["sc_total"], q=5, labels=False, duplicates="drop")
        q_dummies = pd.get_dummies(reg_r1["sc_quintile"], prefix="q", drop_first=True)
        X_r1 = pd.concat([
            reg_r1[["show_sc"]].astype(float),
            q_dummies, exp_dummies,
            mandate_dummies, discr_dummies, evtype_dummies, regime_dummies, scenario_pos,
            block_dummies,
        ], axis=1).astype(float)
        X_r1 = X_r1.loc[:, X_r1.nunique() > 1]
        X_r1 = sm.add_constant(X_r1)
        m_r1 = sm.OLS(y, X_r1).fit(cov_type="HC3")
        rob_rows.append({
            "spec": "spec_1_quintiles", "note": "Shock Score quintile dummies",
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
                "p": _round4(p_), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
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
            # Pull new controls from original df (reg_r3.index is a subset of df.index)
            for _col in ["investment_mandate", "discretionary_authority",
                         "event_type", "market_regime", "scenario_position"]:
                if _col in df.columns:
                    reg_r3[_col] = df.loc[reg_r3.index, _col]
            for _col in ["investment_mandate", "discretionary_authority", "event_type", "market_regime"]:
                if _col in reg_r3.columns:
                    reg_r3[_col] = reg_r3[_col].astype(str).replace(
                        {"nan": "Unknown", "<NA>": "Unknown", "None": "Unknown", "": "Unknown"}
                    )
            bd3 = pd.get_dummies(reg_r3["block_id"], prefix="block", drop_first=True)
            if "investment_mandate" in reg_r3.columns:
                mand3 = pd.get_dummies(reg_r3["investment_mandate"], prefix="mand", drop_first=False)
                mand3 = mand3.drop(
                    columns=[c for c in mand3.columns if "long-only" in c or "long_only" in c],
                    errors="ignore").astype(float)
            else:
                mand3 = pd.DataFrame(index=reg_r3.index)
            if "discretionary_authority" in reg_r3.columns:
                discr3 = pd.get_dummies(reg_r3["discretionary_authority"], prefix="discr", drop_first=False)
                discr3 = discr3.drop(
                    columns=[c for c in discr3.columns if "Full" in c or "full" in c],
                    errors="ignore").astype(float)
            else:
                discr3 = pd.DataFrame(index=reg_r3.index)
            if "event_type" in reg_r3.columns:
                evt3 = pd.get_dummies(reg_r3["event_type"], prefix="evt", drop_first=False)
                evt3 = evt3.drop(
                    columns=[c for c in evt3.columns if "earnings" in c],
                    errors="ignore").astype(float)
            else:
                evt3 = pd.DataFrame(index=reg_r3.index)
            if "market_regime" in reg_r3.columns:
                reg3 = pd.get_dummies(reg_r3["market_regime"], prefix="regime", drop_first=False)
                reg3 = reg3.drop(
                    columns=[c for c in reg3.columns if "neutral" in c],
                    errors="ignore").astype(float)
            else:
                reg3 = pd.DataFrame(index=reg_r3.index)
            if "scenario_position" in reg_r3.columns:
                spos3 = reg_r3[["scenario_position"]].apply(
                    pd.to_numeric, errors="coerce").fillna(4.5).astype(float)
            else:
                spos3 = pd.DataFrame({"scenario_position": 4.5}, index=reg_r3.index)
            X_r3 = pd.concat([
                reg_r3[["show_sc"] + comp_cols], bd3, mand3, discr3, evt3, reg3, spos3,
            ], axis=1).astype(float)
            X_r3 = X_r3.loc[:, X_r3.nunique() > 1]
            X_r3 = sm.add_constant(X_r3)
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
                    "p": _round4(p_), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
                    "r2": round(m_r3.rsquared, 4), "n_obs": int(m_r3.nobs), "clustering": "HC3",
                })
    except Exception as e:
        rob_rows.append({"spec": "spec_3_components", "note": str(e)})

    # Spec 4: Interaction SC_total × ShowSC
    try:
        reg_r4 = reg.copy()
        reg_r4["sc_x_showsc"] = reg_r4["sc_total"] * reg_r4["show_sc"]
        X_r4 = pd.concat([
            reg_r4[["sc_total", "show_sc", "sc_x_showsc"]].astype(float),
            exp_dummies, mandate_dummies, discr_dummies,
            evtype_dummies, regime_dummies, scenario_pos,
            block_dummies,
        ], axis=1).astype(float)
        X_r4 = X_r4.loc[:, X_r4.nunique() > 1]
        X_r4 = sm.add_constant(X_r4)
        m_r4 = sm.OLS(y, X_r4).fit(cov_type="HC3")
        b = m_r4.params.get("sc_x_showsc", np.nan)
        se_ = m_r4.bse.get("sc_x_showsc", np.nan)
        t_ = m_r4.tvalues.get("sc_x_showsc", np.nan)
        p_ = m_r4.pvalues.get("sc_x_showsc", np.nan)
        ci_ = m_r4.conf_int().loc["sc_x_showsc"] if "sc_x_showsc" in m_r4.conf_int().index else [np.nan, np.nan]
        rob_rows.append({
            "spec": "spec_4_interaction", "note": "Shock Score × ShowSC interaction",
            "beta1": round(b, 4), "se": round(se_, 4), "t": round(t_, 4),
            "p": _round4(p_), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
            "r2": round(m_r4.rsquared, 4), "n_obs": int(m_r4.nobs), "clustering": "HC3",
        })
    except Exception as e:
        rob_rows.append({"spec": "spec_4_interaction", "note": str(e)})

    # Spec 5: Direction interaction – SC_total × D_neg (loss aversion amplification)
    # D_neg = 1 for negative-sentiment events (Negative, Mildly Negative, Strongly Negative)
    # Model: NRS = α + β1·SC_total + β2·D_neg + β3·(SC_total × D_neg) + controls
    # β1 = SC_total effect for positive events (anchoring/confirmation bias channel)
    # β3 = incremental SC_total amplification for negative events (loss aversion channel)
    # β1 + β3 = total SC_total effect for negative events
    try:
        reg_r5 = reg.copy()
        neg_labels = {"Negative", "Mildly Negative", "Strongly Negative"}
        reg_r5["d_neg"] = reg_r5["sentiment_direction"].apply(
            lambda x: 1 if str(x) in neg_labels else 0
        ).astype(float)
        reg_r5["sc_x_dneg"] = reg_r5["sc_total"] * reg_r5["d_neg"]
        X_r5 = pd.concat([
            reg_r5[["sc_total", "d_neg", "sc_x_dneg", "show_sc"]].astype(float),
            exp_dummies, mandate_dummies, discr_dummies,
            evtype_dummies, regime_dummies, scenario_pos,
            block_dummies,
        ], axis=1).astype(float)
        X_r5 = X_r5.loc[:, X_r5.nunique() > 1]
        X_r5 = sm.add_constant(X_r5)
        m_r5 = sm.OLS(y, X_r5).fit(cov_type="HC3")

        # β1: SC_total main effect (positive events)
        b1 = m_r5.params.get("sc_total", np.nan)
        se1 = m_r5.bse.get("sc_total", np.nan)
        t1 = m_r5.tvalues.get("sc_total", np.nan)
        p1 = m_r5.pvalues.get("sc_total", np.nan)
        ci1 = m_r5.conf_int().loc["sc_total"] if "sc_total" in m_r5.conf_int().index else [np.nan, np.nan]
        rob_rows.append({
            "spec": "spec_5_direction_b1", "note": "Shock Score main effect (positive events)",
            "beta1": round(b1, 4), "se": round(se1, 4), "t": round(t1, 4),
            "p": _round4(p1), "ci_lo": round(ci1[0], 4), "ci_hi": round(ci1[1], 4),
            "r2": round(m_r5.rsquared, 4), "n_obs": int(m_r5.nobs), "clustering": "HC3",
        })

        # β3: SC_total × D_neg incremental amplification (negative events)
        b3 = m_r5.params.get("sc_x_dneg", np.nan)
        se3 = m_r5.bse.get("sc_x_dneg", np.nan)
        t3 = m_r5.tvalues.get("sc_x_dneg", np.nan)
        p3 = m_r5.pvalues.get("sc_x_dneg", np.nan)
        ci3 = m_r5.conf_int().loc["sc_x_dneg"] if "sc_x_dneg" in m_r5.conf_int().index else [np.nan, np.nan]
        rob_rows.append({
            "spec": "spec_5_direction_b3", "note": "Shock Score × negative-sentiment amplification (negative events)",
            "beta1": round(b3, 4), "se": round(se3, 4), "t": round(t3, 4),
            "p": _round4(p3), "ci_lo": round(ci3[0], 4), "ci_hi": round(ci3[1], 4),
            "r2": round(m_r5.rsquared, 4), "n_obs": int(m_r5.nobs), "clustering": "HC3",
        })
    except Exception as e:
        rob_rows.append({"spec": "spec_5_direction_b1", "note": str(e)})
        rob_rows.append({"spec": "spec_5_direction_b3", "note": str(e)})

    # Spec 6: HC3 SEs on the primary specification (demoted from primary to robustness)
    try:
        hc3_fit = _fit_ols_hc3(X, y)
        rob_rows.append({
            "spec": "spec_6_hc3", "note": "Primary specification with HC3 SEs",
            "beta1": hc3_fit["beta1"], "se": hc3_fit["se"], "t": hc3_fit["t"],
            "p": hc3_fit["p"], "ci_lo": hc3_fit["ci_lo"], "ci_hi": hc3_fit["ci_hi"],
            "r2": hc3_fit["r2"], "n_obs": hc3_fit["n_obs"], "clustering": "HC3",
        })
    except Exception as e:
        rob_rows.append({"spec": "spec_6_hc3", "note": str(e)})

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
                "p":    _round4(primary_model.pvalues[covariate]),
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
                                               "horizon_days", "data_sufficient"]].copy()
    df_h2 = df.merge(hr_merge, on="scenario_id", how="left")
    df_h2 = df_h2[df_h2["data_sufficient"] == True].copy()
    df_h2["nrs"] = pd.to_numeric(df_h2["nrs"], errors="coerce")
    BASELINE_W = 0.5
    df_h2["delta_w"]       = (df_h2["nrs"] - NRS_NEUTRAL) * WEIGHT_STEP
    df_h2["stock_weight"]  = BASELINE_W + df_h2["delta_w"]
    df_h2["cash_weight"]   = 1.0 - df_h2["stock_weight"]
    df_h2["rf_period_pct"] = RF_ANNUAL / 252 * df_h2["horizon_days"] * 100
    df_h2["weighted_return"] = (
        df_h2["stock_weight"] * df_h2["horizon_return_pct"]
        + df_h2["cash_weight"] * df_h2["rf_period_pct"]
    )

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
                "p": _round4(p_), "ci_lo": round(ci_[0], 4), "ci_hi": round(ci_[1], 4),
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
            delta_w      = (mean_nrs - NRS_NEUTRAL) * WEIGHT_STEP
            stock_w      = 0.5 + delta_w
            cash_w       = 1.0 - stock_w
            hr           = horizon_returns.loc[sid, "horizon_return_pct"] if sid in horizon_returns.index else np.nan
            h_days       = horizon_returns.loc[sid, "horizon_days"] if sid in horizon_returns.index else np.nan
            rf_pct       = RF_ANNUAL / 252 * h_days * 100 if not np.isnan(h_days) else np.nan
            port_ret     = (stock_w * hr + cash_w * rf_pct) if not (np.isnan(hr) or np.isnan(rf_pct)) else np.nan
            opt_a_rows.append({
                "scenario_id": sid, "show_sc": cond,
                "mean_nrs": round(mean_nrs, 4), "delta_w": round(delta_w, 4),
                "stock_weight": round(stock_w, 4),
                "horizon_return_pct": hr,
                "rf_period_pct": round(rf_pct, 4) if not np.isnan(rf_pct) else np.nan,
                "weighted_return": round(port_ret, 4) if not np.isnan(port_ret) else np.nan,
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
        _fig_h2_nrs_by_sc(df)

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


def _fig_h2_nrs_by_sc(df: pd.DataFrame) -> None:
    """Line plot: mean NRS by SC_total quintile, split by ShowSC condition."""
    needed = {"sc_total", "nrs", "show_sc"}
    if df.empty or not needed.issubset(df.columns):
        return
    plot_df = df[list(needed)].dropna()
    if len(plot_df) < 10:
        return

    plot_df = plot_df.copy()
    plot_df["sc_quintile"] = pd.qcut(plot_df["sc_total"], q=5, labels=False, duplicates="drop")

    q_centers = plot_df.groupby("sc_quintile")["sc_total"].mean()

    fig, ax = plt.subplots(figsize=(8, 5))

    rng = np.random.default_rng(42)

    styles = {
        0: {"color": "#abd9e9", "linestyle": "--", "label": "Control (ShowSC = 0)"},
        1: {"color": "#2c7bb6", "linestyle": "-",  "label": "Treatment (ShowSC = 1)"},
    }
    for cond, sty in styles.items():
        cond_df = plot_df[plot_df["show_sc"] == cond]
        grp = cond_df.groupby("sc_quintile")["nrs"]
        means = grp.mean()
        sems  = grp.sem()
        x_vals = [q_centers[q] for q in means.index]



        ax.plot(x_vals, means.values, color=sty["color"], linestyle=sty["linestyle"],
                marker="o", linewidth=2, markersize=6, label=sty["label"], zorder=3)
        ax.fill_between(x_vals, means.values - sems.values,
                        means.values + sems.values, alpha=0.15, color=sty["color"], zorder=2)

    ax.axhline(4, color="grey", linestyle=":", linewidth=0.8)
    ax.set_xlabel("Shock Score (quintile mean)")
    ax.set_ylabel("Mean NRS")
    ax.set_ylim(3, 5)
    ax.set_yticks([3.0, 3.5, 4.0, 4.5, 5.0])
    ax.legend()
    _apa_style(ax)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_h2_nrs_by_sc.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Group B figures — rebuilt from data (forest, scatter, alignment bars).
# Reproduce the previously-static results/figures PNGs at run time.
# ---------------------------------------------------------------------------

def _fig_component_forest(rob_df: pd.DataFrame) -> None:
    """Forest plot of the four Spec 3 SC_total component coefficients with 95% CIs."""
    if rob_df.empty or "spec" not in rob_df.columns:
        return

    # (y-axis label, robustness spec row) ordered bottom (y=0) to top.
    components = [
        ("Article Count",       "spec_3_component_ac_e"),
        ("Sentiment Extremity", "spec_3_component_se_e"),
        ("Attention Intensity", "spec_3_component_ai_e"),
        ("Event-Type Severity",    "spec_3_component_es_raw"),
    ]
    C_DOWN, C_UP, C_NS = "#2c7bb6", "#d7191c", "#999999"

    fig, ax = plt.subplots(figsize=(11, 6))
    yticks, ylabels = [], []
    for y, (ylabel, spec) in enumerate(components):
        row = rob_df[rob_df["spec"] == spec]
        if row.empty:
            continue
        r = row.iloc[0]
        beta = float(r["beta1"]); lo = float(r["ci_lo"]); hi = float(r["ci_hi"])
        p = _parse_p(r["p"])
        sig = (not np.isnan(p)) and p < 0.05
        color = C_NS if not sig else (C_DOWN if beta < 0 else C_UP)

        ax.errorbar(beta, y, xerr=[[beta - lo], [hi - beta]], fmt="o", color=color,
                    markersize=13, elinewidth=2.5, capsize=0, zorder=3)
        label = f"β = {beta:+.4f} [{lo:.4f}, {hi:.4f}] {'**' if sig else 'ns'}"
        # Default: label to the right of the CI. The bottom row (AC_e) is labelled
        # to the left so it clears the lower-right legend (issue 1).
        if spec == "spec_3_component_ac_e":
            ax.annotate(label, (lo, y), xytext=(-10, 0), textcoords="offset points",
                        ha="right", va="center", color=color, fontsize=10)
        else:
            ax.annotate(label, (hi, y), xytext=(10, 0), textcoords="offset points",
                        ha="left", va="center", color=color, fontsize=10)
        yticks.append(y); ylabels.append(ylabel)

    if not yticks:
        plt.close(fig)
        return

    ax.axvline(0, color="black", linestyle="--", linewidth=1, zorder=1)
    ax.set_yticks(yticks); ax.set_yticklabels(ylabels)
    ax.set_ylim(-0.6, len(components) - 0.4)
    ax.set_xlabel("OLS Coefficient (β) with 95% Confidence Interval")

    handles = [
        Patch(facecolor=C_DOWN, label="Significant, risk-reducing (p < 0.05)"),
        Patch(facecolor=C_UP,   label="Significant, risk-increasing (p < 0.05)"),
        Patch(facecolor=C_NS,   label="Not significant"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False)
    _apa_style(ax)

    # Pad the x-range so value labels are not clipped (more room on the right).
    x0, x1 = ax.get_xlim()
    span = x1 - x0
    ax.set_xlim(x0 - 0.15 * span, x1 + 0.32 * span)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_component_forest.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _fig_sc_vs_horizon_return(scenarios: pd.DataFrame, horizon_returns: pd.DataFrame) -> None:
    """Scatter of realized horizon return vs SC_total (one point per scenario, by block)."""
    if scenarios.empty or horizon_returns.empty:
        return
    sdf = scenarios[["scenario_id", "ticker", "block_id", "sc_total"]].copy()
    hr = horizon_returns.reset_index()[["scenario_id", "horizon_return_pct"]]
    m = sdf.merge(hr, on="scenario_id", how="inner")
    m["sc_total"]           = pd.to_numeric(m["sc_total"], errors="coerce")
    m["horizon_return_pct"] = pd.to_numeric(m["horizon_return_pct"], errors="coerce")
    m = m.dropna(subset=["sc_total", "horizon_return_pct"])
    if len(m) < 3:
        return

    block_colors = {1: "#2c7bb6", 2: "#1b9e77", 3: "#b8860b"}
    fig, ax = plt.subplots(figsize=(12, 7.5))

    ax.axhline(0, color="grey", linewidth=0.8, zorder=1)
    ax.axvline(0, color="grey", linewidth=0.8, zorder=1)

    x = m["sc_total"].to_numpy(); y = m["horizon_return_pct"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, slope * xs + intercept, color="#d7191c", linestyle="--", linewidth=1.8,
            label=f"Linear trend (β = {slope:.2f}%/unit Shock Score)", zorder=2)

    for b in sorted(m["block_id"].dropna().unique()):
        sub = m[m["block_id"] == b]
        color = block_colors.get(int(b), "#666666")
        ax.scatter(sub["sc_total"], sub["horizon_return_pct"], s=130, color=color,
                   edgecolor="white", linewidth=1.0, label=f"Block {int(b)}", zorder=3)
        for _, row in sub.iterrows():
            ax.annotate(str(row["ticker"]),
                        (float(row["sc_total"]), float(row["horizon_return_pct"])),
                        xytext=(5, 5), textcoords="offset points", fontsize=8, color=color)

    ax.set_xlabel("Composite Shock Score")
    ax.set_ylabel("Actual horizon return (%)")
    ax.legend(loc="upper right")
    _apa_style(ax)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_sc_vs_horizon_return.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _fig_alignment_rates(alignment_df: pd.DataFrame, overall_rate: float) -> None:
    """Horizontal bar chart of NRS–sentiment alignment rate by sentiment category."""
    if alignment_df.empty or "group" not in alignment_df.columns:
        return
    sent = alignment_df[alignment_df["group"].str.startswith("sentiment=")].copy()
    if sent.empty:
        return
    sent["category"] = sent["group"].str.replace("sentiment=", "", regex=False)
    sent = sent.sort_values("alignment_rate", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(sent))
    rates = sent["alignment_rate"].to_numpy()
    ax.barh(y, rates, color="#c0392b", zorder=3)
    for yi, rate in zip(y, rates):
        ax.annotate(f"{rate:.4f}", (rate, yi), xytext=(6, 0), textcoords="offset points",
                    va="center", ha="left", fontsize=10)
    ax.set_yticks(y); ax.set_yticklabels(sent["category"].tolist())

    ax.axvline(0.50, color="black", linestyle="--", linewidth=2,
               label="Directional consistency threshold (0.50)", zorder=2)
    if not (overall_rate is None or (isinstance(overall_rate, float) and np.isnan(overall_rate))):
        ax.axvline(overall_rate, color="grey", linestyle=":", linewidth=1.5,
                   label=f"Overall alignment rate ({overall_rate:.4f})", zorder=2)

    ax.set_xlim(0, 0.62)
    ax.set_xlabel("Alignment Rate (proportion of observations)")
    ax.legend(loc="lower right")
    _apa_style(ax)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_alignment_rates.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Section 7 – Conclusions engine
# ---------------------------------------------------------------------------

def _parse_p(p_val: float | str) -> float:
    """Helper to convert P-value (which might be a string like '<0.0001') back to float for threshold checks."""
    if isinstance(p_val, str):
        if p_val.startswith("<"):
            return float(p_val[1:]) - 0.000001
        if p_val.startswith(">"):
            return float(p_val[1:]) + 0.000001
        if p_val == "N/A":
            return np.nan
        try:
            return float(p_val)
        except ValueError:
            return np.nan
    return float(p_val)


def generate_conclusions(h1: dict, h2: dict, desc: dict, norm: dict) -> dict:
    conc = {}

    # H1
    primary = h1.get("primary", {})
    beta1 = primary.get("beta1", np.nan)
    h1_p_val  = primary.get("p", np.nan)
    h1_p_float = _parse_p(h1_p_val)
    h1_t  = primary.get("t", np.nan)
    h1_ci_lo = primary.get("ci_lo", np.nan)
    h1_ci_hi = primary.get("ci_hi", np.nan)
    h1_supported = (not np.isnan(h1_p_float)) and (h1_p_float < ALPHA)

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
        f"{'At the α = 0.05 level of significance, support for the alternative hypothesis H1ₐ was found.' if h1_supported else 'At the α = 0.05 level of significance, the evidence fails to reject the null hypothesis H1₀.'} "
        f"The OLS regression of SC_total on Net Risk Stance (NRS) – controlling for the ShowSC treatment indicator, years of experience, and block fixed effects – yields "
        f"β₁ = {_round4(beta1)} (robust SE = {_round4(primary.get('se', np.nan))}, "
        f"t = {_round4(h1_t)}, p = {h1_p_val}, "
        f"95% CI [{_round4(h1_ci_lo)}, {_round4(h1_ci_hi)}]). "
        f"{_h1_direction_sentence} "
        f"Robustness checks using quintile dummies, respondent fixed effects, "
        f"decomposed components, and an interaction term are reported in Table 5.4."
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
    h2_p_val = h2_primary.get("p", np.nan)
    h2_p_float = _parse_p(h2_p_val)
    h2_supported = (not np.isnan(h2_p_float)) and (h2_p_float < ALPHA)
    conc["h2_supported"] = h2_supported
    conc["h2_verdict"]   = "Supported" if h2_supported else "Not supported"
    conc["tau"]          = tau
    conc["h2_p"]         = h2_p_float

    ret_diff    = h2.get("return_differential", np.nan)
    dollar_imp  = h2.get("dollar_impact", np.nan)
    ret_sc0     = h2.get("collective_return_sc0", np.nan)
    ret_sc1     = h2.get("collective_return_sc1", np.nan)

    if h2_supported and not np.isnan(tau):
        if tau > 0:
            _h2_support_sentence = (
                "The Shock Score dashboard is associated with a statistically significant improvement "
                "in risk-adjusted portfolio outcomes, supporting the case for structured decision support "
                "during information shocks."
            )
        else:
            _h2_support_sentence = (
                "The sign of the treatment effect is negative (τ < 0), indicating that dashboard "
                "exposure is associated with worse portfolio outcomes in the current sample. "
                "This unexpected result warrants further investigation before any deployment recommendation is made."
            )
    else:
        _h2_support_sentence = (
            "No statistically significant difference in portfolio outcomes between the treatment "
            "and control conditions was found. Validation on a larger professional sample is recommended."
        )

    _dollar_part = (
        f" On an assumed AUM of $100M, the ShowSC=1 collective portfolio generated a "
        f"dollar return differential of ${dollar_imp:,.0f} relative to the ShowSC=0 "
        f"portfolio over the evaluation window."
    ) if not np.isnan(dollar_imp) else ""

    conc["h2_narrative"] = (
        f"{'At the α = 0.05 level of significance, support for the alternative hypothesis H2ₐ was found.' if h2_supported else 'At the α = 0.05 level of significance, the evidence fails to reject the null hypothesis H2₀.'} "
        f"Hypothesis H2 is tested using individual-portfolio regressions (Option B). "
        f"Per respondent, portfolio returns are constructed from NRS-weighted horizon "
        f"returns across the four scenarios assigned to each condition. The estimated "
        f"treatment effect on portfolio return is τ = {_round4(tau)} "
        f"(robust SE = {_round4(h2_primary.get('se', np.nan))}, "
        f"t = {_round4(h2_primary.get('t', np.nan))}, p = {h2_p_val}, "
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

    lines = [
        "# Thesis Results – Auto-generated",
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

    # ---- tbl_4_7_counts ----
    n_resp_panel = df["respondent_id"].nunique() if "respondent_id" in df.columns else 0
    n_obs_panel  = len(df.dropna(subset=["nrs"]))
    tbl_47_lines = [
        f"| Total valid responses included in analysis | {n_resp_panel} |",
        f"| Total scenario-level observations | {n_obs_panel} |",
    ]
    tbl_47 = block("tbl_4_7_counts", "\n".join(tbl_47_lines))

    # ---- tbl_5_1_respondents ----
    freq_df = desc.get("freq_demographics", pd.DataFrame())
    inst_rows = freq_df[freq_df["field"] == "institution_type"] if not freq_df.empty else pd.DataFrame()
    aum_rows  = freq_df[freq_df["field"] == "aum_category"]    if not freq_df.empty else pd.DataFrame()

    resp_lines = [
        "**Table 5.1**",
        "",
        "*Respondent Demographics*",
        "",
        "| Characteristic | Metric | Value |",
        "|---|---|---|",
    ]
    for r in desc.get("exp_freq", []):
        resp_lines.append(f"| Years of experience | {r['label']} | {r['count']} ({r['pct']}%) |")
    for _, row in inst_rows.iterrows():
        resp_lines.append(f"| Institution type | {row['value']} | {row['count']} ({row['pct']}%) |")
    for _, row in aum_rows.iterrows():
        resp_lines.append(f"| AUM category | {row['value']} | {row['count']} ({row['pct']}%) |")
    resp_lines += ["", f"*Note.* N = {n_total} respondents."]
    tbl_5_1 = block("tbl_5_1_respondents", "\n".join(resp_lines))

    # ---- fig_5_1_demographics ----
    fig_5_1 = block("fig_5_1_demographics", "\n".join([
        "**Figure 5.1**",
        "",
        "*Sample Composition by Institution Type and AUM Category*",
        "",
        "![Respondent demographics](figures/fig_demographics.png)",
        "",
        f"*Note.* N = {n_total} respondents. Original figure by the author.",
    ]))

    # ---- fig_5_2_nrs_distribution / fig_5_3_nrs_by_condition / fig_5_4_sc_distribution ----
    fig_5_2 = block("fig_5_2_nrs_distribution", "\n".join([
        "**Figure 5.2**",
        "",
        "*Distribution of Net Risk Stance Responses*",
        "",
        "![NRS distribution](figures/fig_nrs_distribution.png)",
        "",
        f"*Note.* N = {n_obs} scenario-level observations. Original figure by the author.",
    ]))
    fig_5_3 = block("fig_5_3_nrs_by_condition", "\n".join([
        "**Figure 5.3**",
        "",
        "*Net Risk Stance Distribution by Experimental Condition*",
        "",
        "![NRS by condition](figures/fig_nrs_by_condition.png)",
        "",
        "*Note.* Control (ShowSC = 0) versus treatment (ShowSC = 1) conditions. Original figure by the author.",
    ]))
    fig_5_4 = block("fig_5_4_sc_distribution", "\n".join([
        "**Figure 5.4**",
        "",
        "*Distribution of the Composite Shock Score*",
        "",
        "![Shock Score distribution](figures/fig_sc_distribution.png)",
        "",
        "*Note.* The Shock Score is the first principal component of the four standardised components. Original figure by the author.",
    ]))

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
        "**Table 5.3**",
        "",
        "*Final Scenario Selection Across Survey Blocks*",
        "",
        _md_table(scen_tbl),
        "",
    ]
    tbl_5_3 = block("tbl_5_3_scenarios", "\n".join(s523_lines))

    # Inject residual normality from H1 into norm dict for use in s5_4_normality block
    norm["residual_normality"] = h1.get("residual_normality", {})

    # ---- tbl_5_4_nrs_freq / tbl_5_5_icc / tbl_5_6_residuals ----
    freq_df          = norm.get("freq_df", pd.DataFrame())
    n_resp_norm      = norm.get("n_respondents", 0)
    icc_per_block    = norm.get("icc_per_block", {})
    n_per_block      = norm.get("n_per_block", {})
    resid_norm       = norm.get("residual_normality", {})

    # --- Table 5.4: NRS Frequency Distribution ---
    freq_lines = [
        "**Table 5.4**",
        "",
        "*NRS Response Frequency Distribution*",
        "",
    ]
    if not freq_df.empty:
        groups = ["Overall", "ShowSC=0 (Control)", "ShowSC=1 (Treatment)"]
        header = "| NRS | " + " | ".join([f"N ({g})" for g in groups]) + \
                 " | " + " | ".join([f"% ({g})" for g in groups]) + " |"
        sep    = "|" + "---|" * (1 + len(groups) * 2)
        rows   = [header, sep]
        for sp in range(1, 8):
            row_data = [str(sp)]
            for g in groups:
                mask = (freq_df["scale_point"] == sp) & (freq_df["group"] == g)
                n_val = int(freq_df.loc[mask, "count"].values[0]) if mask.any() else 0
                row_data.append(str(n_val))
            for g in groups:
                mask = (freq_df["scale_point"] == sp) & (freq_df["group"] == g)
                p_val = float(freq_df.loc[mask, "pct"].values[0]) if mask.any() else 0.0
                row_data.append(f"{p_val:.2f}%")
            rows.append("| " + " | ".join(row_data) + " |")
        freq_lines += rows
        total_overall = int(freq_df[freq_df["group"] == "Overall"]["count"].sum())
        freq_lines += [
            "",
            f"*Note.* NRS responses on a 7-point scale (1 = Strongly reduce concentration, "
            f"7 = Strongly increase concentration). N = {n_resp_norm} respondents, "
            f"{total_overall} total observations. Percentages may not sum to 100% due to rounding.",
        ]
    tbl_5_4 = block("tbl_5_4_nrs_freq", "\n".join(freq_lines))

    # --- Table 5.5: ICC(2,1) Inter-rater Reliability by Block ---
    icc_lines = [
        "**Table 5.5**",
        "",
        "*Instrument Reliability – Mean ICC(2,1) by Block*",
        "",
        "| Block | N respondents | Mean ICC(2,1) | Threshold (≥ 0.70) | Assessment |",
        "|-------|--------------|---------------|---------------------|------------|",
    ]
    threshold_icc = 0.70
    all_blocks = sorted(set(list(icc_per_block.keys()) + [1, 2, 3]))
    for blk in all_blocks:
        n_blk   = n_per_block.get(blk, 0)
        icc_val = icc_per_block.get(blk, np.nan)
        n_str   = str(n_blk) if n_blk > 0 else "Not yet available"
        if isinstance(icc_val, float) and np.isnan(icc_val):
            if n_blk == 0:
                icc_lines.append(
                    f"| Block {blk} | {n_str} | — | — | Pending full sample |"
                )
            else:
                icc_lines.append(
                    f"| Block {blk} | {n_str} | — | — | "
                    f"Could not compute (check version column) |"
                )
        else:
            meets = icc_val >= threshold_icc
            icc_lines.append(
                f"| Block {blk} | {n_str} | {icc_val:.4f} | "
                f"{'Above' if meets else 'Below'} | "
                f"{'Acceptable' if meets else 'Sub-threshold'} |"
            )
    icc_lines += [
        "",
        "*Note.* ICC(2,1) computed per block using mean NRS per scenario × version "
        "(V1/V2) as the data structure; scenarios are targets, versions are raters. "
        "Threshold of ICC ≥ 0.70 follows Koo and Mae (2016). "
        "Blocks with no respondents in the current sample are marked as pending.",
    ]
    tbl_5_5 = block("tbl_5_5_icc", "\n".join(icc_lines))

    # --- Table 5.6: Residual Normality ---
    resid_lines = [
        "**Table 5.6**",
        "",
        "*OLS Residual Normality – Primary H1 Regression*",
        "",
    ]
    if resid_norm:
        resid_lines += [
            "| | Shapiro-Wilk W | p-value | Normality rejected (α = 0.05) |",
            "|---|---|---|---|",
            f"| Primary H1 residuals | {_round4(resid_norm.get('w', np.nan))} | "
            f"{_round4(resid_norm.get('p', np.nan))} | "
            f"{'Yes' if resid_norm.get('rejected') else 'No'} |",
            "",
            f"*Note.* Shapiro-Wilk test applied to OLS residuals from the primary H1 "
            f"regression specification (N = {resid_norm.get('n', '—')} observations). "
            f"Residual normality is the relevant OLS assumption; the marginal distribution "
            f"of NRS is not required to be normal. Inference for the primary "
            f"specification uses two-way cluster-robust standard errors (clustered by "
            f"respondent and scenario), whose validity does not depend on residual normality.",
        ]
    else:
        resid_lines += ["*(To be populated once H1 regression is computed.)*"]
    tbl_5_6 = block("tbl_5_6_residuals", "\n".join(resid_lines))

    # ---- s5_5_1_h1_main ----
    primary = h1.get("primary", {})
    rob_df  = h1.get("robustness", pd.DataFrame())

    main_tbl_df = pd.DataFrame([{
        "Covariate": "Shock Score",
        "β₁":   primary.get("beta1", np.nan),
        "SE":   primary.get("se",    np.nan),
        "t":    primary.get("t",     np.nan),
        "p":    primary.get("p",     ""),
        "CI_lo": primary.get("ci_lo", np.nan),
        "CI_hi": primary.get("ci_hi", np.nan),
        "R²":   primary.get("r2",    np.nan),
        "N_obs":  primary.get("n_obs",          ""),
        "N_resp": primary.get("n_respondents",   ""),
        "SE_type": primary.get("clustering", "HC3"),
    }])
    s551_main_lines = [
        "**Table 5.7**",
        "",
        "*H1 Primary Regression Result*",
        "",
        _md_table(main_tbl_df),
        "",
    ]
    tbl_5_7 = block("tbl_5_7_h1_main", "\n".join(s551_main_lines))

    # ---- tbl_5_8_h1_robustness ----
    s551_rob_lines = ["**Table 5.8**", "", "*H1 Robustness Specification Results*", ""]
    if not rob_df.empty:
        s551_rob_lines += [_md_table(rob_df), ""]
    tbl_5_8 = block("tbl_5_8_h1_robustness", "\n".join(s551_rob_lines))

    # ---- tbl_5_9_h2_results ----
    n_sortino_elig = h2.get("n_sortino_eligible", 0)
    n_b_pairs_     = h2.get("n_option_b_pairs", 0)
    opt_b_reg = h2.get("opt_b_reg", pd.DataFrame())
    s552_lines = ["**Table 5.9**", "", "*H2 Portfolio Analysis Results*", ""]
    if not opt_b_reg.empty:
        s552_lines += [_md_table(opt_b_reg), ""]
    s552_lines.append(
        f"*Note.* The Sortino ratio is computed only for respondent-condition pairs that yield "
        f"at least one negative portfolio return; in the current sample this applies to "
        f"{n_sortino_elig} of {n_b_pairs_} respondent-condition pairs. The collective portfolios "
        f"in the descriptive Option A analysis are constructed from the same respondent pool, so "
        f"no causal inference should be drawn from Option A alone; it is presented for "
        f"institutional illustration only."
    )
    tbl_5_9 = block("tbl_5_9_h2_results", "\n".join(s552_lines))

    # ---- fig_5_7_sharpe ----
    fig_5_7 = block("fig_5_7_sharpe", "\n".join([
        "**Figure 5.7**",
        "",
        "*Sharpe Ratio Comparison Across Experimental Conditions*",
        "",
        "![Sharpe comparison](figures/fig_sharpe_comparison.png)",
        "",
        "*Note.* Sharpe ratios computed per respondent-condition pair from NRS-weighted simulated "
        "portfolio returns. Original figure by the author.",
    ]))

    # ---- fig_h2_nrs_sc_split ----
    _h2_opt_b = h2.get("opt_b_reg", pd.DataFrame())
    _h2_tau   = "N/A"
    _h2_p_fig = "N/A"
    if not _h2_opt_b.empty and "method" in _h2_opt_b.columns and "outcome" in _h2_opt_b.columns:
        _pr = _h2_opt_b[
            (_h2_opt_b["method"] == "option_b_individual") &
            (_h2_opt_b["outcome"] == "portfolio_return")
        ]
        if len(_pr) > 0:
            _h2_tau   = _round4(_pr.iloc[0].get("tau",  np.nan))
            _h2_p_fig = str(_pr.iloc[0].get("p", "N/A"))
    _h2_verdict_fig = conc.get("h2_verdict", "Not supported").lower()
    fig_5_8 = block("fig_5_8_nrs_sc_split", "\n".join([
        "**Figure 5.8**",
        "",
        "*Mean NRS by Shock Score Quintile and Experimental Condition*",
        "",
        "![Mean NRS by Shock Score quintile and ShowSC condition](figures/fig_h2_nrs_by_sc.png)",
        "",
        f"*Note.* Each point represents the mean Net Risk Stance (NRS) within a Shock Score quintile, "
        f"separately for the control (ShowSC = 0, dashed) and treatment (ShowSC = 1, solid) conditions. "
        f"Shaded bands show ±1 standard error. Error bars that substantially overlap across conditions "
        f"indicate that the Shock Score dashboard does not systematically alter risk-stance responses. "
        f"The near-parallel trajectories are consistent with the H2 result being {_h2_verdict_fig} "
        f"(τ = {_h2_tau}, p = {_h2_p_fig}). "
        f"The dotted horizontal line marks the NRS neutral point (4 = maintain exposure). "
        f"Original figure by the author.",
    ]))

    # ---- tbl_5_10_alignment ----
    alignment = alignment or {}
    aln_df   = alignment.get("alignment_df", pd.DataFrame())
    if not aln_df.empty:
        _aln_lines = [
            "**Table 5.10**",
            "",
            "*NRS–Sentiment Alignment by Group*",
            "",
            _md_table(aln_df),
        ]
        tbl_5_10 = block("tbl_5_10_alignment", "\n".join(_aln_lines))
    else:
        tbl_5_10 = block(
            "tbl_5_10_alignment",
            "**Table 5.10**\n\n*NRS–Sentiment Alignment by Group*\n\n"
            "*(Alignment diagnostic could not be computed.)*",
        )

    # Assemble file (atomic blocks in document order; narrative lives in thesis.md)
    sections = [
        tbl_47,
        tbl_5_1, fig_5_1,
        fig_5_2, fig_5_3, fig_5_4,
        tbl_5_3,
        tbl_5_4, tbl_5_5, tbl_5_6,
        tbl_5_7, tbl_5_8,
        tbl_5_9, fig_5_7, fig_5_8,
        tbl_5_10,
    ]
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
    print(f"  H1 (SC_total->NRS): beta1 = {_round4(primary.get('beta1', np.nan))}, p = {primary.get('p', 'N/A')} -> {conc['h1_verdict']}")
    print(f"  H2 Option B       : tau  = {_round4(tau)}, p = {h2_p if isinstance(h2_p, str) else _round4(h2_p)} -> {conc['h2_verdict']}")
    diff_str = f"{_round4(ret_diff)}%" if not np.isnan(ret_diff) else "N/A"
    dol_str  = f"${dollar_imp:,.0f}" if not np.isnan(dollar_imp) else "N/A"
    print(f"  H2 Option A       : Return differential = {diff_str}, Dollar impact = {dol_str}")
    print(f"  Outputs           : {RESULTS_MD_PATH}")
    print(f"                      {FIGURES_DIR}/ ({n_figs} files)")
    print(f"                      {TABLES_DIR}/  ({n_tables} files)")
    print("=" * 61)


# ---------------------------------------------------------------------------
# Section 10 – PCA diagnostics
# ---------------------------------------------------------------------------

def compute_pca_diagnostics() -> dict:
    """Refit PCA on z-standardised components from the authoritative shock score CSV and save diagnostics."""
    ss = pd.read_csv(SHOCK_SCORE_PATH)

    z_cols  = ["ac_z", "se_z", "ai_z", "es_z"]
    raw_cols = ["ac_raw", "se_raw", "ai_raw", "es_raw"]

    if all(c in ss.columns for c in z_cols):
        Z = ss[z_cols].fillna(0.0).values.astype(float)
    elif all(c in ss.columns for c in raw_cols):
        Z = _StandardScaler().fit_transform(ss[raw_cols].fillna(0.0).values.astype(float))
    else:
        print("WARNING: PCA diagnostics — required z-columns not found in shock score CSV; skipping.")
        return {}

    n = len(ss)
    pca = _PCA(n_components=1)
    pca.fit(Z)
    loadings = pca.components_[0].copy()

    # Sign convention: loading on AC_e (index 0) must be positive
    if loadings[0] < 0:
        loadings = -loadings

    diag = {
        "eigenvalue_pc1":        round(float(pca.explained_variance_[0]),       4),
        "variance_explained_pc1": round(float(pca.explained_variance_ratio_[0]), 4),
        "variance_explained_pct": round(float(pca.explained_variance_ratio_[0]) * 100, 2),
        "loadings": {
            "AC_e":   round(float(loadings[0]), 4),
            "SE_e":   round(float(loadings[1]), 4),
            "AI_e":   round(float(loadings[2]), 4),
            "ES_raw": round(float(loadings[3]), 4),
        },
        "n_scenarios": n,
    }

    out_path = TABLES_DIR / "pca_diagnostics.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(diag, fh, indent=2)
    print(f"  PCA diagnostics saved to {out_path}")
    print(f"  Eigenvalue PC1 = {diag['eigenvalue_pc1']}, variance explained = {diag['variance_explained_pct']}%")
    return diag


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-augment",    action="store_true")
    parser.add_argument("--skip-figures",  action="store_true")
    args, _ = parser.parse_known_args()

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

    if not args.skip_figures:
        print("\nRebuilding forest / scatter / alignment figures...")
        _fig_component_forest(h1.get("robustness", pd.DataFrame()))
        _fig_sc_vs_horizon_return(scenarios, horizon_returns)
        _fig_alignment_rates(alignment.get("alignment_df", pd.DataFrame()),
                             alignment.get("overall_alignment_rate", np.nan))

    print("\nComputing PCA diagnostics...")
    compute_pca_diagnostics()

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
            f"({'supported' if _parse_p(primary.get('p', 1)) < ALPHA else 'not supported'}). "
            f"H2: tau={sharpe_row.get('tau', 'n/a')}, p={sharpe_row.get('p', 'n/a')} "
            f"({'supported' if sharpe_row.get('h2_supported') else 'not supported'})."
        ),
    )


if __name__ == "__main__":
    main()
