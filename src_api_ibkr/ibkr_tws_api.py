import threading
from typing import Dict, Optional
import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import BarData

class TradingApp(EClient, EWrapper):
    def __init__(self) -> None:
        EClient.__init__(self, self)
        self.data: Dict[int, pd.DataFrame] = {}
        self._done: Dict[int, threading.Event] = {}
        self.nextOrderId: Optional[int] = None

    # --- Connection / Errors ---
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"[IB ERROR] reqId={reqId} code={errorCode} msg={errorString}")
        if advancedOrderRejectJson:
            print(f"[AdvancedReject] {advancedOrderRejectJson}")

    def nextValidId(self, orderId: int):
        print("Connected. NextValidId:", orderId)
        self.nextOrderId = orderId  # IMPORTANT: set it!

    # --- Historical Data API ---
    def get_historical_data(
        self,
        reqId: int,
        contract: Contract,
        endDateTime: str = "",      # "" = now (server time)
        durationStr: str = "1 D",   # e.g., "1 D", "2 W", "1 M", "1 Y"
        barSize: str = "1 min",     # e.g., "1 min", "5 mins", "1 day"
        whatToShow: str = "TRADES", # TRADES/MIDPOINT/BID/ASK
        useRTH: int = 0,
    ) -> pd.DataFrame:

        self.data[reqId] = pd.DataFrame(columns=["time", "close", "volume"])
        self.data[reqId].set_index("time", inplace=True)
        self._done[reqId] = threading.Event()

        self.reqHistoricalData(
            reqId=reqId,
            contract=contract,
            endDateTime=endDateTime,
            durationStr=durationStr,
            barSizeSetting=barSize,
            whatToShow=whatToShow,
            useRTH=useRTH,
            formatDate=2,            # human-readable timestamps
            keepUpToDate=False,
            chartOptions=[],
        )

        # Wait until historicalDataEnd fires, with a sensible timeout
        if not self._done[reqId].wait(timeout=30):
            print(f"[WARN] Historical data request {reqId} timed out.")
        return self.data[reqId].sort_index()

    def historicalData(self, reqId: int, bar: BarData) -> None:
        df = self.data[reqId]
        raw = str(bar.date)

        # Parse IB historical bar date robustly
        # 1) Daily bars: 'YYYYMMDD'
        # 2) Intraday: 'YYYY-MM-DD HH:MM:SS' (or similar)
        # 3) Epoch seconds (10+ digits)
        try:
            if raw.isdigit():
                if len(raw) == 8:
                    # 'YYYYMMDD' -> treat as midnight UTC for a clean index
                    ts = pd.to_datetime(raw, format="%Y%m%d", utc=True)
                else:
                    # epoch seconds
                    ts = pd.to_datetime(int(raw), unit="s", utc=True)
            else:
                # datetime string
                ts = pd.to_datetime(raw, utc=True, errors="raise")
        except Exception as e:
            print(f"[WARN] Could not parse timestamp {raw!r}: {e}; skipping bar")
            return

        # Keep only close & volume
        df.loc[ts, ["close", "volume"]] = [bar.close, bar.volume]

    def historicalDataEnd(self, reqId: int, start: str, end: str) -> None:
        # Signal that we’re done receiving bars for this request
        ev = self._done.get(reqId)
        if ev:
            ev.set()

    # --- Helpers ---
    @staticmethod
    def get_contract(symbol: str) -> Contract:
        c = Contract()
        c.symbol = symbol
        c.secType = "STK"
        c.exchange = "SMART"
        c.primaryExchange = "NASDAQ"  # for NVDA; use "NYSE"/"ARCA" etc. as needed
        c.currency = "USD"
        return c

    def place_order(self, contract: Contract, action: str, order_type: str, quantity: int) -> None:
        if self.nextOrderId is None:
            raise RuntimeError("Not connected yet; nextOrderId is None.")
        order = Order()
        order.action = action
        order.orderType = order_type
        order.totalQuantity = quantity
        self.placeOrder(self.nextOrderId, contract, order)
        self.nextOrderId += 1
        print("Order placed")
