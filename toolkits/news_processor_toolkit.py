"""
news_processor_toolkit.py
=========================
News aggregation, headline selection, and AI-powered summarisation for
the survey assembly pipeline.

Responsibilities
----------------
- Strip Benzinga metadata tokens from raw headlines
- Select the best displayed headline per scenario
- Generate 2–3 sentence survey summaries via the Claude API
- Manage a CSV cache so summaries survive re-runs without extra API calls
- Build the scenario_news_text.csv DataFrame consumed by the pipeline

FinBERT sentiment
-----------------
The module initialises the ProsusAI/finbert pipeline at import time if
`transformers` and `torch` are available.  `HAS_FINBERT` and
`_finbert_score()` are exported for use by the SC computation step.
"""

from __future__ import annotations

import os
import re
import warnings

import numpy as np
import pandas as pd

# ── FinBERT (optional) ────────────────────────────────────────────────────────

try:
    from transformers import pipeline as _hf_pipeline
    _finbert = _hf_pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        top_k=None,
    )
    HAS_FINBERT = True
except Exception:
    _finbert = None
    HAS_FINBERT = False


def _finbert_score(text: str) -> float:
    """Return FinBERT sentiment as positive_prob − negative_prob in [−1, 1].

    Returns 0.0 if FinBERT is unavailable or text is empty.

    FinBERT (BERT-base) has a hard 512-token limit.  We pass
    truncation=True so the HuggingFace tokenizer silently truncates long
    inputs instead of raising an indexing error.  The character pre-slice
    (:512) is a cheap first-pass guard that keeps the tokenizer fast.
    """
    if not HAS_FINBERT or not isinstance(text, str) or not text.strip():
        return 0.0
    output = _finbert(text[:512], truncation=True, max_length=512)
    labels = output[0] if isinstance(output[0], list) else output
    probs = {d["label"].lower(): d["score"] for d in labels}
    return float(probs.get("positive", 0.0) - probs.get("negative", 0.0))


# ── Headline cleaning ─────────────────────────────────────────────────────────

def _clean_bz_headline(text: str) -> str:
    """Strip Benzinga metadata tokens {A:...:L:...:K:...:C:...} from headline."""
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r"\{A:.*?:L:.*?(?::K:.*?:C:.*?)?\}!?", "", text).strip()
    return cleaned if cleaned else text


# ── Headline selection ────────────────────────────────────────────────────────

def _pick_displayed_headline(
    manifest_headline: str,
    articles_df: pd.DataFrame,
) -> str:
    """
    Return the headline to display to respondents.
    Priority: manifest headline if not blank → highest |FinBERT| article → first article.
    """
    if isinstance(manifest_headline, str) and manifest_headline.strip() not in (
        "", "nan", "<paste displayed headline here>",
    ):
        return _clean_bz_headline(manifest_headline.strip())

    if articles_df.empty:
        return "[HEADLINE NOT AVAILABLE]"

    if HAS_FINBERT and "headline" in articles_df.columns:
        scores = articles_df["headline"].apply(
            lambda h: abs(_finbert_score(str(h)))
        )
        best_idx = scores.idxmax()
        return _clean_bz_headline(str(articles_df.loc[best_idx, "headline"]))

    return _clean_bz_headline(str(articles_df.iloc[0]["headline"]))


# ── Claude API summarisation ──────────────────────────────────────────────────

_ANTHROPIC_SYSTEM = (
    "You are editing financial news summaries for a professional investment survey. "
    "Produce a 2–3 sentence summary from the raw news provided. "
    "Preserve the factual content and the direct, evaluative register of financial "
    "wire copy (Benzinga style). Do not make the text more neutral or academic. "
    "Do not add context not present in the original. "
    "Return only the summary, no preamble."
)


