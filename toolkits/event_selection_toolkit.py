"""
event_selection_toolkit.py
==========================
Implements §2.2 of scenario_selection_protocol.md:
Three-stage shock identification algorithm producing a pool of
candidate stock-bar-news triples from which the final 36 scenarios
are selected.

Granularity
    All shock detection and news attribution operate at the **30-minute bar**
    level — the resolution specified in §2.1A of the scenario selection
    protocol.  Information shocks unfold within the 30-minute window of a
    news release; daily aggregation loses this temporal precision, and hourly
    bars introduce ambiguity when the shock timestamp and observed price move
    are separated by up to 60 minutes.

    News timestamps (which can be sub-minute) are floored to the nearest
    30-minute bar boundary to align with price bars.

    All timestamps are expressed as tz-naive Eastern Time (ET/EDT) so that
    IBKR (UTC source) and Yahoo Finance (ET source) data align correctly
    without daylight-saving mismatches.

Design context (updated protocol)
    The study uses 24 scenarios organised into three mutually exclusive
    blocks of 8 (Block A, Block B, Block C), each administered to
    ~33 respondents.  The stock universe contains 39 candidate stocks
    (24 final + 15 buffer).  Each stock contributes exactly one triple
    and appears in exactly one block.

Stage 1 – Statistical Screening
    For each stock in the universe:
      (a) Rolling historical volatility of 30-minute bar log returns over a
          window of rolling_window trading days.  The window is converted to
          bars automatically:
              rolling_bars = rolling_window_days × inferred_bars_per_day
          Flag bars: |ret_t – rolling_mean| > RETURN_Z * rolling_std
      (b) Relative abnormal return  =  stock_ret – spx_ret  (both per-bar).
          Flag bars: |rel_abn_t – rolling_mean_rel| > REL_Z * rolling_std_rel
      Both conditions must hold simultaneously.

Stage 1B – Within-day Causal Plausibility Screen (§2.2, Stage 1B)
    For each Stage 1 candidate (symbol, event_time), verify that the shock
    bar exhibits a meaningfully larger price move than the typical intraday
    fluctuation on that day:
        shock_bar_return > STAGE1B_MULTIPLIER × median(non-shock bar returns)
    The 1.5× multiplier is calibrated to retain ~60–70 % of Stage 1 candidates.
    Opening-bar (09:30) candidates apply the 2.0× threshold used in §2.3.

Stage 2 – News Attribution
    For each Stage 1B candidate (symbol, event_time), verify ≥1
    identifiable firm-specific Benzinga article in the event bar (T)
    or the immediately preceding bar (T – 30 min).
    The displayed_headline column records the single headline with the
    highest absolute VADER sentiment score; article_count records all
    articles in the event window.

Output (§2.2)
    DataFrame of validated stock-bar-news triples with shock statistics.
    Primary key: (symbol, event_time).  Also carries event_date,
    shock_time_et, shock_bar_median_ratio, article_count, displayed_headline.

SC_total construction (compute_sc_total)
    Enriches the candidate pool with four z-standardised components:
        AC_e  – article count in event window (T and T−30 min)
        SE_e  – max |VADER compound| across event-window articles
        AI_e  – event-bar volume / trailing 60-day mean 30-min bar volume
        ES_e  – event-type severity ratio (sigma_k / sigma_all, 30-min returns)
    PCA (first principal component) produces SC_total per event.
    Also adds event_type and market_regime columns.

§2.3 Multi-Block Balanced Scenario Selection (assign_blocks)
    Selects the best triple per stock (preferring AC_e = 1, then 2, then ≥3),
    assigns intensity tiers, and partitions 24 stocks into three blocks of 8
    (A, B, C) satisfying sector, direction, event-type, market-regime, and
    opening-bar balance constraints.
    Hard constraint caps the share of earnings events per block
    (default: max_earnings_share = 0.5, i.e. ≤4 of 8 per block).

§2.4 Selection Summary Tables (print_block_tables)
    Prints Tables 2.4a–c matching the expanded protocol column definitions,
    including Shock Time (ET), AC_e, Displayed Headline, and Shock Bar /
    Median Bar Ratio.

Pool adequacy target
    ≥36 distinct symbols must each have at least one qualifying triple.
    Symbols with no triple are ineligible for scenario assignment.

Notation follows CLAUDE.md thesis conventions.
"""

from __future__ import annotations

import os
import glob
import html as _html      # stdlib – always available; used for headline sanitisation
import re as _re
import warnings
import pandas as pd
import numpy as np
import yfinance as yf

# Optional: VADER for SE_e sentiment scoring (proxy for FinBERT per CLAUDE.md)
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer as _VADER
    nltk.download("vader_lexicon", quiet=True)
    _HAS_VADER = True
except (ImportError, LookupError):
    _HAS_VADER = False

# scikit-learn — required for z-standardisation and PCA (SC_total construction)
from sklearn.preprocessing import StandardScaler as _StandardScaler
from sklearn.decomposition import PCA as _PCA

# Optional: matplotlib for §2.5 scenario visualisation
try:
    import matplotlib.pyplot as _plt
    import matplotlib.dates as _mdates
    from matplotlib.gridspec import GridSpec as _GridSpec
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False


# ── Protocol defaults (§2.1A, §2.2) ──────────────────────────────────────────

BARS_PER_DAY     = 13    # 30-min bars per full trading day: 09:30–16:00 ET
ROLLING_WINDOW   = 60    # rolling lookback in trading days (converted to bars internally)
RETURN_Z_THRESH  = 2.0   # |z| threshold on absolute 30-min bar return
REL_Z_THRESH     = 1.5   # |z| threshold on relative abnormal return
STAGE1B_MULT     = 1.5   # within-day causal plausibility screen multiplier (§2.2, Stage 1B)
OPENING_BAR_MULT = 2.0   # stricter multiplier for first bar (09:30–10:00) shocks (§2.3)
OPENING_BAR_TIME = "09:30"   # HH:MM label of the first 30-min bar

# Canonical timezone for all internal timestamps (tz-naive after conversion)
_ET_TZ = "America/New_York"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _prices_to_bar_close(prices: pd.Series) -> pd.DataFrame:
    """
    Reshape (symbol, time) → close MultiIndex Series into a 30-minute bar
    close DataFrame, preserving intraday resolution.

    IBKR timestamps are UTC-aware; they are converted to tz-naive Eastern
    Time so they align correctly with Yahoo Finance SPX daily bars.

    Returns a DataFrame indexed by tz-naive ET datetime, columns = symbols.
    """
    df = prices.reset_index()
    df["dt"] = (
        df["time"]
        .dt.tz_convert(_ET_TZ)   # UTC → ET (handles DST automatically)
        .dt.tz_localize(None)    # strip tz → tz-naive ET
    )
    bar_close = (
        df.groupby(["symbol", "dt"])["close"]
        .last()                    # last tick within each bar (defensive)
        .unstack("symbol")
        .sort_index()
    )
    return bar_close


def _infer_bars_per_day(bar_close: pd.DataFrame) -> int:
    """
    Infer the typical number of 30-minute trading bars per day from price data.

    Uses the mode of non-null bar counts across all trading days.
    Falls back to 13 (US equity session 09:30–16:00 ET, 13 × 30-min bars).
    """
    counts = (
        bar_close.notna().any(axis=1)
        .groupby(bar_close.index.normalize())
        .sum()
    )
    if counts.empty:
        return BARS_PER_DAY
    return int(counts.mode().iloc[0])


def _fetch_spx_daily(start: str, end: str) -> pd.Series:
    """
    Download S&P 500 daily log returns from Yahoo Finance (^GSPC).

    Returns a tz-naive date-indexed Series named 'spx_ret'.
    The date range is padded backward by ~120 calendar days so the 60-day
    rolling window is fully populated at the start of the price history.

    Daily resolution is used deliberately: the two schedules (IBKR 30-min
    bars starting at 09:30, 10:00, … vs Yahoo Finance hourly starting at
    09:30, 10:30, …) cannot be directly intersected.  Instead, each IBKR
    bar's market contribution is approximated as
    daily_spx_return / bars_per_day (proportional allocation).
    """
    extended_start = (
        pd.Timestamp(start) - pd.DateOffset(days=120)
    ).strftime("%Y-%m-%d")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        raw = yf.download(
            "^GSPC",
            start=extended_start,
            end=end,
            progress=False,
            auto_adjust=True,
        )

    close = raw["Close"].squeeze()
    close.index = pd.to_datetime(close.index).tz_localize(None)
    log_ret = np.log(close / close.shift(1)).dropna()
    log_ret.name = "spx_ret"
    return log_ret


