from __future__ import annotations

import os
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


# -----------------------------
# Helpers
# -----------------------------

def _sanitize_filename(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s.strip())


def _to_utc_day_start(d: str) -> datetime:
    dd = datetime.strptime(d, "%Y-%m-%d").date()
    return datetime(dd.year, dd.month, dd.day, 0, 0, 0, tzinfo=timezone.utc)


def _to_utc_day_end(d: str) -> datetime:
    dd = datetime.strptime(d, "%Y-%m-%d").date()
    return datetime(dd.year, dd.month, dd.day, 23, 59, 59, tzinfo=timezone.utc)


def parse_ib_time_utc(s: str) -> Optional[datetime]:
    # Your IBKR returns: "2025-12-18 15:00:16.0"
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def stock_contract(symbol: str, currency: str = "USD") -> Contract:
    c = Contract()
    c.symbol = symbol
    c.secType = "STK"
    c.exchange = "SMART"
    c.currency = currency
    return c


# -----------------------------
# Connection config
# -----------------------------

@dataclass(frozen=True)
class IBKRConnectionConfig:
    host: str = "127.0.0.1"
    port: int = 7496
    client_id: int = 7  # keep the client id you validated works fast/stable


# -----------------------------
# Low-level app (IBKR)
# -----------------------------

class _IBKRBZApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.ready = threading.Event()

        self._conid_event = threading.Event()
        self._conid_value: Optional[int] = None

        self._news_event = threading.Event()
        self._news_rows: List[Tuple[str, str, str, str]] = []

        self._req_id = 1000

    def _next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def nextValidId(self, orderId: int):
        self.ready.set()

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"[IB ERROR] reqId={reqId} code={errorCode} msg={errorString}")

    def contractDetails(self, reqId, contractDetails):
        if self._conid_value is None:
            self._conid_value = int(contractDetails.contract.conId)

    def contractDetailsEnd(self, reqId):
        self._conid_event.set()

    def historicalNews(self, reqId, timeStr, providerCode, articleId, headline):
        self._news_rows.append((timeStr, providerCode, articleId, headline))

    def historicalNewsEnd(self, reqId, hasMore):
        self._news_event.set()

    def resolve_conid(self, contract: Contract, timeout: int = 15) -> Optional[int]:
        self._conid_value = None
        self._conid_event.clear()

        req_id = self._next_req_id()
        self.reqContractDetails(req_id, contract)

        if not self._conid_event.wait(timeout=timeout):
            return None
        return self._conid_value

    def fetch_latest_bz(self, conId: int, total_results: int = 300, timeout: int = 25) -> List[Tuple[str, str, str, str]]:
        """
        Proven working call pattern:
        reqHistoricalNews(conId, providerCodes="BZ", startDateTime="", endDateTime="").
        """
        self._news_rows = []
        self._news_event.clear()

        total_results = int(min(max(total_results, 1), 300))
        req_id = self._next_req_id()

        self.reqHistoricalNews(req_id, int(conId), "BZ", "", "", total_results, [])

        if not self._news_event.wait(timeout=timeout):
            return []
        return self._news_rows


# -----------------------------
# Toolkit
# -----------------------------

class IBKRBenzingaNewsToolkit:
    """
    Toolkit responsibilities
    - Connect/disconnect to IB Gateway
    - For each symbol: resolve conId, fetch latest 300 BZ headlines, filter by date range
    - Cache to disk in data/ (CSV per symbol+date window)
    - Load from disk if file exists (unless force_refresh=True)
    """

    def __init__(
        self,
        cfg: IBKRConnectionConfig,
        data_dir: str = "data",
        currency: str = "USD",
        sleep_sec: float = 0.20,
    ):
        self.cfg = cfg
        self.data_dir = data_dir
        self.currency = currency
        self.sleep_sec = float(sleep_sec)

        os.makedirs(self.data_dir, exist_ok=True)

        self._app = _IBKRBZApp()
        self._thread: Optional[threading.Thread] = None

    def connect(self) -> None:
        print("[INFO] Connecting ...")
        self._app.connect(self.cfg.host, int(self.cfg.port), clientId=int(self.cfg.client_id))
        self._thread = threading.Thread(target=self._app.run, daemon=True)
        self._thread.start()

        if not self._app.ready.wait(15):
            raise RuntimeError("IBKR API not ready (no nextValidId).")
        print("[OK] Connected and API ready.")

    def disconnect(self) -> None:
        try:
            self._app.disconnect()
        except Exception:
            pass
        time.sleep(1)

    def _cache_path(self, symbol: str, start_date: str, end_date: str) -> str:
        sym = _sanitize_filename(symbol)
        return os.path.join(self.data_dir, f"{sym}_BZ_{start_date}_to_{end_date}.csv")

    def load_or_fetch_symbol(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        *,
        top_n: int = 10,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Returns a DataFrame (already filtered to date window) with columns:
        symbol, conId, time_utc, provider, article_id, headline
        """
        path = self._cache_path(symbol, start_date, end_date)

        if (not force_refresh) and os.path.exists(path):
            df = pd.read_csv(path)
            if len(df) > 0:
                return df
            # empty-cache poisoning guard: fall through and re-fetch

        start_dt = _to_utc_day_start(start_date)
        end_dt = _to_utc_day_end(end_date)

        conId = self._app.resolve_conid(stock_contract(symbol, currency=self.currency), timeout=15)
        if not conId:
            raise RuntimeError(f"Could not resolve conId for symbol={symbol}.")

        raw = self._app.fetch_latest_bz(conId, total_results=300, timeout=25)

        rows = []
        for (timeStr, providerCode, articleId, headline) in raw:
            dt = parse_ib_time_utc(timeStr)
            if dt is None:
                continue
            if start_dt <= dt <= end_dt:
                rows.append(
                    {
                        "symbol": symbol,
                        "conId": int(conId),
                        "time_utc": dt.isoformat(),
                        "provider": str(providerCode),
                        "article_id": str(articleId),
                        "headline": str(headline),
                    }
                )

        df = pd.DataFrame(rows)

        if not df.empty:
            # Deduplicate and sort descending time
            df = df.drop_duplicates(subset=["time_utc", "article_id"]).copy()
            df["time_utc_dt"] = pd.to_datetime(df["time_utc"], utc=True, errors="coerce")
            df = df.dropna(subset=["time_utc_dt"]).sort_values("time_utc_dt", ascending=False)
            df = df.drop(columns=["time_utc_dt"]).reset_index(drop=True)

            # Keep top_n if requested (the file will contain only top_n filtered rows)
            df = df.head(int(top_n)).reset_index(drop=True)

        df.to_csv(path, index=False)
        time.sleep(self.sleep_sec)
        return df

    def run_for_symbols(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        *,
        top_n: int = 10,
        force_refresh: bool = False,
    ) -> Dict[str, pd.DataFrame]:
        out: Dict[str, pd.DataFrame] = {}
        for sym in symbols:
            df = self.load_or_fetch_symbol(
                sym,
                start_date,
                end_date,
                top_n=top_n,
                force_refresh=force_refresh,
            )
            out[sym] = df
            print(f"{sym}: {len(df)} rows saved/loaded")
        return out


