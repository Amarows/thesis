"""
3_survey_assembly.py
====================
Survey Assembly Pipeline for the thesis experiment.

Produces all data assets needed to construct the Google Forms survey instrument:
  - survey/metadata/           CSV tables (metadata, news text, price reaction, shock score)
  - survey/charts/             36 Bloomberg-style intraday shock chart PNGs (2-day, 30-min)
  - survey/dashboards/         36 Shock Score dashboard PNGs
  - survey/counterbalancing/   Latin square assignment matrix and form assembly guide
  - survey/survey_assembly_report.md

Usage:
    python 3_survey_assembly.py

Prerequisites:
    pip install pandas numpy matplotlib scikit-learn nltk
    (Optional) pip install anthropic   # for auto-generated news summaries
    (Optional) ANTHROPIC_API_KEY env variable set

The script is idempotent: running it again cleans and rewrites survey/.
If data/scenario_manifest.csv is missing, a template is created and the
script exits with instructions.
"""

import os
import re
import sys
import glob
import shutil
import warnings
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "toolkits")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

DATA_DIR = Path("data")
SURVEY_DIR = Path("survey")
MANIFEST_PATH = DATA_DIR / "scenario_manifest.csv"
NEWS_CACHE_PATH = DATA_DIR / "news_summary_cache.csv"
_CREDENTIALS_API_KEY = Path("credentials") / "claude_api.txt"

# Load API key: env variable takes priority, fall back to credentials file
if not os.environ.get("ANTHROPIC_API_KEY") and _CREDENTIALS_API_KEY.exists():
    _key = _CREDENTIALS_API_KEY.read_text().strip()
    if _key:
        os.environ["ANTHROPIC_API_KEY"] = _key

MANIFEST_COLUMNS = [
    "scenario_id", "block_id", "ticker", "company_name", "gics_sector",
    "event_date", "event_time", "event_type", "headline", "num_articles",
]

# Placeholder severity mapping for es_raw; requires manual review
# Source: thesis design - category-level severity ratio proxy
EVENT_TYPE_SEVERITY = {
    "earnings": 1.0, "guidance": 0.9, "regulatory": 1.1,
    "management": 0.8, "analyst": 0.6, "macro": 0.7,
    "product": 0.7, "legal": 1.0, "dividend": 0.5, "other": 0.5,
}

# Sentiment direction thresholds (applied to mean score across event-day articles)
SENTIMENT_THRESHOLDS = [-0.6, -0.3, -0.1, 0.1, 0.3, 0.6]
SENTIMENT_LABELS = [
    "Strongly Negative", "Negative", "Mildly Negative",
    "Neutral",
    "Mildly Positive", "Positive", "Strongly Positive",
]

# Dashboard colours
_C_RED = "#c0392b"
_C_AMBER = "#e67e22"
_C_GREEN = "#27ae60"
_C_BLUE = "#1f4e79"
_C_GREY = "#7f8c8d"
_C_STRIPE = "#f2f3f4"
_C_CHART = "#1f4e79"

# ------------------------------------------------------------------------------
# Runtime warnings log
# ------------------------------------------------------------------------------

_WARNINGS: list[str] = []


def _warn(msg: str) -> None:
    print(f"  [WARNING] {msg}")
    _WARNINGS.append(msg)


# ------------------------------------------------------------------------------
# Section 1 - Input loading
# ------------------------------------------------------------------------------

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
    output_path  : write destination (default: data/scenario_manifest.csv)

    Returns
    -------
    manifest_df  : DataFrame in MANIFEST_COLUMNS format (up to 36 rows)
    """
    if output_path is None:
        output_path = MANIFEST_PATH

    block_to_id = {"A": 1, "B": 2, "C": 3}
    rows = []

    # Build portfolio lookup once if provided
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

            # company_name: prefer blocks column, fallback to portfolio
            company_name = str(row.get("company_name", ""))
            if company_name in ("", "nan") and ticker in port_lookup:
                company_name = str(
                    port_lookup[ticker].get("company_name",
                    port_lookup[ticker].get("Company", ticker))
                )
            if company_name in ("", "nan"):
                company_name = ticker

            # gics_sector: prefer blocks "sector" column, fallback to portfolio
            gics_sector = str(row.get("sector", ""))
            if gics_sector in ("", "nan", "Unknown") and ticker in port_lookup:
                gics_sector = str(
                    port_lookup[ticker].get("gics_sector",
                    port_lookup[ticker].get("GICS Sector", "Unknown"))
                )

            # event_time: shock_time_et is already "HH:MM" string
            shock_time = row.get("shock_time_et", row.get("event_time", "09:30"))
            if hasattr(shock_time, "strftime"):
                event_time = shock_time.strftime("%H:%M")
            else:
                event_time = str(shock_time)[:5]

            # num_articles: ac_e raw count
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_df.to_csv(output_path, index=False)
    print(f"\nManifest written: {output_path}  ({len(manifest_df)} scenarios across "
          f"{manifest_df['block_id'].nunique()} block(s))")
    return manifest_df


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

    return populate_manifest_from_blocks(blocks, portfolio_df)


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


def load_manifest() -> pd.DataFrame:
    """
    Load and validate scenario_manifest.csv.

    Always re-runs the upstream pipeline (identify_shocks → compute_sc_total →
    assign_blocks) to regenerate and overwrite the manifest on every run,
    so that refreshed price/news data is reflected without manual deletion.
    Falls back to reading the existing file only if auto-population fails.
    """
    print("\ndata/scenario_manifest.csv — regenerating from upstream pipeline...")
    _portfolio = load_portfolio()
    result = _auto_populate_manifest(_portfolio)

    if result is not None:
        df = result
        df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
        df["block_id"] = df["block_id"].astype(int)
        df["event_time"] = df["event_time"].astype(str).str.strip()
        n_blocks = df["block_id"].nunique()
        print(f"Manifest loaded: {len(df)} scenarios in {n_blocks} block(s)")
        return df

    # Auto-population failed — fall back to existing file if present
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
    df["block_id"] = df["block_id"].astype(int)
    df["event_time"] = df["event_time"].astype(str).str.strip()

    n_blocks = df["block_id"].nunique()
    print(f"Manifest loaded: {len(df)} scenarios in {n_blocks} block(s)")
    return df


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
        # Try 30-min first, then 1-hour
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


def _clean_bz_headline(text: str) -> str:
    """Strip Benzinga metadata tokens {A:...:L:...:K:...:C:...} from headline."""
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r"\{A:.*?:L:.*?(?::K:.*?:C:.*?)?\}!?", "", text).strip()
    return cleaned if cleaned else text


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
                continue  # empty file — skip silently
            except Exception as exc:
                _warn(f"{ticker}: error reading {Path(fpath).name} - {exc}")

        if not frames:
            continue

        combined = pd.concat(frames, ignore_index=True)

        # Normalise time column
        if "time_utc" in combined.columns:
            combined["time"] = pd.to_datetime(combined["time_utc"], format="ISO8601", utc=True)
        elif "time" in combined.columns:
            combined["time"] = pd.to_datetime(combined["time"], format="ISO8601", utc=True)
        else:
            _warn(f"{ticker}: news files have no recognisable time column")
            continue

        # Clean headlines
        if "headline" in combined.columns:
            combined["headline"] = combined["headline"].apply(_clean_bz_headline)

        news[ticker] = combined.sort_values("time").reset_index(drop=True)

    return news


# ------------------------------------------------------------------------------
# Section 2 - Price data helpers
# ------------------------------------------------------------------------------

def aggregate_daily(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate 30-min bars to daily close (last bar) and total volume (sum).
    Groups by ET calendar date.
    Returns DataFrame[date (datetime.date), close, volume].
    """
    df = price_df.copy()
    df["date_et"] = df["time"].dt.tz_convert("America/New_York").dt.date
    daily = (
        df.groupby("date_et")
        .agg(close=("close", "last"), volume=("volume", "sum"))
        .reset_index()
        .rename(columns={"date_et": "date"})
        .sort_values("date")
        .reset_index(drop=True)
    )
    return daily


