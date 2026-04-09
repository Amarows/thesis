"""
3_survey_assembly.py
====================
Survey Assembly Pipeline — controller script.

Orchestrates the full pipeline that produces all data assets needed to
construct the Google Forms survey instrument:

  survey/metadata/           CSV tables (metadata, news text, price reaction, shock score)
  survey/charts/             Bloomberg-style intraday shock chart PNGs
  survey/dashboards/         Shock Score dashboard PNGs
  survey/counterbalancing/   Latin square assignment matrix and form assembly guide
  diagnostics/survey_assembly_report.md

Usage:
    python 3_survey_assembly.py               # auto-populates manifest from upstream pipeline
    python 3_survey_assembly.py --skip-auto   # reads existing data/scenario_manifest.csv

This script is a thin controller.  Domain logic lives in the toolkits:

  toolkits/visualization_toolkit.py    -- chart and dashboard PNGs
  toolkits/news_processor_toolkit.py   -- headlines, summaries, FinBERT scoring
  toolkits/event_selection_toolkit.py  -- shock identification + SC_total computation
  toolkits/survey_design_toolkit.py    -- counterbalancing, manifest conversion, report

Prerequisites:
    pip install pandas numpy matplotlib scikit-learn nltk yfinance
    (Optional) pip install anthropic        # auto-generated news summaries
    (Optional) pip install transformers torch  # FinBERT sentiment scoring
    (Optional) ANTHROPIC_API_KEY env variable set
"""

import json
import os
import sys
import glob
import re
import shutil
import warnings as _warnings_module
from datetime import datetime, timezone
from pathlib import Path


def _add_toolkits_to_path() -> None:
    """Ensure toolkits directory is importable regardless of CWD."""
    try:
        toolkits_dir = Path(__file__).resolve().parent / "toolkits"
        sys.path.insert(0, str(toolkits_dir))
    except Exception:
        sys.path.insert(0, "toolkits")


_add_toolkits_to_path()

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Toolkit imports ───────────────────────────────────────────────────────────

from visualization_toolkit import (
    _infer_shock_direction,
    plot_shock_chart,
    plot_dashboard,
)
from news_processor_toolkit import (
    HAS_FINBERT,
    _clean_bz_headline,
    build_news_text_df,
)
from event_selection_toolkit import (
    compute_raw_components,
    compute_shock_scores,
    compute_persistence_horizon,
)
from survey_design_toolkit import (
    MANIFEST_COLUMNS,
    populate_manifest_from_blocks,
    generate_counterbalancing,
    generate_report,
)

# ── Path constants ────────────────────────────────────────────────────────────

DATA_DIR    = Path("data")
SURVEY_DIR  = Path("survey")
MANIFEST_PATH    = DATA_DIR / "scenario_manifest.csv"
NEWS_CACHE_PATH  = DATA_DIR / "news_summary_cache.csv"
_CREDENTIALS_API_KEY = Path("credentials") / "claude_api.txt"

# Load API key: env variable takes priority, fall back to credentials file
if not os.environ.get("ANTHROPIC_API_KEY") and _CREDENTIALS_API_KEY.exists():
    _key = _CREDENTIALS_API_KEY.read_text().strip()
    if _key:
        os.environ["ANTHROPIC_API_KEY"] = _key

# ── Runtime warnings log ──────────────────────────────────────────────────────

_WARNINGS: list[str] = []


def _warn(msg: str) -> None:
    print(f"  [WARNING] {msg}")
    _WARNINGS.append(msg)


# ── Input loading ─────────────────────────────────────────────────────────────

def load_portfolio() -> pd.DataFrame:
    """Load data/portfolio.csv; return DataFrame with [ticker, company_name, gics_sector]."""
    path = DATA_DIR / "portfolio.csv"
    if not path.exists():
        print(f"ERROR: {path} not found.")
        sys.exit(1)

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    col_map = {
        "#": "row_num", "Company": "company_name",
        "Symbol": "ticker", "ISIN": "isin",
        "GICS Sector": "gics_sector",
        "Market cap": "market_cap", "SP 500 rank": "sp500_rank",
    }
    df = df.rename(columns={c: col_map.get(c, c) for c in df.columns})

    required = {"ticker", "company_name", "gics_sector"}
    if not required.issubset(df.columns):
        print(f"ERROR: portfolio.csv is missing columns. Expected: {required}")
        sys.exit(1)

    return df[["ticker", "company_name", "gics_sector"]].copy()


