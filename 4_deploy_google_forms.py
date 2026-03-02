"""4_deploy_google_forms.py

Programmatic Google Forms survey deployment for the Shock Score thesis study.

Creates 3 Google Forms (one per scenario block), uploads all survey images to
Google Drive, and populates each form with demographics, scenario pages, and
final questions using the Google Forms API v1 and Google Drive API v3.

Usage:
    python 4_deploy_google_forms.py                  # 3 forms, one per block (V1 version)
    python 4_deploy_google_forms.py --sub-blocks 2   # 6 forms (V1 + V2 per block)
    python 4_deploy_google_forms.py --sub-blocks 4   # 12 forms (all 4 versions per block)
    python 4_deploy_google_forms.py --dry-run        # print structure without API calls

Prerequisites:
    credentials/client_secret.json   -- Google Cloud OAuth2 Desktop app credentials
    Enabled APIs: Google Forms API, Google Drive API
    Packages: google-auth-oauthlib google-auth-httplib2 google-api-python-client
    Survey assets: run 3_survey_assembly.py first to generate survey/ directory
"""

import argparse
import json
import os
import pickle
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive.file",
]

TOKEN_PATH = "credentials/token.json"
SECRET_PATH = "credentials/client_secret.json"

SURVEY_DIR = Path("survey")
CHARTS_DIR = SURVEY_DIR / "charts"
DASHBOARDS_DIR = SURVEY_DIR / "dashboards"
METADATA_DIR = SURVEY_DIR / "metadata"
CB_DIR = SURVEY_DIR / "counterbalancing"
DEPLOYMENT_MANIFEST_PATH = SURVEY_DIR / "deployment_manifest.json"

FORM_DESCRIPTION = (
    "This survey is part of an academic research study on how equity portfolio managers "
    "respond to financial information events. You will review investment scenarios and "
    "indicate your intended portfolio adjustment for each. The survey takes approximately "
    "20\u201325 minutes. Your responses are anonymous and confidential."
)

# Portfolio context: equal-weight portfolio of PORTFOLIO_N stocks (per presentation protocol)
PORTFOLIO_N = 30

DRIVE_FOLDER_NAME = "Thesis Survey \u2013 Block Images"

# Google Forms API rate limit: sleep between batchUpdate calls
API_SLEEP = 1.0  # seconds