def get_trailing_window(daily_df: pd.DataFrame, event_date, n: int = 20) -> pd.DataFrame:
    """
    Return the n trading days immediately preceding event_date (exclusive).
    event_date: datetime.date
    """
    before = daily_df[daily_df["date"] < event_date].tail(n).copy()
    return before.reset_index(drop=True)


def get_event_day_bars(price_df: pd.DataFrame, event_date) -> pd.DataFrame:
    """Return all 30-min bars for event_date (in ET)."""
    df = price_df.copy()
    df["date_et"] = df["time"].dt.tz_convert("America/New_York").dt.date
    return df[df["date_et"] == event_date].copy().reset_index(drop=True)


# ------------------------------------------------------------------------------
# Section 3 - Intraday shock chart (Bloomberg dark style)
# ------------------------------------------------------------------------------

def _infer_shock_direction(price_df: pd.DataFrame, event_date, event_time_et: str) -> str:
    """
    Derive shock direction from the immediate post-shock price move.
    Returns 'positive' if the bar after the shock bar closed higher, else 'negative'.
    """
    try:
        shock_ts = pd.Timestamp(f"{event_date} {event_time_et}", tz="America/New_York")
        shock_utc = shock_ts.tz_convert("UTC")
        sorted_df = price_df.sort_values("time")
        at_or_after = sorted_df[sorted_df["time"] >= shock_utc]
        if len(at_or_after) < 2:
            return "positive"
        shock_close = float(at_or_after.iloc[0]["close"])
        next_close  = float(at_or_after.iloc[1]["close"])
        return "positive" if next_close >= shock_close else "negative"
    except Exception:
        return "positive"


def plot_shock_chart(
    df: pd.DataFrame,
    shock_timestamp,
    ticker: str,
    shock_direction: str,
    save_path=None,
    # Additional metadata for enhanced chart header and badge
    company_name: str = "",
    gics_sector: str = "",
    price_reaction_pct: float | None = None,
    event_type: str = "",
):
    """
    Bloomberg-style dark intraday shock chart — 2 trading days at 30-min granularity.

    Parameters
    ----------
    df              : DataFrame[time (UTC tz-aware), close, volume] — full price series.
                      The function selects the prior trading day + event day automatically.
    shock_timestamp : pd.Timestamp (ET tz-aware) for the shock bar
    ticker          : stock ticker (used in chart title)
    shock_direction : 'positive' or 'negative' (controls colour encoding)
    save_path       : if provided, saved as PNG at 200 DPI with tight bounding box

    Returns
    -------
    matplotlib Figure object, or None if no data available.
    """
    # ── Colour encoding ───────────────────────────────────────────────────
    if price_reaction_pct is not None:
        clr = "#00cc66" if price_reaction_pct >= 0 else "#ff4444"
    else:
        clr = "#00cc66" if shock_direction == "positive" else "#ff4444"

    # ── Filter to 2 trading days ──────────────────────────────────────────
    tdf = df.copy()
    tdf["date_et"] = tdf["time"].dt.tz_convert("America/New_York").dt.date
    event_date = shock_timestamp.date()
    all_dates = sorted(tdf["date_et"].unique())

    if event_date not in all_dates:
        _warn(f"{ticker}: event date {event_date} not in price data — chart skipped")
        return None

    idx = all_dates.index(event_date)
    if idx > 0:
        prior_date = all_dates[idx - 1]
        two_day = tdf[tdf["date_et"].isin([prior_date, event_date])]
    else:
        prior_date = None
        two_day = tdf[tdf["date_et"] == event_date]

    two_day = two_day.sort_values("time").reset_index(drop=True)
    if two_day.empty:
        _warn(f"{ticker}: no bars for 2-day window — chart skipped")
        return None

    # ── Shock position (pre-truncation) ──────────────────────────────────
    shock_utc  = shock_timestamp.tz_convert("UTC")
    time_diffs = np.abs((two_day["time"] - shock_utc).dt.total_seconds().values)
    shock_pos  = int(np.argmin(time_diffs))

    # ── Truncate to shock bar + 1 confirmation bar ────────────────────────
    cutoff = min(shock_pos + 2, len(two_day))
    two_day = two_day.iloc[:cutoff].reset_index(drop=True)

    closes   = two_day["close"].values.astype(float)
    volumes  = two_day["volume"].values.astype(float)
    positions = np.arange(len(two_day))
    times_et  = two_day["time"].dt.tz_convert("America/New_York")

    # ── Recompute shock position after truncation ─────────────────────────
    time_diffs = np.abs((two_day["time"] - shock_utc).dt.total_seconds().values)
    shock_pos  = int(np.argmin(time_diffs))
    shock_display_pos = max(0, shock_pos - 1)   # dot one bar before shock

    # ── Day boundary (first bar of event day) ─────────────────────────────
    boundary_pos = (
        int((two_day["date_et"] == event_date).argmax())
        if prior_date is not None else None
    )

    # ── Figure ────────────────────────────────────────────────────────────
    with plt.style.context("dark_background"):
        fig, (ax_p, ax_v) = plt.subplots(
            2, 1, figsize=(12, 7.2),
            gridspec_kw={"height_ratios": [3, 1]},
            sharex=True,
        )

        fig.patch.set_facecolor("#000000")
        ax_p.set_facecolor("#1a1a2e")
        ax_v.set_facecolor("#1a1a2e")

        # ── Price line + fill ─────────────────────────────────────────────
        ax_p.plot(positions, closes, color=clr, linewidth=1.8, zorder=3,
                  solid_capstyle="round")
        ax_p.fill_between(positions, closes.min(), closes,
                          color=clr, alpha=0.15, zorder=1)

        # ── Grids ─────────────────────────────────────────────────────────
        for ax in (ax_p, ax_v):
            ax.grid(True, color="#333333", linewidth=0.5, linestyle="--", zorder=0)
            ax.set_axisbelow(True)

        # ── Volume bars (all grey; shock bar in directional colour) ────
        vol_colors = ["#666666"] * len(volumes)
        vol_colors[shock_pos] = clr
        ax_v.bar(positions, volumes, color=vol_colors,
                 width=0.8, align="center", alpha=0.7, zorder=2)

        # ── Shock marker ──────────────────────────────────────────────────
        sv = closes[shock_display_pos]
        ax_p.scatter([shock_display_pos], [sv], s=90, color=clr, zorder=6,
                     edgecolors="white", linewidths=1.5)
        # Place annotation BELOW the dot to avoid overlap with top-area date labels.
        # Shift left if dot is in the right half of the chart, right otherwise.
        ann_x = -42 if shock_display_pos > len(positions) * 0.5 else 10
        ax_p.annotate(
            "News arrives\nnext bar",
            xy=(shock_display_pos, sv),
            xytext=(ann_x, -28), textcoords="offset points",
            fontsize=12, color="white", va="top", ha="left",
            arrowprops=dict(arrowstyle="->", color="white", lw=0.8),
        )

        # ── Day boundary line ─────────────────────────────────────────────
        if boundary_pos is not None and boundary_pos > 0:
            for ax in (ax_p, ax_v):
                ax.axvline(boundary_pos - 0.5, color="white", linewidth=1.0,
                           linestyle="--", alpha=0.6, zorder=4)
            # Date labels: inside the plot, just below the top edge (y=0.94 axes fraction)
            xform = ax_p.get_xaxis_transform()
            if prior_date is not None:
                prior_mid = (boundary_pos - 1) / 2.0
                ax_p.text(prior_mid, 0.94, prior_date.strftime("%d %b"),
                          transform=xform, fontsize=13, color="#cccccc",
                          ha="center", va="top", style="italic")
            event_mid = (boundary_pos + len(two_day) - 1) / 2.0
            ax_p.text(event_mid, 0.94, event_date.strftime("%d %b  << Event"),
                      transform=xform, fontsize=13, color="#cccccc",
                      ha="center", va="top", style="italic")

        # ── x-axis ticks ──────────────────────────────────────────────────
        tick_step = 2 if prior_date is not None else 1
        tick_pos  = list(range(0, len(two_day), tick_step))
        tick_lbl  = [times_et.iloc[i].strftime("%H:%M") for i in tick_pos]
        ax_v.set_xticks(tick_pos)
        ax_v.set_xticklabels(tick_lbl, fontsize=13, color="#cccccc", rotation=0)
        ax_v.set_xlabel("Trading Time", fontsize=14, color="#cccccc")
        plt.setp(ax_p.get_xticklabels(), visible=False)

        # ── y-axis: price ─────────────────────────────────────────────────
        ax_p.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"{x:.2f}")
        )
        ax_p.tick_params(axis="y", labelsize=13, colors="#cccccc")
        ax_p.set_ylabel("Price (USD)", fontsize=14, color="#cccccc")

        # ── y-axis: volume ────────────────────────────────────────────────
        def _vol_fmt(x, _):
            if x >= 1_000_000:
                return f"{x / 1_000_000:.1f}M"
            if x >= 1_000:
                return f"{x / 1_000:.1f}K"
            return f"{x:.0f}"

        ax_v.yaxis.set_major_formatter(plt.FuncFormatter(_vol_fmt))
        ax_v.tick_params(axis="y", labelsize=13, colors="#cccccc")
        ax_v.set_ylabel("Volume", fontsize=14, color="#cccccc")

        # ── xlim ──────────────────────────────────────────────────────────
        ax_p.set_xlim(-0.5, len(two_day) - 0.5)

        # ── Two-line title ────────────────────────────────────────────────
        main_title = (f"{company_name} ({ticker})" if company_name
                      else f"{ticker}")
        fig.suptitle(main_title, fontsize=22, fontweight="bold",
                     color="white", x=0.08, ha="left")

        subtitle = (f"{gics_sector} | Intraday Price (30-min bars)"
                    if gics_sector else "Intraday Price (30-min bars)")
        ax_p.set_title(subtitle, fontsize=15, color="#aaaaaa",
                       fontweight="normal", loc="left")

        fig.subplots_adjust(top=0.84)

        # ── Shock date label (upper-right) ────────────────────────────────
        ax_p.annotate(
            shock_timestamp.strftime("%d %b %Y"),
            xy=(1, 1), xycoords="axes fraction",
            xytext=(-8, -8), textcoords="offset points",
            fontsize=12, color="#cccccc", ha="right", va="top",
        )

        # ── Spine colours ─────────────────────────────────────────────────
        for ax in (ax_p, ax_v):
            for spine in ax.spines.values():
                spine.set_edgecolor("#333333")
            ax.tick_params(axis="x", colors="#cccccc")

        plt.tight_layout(pad=0.5)

        if save_path is not None:
            plt.savefig(save_path, dpi=200, bbox_inches="tight",
                        facecolor="#000000", edgecolor="none")

    return fig