def load_price_data(tickers: list[str]) -> dict[str, pd.DataFrame]:
    """
    Load 30-min bar price data for each ticker.
    Falls back to 1-hour bars if 30-min files are absent.
    Returns: {ticker: DataFrame[time (UTC tz-aware), close, volume]}
    """
    prices: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        candidates = [
            str(DATA_DIR / f"{ticker}_30mins_360D.csv"),
            str(DATA_DIR / f"{ticker}_30mins_90D.csv"),
            str(DATA_DIR / f"{ticker}_1hour_360D.csv"),
            str(DATA_DIR / f"{ticker}_1hour_90D.csv"),
        ]
        found = None
        for pattern in candidates:
            matches = glob.glob(pattern)
            if matches:
                found = matches[0]
                if "1hour" in found:
                    _warn(f"{ticker}: 30-min file not found; using {Path(found).name}")
                break

        if found is None:
            _warn(f"{ticker}: no price file found (tried 30-min and 1-hour)")
            continue

        try:
            df = pd.read_csv(found)
            df["time"] = pd.to_datetime(df["time"], utc=True)
            df = df.sort_values("time").reset_index(drop=True)
            prices[ticker] = df[["time", "close", "volume"]].copy()
        except Exception as exc:
            _warn(f"{ticker}: failed to load price file - {exc}")

    return prices


def load_news_data(tickers: list[str]) -> dict[str, pd.DataFrame]:
    """
    Load all *_BZ_*.csv news files for each ticker.
    Returns: {ticker: DataFrame[time (UTC tz-aware), headline, article_text, ...]}
    """
    news: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        files = glob.glob(str(DATA_DIR / f"{ticker}_BZ_*.csv"))
        if not files:
            _warn(f"{ticker}: no Benzinga news files found")
            continue

        frames = []
        for fpath in files:
            try:
                df = pd.read_csv(fpath)
                if df.empty:
                    continue
                frames.append(df)
            except pd.errors.EmptyDataError:
                continue
            except Exception as exc:
                _warn(f"{ticker}: error reading {Path(fpath).name} - {exc}")

        if not frames:
            continue

        combined = pd.concat(frames, ignore_index=True)

        if "time_utc" in combined.columns:
            combined["time"] = pd.to_datetime(combined["time_utc"], format="ISO8601", utc=True)
        elif "time" in combined.columns:
            combined["time"] = pd.to_datetime(combined["time"], format="ISO8601", utc=True)
        else:
            _warn(f"{ticker}: news files have no recognisable time column")
            continue

        if "headline" in combined.columns:
            combined["headline"] = combined["headline"].apply(_clean_bz_headline)

        news[ticker] = combined.sort_values("time").reset_index(drop=True)

    return news


# ── Manifest loading ──────────────────────────────────────────────────────────

def _create_manifest_template() -> None:
    """Write an empty scenario_manifest.csv template and exit."""
    print(f"\ndata/scenario_manifest.csv not found.")
    print("Creating template - please fill it in and re-run the script.\n")

    template_rows = [
        {
            "scenario_id": "B1_S01", "block_id": 1, "ticker": "LIN",
            "company_name": "Linde", "gics_sector": "Materials",
            "event_date": "2025-07-30", "event_time": "14:30",
            "event_type": "product",
            "headline": "<paste displayed headline here>",
            "num_articles": 1,
        },
        {
            "scenario_id": "B1_S02", "block_id": 1, "ticker": "JPM",
            "company_name": "JPMorgan Chase", "gics_sector": "Financials",
            "event_date": "2025-06-15", "event_time": "10:00",
            "event_type": "earnings",
            "headline": "<paste displayed headline here>",
            "num_articles": 2,
        },
    ]
    df = pd.DataFrame(template_rows, columns=MANIFEST_COLUMNS)
    df.to_csv(MANIFEST_PATH, index=False)

    print(f"Template written to: {MANIFEST_PATH}")
    print("\nColumn reference:")
    print("  scenario_id   - unique identifier, e.g. B1_S01 (Block 1, Scenario 1)")
    print("  block_id      - integer 1, 2, or 3")
    print("  ticker        - stock ticker symbol (must match data/ file names)")
    print("  company_name  - full company name for display")
    print("  gics_sector   - GICS sector name (from portfolio.csv)")
    print("  event_date    - YYYY-MM-DD (event day)")
    print("  event_time    - HH:MM in Eastern Time, e.g. 14:30")
    print("  event_type    - one of: earnings, guidance, regulatory, management,")
    print("                           analyst, macro, product, legal, dividend, other")
    print("  headline      - the displayed headline (highest |sentiment| when AC>1)")
    print("  num_articles  - total articles in the shock bar (AC_e)")
    sys.exit(0)


