import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, "toolkits")

pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth',10000)


#================================ Load and describe offline data =============================================

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


#================================ select events =============================================

from event_selection_toolkit import identify_shocks

candidates = identify_shocks(prices, news)

if not candidates.empty:
    print(f"=== CANDIDATE POOL: {len(candidates)} stock-day-news triples ===\n")
    pd.set_option("display.max_colwidth", 80)
    pd.set_option("display.width", 200)
    print(candidates[
              ["symbol", "event_date", "daily_return", "spx_return", "rel_abnormal_ret", "return_zscore", "rel_zscore",
               "shock_direction", "article_count"]])
    pd.reset_option("display.max_colwidth")
    pd.reset_option("display.width")
else:
    print("\nNo candidates found. Consider re-downloading prices with a longer window.")


#================================ SC_total construction + §2.3 block assignment =============================================

from event_selection_toolkit import compute_sc_total, assign_blocks, print_block_tables

if not candidates.empty:
    portfolio = pd.read_csv("data/portfolio.csv")

    # Compute SC_total and auxiliary fields (event_type, market_regime) for all candidates
    candidates_sc = compute_sc_total(candidates, news, data_dir="data")

    # §2.3: select best triple per stock, assign intensity tiers, partition into 3 blocks of 12
    blocks = assign_blocks(candidates_sc, portfolio)

    # §2.4: print selection summary tables
    print_block_tables(blocks)
else:
    print("Skipping SC_total and block assignment — no candidates available.")