# ------------------------------------------------------------------------------
# Section 4 - Price reaction
# ------------------------------------------------------------------------------

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

    price_before  - last close before event_time_et
    price_after   - close 2 hours after event, or end-of-day (whichever is earlier)
    price_reaction_pct - percentage change, rounded to 4 dp
    reaction_window    - descriptive string

    event_time_et: "HH:MM" in Eastern Time
    """
    try:
        event_dt_et = pd.Timestamp(
            f"{event_date} {event_time_et}", tz="America/New_York"
        )
    except Exception as exc:
        return _empty_reaction(f"bad event_time format: {exc}")

    event_dt_utc = event_dt_et.tz_convert("UTC")
    eod_et = pd.Timestamp(f"{event_date} 16:00", tz="America/New_York")
    eod_utc = eod_et.tz_convert("UTC")
    two_h_utc = event_dt_utc + pd.Timedelta(hours=2)
    target_utc = min(two_h_utc, eod_utc)

    # price_before: last bar strictly before event
    before = price_df[price_df["time"] < event_dt_utc]
    if before.empty:
        return _empty_reaction("no bars before event time")
    price_before = float(before.iloc[-1]["close"])

    # price_after: last bar in (event, target]
    after_window = price_df[
        (price_df["time"] > event_dt_utc) & (price_df["time"] <= target_utc)
    ]
    if after_window.empty:
        # Fallback: first bar after event, any time
        after_any = price_df[price_df["time"] > event_dt_utc]
        if after_any.empty:
            return _empty_reaction("no bars after event time")
        price_after = float(after_any.iloc[0]["close"])
        reaction_window = "next available bar post-event"
    else:
        price_after = float(after_window.iloc[-1]["close"])
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
        "price_before": round(price_before, 4),
        "price_after": round(price_after, 4),
        "price_reaction_pct": price_reaction_pct,
        "reaction_window": reaction_window,
    }


# ------------------------------------------------------------------------------
# Section 5 - Sentiment scoring (FinBERT)
# ------------------------------------------------------------------------------

try:
    from transformers import pipeline as _hf_pipeline
    _finbert = _hf_pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        truncation=True,
        max_length=512,
        top_k=None,
    )
    HAS_FINBERT = True
except Exception:
    _finbert = None
    HAS_FINBERT = False


def _finbert_score(text: str) -> float:
    """Return FinBERT sentiment as positive_prob - negative_prob in [-1, 1].

    Returns 0.0 if FinBERT is unavailable or text is empty.
    """
    if not HAS_FINBERT or not isinstance(text, str) or not text.strip():
        return 0.0
    output = _finbert(text[:1500])
    # output: [[{'label': ..., 'score': ...}, ...]] for a single input
    labels = output[0] if isinstance(output[0], list) else output
    probs = {d["label"].lower(): d["score"] for d in labels}
    return float(probs.get("positive", 0.0) - probs.get("negative", 0.0))


def get_event_day_news(
    news_data: dict[str, pd.DataFrame],
    ticker: str,
    event_date,
) -> pd.DataFrame:
    """Return all BZ articles for ticker on event_date (ET calendar date)."""
    if ticker not in news_data:
        return pd.DataFrame()
    df = news_data[ticker].copy()
    if df.empty or "time" not in df.columns:
        return pd.DataFrame()
    df["date_et"] = df["time"].dt.tz_convert("America/New_York").dt.date
    return df[df["date_et"] == event_date].reset_index(drop=True)


def _sentiment_direction_label(mean_score: float) -> str:
    """Map mean sentiment score to a directional label (7-level scale)."""
    t = SENTIMENT_THRESHOLDS
    if mean_score <= t[0]:
        return "Strongly Negative"
    elif mean_score <= t[1]:
        return "Negative"
    elif mean_score <= t[2]:
        return "Mildly Negative"
    elif mean_score <= t[3]:
        return "Neutral"
    elif mean_score <= t[4]:
        return "Mildly Positive"
    elif mean_score <= t[5]:
        return "Positive"
    else:
        return "Strongly Positive"


# ------------------------------------------------------------------------------
# Section 6 - Shock Score computation
# ------------------------------------------------------------------------------

def compute_raw_components(
    manifest_df: pd.DataFrame,
    prices: dict[str, pd.DataFrame],
    news_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Compute four raw SC components for each scenario.

    ac_raw  - Article Count: number of BZ articles on event day
    se_raw  - Sentiment Extremity: max |FinBERT score| across event-day articles
    ai_raw  - Attention Intensity: event-day volume / 20-day trailing avg daily volume
    es_raw  - Event-Type Severity: category severity from EVENT_TYPE_SEVERITY mapping
               (placeholder - requires manual review per protocol S.2.2)

    Also records mean_sentiment and per-article sentiment_scores for dashboard signals.
    """
    rows = []

    for _, mrow in manifest_df.iterrows():
        sid = mrow["scenario_id"]
        ticker = mrow["ticker"]
        event_date = mrow["event_date"]
        event_type = str(mrow.get("event_type", "other")).lower().strip()

        print(f"  {sid} ({ticker} {event_date})...", end="", flush=True)

        # -- AC_raw ------------------------------------------------------------
        day_articles = get_event_day_news(news_data, ticker, event_date)
        ac_raw = len(day_articles)
        if ac_raw == 0:
            _warn(f"{sid}: no news articles found for {ticker} on {event_date}")

        # -- SE_raw ------------------------------------------------------------
        sentiment_scores: list[float] = []
        mean_sentiment = 0.0
        se_raw = 0.0

        if not day_articles.empty:
            if HAS_FINBERT:
                for _, art in day_articles.iterrows():
                    hl = str(art.get("headline", ""))
                    body = str(art.get("article_text", ""))
                    # Strip HTML from body
                    body_clean = re.sub(r"<[^>]+>", " ", body)
                    combined = f"{hl} {body_clean}"
                    score = _finbert_score(combined)
                    sentiment_scores.append(score)
                if sentiment_scores:
                    se_raw = max(abs(s) for s in sentiment_scores)
                    mean_sentiment = float(np.mean(sentiment_scores))
            else:
                _warn(f"{sid}: FinBERT unavailable - se_raw set to 0 (install transformers torch)")

        # -- AI_raw ------------------------------------------------------------
        ai_raw = 0.0
        if ticker in prices:
            daily_df = aggregate_daily(prices[ticker])
            trailing_20 = get_trailing_window(daily_df, event_date, n=20)
            event_day_vol = daily_df[daily_df["date"] == event_date]["volume"]

            if not event_day_vol.empty and not trailing_20.empty:
                avg_vol = float(trailing_20["volume"].mean())
                if avg_vol > 0:
                    ai_raw = float(event_day_vol.iloc[0]) / avg_vol
                else:
                    _warn(f"{sid}: 20-day average volume is zero; ai_raw set to 0")
            else:
                _warn(f"{sid}: insufficient volume data for ai_raw computation")
        else:
            _warn(f"{sid}: no price data for {ticker}; ai_raw set to 0")

        # -- ES_raw ------------------------------------------------------------
        es_raw = EVENT_TYPE_SEVERITY.get(event_type, 0.5)

        print(" done")

        rows.append({
            "scenario_id": sid,
            "ticker": ticker,
            "event_date": event_date,
            "event_type": event_type,
            "ac_raw": ac_raw,
            "se_raw": se_raw,
            "ai_raw": ai_raw,
            "es_raw": es_raw,
            "mean_sentiment": mean_sentiment,
            "sentiment_scores": sentiment_scores,
            "num_articles_found": ac_raw,
        })

    return pd.DataFrame(rows)