def _auto_populate_manifest(portfolio_df: pd.DataFrame) -> "pd.DataFrame | None":
    """
    Run the full upstream pipeline (load_market_data → identify_shocks →
    compute_sc_total → assign_blocks) and write scenario_manifest.csv.
    Returns the manifest DataFrame, or None on failure.
    """
    try:
        from market_data_processor_toolkit import load_market_data
        from event_selection_toolkit import identify_shocks, compute_sc_total, assign_blocks
    except ImportError as exc:
        print(f"  Cannot import pipeline modules: {exc}")
        return None

    print("  Loading market data for all tickers (this may take a moment)...")
    prices_raw, news_raw = load_market_data(str(DATA_DIR))

    print("  Running shock identification (Stages 1, 1B, 2)...")
    candidates = identify_shocks(prices_raw, news_raw)
    if candidates.empty:
        print("  No shock candidates found — cannot auto-populate manifest.")
        return None

    print("  Computing SC_total and assigning blocks...")
    candidates_sc = compute_sc_total(candidates, news_raw, data_dir=str(DATA_DIR))
    blocks = assign_blocks(candidates_sc, portfolio_df)

    return populate_manifest_from_blocks(blocks, portfolio_df, output_path=MANIFEST_PATH)


def load_manifest(auto_populate: bool = True) -> pd.DataFrame:
    """
    Load and validate scenario_manifest.csv.

    Parameters
    ----------
    auto_populate : bool
        If True (default), re-runs the upstream pipeline to regenerate the
        manifest on every run.  If False, reads the existing file.
    """
    if auto_populate:
        print("\ndata/scenario_manifest.csv — regenerating from upstream pipeline...")
        _portfolio = load_portfolio()
        result = _auto_populate_manifest(_portfolio)

        if result is not None:
            df = result
            df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
            df["block_id"]   = df["block_id"].astype(int)
            df["event_time"] = df["event_time"].astype(str).str.strip()
            n_blocks = df["block_id"].nunique()
            print(f"Manifest loaded: {len(df)} scenarios in {n_blocks} block(s)")
            return df
        print("  Auto-population failed — checking for existing manifest.")
    else:
        print("\nLoading existing data/scenario_manifest.csv (auto-population skipped)...")

    if not MANIFEST_PATH.exists():
        _create_manifest_template()  # prints instructions and exits

    print("  Auto-population failed — loading existing manifest as fallback.")
    df = pd.read_csv(MANIFEST_PATH)
    df.columns = df.columns.str.strip()

    missing = [c for c in MANIFEST_COLUMNS if c not in df.columns]
    if missing:
        print(f"ERROR: scenario_manifest.csv is missing required columns: {missing}")
        sys.exit(1)

    is_template = df["headline"].astype(str).str.startswith("<paste")
    if is_template.all():
        print(
            "\nAuto-population failed and manifest contains only template rows.\n"
            "Run 2_prepare_data.py first to ensure price/news data is available,\n"
            "or fill data/scenario_manifest.csv manually."
        )
        sys.exit(1)
    elif is_template.any():
        n = int(is_template.sum())
        print(f"  [NOTE] {n}/{len(df)} manifest row(s) still have placeholder headlines.")

    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
    df["block_id"]   = df["block_id"].astype(int)
    df["event_time"] = df["event_time"].astype(str).str.strip()

    n_blocks = df["block_id"].nunique()
    print(f"Manifest loaded: {len(df)} scenarios in {n_blocks} block(s)")
    return df


# ── Price reaction ────────────────────────────────────────────────────────────

def _empty_reaction(reason: str) -> dict:
    return {
        "price_before": np.nan,
        "price_after": np.nan,
        "price_reaction_pct": np.nan,
        "reaction_window": f"[MISSING: {reason}]",
    }


