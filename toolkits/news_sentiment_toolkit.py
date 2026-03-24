import pandas as pd
import numpy as np
from market_data_processor_toolkit import load_market_data

# Note: You may need to install these libraries:
# pip install transformers torch

try:
    from transformers import pipeline as _hf_pipeline
    _finbert = _hf_pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        truncation=True,
        max_length=512,
        top_k=None,
    )
    HAS_FINBERT = True
except Exception:
    _finbert = None
    HAS_FINBERT = False


def _finbert_score(text: str) -> float:
    """Return FinBERT sentiment as positive_prob - negative_prob in [-1, 1].

    Returns 0.0 if FinBERT is unavailable or text is empty.
    """
    if not HAS_FINBERT or not isinstance(text, str) or not text.strip():
        return 0.0
    output = _finbert(text[:1500])
    # output: [[{'label': ..., 'score': ...}, ...]] for a single input
    labels = output[0] if isinstance(output[0], list) else output
    probs = {d["label"].lower(): d["score"] for d in labels}
    return float(probs.get("positive", 0.0) - probs.get("negative", 0.0))


def calculate_finbert_sentiment(news_df):
    """
    Calculates sentiment scores using FinBERT (yiyanghkust/finbert-tone).

    Returns positive_prob - negative_prob per article as sentiment_score [-1, 1].
    Applied to headline text.
    """
    if not HAS_FINBERT:
        print("FinBERT not available. Please run 'pip install transformers torch'. Using 0.0 as placeholder.")
        news_df['sentiment_score'] = 0.0
        return news_df

    print("Calculating FinBERT sentiment scores...")
    news_df['sentiment_score'] = news_df['headline'].apply(
        lambda x: _finbert_score(str(x))
    )
    return news_df


def aggregate_sentiment(news_df, freq='D'):
    """
    Aggregates sentiment by symbol and time frequency.
    """
    if 'sentiment_score' not in news_df.columns:
        return None

    df_flat = news_df.reset_index()

    sentiment_ts = df_flat.groupby([
        'symbol',
        pd.Grouper(key='time', freq=freq)
    ])['sentiment_score'].mean()

    return sentiment_ts


if __name__ == "__main__":
    # 1. Load data
    prices, news = load_market_data("../data")

    if news.empty:
        print("No news data found to process.")
    else:
        # 2. Calculate Sentiment
        news = calculate_finbert_sentiment(news)

        # 3. Aggregate
        daily_sentiment = aggregate_sentiment(news, freq='D')

        print("\n--- Sentiment Results (First 5) ---")
        print(news[['headline', 'sentiment_score']].head())

        if daily_sentiment is not None:
            print("\n--- Daily Aggregate Sentiment ---")
            print(daily_sentiment)

        print("\nSuggestion: You can now join 'daily_sentiment' with 'prices' to see correlations.")
