"""6_process_survey_data.py

Download, parse, and merge survey responses into a clean analysis panel.

All responses are stored in a single Google Sheets workbook (one tab per
form version).  This script authenticates, downloads each tab, applies the
confirmed column schema, excludes non-qualifying respondents, merges the
counterbalancing matrix and scenario metadata, and writes the primary
deliverable: results/analysis_panel.csv.

Usage
-----
    python 6_process_survey_data.py                        # full API run
    python 6_process_survey_data.py --dry-run              # use cached raw_responses/ CSVs
    python 6_process_survey_data.py --form-key block_1_v1  # single form key only
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

from toolkits.data_aggregation_toolkit import (
    authenticate_google,
    build_analysis_panel,
    download_tab_responses,
    load_mapping_tab,
    merge_metadata,
    parse_response_tab,
    validate_and_exclude,
    write_qc_report,
    _normalise_form_key,
)

# ── Constants ──────────────────────────────────────────────────────────────────

SPREADSHEET_ID        = "1ICjcSZdwuW-xKepA5VMDjO-gfBfAe544wuO-wsmG3fM"
CREDENTIALS_PATH      = Path("credentials/client_secret.json")
METADATA_PATH         = Path("survey/metadata/scenario_metadata.csv")
COUNTERBALANCING_PATH = Path("survey/counterbalancing/counterbalancing_matrix.csv")
RESULTS_DIR           = Path("results")
RAW_RESPONSES_DIR     = Path("survey/raw_responses")


# ── Dry-run helpers ────────────────────────────────────────────────────────────

def _load_cached_mapping() -> dict[str, str]:
    """
    Build {tab_name: form_key} from existing raw CSV filenames.

    Expects files like survey/raw_responses/Block1_V1_raw.csv.
    Returns canonical tab_name → form_key pairs.
    """
    mapping: dict[str, str] = {}
    for csv_path in sorted(RAW_RESPONSES_DIR.glob("*_raw.csv")):
        stem = csv_path.stem  # e.g. 'Block1_V1_raw'
        tab_name = stem.replace("_raw", "")  # e.g. 'Block1_V1'
        try:
            form_key = _normalise_form_key(tab_name)
            mapping[tab_name] = form_key
        except ValueError:
            pass
    return mapping


def _load_cached_raw(tab_name: str) -> pd.DataFrame:
    """Load a previously saved raw CSV snapshot."""
    csv_path = RAW_RESPONSES_DIR / f"{tab_name}_raw.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Cached raw file not found: {csv_path}\n"
            "Run without --dry-run first to download raw responses."
        )
    return pd.read_csv(csv_path, dtype=str, encoding="utf-8").fillna("")


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run(dry_run: bool = False, form_key_filter: str | None = None) -> None:
    """Execute the full survey data processing pipeline."""

    # 1. Create output directories
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    # 2–3. Authenticate and load tab mapping
    if dry_run:
        tab_map = _load_cached_mapping()
        print(f"[dry-run] Loaded mapping from cached files: {list(tab_map.keys())}")
    else:
        print("Authenticating with Google Sheets API …")
        sheets_service = authenticate_google(CREDENTIALS_PATH)
        tab_map: dict[str, str] = load_mapping_tab(sheets_service, SPREADSHEET_ID)

    # Apply --form-key filter
    if form_key_filter:
        try:
            canonical_filter = _normalise_form_key(form_key_filter)
        except ValueError:
            canonical_filter = form_key_filter.lower()
        tab_map = {tn: fk for tn, fk in tab_map.items() if fk == canonical_filter}
        if not tab_map:
            print(
                f"ERROR: No tab found for --form-key={form_key_filter!r}. "
                f"Available keys: {list(tab_map.values()) or 'block_1_v1 .. block_3_v2'}",
                file=sys.stderr,
            )
            sys.exit(1)

    # 4. Download or load each tab; record raw row counts
    raw_counts: dict[str, int] = {}
    parsed_frames: list[pd.DataFrame] = []

    for tab_name, form_key in tab_map.items():
        if dry_run:
            print(f"  [dry-run] Loading cached: {tab_name} …")
            raw_df = _load_cached_raw(tab_name)
        else:
            print(f"  Downloading tab: {tab_name} …")
            raw_df = download_tab_responses(
                sheets_service, SPREADSHEET_ID, tab_name, RAW_RESPONSES_DIR
            )

        raw_counts[tab_name] = len(raw_df)

        if raw_df.empty:
            print(f"    -> empty tab, skipping.")
            continue

        # 5. Parse each tab
        parsed = parse_response_tab(raw_df, form_key)
        parsed_frames.append(parsed)
        print(f"    -> {len(raw_df)} raw rows -> {parsed['respondent_id'].nunique()} respondents parsed.")

    # 6. Concatenate
    if not parsed_frames:
        print("No response data found. Exiting.", file=sys.stderr)
        sys.exit(0)

    all_responses = pd.concat(parsed_frames, ignore_index=True)

    # 7. Validate and exclude
    clean_df, excluded_df = validate_and_exclude(all_responses, 0)
    n_excl = excluded_df["respondent_id"].nunique() if not excluded_df.empty else 0
    print(f"\nValidation: {clean_df['respondent_id'].nunique()} clean | {n_excl} excluded.")

    # 8. Merge metadata
    print("Merging counterbalancing matrix and scenario metadata …")
    merged_df = merge_metadata(
        clean_df,
        METADATA_PATH,
        COUNTERBALANCING_PATH,
        join_failures_path=RESULTS_DIR / "join_failures.csv",
    )

    # 9. Build analysis panel
    panel_df = build_analysis_panel(merged_df)

    # 10. Write analysis_panel.csv
    panel_path = RESULTS_DIR / "analysis_panel.csv"
    panel_df.to_csv(panel_path, index=False)
    print(f"Written: {panel_path}  ({len(panel_df)} rows)")

    # 11. Write excluded_respondents.csv
    excl_path = RESULTS_DIR / "excluded_respondents.csv"
    excluded_df.to_csv(excl_path, index=False)
    print(f"Written: {excl_path}  ({len(excluded_df)} rows)")

    # 12. Write QC report
    qc_path = RESULTS_DIR / "analysis_panel_comments.md"
    write_qc_report(
        clean_df=panel_df,
        excluded_df=excluded_df,
        raw_counts=raw_counts,
        output_path=qc_path,
        spreadsheet_id=SPREADSHEET_ID,
    )
    print(f"Written: {qc_path}")

    # 13. Stdout summary
    n_resp = panel_df["respondent_id"].nunique() if not panel_df.empty else 0
    n_obs  = len(panel_df)
    show0  = int((panel_df["show_sc"] == 0).sum()) if not panel_df.empty else 0
    show1  = int((panel_df["show_sc"] == 1).sum()) if not panel_df.empty else 0
    scen   = panel_df["scenario_id"].nunique() if not panel_df.empty else 0
    pilot_rows = int(panel_df["is_pilot_block"].sum()) if not panel_df.empty else 0

    excl_by_reason: dict[str, int] = {}
    if not excluded_df.empty and "exclusion_reason" in excluded_df.columns:
        excl_by_reason = (
            excluded_df.drop_duplicates("respondent_id")["exclusion_reason"]
            .value_counts()
            .to_dict()
        )

    total_raw = sum(raw_counts.values())

    print()
    print("=" * 61)
    print("Survey Data Processing Complete")
    print("=" * 61)
    print(f"  Spreadsheet       : {SPREADSHEET_ID}")
    print(f"  Tabs processed    : {len(raw_counts)}")
    print(f"  Raw responses     : {total_raw} rows total")
    excl_detail = " | ".join(f"{r}: {c}" for r, c in excl_by_reason.items()) or "0"
    print(f"  Excluded          : {n_excl} ({excl_detail})")
    print(f"  Final panel       : {n_resp} respondents x {n_obs} observations")
    print(f"  ShowSC balance    : ShowSC=0: {show0} | ShowSC=1: {show1}")
    print(f"  Scenarios covered : {scen} / 24")
    print(f"  Pilot block rows  : {pilot_rows} (Block 1 respondents with pilot feedback)")
    print(f"  Outputs           : {RESULTS_DIR}/")
    print("=" * 61)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and process survey responses into analysis_panel.csv."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use cached raw_responses/ CSVs instead of calling the Sheets API.",
    )
    parser.add_argument(
        "--form-key",
        metavar="FORM_KEY",
        default=None,
        help="Process a single form key only, e.g. block_1_v1.",
    )
    args, _ = parser.parse_known_args()
    run(dry_run=args.dry_run, form_key_filter=args.form_key)