def compute_price_reaction(
    price_df: pd.DataFrame,
    event_date,
    event_time_et: str,
) -> dict:
    """
    Compute immediate price reaction around the event timestamp.

    price_before       – last close before event_time_et
    price_after        – close 2 hours after event, or end-of-day (whichever earlier)
    price_reaction_pct – percentage change, rounded to 4 dp
    reaction_window    – descriptive string
    """
    try:
        event_dt_et = pd.Timestamp(
            f"{event_date} {event_time_et}", tz="America/New_York"
        )
    except Exception as exc:
        return _empty_reaction(f"bad event_time format: {exc}")

    event_dt_utc = event_dt_et.tz_convert("UTC")
    eod_et       = pd.Timestamp(f"{event_date} 16:00", tz="America/New_York")
    eod_utc      = eod_et.tz_convert("UTC")
    two_h_utc    = event_dt_utc + pd.Timedelta(hours=2)
    target_utc   = min(two_h_utc, eod_utc)

    before = price_df[price_df["time"] < event_dt_utc]
    if before.empty:
        return _empty_reaction("no bars before event time")
    price_before = float(before.iloc[-1]["close"])

    after_window = price_df[
        (price_df["time"] > event_dt_utc) & (price_df["time"] <= target_utc)
    ]
    if after_window.empty:
        after_any = price_df[price_df["time"] > event_dt_utc]
        if after_any.empty:
            return _empty_reaction("no bars after event time")
        price_after     = float(after_any.iloc[0]["close"])
        reaction_window = "next available bar post-event"
    else:
        price_after     = float(after_window.iloc[-1]["close"])
        reaction_window = (
            "close of trading day"
            if target_utc == eod_utc
            else "2 hours post-event"
        )

    if price_before == 0:
        return _empty_reaction("price_before is zero")

    price_reaction_pct = round(
        (price_after - price_before) / price_before * 100.0, 4
    )

    return {
        "price_before":        round(price_before, 4),
        "price_after":         round(price_after, 4),
        "price_reaction_pct":  price_reaction_pct,
        "reaction_window":     reaction_window,
    }


# ── Deployment manifest ───────────────────────────────────────────────────────