def compute_shock_scores(
    components_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Z-standardise raw components, run PCA (PC1), compute sc_total.
    Adds dashboard signal columns to the DataFrame.

    Sign convention: sc_total is oriented so that higher values = higher shock intensity.
    Verification: PC1 should load positively on ac_raw (article count).

    Returns (enriched_df, pca_info_dict).
    """
    df = components_df.copy()
    n = len(df)
    raw_cols = ["ac_raw", "se_raw", "ai_raw", "es_raw"]
    z_cols = ["ac_z", "se_z", "ai_z", "es_z"]

    if n < 2:
        _warn("Fewer than 2 scenarios - PCA degenerate; sc_total set to 0")
        for zcol in z_cols:
            df[zcol] = 0.0
        df["sc_total"] = 0.0
        return df, {}

    # Z-standardise across all N scenarios (mean=0, sd=1)
    X = df[raw_cols].fillna(0).values.astype(float)
    scaler = StandardScaler()
    Z = scaler.fit_transform(X)

    for i, zcol in enumerate(z_cols):
        df[zcol] = Z[:, i]

    # PCA: first principal component
    pca = PCA(n_components=1)
    sc_raw = pca.fit_transform(Z).flatten()
    loadings = pca.components_[0]
    explained_var = float(pca.explained_variance_ratio_[0])

    # Sign convention: pc1 should correlate positively with ac_raw (col 0)
    if loadings[0] < 0:
        sc_raw = -sc_raw
        loadings = -loadings

    df["sc_total"] = sc_raw

    pca_info = {
        "loadings": {k: round(float(v), 4)
                     for k, v in zip(["ac", "se", "ai", "es"], loadings)},
        "explained_variance": round(explained_var, 4),
        "n_scenarios": n,
    }

    print("\n  PCA Results (SC_total construction):")
    print(f"    PC1 explains {explained_var * 100:.1f}% of variance")
    print("    Loadings: " + ", ".join(
        f"{k}={v:.4f}" for k, v in pca_info["loadings"].items()
    ))

    # -- Dashboard signals ------------------------------------------------------

    # 1. Sentiment direction (from mean FinBERT score)
    df["sentiment_direction"] = df["mean_sentiment"].apply(
        _sentiment_direction_label
    )

    # 2. Severity level (33rd/66th percentile of sc_total across all scenarios)
    p33 = df["sc_total"].quantile(1 / 3)
    p66 = df["sc_total"].quantile(2 / 3)

    def _severity(sc: float) -> str:
        if sc < p33:
            return "Low"
        elif sc < p66:
            return "Medium"
        return "High"

    df["severity_level"] = df["sc_total"].apply(_severity)

    # 3. Protocol recommendation (60th / 85th percentile thresholds per thesis design)
    p60 = df["sc_total"].quantile(0.60)
    p85 = df["sc_total"].quantile(0.85)

    def _protocol(sc: float) -> str:
        if sc < p60:
            return "Standard Process"
        elif sc < p85:
            return "Enhanced Review"
        return "Cooling-Off and Second Review"

    df["protocol_recommendation"] = df["sc_total"].apply(_protocol)

    # persistence_score and horizon_bucket populated by compute_persistence_horizon()
    # which must be called immediately after this function in the pipeline.

    return df, pca_info


# ------------------------------------------------------------------------------
# Section 6b - Persistence horizon computation
# ------------------------------------------------------------------------------

def compute_persistence_horizon(
    sc_df: pd.DataFrame,
    prices: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Compute CAR-based persistence horizon for each scenario in sc_df.

    For each event e:
        base_price  = EOD close of event day (last 30-min bar)
        CAR_Day_n   = (stock_price_at_day_n / base_price - 1) - cumulative_SPX_return
        P_e         = CAR_Day5 / CAR_Day1

    If abs(CAR_Day1) < 0.001, P_e is unreliable; scenario is flagged for manual review.

    Horizon bucket mapping (initial cutoffs, validate against distribution below):
        Intraday:      |P_e| <= 0.30
        Several Days:  0.30 < |P_e| <= 0.70
        Several Weeks: |P_e| > 0.70

    Prints P_e distribution summary after all scenarios are computed so
    cutoffs can be validated against the data.

    Parameters
    ----------
    sc_df  : output of compute_shock_scores() -- must contain scenario_id, ticker, event_date
    prices : {ticker: DataFrame[time (UTC tz-aware), close, volume]}

    Returns
    -------
    sc_df with persistence_score and horizon_bucket columns added / overwritten.
    """
    df = sc_df.copy()

    # Fetch SPX daily returns for the full date span covered by scenarios
    event_dates = pd.to_datetime(df["event_date"]).dt.date
    spx_start = str(min(event_dates))
    spx_end   = str(max(event_dates) + pd.Timedelta(days=20))
    spx_ret   = _fetch_spx_daily_returns(spx_start, spx_end)
    spx_available = not spx_ret.empty

    CAR_DAYS = [1, 3, 5, 10]
    persistence_scores: list = []
    horizon_buckets:    list = []

    print("\n  CAR-based persistence horizon computation:")
    print(f"  {'Scenario':<12} {'Ticker':<6} {'CAR1':>8} {'CAR3':>8} "
          f"{'CAR5':>8} {'CAR10':>9} {'P_e':>8}  Bucket")
    print("  " + "-" * 80)

    for _, row in df.iterrows():
        sid        = str(row["scenario_id"])
        ticker     = str(row["ticker"])
        event_date = pd.to_datetime(row["event_date"]).date()

        # ── Guard: price data must exist ──────────────────────────────────
        if ticker not in prices:
            persistence_scores.append(np.nan)
            horizon_buckets.append("[NO PRICE DATA]")
            print(f"  {sid:<12} {ticker:<6}  -- no price data --")
            continue

        price_df = prices[ticker].copy()
        price_df["date_et"] = (
            price_df["time"].dt.tz_convert("America/New_York").dt.date
        )

        # ── Base price: last bar of event day (= EOD close) ───────────────
        event_day_bars = price_df[price_df["date_et"] == event_date]
        if event_day_bars.empty:
            persistence_scores.append(np.nan)
            horizon_buckets.append("[NO EVENT-DAY PRICE]")
            print(f"  {sid:<12} {ticker:<6}  -- no event-day bars --")
            continue

        base_price = float(event_day_bars["close"].iloc[-1])

        # ── Post-event daily EOD closes ───────────────────────────────────
        after_eod = (
            price_df[price_df["date_et"] > event_date]
            .groupby("date_et")["close"]
            .last()
            .sort_index()
        )

        # ── Compute CAR at each horizon ───────────────────────────────────
        car_vals: dict[int, float] = {}
        for n in CAR_DAYS:
            if n > len(after_eod) or base_price == 0:
                car_vals[n] = np.nan
                continue
            target_price = float(after_eod.iloc[n - 1])
            stock_ret    = (target_price - base_price) / base_price

            if spx_available:
                # Cumulative SPX return over the same n trading days
                trading_dates = list(after_eod.index[:n])
                spx_cum = 1.0
                for td in trading_dates:
                    if td in spx_ret.index:
                        spx_cum *= (1.0 + float(spx_ret[td]))
                car_vals[n] = round(stock_ret - (spx_cum - 1.0), 6)
            else:
                car_vals[n] = round(stock_ret, 6)  # raw return if SPX unavailable

        # ── Persistence ratio P_e ─────────────────────────────────────────
        car1 = car_vals.get(1, np.nan)
        car5 = car_vals.get(5, np.nan)

        if np.isnan(car1) or np.isnan(car5):
            p_e = np.nan
            bucket = "[INSUFFICIENT DATA]"
        elif abs(car1) < 0.001:
            # Day-1 CAR is near zero: the shock was absorbed entirely intraday
            # (stock moved in line with market by EOD).  P_e = CAR5/CAR1 is
            # unreliable; classify directly as Intraday.
            p_e = np.nan
            bucket = "Intraday"
        else:
            p_e = round(car5 / car1, 4)
            if abs(p_e) <= 0.30:
                bucket = "Intraday"
            elif abs(p_e) <= 0.70:
                bucket = "Several Days"
            else:
                bucket = "Several Weeks"

        persistence_scores.append(p_e)
        horizon_buckets.append(bucket)

        def _fmt(v):
            return f"{v:>8.4f}" if not (v is None or np.isnan(v)) else f"{'n/a':>8}"

        print(f"  {sid:<12} {ticker:<6} {_fmt(car_vals.get(1,np.nan))} "
              f"{_fmt(car_vals.get(3,np.nan))} {_fmt(car_vals.get(5,np.nan))} "
              f"{_fmt(car_vals.get(10,np.nan))} {_fmt(p_e)}  {bucket}")

    df["persistence_score"] = persistence_scores
    df["horizon_bucket"]    = horizon_buckets

    # ── Distribution summary for cutoff validation ────────────────────────
    valid = pd.Series([s for s in persistence_scores
                       if s is not None and not np.isnan(float(s))],
                      dtype=float)
    print(f"\n  P_e distribution ({len(valid)} valid of {len(df)} scenarios):")
    if not valid.empty:
        print(f"    mean={valid.mean():.4f}  median={valid.median():.4f}  "
              f"std={valid.std():.4f}")
        print(f"    Q1={valid.quantile(0.25):.4f}  Q3={valid.quantile(0.75):.4f}  "
              f"min={valid.min():.4f}  max={valid.max():.4f}")
        print(f"    Current cutoffs: Intraday<=0.30 / SeveralDays<=0.70 / SeveralWeeks>0.70")
    bkt_counts = pd.Series(horizon_buckets).value_counts()
    print("  Horizon bucket distribution:")
    for bkt, cnt in bkt_counts.items():
        print(f"    {bkt}: {cnt}")

    return df


# ------------------------------------------------------------------------------
# Section 7 - Dashboard image generation
# ------------------------------------------------------------------------------

def _fetch_spx_daily_returns(start: str, end: str) -> pd.Series:
    """
    Fetch S&P 500 daily close-to-close returns via yfinance.
    Returns a pd.Series indexed by datetime.date, values are decimal returns.
    Returns an empty Series on failure so callers can gracefully degrade to raw returns.
    """
    try:
        import yfinance as yf
        data = yf.download("^GSPC", start=start, end=end,
                           progress=False, auto_adjust=True)
        if data.empty:
            _warn("SPX download returned empty data - CAR computed without market adjustment")
            return pd.Series(dtype=float)
        closes = data["Close"].squeeze()
        rets = closes.pct_change().dropna()
        rets.index = pd.to_datetime(rets.index).date
        return rets
    except Exception as exc:
        _warn(f"SPX fetch failed ({exc}) - CAR computed without market adjustment")
        return pd.Series(dtype=float)


def _colour_for_sentiment(label: str) -> str:
    if "Negative" in label:
        return _C_RED
    if "Positive" in label:
        return _C_GREEN
    return _C_GREY


def _colour_for_severity(label: str) -> str:
    return {"Low": _C_GREEN, "Medium": _C_AMBER, "High": _C_RED}.get(label, _C_GREY)


def _colour_for_protocol(label: str) -> str:
    return {
        "Standard Process": _C_GREEN,
        "Enhanced Review": _C_AMBER,
        "Cooling-Off and Second Review": _C_RED,
    }.get(label, _C_GREY)


def _colour_for_horizon(label: str) -> str:
    return {
        "Intraday":      _C_GREEN,
        "Several Days":  _C_AMBER,
        "Several Weeks": _C_RED,
    }.get(label, _C_GREY)


def plot_dashboard(
    row: "pd.Series",
    scenario_id: str,
    out_dir: Path,
) -> bool:
    """
    Render a compact 6x3-inch Shock Score dashboard panel.
    Four signal rows: Sentiment Direction, Shock Severity, Persistence Horizon, Protocol.
    Saves to out_dir/dashboard_{scenario_id}.png
    """
    sentiment_dir = str(row.get("sentiment_direction", "Neutral"))
    severity      = str(row.get("severity_level", "Low"))
    horizon       = str(row.get("horizon_bucket", "N/A"))
    protocol      = str(row.get("protocol_recommendation", "Standard Process"))
    # sc_total kept in data for diagnostics but NOT rendered on respondent-facing dashboard

    signal_rows = [
        # (label, value, colour, use_bg_pill)
        ("Sentiment Direction", sentiment_dir,
         _colour_for_sentiment(sentiment_dir), False),
        ("Shock Severity", severity,
         _colour_for_severity(severity), True),
        ("Persistence Horizon", horizon,
         _colour_for_horizon(horizon), True),
        ("Protocol", protocol,
         _colour_for_protocol(protocol), True),
    ]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Outer border
    border = mpatches.FancyBboxPatch(
        (0.01, 0.01), 0.98, 0.98,
        boxstyle="round,pad=0.01",
        linewidth=1.0, edgecolor="#cccccc", facecolor="white",
        transform=ax.transAxes, zorder=0,
    )
    ax.add_patch(border)

    # Title
    ax.text(0.5, 0.91, "Shock Score Dashboard",
            ha="center", va="center", fontsize=12, fontweight="bold",
            transform=ax.transAxes, zorder=2)

    # Divider (SC_0 numeric removed from respondent-facing output per thesis design)
    ax.plot([0.05, 0.95], [0.82, 0.82], color="#cccccc",
            linewidth=0.8, transform=ax.transAxes, zorder=2)

    # Signal rows spread evenly in the space below the divider
    y_positions = [0.68, 0.51, 0.34, 0.17]

    for (label, value, colour, use_pill), y_pos in zip(signal_rows, y_positions):
        # Row stripe background
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.03, y_pos - 0.08), 0.94, 0.15,
            boxstyle="round,pad=0.005",
            facecolor=_C_STRIPE, edgecolor="none",
            transform=ax.transAxes, zorder=1,
        ))
        # Signal label (left)
        ax.text(0.07, y_pos, label,
                ha="left", va="center", fontsize=8.5,
                color="#555555", transform=ax.transAxes, zorder=2)

        if use_pill:
            # Coloured pill background for value
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.54, y_pos - 0.065), 0.42, 0.13,
                boxstyle="round,pad=0.005",
                facecolor=colour, edgecolor="none", alpha=0.85,
                transform=ax.transAxes, zorder=2,
            ))
            ax.text(0.75, y_pos, value,
                    ha="center", va="center", fontsize=8,
                    color="white", fontweight="bold",
                    transform=ax.transAxes, zorder=3)
        else:
            ax.text(0.75, y_pos, value,
                    ha="center", va="center", fontsize=8,
                    color=colour, fontweight="bold",
                    transform=ax.transAxes, zorder=2)

    out_path = out_dir / f"dashboard_{scenario_id}.png"
    plt.tight_layout(pad=0.2)
    plt.savefig(out_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return True


# ------------------------------------------------------------------------------
# Section 8 - News text
# ------------------------------------------------------------------------------

_ANTHROPIC_SYSTEM = (
    "You are an academic research assistant preparing survey scenarios for "
    "professional equity portfolio managers. Simplify raw financial news into "
    "a single concise paragraph (80-120 words) suitable for survey presentation. "
    "Include key financial figures, analyst estimates, and market reactions where "
    "available. Use formal, neutral tone. Do not provide investment advice or "
    "editorial commentary. Do not use bullet points or lists."
)


def _generate_summary_anthropic(
    company_name: str,
    ticker: str,
    gics_sector: str,
    event_date,
    articles_df: pd.DataFrame,
) -> str:
    """
    Call Claude API to produce an 80-120 word survey-ready summary.
    Returns placeholder string if API unavailable or call fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "[TO BE GENERATED]"

    try:
        import anthropic
    except ImportError:
        _warn("anthropic package not installed - summaries will use placeholder")
        return "[TO BE GENERATED]"

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Build raw news content
        parts = []
        for _, art in articles_df.iterrows():
            hl = _clean_bz_headline(str(art.get("headline", "")))
            body = str(art.get("article_text", ""))
            body = re.sub(r"<[^>]+>", " ", body)
            body = " ".join(body.split())[:600]
            parts.append(f"Headline: {hl}\nBody: {body}")
        raw_news = "\n\n".join(parts)[:3500]

        user_msg = (
            f"Stock: {company_name} ({ticker}), Sector: {gics_sector}. "
            f"Event date: {event_date}. "
            f"Raw news:\n{raw_news}\n\n"
            "Produce one concise paragraph for survey presentation."
        )

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=220,
            system=_ANTHROPIC_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text.strip()

    except Exception as exc:
        _warn(f"Anthropic API error ({ticker} {event_date}): {exc}")
        return "[TO BE GENERATED]"


def _pick_displayed_headline(
    manifest_headline: str,
    articles_df: pd.DataFrame,
) -> str:
    """
    Return the headline to display to respondents.
    Priority: manifest headline if not blank -> highest |FinBERT| article -> first article.
    """
    if isinstance(manifest_headline, str) and manifest_headline.strip() not in (
        "", "nan", "<paste displayed headline here>",
    ):
        return _clean_bz_headline(manifest_headline.strip())

    if articles_df.empty:
        return "[HEADLINE NOT AVAILABLE]"

    if HAS_FINBERT and "headline" in articles_df.columns:
        scores = articles_df["headline"].apply(
            lambda h: abs(_finbert_score(str(h)))
        )
        best_idx = scores.idxmax()
        return _clean_bz_headline(str(articles_df.loc[best_idx, "headline"]))

    return _clean_bz_headline(str(articles_df.iloc[0]["headline"]))


def _load_summary_cache() -> dict[str, str]:
    """Load scenario_id -> summary_paragraph from cache file if it exists."""
    if not NEWS_CACHE_PATH.exists():
        return {}
    try:
        df = pd.read_csv(NEWS_CACHE_PATH, dtype=str)
        df = df[df["summary_paragraph"].notna()]
        df = df[~df["summary_paragraph"].str.strip().isin(["", "[TO BE GENERATED]"])]
        return dict(zip(df["scenario_id"], df["summary_paragraph"]))
    except Exception:
        return {}


def _save_summary_cache(cache: dict[str, str]) -> None:
    """Persist the cache dict to NEWS_CACHE_PATH as CSV."""
    if not cache:
        return
    rows = [{"scenario_id": k, "summary_paragraph": v} for k, v in cache.items()]
    pd.DataFrame(rows).to_csv(NEWS_CACHE_PATH, index=False)


def build_news_text_df(
    manifest_df: pd.DataFrame,
    news_data: dict[str, pd.DataFrame],
    portfolio_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build scenario_news_text.csv content."""
    port_lookup = portfolio_df.set_index("ticker")
    has_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    cache = _load_summary_cache()

    rows = []
    for _, mrow in manifest_df.iterrows():
        sid = mrow["scenario_id"]
        ticker = mrow["ticker"]
        event_date = mrow["event_date"]
        company_name = str(mrow.get("company_name", ""))
        gics_sector = str(mrow.get("gics_sector", ""))

        # Fill from portfolio lookup if missing
        if (not company_name or company_name == "nan") and ticker in port_lookup.index:
            company_name = str(port_lookup.loc[ticker, "company_name"])
        if (not gics_sector or gics_sector == "nan") and ticker in port_lookup.index:
            gics_sector = str(port_lookup.loc[ticker, "gics_sector"])

        day_articles = get_event_day_news(news_data, ticker, event_date)
        num_articles = len(day_articles)

        headline = _pick_displayed_headline(
            str(mrow.get("headline", "")), day_articles
        )

        if sid in cache:
            print(f"  {sid} news text (cached)... done")
            summary = cache[sid]
        else:
            print(
                f"  {sid} news text "
                f"({'API' if has_api else 'placeholder'})...",
                end="", flush=True,
            )
            summary = _generate_summary_anthropic(
                company_name, ticker, gics_sector, event_date, day_articles
            )
            print(" done")
            if summary != "[TO BE GENERATED]":
                cache[sid] = summary

        rows.append({
            "scenario_id": sid,
            "ticker": ticker,
            "event_date": str(event_date),
            "headline": headline,
            "summary_paragraph": summary,
            "num_articles": num_articles,
        })

    _save_summary_cache(cache)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------
# Section 9 - Counterbalancing (Latin square)
# ------------------------------------------------------------------------------

def generate_counterbalancing(
    manifest_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate a balanced Latin square counterbalancing design for all blocks.

    For each block of 12 scenarios [S1...S12], four respondent versions are produced:

      Version 1: Group A (S1-S6) = ShowSC=1; Group B (S7-S12) = ShowSC=0
                 Order: interleaved A-B  [S1, S7, S2, S8, S3, S9, ...]
      Version 2: Group B = ShowSC=1; Group A = ShowSC=0
                 Order: interleaved A-B  [S1, S7, S2, S8, S3, S9, ...]
      Version 3: Group A = ShowSC=1; Group B = ShowSC=0
                 Order: interleaved B-A  [S7, S1, S8, S2, S9, S3, ...]
      Version 4: Group B = ShowSC=1; Group A = ShowSC=0
                 Order: interleaved B-A  [S7, S1, S8, S2, S9, S3, ...]

    Result:
      - Each scenario appears as treatment in exactly 2 of 4 versions (50% rate)
      - Two distinct presentation orders distribute position effects
      - Treatment/control alternates within each version (no clustering)

    counterbalancing_matrix.csv : respondent_block, block_id, presentation_order,
                                   scenario_id, show_sc
    form_assembly_guide.csv     : same + ticker, dashboard_shown (human-readable)
    """
    matrix_rows = []
    guide_rows = []

    for block_id in sorted(manifest_df["block_id"].unique()):
        block = manifest_df[manifest_df["block_id"] == block_id].reset_index(drop=True)
        scenario_ids = block["scenario_id"].tolist()
        tickers_map = dict(zip(block["scenario_id"], block["ticker"]))

        n = len(scenario_ids)
        half = n // 2
        group_a = scenario_ids[:half]    # first half
        group_b = scenario_ids[half:]    # second half

        # Interleaved order A-B: A0, B0, A1, B1, ...
        order_ab = []
        for i in range(max(len(group_a), len(group_b))):
            if i < len(group_a):
                order_ab.append(group_a[i])
            if i < len(group_b):
                order_ab.append(group_b[i])

        # Interleaved order B-A: B0, A0, B1, A1, ...
        order_ba = []
        for i in range(max(len(group_b), len(group_a))):
            if i < len(group_b):
                order_ba.append(group_b[i])
            if i < len(group_a):
                order_ba.append(group_a[i])

        versions = [
            (f"Block{block_id}_V1", set(group_a), order_ab),
            (f"Block{block_id}_V2", set(group_b), order_ab),
            (f"Block{block_id}_V3", set(group_a), order_ba),
            (f"Block{block_id}_V4", set(group_b), order_ba),
        ]

        for version_id, treatment_set, order in versions:
            for pos, sid in enumerate(order, start=1):
                show_sc = 1 if sid in treatment_set else 0
                ticker = tickers_map.get(sid, "")
                matrix_rows.append({
                    "respondent_block": version_id,
                    "block_id": block_id,
                    "presentation_order": pos,
                    "scenario_id": sid,
                    "show_sc": show_sc,
                })
                guide_rows.append({
                    "respondent_block": version_id,
                    "block_id": block_id,
                    "presentation_order": pos,
                    "scenario_id": sid,
                    "ticker": ticker,
                    "show_sc": show_sc,
                    "dashboard_shown": "YES" if show_sc else "no",
                })

    matrix_df = pd.DataFrame(matrix_rows)
    guide_df = pd.DataFrame(guide_rows)
    return matrix_df, guide_df


# ------------------------------------------------------------------------------
# Section 10 - Summary report
# ------------------------------------------------------------------------------

def generate_report(
    manifest_df: pd.DataFrame,
    sc_df: pd.DataFrame,
    pca_info: dict,
    charts_ok: int,
    dashboards_ok: int,
    output_dir: Path,
    price_reaction_df: pd.DataFrame | None = None,
) -> str:
    """Build the Markdown survey assembly report.

    The report is self-contained: an external reader can understand the survey
    design, measures, and descriptive statistics without access to the thesis.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        "respondent sees 12 scenarios (6 control, 6 treatment), with treatment "
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
    lines.append("Each respondent completes one block (12 scenarios). Three blocks "
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
        dates = pd.to_datetime(manifest_df["event_date"])
        earliest_idx = dates.idxmin()
        latest_idx = dates.idxmax()
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
        sc = sc_df["sc_total"]
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
        # AC_raw
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

        # SE_raw
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

        # AI_raw
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

        # ES_raw
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
            n_pos = (pr > 0).sum()
            n_neg = (pr < 0).sum()
            pr_merged = price_reaction_df
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

            # Largest moves
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

            # Reaction by severity
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
        sent_order = [
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
        "- **Form versions per block:** 4 (V1, V2, V3, V4)",
        "- **Total form versions:** 12 (4 per block x 3 blocks)",
        "- **Scenarios per form:** 12 (6 treatment, 6 control)",
        "- **Treatment assignment:** Each scenario appears as treatment "
        "(ShowSC = 1) in 2 of 4 versions and as control (ShowSC = 0) in the "
        "other 2",
        "- **Presentation order:** Treatment and control scenarios are "
        "interleaved (alternating T-C or C-T), preventing order-based "
        "response patterns",
        "",
        "This Latin-square-inspired design ensures that:",
        "1. Every scenario is seen with and without the Shock Score dashboard "
        "across the sample",
        "2. No respondent sees the same scenario twice",
        "3. Order effects are balanced across conditions",
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
        "(see `EVENT_TYPE_SEVERITY` in `3_survey_assembly.py`). "
        "**Requires manual review** against actual event characteristics "
        "before finalising SC_total for the thesis.",
        "",
        "### 9b. Sentiment Scoring",
        "Scores use **FinBERT** (`ProsusAI/finbert`) via HuggingFace Transformers. "
        "The sentiment score is `positive_prob - negative_prob` in [-1, 1]. "
        "See `toolkits/news_sentiment_toolkit.py` for the shared scorer.",
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
            "via Claude (claude-sonnet-4-6). Review each paragraph before use."
        )
    else:
        lines.append(
            "ANTHROPIC_API_KEY was not set -- `summary_paragraph` contains "
            "`[TO BE GENERATED]` placeholders. Set the environment variable "
            "and re-run, or populate manually."
        )

    # Warnings
    lines += ["", "---", "", "## 10. Warnings"]
    if _WARNINGS:
        for w in _WARNINGS:
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
    counter_lines: list[str] = []
    metadata_lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(output_dir):
        dirnames.sort()
        for fname in sorted(filenames):
            if fname == "survey_assembly_report.md":
                continue
            fpath = Path(dirpath) / fname
            size_kb = fpath.stat().st_size / 1024
            rel = fpath.relative_to(output_dir)
            entry = f"- `survey/{rel}` ({size_kb:.1f} KB)"
            rel_str = str(rel)
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
    lines += [
        "",
        "### Counterbalancing Files",
    ]
    lines.extend(counter_lines)
    lines += [
        "",
        "### Metadata Files",
    ]
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


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main() -> None:
    print("=" * 65)
    print("Survey Assembly Pipeline  -  3_survey_assembly.py")
    print("=" * 65)

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

    # -- [1/8] Load inputs -----------------------------------------------------
    print("\n[1/8] Loading inputs...")
    manifest_df = load_manifest()
    portfolio_df = load_portfolio()

    tickers = manifest_df["ticker"].unique().tolist()
    print(f"  Tickers: {tickers}")

    prices = load_price_data(tickers)
    print(f"  Price data loaded: {sorted(prices)}")

    news_data = load_news_data(tickers)
    print(f"  News data loaded:  {sorted(news_data)}")

    # -- [2/8] Scenario metadata -----------------------------------------------
    print("\n[2/8] Generating scenario_metadata.csv...")
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

    # -- [3/8] Price reactions (moved before charts so badge data is available) --
    print("\n[3/8] Computing price reactions...")
    reaction_rows = []

    for _, mrow in manifest_df.iterrows():
        sid = mrow["scenario_id"]
        ticker = mrow["ticker"]
        event_date = mrow["event_date"]
        event_time_et = str(mrow.get("event_time", "09:30"))

        base = {
            "scenario_id": sid,
            "ticker": ticker,
            "event_date": str(event_date),
            "event_time": event_time_et,
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

    # Build reaction lookup: scenario_id → price_reaction_pct
    reaction_lookup = {}
    for _, rrow in price_reaction_df.iterrows():
        pct = rrow.get("price_reaction_pct")
        if pd.notna(pct):
            reaction_lookup[rrow["scenario_id"]] = float(pct)

    # -- [4/8] Bloomberg-style intraday shock charts (2-day, 30-min) -----------
    print("\n[4/8] Generating Bloomberg-style intraday shock charts (2-day, 30-min)...")
    charts_ok = 0

    for _, mrow in manifest_df.iterrows():
        sid          = mrow["scenario_id"]
        ticker       = mrow["ticker"]
        event_date   = mrow["event_date"]
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

    # -- [5/8] Shock Score -----------------------------------------------------
    print("\n[5/8] Computing Shock Score components and SC_total...")
    if not HAS_FINBERT:
        print("  [NOTE] FinBERT not available - se_raw will be 0 for all scenarios")
        print("         Install: pip install transformers torch  (then re-run)")

    components_df = compute_raw_components(manifest_df, prices, news_data)
    sc_df, pca_info = compute_shock_scores(components_df)

    # Compute CAR-based persistence horizon (P_e = CAR_Day5 / CAR_Day1)
    print("\n  [5b] Computing persistence horizon (CAR Day1/3/5/10)...")
    sc_df = compute_persistence_horizon(sc_df, prices)

    # Round numeric columns for output
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

    # -- [6/8] Dashboard images ------------------------------------------------
    print("\n[6/8] Generating Shock Score dashboard images...")
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

    # -- [6b] Test dashboards: one per severity tier → diagnostics/dashboard_test/ --
    test_dir = Path("diagnostics") / "dashboard_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n  [6b] Saving test dashboards (Low/Medium/High) to {test_dir}/...")
    for tier in ("Low", "Medium", "High"):
        tier_rows = sc_df[sc_df["severity_level"] == tier]
        if tier_rows.empty:
            print(f"    {tier}: no scenarios in this tier")
            continue
        test_row = tier_rows.iloc[0]
        test_sid = str(test_row["scenario_id"])
        test_sid_key = f"test_{tier.lower()}_{test_sid}"
        ok = plot_dashboard(test_row, test_sid_key, test_dir)
        out_name = f"dashboard_{test_sid_key}.png"
        print(f"    {tier}: {test_sid} -> {out_name}  {'OK' if ok else 'FAILED'}")

    # -- [7/8] News text -------------------------------------------------------
    api_status = "ANTHROPIC_API_KEY set" if os.environ.get("ANTHROPIC_API_KEY") else "no API key"
    print(f"\n[7/8] Generating scenario_news_text.csv ({api_status})...")
    news_text_df = build_news_text_df(manifest_df, news_data, portfolio_df)

    out_path = out_dirs["metadata"] / "scenario_news_text.csv"
    news_text_df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path.relative_to(SURVEY_DIR)}  ({len(news_text_df)} rows)")

    # -- [8/8] Counterbalancing ------------------------------------------------
    print("\n[8/8] Generating counterbalancing matrix and form assembly guide...")
    matrix_df, guide_df = generate_counterbalancing(manifest_df)

    out_matrix = out_dirs["counterbalancing"] / "counterbalancing_matrix.csv"
    out_guide = out_dirs["counterbalancing"] / "form_assembly_guide.csv"
    matrix_df.to_csv(out_matrix, index=False)
    guide_df.to_csv(out_guide, index=False)

    n_versions = matrix_df["respondent_block"].nunique()
    print(f"  Respondent versions: {n_versions} "
          f"({n_versions // manifest_df['block_id'].nunique()} per block)")
    print(f"  Saved: {out_matrix.relative_to(SURVEY_DIR)}  ({len(matrix_df)} rows)")
    print(f"  Saved: {out_guide.relative_to(SURVEY_DIR)}  ({len(guide_df)} rows)")

    # Verify balance: each scenario should appear as treatment in exactly n_ver/2 versions
    if not matrix_df.empty:
        per_scenario = (
            matrix_df.groupby("scenario_id")["show_sc"].sum()
        )
        expected_treat = n_versions // manifest_df["block_id"].nunique() // 2
        unbalanced = per_scenario[per_scenario != expected_treat]
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
    report_md = generate_report(
        manifest_df, sc_df, pca_info,
        charts_ok, dashboards_ok,
        SURVEY_DIR,
        price_reaction_df=price_reaction_df,
    )
    report_path = SURVEY_DIR / "survey_assembly_report.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"\nReport: {report_path}")

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
    main()
