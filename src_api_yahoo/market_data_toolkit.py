from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable, Dict, Literal

import numpy as np
import pandas as pd
import yfinance as yf


# =========================
# Lightweight logging (no signature changes)
# =========================
VERBOSE = True  # flip to False to silence logs

def set_log_verbosity(flag: bool) -> None:
    """Toggle module-level verbosity without changing function signatures."""
    global VERBOSE
    VERBOSE = bool(flag)

def _log(msg: str) -> None:
    if VERBOSE:
        print(msg)


# =========================
# Data container
# =========================
@dataclass
class PriceResult:
    prices_chf: pd.DataFrame          # CHF-denominated price series, columns are ISINs
    fx_used: pd.DataFrame             # FX series actually applied per ISIN (1.0 for CHF)
    raw_prices: pd.DataFrame          # Raw price series in local trading currency (by ISIN)
    historical_returns: pd.DataFrame  # Daily log returns (CHF), same columns as prices_chf


# =========================
# Yahoo mapping: ISIN → ticker
# =========================
def isin_to_ticker(tickers: pd.DataFrame) -> pd.DataFrame:
    """
    Map ISIN → Yahoo ticker. Handle common FX codes (base CHF).
    Also fetch trading currency (Yahoo 'currency' field).
    If a ticker cannot be resolved, mark it as 'missing<isin>'.
    """
    df = tickers.copy()
    if "ticker" not in df.columns:
        df["ticker"] = ""
    df["isin"] = df["isin"].astype(str)
    df["ticker"] = df["ticker"].astype(str).fillna("")
    df["ccy"] = ""   # new column for currency
    df["quote_type"] = ""

    for index, row in df.iterrows():
        tkr = str(row["ticker"])
        if tkr and not tkr.lower().startswith("missing"):
            continue
        try:
            t = yf.Ticker(row["isin"])
            ticker_found = t.ticker

            if ticker_found:
                df.at[index, "ticker"] = ticker_found
                info = t.get_info()
                df.at[index, "ccy"] = info.get("currency", "")
                df.at[index, "quote_type"] = (info.get("quoteType") or info.get("quote_type") or "").upper()

                _log(f"[map] ISIN {row['isin']} -> {ticker_found}, ccy={df.at[index,'ccy']}, type={df.at[index,'quote_type']}")
            else:
                _log(f"[map-miss] ISIN {row['isin']} (no Yahoo mapping)")
        except Exception as e:
            _log(f"[map-fail] ISIN {row['isin']}: {e}")

    # Handle currencies explicitly (FX pairs)
    fx_ccys = ["USD", "JPY", "EUR", "AUD", "GBP", "CAD", "HKD"]
    mask = df["ticker"].isin(fx_ccys)
    df.loc[mask, "ticker"] = df.loc[mask, "ticker"] + "CHF=X"
    df.loc[mask, "ccy"] = df.loc[mask, "ticker"].str.replace("CHF=X", "", regex=False)

    # CHF base -> no Yahoo ticker; mark unresolved as 'missing<isin>'
    df.loc[df["ticker"] == "CHF", ["ticker", "ccy"]] = ["", "CHF"]
    empty_mask = df["ticker"].eq("")
    df.loc[empty_mask, "ticker"] = "missing" + df.loc[empty_mask, "isin"]
    df.loc[empty_mask, "ccy"]="CHF"
    df["ccy"] = df["ccy"].astype(str).str.upper()

    return df


