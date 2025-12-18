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
    """
    Handles the formats commonly seen in IBKR news callbacks.
    Your current Benzinga timeStr example: "2025-12-18 15:00:16.0"
    """
    if s is None:
        return None
    s = str(s).strip()

    fmts = (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y%m%d %H:%M:%S.%f",
        "%Y%m%d %H:%M:%S",
    )
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            pass
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
    client_id: int = 7


# -----------------------------
# Low-level app (IBKR)
# -----------------------------

class _IBKRNewsApp(EWrapper, EClient):
    """
    Supports:
    - conId resolution
    - historical headlines (reqHistoricalNews)
    - article body retrieval (reqNewsArticle)
    """
    def __init__(self):
        EClient.__init__(self, self)

        self.ready = threading.Event()

        self._conid_event = threading.Event()
        self._conid_value: Optional[int] = None

        self._news_event = threading.Event()
        self._news_rows: List[Tuple[str, str, str, str]] = []  # (timeStr, providerCode, articleId, headline)
        self._last_news_req_id: Optional[int] = None

        self._article_event = threading.Event()
        self._article_payload: Optional[Tuple[int, str]] = None  # (articleType, articleText)
        self._last_article_req_id: Optional[int] = None

        self._req_id = 1000

    def _next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def nextValidId(self, orderId: int):
        self.ready.set()

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"[IB ERROR] reqId={reqId} code={errorCode} msg={errorString}")

        # Unblock waits if this error pertains to current requests
        if self._last_news_req_id is not None and int(reqId) == int(self._last_news_req_id):
            self._news_event.set()
        if self._last_article_req_id is not None and int(reqId) == int(self._last_article_req_id):
            self._article_event.set()

    # ---- conId
    def contractDetails(self, reqId, contractDetails):
        if self._conid_value is None:
            self._conid_value = int(contractDetails.contract.conId)

    def contractDetailsEnd(self, reqId):
        self._conid_event.set()

    def resolve_conid(self, contract: Contract, timeout: int = 15) -> Optional[int]:
        self._conid_value = None
        self._conid_event.clear()

        req_id = self._next_req_id()
        self.reqContractDetails(req_id, contract)

        if not self._conid_event.wait(timeout=timeout):
            return None
        return self._conid_value

    # ---- historical headlines
    def historicalNews(self, reqId, timeStr, providerCode, articleId, headline):
        self._news_rows.append((str(timeStr), str(providerCode), str(articleId), str(headline)))

    def historicalNewsEnd(self, reqId, hasMore):
        self._news_event.set()

    def fetch_latest_headlines(
        self,
        conId: int,
        provider_code: str,
        total_results: int = 300,
        timeout: int = 25,
    ) -> List[Tuple[str, str, str, str]]:
        self._news_rows = []
        self._news_event.clear()

        total_results = int(min(max(total_results, 1), 300))
        req_id = self._next_req_id()
        self._last_news_req_id = req_id

        # Proven working pattern: start="", end=""
        self.reqHistoricalNews(req_id, int(conId), provider_code, "", "", total_results, [])

        if not self._news_event.wait(timeout=timeout):
            return []
        return self._news_rows

    # ---- article body
    def newsArticle(self, requestId: int, articleType: int, articleText: str):
        self._article_payload = (int(articleType), str(articleText))
        self._article_event.set()

    def fetch_article_body(
        self,
        provider_code: str,
        article_id: str,
        timeout: int = 20,
    ) -> Optional[Tuple[int, str]]:
        """
        Attempts to retrieve full article content.
        articleType is a provider-defined format indicator (often plain vs html/xml).
        """
        self._article_payload = None
        self._article_event.clear()

        req_id = self._next_req_id()
        self._last_article_req_id = req_id

        self.reqNewsArticle(req_id, provider_code, str(article_id), [])

        if not self._article_event.wait(timeout=timeout):
            return None
        return self._article_payload


# -----------------------------
# Toolkit
# -----------------------------

