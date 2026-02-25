from __future__ import annotations
import time
import threading
from ibkr_tws_api import TradingApp

#=============================================== connect to IB #=============================================
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

#=============================================== list of single stocks =================================================

import pandas as pd
list_of_prospects = pd.read_csv("data/portfolio.csv")["Symbol"].tolist()


#=============================================== download historical data #=============================================



from historical_data_toolkit import download_close_series_save

# ---- Example usage ----
if __name__ == "__main__":

    series_long = download_close_series_save(
        app,
        list_of_prospects,
        duration="90 D",
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


#=============================================== download news as CLIENT!!! #========================================

from src_api_ibkr.ibkr_news_toolkit import IBKRNewsToolkit, IBKRConnectionConfig

if __name__ == "__main__":
    symbols = list_of_prospects  # Using the first 3 symbols from the portfolio

    # Put here the provider codes that you verified return headlines in your test.
    providers = ["BZ"]#, "BRFG", "BRFUPDN", "DJNL", "DJ-RT", "FLY"]

    start_date = "2026-02-01"
    end_date = "2026-02-28"

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
            top_n=10000,
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

# =============================================== Import news #=============================================
from market_data_processor_toolkit import load_market_data

prices, news = load_market_data("data")


# =============================================== Calculate Sentiment #=============================================

from news_sentiment_toolkit  import calculate_vader_sentiment, aggregate_sentiment, openai_sentiment_hint

if __name__ == "__main__":
    if news.empty:
        print("No news data found to process.")
    else:
        # 2. Calculate Sentiment
        news = calculate_vader_sentiment(news)

        # 3. Aggregate
        daily_sentiment = aggregate_sentiment(news, freq='D')

        print("\n--- Sentiment Results (First 5) ---")
        print(news[['headline', 'sentiment_score']].head())

        if daily_sentiment is not None:
            print("\n--- Daily Aggregate Sentiment ---")
            print(daily_sentiment)

        # 4. Show OpenAI hint
        #print("\n--- How to use ChatGPT for Sentiment ---")
        # openai_sentiment_hint()

        # 5. Suggestion for next steps
        print("\nSuggestion: You can now join 'daily_sentiment' with 'prices' to see correlations.")

#olama