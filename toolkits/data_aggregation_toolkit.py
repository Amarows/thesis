"""
data_aggregation_toolkit.py
===========================
Survey response download, parsing, and panel construction for the thesis
data pipeline.

Responsibilities
----------------
- Authenticate to Google Sheets API (OAuth2)
- Download raw response tabs from the linked Google Sheets workbook
- Parse and normalise the confirmed column schema (positional NRS columns)
- Construct respondent_id without PII
- Validate and exclude non-qualifying respondents
- Merge counterbalancing matrix and scenario metadata
- Build the analysis-ready panel (analysis_panel.csv)
- Write the QC/audit report (analysis_panel_comments.md)
"""

from __future__ import annotations

import hashlib
import json
import os
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Constants ─────────────────────────────────────────────────────────────────

_SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"
_TOKEN_PATH = Path("credentials/token_sheets.json")

# Positional indices (0-based) for the 8 NRS columns inside each response tab
_NRS_COL_START = 8
_NRS_COL_END = 16  # exclusive

_NRS_MIN = 1
_NRS_MAX = 7

# Pilot-block columns (0-based, positions 18–23)
_PILOT_COL_INDICES = {
    "completion_time": 18,
    "pilot_clarity": 19,
    "pilot_dashboard_ease": 20,
    "pilot_realism": 21,
    "open_feedback": 22,
    "contact_optional": 23,
}

# Columns expected at fixed positions 0–17
_FIXED_SCHEMA = {
    0: "timestamp",
    1: "years_experience",
    2: "aum_category",
    3: "institution_type",
    4: "investment_mandate",
    5: "geographic_focus",
    6: "discretionary_authority",
    7: "certifications",
    16: "manipulation_check",
    17: "usefulness_rating",
}

# Ordinal experience categories → (midpoint, minimum) for analysis and exclusion.
# Midpoint used in regression; minimum used for the experience<5 exclusion rule.
# All keys use ASCII hyphen; _norm_exp() normalises any dash variant before lookup.
_EXPERIENCE_MAP: dict[str, tuple[float, float]] = {
    "less than 2": (1.0,  0.0),
    "2-5":         (3.5,  2.0),
    "6-10":        (8.0,  6.0),
    "11-20":       (15.5, 11.0),
    "more than 20":(25.0, 21.0),
}

# Regex that matches any Unicode dash/hyphen variant
_DASH_RE = re.compile(r"[-‐‑‒–—―−﹘﹣－]|â€“")


def _norm_exp(raw: str) -> str:
    """Normalise an experience label for _EXPERIENCE_MAP lookup."""
    return _DASH_RE.sub("-", raw).strip().lower()


# Final column order for the analysis panel
_PANEL_COLUMNS = [
    # Respondent fields
    "respondent_id",
    "form_key",
    "block_id",
    "version",
    "timestamp",
    "years_experience",
    "years_experience_label",
    "aum_category",
    "institution_type",
    "investment_mandate",
    "geographic_focus",
    "discretionary_authority",
    "certifications",
    "manipulation_check",
    "usefulness_rating",
    # Pilot fields
    "is_pilot_block",
    "completion_time",
    "pilot_clarity",
    "pilot_dashboard_ease",
    "pilot_realism",
    "open_feedback",
    "contact_optional",
    # Scenario (observation) fields
    "scenario_position",
    "nrs",
    "nrs_invalid",
    # Metadata from counterbalancing + scenario tables
    "scenario_id",
    "show_sc",
    "show_sc_conflict",
    "metadata_join_failed",
    "ticker",
    "company_name",
    "gics_sector",
    "event_date",
    "event_type",
    "sc_total",
    "ac_e",
    "se_e",
    "ai_e",
    "es_raw",
    "market_regime",
    # Augmentation placeholder
]