# =========================
# Yahoo analyst price targets (equities only)
# =========================
def fetch_price_targets_from_yahoo(tickers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetch analyst mean price targets for equities only (Yahoo Finance via yfinance).

    Parameters
    ----------
    tickers_df : pd.DataFrame
        Must contain columns ['isin','ticker'].

    Returns
    -------
    pd.DataFrame
        Columns: ['isin','quoteType','mean'] (one row per ISIN where a mean target exists).
    """
    results: list[dict] = []

    n_seen = 0
    n_skipped_missing = 0
    n_equity = 0
    n_targets = 0

    for _, row in tickers_df.iterrows():
        ticker = str(row["ticker"])
        isin = str(row["isin"])
        quote_type = str(row["quote_type"])
        n_seen += 1

        # skip missing/unresolved tickers
        if not ticker or ticker.lower().startswith("missing"):
            n_skipped_missing += 1
            continue

        try:

            if quote_type == "EQUITY":
                t = yf.Ticker(ticker)
                n_equity += 1
                pt = t.get_analyst_price_targets()
                if pt and ("mean" in pt or "targetMean" in pt):
                    mean_val = pt.get("mean", pt.get("targetMean"))
                    results.append({"isin": isin, "quoteType": quote_type, "mean": mean_val})
                    n_targets += 1
                    _log(f"[pt] {ticker}: mean={mean_val}")
            else:
                _log(f"[skip-pt] {ticker} type={quote_type}")

        except Exception as e:
            _log(f"[pt-fail] {ticker}: {e}")

    _log(
        f"[fetch_price_targets_from_yahoo] seen={n_seen}, skipped_missing={n_skipped_missing}, "
        f"equity={n_equity}, with_targets={n_targets}"
    )
    return pd.DataFrame(results)

# =========================
# Generate targets from a chosen source
# =========================
def generate_price_targets(
    tickers_df: pd.DataFrame,
    source: Literal["none", "ubs", "yahoo"] = "ubs",
    ubs_file: str = "price_targets.csv",
) -> pd.DataFrame:
    """
    Return a simple price-target table with columns ['isin','mean'].

    Parameters
    ----------
    tickers_df : DataFrame
        Must contain at least ['isin','ticker'] if source='yahoo'.
        For 'ubs' and 'none', 'ticker' is not required.
    source : {'none','ubs','yahoo'}
        - 'none'  : return empty DataFrame with columns ['isin','mean']
        - 'ubs'   : read CSV file and normalize to ['isin','mean']
        - 'yahoo' : fetch via yfinance (equities only) and keep ['isin','mean']
    ubs_file : str
        Path to the UBS CSV file when source='ubs'.

    Returns
    -------
    DataFrame
        Columns: ['isin','mean'] (one row per isin, duplicates collapsed).
    """
    if source == "none":
        _log("[targets] source=none -> empty")
        return pd.DataFrame(columns=["isin", "mean"])

    if source == "ubs":
        df = pd.read_csv(ubs_file)
        # Normalize columns and pick a plausible target column
        cols_lower = {c: c.strip().lower() for c in df.columns}
        df = df.rename(columns=cols_lower)

        candidate_cols = [c for c in ["mean", "price_target", "target_mean", "targetmean"] if c in df.columns]
        if not candidate_cols or "isin" not in df.columns:
            raise ValueError("UBS file must contain 'isin' and a price target column like 'mean' or 'price_target'.")

        target_col = candidate_cols[0]
        out = df[["isin", target_col]].rename(columns={target_col: "mean"}).copy()
        _log(f"[targets/ubs] rows_in={len(df)}, rows_out={len(out)} -> ['isin','mean']")

    elif source == "yahoo":
        raw = fetch_price_targets_from_yahoo(tickers_df)  # ['isin','quoteType','mean']
        out = raw[["isin", "mean"]].copy()
        _log(f"[targets/yahoo] equities_with_targets={len(out)}")

    else:
        raise ValueError("source must be one of {'none','ubs','yahoo'}.")

    out["isin"] = out["isin"].astype(str)
    out = (
        out.dropna(subset=["isin", "mean"])
           .drop_duplicates(subset=["isin"])
           .reset_index(drop=True)
    )
    _log(f"[targets] final unique_isins={len(out)}")
    return out

# =========================
# Internal helpers
# =========================
def _ensure_dataframe(obj) -> pd.DataFrame:
    return obj.to_frame() if isinstance(obj, pd.Series) else obj


def _extract_price_table(raw: pd.DataFrame) -> pd.DataFrame:
    """
    From yfinance's raw download (possibly MultiIndex), extract Adj Close (preferred) or Close.
    """
    if isinstance(raw.columns, pd.MultiIndex):
        lvl0 = raw.columns.get_level_values(0)
        lvl1 = raw.columns.get_level_values(1)
        if "Adj Close" in lvl0:
            tbl = raw["Adj Close"].copy()
        elif "Close" in lvl1:
            tbl = raw.xs("Close", axis=1, level=1).copy()
        else:
            raise RuntimeError("Neither 'Adj Close' nor 'Close' found in downloaded data.")
    else:
        # Single ticker or already flat
        if "Adj Close" in raw.columns:
            tbl = raw[["Adj Close"]].copy()
            tbl.columns = [raw.attrs.get("ticker", "TICKER")]
        elif "Close" in raw.columns:
            tbl = raw[["Close"]].copy()
            tbl.columns = [raw.attrs.get("ticker", "TICKER")]
        else:
            # If caller passed multiple tickers and yfinance flattened already:
            tbl = raw.copy()

    tbl = tbl.sort_index().dropna(how="all")
    tbl.columns = tbl.columns.astype(str)
    return tbl


def _download_prices_by_ticker(
    tickers: Iterable[str],
    start: str,
    end: Optional[str],
    auto_adjust: bool
) -> pd.DataFrame:
    """
    Download price table by ticker (Adj Close preferred).
    Returns a DataFrame indexed by date, columns=tickers.
    """
    tickers = [t for t in tickers if pd.notna(t) and str(t).strip() != ""]
    if not tickers:
        return pd.DataFrame()

    raw = yf.download(
        tickers=tickers, start=start, end=end,
        progress=False, auto_adjust=auto_adjust,
        group_by="ticker", threads=True, multi_level_index=True,
    )
    if isinstance(raw.columns, pd.MultiIndex):
        out = []
        for t in pd.Index(raw.columns.get_level_values(0)).unique():
            sub = raw[t].copy()
            sub.attrs["ticker"] = t
            tbl = _extract_price_table(sub)
            out.append(tbl.rename(columns={tbl.columns[0]: t}))
        prices = pd.concat(out, axis=1).sort_index()
    else:
        prices = _extract_price_table(raw)

    prices = prices[~prices.index.duplicated()].sort_index().dropna(how="all")
    return prices


# =========================
# FX helpers (CHF base)
# =========================
_YF_DIRECT_TO_CHF = {
    "USD": "USDCHF=X",
    "EUR": "EURCHF=X",
    "GBP": "GBPCHF=X",
    "JPY": "JPYCHF=X",
    "AUD": "AUDCHF=X",
    "CAD": "CADCHF=X",
    "HKD": "HKDCHF=X",
}
_YF_INVERSE_FROM_CHF = {
    "USD": "CHFUSD=X",
    "EUR": "CHFEUR=X",
    "GBP": "CHFGBP=X",
    "JPY": "CHFJPY=X",
    "AUD": "CHFAUD=X",
    "CAD": "CHFCAD=X",
    "HKD": "CHFHKD=X",
}


def _fetch_fx_to_chf(
    ccys: Iterable[str],
    start: str,
    end: Optional[str],
    auto_adjust: bool
) -> Dict[str, pd.Series]:
    """
    For each ccy in {USD, EUR, GBP, JPY, AUD, CAD, HKD}, return a Series of FX (CHF per 1 ccy).
    Tries direct pair (e.g., USDCHF=X). If unavailable, fetches inverse (e.g., CHFUSD=X) and inverts.
    """
    fx_needed = {c for c in ccys if c and c != "CHF"}
    if not fx_needed:
        _log("[fx] no FX required (all CHF)")
        return {}

    # Fetch all direct pairs at once where available
    direct_pairs = [_YF_DIRECT_TO_CHF[c] for c in fx_needed if c in _YF_DIRECT_TO_CHF]
    direct_tbl = _download_prices_by_ticker(direct_pairs, start, end, auto_adjust) if direct_pairs else pd.DataFrame()

    fx_map: Dict[str, pd.Series] = {}
    n_direct = 0
    n_inverse = 0

    for c in fx_needed:
        ser = None
        if c in _YF_DIRECT_TO_CHF and (not direct_tbl.empty):
            p = _YF_DIRECT_TO_CHF[c]
            if p in direct_tbl.columns:
                ser = direct_tbl[p]
                n_direct += 1
        if ser is None:
            inv_ticker = _YF_INVERSE_FROM_CHF.get(c)
            if inv_ticker is None:
                raise RuntimeError(f"No FX mapping defined for currency {c}.")
            inv_tbl = _download_prices_by_ticker([inv_ticker], start, end, auto_adjust)
            if inv_ticker not in inv_tbl.columns:
                raise RuntimeError(f"FX pair {inv_ticker} unavailable on Yahoo Finance.")
            ser = 1.0 / inv_tbl[inv_ticker]
            n_inverse += 1

        ser = ser.sort_index().ffill()
        fx_map[c] = ser.rename(f"{c}CHF")

    _log(f"[fx] needed={len(fx_needed)}, direct={n_direct}, inverse={n_inverse}")
    return fx_map


# =========================
# Main: fetch prices and FX → CHF
# =========================
def fetch_prices(
    tickers_df: pd.DataFrame,
    start: str = "2025-01-01",
    end: Optional[str] = None,
    auto_adjust: bool = True,
) -> PriceResult:
    """
    Download Yahoo prices for provided tickers and convert all series to CHF.

    Expected columns in tickers_df: ['ticker','isin','ccy']
      - 'ticker': Yahoo ticker for the instrument (e.g., AAPL, NESN.SW)
      - 'isin' : output column name
      - 'ccy'  : trading currency of the instrument: CHF, USD, EUR, JPY, AUD, GBP, CAD, HKD

    Returns
    -------
    PriceResult(prices_chf, fx_used, raw_prices, historical_returns)
    """
    # Normalize column names to lowercase for internal use
    cols_map = {c: c.lower() for c in tickers_df.columns}
    df = tickers_df.rename(columns=cols_map)

    required = {"ticker", "isin", "ccy"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"tickers_df is missing required columns: {missing}")

    # Filter valid tickers (avoid 'missing<isin>' placeholders)
    valid = df.loc[
        df["ticker"].notna()
        & (df["ticker"].astype(str).str.len() > 0)
        & (~df["ticker"].astype(str).str.startswith("missing"))
    ].copy()

    if valid.empty:
        _log("[fetch_prices] no valid tickers (all missing/empty); returning empty PriceResult")
        empty = pd.DataFrame()
        return PriceResult(prices_chf=empty, fx_used=empty, raw_prices=empty, historical_returns=empty)

    _log(f"[fetch_prices] request tickers={len(valid)} from {start} to {end or 'today'}")

    # 1) Download raw prices by ticker
    raw_by_ticker = _download_prices_by_ticker(valid["ticker"].tolist(), start, end, auto_adjust)

    # Add placeholders for any requested tickers not returned by Yahoo
    missing_tickers = set(tickers_df["ticker"])- set(raw_by_ticker.columns)
    for tkr in sorted(missing_tickers):
        raw_by_ticker[tkr] = 1.0
    if missing_tickers:
        _log(f"[prices] placeholders added (1.0) for missing tickers: {sorted(missing_tickers)}")

    # 2) Map ticker → ISIN
    col_map = (
        pd.DataFrame({"ticker": raw_by_ticker.columns})
        .merge(df[["ticker", "isin", "ccy"]], on="ticker", how="left")
    )
    raw_prices = raw_by_ticker.copy()
    raw_prices.columns = col_map["isin"].tolist()

    _log(f"[prices] rows={len(raw_prices):,}, cols={raw_prices.shape[1]} (ISINs)")

    # 3) FX to CHF
    fx_map = _fetch_fx_to_chf(col_map["ccy"].unique().tolist(), start, end, auto_adjust)

    # 4) fx_used table
    fx_used = pd.DataFrame(index=raw_prices.index, columns=raw_prices.columns, dtype=float)
    n_chf = 0
    for isin, ccy in zip(col_map["isin"], col_map["ccy"]):
        if pd.isna(isin):
            continue
        if str(ccy) == "CHF":
            fx_used[isin] = 1.0
            n_chf += 1
        else:
            ser = fx_map.get(str(ccy))
            if ser is None:
                raise RuntimeError(f"Missing FX series for currency {ccy}.")
            fx_used[isin] = ser.reindex(raw_prices.index).ffill()
    _log(f"[fx_used] CHF-direct={n_chf}, converted={fx_used.shape[1]-n_chf}")

    # 5) CHF prices and returns
    prices_chf = raw_prices * fx_used
    safe_prices = prices_chf.where(prices_chf > 0)
    historical_returns = np.log(safe_prices / safe_prices.shift(1))

    _log(f"[returns] daily rows={len(historical_returns):,}, columns={historical_returns.shape[1]}")

    return PriceResult(
        prices_chf=prices_chf,
        fx_used=fx_used,
        raw_prices=raw_prices,
        historical_returns=historical_returns,
    )




def assign_trading_plan(
        positions: pd.DataFrame,
        allow_trading: str = "stocks",
) -> pd.DataFrame:
    # ---------- this section correctly assigns advise/manage attribute to individual positions
    # Default plan = manage
    positions["plan"] = "manage"

    if allow_trading == 'none':
        positions["plan"] = "manage"
    elif allow_trading == 'stocks':
        positions.loc[(positions["quote_type"] == "EQUITY") & (positions["product"].str[-2:] == "S1"), "plan"] = "advise"
        positions.loc[(positions["product"] == "ib"), "plan"] = "advise"

    elif allow_trading == 'all':
        positions.loc[~positions["product"].astype(str).str.endswith("T1"), "plan"] = "advise"
        positions.loc[(positions["product"] == "ib"), "plan"] = "advise"


    # Liquidity accounts → advise
    positions.loc[positions["group_of_products"] == "Liquidity - Accounts", "plan"] = "advise"

    # prospect investments -> advise
    positions.loc[(positions["product"] == "prospect"), "plan"] = "advise"
    # leverage -> advise
    positions.loc[(positions["product"] == "levarage"), "plan"] = "advise"

    return positions