def generate_deployment_manifest(
    manifest_df: pd.DataFrame,
    existing_manifest: dict | None = None,
) -> None:
    """
    Write survey/deployment_manifest.json — required input for 4_deploy_google_forms.py.

    Uses the flat key schema (block_1_v1, block_1_v2, …) that 4_deploy_google_forms.py
    expects. Existing form_id and responder_url values are preserved across re-runs so
    manually entered or previously deployed IDs are never overwritten.

    `existing_manifest` must be the pre-wipe manifest dict (passed by main() after
    snapshotting before shutil.rmtree clears SURVEY_DIR).
    """
    out_path = SURVEY_DIR / "deployment_manifest.json"

    # Use the pre-wipe snapshot if provided; otherwise fall back to reading from disk
    # (handles direct calls outside of main()).
    if existing_manifest is not None:
        existing_data = existing_manifest
    elif out_path.exists():
        try:
            with open(out_path, encoding="utf-8") as fh:
                existing_data = json.load(fh)
        except (json.JSONDecodeError, IOError):
            _warn(f"Could not parse existing {out_path.name} — regenerating from scratch.")
            existing_data = {}
    else:
        existing_data = {}

    existing_forms: dict = existing_data.get("forms", {})
    existing_drive_folder_id: str = existing_data.get("drive_folder_id", "")

    def _get_existing_form_entry(block_id: int, version: int) -> dict:
        """Return existing form entry supporting both flat and legacy nested schemas."""
        flat_key = f"block_{block_id}_v{version}"
        if flat_key in existing_forms:
            return existing_forms[flat_key]
        # Legacy nested schema: {"block_1": {"v1": {"form_id": "..."}}}
        nested = existing_forms.get(f"block_{block_id}", {})
        if isinstance(nested, dict) and f"v{version}" in nested:
            return nested[f"v{version}"]
        return {}

    new_forms: dict = {}
    for block_id in sorted(manifest_df["block_id"].unique()):
        block_rows = manifest_df[manifest_df["block_id"] == block_id]
        scenario_ids = block_rows["scenario_id"].tolist()

        for version in [1, 2]:
            flat_key = f"block_{block_id}_v{version}"
            entry = _get_existing_form_entry(block_id, version)
            existing_id = entry.get("form_id", "")
            responder_url = entry.get("responder_url", "")
            if existing_id and not responder_url:
                responder_url = f"https://docs.google.com/forms/d/{existing_id}/viewform"
            new_forms[flat_key] = {
                "form_id": existing_id,
                "responder_url": responder_url,
                "n_scenarios": len(block_rows),
                "scenario_ids": scenario_ids,
            }

    manifest = {
        "generated":         datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_blocks":          int(manifest_df["block_id"].nunique()),
        "n_scenarios_total": int(len(manifest_df)),
        "drive_folder_id":   existing_drive_folder_id,
        "forms":             new_forms,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    populated = sum(1 for v in new_forms.values() if v.get("form_id", ""))
    print(f"\nDeployment manifest written: {out_path}")
    print(f"  Blocks: {list(new_forms.keys())}")
    print(f"  Total scenarios: {len(manifest_df)}")
    print(f"  Form IDs populated: {populated}/{len(new_forms)}")
    if populated < len(new_forms):
        missing = [k for k, v in new_forms.items() if not v.get("form_id", "")]
        print(
            f"  [NOTE] Set form_id for {missing} in {out_path.name} "
            f"after creating the Google Forms."
        )


# ── Main pipeline ─────────────────────────────────────────────────────────────

def main(auto_populate: bool = True) -> None:
    print("=" * 65)
    print("Survey Assembly Pipeline  -  3_survey_assembly.py")
    print("=" * 65)

    # -- Snapshot deployment manifest before wiping survey/ -------------------
    # deployment_manifest.json lives inside SURVEY_DIR and is wiped below.
    # Read it now so generate_deployment_manifest() can preserve existing form IDs.
    _manifest_snapshot: dict = {}
    _manifest_path = SURVEY_DIR / "deployment_manifest.json"
    if _manifest_path.exists():
        try:
            with open(_manifest_path, encoding="utf-8") as _fh:
                _manifest_snapshot = json.load(_fh)
        except (json.JSONDecodeError, IOError):
            pass

    # -- Output directories ----------------------------------------------------
    if SURVEY_DIR.exists():
        shutil.rmtree(SURVEY_DIR, ignore_errors=True)
        print(f"\nCleared existing {SURVEY_DIR}/")

    out_dirs = {
        "metadata":         SURVEY_DIR / "metadata",
        "charts":           SURVEY_DIR / "charts",
        "dashboards":       SURVEY_DIR / "dashboards",
        "counterbalancing": SURVEY_DIR / "counterbalancing",
    }
    for d in out_dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    # -- [1/9] Load inputs -----------------------------------------------------
    print("\n[1/9] Loading inputs...")
    manifest_df  = load_manifest(auto_populate=auto_populate)
    portfolio_df = load_portfolio()

    tickers = manifest_df["ticker"].unique().tolist()
    print(f"  Tickers: {tickers}")

    prices    = load_price_data(tickers)
    print(f"  Price data loaded: {sorted(prices)}")

    news_data = load_news_data(tickers)
    print(f"  News data loaded:  {sorted(news_data)}")

    # -- [2/9] Scenario metadata -----------------------------------------------
    print("\n[2/9] Generating scenario_metadata.csv...")
    port_lookup = portfolio_df.set_index("ticker")

    meta_df = manifest_df.copy()
    for col in ["company_name", "gics_sector"]:
        mask = meta_df[col].isna() | (meta_df[col].astype(str) == "nan")
        if mask.any():
            meta_df.loc[mask, col] = meta_df.loc[mask, "ticker"].map(
                port_lookup.get(col, pd.Series(dtype=str))
            )

    scenario_metadata = meta_df[[
        "scenario_id", "block_id", "ticker", "company_name",
        "gics_sector", "event_date", "event_time", "num_articles", "event_type",
    ]].copy()
    scenario_metadata["event_date"] = scenario_metadata["event_date"].astype(str)
    out_path = out_dirs["metadata"] / "scenario_metadata.csv"
    scenario_metadata.to_csv(out_path, index=False)
    print(f"  Saved: {out_path.relative_to(SURVEY_DIR)}  ({len(scenario_metadata)} rows)")

    # -- [3/9] Price reactions -------------------------------------------------
    print("\n[3/9] Computing price reactions...")
    reaction_rows = []

    for _, mrow in manifest_df.iterrows():
        sid           = mrow["scenario_id"]
        ticker        = mrow["ticker"]
        event_date    = mrow["event_date"]
        event_time_et = str(mrow.get("event_time", "09:30"))

        base = {
            "scenario_id": sid,
            "ticker":      ticker,
            "event_date":  str(event_date),
            "event_time":  event_time_et,
        }

        if ticker not in prices:
            reaction_rows.append({**base, **_empty_reaction("no price data")})
            continue

        reaction = compute_price_reaction(prices[ticker], event_date, event_time_et)
        reaction_rows.append({**base, **reaction})

    price_reaction_df = pd.DataFrame(reaction_rows)
    out_path = out_dirs["metadata"] / "scenario_price_reaction.csv"
    price_reaction_df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path.relative_to(SURVEY_DIR)}  ({len(price_reaction_df)} rows)")

    reaction_lookup = {
        rrow["scenario_id"]: float(rrow["price_reaction_pct"])
        for _, rrow in price_reaction_df.iterrows()
        if pd.notna(rrow.get("price_reaction_pct"))
    }

    # -- [4/9] Intraday shock charts -------------------------------------------
    print("\n[4/9] Generating Bloomberg-style intraday shock charts (2-day, 30-min)...")
    charts_ok = 0

    for _, mrow in manifest_df.iterrows():
        sid           = mrow["scenario_id"]
        ticker        = mrow["ticker"]
        event_date    = mrow["event_date"]
        event_time_et = str(mrow.get("event_time", "09:30"))

        print(f"  chart for {sid} ({ticker})...", end="", flush=True)

        if ticker not in prices:
            _warn(f"{sid}: no price data - chart skipped")
            print(" skipped")
            continue

        try:
            shock_ts = pd.Timestamp(
                f"{event_date} {event_time_et}", tz="America/New_York"
            )
        except Exception as exc:
            _warn(f"{sid}: invalid event_time '{event_time_et}' - {exc}")
            print(" skipped")
            continue

        shock_dir = _infer_shock_direction(prices[ticker], event_date, event_time_et)
        save_path = out_dirs["charts"] / f"chart_{sid}.png"

        fig = plot_shock_chart(
            prices[ticker], shock_ts, ticker, shock_dir,
            save_path=save_path,
            company_name=str(mrow.get("company_name", "")),
            gics_sector=str(mrow.get("gics_sector", "")),
            price_reaction_pct=reaction_lookup.get(sid),
            event_type=str(mrow.get("event_type", "")),
        )
        if fig is not None:
            plt.close(fig)
            charts_ok += 1
            print(" done")
        else:
            print(" failed")

    print(f"  Charts: {charts_ok}/{len(manifest_df)}")

    # -- [5/9] Shock Score -----------------------------------------------------
    print("\n[5/9] Computing Shock Score components and SC_total...")
    if not HAS_FINBERT:
        print("  [NOTE] FinBERT not available - se_raw will be 0 for all scenarios")
        print("         Install: pip install transformers torch  (then re-run)")

    components_df        = compute_raw_components(manifest_df, prices, news_data)
    sc_df, pca_info      = compute_shock_scores(components_df)

    print("\n  [5b] Computing persistence horizon (CAR Day1/3/5/10)...")
    sc_df = compute_persistence_horizon(sc_df, prices)

    shock_cols = [
        "scenario_id", "ticker", "event_date",
        "ac_raw", "se_raw", "ai_raw", "es_raw",
        "ac_z", "se_z", "ai_z", "es_z",
        "sc_total", "sentiment_direction", "severity_level",
        "persistence_score", "horizon_bucket", "protocol_recommendation",
    ]
    shock_score_out = sc_df[[c for c in shock_cols if c in sc_df.columns]].copy()
    for col in ["ac_raw", "se_raw", "ai_raw", "es_raw",
                "ac_z", "se_z", "ai_z", "es_z", "sc_total", "persistence_score"]:
        if col in shock_score_out.columns:
            shock_score_out[col] = pd.to_numeric(
                shock_score_out[col], errors="coerce"
            ).round(4)
    shock_score_out["event_date"] = shock_score_out["event_date"].astype(str)

    out_path = out_dirs["metadata"] / "scenario_shock_score.csv"
    shock_score_out.to_csv(out_path, index=False)
    print(f"  Saved: {out_path.relative_to(SURVEY_DIR)}  ({len(shock_score_out)} rows)")

    # -- [6/9] Dashboard images ------------------------------------------------
    print("\n[6/9] Generating Shock Score dashboard images...")
    dashboards_ok = 0

    for _, row in sc_df.iterrows():
        sid = row["scenario_id"]
        print(f"  dashboard for {sid}...", end="", flush=True)
        ok = plot_dashboard(row, sid, out_dirs["dashboards"])
        if ok:
            dashboards_ok += 1
            print(" done")
        else:
            print(" failed")

    print(f"  Dashboards: {dashboards_ok}/{len(manifest_df)}")

    # -- [7/9] News text -------------------------------------------------------
    api_status = "ANTHROPIC_API_KEY set" if os.environ.get("ANTHROPIC_API_KEY") else "no API key"
    print(f"\n[7/9] Generating scenario_news_text.csv ({api_status})...")
    news_text_df = build_news_text_df(
        manifest_df, news_data, portfolio_df, cache_path=NEWS_CACHE_PATH
    )

    out_path = out_dirs["metadata"] / "scenario_news_text.csv"
    news_text_df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path.relative_to(SURVEY_DIR)}  ({len(news_text_df)} rows)")

    # -- [8/9] Counterbalancing ------------------------------------------------
    print("\n[8/9] Generating counterbalancing matrix and form assembly guide...")
    matrix_df, guide_df = generate_counterbalancing(manifest_df)

    out_matrix = out_dirs["counterbalancing"] / "counterbalancing_matrix.csv"
    out_guide  = out_dirs["counterbalancing"] / "form_assembly_guide.csv"
    matrix_df.to_csv(out_matrix, index=False)
    guide_df.to_csv(out_guide, index=False)

    n_versions = matrix_df["respondent_block"].nunique()
    print(f"  Respondent versions: {n_versions} "
          f"({n_versions // manifest_df['block_id'].nunique()} per block)")
    print(f"  Saved: {out_matrix.relative_to(SURVEY_DIR)}  ({len(matrix_df)} rows)")
    print(f"  Saved: {out_guide.relative_to(SURVEY_DIR)}  ({len(guide_df)} rows)")

    if not matrix_df.empty:
        per_scenario    = matrix_df.groupby("scenario_id")["show_sc"].sum()
        expected_treat  = n_versions // manifest_df["block_id"].nunique() // 2
        unbalanced      = per_scenario[per_scenario != expected_treat]
        if not unbalanced.empty:
            _warn(
                f"Counterbalancing imbalance: {len(unbalanced)} scenarios have "
                f"show_sc count != {expected_treat}: {unbalanced.to_dict()}"
            )
        else:
            print(f"  Balance check: each scenario is treatment in "
                  f"exactly {expected_treat}/{n_versions // manifest_df['block_id'].nunique()} "
                  f"versions OK")

    # -- Report ----------------------------------------------------------------
    report_md   = generate_report(
        manifest_df, sc_df, pca_info,
        charts_ok, dashboards_ok,
        SURVEY_DIR,
        price_reaction_df=price_reaction_df,
        warnings_list=_WARNINGS,
    )
    report_path = Path("diagnostics") / "survey_assembly_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"\nReport: {report_path}")

    # -- [9/9] Deployment manifest ---------------------------------------------
    print("\n[9/9] Writing deployment manifest (survey/deployment_manifest.json)...")
    generate_deployment_manifest(manifest_df, existing_manifest=_manifest_snapshot)

    # -- Final summary ---------------------------------------------------------
    print("\n" + "=" * 65)
    print("Assembly complete.")
    print(f"  Scenarios:  {len(manifest_df)}")
    print(f"  Charts:     {charts_ok}/{len(manifest_df)}")
    print(f"  Dashboards: {dashboards_ok}/{len(manifest_df)}")
    print(f"  Warnings:   {len(_WARNINGS)}")
    if _WARNINGS:
        print("\n  Warning summary:")
        for w in _WARNINGS:
            print(f"    - {w}")
    print(f"\nAll outputs written to:  {SURVEY_DIR}/")
    print("=" * 65)


if __name__ == "__main__":
    skip_auto = "--skip-auto" in sys.argv
    main(auto_populate=not skip_auto)
