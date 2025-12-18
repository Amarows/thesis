import threading
import time
from datetime import datetime, timezone
from typing import List, Tuple, Optional

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


def parse_ib_time_utc(s: str) -> Optional[datetime]:
    # Handle the formats you observed plus common IB variants
    if s is None:
        return None
    s = str(s).strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S.%f",   # 2025-12-18 15:00:16.0
        "%Y-%m-%d %H:%M:%S",
        "%Y%m%d %H:%M:%S.%f",
        "%Y%m%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return None


class ProviderDirectTest(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.ready = threading.Event()

        self._conid_event = threading.Event()
        self._conid_value: Optional[int] = None

        self._news_event = threading.Event()
        self._news_rows: List[Tuple[str, str, str, str]] = []
        self._last_news_req_id: Optional[int] = None

        self._req_id = 1000

    def _next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    # ---- connection
    def nextValidId(self, orderId: int):
        print(f"[OK] API ready. nextValidId={orderId}")
        self.ready.set()

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"[IB ERROR] reqId={reqId} code={errorCode} msg={errorString}")

        # If the error relates to the current news request, unblock waits
        if self._last_news_req_id is not None and int(reqId) == int(self._last_news_req_id):
            self._news_event.set()

    # ---- conId
    def contractDetails(self, reqId, contractDetails):
        if self._conid_value is None:
            self._conid_value = int(contractDetails.contract.conId)

    def contractDetailsEnd(self, reqId):
        self._conid_event.set()

    # ---- historical news
    def historicalNews(self, reqId, timeStr, providerCode, articleId, headline):
        self._news_rows.append((str(timeStr), str(providerCode), str(articleId), str(headline)))

    def historicalNewsEnd(self, reqId, hasMore):
        self._news_event.set()

    # ---- helpers
    def resolve_conid(self, contract: Contract, timeout: int = 15) -> Optional[int]:
        self._conid_value = None
        self._conid_event.clear()

        req_id = self._next_req_id()
        self.reqContractDetails(req_id, contract)

        if not self._conid_event.wait(timeout=timeout):
            return None
        return self._conid_value

    def fetch_top_headlines(self, conId: int, provider_code: str, top_n: int = 10, timeout: int = 20):
        self._news_rows = []
        self._news_event.clear()

        req_id = self._next_req_id()
        self._last_news_req_id = req_id

        # Working call pattern (like your BZ script)
        self.reqHistoricalNews(req_id, int(conId), provider_code, "", "", int(top_n), [])

        ok = self._news_event.wait(timeout=timeout)
        if not ok:
            return []

        return self._news_rows[:top_n]


def stock_contract(symbol: str) -> Contract:
    c = Contract()
    c.symbol = symbol
    c.secType = "STK"
    c.exchange = "SMART"
    c.currency = "USD"
    return c


def main():
    host = "127.0.0.1"
    port = 7496
    client_id = 7  # use the same known-good ID for news

    test_symbol = "AAPL"
    top_n = 10

    # Provider codes exactly as shown in your Gateway screenshot
    provider_codes = [
        "BZ",
        "BRFUPDN",
        "BRFG",
        "DJ-N",
        "DJNL",
        "DJ-RTA",
        "DJ-RTE",
        "DJ-RTG",
        "DJ-RT",
        "FLY",
    ]

    app = ProviderDirectTest()
    print("[INFO] Connecting ...")
    app.connect(host, port, clientId=client_id)
    threading.Thread(target=app.run, daemon=True).start()

    if not app.ready.wait(10):
        print("[FAIL] No nextValidId – connection not ready (clientId conflict or Gateway not accepting API).")
        app.disconnect()
        return

    print(f"[INFO] Resolving conId for {test_symbol} ...")
    conId = app.resolve_conid(stock_contract(test_symbol), timeout=15)
    if not conId:
        print("[FAIL] Could not resolve conId.")
        app.disconnect()
        return
    print(f"[OK] {test_symbol} conId={conId}")

    for code in provider_codes:
        print(f"\n=== Testing provider {code} ===")
        rows = app.fetch_top_headlines(conId, code, top_n=top_n, timeout=20)

        if not rows:
            print("No headlines returned (likely not entitled, or no items). Check any IB ERROR lines above.")
            continue

        for (timeStr, providerCode, articleId, headline) in rows:
            dt = parse_ib_time_utc(timeStr)
            ts = dt.isoformat() if dt else timeStr
            print(f"{ts} | {providerCode} | {articleId} | {headline}")

        time.sleep(0.25)

    app.disconnect()
    time.sleep(1)


if __name__ == "__main__":
    main()
