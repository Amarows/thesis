import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Global pandas display setup (retain behavior for normal cases)
pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 10000)


def _add_toolkits_to_path():
    """Ensure toolkits directory is importable regardless of CWD."""
    try:
        toolkits_dir = Path(__file__).resolve().parent / "toolkits"
        sys.path.insert(0, str(toolkits_dir))
    except Exception:
        # Fallback to previous behavior if __file__ is not available
        sys.path.insert(0, "toolkits")


def main():
    # Set up import path for toolkits, then import
    _add_toolkits_to_path()
    from market_data_processor_toolkit import load_market_data
    from event_selection_toolkit import (
        identify_shocks,
        compute_sc_total,
        assign_blocks,
        print_block_tables,
        plot_scenario_charts,
    )

    #================================ Load and describe offline data =============================================
    prices, news = load_market_data("data")

    # prices overview
    if not prices.empty:
        p = prices.reset_index()
        p["date"] = p["time"].dt.normalize()
        stats = p.groupby("symbol").agg(
            first=("date", "min"), last=("date", "max"), days=("date", "nunique"), bars=("close", "count")
        )
        print(f"\n=== PRICES: {len(stats)} symbols, {stats['bars'].sum():,} bars ===")
        print(stats.to_string())
    else:
        print("\n=== PRICES: 0 symbols, 0 bars ===")

    # news overview
    if not news.empty:
        n = news.reset_index()
        n["date"] = n["time"].dt.normalize()
        stats = n.groupby("symbol").agg(
            first=("date", "min"),
            last=("date", "max"),
            days=("date", "nunique"),
            articles=("headline", "count"),
            providers=("provider", lambda s: ", ".join(sorted(s.unique()))),
        )
        print(f"\n=== NEWS: {len(stats)} symbols, {stats['articles'].sum():,} articles ===")
        print(stats.to_string())
    else:
        print("\n=== NEWS: 0 symbols, 0 articles ===")

    # chart (guarded)
    if not prices.empty:
        p_reset = prices.reset_index()
        daily = (
            p_reset.assign(date=lambda df: df["time"].dt.normalize())
            .groupby(["symbol", "date"])["close"].last()
            .unstack("symbol")
        )
        if not daily.empty and daily.iloc[0].notna().any():
            norm = daily.div(daily.iloc[0]).mul(100)
            fig, ax = plt.subplots(figsize=(12, 6))
            norm.plot(ax=ax, linewidth=1)
            ax.set(title="Normalised Daily Close (rebased to 100)", xlabel="Date", ylabel="Index")
            ax.grid(True, alpha=0.3)
            # keep legend for normal cases; if too many symbols, it may overlap, but preserve behavior
            ax.legend(loc="upper left", ncol=4, fontsize=8)
            plt.tight_layout()
            Path("images").mkdir(exist_ok=True)
            plt.savefig("images/portfolio_overview.png", dpi=100, bbox_inches="tight")
            plt.close(fig)
            print("Saved: images/portfolio_overview.png")
        else:
            print("Skipping plot: insufficient daily data to compute normalization.")
    else:
        print("Skipping plot: prices empty.")

    #================================ select events =============================================
    candidates = identify_shocks(prices, news)

    if not candidates.empty:
        print(f"=== CANDIDATE POOL: {len(candidates)} stock-day-news triples ===\n")
        cols = [
            "symbol", "event_date", "shock_time_et", "bar_return", "spx_return",
            "rel_abnormal_ret", "return_zscore", "rel_zscore",
            "shock_direction", "shock_bar_median_ratio", "article_count",
            "displayed_headline",
        ]
        cols = [c for c in cols if c in candidates.columns]
        with pd.option_context("display.max_colwidth", 80, "display.width", 200):
            print(candidates[cols])
    else:
        print("\nNo candidates found. Consider re-downloading prices with a longer window.")

    #================================ SC_total construction + §2.3 block assignment =============================================
    if not candidates.empty:
        portfolio_path = Path("data") / "portfolio.csv"
        if not portfolio_path.exists():
            print(f"Portfolio file not found at {portfolio_path}. Skipping SC_total and block assignment.")
            return

        portfolio = pd.read_csv(portfolio_path)

        # Compute SC_total and auxiliary fields (event_type, market_regime) for all candidates
        candidates_sc = compute_sc_total(candidates, news, data_dir="data")

        # §2.3: select best triple per stock, assign intensity tiers, partition into 3 blocks of 12
        blocks = assign_blocks(candidates_sc, portfolio)

        # §2.4: print selection summary tables
        print_block_tables(blocks)

        # §2.5: generate intraday scenario charts for visual review
        plot_scenario_charts(blocks, prices, output_dir="images", data_dir="data")
    else:
        print("Skipping SC_total and block assignment -- no candidates available.")


if __name__ == "__main__":
    main()