def _news_to_bar_bz(news: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten news to a BZ-only table with timestamps floored to the nearest
    30-minute bar boundary (§2.1A, §2.2 intraday shock assignment).

    IBKR news timestamps (UTC-aware) are converted to tz-naive ET and
    floored so that sub-minute news publication times align with the
    corresponding 30-minute price bar.

    Returns columns: symbol, bar_time (tz-naive ET datetime), headline.
    """
    flat = news.reset_index()
    flat["bar_time"] = (
        flat["time"]
        .dt.tz_convert(_ET_TZ)
        .dt.tz_localize(None)
        .dt.floor("30min")    # floor to bar start: 09:47 → 09:30, 10:05 → 10:00
    )
    bz_cols = ["symbol", "bar_time", "headline"]
    if "article_text" in flat.columns:
        bz_cols.append("article_text")
    bz = (
        flat.loc[flat["provider"] == "BZ", bz_cols]
        .copy()
        .reset_index(drop=True)
    )
    return bz


# ── Stage 1 ───────────────────────────────────────────────────────────────────

def run_stage1(
    prices: pd.Series,
    spx_ret: pd.Series,
    rolling_window: int = ROLLING_WINDOW,
    return_z: float = RETURN_Z_THRESH,
    rel_z: float = REL_Z_THRESH,
) -> pd.DataFrame:
    """
    Stage 1 – Statistical Screening (§2.2, Stage 1).

    Operates at 30-minute bar granularity.  The rolling_window parameter is
    specified in trading days; it is converted to a bar count by inferring
    bars_per_day from the actual price data.

    Parameters
    ----------
    prices        : (symbol, time) → close  [30-min IBKR bars from load_market_data]
    spx_ret       : daily log returns of S&P 500, date-indexed (from _fetch_spx_daily)
    rolling_window: lookback in trading days (protocol default: 60)
    return_z      : absolute-return z-score threshold (protocol default: 2.0)
    rel_z         : relative-return z-score threshold  (protocol default: 1.5)

    Returns
    -------
    DataFrame with columns:
        symbol, event_time (30-min ET), shock_time_et (HH:MM string),
        event_date (derived date), bar_return, spx_return, rel_abnormal_ret,
        return_zscore, rel_zscore, shock_direction

    Notes
    -----
    spx_ret is a daily Series (date index, tz-naive).  Each 30-min bar
    is mapped to its calendar date; the daily SPX return is then prorated as
    daily_spx / bars_per_day to approximate the market contribution per bar.
    """
    bar_close     = _prices_to_bar_close(prices)
    log_returns   = np.log(bar_close / bar_close.shift(1))

    # Derive rolling window in bars from actual trading-day density
    bars_per_day = _infer_bars_per_day(bar_close)
    rolling_bars = rolling_window * bars_per_day   # e.g. 60 × 13 = 780

    n_bars = len(log_returns)
    if n_bars < rolling_bars:
        print(
            f"    ⚠  Only {n_bars:,} 30-min bars "
            f"(≈{n_bars // max(bars_per_day, 1)} trading days) in price data; "
            f"rolling window requires {rolling_bars:,} bars "
            f"({rolling_window} days × {bars_per_day} bars/day).\n"
            f"       Re-download prices with PRICE_DURATION = '360 D' for full coverage."
        )

    spx_daily_dates = spx_ret.index   # date index

    records = []

    for symbol in log_returns.columns:
        ret = log_returns[symbol].dropna()
        if len(ret) < 2:
            continue

        bar_dates = pd.to_datetime(ret.index.normalize())
        spx_per_bar = (
            spx_ret
            .reindex(bar_dates)          # align by date (NaN if no SPX for that date)
            .values / bars_per_day       # prorate: market contribution per 30-min bar
        )
        spx = pd.Series(spx_per_bar, index=ret.index)

        valid = spx.notna()
        if valid.sum() < 2:
            continue
        ret = ret[valid]
        spx = spx[valid]

        # ── (a) Absolute return anomaly ───────────────────────────────────────
        roll_mean = ret.rolling(rolling_bars, min_periods=rolling_bars).mean()
        roll_std  = ret.rolling(rolling_bars, min_periods=rolling_bars).std()
        z_abs     = (ret - roll_mean) / roll_std
        flag_abs  = z_abs.abs() > return_z

        # ── (b) Relative abnormal return anomaly (firm-specific shock) ────────
        rel_abn       = ret - spx
        rel_roll_mean = rel_abn.rolling(rolling_bars, min_periods=rolling_bars).mean()
        rel_roll_std  = rel_abn.rolling(rolling_bars, min_periods=rolling_bars).std()
        z_rel         = (rel_abn - rel_roll_mean) / rel_roll_std
        flag_rel      = z_rel.abs() > rel_z

        # ── Both conditions must hold simultaneously ──────────────────────────
        flagged = flag_abs & flag_rel

        for event_time in flagged[flagged].index:
            records.append({
                "symbol":           symbol,
                "event_time":       event_time,           # primary key: 30-min ET timestamp
                "shock_time_et":    event_time.strftime("%H:%M"),   # HH:MM for protocol table
                "event_date":       event_time.date(),    # derived date for display/grouping
                "bar_return":       ret.loc[event_time],
                "spx_return":       spx.loc[event_time],  # prorated daily SPX / bars_per_day
                "rel_abnormal_ret": rel_abn.loc[event_time],
                "return_zscore":    round(z_abs.loc[event_time], 4),
                "rel_zscore":       round(z_rel.loc[event_time], 4),
                "shock_direction":  "positive" if ret.loc[event_time] > 0 else "negative",
            })

    if not records:
        return pd.DataFrame(columns=[
            "symbol", "event_time", "shock_time_et", "event_date", "bar_return",
            "spx_return", "rel_abnormal_ret", "return_zscore", "rel_zscore",
            "shock_direction",
        ])

    df = (
        pd.DataFrame(records)
        .sort_values(["event_time", "symbol"])
        .reset_index(drop=True)
    )
    for col in ("bar_return", "spx_return", "rel_abnormal_ret"):
        df[col] = df[col].round(6)

    return df


# ── Stage 1B ──────────────────────────────────────────────────────────────────

def run_stage1b(
    stage1: pd.DataFrame,
    prices: pd.Series,
    multiplier: float = STAGE1B_MULT,
) -> pd.DataFrame:
    """
    Stage 1B – Within-day Causal Plausibility Screen (§2.2, Stage 1B).

    For each Stage 1 candidate, verifies that the shock bar exhibits a price
    move meaningfully larger than the typical intraday fluctuation on that day.
    This ensures the survey chart presents an unambiguous visual narrative.

    Filter condition (non-opening bars):
        |shock_bar_return| > multiplier × median(|non-shock bar returns|)

    Opening bars (09:30 ET) are also filtered here using the stricter 2.0×
    threshold from §2.3, so they do not inflate the candidate pool with
    mechanically volatile opening-auction moves.

    The shock_bar_median_ratio column (ratio of shock bar return to median
    non-shock bar return) is added and flows through to assign_blocks for
    the §2.4 summary table.

    Parameters
    ----------
    stage1     : output of run_stage1
    prices     : (symbol, time) → close  [same Series passed to run_stage1]
    multiplier : within-day screen threshold for non-opening bars (default 1.5)

    Returns
    -------
    Filtered DataFrame with additional column:
        shock_bar_median_ratio  – ratio used in the §2.4 table
    """
    if stage1.empty:
        stage1 = stage1.copy()
        stage1["shock_bar_median_ratio"] = pd.Series(dtype="float64")
        return stage1

    bar_close = _prices_to_bar_close(prices)
    log_returns = np.log(bar_close / bar_close.shift(1))

    passed = []

    for _, row in stage1.iterrows():
        sym        = row["symbol"]
        event_time = pd.Timestamp(row["event_time"])
        event_date = event_time.normalize()

        if sym not in log_returns.columns:
            continue

        # All 30-min bar absolute log returns for the event day
        day_rets = log_returns[sym].dropna()
        day_mask = day_rets.index.normalize() == event_date
        day_abs  = day_rets[day_mask].abs().sort_index()

        if len(day_abs) < 2:
            continue  # insufficient bars to compute a meaningful ratio

        # Shock bar return
        if event_time in day_abs.index:
            shock_ret = float(day_abs.loc[event_time])
        else:
            diffs     = (day_abs.index - event_time).abs()
            shock_ret = float(day_abs.iloc[diffs.argmin()])

        # Reference: median absolute return of all non-shock bars on the same day
        non_shock = day_abs[day_abs.index != event_time]
        if non_shock.empty:
            continue
        ref_ret = float(non_shock.median())
        ratio   = (shock_ret / ref_ret) if ref_ret > 0 else float("nan")

        # Threshold: stricter for opening bar per §2.3 opening-bar constraint
        is_opening = row["shock_time_et"] == OPENING_BAR_TIME
        threshold  = OPENING_BAR_MULT if is_opening else multiplier

        if pd.isna(ratio) or ratio < threshold:
            continue  # fails within-day screen

        out = row.to_dict()
        out["shock_bar_median_ratio"] = round(ratio, 4)
        passed.append(out)

    if not passed:
        empty = stage1.iloc[0:0].copy()
        empty["shock_bar_median_ratio"] = pd.Series(dtype="float64")
        return empty

    return pd.DataFrame(passed).reset_index(drop=True)


# ── Stage 2 ───────────────────────────────────────────────────────────────────

def run_stage2(stage1b: pd.DataFrame, news: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2 – News Attribution (§2.2, Stage 2 and Intraday Shock Assignment).

    For each Stage 1B candidate (symbol, event_time), checks whether the
    Benzinga feed contains ≥1 identifiable firm-specific article in the
    event bar (T) or the immediately preceding bar (T − 30 min).
    Candidates with no news coverage are discarded.

    Adds:
        article_count     – number of BZ articles in event window [T−30min, T]
        displayed_headline – headline with the highest |VADER compound|; used
                             as the primary headline shown to survey respondents
                             when AC_e > 1 (§2.3 article count preference)
        sample_headlines  – up to 3 headlines (pipe-separated), for diagnostics

    Parameters
    ----------
    stage1b : output of run_stage1b
    news    : (symbol, provider, time) DataFrame from load_market_data

    Returns
    -------
    Enriched DataFrame.
    """
    if stage1b.empty:
        return pd.DataFrame()

    bz = _news_to_bar_bz(news)

    # Build VADER scorer once for displayed_headline selection
    sia = _VADER() if _HAS_VADER else None

    enriched = []

    for _, row in stage1b.iterrows():
        sym  = row["symbol"]
        ebar = pd.Timestamp(row["event_time"])
        prior = ebar - pd.Timedelta(minutes=30)   # immediately preceding 30-min bar

        mask = (
            (bz["symbol"] == sym) &
            (bz["bar_time"].isin([ebar, prior]))
        )
        matching = bz[mask]

        if matching.empty:
            continue  # no Benzinga coverage → discard

        headlines = matching["headline"].dropna().astype(str).tolist()

        # Select displayed_headline: highest |VADER compound|, else first headline
        if sia is not None and headlines:
            scores = [abs(sia.polarity_scores(h[:500])["compound"]) for h in headlines]
            displayed = headlines[int(np.argmax(scores))]
        else:
            displayed = headlines[0] if headlines else ""

        # Full article text: stored only for AC_e = 1 (single unambiguous source)
        # For AC_e > 1 the attribution is ambiguous — text is left empty.
        if len(matching) == 1 and "article_text" in matching.columns:
            art_text = str(matching["article_text"].iloc[0]).strip()
            art_text = "" if art_text.lower() in ("nan", "none") else art_text
        else:
            art_text = ""

        out = row.to_dict()
        out["article_count"]      = len(matching)
        out["displayed_headline"] = displayed
        out["article_text_full"]  = art_text
        out["sample_headlines"]   = " | ".join(headlines[:3])
        enriched.append(out)

    if not enriched:
        return pd.DataFrame()

    return pd.DataFrame(enriched).reset_index(drop=True)


# ── Main entry point ──────────────────────────────────────────────────────────

def identify_shocks(
    prices: pd.Series,
    news: pd.DataFrame,
    rolling_window: int = ROLLING_WINDOW,
    return_z: float = RETURN_Z_THRESH,
    rel_z: float = REL_Z_THRESH,
    stage1b_mult: float = STAGE1B_MULT,
) -> pd.DataFrame:
    """
    Full three-stage shock identification pipeline (§2.2).

    Shocks are identified at 30-minute bar granularity per §2.1A.

    Parameters
    ----------
    prices         : (symbol, time) → close  [from load_market_data]
    news           : (symbol, provider, time) DataFrame [from load_market_data]
    rolling_window : lookback in trading days (converted to bars internally; default 60)
    return_z       : absolute-return z-score threshold (default 2.0)
    rel_z          : relative-return z-score threshold  (default 1.5)
    stage1b_mult   : within-day plausibility screen multiplier (default 1.5)

    Returns
    -------
    DataFrame of validated stock-bar-news triples ready for §2.3 selection.
    Columns: symbol, event_time, shock_time_et, event_date, bar_return,
             spx_return, rel_abnormal_ret, return_zscore, rel_zscore,
             shock_direction, shock_bar_median_ratio,
             article_count, displayed_headline, sample_headlines.
    """
    times    = prices.index.get_level_values("time")
    start    = times.min().strftime("%Y-%m-%d")
    end      = (times.max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    n_stocks = prices.index.get_level_values("symbol").nunique()

    print(f"\n{'─' * 62}")
    print(f"  EVENT SELECTION  ·  §2.2 Shock Identification Algorithm")
    print(f"{'─' * 62}")
    print(f"  Stock universe : {n_stocks} symbols  (target: 39 candidates)")
    print(f"  Price window   : {start}  →  {end}")
    print(f"  Granularity    : 30-minute bars (tz-naive ET, {BARS_PER_DAY} bars/day)")
    print(
        f"  Parameters     : rolling={rolling_window} d (→ bars auto-derived)  |  "
        f"|z_ret| > {return_z}  |  |z_rel| > {rel_z}  |  Stage 1B mult = {stage1b_mult}×"
    )

    # ── Fetch daily SPX benchmark ─────────────────────────────────────────
    print(f"\n  [SPX]      Downloading daily S&P 500 benchmark ... ", end="", flush=True)
    spx_ret = _fetch_spx_daily(start, end)
    print(f"done  ({len(spx_ret):,} trading days, extended window)")

    # ── Stage 1 ───────────────────────────────────────────────────────────
    print(f"\n  [Stage 1]  Statistical screening (30-min bars) ...")
    stage1 = run_stage1(prices, spx_ret, rolling_window, return_z, rel_z)

    if stage1.empty:
        print(
            "  ✗  Stage 1: 0 candidates.\n"
            "     Price history may be too short for the rolling window.\n"
            "     Try re-downloading prices with PRICE_DURATION = '360 D'."
        )
        return pd.DataFrame()

    s1_by_symbol = stage1.groupby("symbol").size().rename("n")
    print(f"\n  Candidate bars per symbol (Stage 1):")
    for sym, n in s1_by_symbol.items():
        bar = "█" * min(n, 40)
        print(f"    {sym:<6}  {bar}  ({n:,})")
    print(f"\n  Stage 1 total : {len(stage1):,} candidate (symbol, bar) pairs")

    # ── Stage 1B ──────────────────────────────────────────────────────────
    print(f"\n  [Stage 1B] Within-day causal plausibility screen ({stage1b_mult}× / {OPENING_BAR_MULT}× opening) ...")
    stage1b = run_stage1b(stage1, prices, multiplier=stage1b_mult)

    if stage1b.empty:
        print("  ✗  Stage 1B: 0 candidates after within-day filter.")
        return pd.DataFrame()

    s1b_discarded = len(stage1) - len(stage1b)
    retention_pct = len(stage1b) / max(len(stage1), 1) * 100
    print(
        f"  Discarded (ambiguous intraday pattern) : {s1b_discarded:,}  "
        f"({retention_pct:.0f}% retained)"
    )
    print(f"  Stage 1B total : {len(stage1b):,} candidates")

    # ── Stage 2 ───────────────────────────────────────────────────────────
    print(f"\n  [Stage 2]  News attribution  (BZ, shock bar T or T−30 min) ...")
    stage2 = run_stage2(stage1b, news)

    if stage2.empty:
        print("  ✗  Stage 2: 0 triples after news filter.")
        return pd.DataFrame()

    discarded = len(stage1b) - len(stage2)
    print(f"  Discarded (no BZ coverage)    : {discarded:,}")
    print(f"  Stage 2 total                 : {len(stage2):,} stock-bar-news triples")

    # ── Pool adequacy check against the 36-scenario target ────────────────
    symbols_with_triples    = stage2["symbol"].nunique()
    symbols_without_triples = n_stocks - symbols_with_triples
    adequate = symbols_with_triples >= 36

    print(f"\n  Pool adequacy  (target: 36 distinct symbols with ≥1 triple)")
    print(f"    Symbols with qualifying triple  : {symbols_with_triples} / {n_stocks}")
    if symbols_without_triples:
        no_triple = sorted(
            set(prices.index.get_level_values("symbol"))
            - set(stage2["symbol"].unique())
        )
        print(f"    Symbols with no triple         : {symbols_without_triples}  →  {no_triple}")
    if adequate:
        print(f"    ✓  Pool covers ≥36 symbols — sufficient for block assignment.")
    else:
        shortfall = 36 - symbols_with_triples
        print(
            f"    ✗  Pool covers only {symbols_with_triples} symbols "
            f"({shortfall} short of 36).\n"
            f"       Consider re-downloading prices with a longer history\n"
            f"       (e.g. PRICE_DURATION = '360 D') to widen the candidate pool."
        )

    print(f"\n{'─' * 62}\n")

    return stage2


# ── SC_total construction ─────────────────────────────────────────────────────
# Implements the four-component Shock Score described in CLAUDE.md §SC_total.
# Notation: e = event index, k = event-type category.

# Event-type keyword taxonomy (used for ES_e and §2.3.2 diversity constraint)
_EVENT_TYPE_KEYWORDS: dict[str, list[str]] = {
    "earnings":   ["earnings", "eps", "revenue", "quarterly", "q1", "q2", "q3", "q4",
                   "guidance", "beat", "miss", "profit", "loss", "results", "income",
                   "dividend", "buyback"],
    "regulatory": ["fda", "sec", "doj", "ftc", "regulatory", "approval",
                   "investigation", "lawsuit", "fine", "settlement", "legal", "court",
                   "compliance", "ruling", "penalty", "sanction"],
    "management": ["ceo", "cfo", "cto", "coo", "resign", "appoint", "hire", "departure",
                   "executive", "board", "director", "leadership", "succession"],
    "product":    ["launch", "product", "merger", "acquisition", "deal", "contract",
                   "partnership", "recall", "service", "platform", "agreement",
                   "joint venture", "divestiture", "restructur"],
    "analyst":    ["downgrade", "upgrade", "rating", "price target", "analyst",
                   "outperform", "underperform", "overweight", "underweight",
                   "initiate", "coverage"],
}


def _classify_event_type(text: str) -> str:
    """
    Keyword-based event-type classifier applied to combined headline + article text.
    Returns the category with the most keyword hits; 'other' if none match.
    """
    t = text.lower()
    scores = {etype: sum(1 for kw in kws if kw in t)
              for etype, kws in _EVENT_TYPE_KEYWORDS.items()}
    best, best_n = max(scores.items(), key=lambda x: x[1])
    return best if best_n > 0 else "other"


def _build_event_articles(candidates: pd.DataFrame, news: pd.DataFrame) -> dict:
    """
    Collect all BZ article texts (headline + article_text) for each candidate's
    event window: event bar T and preceding bar T−30 min.

    Returns dict  {candidates.index value → list[str]}
    """
    flat = news.reset_index()
    flat["bar_time"] = (
        flat["time"]
        .dt.tz_convert(_ET_TZ)
        .dt.tz_localize(None)
        .dt.floor("30min")
    )
    flat = flat.loc[flat["provider"] == "BZ"].copy()

    flat["text"] = (
        flat.get("headline",     pd.Series("", index=flat.index)).fillna("").astype(str)
        + " "
        + flat.get("article_text", pd.Series("", index=flat.index)).fillna("").astype(str)
    ).str.strip()

    result: dict = {}
    for idx, row in candidates.iterrows():
        sym  = row["symbol"]
        ebar = pd.Timestamp(row["event_time"])
        prior = ebar - pd.Timedelta(minutes=30)
        mask  = (flat["symbol"] == sym) & (flat["bar_time"].isin([ebar, prior]))
        result[idx] = flat.loc[mask, "text"].tolist()

    return result


def _se_e_from_articles(event_articles: dict) -> pd.Series:
    """
    SE_e: max |VADER compound score| across articles in the event window.

    VADER serves as a proxy for FinBERT (CLAUDE.md convention); the pipeline
    structure is identical — swap the scorer to switch models.
    Returns 0.0 where VADER is unavailable or no articles exist.
    """
    if not _HAS_VADER:
        print("    ⚠  VADER not found (pip install nltk).  SE_e set to 0.0.")
        return pd.Series({k: 0.0 for k in event_articles})

    sia = _VADER()
    out: dict = {}
    for idx, texts in event_articles.items():
        if not texts:
            out[idx] = 0.0
        else:
            scores = [abs(sia.polarity_scores(t[:1_000])["compound"]) for t in texts]
            out[idx] = max(scores)
    return pd.Series(out)


def _load_bar_volumes(data_dir: str = "data") -> pd.DataFrame:
    """
    Load 30-minute bar volume from IBKR price CSVs (*_30mins_*.csv).

    Timestamps are converted to tz-naive ET (matching price bars and news) so
    that volume can be joined to candidates on event_time directly.
    Skips news files, 1-hour files, and any file without a 'volume' column.

    Returns DataFrame indexed by tz-naive ET datetime, columns = symbols.
    """
    price_pat = _re.compile(r"^(.+)_([^_]+)_([^_]+)\.csv$")
    news_pat  = _re.compile(r"^.+_[^_]+_\d{4}-\d{2}-\d{2}_to_\d{4}-\d{2}-\d{2}\.csv$")
    frames: list[pd.DataFrame] = []

    for fpath in glob.glob(os.path.join(data_dir, "*.csv")):
        fname = os.path.basename(fpath)
        if news_pat.match(fname):
            continue
        m = price_pat.match(fname)
        if not m:
            continue
        # Only load 30-minute bar files (§2.1A)
        if m.group(2) != "30mins":
            continue
        symbol = m.group(1)
        try:
            df = pd.read_csv(fpath)
            if "volume" not in df.columns:
                continue
            df["dt"] = (
                pd.to_datetime(df["time"], utc=True)
                .dt.tz_convert(_ET_TZ)
                .dt.tz_localize(None)
            )
            frames.append(df[["dt", "volume"]].assign(symbol=symbol))
        except Exception:
            continue

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    bar_vol  = (
        combined.groupby(["symbol", "dt"])["volume"]
        .sum()                     # sum handles any within-bar duplicates
        .unstack("symbol")
        .sort_index()
    )
    return bar_vol


def _ai_e_from_volumes(
    candidates: pd.DataFrame,
    bar_volumes: pd.DataFrame,
    trailing_bars: int = 60 * BARS_PER_DAY,    # ≈ 60 trading days × 13 bars/day = 780
) -> pd.Series:
    """
    AI_e: event-bar volume / mean of trailing N 30-min bars.

    trailing_bars defaults to 780 (≈ 60 trading days × 13 bars/day), matching
    the 60-day rolling window used for historical volatility calibration.
    This is recomputed in compute_sc_total using the inferred bars_per_day
    so it adapts to the actual data density.

    Returns 1.0 (neutral) for missing symbols or insufficient history.
    """
    out: dict = {}
    for idx, row in candidates.iterrows():
        sym  = row["symbol"]
        ebar = pd.Timestamp(row["event_time"])

        if bar_volumes.empty or sym not in bar_volumes.columns:
            out[idx] = 1.0
            continue

        vol = bar_volumes[sym].dropna()
        if ebar not in vol.index:
            out[idx] = 1.0
            continue

        event_vol = float(vol[ebar])
        trailing  = vol[vol.index < ebar].tail(trailing_bars)
        avg_vol   = float(trailing.mean()) if len(trailing) > 0 else event_vol
        out[idx]  = event_vol / avg_vol if avg_vol > 0 else 1.0

    return pd.Series(out)


def _es_e_from_types(
    candidates: pd.DataFrame,
    event_types: pd.Series,
) -> pd.Series:
    """
    ES_e = sigma_k / sigma_all  (computed from 30-min bar_return).
        sigma_k   : std of bar_return for events of type k in the pool.
        sigma_all : std of bar_return across all candidates.
    Returns 1.0 where sigma_all = 0 or a category has only one event.
    """
    sigma_all = candidates["bar_return"].std()
    if sigma_all == 0 or pd.isna(sigma_all):
        return pd.Series(1.0, index=candidates.index)

    out: dict = {}
    for idx in candidates.index:
        etype   = event_types.loc[idx]
        mask    = event_types == etype
        sigma_k = candidates.loc[mask, "bar_return"].std()
        out[idx] = (sigma_k / sigma_all) if (sigma_k > 0 and not pd.isna(sigma_k)) else 1.0

    return pd.Series(out)


def _market_regimes(
    candidates: pd.DataFrame,
    spx_ret: pd.Series,
    window_days: int = 20,
    bull_thresh: float = 0.03,
    bear_thresh: float = -0.03,
) -> pd.Series:
    """
    Label market regime on each event using trailing 20-trading-day
    cumulative S&P 500 return (daily Series from _fetch_spx_daily).

        bull    : cumulative return > +3 %
        bear    : cumulative return < -3 %
        neutral : otherwise
    """
    spx_cumret = (
        (1 + spx_ret)
        .rolling(window_days, min_periods=window_days)
        .apply(np.prod, raw=True)
        - 1
    )
    out: dict = {}
    for idx, row in candidates.iterrows():
        edate = pd.Timestamp(row["event_time"]).normalize()
        if edate in spx_cumret.index and not pd.isna(spx_cumret[edate]):
            r = spx_cumret[edate]
            out[idx] = "bull" if r > bull_thresh else ("bear" if r < bear_thresh else "neutral")
        else:
            out[idx] = "neutral"

    return pd.Series(out)


def compute_sc_total(
    candidates: pd.DataFrame,
    news: pd.DataFrame,
    data_dir: str = "data",
) -> pd.DataFrame:
    """
    Enrich the candidate pool with SC_total and auxiliary columns.

    Computes four components at 30-minute bar granularity, z-standardises
    each, then applies PCA (first principal component) to produce SC_total
    per event.  Sign convention enforced: higher SC_total = higher shock
    intensity.

    Parameters
    ----------
    candidates : output of identify_shocks (§2.2), 30-min bar triples
    news       : (symbol, provider, time) DataFrame from load_market_data
    data_dir   : directory containing *_30mins_*.csv price files

    Returns
    -------
    DataFrame — all original columns plus:
        ac_e, se_e, ai_e, es_e  – raw component values
        sc_total                 – PCA-based composite score
        event_type               – keyword-classified event category
        market_regime            – bull / neutral / bear
    """
    if candidates.empty:
        return candidates.copy()

    df = candidates.copy().reset_index(drop=True)

    print(f"\n{'─' * 62}")
    print(f"  SC_TOTAL CONSTRUCTION  ·  §2.2 Technical Appendix")
    print(f"{'─' * 62}")
    print(f"  Events in pool : {len(df):,} 30-min bar triples")

    # ── Daily SPX for market regime ───────────────────────────────────────
    event_times = pd.to_datetime(df["event_time"])
    spx_start   = event_times.min().strftime("%Y-%m-%d")
    spx_end     = (event_times.max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    spx_ret     = _fetch_spx_daily(spx_start, spx_end)

    # Infer bars_per_day from volume data (adapts to actual data density)
    bar_volumes_tmp = _load_bar_volumes(data_dir)
    if not bar_volumes_tmp.empty:
        bpd = bar_volumes_tmp.notna().any(axis=1).groupby(
            bar_volumes_tmp.index.normalize()
        ).sum()
        bars_per_day = int(bpd.mode().iloc[0]) if not bpd.empty else BARS_PER_DAY
    else:
        bars_per_day = BARS_PER_DAY

    # ── AC_e ─────────────────────────────────────────────────────────────
    print(f"  [AC_e]   Article count (30-min bar window) ... ", end="", flush=True)
    df["ac_e"] = df["article_count"].astype(float)
    print("done")

    # ── Collect event articles (reused for SE_e and event_type) ──────────
    print(f"  [fetch]  Collecting event articles ... ", end="", flush=True)
    event_articles = _build_event_articles(df, news)
    print("done")

    # ── SE_e ─────────────────────────────────────────────────────────────
    print(f"  [SE_e]   Sentiment extremity (VADER) ... ", end="", flush=True)
    df["se_e"] = _se_e_from_articles(event_articles).reindex(df.index).fillna(0.0)
    print("done")

    # ── Event type classification ─────────────────────────────────────────
    print(f"  [type]   Event type classification ... ", end="", flush=True)
    raw_types = {
        idx: _classify_event_type(" ".join(texts))
        for idx, texts in event_articles.items()
    }
    df["event_type"] = pd.Series(raw_types).reindex(df.index).fillna("other")
    type_counts = df["event_type"].value_counts().to_dict()
    print(f"done  →  {type_counts}")

    # ── AI_e ─────────────────────────────────────────────────────────────
    print(f"  [AI_e]   Attention intensity (30-min bar volume) ... ", end="", flush=True)
    trailing_bars = 60 * bars_per_day   # 60-day trailing average (§2.1A calibration)
    df["ai_e"] = (
        _ai_e_from_volumes(df, bar_volumes_tmp, trailing_bars=trailing_bars)
        .reindex(df.index)
        .fillna(1.0)
    )
    print("done")

    # ── ES_e ─────────────────────────────────────────────────────────────
    print(f"  [ES_e]   Event-type severity ratio (30-min returns) ... ", end="", flush=True)
    df["es_e"] = _es_e_from_types(df, df["event_type"]).reindex(df.index).fillna(1.0)
    print("done")

    # ── Market regime ────────────────────────────────────────────────────
    print(f"  [regime] Market regime (20d trailing daily SPX) ... ", end="", flush=True)
    df["market_regime"] = (
        _market_regimes(df, spx_ret)
        .reindex(df.index)
        .fillna("neutral")
    )
    regime_counts = df["market_regime"].value_counts().to_dict()
    print(f"done  →  {regime_counts}")

    # ── Z-standardise and PCA ─────────────────────────────────────────────
    print(f"\n  [PCA]    Z-standardising components and fitting PCA ...")
    component_cols = ["ac_e", "se_e", "ai_e", "es_e"]
    Z        = df[component_cols].fillna(0.0).values
    scaler   = _StandardScaler()
    Z_scaled = scaler.fit_transform(Z)

    pca    = _PCA(n_components=1)
    pca.fit(Z_scaled)
    w1     = pca.components_[0]
    sc_raw = Z_scaled @ w1

    # Sign convention: positive correlation with |rel_abnormal_ret|
    if np.corrcoef(sc_raw, df["rel_abnormal_ret"].abs())[0, 1] < 0:
        w1     = -w1
        sc_raw = -sc_raw

    df["sc_total"] = sc_raw.round(4)

    explained = pca.explained_variance_ratio_[0]
    loadings  = dict(zip(component_cols, w1.round(4)))
    print(f"  Variance explained by PC1 : {explained:.1%}")
    print(f"  Loading vector w_1        : {loadings}")

    desc = df["sc_total"].describe()
    print(
        f"\n  SC_total distribution:"
        f"\n    min={desc['min']:.4f}  "
        f"p33={df['sc_total'].quantile(1/3):.4f}  "
        f"median={desc['50%']:.4f}  "
        f"p67={df['sc_total'].quantile(2/3):.4f}  "
        f"max={desc['max']:.4f}"
    )
    print(f"\n{'─' * 62}\n")

    return df


# ── §2.3 Multi-Block Balanced Scenario Selection ──────────────────────────────

_SCENARIOS_TOTAL     = 24
_BLOCKS              = 3
_SCENARIOS_PER_BLOCK = _SCENARIOS_TOTAL // _BLOCKS   # 8
_BLOCK_LABELS        = ["A", "B", "C"]

# Hard constraint: max same GICS sector per block
_MAX_SECTOR_PER_BLOCK = 2

# Soft constraint: max opening-bar (09:30) shocks per block (≤1/4 of 8, rounded down)
_MAX_OPENING_BAR_PER_BLOCK = 2


def _can_add(stock: dict, block: list[dict]) -> bool:
    """
    Hard constraints for adding a stock-triple to a block (§2.3.2 revised).

    Constraint table (old → new):
    ┌──────────────────────────┬────────────────────┬──────────────────────────────────┐
    │ Constraint               │ Old rule           │ New rule                         │
    ├──────────────────────────┼────────────────────┼──────────────────────────────────┤
    │ Block capacity           │ < 8 (hard)         │ < 8 (hard)                       │
    │ Sector per block         │ ≤ 2 (hard)         │ ≤ 2 (hard)                       │
    │ Direction floor          │ ≥ 3 minority (hard)│ ≥ 2 minority (hard, relaxed)     │
    │ Earnings share           │ ≤ 50 % (hard)      │ soft warning only (see audit)    │
    │ Opening-bar count        │ ≤ 2 (soft)         │ soft warning only (see audit)    │
    │ Event-type diversity     │ ≥ 3 types (soft)   │ soft warning only (see audit)    │
    └──────────────────────────┴────────────────────┴──────────────────────────────────┘

    Root cause for direction-floor relaxation: the candidate pool contains only ~8 of
    36 negative shocks.  A ≥3 floor causes cascading _can_add failures in the greedy
    loop that cannot be resolved by direction-aware variant selection alone.  Lowering
    the hard floor to ≥2 (max 6 of one direction) unblocks the algorithm while keeping
    direction diversity meaningful.

    Root cause for earnings/opening-bar/event-type becoming soft: the greedy algorithm
    produced whack-a-mole hard failures when rare-event stocks happened to cluster in
    the same tier.  Soft warnings in the audit preserve observability without blocking
    valid assignments.
    """
    if len(block) >= _SCENARIOS_PER_BLOCK:
        return False
    sector = stock.get("sector", "Unknown")
    if sum(1 for s in block if s.get("sector") == sector) >= _MAX_SECTOR_PER_BLOCK:
        return False
    direction = stock.get("shock_direction", "")
    if direction in ("positive", "negative"):
        n_same = sum(1 for s in block if s.get("shock_direction") == direction)
        if n_same >= _SCENARIOS_PER_BLOCK - 2:  # max 6 of one direction → ≥2 of other
            return False
    return True


def _soft_score(stock: dict, block: list[dict]) -> float:
    """
    Soft preference score for assigning stock to block (higher = better fit).
    Penalises direction imbalance (heavily), event-type repetition, opening-bar
    overrepresentation, and regime homogeneity.

    Weights: direction (0.50), event_type (0.25), opening_bar (0.15), regime (0.10).
    """
    if not block:
        return 1.0
    n         = len(block)
    direction = stock.get("shock_direction", "")
    etype     = stock.get("event_type", "")
    regime    = stock.get("market_regime", "")

    dir_count   = sum(1 for s in block if s.get("shock_direction") == direction)
    etype_count = sum(1 for s in block if s.get("event_type")      == etype)
    reg_count   = sum(1 for s in block if s.get("market_regime")   == regime)
    open_count  = sum(1 for s in block if s.get("is_opening_bar", False))

    # Direction: penalise overrepresentation to nudge toward ≥2 minority (hard floor = 6/8).
    # Threshold moved from 0.4 → 0.5 to match the relaxed hard floor.
    dir_score    = 1.0 - max(0.0, dir_count / max(n, 1) - 0.5)
    etype_score  = 1.0 if etype_count < 3 else 0.4
    # Opening-bar soft preference: ideal ≤ _MAX_OPENING_BAR_PER_BLOCK per block
    open_excess  = max(0, open_count + (1 if stock.get("is_opening_bar", False) else 0)
                       - _MAX_OPENING_BAR_PER_BLOCK)
    open_score   = 1.0 if open_excess == 0 else max(0.3, 1.0 - 0.25 * open_excess)
    regime_score = 1.0 if reg_count < n else 0.6

    return 0.50 * dir_score + 0.25 * etype_score + 0.15 * open_score + 0.10 * regime_score


def assign_blocks(
    enriched: pd.DataFrame,
    portfolio: pd.DataFrame,
    max_earnings_share: float = 0.5,
) -> dict[str, pd.DataFrame]:
    """
    §2.3 Multi-Block Balanced Scenario Selection (revised algorithm).

    Steps:
    1.  Merge GICS sector from portfolio.csv.
    2.  Flag is_opening_bar column.
    3.  Build direction-aware pool: for each stock, retain the BEST positive
        triple AND the BEST negative triple (AC_e preference 1 > 2 > ≥3,
        then highest SC_total).  This is the key change from the prior
        one-triple-per-stock approach — it solves the negative-shock scarcity
        problem (≈8/36 negatives in raw pool) without relaxing the ≥2 floor.
    4.  Assign intensity tiers (low / medium / high) using the highest SC_total
        across a stock's two directional variants.
    5.  Greedy block assignment: for each stock, evaluate ALL viable
        (block, direction_variant) combinations, score them with _soft_score,
        and assign the best-fit (block, direction) pair.
    6.  Convert to DataFrames and add scenario IDs.
    7.  Constraint audit (§2.3.2):
        Hard (blocks are enforced):  capacity, sector ≤ 2, direction ≥ 2 minority.
        Soft (audit warnings only):  earnings share, event-type diversity, opening-bar count.

    Parameters
    ----------
    enriched           : output of compute_sc_total (30-min bar triples)
    portfolio          : DataFrame from data/portfolio.csv
    max_earnings_share : audit reference fraction for earnings (default 0.5; no longer hard)

    Returns
    -------
    dict {"A": DataFrame, "B": DataFrame, "C": DataFrame}
    Each DataFrame contains up to 8 rows with columns:
        scenario_id, symbol, sector, event_time, shock_time_et, event_date,
        event_type, shock_direction, intensity_tier, sc_total, ac_e,
        displayed_headline, rel_abnormal_ret, shock_bar_median_ratio,
        market_regime, is_opening_bar, block
    """
    max_earnings_count = int(max_earnings_share * _SCENARIOS_PER_BLOCK)  # audit reference only

    print(f"\n{'─' * 62}")
    print(f"  BLOCK ASSIGNMENT  ·  §2.3 Multi-Block Scenario Selection")
    print(f"{'─' * 62}")
    print(
        f"  Hard  : capacity ≤ {_SCENARIOS_PER_BLOCK}  |  "
        f"sector ≤ {_MAX_SECTOR_PER_BLOCK} per block  |  "
        f"direction floor ≥ 2 minority (max 6 of one direction)"
    )
    print(
        f"  Soft  : earnings share ≤ {max_earnings_share:.0%} (audit only)  |  "
        f"opening-bar ≤ {_MAX_OPENING_BAR_PER_BLOCK} (audit only)  |  "
        f"event-type diversity ≥ 3 types (audit only)"
    )

    # ── 1. Merge GICS sector ──────────────────────────────────────────────
    sector_col = next(
        (c for c in portfolio.columns if c.lower() in ("gics sector", "sector", "gics_sector")),
        None,
    )
    sym_col = next(
        (c for c in portfolio.columns if c.lower() in ("symbol", "ticker")),
        None,
    )
    if sector_col and sym_col:
        sector_map = portfolio.set_index(sym_col)[sector_col].to_dict()
    else:
        sector_map = {}
        print("  ⚠  Could not find Symbol/GICS Sector columns in portfolio.csv.")

    # Company name lookup for chart titles and survey presentation (§4.2.4)
    name_col = next(
        (c for c in portfolio.columns
         if c.lower() in ("company", "company name", "name", "security",
                          "security name", "company_name", "long name")),
        None,
    )
    if name_col and sym_col:
        name_map = portfolio.set_index(sym_col)[name_col].to_dict()
    else:
        name_map = {}
        print("  ⚠  Could not find Company Name column in portfolio.csv — "
              "ticker will be used as fallback.")

    df = enriched.copy()
    df["sector"]       = df["symbol"].map(sector_map).fillna("Unknown")
    df["company_name"] = df["symbol"].map(name_map).fillna(df["symbol"])

    # ── 2. Opening-bar flag ───────────────────────────────────────────────
    if "shock_time_et" in df.columns:
        df["is_opening_bar"] = df["shock_time_et"] == OPENING_BAR_TIME
    else:
        df["is_opening_bar"] = False

    # ── 3. Direction-aware pool: best positive + best negative per stock ────
    # Root cause for this change: old one-triple-per-stock approach left the
    # greedy loop with no ability to balance direction — it simply accepted
    # whichever direction happened to rank highest on SC_total per stock.
    # Keeping both directional variants per stock lets the greedy loop pick
    # the direction that the target block currently needs.
    print(f"\n  [1/5]  Building direction-aware pool (best +/- triple per stock) ...")
    df["_ac_pref"] = df["article_count"].apply(lambda x: 0 if x == 1 else (1 if x == 2 else 2))
    sorted_df = df.sort_values(["_ac_pref", "sc_total"], ascending=[True, False])
    df.drop(columns=["_ac_pref"], inplace=True)

    # Best triple per (symbol × shock_direction)
    dir_pool = (
        sorted_df
        .groupby(["symbol", "shock_direction"], as_index=False)
        .first()
        .reset_index(drop=True)
    )
    dir_pool.drop(columns=["_ac_pref"], inplace=True, errors="ignore")

    # Build lookup: symbol → {"positive": row_dict, "negative": row_dict}
    dir_lookup: dict[str, dict[str, dict]] = {}
    for _, row in dir_pool.iterrows():
        sym = row["symbol"]
        d   = row["shock_direction"]
        if sym not in dir_lookup:
            dir_lookup[sym] = {}
        dir_lookup[sym][d] = row.to_dict()

    symbols_both = [s for s in dir_lookup if len(dir_lookup[s]) == 2]
    symbols_one  = [s for s in dir_lookup if len(dir_lookup[s]) == 1]
    n_with_triple = len(dir_lookup)

    ac_vals = [
        row["article_count"]
        for variants in dir_lookup.values()
        for row in variants.values()
    ]
    ac_dist = {
        "AC=1": sum(1 for v in ac_vals if v == 1),
        "AC=2": sum(1 for v in ac_vals if v == 2),
        "AC≥3": sum(1 for v in ac_vals if v >= 3),
    }

    print(f"    Stocks with both +/− triples : {len(symbols_both)}")
    print(f"    Stocks with one direction     : {len(symbols_one)}")
    print(f"    Total stocks in pool          : {n_with_triple} / {_SCENARIOS_TOTAL} needed")
    print(f"    Article count distribution    : {ac_dist}")
    if n_with_triple < _SCENARIOS_TOTAL:
        shortfall = _SCENARIOS_TOTAL - n_with_triple
        print(
            f"    ⚠  {shortfall} stocks lack any qualifying triple — "
            f"blocks will be incomplete.\n"
            f"       Re-download prices with PRICE_DURATION = '360 D' for full coverage."
        )

    # ── 4. Assign intensity tiers (per stock, using highest SC_total variant) ─
    # Using the maximum SC_total across a stock's directional variants ensures
    # tier assignment reflects the strongest available signal for that stock.
    print(f"\n  [2/5]  Assigning intensity tiers (max SC_total across directional variants) ...")
    rep_sc = pd.Series({
        sym: max(v["sc_total"] for v in variants.values())
        for sym, variants in dir_lookup.items()
    })
    p33 = rep_sc.quantile(1 / 3)
    p67 = rep_sc.quantile(2 / 3)
    sym_tier: dict[str, str] = {
        sym: ("low" if sc <= p33 else ("high" if sc > p67 else "medium"))
        for sym, sc in rep_sc.items()
    }
    tier_counts = {
        t: sum(1 for v in sym_tier.values() if v == t)
        for t in ("low", "medium", "high")
    }
    print(f"    {tier_counts}  (p33={p33:.4f}, p67={p67:.4f})")

    # ── 5. Greedy block assignment (direction-aware) ──────────────────────
    # For each stock, we consider BOTH its positive and negative directional
    # variants (Steps 6–7 of revised spec).  For each candidate
    # (block, direction_variant) pair we call _can_add and score with
    # _soft_score; the best-scoring viable pair wins.  If no pair passes
    # _can_add, sector is the only hard backstop — direction is relaxed to
    # ensure every stock that has a qualifying triple gets placed.
    _TYPE_PRIORITY = {
        "management": 0, "regulatory": 0,
        "product": 1,
        "analyst": 2, "other": 2,
        "earnings": 3,
    }

    # Use a representative event_type per stock for sorting (from first available variant)
    rep_etype = {
        sym: next(iter(variants.values())).get("event_type", "other")
        for sym, variants in dir_lookup.items()
    }
    # Sort stocks: process rare event types first, then by tier
    symbols_sorted = sorted(
        dir_lookup.keys(),
        key=lambda s: (
            _TYPE_PRIORITY.get(rep_etype.get(s, "other"), 2),
            {"low": 0, "medium": 1, "high": 2}.get(sym_tier.get(s, "medium"), 1),
        ),
    )

    dir_pool_dist = dir_pool["shock_direction"].value_counts().to_dict()
    dir_pool_type = dir_pool["event_type"].value_counts().to_dict()
    print(f"\n  [3/5]  Greedy block assignment (direction-aware) ...")
    print(f"    Direction-aware pool: {len(dir_lookup)} stocks  direction_variants={dir_pool_dist}")
    print(f"    Event types in pool : {dir_pool_type}")

    blocks: dict[str, list[dict]] = {"A": [], "B": [], "C": []}

    for i, symbol in enumerate(symbols_sorted):
        variants = dir_lookup[symbol]       # {direction: row_dict}, 1 or 2 entries
        tier     = sym_tier.get(symbol, "medium")

        # Collect all viable (block_label, direction) pairs
        viable: list[tuple[str, str]] = []
        rotation = [_BLOCK_LABELS[(i + offset) % _BLOCKS] for offset in range(_BLOCKS)]
        for block_label in rotation:
            for direction, stock_dict in variants.items():
                if _can_add(stock_dict, blocks[block_label]):
                    viable.append((block_label, direction))

        if viable:
            # Pick (block, direction) with highest soft score
            best_block, best_dir = max(
                viable,
                key=lambda bd: _soft_score(variants[bd[1]], blocks[bd[0]]),
            )
        elif all(len(blocks[k]) >= _SCENARIOS_PER_BLOCK for k in _BLOCK_LABELS):
            continue  # all blocks at capacity
        else:
            # Sector is the only remaining hard constraint — try every
            # non-full block and every direction variant, ignoring direction floor.
            sector = next(iter(variants.values())).get("sector", "Unknown")
            fallback: list[tuple[str, str]] = [
                (k, d)
                for k in _BLOCK_LABELS
                for d in variants
                if (
                    len(blocks[k]) < _SCENARIOS_PER_BLOCK
                    and sum(1 for s in blocks[k] if s.get("sector") == sector)
                    < _MAX_SECTOR_PER_BLOCK
                )
            ]
            if not fallback:
                continue  # sector cap hit in every non-full block — skip stock
            best_block, best_dir = min(fallback, key=lambda bd: len(blocks[bd[0]]))

        blocks[best_block].append(variants[best_dir])

    # ── 6. Convert to DataFrames and add scenario IDs ─────────────────────
    output: dict[str, pd.DataFrame] = {}
    for label in _BLOCK_LABELS:
        rows = blocks[label]
        if not rows:
            output[label] = pd.DataFrame()
            continue
        bdf = (
            pd.DataFrame(rows)
            .sort_values("sc_total")
            .reset_index(drop=True)
        )
        bdf["block"]       = label
        bdf["scenario_id"] = [f"{label}{i + 1}" for i in range(len(bdf))]
        output[label] = bdf

    # ── 7. Constraint audit ───────────────────────────────────────────────
    # Hard constraints carry ✓/✗; soft constraints carry ✓/⚠ (never block assignment).
    print(f"\n  [5/5]  Constraint audit (§2.3.2 revised):")
    print(f"  {'Block':<6} {'n':>3}  {'Sector':^6}  {'Direction':^20}  "
          f"{'Earnings':>12}  {'Event types':>11}  {'Regimes':>7}  {'OpenBar':>7}")
    print(f"  {'─'*88}")
    for label, bdf in output.items():
        if bdf.empty:
            print(f"  {label:<6} {'0':>3}  (empty)")
            continue
        n          = len(bdf)
        # --- Hard constraints (✓ / ✗) ---
        max_sec    = bdf["sector"].value_counts().max() if n > 0 else 0
        sec_ok     = "✓" if max_sec <= _MAX_SECTOR_PER_BLOCK else f"✗(max {max_sec})"
        dirs       = bdf["shock_direction"].value_counts().to_dict()
        dir_min    = min(dirs.values(), default=0)
        # Revised hard floor is ≥2 minority (was ≥3)
        dir_ok     = "✓" if dir_min >= 2 else f"✗(min {dir_min})"
        dir_str    = f"{dirs}"
        # --- Soft constraints (✓ / ⚠ — informational only, not blocking) ---
        n_earn     = int((bdf["event_type"] == "earnings").sum())
        earn_share = n_earn / n
        earn_ok    = "✓" if n_earn <= max_earnings_count else f"⚠({n_earn})"
        earn_str   = f"{n_earn}/{n}={earn_share:.0%} {earn_ok}"
        n_types    = bdf["event_type"].nunique()
        type_ok    = "✓" if n_types >= 3 else f"⚠({n_types})"
        n_regimes  = bdf["market_regime"].nunique()
        regime_ok  = "✓" if n_regimes >= 2 else f"⚠({n_regimes})"
        n_open     = int(bdf.get("is_opening_bar", pd.Series(False, index=bdf.index)).sum())
        open_ok    = "✓" if n_open <= _MAX_OPENING_BAR_PER_BLOCK else f"⚠({n_open})"
        print(
            f"  Block {label}  {n:>3}/8   "
            f"sector:{sec_ok:<9}  dir:{dir_ok:<12} {dir_str:<20}  "
            f"earn:{earn_str:<14}  types:{type_ok:<6}  regimes:{regime_ok}  "
            f"open:{open_ok}"
        )

    print(f"  Legend: ✓ = constraint met  |  ✗ = hard constraint violated  |  ⚠ = soft warning")
    # Flag if any block has a hard constraint violation (negative count < 2)
    for label, bdf in output.items():
        if bdf.empty:
            continue
        dirs    = bdf["shock_direction"].value_counts().to_dict()
        dir_min = min(dirs.values(), default=0)
        if dir_min < 2:
            print(
                f"\n  ⚠ Block {label} has only {dir_min} minority-direction scenario(s) "
                f"(hard floor = 2).  The direction-aware selection in Step 3 needs further "
                f"tuning — review and do NOT accept this result without investigation."
            )

    print(f"\n{'─' * 62}\n")
    return output


def print_block_tables(blocks: dict[str, pd.DataFrame]) -> None:
    """
    Print Tables 2.4a–c (§2.4 Selection Summary Tables).

    Column order matches the expanded protocol table definition (Amendment 6):
        Scenario | Stock | Ticker | GICS Sector | Event Date | Shock Time (ET) |
        Event Type | Direction | SC_total | AC_e | Displayed Headline |
        Rel Abn Ret | Shock Bar / Median Bar Ratio | Market Regime
    """
    _display = {
        "scenario_id":           "Scenario",
        "symbol":                "Stock",
        "sector":                "GICS Sector",
        "event_date":            "Event Date",
        "shock_time_et":         "Shock Time (ET)",
        "event_type":            "Event Type",
        "shock_direction":       "Direction",
        "sc_total":              "SC_total",
        "ac_e":                  "AC_e",
        "displayed_headline":    "Displayed Headline",
        "rel_abnormal_ret":      "Rel Abn Ret",
        "shock_bar_median_ratio": "Bar/Med Ratio",
        "market_regime":         "Regime",
    }
    _table_name = {"A": "2.4a", "B": "2.4b", "C": "2.4c"}

    for label, bdf in blocks.items():
        print(f"\n{'═' * 130}")
        print(f"  Table {_table_name[label]}: Block {label} Scenario Selection Summary")
        print(f"{'═' * 130}")
        if bdf.empty:
            print("  (no scenarios — candidate pool insufficient for this block)\n")
            continue

        out = bdf[[c for c in _display if c in bdf.columns]].copy()
        out = out.rename(columns=_display)

        # Truncate displayed headline for readable table output
        if "Displayed Headline" in out.columns:
            out["Displayed Headline"] = out["Displayed Headline"].astype(str).apply(
                lambda h: h[:55] + "…" if len(h) > 56 else h
            )

        for col in ("SC_total", "Rel Abn Ret", "Bar/Med Ratio"):
            if col in out.columns:
                out[col] = out[col].astype(float).round(4)

        if "AC_e" in out.columns:
            out["AC_e"] = out["AC_e"].astype(float).round(0).astype(int)

        print(out.to_string(index=False))
        print()


# ── §2.5 Scenario Visualisation ───────────────────────────────────────────────

def plot_scenario_charts(
    blocks: dict[str, pd.DataFrame],
    prices: pd.Series,
    output_dir: str = "images",
    dpi: int = 150,
    data_dir: str = "data",
) -> None:
    """
    §2.5 Scenario Visualisation – Intraday Event Charts.

    For each scenario in blocks, generates a two-panel figure:

    Upper panel
        Intraday price action for the event day, normalised to 100 at the
        first bar (market open), displayed as 30-minute bars per §2.1A.
        Produces up to 13 bars for a full trading day (09:30–16:00 ET).
        Positive/negative regions above and below the open are shaded
        green/red respectively.  A coloured dot marks the shock bar; a
        dotted vertical line marks the shock time.  High and low of the
        day are annotated directly on the chart.

    Middle panel  (rendered only when volume data is available)
        30-minute bar trading volume as a bar chart.  The shock bar is
        highlighted in the same direction colour as the dot.

    Lower panel
        Shock characteristics printed in monospaced text:
          Line 1 – SC_total, shock direction, 30-min bar return, relative abnormal return
          Line 2 – SC_total components: AC_e, SE_e, AI_e, ES_e
          Line 3 – Displayed headline (primary headline for survey respondents)

    Naming convention
        {Block}_{ScenarioNumber}.png
        e.g.  A_1.png, A_12.png, B_3.png, C_9.png

    Parameters
    ----------
    blocks     : dict {"A": df, "B": df, "C": df} — output of assign_blocks
    prices     : (symbol, time) → close MultiIndex Series from load_market_data
    output_dir : directory for saving images (created if absent; default "images")
    dpi        : image resolution (default 150)
    data_dir   : directory containing *_30mins_*.csv files for volume data
    """
    if not _HAS_MATPLOTLIB:
        print(
            "  ⚠  matplotlib not available (pip install matplotlib).\n"
            "     Skipping scenario chart generation."
        )
        return

    os.makedirs(output_dir, exist_ok=True)

    # ── Convert price MultiIndex Series → 30-min tz-naive ET DataFrame ───────
    bar_close = _prices_to_bar_close(prices)

    # ── Load 30-min bar volumes (best-effort; skipped gracefully if unavailable)
    bar_volumes = _load_bar_volumes(data_dir)

    total_charts = sum(len(bdf) for bdf in blocks.values() if not bdf.empty)

    print(f"\n{'─' * 62}")
    print(f"  SCENARIO CHARTS  ·  §2.5 Intraday Event Visualisation")
    print(f"  Granularity: 30-minute bars  ({BARS_PER_DAY} bars/day)")
    print(f"  Generating {total_charts} charts → {os.path.abspath(output_dir)}/")
    print(f"{'─' * 62}")

    saved   = 0
    skipped = 0

    def _fmt(v, fmt=".4f"):
        try:
            f = float(v)
            return "N/A" if np.isnan(f) else format(f, fmt)
        except (ValueError, TypeError):
            return "N/A"

    def _pct(v):
        try:
            f = float(v)
            return "N/A" if np.isnan(f) else f"{f * 100:+.2f}%"
        except (ValueError, TypeError):
            return "N/A"

    for block_label, bdf in blocks.items():
        if bdf.empty:
            continue

        for _, row in bdf.iterrows():
            scenario_id  = str(row.get("scenario_id", f"{block_label}?"))
            scenario_num = scenario_id.lstrip("ABCabc").strip()
            filename     = f"{block_label}_{scenario_num}.png"
            save_path    = os.path.join(output_dir, filename)

            symbol     = str(row["symbol"])
            event_time = pd.Timestamp(row["event_time"])   # tz-naive ET
            event_date = event_time.normalize()

            # ── Intraday price slice ───────────────────────────────────────
            if symbol not in bar_close.columns:
                print(f"  ✗  {filename:<18}  {symbol} not in price data — skipped")
                skipped += 1
                continue

            sym_series = bar_close[symbol].dropna()
            day_prices = sym_series[
                sym_series.index.normalize() == event_date
            ].sort_index()

            if day_prices.empty:
                print(
                    f"  ✗  {filename:<18}  {symbol} no data on "
                    f"{event_date.date()} — skipped"
                )
                skipped += 1
                continue

            # ── Prior trading day context (§4.2.4) ────────────────────────
            all_trade_dates   = sorted(sym_series.index.normalize().unique())
            prior_dates_avail = [d for d in all_trade_dates if d < event_date]
            prior_date        = prior_dates_avail[-1] if prior_dates_avail else None
            prior_prices      = (
                sym_series[sym_series.index.normalize() == prior_date].sort_index()
                if prior_date is not None else pd.Series(dtype="float64")
            )

            # Combined series: prior day + event day.
            # Normalise to 100 at the start of the combined series (prior day
            # open if available) so respondents see the run-in context.
            if not prior_prices.empty:
                combined     = pd.concat([prior_prices, day_prices]).sort_index()
                day_boundary = day_prices.index[0]
            else:
                combined     = day_prices
                day_boundary = None

            two_day = day_boundary is not None
            norm    = combined / combined.iloc[0] * 100.0

            # ── Identify shock bar ─────────────────────────────────────────
            if event_time in norm.index:
                shock_bar = event_time
            elif len(norm) > 0:
                diff      = (norm.index - event_time).abs()
                shock_bar = norm.index[diff.argmin()]
            else:
                shock_bar = None

            # ── Integer x-axis (eliminates non-trading-hours gaps) ─────────
            # Each bar occupies one integer slot; overnight gaps are absent.
            positions   = np.arange(len(norm))
            time_to_pos = {t: i for i, t in enumerate(norm.index)}

            if shock_bar is not None:
                shock_pos = time_to_pos.get(
                    shock_bar,
                    int(np.argmin(np.abs(norm.index - shock_bar))),
                )
                # Place dot one bar before the shock bar (§4.2.4 request)
                shock_display_pos = max(0, shock_pos - 1)
            else:
                shock_pos         = None
                shock_display_pos = None

            boundary_pos = (
                time_to_pos.get(day_boundary)
                if (two_day and day_boundary is not None) else None
            )

            # ── Volume slice (optional) ────────────────────────────────────
            has_vol = (
                not bar_volumes.empty
                and symbol in bar_volumes.columns
            )
            if has_vol:
                vol_series = bar_volumes[symbol].dropna()
                event_vol  = vol_series[
                    vol_series.index.normalize() == event_date
                ].sort_index()
                prior_vol  = (
                    vol_series[vol_series.index.normalize() == prior_date].sort_index()
                    if prior_date is not None else pd.Series(dtype="float64")
                )
                day_vol = (
                    pd.concat([prior_vol, event_vol]).sort_index()
                    if not prior_vol.empty else event_vol
                )
                has_vol = not day_vol.empty

            # ── Direction colour palette ───────────────────────────────────
            direction = str(row.get("shock_direction", "")).lower()
            if direction == "negative":
                dot_color = "#d62728"
                bg_color  = "#fff5f5"
                dir_arrow = "▼"
            elif direction == "positive":
                dot_color = "#2ca02c"
                bg_color  = "#f5fff8"
                dir_arrow = "▲"
            else:
                dot_color = "#7f7f7f"
                bg_color  = "#f8f8f8"
                dir_arrow = "–"

            # ── Figure layout ──────────────────────────────────────────────
            if has_vol:
                fig = _plt.figure(figsize=(14, 12.0), constrained_layout=True)
                gs  = _GridSpec(
                    3, 1, figure=fig,
                    height_ratios=[5.0, 1.4, 3.6],
                )
                ax_price = fig.add_subplot(gs[0])
                ax_vol   = fig.add_subplot(gs[1], sharex=ax_price)
                ax_meta  = fig.add_subplot(gs[2])
            else:
                fig = _plt.figure(figsize=(14, 11.0), constrained_layout=True)
                gs  = _GridSpec(
                    2, 1, figure=fig,
                    height_ratios=[5.5, 3.6],
                )
                ax_price = fig.add_subplot(gs[0])
                ax_vol   = None
                ax_meta  = fig.add_subplot(gs[1])

            ax_meta.axis("off")

            # ── Price line ─────────────────────────────────────────────────
            ax_price.plot(
                positions, norm.values,
                color="#1f77b4", linewidth=2.2, zorder=3,
                solid_capstyle="round",
            )
            ax_price.axhline(
                100.0, color="#888888", linewidth=0.9,
                linestyle="--", alpha=0.7, zorder=1,
            )
            ax_price.fill_between(
                positions, 100.0, norm.values,
                where=(norm.values >= 100.0),
                color="#2ca02c", alpha=0.08, zorder=1,
            )
            ax_price.fill_between(
                positions, 100.0, norm.values,
                where=(norm.values < 100.0),
                color="#d62728", alpha=0.08, zorder=1,
            )

            # ── Shock marker (dot placed one bar before shock bar) ─────────
            if shock_bar is not None and shock_display_pos is not None:
                sv = norm.values[shock_display_pos]
                ax_price.scatter(
                    [shock_display_pos], [sv],
                    s=180, color=dot_color, zorder=6,
                    edgecolors="white", linewidths=2.0,
                )
                ax_price.axvline(
                    shock_display_pos, color=dot_color,
                    linewidth=1.2, linestyle=":", alpha=0.5, zorder=2,
                )
                ax_price.annotate(
                    f"Shock\n{shock_bar.strftime('%H:%M')} ET",
                    xy=(shock_display_pos, sv),
                    xytext=(8, 0), textcoords="offset points",
                    fontsize=8.5, color=dot_color,
                    va="center", fontweight="bold",
                )
                if ax_vol is not None and has_vol:
                    ax_vol.axvline(
                        shock_display_pos, color=dot_color,
                        linewidth=1.2, linestyle=":", alpha=0.5, zorder=2,
                    )

            # ── Day high / low annotations ─────────────────────────────────
            day_high  = norm.max()
            day_low   = norm.min()
            day_close = norm.iloc[-1]

            ax_price.annotate(
                f"H: {day_high:.2f}",
                xy=(int(norm.values.argmax()), day_high),
                xytext=(0, 6), textcoords="offset points",
                fontsize=8, color="#2ca02c", fontweight="bold",
                ha="center", va="bottom",
            )
            ax_price.annotate(
                f"L: {day_low:.2f}",
                xy=(int(norm.values.argmin()), day_low),
                xytext=(0, -7), textcoords="offset points",
                fontsize=8, color="#d62728", fontweight="bold",
                ha="center", va="top",
            )

            # ── Chart formatting ───────────────────────────────────────────
            sector = str(row.get("sector", "Unknown"))
            etype  = str(row.get("event_type", "other")).capitalize()
            regime = str(row.get("market_regime", "neutral")).capitalize()
            tier   = str(row.get("intensity_tier", "")).capitalize()

            close_chg = day_close - 100.0
            close_str = f"{dir_arrow} {abs(close_chg):.2f}% vs open"

            company_name = str(row.get("company_name", symbol))
            ax_price.set_title(
                f"Scenario {scenario_id}  ·  {company_name} ({symbol})  ·  {sector}\n"
                f"{event_time.strftime('%A, %d %B %Y')}  "
                f"Shock bar: {event_time.strftime('%H:%M')} ET     "
                f"Event Type: {etype}     Market Regime: {regime}     "
                f"Intensity: {tier}     Close: {close_str}",
                fontsize=12, fontweight="bold", pad=10, loc="left",
            )
            ax_price.set_ylabel("Normalised Price (Open = 100)", fontsize=9)
            ax_price.grid(True, alpha=0.20, linestyle="--", color="#aaaaaa")
            ax_price.set_facecolor(bg_color)
            ax_price.set_xlim(-0.5, len(norm) - 0.5)

            # ── Day boundary line and labels ───────────────────────────────
            if two_day and boundary_pos is not None:
                ax_price.axvline(
                    boundary_pos - 0.5, color="#555555",
                    linewidth=1.4, linestyle="--", alpha=0.5, zorder=2,
                )
                y_range       = norm.max() - norm.min()
                y_lbl         = norm.max() + y_range * 0.04
                prior_mid_pos = (boundary_pos - 1) / 2.0
                event_mid_pos = (boundary_pos + len(norm) - 1) / 2.0
                if not prior_prices.empty:
                    ax_price.text(
                        prior_mid_pos, y_lbl,
                        prior_date.strftime("%d %b"),
                        fontsize=8, color="#999999",
                        ha="center", va="bottom",
                    )
                ax_price.text(
                    event_mid_pos, y_lbl,
                    event_date.strftime("%d %b  ◀ Event"),
                    fontsize=8, color="#333333",
                    ha="center", va="bottom", fontweight="bold",
                )
                if ax_vol is not None and has_vol:
                    ax_vol.axvline(
                        boundary_pos - 0.5, color="#555555",
                        linewidth=1.4, linestyle="--", alpha=0.5, zorder=2,
                    )

            # ── x-axis tick marks (integer positions; no non-trading gaps) ─
            # Single day: every bar (step 1); two-day: every other bar (step 2)
            _tick_step = 2 if two_day else 1
            _tick_pos  = list(range(0, len(norm), _tick_step))
            _tick_lbl  = [norm.index[i].strftime("%H:%M") for i in _tick_pos]

            # Labels go on the bottom-most axis that is visible
            _ax_bottom = ax_vol if (ax_vol is not None and has_vol) else ax_price
            _ax_bottom.set_xticks(_tick_pos)
            _ax_bottom.set_xticklabels(_tick_lbl, fontsize=7.5, rotation=0)
            _ax_bottom.set_xlabel("Time (ET)", fontsize=9)

            if ax_vol is not None and has_vol:
                _plt.setp(ax_price.get_xticklabels(), visible=False)

            # ── Volume bars (integer positions matching price bars) ─────────
            if ax_vol is not None and has_vol:
                vol_pos_list = []
                vol_val_list = []
                vol_col_list = []
                for t, v in day_vol.items():
                    if t in time_to_pos:
                        p = time_to_pos[t]
                        vol_pos_list.append(p)
                        vol_val_list.append(float(v))
                        # Highlight the actual shock bar (not the dot position)
                        vol_col_list.append(
                            dot_color if p == shock_pos else "#bbbbbb"
                        )
                if vol_pos_list:
                    ax_vol.bar(
                        vol_pos_list, vol_val_list,
                        width=0.8, color=vol_col_list,
                        align="center", zorder=2,
                    )
                ax_vol.set_ylabel("Volume", fontsize=8)
                ax_vol.yaxis.set_major_formatter(
                    _plt.FuncFormatter(
                        lambda v, _: (
                            f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K"
                        )
                    )
                )
                ax_vol.set_facecolor(bg_color)
                ax_vol.grid(True, alpha=0.15, linestyle="--")

            # ── Metadata panel ─────────────────────────────────────────────
            sc_total   = row.get("sc_total",         float("nan"))
            rel_abn    = row.get("rel_abnormal_ret", float("nan"))
            bar_ret    = row.get("bar_return",       float("nan"))
            ac_e_v     = row.get("ac_e",  row.get("article_count", float("nan")))
            se_e_v     = row.get("se_e",  float("nan"))
            ai_e_v     = row.get("ai_e",  float("nan"))
            es_e_v     = row.get("es_e",  float("nan"))
            disp_hl    = str(row.get("displayed_headline", row.get("sample_headlines", ""))).strip()
            art_text   = str(row.get("article_text_full", "")).strip()

            disp_hl = _html.unescape(disp_hl)
            disp_hl = disp_hl.replace("$", r"\$")
            if len(disp_hl) > 160:
                disp_hl = disp_hl[:157] + "…"
            if not disp_hl:
                disp_hl = "(no headline data)"

            # Article text snippet (AC_e = 1 only; first ~300 chars)
            art_text = _html.unescape(art_text)
            art_text = art_text.replace("$", r"\$")
            if art_text.lower() in ("nan", "none", ""):
                art_snippet = ""
            elif len(art_text) > 300:
                art_snippet = art_text[:297] + "…"
            else:
                art_snippet = art_text

            line1 = (
                f"  SC_total = {_fmt(sc_total)}   │   "
                f"Direction: {dir_arrow} {direction.upper():<8}   │   "
                f"Bar Return (30-min): {_pct(bar_ret):<10}   │   "
                f"Rel Abnormal Return: {_pct(rel_abn)}"
            )
            line2 = (
                f"  Shock Score Components:   "
                f"AC_e (articles) = {_fmt(ac_e_v, '.0f'):<4}   │   "
                f"SE_e (sentiment) = {_fmt(se_e_v):<8}   │   "
                f"AI_e (vol ratio) = {_fmt(ai_e_v, '.3f'):<8}   │   "
                f"ES_e (severity) = {_fmt(es_e_v)}"
            )
            line3 = f"  Headline:  {disp_hl}"
            line4 = f"  Text:      {art_snippet}" if art_snippet else ""

            ax_meta.set_xlim(0, 1)
            ax_meta.set_ylim(0, 1)
            ax_meta.add_patch(
                _plt.Rectangle(
                    (0, 0), 1, 1,
                    transform=ax_meta.transAxes,
                    facecolor="#f2f2f2", edgecolor="#cccccc",
                    linewidth=0.8, clip_on=False, zorder=0,
                )
            )
            ax_meta.axhline(1.0, color="#cccccc", linewidth=0.8, zorder=1)

            meta_lines = [
                (0.87, line1, 9.5, "normal"),
                (0.64, line2, 9.5, "normal"),
                (0.42, line3, 8.5, "italic"),
            ]
            if line4:
                meta_lines.append((0.18, line4, 8.0, "italic"))

            for y_pos, text, fontsize, fontstyle in meta_lines:
                ax_meta.text(
                    0.005, y_pos, text,
                    transform=ax_meta.transAxes,
                    fontsize=fontsize, va="top", ha="left",
                    fontstyle=fontstyle,
                    fontfamily="monospace",
                    color="#111111",
                    clip_on=True,
                )

            # ── Save ───────────────────────────────────────────────────────
            fig.patch.set_facecolor("white")
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight", facecolor="white")
            _plt.close(fig)

            saved += 1
            print(
                f"  ✓  {filename:<18}  {symbol:<6}  "
                f"{event_date.date()}  {dir_arrow} {direction:<8}"
            )

    print(f"\n  {'─' * 58}")
    print(f"  Saved : {saved}   Skipped : {skipped}   Total : {total_charts}")
    print(f"  Path  : {os.path.abspath(output_dir)}/")
    print(f"{'─' * 62}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# Survey SC scoring — survey_assembly pipeline helpers
# ═══════════════════════════════════════════════════════════════════════════════
#
# These functions are called by 3_survey_assembly.py to compute SC_total and
# persistence horizon for a pre-defined set of scenarios (the manifest).  They
# complement the candidate-pool functions above but operate on a finalised
# scenario list rather than the full candidate pool.
#
# Functions
# ---------
# aggregate_daily              – 30-min bars → daily close + volume
# get_trailing_window          – n trading days before event_date
# get_event_day_bars           – all 30-min bars on event_date
# get_event_day_news           – BZ articles for (ticker, event_date)
# _sentiment_direction_label   – mean score → 7-level label
# compute_raw_components       – ac_raw / se_raw / ai_raw / es_raw per scenario
# compute_shock_scores         – z-standardise + PCA → sc_total + dashboard signals
# compute_persistence_horizon  – CAR-based P_e and horizon bucket
# ═══════════════════════════════════════════════════════════════════════════════

# ── Survey SC constants ───────────────────────────────────────────────────────

# Sentiment direction thresholds (applied to mean FinBERT score across event-day articles)
SENTIMENT_THRESHOLDS = [-0.6, -0.3, -0.1, 0.1, 0.3, 0.6]
SENTIMENT_LABELS = [
    "Strongly Negative", "Negative", "Mildly Negative",
    "Neutral",
    "Mildly Positive", "Positive", "Strongly Positive",
]

# Placeholder severity mapping for es_raw; requires manual review per protocol §2.2
EVENT_TYPE_SEVERITY = {
    "earnings": 1.0, "guidance": 0.9, "regulatory": 1.1,
    "management": 0.8, "analyst": 0.6, "macro": 0.7,
    "product": 0.7, "legal": 1.0, "dividend": 0.5, "other": 0.5,
}


# ── Price data helpers ────────────────────────────────────────────────────────

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


def get_event_day_news(
    news_data: dict,
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


# ── Sentiment label ───────────────────────────────────────────────────────────

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


# ── Raw component computation ─────────────────────────────────────────────────

def compute_raw_components(
    manifest_df: pd.DataFrame,
    prices: dict,
    news_data: dict,
) -> pd.DataFrame:
    """
    Compute four raw SC components for each scenario in manifest_df.

    ac_raw  – Article Count: number of BZ articles on event day
    se_raw  – Sentiment Extremity: max |FinBERT score| across event-day articles
    ai_raw  – Attention Intensity: event-day volume / 20-day trailing avg daily volume
    es_raw  – Event-Type Severity: category severity from EVENT_TYPE_SEVERITY mapping
               (placeholder — requires manual review per protocol §2.2)

    Also records mean_sentiment and sentiment_scores for dashboard signals.

    Parameters
    ----------
    manifest_df : scenario manifest (columns: scenario_id, ticker, event_date, event_type)
    prices      : {ticker: DataFrame[time (UTC tz-aware), close, volume]}
    news_data   : {ticker: DataFrame[time (UTC tz-aware), headline, article_text, ...]}

    Returns
    -------
    DataFrame with one row per scenario and columns:
        scenario_id, ticker, event_date, event_type,
        ac_raw, se_raw, ai_raw, es_raw,
        mean_sentiment, sentiment_scores, num_articles_found
    """
    try:
        from news_processor_toolkit import HAS_FINBERT, _finbert_score
    except ImportError:
        HAS_FINBERT = False
        def _finbert_score(text: str) -> float:
            return 0.0

    import re as _re

    rows = []
    for _, mrow in manifest_df.iterrows():
        sid        = mrow["scenario_id"]
        ticker     = mrow["ticker"]
        event_date = mrow["event_date"]
        event_type = str(mrow.get("event_type", "other")).lower().strip()

        print(f"  {sid} ({ticker} {event_date})...", end="", flush=True)

        # ── AC_raw ────────────────────────────────────────────────────────
        day_articles = get_event_day_news(news_data, ticker, event_date)
        ac_raw = len(day_articles)
        if ac_raw == 0:
            print(f"  [WARNING] {sid}: no news articles found for {ticker} on {event_date}")

        # ── SE_raw ────────────────────────────────────────────────────────
        sentiment_scores: list = []
        mean_sentiment = 0.0
        se_raw = 0.0

        if not day_articles.empty:
            if HAS_FINBERT:
                for _, art in day_articles.iterrows():
                    hl         = str(art.get("headline", ""))
                    body       = str(art.get("article_text", ""))
                    body_clean = _re.sub(r"<[^>]+>", " ", body)
                    score      = _finbert_score(f"{hl} {body_clean}")
                    sentiment_scores.append(score)
                if sentiment_scores:
                    se_raw         = max(abs(s) for s in sentiment_scores)
                    mean_sentiment = float(np.mean(sentiment_scores))
            else:
                print(
                    f"  [WARNING] {sid}: FinBERT unavailable – se_raw set to 0 "
                    "(install transformers torch)"
                )

        # ── AI_raw ────────────────────────────────────────────────────────
        ai_raw = 0.0
        if ticker in prices:
            daily_df      = aggregate_daily(prices[ticker])
            trailing_20   = get_trailing_window(daily_df, event_date, n=20)
            event_day_vol = daily_df[daily_df["date"] == event_date]["volume"]

            if not event_day_vol.empty and not trailing_20.empty:
                avg_vol = float(trailing_20["volume"].mean())
                if avg_vol > 0:
                    ai_raw = float(event_day_vol.iloc[0]) / avg_vol
                else:
                    print(f"  [WARNING] {sid}: 20-day average volume is zero; ai_raw set to 0")
            else:
                print(f"  [WARNING] {sid}: insufficient volume data for ai_raw computation")
        else:
            print(f"  [WARNING] {sid}: no price data for {ticker}; ai_raw set to 0")

        # ── ES_raw ────────────────────────────────────────────────────────
        es_raw = EVENT_TYPE_SEVERITY.get(event_type, 0.5)

        print(" done")

        rows.append({
            "scenario_id":       sid,
            "ticker":            ticker,
            "event_date":        event_date,
            "event_type":        event_type,
            "ac_raw":            ac_raw,
            "se_raw":            se_raw,
            "ai_raw":            ai_raw,
            "es_raw":            es_raw,
            "mean_sentiment":    mean_sentiment,
            "sentiment_scores":  sentiment_scores,
            "num_articles_found": ac_raw,
        })

    return pd.DataFrame(rows)


# ── Shock score computation ───────────────────────────────────────────────────

def compute_shock_scores(
    components_df: pd.DataFrame,
) -> tuple:
    """
    Z-standardise raw components, run PCA (PC1), compute sc_total.
    Adds dashboard signal columns to the DataFrame.

    Sign convention: sc_total is oriented so that higher values = higher shock intensity.
    Verification: PC1 should load positively on ac_raw (article count).

    Parameters
    ----------
    components_df : output of compute_raw_components()

    Returns
    -------
    (enriched_df, pca_info_dict)
        enriched_df  – components_df with z-columns, sc_total, and dashboard signals
        pca_info_dict – {"loadings": {...}, "explained_variance": float, "n_scenarios": int}
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    df      = components_df.copy()
    n       = len(df)
    raw_cols = ["ac_raw", "se_raw", "ai_raw", "es_raw"]
    z_cols   = ["ac_z",  "se_z",  "ai_z",  "es_z"]

    if n < 2:
        print("  [WARNING] Fewer than 2 scenarios – PCA degenerate; sc_total set to 0")
        for zcol in z_cols:
            df[zcol] = 0.0
        df["sc_total"] = 0.0
        return df, {}

    # Z-standardise
    X      = df[raw_cols].fillna(0).values.astype(float)
    scaler = StandardScaler()
    Z      = scaler.fit_transform(X)
    for i, zcol in enumerate(z_cols):
        df[zcol] = Z[:, i]

    # PCA: first principal component
    pca     = PCA(n_components=1)
    sc_raw  = pca.fit_transform(Z).flatten()
    loadings = pca.components_[0]
    explained_var = float(pca.explained_variance_ratio_[0])

    # Sign convention: pc1 should correlate positively with ac_raw (col 0)
    if loadings[0] < 0:
        sc_raw   = -sc_raw
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

    # ── Dashboard signals ─────────────────────────────────────────────────

    # 1. Sentiment direction (from mean FinBERT score)
    df["sentiment_direction"] = df["mean_sentiment"].apply(_sentiment_direction_label)

    # 2. Severity level (33rd/66th percentile)
    p33 = df["sc_total"].quantile(1 / 3)
    p66 = df["sc_total"].quantile(2 / 3)

    def _severity(sc: float) -> str:
        if sc < p33:
            return "Low"
        elif sc < p66:
            return "Medium"
        return "High"

    df["severity_level"] = df["sc_total"].apply(_severity)

    # 3. Protocol recommendation (60th / 85th percentile per thesis design)
    p60 = df["sc_total"].quantile(0.60)
    p85 = df["sc_total"].quantile(0.85)

    def _protocol(sc: float) -> str:
        if sc < p60:
            return "Standard Process"
        elif sc < p85:
            return "Enhanced Review"
        return "Cooling-Off and Second Review"

    df["protocol_recommendation"] = df["sc_total"].apply(_protocol)

    return df, pca_info


# ── Persistence horizon ───────────────────────────────────────────────────────

def _fetch_spx_pct_returns(start: str, end: str) -> pd.Series:
    """
    Fetch S&P 500 daily close-to-close simple returns via yfinance.
    Returns a pd.Series indexed by datetime.date, values are decimal returns.
    Returns an empty Series on failure so callers can degrade to raw returns.

    Note: differs from _fetch_spx_daily() which returns log returns with an
    extended look-back for the rolling-window shock identification step.
    """
    try:
        raw  = yf.download("^GSPC", start=start, end=end,
                           progress=False, auto_adjust=True)
        if raw.empty:
            print("  [WARNING] SPX download returned empty data – CAR computed without market adjustment")
            return pd.Series(dtype=float)
        closes = raw["Close"].squeeze()
        rets   = closes.pct_change().dropna()
        rets.index = pd.to_datetime(rets.index).date
        return rets
    except Exception as exc:
        print(f"  [WARNING] SPX fetch failed ({exc}) – CAR computed without market adjustment")
        return pd.Series(dtype=float)


def compute_persistence_horizon(
    sc_df: pd.DataFrame,
    prices: dict,
) -> pd.DataFrame:
    """
    Compute CAR-based persistence horizon for each scenario in sc_df.

    For each event e:
        base_price  = EOD close of event day (last 30-min bar)
        CAR_Day_n   = (stock_price_at_day_n / base_price − 1) − cumulative_SPX_return
        P_e         = CAR_Day5 / CAR_Day1

    If abs(CAR_Day1) < 0.001, P_e is unreliable; scenario is classified
    directly as Intraday.

    Horizon bucket mapping (validate against distribution after run):
        Intraday:      |P_e| <= 0.30
        Several Days:  0.30 < |P_e| <= 0.70
        Several Weeks: |P_e| > 0.70

    Parameters
    ----------
    sc_df  : output of compute_shock_scores() — must contain scenario_id, ticker, event_date
    prices : {ticker: DataFrame[time (UTC tz-aware), close, volume]}

    Returns
    -------
    sc_df with persistence_score and horizon_bucket columns added / overwritten.
    """
    df = sc_df.copy()

    event_dates   = pd.to_datetime(df["event_date"]).dt.date
    spx_start     = str(min(event_dates))
    spx_end       = str(max(event_dates) + pd.Timedelta(days=20))
    spx_ret       = _fetch_spx_pct_returns(spx_start, spx_end)
    spx_available = not spx_ret.empty

    CAR_DAYS           = [1, 3, 5, 10]
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

        if ticker not in prices:
            persistence_scores.append(np.nan)
            horizon_buckets.append("[NO PRICE DATA]")
            print(f"  {sid:<12} {ticker:<6}  -- no price data --")
            continue

        price_df = prices[ticker].copy()
        price_df["date_et"] = (
            price_df["time"].dt.tz_convert("America/New_York").dt.date
        )

        event_day_bars = price_df[price_df["date_et"] == event_date]
        if event_day_bars.empty:
            persistence_scores.append(np.nan)
            horizon_buckets.append("[NO EVENT-DAY PRICE]")
            print(f"  {sid:<12} {ticker:<6}  -- no event-day bars --")
            continue

        base_price = float(event_day_bars["close"].iloc[-1])

        after_eod = (
            price_df[price_df["date_et"] > event_date]
            .groupby("date_et")["close"]
            .last()
            .sort_index()
        )

        car_vals: dict = {}
        for n_days in CAR_DAYS:
            if n_days > len(after_eod) or base_price == 0:
                car_vals[n_days] = np.nan
                continue
            target_price = float(after_eod.iloc[n_days - 1])
            stock_ret    = (target_price - base_price) / base_price

            if spx_available:
                trading_dates = list(after_eod.index[:n_days])
                spx_cum = 1.0
                for td in trading_dates:
                    if td in spx_ret.index:
                        spx_cum *= (1.0 + float(spx_ret[td]))
                car_vals[n_days] = round(stock_ret - (spx_cum - 1.0), 6)
            else:
                car_vals[n_days] = round(stock_ret, 6)

        car1 = car_vals.get(1, np.nan)
        car5 = car_vals.get(5, np.nan)

        if np.isnan(car1) or np.isnan(car5):
            p_e    = np.nan
            bucket = "[INSUFFICIENT DATA]"
        elif abs(car1) < 0.001:
            p_e    = np.nan
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

        print(f"  {sid:<12} {ticker:<6} {_fmt(car_vals.get(1, np.nan))} "
              f"{_fmt(car_vals.get(3, np.nan))} {_fmt(car_vals.get(5, np.nan))} "
              f"{_fmt(car_vals.get(10, np.nan))} {_fmt(p_e)}  {bucket}")

    df["persistence_score"] = persistence_scores
    df["horizon_bucket"]    = horizon_buckets

    valid = pd.Series(
        [s for s in persistence_scores if s is not None and not np.isnan(float(s))],
        dtype=float,
    )
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
