import time
import threading
from ibkr_tws_api import TradingApp

#=============================================== connect #=============================================
app = TradingApp()
# Your Gateway shows port 7496 (paper) and Master Client ID = 5, so:
app.connect("127.0.0.1", 7496, clientId=5)

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
from load_prospects import load_prospect_symbols

list_of_prospects=load_prospect_symbols('data/algo_prospects.csv')

from src_algo_trader.data_layer import download_close_series_save

# ---- Example usage ----
if __name__ == "__main__":
    list_of_prospects = ['BTC', 'ETH']
    series_long = download_close_series_save(
        app,
        list_of_prospects,
        duration="20 D",
        bar="1 min",
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