# Normalised form_key → respondent_block label in counterbalancing matrix
# e.g. "block_1_v1" → "Block1_V1"
def _form_key_to_cb_label(form_key: str) -> str:
    """Convert 'block_1_v1' → 'Block1_V1' to match counterbalancing_matrix."""
    m = re.match(r"block_(\d+)_v(\d+)", form_key, re.IGNORECASE)
    if not m:
        raise ValueError(f"Cannot parse block/version from form_key: {form_key!r}")
    return f"Block{m.group(1)}_V{m.group(2)}"


def _normalise_form_key(raw: str) -> str:
    """Normalise 'Block1_V1' or 'block_1_v1' to canonical 'block_1_v1'."""
    raw = raw.strip()
    # Already in canonical form
    if re.match(r"^block_\d+_v\d+$", raw, re.IGNORECASE):
        return raw.lower()
    # Handle 'Block1_V1' or 'Block1V1' style
    m = re.match(r"[Bb]lock\s*(\d+)[_\s]*[Vv]\s*(\d+)", raw)
    if m:
        return f"block_{m.group(1)}_v{m.group(2)}"
    # Handle tab names like 'Block1_V1 (Responses)'
    m2 = re.match(r"[Bb]lock\s*(\d+)[_\s]*[Vv]\s*(\d+)", raw.split("(")[0])
    if m2:
        return f"block_{m2.group(1)}_v{m2.group(2)}"
    raise ValueError(f"Cannot normalise form key: {raw!r}")


# ── Authentication ─────────────────────────────────────────────────────────────

def authenticate_google(credentials_path: Path) -> object:
    """
    Authenticate with Google Sheets API v4 using OAuth2 desktop flow.

    Parameters
    ----------
    credentials_path : Path
        Path to client_secret.json (Google Cloud OAuth2 Desktop credentials).

    Returns
    -------
    sheets_service : googleapiclient Resource
        Authorised Sheets API service object.

    Notes
    -----
    Token is cached to credentials/token_sheets.json and refreshed automatically
    on subsequent runs. Scope is read-only (spreadsheets.readonly).
    """
    creds = None
    token_path = _TOKEN_PATH

    if token_path.exists():
        try:
            with open(token_path, "rb") as fh:
                creds = pickle.load(fh)
            # Discard token if it was issued without the required Sheets scope
            if creds and hasattr(creds, "scopes") and creds.scopes:
                if not any("spreadsheets" in s for s in creds.scopes):
                    print(
                        f"  [auth] Cached token lacks spreadsheets scope — re-authenticating."
                    )
                    creds = None
                    token_path.unlink(missing_ok=True)
        except Exception:
            creds = None
            token_path.unlink(missing_ok=True)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # Refresh failed (e.g. token revoked); force full re-auth
                creds = None
                token_path.unlink(missing_ok=True)

        if not creds or not creds.valid:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"OAuth credentials not found at '{credentials_path}'.\n"
                    "Download the Desktop app client_secret.json from Google Cloud Console\n"
                    "and place it at credentials/client_secret.json."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), [_SHEETS_SCOPE]
            )
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "wb") as fh:
            pickle.dump(creds, fh)

    sheets_service = build("sheets", "v4", credentials=creds)

    # Print authenticated account for diagnostics
    try:
        id_info = build("oauth2", "v2", credentials=creds).userinfo().get().execute()
        print(f"  [auth] Authenticated as: {id_info.get('email', 'unknown')}")
    except Exception:
        pass

    return sheets_service


# ── Sheet enumeration ─────────────────────────────────────────────────────────

