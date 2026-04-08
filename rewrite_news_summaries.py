"""rewrite_news_summaries.py – SURVEY-04

Rewrites the `summary_paragraph` column in survey/metadata/scenario_news_text.csv
using the Anthropic API, shortening each entry to 2–3 sentences while preserving
the direct, evaluative register of Benzinga financial wire copy.

Usage:
    python rewrite_news_summaries.py           # live rewrite all rows
    python rewrite_news_summaries.py --dry-run # print plan without API calls

Prerequisites:
    ANTHROPIC_API_KEY environment variable set, OR
    credentials/claude_api.txt file containing the key.
"""

import argparse
import os
import shutil
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "survey" / "metadata" / "scenario_news_text.csv"
BACKUP_PATH = ROOT / "survey" / "metadata" / "scenario_news_text_backup.csv"
CREDENTIALS_KEY_PATH = ROOT / "credentials" / "claude_api.txt"

# ---------------------------------------------------------------------------
# Prompt (SURVEY-04 spec)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are editing financial news summaries for a professional investment survey. "
    "Rewrite the provided summary in 2–3 concise sentences. "
    "Preserve the factual content and the direct, evaluative register of financial "
    "wire copy (Benzinga style). Do not make the text more neutral or academic. "
    "Do not add context not present in the original. "
    "Return only the rewritten summary, no preamble."
)

_MODEL = "claude-sonnet-4-20250514"
_MAX_TOKENS = 300


# ---------------------------------------------------------------------------
# API helper
# ---------------------------------------------------------------------------

def _load_api_key() -> str | None:
    """Return API key from env or credentials file, or None if unavailable."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    if CREDENTIALS_KEY_PATH.exists():
        key = CREDENTIALS_KEY_PATH.read_text().strip()
        if key:
            os.environ["ANTHROPIC_API_KEY"] = key
            return key
    return None


def _rewrite_summary(client, headline: str, summary: str) -> str:
    """Call the Anthropic API to rewrite a single summary paragraph."""
    user_msg = (
        f"Headline: {headline}\n\n"
        f"Current summary: {summary}\n\n"
        "Rewrite in 2–3 sentences preserving Benzinga tone:"
    )
    response = client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite scenario_news_text.csv summaries to Benzinga style.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python rewrite_news_summaries.py           # live rewrite\n"
            "  python rewrite_news_summaries.py --dry-run # validate without API calls"
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Print the rewrite plan without making any API calls.",
    )
    args, _ = parser.parse_known_args()
    return args


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    dry_run = args.dry_run

    print("=" * 70)
    print("SURVEY-04: Rewrite scenario news summaries to Benzinga style")
    print(f"  Mode   : {'DRY-RUN (no API calls)' if dry_run else 'LIVE'}")
    print(f"  Model  : {_MODEL}")
    print(f"  Source : {CSV_PATH.relative_to(ROOT)}")
    print("=" * 70)

    # ── Load CSV ──────────────────────────────────────────────────────────────
    if not CSV_PATH.exists():
        print(f"[ERROR] CSV not found: {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH, dtype=str)

    if "summary_paragraph" not in df.columns or "headline" not in df.columns:
        print("[ERROR] Expected columns 'headline' and 'summary_paragraph' not found.")
        return

    n_rows = len(df)
    print(f"\nLoaded {n_rows} rows from {CSV_PATH.name}")

    if dry_run:
        print(f"\n[DRY-RUN] Would back up -> {BACKUP_PATH.name}")
        print(f"[DRY-RUN] Would rewrite {n_rows} summary_paragraph values via Anthropic API.")
        print(f"[DRY-RUN] No files will be modified.")
        print("\n" + "=" * 70)
        print("DRY-RUN complete.")
        print("=" * 70)
        return

    # ── Backup ────────────────────────────────────────────────────────────────
    shutil.copy2(CSV_PATH, BACKUP_PATH)
    print(f"Backup saved -> {BACKUP_PATH.name}")

    # ── API client ────────────────────────────────────────────────────────────
    api_key = _load_api_key()
    if not api_key:
        print(
            "[ERROR] ANTHROPIC_API_KEY not set and credentials/claude_api.txt not found.\n"
            "Set the environment variable or add the key to credentials/claude_api.txt."
        )
        return

    try:
        import anthropic
    except ImportError:
        print("[ERROR] anthropic package not installed. Run: pip install anthropic")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # ── Rewrite loop ─────────────────────────────────────────────────────────
    print(f"\nRewriting {n_rows} summaries...\n")
    total_before = 0
    total_after = 0
    errors = []

    for i, row in df.iterrows():
        scenario_id = str(row.get("scenario_id", f"row_{i}"))
        headline = str(row.get("headline", "")).strip()
        original = str(row.get("summary_paragraph", "")).strip()

        words_before = len(original.split())
        total_before += words_before

        try:
            rewritten = _rewrite_summary(client, headline, original)
            words_after = len(rewritten.split())
            total_after += words_after
            df.at[i, "summary_paragraph"] = rewritten

            reduction_pct = (
                round((words_before - words_after) / words_before * 100, 1)
                if words_before > 0 else 0.0
            )
            print(
                f"  {scenario_id:<10}  {words_before:>3}w -> {words_after:>3}w  "
                f"({'-' if words_before >= words_after else '+'}"
                f"{abs(words_before - words_after)}w, {reduction_pct:.1f}% reduction)"
            )

        except Exception as exc:
            words_after = words_before  # keep original on error
            total_after += words_after
            errors.append((scenario_id, str(exc)))
            print(f"  {scenario_id:<10}  [ERROR] {exc}")

    # ── Save ─────────────────────────────────────────────────────────────────
    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved updated CSV -> {CSV_PATH.name}")

    # ── Summary ───────────────────────────────────────────────────────────────
    overall_reduction = (
        round((total_before - total_after) / total_before * 100, 1)
        if total_before > 0 else 0.0
    )
    print("\n" + "=" * 70)
    print("Word count summary:")
    print(f"  Total before : {total_before} words")
    print(f"  Total after  : {total_after} words")
    print(f"  Reduction    : {total_before - total_after} words ({overall_reduction:.1f}%)")
    if errors:
        print(f"\n  Errors ({len(errors)}):")
        for sid, msg in errors:
            print(f"    {sid}: {msg}")
    print("=" * 70)


if __name__ == "__main__":
    main()