class IBKRNewsToolkit:
    """
    Multi-provider news toolkit.

    For each (symbol, provider):
    - resolve conId
    - fetch latest headlines (up to 300)
    - parse timestamp, filter by [start_date, end_date]
    - optionally fetch article bodies using reqNewsArticle
    - cache to CSV per (symbol, provider, date window)
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

        self._app = _IBKRNewsApp()
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

    def _cache_path(self, symbol: str, provider: str, start_date: str, end_date: str) -> str:
        sym = _sanitize_filename(symbol)
        prov = _sanitize_filename(provider)
        return os.path.join(self.data_dir, f"{sym}_{prov}_{start_date}_to_{end_date}.csv")

    def load_or_fetch(
        self,
        symbol: str,
        provider: str,
        start_date: str,
        end_date: str,
        *,
        top_n: int = 10,
        force_refresh: bool = False,
        include_article_text: bool = False,
        article_timeout: int = 20,
    ) -> pd.DataFrame:
        path = self._cache_path(symbol, provider, start_date, end_date)

        if (not force_refresh) and os.path.exists(path):
            df = pd.read_csv(path)
            if len(df) > 0:
                return df

        start_dt = _to_utc_day_start(start_date)
        end_dt = _to_utc_day_end(end_date)

        conId = self._app.resolve_conid(stock_contract(symbol, currency=self.currency), timeout=15)
        if not conId:
            raise RuntimeError(f"Could not resolve conId for symbol={symbol}.")

        raw = self._app.fetch_latest_headlines(conId, provider, total_results=300, timeout=25)

        rows: List[dict] = []
        for (timeStr, providerCode, articleId, headline) in raw:
            dt = parse_ib_time_utc(timeStr)
            if dt is None:
                continue
            if not (start_dt <= dt <= end_dt):
                continue

            article_type = None
            article_text = None

            if include_article_text:
                payload = self._app.fetch_article_body(provider_code=provider, article_id=articleId, timeout=article_timeout)
                if payload is not None:
                    article_type, article_text = payload

                time.sleep(self.sleep_sec)

            rows.append(
                {
                    "symbol": symbol,
                    "conId": int(conId),
                    "provider": str(providerCode),
                    "article_id": str(articleId),
                    "time_utc": dt.isoformat(),
                    "headline": str(headline),
                    "article_type": article_type,
                    "article_text": article_text,
                }
            )

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.drop_duplicates(subset=["time_utc", "provider", "article_id"]).copy()
            df["time_utc_dt"] = pd.to_datetime(df["time_utc"], utc=True, errors="coerce")
            df = df.dropna(subset=["time_utc_dt"]).sort_values("time_utc_dt", ascending=False)
            df = df.drop(columns=["time_utc_dt"]).reset_index(drop=True)
            df = df.head(int(top_n)).reset_index(drop=True)

        df.to_csv(path, index=False)
        time.sleep(self.sleep_sec)
        return df

    def run(
        self,
        symbols: List[str],
        providers: List[str],
        start_date: str,
        end_date: str,
        *,
        top_n: int = 10,
        force_refresh: bool = False,
        include_article_text: bool = False,
    ) -> Dict[Tuple[str, str], pd.DataFrame]:
        out: Dict[Tuple[str, str], pd.DataFrame] = {}
        for sym in symbols:
            for prov in providers:
                df = self.load_or_fetch(
                    sym, prov, start_date, end_date,
                    top_n=top_n,
                    force_refresh=force_refresh,
                    include_article_text=include_article_text,
                )
                out[(sym, prov)] = df
                print(f"{sym} {prov}: {len(df)} rows saved/loaded")
        return out


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "NVDA"]

    # Put here the provider codes that you verified return headlines in your test.
    providers = ["BZ", "DJ-RT", "FLY"]

    start_date = "2025-12-15"
    end_date = "2025-12-18"

    cfg = IBKRConnectionConfig(host="127.0.0.1", port=7496, client_id=7)

    toolkit = IBKRNewsToolkit(cfg=cfg, data_dir="data", currency="USD")

    try:
        toolkit.connect()

        # 1) Headlines only (fast)
        toolkit.run(
            symbols=symbols,
            providers=providers,
            start_date=start_date,
            end_date=end_date,
            top_n=200,
            force_refresh=False,
            include_article_text=True,
        )

        # 2) Headlines + article bodies (slow; many providers may return empty/denied)
        # toolkit.run(
        #     symbols=symbols,
        #     providers=providers,
        #     start_date=start_date,
        #     end_date=end_date,
        #     top_n=10,
        #     force_refresh=True,
        #     include_article_text=True,
        # )

    finally:
        toolkit.disconnect()