def _generate_summary_anthropic(
    company_name: str,
    ticker: str,
    gics_sector: str,
    event_date,
    articles_df: pd.DataFrame,
) -> str:
    """
    Call Claude API to produce a 2–3 sentence Benzinga-style survey summary.
    Returns placeholder string if API unavailable or call fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "[TO BE GENERATED]"

    try:
        import anthropic
    except ImportError:
        warnings.warn("anthropic package not installed – summaries will use placeholder")
        return "[TO BE GENERATED]"

    try:
        client = anthropic.Anthropic(api_key=api_key)

        parts = []
        for _, art in articles_df.iterrows():
            hl   = _clean_bz_headline(str(art.get("headline", "")))
            body = str(art.get("article_text", ""))
            body = re.sub(r"<[^>]+>", " ", body)
            body = " ".join(body.split())[:600]
            parts.append(f"Headline: {hl}\nBody: {body}")
        raw_news = "\n\n".join(parts)[:3500]

        user_msg = (
            f"Stock: {company_name} ({ticker}), Sector: {gics_sector}. "
            f"Event date: {event_date}. "
            f"Raw news:\n{raw_news}\n\n"
            "Produce a 2–3 sentence summary in Benzinga financial wire style:"
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=_ANTHROPIC_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text.strip()

    except Exception as exc:
        warnings.warn(f"Anthropic API error ({ticker} {event_date}): {exc}")
        return "[TO BE GENERATED]"


# ── Summary cache ─────────────────────────────────────────────────────────────

def _load_summary_cache(cache_path: "Path | str") -> dict[str, str]:
    """Load scenario_id → summary_paragraph from cache file if it exists."""
    from pathlib import Path
    cache_path = Path(cache_path)
    if not cache_path.exists():
        return {}
    try:
        df = pd.read_csv(cache_path, dtype=str)
        df = df[df["summary_paragraph"].notna()]
        df = df[~df["summary_paragraph"].str.strip().isin(["", "[TO BE GENERATED]"])]
        return dict(zip(df["scenario_id"], df["summary_paragraph"]))
    except Exception:
        return {}


def _save_summary_cache(cache: dict[str, str], cache_path: "Path | str") -> None:
    """Persist the cache dict to cache_path as CSV."""
    if not cache:
        return
    from pathlib import Path
    rows = [{"scenario_id": k, "summary_paragraph": v} for k, v in cache.items()]
    pd.DataFrame(rows).to_csv(Path(cache_path), index=False)


# ── Build news text DataFrame ─────────────────────────────────────────────────

def build_news_text_df(
    manifest_df: pd.DataFrame,
    news_data: dict[str, pd.DataFrame],
    portfolio_df: pd.DataFrame,
    cache_path: "Path | str | None" = None,
) -> pd.DataFrame:
    """
    Build scenario_news_text.csv content.

    For each scenario in manifest_df:
      - selects the displayed headline
      - generates (or loads from cache) a 2–3 sentence summary paragraph

    Parameters
    ----------
    manifest_df  : scenario manifest (columns: scenario_id, ticker, event_date, ...)
    news_data    : {ticker: DataFrame[time, headline, article_text, ...]}
    portfolio_df : portfolio metadata (columns: ticker, company_name, gics_sector)
    cache_path   : path for the summary CSV cache; None disables caching

    Returns
    -------
    DataFrame with columns: scenario_id, ticker, event_date, headline,
                             summary_paragraph, num_articles
    """
    from event_selection_toolkit import get_event_day_news

    port_lookup = portfolio_df.set_index("ticker")
    has_api     = bool(os.environ.get("ANTHROPIC_API_KEY"))
    cache: dict[str, str] = _load_summary_cache(cache_path) if cache_path else {}

    rows = []
    for _, mrow in manifest_df.iterrows():
        sid          = mrow["scenario_id"]
        ticker       = mrow["ticker"]
        event_date   = mrow["event_date"]
        company_name = str(mrow.get("company_name", ""))
        gics_sector  = str(mrow.get("gics_sector", ""))

        if (not company_name or company_name == "nan") and ticker in port_lookup.index:
            company_name = str(port_lookup.loc[ticker, "company_name"])
        if (not gics_sector or gics_sector == "nan") and ticker in port_lookup.index:
            gics_sector = str(port_lookup.loc[ticker, "gics_sector"])

        day_articles = get_event_day_news(news_data, ticker, event_date)
        num_articles = len(day_articles)

        headline = _pick_displayed_headline(
            str(mrow.get("headline", "")), day_articles
        )

        if sid in cache:
            print(f"  {sid} news text (cached)... done")
            summary = cache[sid]
        else:
            print(
                f"  {sid} news text ({'API' if has_api else 'placeholder'})...",
                end="", flush=True,
            )
            summary = _generate_summary_anthropic(
                company_name, ticker, gics_sector, event_date, day_articles
            )
            print(" done")
            if summary != "[TO BE GENERATED]":
                cache[sid] = summary

        rows.append({
            "scenario_id":      sid,
            "ticker":           ticker,
            "event_date":       str(event_date),
            "headline":         headline,
            "summary_paragraph": summary,
            "num_articles":     num_articles,
        })

    if cache_path:
        _save_summary_cache(cache, cache_path)
    return pd.DataFrame(rows)
