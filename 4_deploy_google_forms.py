"""4_deploy_google_forms.py

Updates 3 existing Google Forms (one per scenario block) with the latest
survey content. Form IDs are read from survey/deployment_manifest.json —
existing forms are never deleted or replaced, only their contents are cleared
and re-populated. This preserves all responder URLs.

Usage:
    python 4_deploy_google_forms.py           # update all 3 forms
    python 4_deploy_google_forms.py --dry-run # print structure without API calls

Prerequisites:
    credentials/client_secret.json          -- Google Cloud OAuth2 Desktop app credentials
    survey/deployment_manifest.json         -- form IDs for Block 1, 2, 3
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

# Portfolio context: equal-weight portfolio of PORTFOLIO_N stocks (per presentation protocol)
PORTFOLIO_N = 30

FORM_DESCRIPTION = (
    "This survey is part of an academic research study on how equity portfolio managers "
    "respond to financial information events.\n\n"
    "You will review a series of real market events for stocks held in your portfolio.\n\n"
    f"Assume you manage a diversified equity portfolio with equal weights across {PORTFOLIO_N} stocks.\n\n"
    "For each event, indicate your intended portfolio adjustment on the provided scale.\n\n"
    "The survey takes approximately 20\u201325 minutes. Your responses are anonymous and confidential."
)

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


def _image_req(title, source_uri, alt_text, idx, width=None, alignment=None):
    image = {"sourceUri": source_uri, "altText": alt_text}
    if width is not None or alignment is not None:
        props = {}
        if width is not None:
            props["width"] = width
        if alignment is not None:
            props["alignment"] = alignment
        image["properties"] = props
    return {"createItem": {
        "item": {
            "title": title,
            "imageItem": {"image": image},
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

# NOTE (#97 / SURVEY-01): _build_holdings_text() and the portfolio stock list page have been
# permanently removed. The page added no decision-relevant information and increased survey
# length. Do not re-introduce this page or function.


def build_demographics_requests(start_idx=0):
    """
    Build batchUpdate requests for the demographics section.
    Includes updateFormInfo for the form description, a portfolio holdings text item,
    then the demographics items.
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


