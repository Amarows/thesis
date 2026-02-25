import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, "toolkits")
from market_data_processor_toolkit import load_market_data

prices, news = load_market_data("data")

# prices
p = prices.reset_index()
p["date"] = p["time"].dt.normalize()
stats = p.groupby("symbol").agg(first=("date","min"), last=("date","max"), days=("date","nunique"), bars=("close","count"))
print(f"\n=== PRICES: {len(stats)} symbols, {stats['bars'].sum():,} bars ===")
print(stats.to_string())

# news
n = news.reset_index()
n["date"] = n["time"].dt.normalize()
stats = n.groupby("symbol").agg(first=("date","min"), last=("date","max"), days=("date","nunique"), articles=("headline","count"), providers=("provider", lambda s: ", ".join(sorted(s.unique()))))
print(f"\n=== NEWS: {len(stats)} symbols, {stats['articles'].sum():,} articles ===")
print(stats.to_string())

# chart
daily = prices.reset_index().assign(date=lambda df: df["time"].dt.normalize()).groupby(["symbol","date"])["close"].last().unstack("symbol")
norm = daily / daily.iloc[0] * 100
fig, ax = plt.subplots(figsize=(12, 6))
norm.plot(ax=ax, linewidth=1)
ax.set(title="Normalised Daily Close (rebased to 100)", xlabel="Date", ylabel="Index")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left", ncol=4, fontsize=8)
plt.tight_layout()
plt.show()