# Benzinga headline metadata prefix: optional {A:...:L:...}! or bare !
_BZ_PREFIX_RE = re.compile(r"^(?:\{[^}]*\})?!")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def get_credentials():
    """Return valid OAuth2 credentials, refreshing or re-authorising as needed."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as fh:
            creds = pickle.load(fh)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(SECRET_PATH):
                raise FileNotFoundError(
                    f"OAuth credentials not found at '{SECRET_PATH}'.\n"
                    "Download the Desktop app client_secret.json from Google Cloud Console\n"
                    "and place it at credentials/client_secret.json."
                )
            flow = InstalledAppFlow.from_client_secrets_file(SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "wb") as fh:
            pickle.dump(creds, fh)

    return creds


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_survey_data():
    """
    Load all survey metadata CSVs.
    Returns (meta_idx, news_idx, reaction_idx, shock_idx, assembly_guide)
    where *_idx DataFrames are indexed by scenario_id for O(1) lookup.
    """
    meta_idx = pd.read_csv(METADATA_DIR / "scenario_metadata.csv").set_index("scenario_id")
    news_idx = pd.read_csv(METADATA_DIR / "scenario_news_text.csv").set_index("scenario_id")
    reaction_idx = pd.read_csv(METADATA_DIR / "scenario_price_reaction.csv").set_index("scenario_id")
    shock_idx = pd.read_csv(METADATA_DIR / "scenario_shock_score.csv").set_index("scenario_id")
    assembly_guide = pd.read_csv(CB_DIR / "form_assembly_guide.csv")
    return meta_idx, news_idx, reaction_idx, shock_idx, assembly_guide


# ---------------------------------------------------------------------------
# Headline cleaning
# ---------------------------------------------------------------------------

def clean_headline(raw):
    """Strip Benzinga metadata prefix ({A:...:L:...}! or bare !) from a headline string."""
    if pd.isna(raw):
        return ""
    return _BZ_PREFIX_RE.sub("", str(raw)).strip()


# ---------------------------------------------------------------------------
# Google Drive helpers
# ---------------------------------------------------------------------------

def _drive_list(drive_service, q, fields="files(id, name)"):
    """Execute a Drive files.list query and return the files list."""
    return drive_service.files().list(
        q=q, fields=fields, spaces="drive"
    ).execute().get("files", [])


def find_drive_folder(drive_service, name):
    """Return the Drive folder ID if a folder with `name` exists, else None."""
    try:
        safe = name.replace("'", "\\'")
        files = _drive_list(
            drive_service,
            f"name='{safe}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        )
        return files[0]["id"] if files else None
    except HttpError as exc:
        print(f"  [WARN] Could not search for existing folder: {exc}")
        return None


def create_drive_folder(drive_service, name):
    """Create a Drive folder and return its ID. Idempotent: reuses an existing folder."""
    existing_id = find_drive_folder(drive_service, name)
    if existing_id:
        print(f"  [Drive] Reusing existing folder '{name}' ({existing_id})")
        return existing_id
    folder = drive_service.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder"},
        fields="id",
    ).execute()
    folder_id = folder["id"]
    print(f"  [Drive] Created folder '{name}' ({folder_id})")
    return folder_id


def find_drive_file(drive_service, filename, folder_id):
    """Return the Drive file ID if `filename` already exists in `folder_id`, else None."""
    try:
        safe = filename.replace("'", "\\'")
        files = _drive_list(
            drive_service,
            f"name='{safe}' and '{folder_id}' in parents and trashed=false",
        )
        return files[0]["id"] if files else None
    except HttpError as exc:
        print(f"  [WARN] Could not search for existing file '{filename}': {exc}")
        return None


def upload_image(drive_service, filepath, folder_id):
    """
    Upload a PNG to Google Drive and return its public URL.
    Idempotent: if the file already exists in the folder, returns the existing URL.
    Sets "anyone with link can view" permission so the Forms API can embed it.
    """
    filename = filepath.name
    existing_id = find_drive_file(drive_service, filename, folder_id)
    if existing_id:
        return f"https://drive.google.com/uc?id={existing_id}"

    media = MediaFileUpload(str(filepath), mimetype="image/png", resumable=False)
    uploaded = drive_service.files().create(
        body={"name": filename, "parents": [folder_id]},
        media_body=media,
        fields="id",
    ).execute()
    file_id = uploaded["id"]

    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"


def upload_block_images(drive_service, block_id, folder_id, scenario_ids, dry_run=False):
    """
    Upload all chart and dashboard PNGs for a block to Drive.
    Returns {scenario_id: {"chart_url": ..., "dashboard_url": ...}}.
    Idempotent: skips files that are already present in the folder.
    """
    image_urls = {}
    uploaded_count = 0

    for sid in scenario_ids:
        chart_path = CHARTS_DIR / f"chart_{sid}.png"
        dashboard_path = DASHBOARDS_DIR / f"dashboard_{sid}.png"

        if dry_run:
            image_urls[sid] = {
                "chart_url": f"[DRY-RUN:{chart_path}]",
                "dashboard_url": f"[DRY-RUN:{dashboard_path}]",
            }
            continue

        chart_url = None
        dashboard_url = None

        if chart_path.exists():
            try:
                chart_url = upload_image(drive_service, chart_path, folder_id)
                uploaded_count += 1
            except HttpError as exc:
                print(f"  [ERROR] Failed to upload {chart_path.name}: {exc}")
        else:
            print(f"  [WARN] Chart not found: {chart_path}")

        if dashboard_path.exists():
            try:
                dashboard_url = upload_image(drive_service, dashboard_path, folder_id)
                uploaded_count += 1
            except HttpError as exc:
                print(f"  [ERROR] Failed to upload {dashboard_path.name}: {exc}")
        else:
            print(f"  [WARN] Dashboard not found: {dashboard_path}")

        image_urls[sid] = {"chart_url": chart_url, "dashboard_url": dashboard_url}

    if not dry_run:
        print(f"  Block {block_id}: {uploaded_count} images uploaded/reused "
              f"({len(scenario_ids)} scenarios)")

    return image_urls


# ---------------------------------------------------------------------------
# Forms API – low-level request builders
# ---------------------------------------------------------------------------

def _page_break_req(title, description, idx):
    return {"createItem": {
        "item": {"title": title, "description": description, "pageBreakItem": {}},
        "location": {"index": idx},
    }}


def _text_req(title, description, idx):
    return {"createItem": {
        "item": {"title": title, "description": description, "textItem": {}},
        "location": {"index": idx},
    }}


def _image_req(title, source_uri, alt_text, idx):
    return {"createItem": {
        "item": {
            "title": title,
            "imageItem": {"image": {"sourceUri": source_uri, "altText": alt_text}},
        },
        "location": {"index": idx},
    }}


def _radio_req(title, options, required, idx):
    return {"createItem": {
        "item": {
            "title": title,
            "questionItem": {"question": {
                "required": required,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [{"value": o} for o in options],
                },
            }},
        },
        "location": {"index": idx},
    }}


def _checkbox_req(title, options, required, idx):
    return {"createItem": {
        "item": {
            "title": title,
            "questionItem": {"question": {
                "required": required,
                "choiceQuestion": {
                    "type": "CHECKBOX",
                    "options": [{"value": o} for o in options],
                },
            }},
        },
        "location": {"index": idx},
    }}


def _scale_req(title, low, high, low_label, high_label, required, idx):
    return {"createItem": {
        "item": {
            "title": title,
            "questionItem": {"question": {
                "required": required,
                "scaleQuestion": {
                    "low": low,
                    "high": high,
                    "lowLabel": low_label,
                    "highLabel": high_label,
                },
            }},
        },
        "location": {"index": idx},
    }}


# ---------------------------------------------------------------------------
# Section builders – return (requests_list, next_index)
# ---------------------------------------------------------------------------

def build_demographics_requests(start_idx=0):
    """
    Build batchUpdate requests for the demographics section.
    Includes updateFormInfo for the form description, then the demographics items.
    Returns (requests, next_available_index).
    """
    reqs = []
    idx = start_idx

    # Set form description (combined with demographics to save one API call)
    reqs.append({
        "updateFormInfo": {
            "info": {"description": FORM_DESCRIPTION},
            "updateMask": "description",
        }
    })

    reqs.append(_page_break_req(
        title="Section 1: Professional Profile",
        description="Please answer the following questions about your professional background.",
        idx=idx,
    ))
    idx += 1

    reqs.append(_radio_req(
        title="Years of portfolio management experience",
        options=["Less than 2", "2\u20135", "6\u201310", "11\u201320", "More than 20"],
        required=True,
        idx=idx,
    ))
    idx += 1

    reqs.append(_radio_req(
        title="Approximate assets under management (USD)",
        options=[
            "Less than $50M",
            "$50M\u2013$500M",
            "$500M\u2013$2B",
            "$2B\u2013$10B",
            "More than $10B",
        ],
        required=True,
        idx=idx,
    ))
    idx += 1

    reqs.append(_radio_req(
        title="Institution type",
        options=[
            "Asset manager",
            "Hedge fund",
            "Pension/endowment fund",
            "Bank/private bank",
            "Family office",
            "Independent/RIA",
            "Other",
        ],
        required=True,
        idx=idx,
    ))
    idx += 1

    reqs.append(_radio_req(
        title="Primary investment mandate",
        options=["Equity long-only", "Equity long-short", "Multi-asset", "Other"],
        required=True,
        idx=idx,
    ))
    idx += 1

    reqs.append(_radio_req(
        title="Geographic market focus",
        options=[
            "United States",
            "Europe",
            "Asia-Pacific",
            "Global/multi-region",
            "Other",
        ],
        required=True,
        idx=idx,
    ))
    idx += 1

    reqs.append(_radio_req(
        title="Level of discretionary authority",
        options=["Full discretion", "Partial (committee-based)", "Advisory only"],
        required=True,
        idx=idx,
    ))
    idx += 1

    reqs.append(_checkbox_req(
        title="Professional certifications (select all that apply)",
        options=["CFA", "FRM", "CAIA", "CPA", "None", "Other"],
        required=False,
        idx=idx,
    ))
    idx += 1

    return reqs, idx


def build_scenario_requests(
    scenario_num,
    total_scenarios,
    scenario_id,
    show_sc,
    meta_idx,
    news_idx,
    reaction_idx,
    image_urls,
    start_idx,
):
    """
    Build batchUpdate requests for one scenario page (page break + all scenario items).
    Returns (requests, next_available_index).
    Raises KeyError if scenario_id is missing from any metadata table.
    """
    reqs = []
    idx = start_idx

    row_meta = meta_idx.loc[scenario_id]
    row_news = news_idx.loc[scenario_id]
    row_reaction = reaction_idx.loc[scenario_id]
    urls = image_urls.get(scenario_id, {})

    company_name = row_meta["company_name"]
    ticker = row_meta["ticker"]
    gics_sector = row_meta["gics_sector"]

    # Headline: strip BZ metadata prefix
    headline = clean_headline(row_news["headline"])

    # Summary paragraph: use placeholder if not yet generated
    summary_para = str(row_news.get("summary_paragraph", "")).strip()
    if summary_para in ("[TO BE GENERATED]", "nan", ""):
        summary_para = "[Summary paragraph to be populated before final deployment]"

    reaction_pct = float(row_reaction["price_reaction_pct"])
    reaction_window = row_reaction["reaction_window"]
    num_articles = int(row_news["num_articles"])

    chart_url = urls.get("chart_url")
    dashboard_url = urls.get("dashboard_url")

    # 1. Page break
    reqs.append(_page_break_req(
        title=f"Scenario {scenario_num} of {total_scenarios}",
        description="",
        idx=idx,
    ))
    idx += 1

    # 2. Portfolio context statement (identical across all scenarios – §3.4)
    reqs.append(_text_req(
        title="Portfolio context",
        description=(
            f"You manage a diversified equity portfolio with equal weights across "
            f"{PORTFOLIO_N} stocks. The following event has occurred for one of your holdings."
        ),
        idx=idx,
    ))
    idx += 1

    # 3. Stock identification: company name, ticker, sector
    reqs.append(_text_req(
        title="Holding",
        description=f"{company_name} ({ticker})  \u00b7  {gics_sector}",
        idx=idx,
    ))
    idx += 1

    # 4. Trailing price chart
    if chart_url:
        reqs.append(_image_req(
            title="Trailing Price Chart (20 trading days before event, rebased to 100)",
            source_uri=chart_url,
            alt_text=f"20-day trailing indexed price chart for {ticker} before the event",
            idx=idx,
        ))
        idx += 1

    # 5. News event – calibrate title to num_articles per §3.5 of presentation protocol
    if num_articles >= 6:
        news_title = f"News Event  \u00b7  Covered by {num_articles} financial news sources"
    elif num_articles >= 3:
        news_title = "News Event  \u00b7  Reported by multiple sources"
    else:
        news_title = "News Event"

    news_body = headline
    if summary_para:
        news_body = f"{headline}\n\n{summary_para}" if headline else summary_para

    reqs.append(_text_req(title=news_title, description=news_body, idx=idx))
    idx += 1

    # 6. Immediate price reaction
    sign = "+" if reaction_pct >= 0 else ""
    reqs.append(_text_req(
        title="Immediate price reaction",
        description=f"{sign}{reaction_pct:.2f}% ({reaction_window})",
        idx=idx,
    ))
    idx += 1

    # 7. Shock Score dashboard (treatment condition only: show_sc == 1)
    if show_sc == 1 and dashboard_url:
        reqs.append(_image_req(
            title="Shock Score Dashboard",
            source_uri=dashboard_url,
            alt_text=(
                "Shock Score dashboard displaying sentiment direction, shock severity level, "
                "persistence horizon bucket, and pre-commitment protocol recommendation"
            ),
            idx=idx,
        ))
        idx += 1

    # 8. NRS response scale (1 = strongly reduce, 7 = strongly increase)
    reqs.append(_scale_req(
        title=(
            "Based on the information above, what would be your intended portfolio "
            "adjustment for this holding?"
        ),
        low=1,
        high=7,
        low_label="Strongly reduce exposure",
        high_label="Strongly increase exposure",
        required=True,
        idx=idx,
    ))
    idx += 1

    return reqs, idx


def build_final_questions_requests(start_idx):
    """
    Build batchUpdate requests for the post-scenario manipulation check section.
    Returns (requests, next_available_index).
    """
    reqs = []
    idx = start_idx

    reqs.append(_page_break_req(
        title="Final Questions",
        description="Please answer the following two questions before submitting.",
        idx=idx,
    ))
    idx += 1

    reqs.append(_radio_req(
        title=(
            "Did you notice that some scenarios included an additional "
            "decision-support dashboard while others did not?"
        ),
        options=["Yes", "No", "Unsure"],
        required=True,
        idx=idx,
    ))
    idx += 1

    reqs.append(_scale_req(
        title=(
            "If you noticed the dashboard, how useful did you find it "
            "for informing your decisions?"
        ),
        low=1,
        high=5,
        low_label="Not at all useful",
        high_label="Extremely useful",
        required=True,
        idx=idx,
    ))
    idx += 1

    return reqs, idx


# ---------------------------------------------------------------------------
# Forms API – form creation and population
# ---------------------------------------------------------------------------

def create_form_shell(forms_service, block_id, version):
    """Create a new Google Form (title only) and return its form ID."""
    if version == 1:
        title = f"Portfolio Decision Survey \u2013 Block {block_id}"
    else:
        title = f"Portfolio Decision Survey \u2013 Block {block_id} (Version {version})"
    body = {"info": {"title": title, "documentTitle": title}}
    form = forms_service.forms().create(body=body).execute()
    return form["formId"]


def batch_update(forms_service, form_id, requests_list, label):
    """
    Execute a batchUpdate call. Prints an error and returns False on failure
    rather than raising, so the caller can continue with remaining sections.
    """
    if not requests_list:
        return True
    try:
        forms_service.forms().batchUpdate(
            formId=form_id, body={"requests": requests_list}
        ).execute()
        return True
    except HttpError as exc:
        print(f"  [ERROR] batchUpdate failed for '{label}': {exc}")
        return False


def try_publish_form(forms_service, form_id):
    """
    Attempt to mark the form as non-quiz (ensure it is in survey mode).
    Separately warns the user about the Google Forms publish requirement
    that takes effect after 31 March 2026.
    """
    try:
        forms_service.forms().batchUpdate(
            formId=form_id,
            body={"requests": [{"updateSettings": {
                "settings": {"quizSettings": {"isQuiz": False}},
                "updateMask": "quizSettings.isQuiz",
            }}]},
        ).execute()
    except HttpError:
        pass  # quizSettings update may fail for non-quiz forms; not critical

    print(
        "  [NOTE] After 31 March 2026, new Google Forms are unpublished by default.\n"
        "         If the form does not accept responses, open it in Google Forms and\n"
        "         click 'Publish' -> 'Publish to all users' to enable response collection."
    )


# ---------------------------------------------------------------------------
# Top-level form deployment
# ---------------------------------------------------------------------------

def deploy_one_form(
    forms_service,
    block_id,
    version,
    assembly_guide,
    meta_idx,
    news_idx,
    reaction_idx,
    image_urls,
    dry_run=False,
):
    """
    Create and populate one Google Form for the given block/version.
    Returns a dict with form_id, edit_url, responder_url (or DRY-RUN placeholders).
    """
    respondent_block = f"Block{block_id}_V{version}"
    guide = (
        assembly_guide[assembly_guide["respondent_block"] == respondent_block]
        .sort_values("presentation_order")
        .reset_index(drop=True)
    )

    if guide.empty:
        print(f"  [WARN] No scenarios found for {respondent_block} – skipping.")
        return {}

    total_scenarios = len(guide)
    version_label = f"Block {block_id}" + (f" V{version}" if version > 1 else "")
    print(f"\n  > {version_label}  ({total_scenarios} scenarios)")

    if dry_run:
        print(f"    Form title: 'Portfolio Decision Survey -- Block {block_id}"
              + (f" (Version {version})'" if version > 1 else "'"))
        print(f"    Demographics: 8 items (section header + 7 questions)")
        for pos, row in guide.iterrows():
            sc_label = "SC shown" if int(row["show_sc"]) == 1 else "control"
            n_items = 8 if int(row["show_sc"]) == 1 else 7
            print(f"    [{pos+1:2d}] {row['scenario_id']:8s} ({row['ticker']:5s}) "
                  f"| {sc_label:9s} | {n_items} items")
        print(f"    Final questions: 3 items")
        return {"form_id": "[DRY-RUN]", "edit_url": "[DRY-RUN]", "responder_url": "[DRY-RUN]"}

    # Create the form shell (title only)
    print(f"    Creating form... ", end="", flush=True)
    form_id = create_form_shell(forms_service, block_id, version)
    print(f"done ({form_id})")
    time.sleep(API_SLEEP)

    # Demographics section (also sets form description via updateFormInfo)
    print(f"    Demographics... ", end="", flush=True)
    demo_reqs, next_idx = build_demographics_requests(start_idx=0)
    ok = batch_update(forms_service, form_id, demo_reqs, "demographics")
    print("ok" if ok else "FAILED")
    time.sleep(API_SLEEP)

    # Scenario pages – one batchUpdate call per scenario
    for pos, row in guide.iterrows():
        scenario_num = int(row["presentation_order"])
        sid = row["scenario_id"]
        show_sc = int(row["show_sc"])

        print(f"    Scenario {pos+1:2d}/{total_scenarios}  {sid} "
              f"({'SC' if show_sc else 'ctrl'})... ", end="", flush=True)
        try:
            sc_reqs, next_idx = build_scenario_requests(
                scenario_num=scenario_num,
                total_scenarios=total_scenarios,
                scenario_id=sid,
                show_sc=show_sc,
                meta_idx=meta_idx,
                news_idx=news_idx,
                reaction_idx=reaction_idx,
                image_urls=image_urls,
                start_idx=next_idx,
            )
        except KeyError as exc:
            print(f"SKIPPED (missing data key: {exc})")
            continue

        ok = batch_update(forms_service, form_id, sc_reqs, f"scenario {sid}")
        print("ok" if ok else "FAILED")
        time.sleep(API_SLEEP)

    # Final questions
    print(f"    Final questions... ", end="", flush=True)
    final_reqs, _ = build_final_questions_requests(start_idx=next_idx)
    ok = batch_update(forms_service, form_id, final_reqs, "final questions")
    print("ok" if ok else "FAILED")
    time.sleep(API_SLEEP)

    # Publishing note
    try_publish_form(forms_service, form_id)

    edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    responder_url = f"https://docs.google.com/forms/d/e/{form_id}/viewform"
    return {"form_id": form_id, "edit_url": edit_url, "responder_url": responder_url}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Deploy Shock Score thesis survey to Google Forms.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python 4_deploy_google_forms.py                 # 3 forms (V1 per block)\n"
            "  python 4_deploy_google_forms.py --sub-blocks 2  # 6 forms (V1+V2 per block)\n"
            "  python 4_deploy_google_forms.py --dry-run       # validate without API calls"
        ),
    )
    parser.add_argument(
        "--sub-blocks",
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        dest="sub_blocks",
        help="Number of form versions per block (default: 1). 4 versions exist per block.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Print the form structure without making any API calls.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    dry_run = args.dry_run
    sub_blocks = args.sub_blocks
    total_forms = 3 * sub_blocks

    print("=" * 70)
    print("Shock Score Survey Deployment")
    print(f"  Mode          : {'DRY-RUN (no API calls)' if dry_run else 'LIVE'}")
    print(f"  Versions/block: {sub_blocks}  (V1{''.join(f'+V{v}' for v in range(2, sub_blocks+1))})")
    print(f"  Total forms   : {total_forms}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Load survey data
    # ------------------------------------------------------------------
    print("\n[1] Loading survey data...")
    meta_idx, news_idx, reaction_idx, shock_idx, assembly_guide = load_survey_data()
    n_scenarios = len(meta_idx)
    n_versions = assembly_guide["respondent_block"].nunique()
    print(f"  Scenarios: {n_scenarios}  |  Assembly guide versions: {n_versions}")

    # Validate that requested versions exist
    for block_id in [1, 2, 3]:
        for v in range(1, sub_blocks + 1):
            label = f"Block{block_id}_V{v}"
            if label not in assembly_guide["respondent_block"].values:
                print(f"  [WARN] {label} not found in form_assembly_guide.csv – will be skipped.")

    # ------------------------------------------------------------------
    # 2. Authenticate
    # ------------------------------------------------------------------
    if not dry_run:
        print("\n[2] Authenticating with Google APIs...")
        creds = get_credentials()
        drive_service = build("drive", "v3", credentials=creds)
        forms_service = build("forms", "v1", credentials=creds)
        print("  Authentication successful.")
    else:
        drive_service = None
        forms_service = None
        print("\n[2] Skipping authentication (dry-run).")

    # ------------------------------------------------------------------
    # 3. Upload images to Google Drive
    # ------------------------------------------------------------------
    print("\n[3] Uploading survey images to Google Drive...")

    if not dry_run:
        folder_id = create_drive_folder(drive_service, DRIVE_FOLDER_NAME)
    else:
        folder_id = "[DRY-RUN-FOLDER]"

    # Upload images once per block (shared across all versions of that block)
    block_image_urls = {}
    total_image_count = 0

    for block_id in [1, 2, 3]:
        scenario_ids = (
            assembly_guide[assembly_guide["block_id"] == block_id]["scenario_id"]
            .unique()
            .tolist()
        )
        n_imgs = len(scenario_ids) * 2
        print(f"  Block {block_id}: {len(scenario_ids)} scenarios ({n_imgs} images)")
        block_image_urls[block_id] = upload_block_images(
            drive_service=drive_service,
            block_id=block_id,
            folder_id=folder_id,
            scenario_ids=scenario_ids,
            dry_run=dry_run,
        )
        total_image_count += n_imgs

    if not dry_run:
        print(f"\n  Images uploaded/reused total: {total_image_count}")
        print(f"  Drive folder: https://drive.google.com/drive/folders/{folder_id}")

    # ------------------------------------------------------------------
    # 4. Create and populate forms
    # ------------------------------------------------------------------
    print("\n[4] Creating and populating Google Forms...")

    manifest = {
        "deployed_at": datetime.now(tz=timezone.utc).isoformat(),
        "sub_blocks": sub_blocks,
        "drive_folder_id": folder_id,
        "drive_folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "forms": {},
    }

    for block_id in [1, 2, 3]:
        manifest["forms"][f"block_{block_id}"] = {}
        for version in range(1, sub_blocks + 1):
            result = deploy_one_form(
                forms_service=forms_service,
                block_id=block_id,
                version=version,
                assembly_guide=assembly_guide,
                meta_idx=meta_idx,
                news_idx=news_idx,
                reaction_idx=reaction_idx,
                image_urls=block_image_urls[block_id],
                dry_run=dry_run,
            )
            manifest["forms"][f"block_{block_id}"][f"v{version}"] = result

    # ------------------------------------------------------------------
    # 5. Save deployment manifest
    # ------------------------------------------------------------------
    if not dry_run:
        DEPLOYMENT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DEPLOYMENT_MANIFEST_PATH, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)
        print(f"\n[5] Deployment manifest saved: {DEPLOYMENT_MANIFEST_PATH}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("DEPLOYMENT SUMMARY")
    print("=" * 70)

    for block_id in [1, 2, 3]:
        for version in range(1, sub_blocks + 1):
            info = manifest["forms"][f"block_{block_id}"].get(f"v{version}", {})
            if not info:
                continue
            label = f"Block {block_id}" + (f" V{version}" if sub_blocks > 1 else "")
            if dry_run:
                print(f"  {label}: [DRY-RUN -- no form created]")
            else:
                print(f"  {label}")
                print(f"    Edit URL     : {info.get('edit_url', 'N/A')}")
                print(f"    Responder URL: {info.get('responder_url', 'N/A')}")

    if not dry_run:
        print(f"\n  Images processed : {total_image_count}")
        print(f"  Drive folder     : https://drive.google.com/drive/folders/{folder_id}")
        print(f"  Manifest         : {DEPLOYMENT_MANIFEST_PATH}")
        print()
        print("  IMPORTANT: After 31 March 2026, open each form in Google Forms")
        print("  and click 'Publish' to enable response collection.")

    print("=" * 70)
    print("Done.")


if __name__ == "__main__":
    main()