def build_instructions_page_requests(start_idx):
    """
    Build batchUpdate requests for Page 3 — scenario format explanation and
    Shock Score dashboard signal descriptions. (#98 / SURVEY-02)

    Framing is descriptive and procedural only: it does not disclose that the
    study tests whether the dashboard changes behaviour.
    Returns (requests, next_available_index).
    """
    reqs = []
    idx = start_idx

    reqs.append(_page_break_req(
        title="How to complete this survey",
        description="",
        idx=idx,
    ))
    idx += 1

    reqs.append(_text_req(
        title="Each scenario contains the following elements:",
        description=(
            "1. Price chart \u2014 a two-day intraday chart showing 30-minute price bars for the stock. "
            "The chart ends shortly after the news event.\n\n"
            "2. News event \u2014 a headline and brief summary of the information shock affecting the holding.\n\n"
            "3. Decision question \u2014 you will be asked to select your intended portfolio adjustment on a "
            "7-point scale from Strongly reduce exposure (1) to Strongly increase exposure (7).\n\n"
            "Some scenarios include an additional decision-support panel called the Shock Score dashboard. "
            "This variation is intentional. The dashboard displays four signals:\n"
            "- Sentiment direction: whether the prevailing news tone is positive or negative\n"
            "- Shock severity: the magnitude of the price and news signal relative to historical norms\n"
            "- Persistence horizon: whether the shock is expected to resolve intraday, over days, or over weeks\n"
            "- Protocol recommendation: a rules-based suggested action (reduce / hold / increase) based on "
            "the combined signal\n\n"
            "Please base your response solely on the information provided in each scenario."
        ),
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

    # 1. Page break – all stock identity info on one line
    sign = "+" if reaction_pct >= 0 else ""
    reqs.append(_page_break_req(
        title=(
            f"{company_name} ({ticker})"
            f"  \u00b7  {sign}{reaction_pct:.2f}%"
            f"  \u00b7  {gics_sector}"
            f"  \u00b7  {row_meta['event_date']}"
        ),
        description="",
        idx=idx,
    ))
    idx += 1

    # 2. Chart image (all identifying info is burned into the image)
    if chart_url:
        reqs.append(_image_req(
            title="",
            source_uri=chart_url,
            alt_text=f"Intraday price chart for {company_name} ({ticker}) around the event",
            idx=idx,
        ))
        idx += 1

    # 3. News: headline as bold title; coverage note moved to end of body
    if num_articles >= 6:
        coverage_note = f"Covered by {num_articles} financial news sources."
    elif num_articles >= 3:
        coverage_note = "Reported by multiple sources."
    else:
        coverage_note = ""

    news_body_parts = []
    if summary_para:
        news_body_parts.append(summary_para)
    if coverage_note:
        news_body_parts.append(coverage_note)

    news_body = "\n\n".join(news_body_parts)

    # Headline in the title renders prominently (bold) in Google Forms
    reqs.append(_text_req(title=headline, description=news_body, idx=idx))
    idx += 1

    # 4. Shock Score dashboard (treatment only: show_sc == 1)
    if show_sc == 1 and dashboard_url:
        reqs.append(_image_req(
            title="",
            source_uri=dashboard_url,
            alt_text=(
                "Shock Score dashboard displaying sentiment direction, shock severity level, "
                "persistence horizon bucket, and pre-commitment protocol recommendation"
            ),
            idx=idx,
            width=630,
            alignment="CENTER",
        ))
        idx += 1

    # 5. NRS response scale (1 = strongly reduce, 7 = strongly increase)
    reqs.append(_scale_req(
        title="What would be your intended portfolio adjustment for this holding?",
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
# Forms API – population (update only; forms are never created by this script)
# ---------------------------------------------------------------------------

def clear_form_items(forms_service, form_id):
    """Delete all existing items from a form, preserving the form ID and URL."""
    form = forms_service.forms().get(formId=form_id).execute()
    items = form.get("items", [])
    if not items:
        print("  (no existing items to clear)")
        return
    # Delete in reverse index order so indices don't shift mid-operation
    delete_reqs = [
        {"deleteItem": {"location": {"index": i}}}
        for i in range(len(items) - 1, -1, -1)
    ]
    forms_service.forms().batchUpdate(
        formId=form_id, body={"requests": delete_reqs}
    ).execute()
    print(f"  Cleared {len(items)} existing items.")


def _migrate_manifest_schema(manifest):
    """
    Migrate old nested schema { "forms": { "block_1": { "v1": {...} } } }
    to flat schema { "forms": { "block_1_v1": { "form_id": "...", ... } } }.
    Returns the (possibly updated) manifest and a bool indicating whether
    a migration occurred.
    """
    forms = manifest.get("forms", {})
    migrated = False
    for block_id in [1, 2, 3]:
        old_key = f"block_{block_id}"
        if old_key in forms and isinstance(forms[old_key], dict):
            block_data = forms.pop(old_key)
            # Old format stored sub-dicts keyed by "v1", "v2", …
            if "v1" in block_data or "v2" in block_data:
                for v_key, v_data in block_data.items():
                    new_key = f"block_{block_id}_{v_key}"
                    forms[new_key] = v_data
            else:
                # Even older format: block_data IS the form record directly
                forms[f"block_{block_id}_v1"] = block_data
            migrated = True
    manifest["forms"] = forms
    return manifest, migrated


def load_manifest():
    """Load deployment_manifest.json, migrating the schema if necessary."""
    if not DEPLOYMENT_MANIFEST_PATH.exists():
        return None
    try:
        with open(DEPLOYMENT_MANIFEST_PATH, encoding="utf-8") as fh:
            manifest = json.load(fh)
    except json.JSONDecodeError:
        return None
    manifest, migrated = _migrate_manifest_schema(manifest)
    if migrated:
        with open(DEPLOYMENT_MANIFEST_PATH, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)
        print("  [INFO] Manifest schema migrated to flat block_N_vM keys.")
    return manifest


def get_existing_form_id(block_id, version):
    """
    Return the form ID stored in the deployment manifest for the given block/version,
    or None if the manifest does not exist or the entry is missing.
    Looks up the flat key f"block_{block_id}_v{version}".
    """
    manifest = load_manifest()
    if manifest is None:
        return None
    return (
        manifest.get("forms", {})
        .get(f"block_{block_id}_v{version}", {})
        .get("form_id")
    )


def get_or_create_form_id(forms_service, block_id, version, dry_run):
    """
    Return the form ID for the given block/version.
    - If the manifest already has a non-empty form_id for that slot, return it (update path).
    - If absent or empty, create a new Google Form, persist its ID and responder URL to
      the manifest, and return the new ID (create path).
    - In dry-run mode, returns "[DRY-RUN]" without touching the manifest.
    """
    if dry_run:
        existing = get_existing_form_id(block_id, version)
        return existing or "[DRY-RUN]"

    manifest = load_manifest()
    if manifest is None:
        raise FileNotFoundError(
            f"Deployment manifest not found at '{DEPLOYMENT_MANIFEST_PATH}'."
        )

    form_key = f"block_{block_id}_v{version}"
    existing_id = manifest.get("forms", {}).get(form_key, {}).get("form_id")
    if existing_id:
        return existing_id

    # Create a new form (V2 first run)
    title = f"Equity Portfolio Decision Survey \u2014 Block {block_id}"
    print(f"    Creating new form (Block {block_id} V{version})... ", end="", flush=True)
    form = forms_service.forms().create(body={"info": {"title": title}}).execute()
    new_id = form["formId"]
    responder_url = f"https://docs.google.com/forms/d/{new_id}/viewform"
    print(f"done ({new_id})")

    manifest.setdefault("forms", {})[form_key] = {
        "form_id": new_id,
        "responder_url": responder_url,
    }
    with open(DEPLOYMENT_MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    return new_id


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
    Update (or create on first run for V2) one Google Form for the given block/version.
    V1 forms are always updated. V2 forms are created on first run then updated thereafter.
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
    print(f"\n  > Block {block_id} V{version}  ({total_scenarios} scenarios)")

    if dry_run:
        form_id = get_or_create_form_id(forms_service, block_id, version, dry_run=True)
        print(f"    Form ID: {form_id}")
        print(f"    Demographics: 8 items (section header + 7 questions)")
        print(f"    Instructions: 2 items (page break + format explanation)")
        for pos, row in guide.iterrows():
            sc_label = "SC shown" if int(row["show_sc"]) == 1 else "control"
            n_items = 5 if int(row["show_sc"]) == 1 else 4
            print(f"    [{pos+1:2d}] {row['scenario_id']:8s} ({row['ticker']:5s}) "
                  f"| {sc_label:9s} | {n_items} items")
        print(f"    Final questions: 3 items")
        return {"form_id": form_id, "edit_url": "[DRY-RUN]", "responder_url": "[DRY-RUN]"}

    form_id = get_or_create_form_id(forms_service, block_id, version, dry_run=False)
    print(f"    Updating existing form {form_id}...")
    clear_form_items(forms_service, form_id)
    time.sleep(API_SLEEP)

    # Demographics section (also sets form description via updateFormInfo)
    print(f"    Demographics... ", end="", flush=True)
    demo_reqs, next_idx = build_demographics_requests(start_idx=0)
    ok = batch_update(forms_service, form_id, demo_reqs, "demographics")
    print("ok" if ok else "FAILED")
    time.sleep(API_SLEEP)

    # Instructions page (Page 3 – scenario format and Shock Score dashboard explanation)
    print(f"    Instructions page... ", end="", flush=True)
    instr_reqs, next_idx = build_instructions_page_requests(start_idx=next_idx)
    ok = batch_update(forms_service, form_id, instr_reqs, "instructions page")
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
    responder_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
    return {"form_id": form_id, "edit_url": edit_url, "responder_url": responder_url}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Update existing Shock Score thesis survey forms (never creates new ones).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python 4_deploy_google_forms.py           # update all 3 forms\n"
            "  python 4_deploy_google_forms.py --dry-run # validate without API calls"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Print the form structure without making any API calls.",
    )
    args, _ = parser.parse_known_args()
    return args


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    dry_run = args.dry_run

    print("=" * 70)
    print("Shock Score Survey – Form Update")
    print(f"  Mode   : {'DRY-RUN (no API calls)' if dry_run else 'LIVE – UPDATE (existing forms)'}")
    print(f"  Forms  : Block 1, Block 2, Block 3  (V1 and V2 each — update or create)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Load survey data
    # ------------------------------------------------------------------
    print("\n[1] Loading survey data...")
    meta_idx, news_idx, reaction_idx, shock_idx, assembly_guide = load_survey_data()
    n_scenarios = len(meta_idx)
    print(f"  Scenarios: {n_scenarios}")

    # Validate that V1 and V2 versions exist for all 3 blocks
    for block_id in [1, 2, 3]:
        for version in [1, 2]:
            label = f"Block{block_id}_V{version}"
            if label not in assembly_guide["respondent_block"].values:
                print(f"  [WARN] {label} not found in form_assembly_guide.csv – will be skipped.")

    # Validate manifest exists
    if not dry_run and not DEPLOYMENT_MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Deployment manifest not found at '{DEPLOYMENT_MANIFEST_PATH}'.\n"
            "Create it manually with the form IDs before running."
        )

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
        # Reuse the existing Drive folder recorded in the manifest
        with open(DEPLOYMENT_MANIFEST_PATH, encoding="utf-8") as fh:
            _manifest_data = json.load(fh)
        folder_id = _manifest_data.get("drive_folder_id") or create_drive_folder(drive_service, DRIVE_FOLDER_NAME)
        print(f"  Drive folder: https://drive.google.com/drive/folders/{folder_id}")
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
    # 4. Update forms
    # ------------------------------------------------------------------
    print("\n[4] Updating Google Forms...")

    results = {}
    for block_id in [1, 2, 3]:
        for version in [1, 2]:
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
            results[(block_id, version)] = result

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("UPDATE SUMMARY")
    print("=" * 70)

    for block_id in [1, 2, 3]:
        for version in [1, 2]:
            info = results.get((block_id, version), {})
            if not info:
                continue
            label = f"Block {block_id} V{version}"
            if dry_run:
                print(f"  {label}: [DRY-RUN]  Form ID: {info.get('form_id', 'N/A')}")
            else:
                print(f"  {label}")
                print(f"    Edit URL     : {info.get('edit_url', 'N/A')}")
                print(f"    Responder URL: {info.get('responder_url', 'N/A')}")

    if not dry_run:
        print(f"\n  Images processed : {total_image_count}")
        print(f"  Drive folder     : https://drive.google.com/drive/folders/{folder_id}")

    print("=" * 70)
    print("Done.")


if __name__ == "__main__":
    main()
