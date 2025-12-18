from __future__ import annotations
import time
import threading
from ibkr_tws_api import TradingApp

#=============================================== connect #=============================================
app = TradingApp()
# Your Gateway shows port 7496 (paper) and Master Client ID = 5, so:
app.connect("127.0.0.1", 7496, clientId=6)

# Start the network loop
threading.Thread(target=app.run, daemon=True).start()

# Wait for nextValidId to arrive
for _ in range(50):
    if isinstance(app.nextOrderId, int):
        print("Connected to IBKR API.")
        break
    time.sleep(0.1)
else:
    raise RuntimeError("Failed to receive nextValidId from IBKR.")

#=============================================== download historical data #=============================================

list_of_prospects=['AAPL','MSFT', 'NVDA','BTC', 'ETH']

from historical_data_toolkit import download_close_series_save

# ---- Example usage ----
if __name__ == "__main__":

    series_long = download_close_series_save(
        app,
        list_of_prospects,
        duration="20 D",
        bar="1 hour",
        what="TRADES",
        useRTH=1,
        outdir="data",
    )
    print(series_long.tail(10))         # MultiIndex Series [symbol, time] -> close

# If you ever need a wide DataFrame:
series_wide = series_long.unstack(level=0)

import matplotlib.pyplot as plt
wide_norm = series_wide / series_wide.iloc[0] * 100  # rebased to 100
wide_norm.plot(figsize=(10, 6), title="Normalized Close Prices (rebased to 100)")
plt.xlabel("Time")
plt.ylabel("Index (Start = 100)")
plt.grid(True)
plt.tight_layout()
plt.show()


#=============================================== download news #=============================================

from ibkr_news_toolkit import IBKRConnectionConfig, IBKRBenzingaNewsToolkit


if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "NVDA"]
    start_date = "2025-12-15"
    end_date = "2025-12-18"

    cfg = IBKRConnectionConfig(host="127.0.0.1", port=7496, client_id=7)

    toolkit = IBKRBenzingaNewsToolkit(cfg=cfg, data_dir="data", currency="USD")

    try:
        toolkit.connect()
        results = toolkit.run_for_symbols(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            top_n=200,
            force_refresh=True,
        )

        # Print each symbol’s top headlines
        for sym, df in results.items():
            print(f"\n{sym} – top headlines in range {start_date} to {end_date}")
            if df.empty:
                print("(no headlines in window)")
            else:
                for _, row in df.iterrows():
                    print(row["time_utc"], row["headline"])

    finally:
        toolkit.disconnect()