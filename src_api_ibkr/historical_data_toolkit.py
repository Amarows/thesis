import os
import re
import time
import pandas as pd
from ibkr_tws_api import TradingApp  # your IB client

def _sanitize_filename(s: str) -> str:
    """Make a safe filename from a symbol (handles spaces, slashes, etc.)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s.strip())

def download_close_series_save(
    app: TradingApp,
    symbols,
    *,
    duration="7 D",
    bar="1 min",
    what="TRADES",
    useRTH=1,
    outdir="data",
    req_base=2000,
    sleep_sec=0.25,
):
    """
    Downloads close/volume for each symbol and saves CSVs.
    Returns a single MultiIndex Series of close prices indexed by [symbol, time].
    """
    os.makedirs(outdir, exist_ok=True)
    series_list = []
    names = []

    for i, sym in enumerate(symbols, start=1):
        print(f"[{i}/{len(symbols)}] {sym}  ({duration}, {bar}, {what}, RTH={useRTH})")
        contract = TradingApp.get_contract(sym)

        df = app.get_historical_data(
            reqId=req_base + i,
            contract=contract,
            endDateTime="",          # now (server time)
            durationStr=duration,
            barSize=bar,
            whatToShow=what,
            useRTH=useRTH,
        )

        if df is None or df.empty:
            print(f"[WARN] No data for {sym}")
            time.sleep(sleep_sec)
            continue

        # Ensure index and columns exist
        df = df.sort_index()
        df.index.name = "time"
        cols = {c.lower(): c for c in df.columns}
        # Keep only close & volume for the CSV
        keep = []
        if "close" in cols: keep.append(cols["close"])
        if "volume" in cols: keep.append(cols["volume"])
        if not keep:
            # If no close provided (unlikely with TRADES), skip symbol
            print(f"[WARN] Missing 'close' for {sym}, skipping.")
            time.sleep(sleep_sec)
            continue

        # Save per-symbol CSV
        fname = f"{_sanitize_filename(sym)}_{bar.replace(' ', '')}_{duration.replace(' ', '')}.csv"
        out_path = os.path.join(outdir, fname)
        df[keep].to_csv(out_path, float_format="%.6f")
        print(f"Saved {out_path}  ({len(df):,} rows)")

        # Build Series of closes for concatenation
        s = df[cols["close"]].copy()
        s.name = sym
        series_list.append(s)
        names.append(sym)

        time.sleep(sleep_sec)  # gentle pacing

    if not series_list:
        # Return an empty, well-typed Series with MultiIndex
        mi = pd.MultiIndex.from_arrays([[], []], names=["symbol", "time"])
        return pd.Series([], index=mi, dtype="float64")

    # Combine into one MultiIndex Series [symbol, time]
    series_all = pd.concat(series_list, keys=names, names=["symbol", "time"])
    return series_all



