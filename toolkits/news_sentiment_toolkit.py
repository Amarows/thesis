import pandas as pd
import numpy as np
from market_data_processor_toolkit import load_market_data

# Note: You may need to install these libraries:
# pip install nltk
# For advanced financial models: pip install transformers torch

try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    # Download VADER lexicon (only needed once)
    nltk.download('vader_lexicon', quiet=True)
    HAS_VADER = True
except ImportError:
    HAS_VADER = False

def calculate_vader_sentiment(news_df):
    """
    Calculates sentiment scores using VADER.
    VADER is good for quick, rule-based sentiment.
    """
    if not HAS_VADER:
        print("VADER not installed. Please run 'pip install nltk'. Using 0.0 as placeholder.")
        news_df['sentiment_score'] = 0.0
        return news_df

    sia = SentimentIntensityAnalyzer()
    
    # We apply sentiment to the headline as it's often more concise for sentiment
    # But you can also apply it to article_text
    print("Calculating sentiment scores...")
    
    # VADER returns: neg, neu, pos, compound
    # We'll use 'compound' as the main metric (-1 to 1)
    news_df['sentiment_score'] = news_df['headline'].apply(
        lambda x: sia.polarity_scores(str(x))['compound']
    )
    
    return news_df

def aggregate_sentiment(news_df, freq='D'):
    """
    Aggregates sentiment by symbol and time frequency.
    """
    if 'sentiment_score' not in news_df.columns:
        return None
        
    # Reset index to access symbol and time
    df_flat = news_df.reset_index()
    
    # Group by symbol and time period
    sentiment_ts = df_flat.groupby([
        'symbol', 
        pd.Grouper(key='time', freq=freq)
    ])['sentiment_score'].mean()
    
    return sentiment_ts

def openai_sentiment_hint():
    """
    Code snippet hint for using ChatGPT (OpenAI API).
    """
    hint = """
    # To use ChatGPT (OpenAI API) for sentiment:
    # 1. pip install openai
    # 2. Use the following pattern:
    
    from openai import OpenAI
    client = OpenAI(api_key='YOUR_API_KEY')
    
    def get_gpt_sentiment(text):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of this financial headline. Return only a number between -1 (very negative) and 1 (very positive)."},
                {"role": "user", "content": text}
            ]
        )
        return float(response.choices[0].message.content)
    """
    print(hint)

if __name__ == "__main__":
    # 1. Load data
    prices, news = load_market_data("../data")
    
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
        print("\n--- How to use ChatGPT for Sentiment ---")
        openai_sentiment_hint()
        
        # 5. Suggestion for next steps
        print("\nSuggestion: You can now join 'daily_sentiment' with 'prices' to see correlations.")
