import os
import glob
import pandas as pd
import re

def clean_html(text):
    """
    Removes HTML tags and unescapes entities from a string.
    """
    if not isinstance(text, str):
        return text

    # Remove HTML tags
    clean_re = re.compile('<.*?>')
    text = re.sub(clean_re, '', text)

    # Basic unescaping of common entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&#169;', '©')
    text = text.replace('&#10;', ' ')

    # Handle both literal \n (backslash + n) and actual newline characters
    text = text.replace('\\n', ' ')
    text = text.replace('\n', ' ')

    # Remove \' combination
    text = text.replace("\\'", "")

    # Clean up multiple spaces and strip
    return ' '.join(text.split())

def parse_headline_metadata(headline):
    """
    Parses headline metadata in curly braces: {A:id:L:lang:K:score:C:conf}
    Returns (cleaned_headline, article_id, language, keyword_score, confidence)
    """
    if not isinstance(headline, str):
        return headline, None, None, None, None

    # Pattern to match {A:...:L:...:K:...:C:...}
    meta_pattern = re.compile(r'\{A:(.*?):L:(.*?):K:(.*?):C:(.*?)\}')
    match = meta_pattern.search(headline)

    if match:
        article_id, lang, k_score, conf = match.groups()
        # Remove the metadata from headline
        clean_headline = meta_pattern.sub('', headline).strip()

        # Convert numeric values if possible
        try:
            k_score = float(k_score) if k_score != 'n/a' else None
        except ValueError:
            k_score = None

        try:
            conf = float(conf) if conf != 'n/a' else None
        except ValueError:
            conf = None

        return clean_headline, article_id, lang, k_score, conf

    return headline, None, None, None, None

def load_market_data(data_dir="data", bar_interval="30mins"):
    """
    Loads price and news CSV files from the specified directory.
    Returns two pandas objects:
    1. prices: MultiIndex Series (symbol, time) -> close
    2. news: MultiIndex DataFrame (symbol, provider, time) -> [headline, article_text, ...]

    Parameters
    ----------
    data_dir     : directory containing CSV files (default "data")
    bar_interval : intraday bar size token to load, matched against the second
                   segment of the price filename (e.g. "30mins", "1hour").
                   Default "30mins" loads only 30-minute bar files per protocol §2.1A.
                   Pass None to load all price resolutions.
    """
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))

    price_frames = []
    news_frames = []

    # Pattern for prices: SYMBOL_BAR_DURATION.csv (e.g., AAPL_30mins_360D.csv)
    price_pattern = re.compile(r"(.+)_([^_]+)_([^_]+)\.csv$")

    # Pattern for news: SYMBOL_PROVIDER_START_to_END.csv (e.g., AAPL_BZ_2025-12-15_to_2025-12-18.csv)
    news_pattern = re.compile(r"(.+)_([^_]+)_(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})\.csv$")

    for fpath in all_files:
        fname = os.path.basename(fpath)

        # Try news pattern first
        news_match = news_pattern.match(fname)
        if news_match:
            symbol, provider, start, end = news_match.groups()
            try:
                df = pd.read_csv(fpath)
            except pd.errors.EmptyDataError:
                continue   # empty file — skip silently
            except Exception as e:
                print(f"Error loading news file {fname}: {e}")
                continue
            try:
                if not df.empty:

                    # Ensure time is datetime and matches price format (UTC)
                    if 'time_utc' in df.columns:
                        df['time'] = pd.to_datetime(df['time_utc'], format='ISO8601', utc=True)
                    elif 'time' in df.columns:
                        df['time'] = pd.to_datetime(df['time'], format='ISO8601', utc=True)

                    # Clean article_text
                    if 'article_text' in df.columns:
                        # Convert to string to avoid issues with float NaN
                        df['article_text'] = df['article_text'].astype(str)

                        # Apply general HTML and \n cleaning
                        df['article_text'] = df['article_text'].apply(clean_html)

                        # 5. Provider FLY: remove time from beginning (e.g. "05:56 EST ")
                        if provider == 'FLY':
                            # Matches "HH:MM EST " or similar
                            fly_time_re = re.compile(r'^\d{2}:\d{2}\s+[A-Z]{3,4}\s+')
                            df['article_text'] = df['article_text'].apply(lambda x: fly_time_re.sub('', x))

                    # 7. Parse headline metadata
                    if 'headline' in df.columns:
                        parsed = df['headline'].apply(parse_headline_metadata)
                        df['headline'] = parsed.apply(lambda x: x[0])
                        df['article_identifier'] = parsed.apply(lambda x: x[1])
                        df['language_code'] = parsed.apply(lambda x: x[2])
                        df['keyword_score'] = parsed.apply(lambda x: x[3])
                        df['confidence'] = parsed.apply(lambda x: x[4])

                    # Provider BZ: replace https... with headline
                    if provider == 'BZ':
                        df.loc[df['article_text'].str.startswith('https'), 'article_text'] = df.loc[
                            df['article_text'].str.startswith('https'), 'headline']

                    if provider == 'DJ-RT':
                        df.loc[df['article_text'].str.startswith('Ratings actions'), 'article_text'] = df.loc[
                            df['article_text'].str.startswith('Ratings actions'), 'headline']

                    news_frames.append(df)
            except Exception as e:
                print(f"Error processing news file {fname}: {e}")
            continue

        # Try price pattern
        price_match = price_pattern.match(fname)
        if price_match:
            symbol, bar, duration = price_match.groups()
            if "-" in duration and "_to_" in fname:
                continue
            # Filter by bar interval (e.g. only "30mins" files per protocol §2.1A)
            if bar_interval is not None and bar != bar_interval:
                continue

            try:
                df = pd.read_csv(fpath)
            except pd.errors.EmptyDataError:
                continue
            except Exception as e:
                print(f"Error loading price file {fname}: {e}")
                continue
            try:
                if not df.empty:
                    df['time'] = pd.to_datetime(df['time'], format='ISO8601', utc=True)
                    df['symbol'] = symbol
                    price_frames.append(df)
            except Exception as e:
                print(f"Error processing price file {fname}: {e}")
            continue

    # Process Prices
    if price_frames:
        prices_df = pd.concat(price_frames, ignore_index=True)
        prices_series = prices_df.set_index(['symbol', 'time'])['close'].sort_index()
    else:
        prices_series = pd.Series(dtype='float64', name='close')
        prices_series.index = pd.MultiIndex.from_arrays([[], []], names=['symbol', 'time'])

    # Process News
    if news_frames:
        # Drop all-NA columns from each frame before concat to avoid FutureWarning
        news_frames = [f.dropna(axis=1, how="all") for f in news_frames]
        news_df = pd.concat(news_frames, ignore_index=True)
        news_df = news_df.set_index(['symbol', 'provider', 'time']).sort_index()
    else:
        news_df = pd.DataFrame(columns=['headline', 'article_text', 'article_identifier', 'language_code', 'keyword_score', 'confidence'])
        news_df.index = pd.MultiIndex.from_arrays([[], [], []], names=['symbol', 'provider', 'time'])

    return prices_series, news_df