def load_mapping_tab(sheets_service, spreadsheet_id: str) -> dict:
    """
    Enumerate response tabs directly from spreadsheet metadata.

    Each tab is named 'Block1_V1' through 'Block3_V2'; no separate Mapping
    tab is present.  Sheet titles are normalised to canonical form_keys and
    returned keyed by their 1-based sheet index.

    Parameters
    ----------
    sheets_service  : authorised Sheets API service (from authenticate_google)
    spreadsheet_id  : str

    Returns
    -------
    mapping : dict
        {tab_title (str): form_key (str)}
        e.g. {"Block1_V1": "block_1_v1", "Block1_V2": "block_1_v2", ...}

    Notes
    -----
    Tabs whose titles cannot be parsed as a Block/Version name are silently
    skipped (e.g. helper sheets).
    """
    from googleapiclient.errors import HttpError as _HttpError
    try:
        meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    except _HttpError as exc:
        status = exc.resp.status
        if status == 403:
            raise PermissionError(
                f"Google Sheets API returned 403 for spreadsheet '{spreadsheet_id}'.\n"
                "Check that:\n"
                "  1. Google Sheets API is enabled in your GCP project\n"
                "     (console.cloud.google.com → APIs & Services → Enable APIs → 'Google Sheets API')\n"
                "  2. The authenticated account has at least Viewer access to the spreadsheet.\n"
                "  3. Delete credentials/token_sheets.json and re-run to force a fresh login."
            ) from exc
        if status == 404:
            raise FileNotFoundError(
                f"Spreadsheet not found (404): '{spreadsheet_id}'.\n"
                "Check that the SPREADSHEET_ID constant is correct and the account\n"
                "running this script has been granted access to the sheet."
            ) from exc
        raise
    sheets = meta.get("sheets", [])
    mapping: dict[str, str] = {}
    for sheet in sheets:
        title = sheet.get("properties", {}).get("title", "")
        try:
            mapping[title] = _normalise_form_key(title)
        except ValueError:
            pass  # skip non-response tabs
    return mapping


# ── Download ───────────────────────────────────────────────────────────────────

