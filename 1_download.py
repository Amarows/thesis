import sys, time, threading
import pandas as pd

sys.path.insert(0, "src_api_ibkr")
from ibkr_tws_api           import TradingApp
from historical_data_toolkit import download_close_series_save
from ibkr_news_toolkit       import IBKRNewsToolkit, IBKRConnectionConfig

# config
PORT           = 7496        # 7496 paper | 7497 live
CLIENT_PRICES  = 6
CLIENT_NEWS    = 7
NEWS_START     = "2026-02-01"
NEWS_END       = "2026-02-28"
NEWS_PROVIDERS = ["BZ"]
PRICE_DURATION = "90 D"
PRICE_BAR      = "1 hour"
SYMBOLS        = pd.read_csv("data/portfolio.csv")["Symbol"].tolist()


def connect(port, client_id):
    app = TradingApp()
    app.connect("127.0.0.1", port, clientId=client_id)
    threading.Thread(target=app.run, daemon=True).start()
    for _ in range(50):
        if isinstance(app.nextOrderId, int):
            print(f"Connected (port={port}, clientId={client_id})")
            return app
        time.sleep(0.1)
    raise RuntimeError("Timed out waiting for nextValidId.")


def download_prices():
    app = connect(PORT, CLIENT_PRICES)
    series = download_close_series_save(app, SYMBOLS, duration=PRICE_DURATION, bar=PRICE_BAR, what="TRADES", useRTH=1, outdir="data")
    print(f"Prices done: {len(series)} bars")
    return series


def download_news():
    toolkit = IBKRNewsToolkit(cfg=IBKRConnectionConfig(host="127.0.0.1", port=PORT, client_id=CLIENT_NEWS), data_dir="data", currency="USD")
    try:
        toolkit.connect()
        toolkit.run(symbols=SYMBOLS, providers=NEWS_PROVIDERS, start_date=NEWS_START, end_date=NEWS_END, top_n=10_000, force_refresh=False, include_article_text=True)
        print(f"News done: {NEWS_START} → {NEWS_END}")
    finally:
        toolkit.disconnect()
