



SYMBOLS = ['MCD']


def download_prices():
    app = connect(PORT, CLIENT_PRICES)
    series = download_close_series_save(app, SYMBOLS, duration=PRICE_DURATION, bar=PRICE_BAR, what="TRADES", useRTH=1, outdir="data")
    print(f"Prices done: {len(series)} bars")
    return series
download_prices()