def download_tab_responses(
    sheets_service,
    spreadsheet_id: str,
    tab_name: str,
    raw_responses_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Download all rows from a named sheet tab and save a raw CSV snapshot.

    Parameters
    ----------
    sheets_service      : authorised Sheets API service
    spreadsheet_id      : str
    tab_name            : str  – exact tab name in the spreadsheet (e.g. 'Block1_V1')
    raw_responses_dir   : Path – directory where raw CSVs are written;
                          defaults to survey/raw_responses/

    Returns
    -------
    raw_df : pd.DataFrame
        DataFrame with first-row headers; all values as strings.
    """
    if raw_responses_dir is None:
        raw_responses_dir = Path("survey/raw_responses")

    result = (
        sheets_service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=tab_name)
        .execute()
    )
    rows = result.get("values", [])

    if not rows:
        return pd.DataFrame()

    headers = rows[0]
    data_rows = rows[1:]

    # Pad short rows to header length
    n_cols = len(headers)
    padded = [r + [""] * (n_cols - len(r)) for r in data_rows]

    raw_df = pd.DataFrame(padded, columns=headers)

    # Save snapshot
    safe_name = tab_name.replace(" ", "_")
    raw_responses_dir.mkdir(parents=True, exist_ok=True)
    raw_df.to_csv(raw_responses_dir / f"{safe_name}_raw.csv", index=False, encoding="utf-8")

    return raw_df


# ── Parsing ────────────────────────────────────────────────────────────────────

def _build_respondent_id(raw_df: pd.DataFrame, row_idx: int, form_key: str) -> str:
    """Return SHA-256 hash of email if available, else positional ID."""
    # Look for an email column (case-insensitive search)
    email_col = next(
        (c for c in raw_df.columns if "email" in c.lower()),
        None,
    )
    if email_col is not None:
        raw_email = str(raw_df.iloc[row_idx][email_col]).strip().lower()
        if raw_email and raw_email not in ("", "nan", "none"):
            return hashlib.sha256(raw_email.encode()).hexdigest()
    return f"{form_key}_row{(row_idx + 1):04d}"


def _parse_nrs(val) -> tuple[Optional[int], bool]:
    """
    Convert a raw NRS cell value to (int, nrs_invalid).

    Returns (pd.NA, True) for blanks or out-of-range values.
    """
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return pd.NA, True
    s = str(val).strip()
    if s == "" or s.lower() == "nan":
        return pd.NA, True
    # Extract leading integer (handles '3 - Neutral' format)
    m = re.match(r"^(-?\d+)", s)
    if not m:
        return pd.NA, True
    try:
        n = int(m.group(1))
    except ValueError:
        return pd.NA, True
    if not (_NRS_MIN <= n <= _NRS_MAX):
        return pd.NA, True
    return n, False


def parse_response_tab(raw_df: pd.DataFrame, form_key: str) -> pd.DataFrame:
    """
    Apply the confirmed column schema to a raw response tab DataFrame.

    Parameters
    ----------
    raw_df   : pd.DataFrame  – output of download_tab_responses()
    form_key : str           – normalised form key, e.g. 'block_1_v1'

    Returns
    -------
    long_df : pd.DataFrame
        One row per (respondent, scenario_position).  Column set defined by
        _PANEL_COLUMNS (minus metadata columns added later in merge_metadata).
    """
    m = re.match(r"block_(\d+)_v(\d+)", form_key)
    if not m:
        raise ValueError(f"Cannot parse block_id/version from form_key: {form_key!r}")
    block_id = int(m.group(1))
    version = int(m.group(2))
    is_pilot_block = block_id == 1

    n_cols = len(raw_df.columns)
    records = []

    for row_idx in range(len(raw_df)):
        row = raw_df.iloc[row_idx]
        resp_id = _build_respondent_id(raw_df, row_idx, form_key)

        # ── Fixed fields ──────────────────────────────────────────────────────
        def _get(pos: int):
            if pos < n_cols:
                v = row.iloc[pos]
                return None if (isinstance(v, float) and np.isnan(v)) else v
            return None

        raw_ts = _get(0)
        try:
            ts = pd.to_datetime(raw_ts)
        except Exception:
            ts = pd.NaT

        yoe_raw = str(_get(1)).strip() if _get(1) is not None else ""
        yoe_entry = _EXPERIENCE_MAP.get(_norm_exp(yoe_raw))
        yoe = yoe_entry[0] if yoe_entry else np.nan          # midpoint
        yoe_label = yoe_raw if yoe_raw else pd.NA             # original label

        # ── NRS columns (positional 8–15) ─────────────────────────────────────
        nrs_vals = []
        nrs_invalids = []
        for pos in range(_NRS_COL_START, _NRS_COL_END):
            raw_val = _get(pos)
            nrs_val, invalid = _parse_nrs(raw_val)
            nrs_vals.append(nrs_val)
            nrs_invalids.append(invalid)

        # ── Pilot columns (positions 18–23, Block 1 only) ─────────────────────
        pilot_data: dict = {}
        if is_pilot_block:
            for field, pos in _PILOT_COL_INDICES.items():
                v = _get(pos)
                pilot_data[field] = (
                    pd.NA if (v is None or str(v).strip() in ("", "nan")) else str(v)
                )
        else:
            for field in _PILOT_COL_INDICES:
                pilot_data[field] = pd.NA

        # ── One row per scenario position (melt NRS) ──────────────────────────
        for pos_idx in range(8):
            records.append(
                {
                    "respondent_id": resp_id,
                    "form_key": form_key,
                    "block_id": block_id,
                    "version": version,
                    "timestamp": ts,
                    "years_experience": yoe,
                    "years_experience_label": yoe_label,
                    "aum_category": str(_get(2)) if _get(2) is not None else pd.NA,
                    "institution_type": str(_get(3)) if _get(3) is not None else pd.NA,
                    "investment_mandate": str(_get(4)) if _get(4) is not None else pd.NA,
                    "geographic_focus": str(_get(5)) if _get(5) is not None else pd.NA,
                    "discretionary_authority": str(_get(6)) if _get(6) is not None else pd.NA,
                    "certifications": str(_get(7)) if _get(7) is not None else pd.NA,
                    "manipulation_check": str(_get(16)) if _get(16) is not None else pd.NA,
                    "usefulness_rating": str(_get(17)) if _get(17) is not None else pd.NA,
                    "is_pilot_block": is_pilot_block,
                    **pilot_data,
                    "scenario_position": pos_idx + 1,
                    "nrs": nrs_vals[pos_idx],
                    "nrs_invalid": nrs_invalids[pos_idx],
                    # metadata placeholders (filled by merge_metadata)
                    "scenario_id": pd.NA,
                    "show_sc": pd.NA,
                    "show_sc_conflict": False,
                    "metadata_join_failed": False,
                    "ticker": pd.NA,
                    "company_name": pd.NA,
                    "gics_sector": pd.NA,
                    "event_date": pd.NA,
                    "event_type": pd.NA,
                    "sc_total": pd.NA,
                    "ac_e": pd.NA,
                    "se_e": pd.NA,
                    "ai_e": pd.NA,
                    "es_raw": pd.NA,
                    "market_regime": pd.NA,
                }
            )

    if not records:
        return pd.DataFrame(columns=_PANEL_COLUMNS)

    return pd.DataFrame(records)


# ── Validation and exclusion ───────────────────────────────────────────────────

def validate_and_exclude(
    df: pd.DataFrame,
    years_of_experience_range_filter
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply per-respondent exclusion rules and split into clean and excluded sets.

    Exclusion rules (evaluated per respondent_id):
      1. Fewer than 8 non-null nrs values   → exclusion_reason = "incomplete"
      2. years_experience < 5               → exclusion_reason = "experience<5"
      3. Any nrs_invalid = True             → exclusion_reason = "nrs_invalid"

    Rules are applied in the order listed; a respondent flagged by rule 1 is not
    re-examined by rules 2 or 3 (first matching rule wins).

    Parameters
    ----------
    df : pd.DataFrame  – concatenated output of parse_response_tab() calls

    Returns
    -------
    (clean_df, excluded_df) : tuple
        excluded_df has an added 'exclusion_reason' column.
    """
    if df.empty:
        excluded_empty = df.copy()
        excluded_empty["exclusion_reason"] = pd.Series(dtype="object")
        return df, excluded_empty

    exclusion_reasons: dict[str, str] = {}

    for resp_id, grp in df.groupby("respondent_id"):
        # Rule 1: completeness
        n_valid_nrs = grp["nrs"].notna().sum()
        if n_valid_nrs < 8:
            exclusion_reasons[resp_id] = "incomplete"
            continue

        # Rule 2: experience — use the minimum of the stated range so that
        # ambiguous categories like "2–5" (min=2) are excluded conservatively.
        yoe_label = grp["years_experience_label"].dropna().iloc[0] if grp["years_experience_label"].dropna().size > 0 else ""
        yoe_entry = _EXPERIENCE_MAP.get(_norm_exp(str(yoe_label)))
        yoe_min = yoe_entry[1] if yoe_entry else np.nan
        if np.isnan(yoe_min) or yoe_min < years_of_experience_range_filter:
            exclusion_reasons[resp_id] = "experience<" + str(years_of_experience_range_filter)
            continue

        # Rule 3: any invalid NRS
        if grp["nrs_invalid"].any():
            exclusion_reasons[resp_id] = "nrs_invalid"

    excluded_ids = set(exclusion_reasons.keys())
    clean_df = df[~df["respondent_id"].isin(excluded_ids)].copy().reset_index(drop=True)
    excl_df = df[df["respondent_id"].isin(excluded_ids)].copy().reset_index(drop=True)
    excl_df["exclusion_reason"] = excl_df["respondent_id"].map(exclusion_reasons)

    return clean_df, excl_df


# ── Metadata merge ─────────────────────────────────────────────────────────────

def merge_metadata(
    responses_df: pd.DataFrame,
    metadata_path: Path,
    counterbalancing_path: Path,
    join_failures_path: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Attach scenario identity and metadata to the long-format responses DataFrame.

    Steps
    -----
    1. Load counterbalancing_matrix.csv; normalise respondent_block → form_key.
    2. Join on (form_key, scenario_position) → scenario_id, show_sc (ground truth).
    3. Load scenario_metadata.csv; join on scenario_id → ticker, event_date, etc.
    4. Flag show_sc conflicts (matrix value always wins).
    5. Write unmatched rows to join_failures_path for inspection.

    Parameters
    ----------
    responses_df          : pd.DataFrame  – clean output of validate_and_exclude()
    metadata_path         : Path          – survey/metadata/scenario_metadata.csv
    counterbalancing_path : Path          – survey/counterbalancing/counterbalancing_matrix.csv
    join_failures_path    : Path | None   – where to write join failure rows
                            (defaults to results/join_failures.csv)

    Returns
    -------
    merged_df : pd.DataFrame
    """
    if join_failures_path is None:
        join_failures_path = Path("results/join_failures.csv")

    if responses_df.empty:
        return responses_df.copy()

    # ── Counterbalancing matrix ───────────────────────────────────────────────
    cb = pd.read_csv(counterbalancing_path)
    # Normalise respondent_block → form_key
    cb["form_key"] = cb["respondent_block"].apply(_normalise_form_key)
    # Rename presentation_order → scenario_position for the join
    cb = cb.rename(columns={"presentation_order": "scenario_position"})
    cb = cb[["form_key", "scenario_position", "scenario_id", "show_sc"]].copy()
    cb["scenario_position"] = cb["scenario_position"].astype(int)
    cb["show_sc"] = cb["show_sc"].astype(int)

    # Drop existing placeholder columns before merge
    drop_cols = [c for c in ["scenario_id", "show_sc", "show_sc_conflict", "metadata_join_failed"]
                 if c in responses_df.columns]
    df = responses_df.drop(columns=drop_cols).copy()
    df["scenario_position"] = df["scenario_position"].astype(int)

    merged = df.merge(
        cb,
        on=["form_key", "scenario_position"],
        how="left",
        suffixes=("", "_matrix"),
    )

    # Flag rows with no CB match
    merged["metadata_join_failed"] = merged["scenario_id"].isna()
    merged["show_sc_conflict"] = False

    # ── Scenario metadata ─────────────────────────────────────────────────────
    meta = pd.read_csv(metadata_path)
    # Columns available in metadata CSV (others will be pd.NA)
    meta_cols_available = [
        c for c in [
            "scenario_id", "ticker", "company_name", "gics_sector",
            "event_date", "event_type", "sc_total", "ac_e", "se_e",
            "ai_e", "es_raw", "market_regime",
        ]
        if c in meta.columns
    ]
    meta_subset = meta[meta_cols_available].copy()

    # Drop placeholder columns before merge
    drop_meta = [c for c in meta_subset.columns if c != "scenario_id" and c in merged.columns]
    merged = merged.drop(columns=drop_meta)

    merged = merged.merge(meta_subset, on="scenario_id", how="left")

    # Ensure all metadata columns exist (fill with NA if not in CSV yet)
    for col in ["sc_total", "ac_e", "se_e", "ai_e", "es_raw", "market_regime"]:
        if col not in merged.columns:
            merged[col] = pd.NA

    # ── Write join failures ───────────────────────────────────────────────────
    failed = merged[merged["metadata_join_failed"]].copy()
    if not failed.empty:
        join_failures_path.parent.mkdir(parents=True, exist_ok=True)
        failed.to_csv(join_failures_path, index=False)

    return merged


# ── Panel construction ─────────────────────────────────────────────────────────

def build_analysis_panel(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce final column order and types.

    Parameters
    ----------
    merged_df : pd.DataFrame  – output of merge_metadata()

    Returns
    -------
    panel_df : pd.DataFrame
        Columns in _PANEL_COLUMNS order; float64 for continuous numerics,
        Int64 (nullable) for integers.
    """
    df = merged_df.copy()

    # Ensure all panel columns exist
    for col in _PANEL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[_PANEL_COLUMNS].copy()

    # Enforce dtypes
    df["nrs"] = pd.array(df["nrs"], dtype="Int64")
    df["block_id"] = pd.array(df["block_id"], dtype="Int64")
    df["version"] = pd.array(df["version"], dtype="Int64")
    df["scenario_position"] = pd.array(df["scenario_position"], dtype="Int64")

    for col in ["show_sc"]:
        if col in df.columns:
            df[col] = pd.array(df[col], dtype="Int64")

    for col in ["years_experience", "sc_total", "ac_e", "se_e", "ai_e", "es_raw"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

    df["nrs_invalid"] = df["nrs_invalid"].astype(bool)
    df["show_sc_conflict"] = df["show_sc_conflict"].astype(bool)
    df["metadata_join_failed"] = df["metadata_join_failed"].astype(bool)
    df["is_pilot_block"] = df["is_pilot_block"].astype(bool)

    return df


# ── QC report ─────────────────────────────────────────────────────────────────

def write_qc_report(
    clean_df: pd.DataFrame,
    excluded_df: pd.DataFrame,
    raw_counts: dict,
    output_path: Path,
    spreadsheet_id: str = "",
) -> None:
    """
    Write the analysis_panel_comments.md QC/audit report.

    Parameters
    ----------
    clean_df        : pd.DataFrame  – final analysis panel
    excluded_df     : pd.DataFrame  – excluded respondents with exclusion_reason
    raw_counts      : dict          – {tab_name: row_count} before processing
    output_path     : Path          – write destination
    spreadsheet_id  : str           – logged in run metadata section
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []

    def _h(n: int, title: str) -> str:
        return f"{'#' * n} {title}"

    lines.append(_h(1, "Survey Data Processing QC Report"))
    lines.append("")

    # ── Section 1: Run metadata ───────────────────────────────────────────────
    lines.append(_h(2, "1. Run Metadata"))
    lines.append("")
    lines.append(f"- **Generated:** {now}")
    lines.append(f"- **Spreadsheet ID:** `{spreadsheet_id}`")
    tabs_processed = list(raw_counts.keys())
    lines.append(f"- **Tabs processed:** {', '.join(tabs_processed) if tabs_processed else 'none'}")
    lines.append("")

    # ── Section 2: Raw download summary ──────────────────────────────────────
    lines.append(_h(2, "2. Raw Download Summary"))
    lines.append("")
    lines.append("| Tab | Raw rows |")
    lines.append("|-----|----------|")
    total_raw = 0
    for tab, cnt in raw_counts.items():
        lines.append(f"| {tab} | {cnt} |")
        total_raw += cnt
    lines.append(f"| **Total** | **{total_raw}** |")
    lines.append("")

    # ── Section 3: Exclusion log ──────────────────────────────────────────────
    lines.append(_h(2, "3. Exclusion Log"))
    lines.append("")
    if excluded_df.empty or "exclusion_reason" not in excluded_df.columns:
        excl_counts: dict[str, int] = {}
    else:
        excl_counts = (
            excluded_df.drop_duplicates("respondent_id")["exclusion_reason"]
            .value_counts()
            .to_dict()
        )
    total_excl = sum(excl_counts.values())
    lines.append(f"Total excluded respondents: **{total_excl}**")
    lines.append("")
    if excl_counts:
        lines.append("| Exclusion reason | N respondents |")
        lines.append("|------------------|--------------|")
        for reason, cnt in excl_counts.items():
            lines.append(f"| {reason} | {cnt} |")
    else:
        lines.append("No respondents excluded.")
    lines.append("")

    # ── Section 4: Final panel summary ───────────────────────────────────────
    lines.append(_h(2, "4. Final Panel Summary"))
    lines.append("")
    if clean_df.empty:
        n_resp = 0
        n_obs = 0
        nrs_desc = "N/A"
        show_sc_0 = 0
        show_sc_1 = 0
        scenarios_covered = 0
    else:
        n_resp = clean_df["respondent_id"].nunique()
        n_obs = len(clean_df)
        nrs_valid = clean_df["nrs"].dropna()
        nrs_desc = (
            f"mean={float(nrs_valid.mean()):.4f}, "
            f"sd={float(nrs_valid.std()):.4f}, "
            f"min={int(nrs_valid.min())}, max={int(nrs_valid.max())}"
            if len(nrs_valid) > 0
            else "N/A"
        )
        show_sc_0 = int((clean_df["show_sc"] == 0).sum())
        show_sc_1 = int((clean_df["show_sc"] == 1).sum())
        scenarios_covered = clean_df["scenario_id"].nunique()

    lines.append(f"- **N respondents:** {n_resp}")
    lines.append(f"- **N observations:** {n_obs}")
    lines.append(f"- **NRS distribution:** {nrs_desc}")
    lines.append(f"- **ShowSC = 0:** {show_sc_0} observations")
    lines.append(f"- **ShowSC = 1:** {show_sc_1} observations")
    lines.append(f"- **Scenarios covered:** {scenarios_covered} / 24")
    lines.append("")

    # ── Section 5: Pilot block summary ───────────────────────────────────────
    lines.append(_h(2, "5. Pilot Block Summary"))
    lines.append("")
    pilot_rows = clean_df[clean_df["is_pilot_block"]] if not clean_df.empty else pd.DataFrame()
    pilot_resp = pilot_rows["respondent_id"].nunique() if not pilot_rows.empty else 0

    if pilot_resp == 0:
        lines.append("No Block 1 (pilot) respondents in the current dataset.")
    else:
        lines.append(f"Block 1 respondents: **{pilot_resp}**")
        lines.append("")
        # Completion time
        ct = pilot_rows.drop_duplicates("respondent_id")["completion_time"].dropna()
        if not ct.empty:
            lines.append(f"- **Completion time responses:** {len(ct)} (values: {', '.join(ct.unique()[:10].tolist())})")
        # Clarity distribution
        for field, label in [
            ("pilot_clarity", "Clarity"),
            ("pilot_realism", "Realism"),
            ("pilot_dashboard_ease", "Dashboard ease"),
        ]:
            col_data = pilot_rows.drop_duplicates("respondent_id")[field].dropna()
            if not col_data.empty:
                dist = col_data.value_counts().to_dict()
                dist_str = "; ".join(f"{k}: {v}" for k, v in dist.items())
                lines.append(f"- **{label}:** {dist_str}")
    lines.append("")

    # ── Section 6: Warnings ───────────────────────────────────────────────────
    lines.append(_h(2, "6. Warnings"))
    lines.append("")
    warnings: list[str] = []

    if not clean_df.empty:
        n_conflict = int(clean_df["show_sc_conflict"].sum())
        if n_conflict > 0:
            warnings.append(f"show_sc_conflict: {n_conflict} observations where response show_sc differed from matrix (matrix value used).")

        n_join_fail = int(clean_df["metadata_join_failed"].sum())
        if n_join_fail > 0:
            warnings.append(f"metadata_join_failed: {n_join_fail} observations could not be matched to counterbalancing matrix. See results/join_failures.csv.")

        # Scenarios with zero responses
        all_scenario_ids = [
            f"B{b}_S{str(s).zfill(2)}"
            for b in range(1, 4)
            for s in range(1, 9)
        ]
        covered = set(clean_df["scenario_id"].dropna().unique())
        zero_coverage = [sid for sid in all_scenario_ids if sid not in covered]
        if zero_coverage:
            warnings.append(f"Scenarios with 0 responses ({len(zero_coverage)}): {', '.join(zero_coverage)}.")

    if warnings:
        for w in warnings:
            lines.append(f"- WARNING: {w}")
    else:
        lines.append("No warnings.")
    lines.append("")

    # ── Section 7: Preliminary data notice ───────────────────────────────────
    lines.append(_h(2, "7. Preliminary Data Notice"))
    lines.append("")
    lines.append(
        "> NOTE: Results are based on preliminary data collected during the pilot and\n"
        "> early main survey phases. All figures and tables derived from `analysis_panel.csv`\n"
        "> are subject to revision upon completion of the full survey sample (target N = 100)."
    )
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
