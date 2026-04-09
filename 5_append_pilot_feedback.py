"""5_append_pilot_feedback.py

Temporary pilot instrument: appends a 'Pilot Feedback' section (page break +
5 questions) to the END of Block 1 – V1 and Block 1 – V2 forms only, after
the existing Final Questions items.  Does NOT modify or delete any existing
items.

Intended for the first ~30 pilot respondents.  Once the pilot is complete,
delete the appended questions manually in Google Forms and retire this script.

Usage:
    python 5_append_pilot_feedback.py           # live update Block 1 V1 & V2
    python 5_append_pilot_feedback.py --dry-run # print plan without API calls

Prerequisites:
    credentials/client_secret.json  -- same OAuth2 Desktop app credentials as
                                       used by 4_deploy_google_forms.py
    Enabled APIs: Google Forms API
"""

import argparse
import os
import pickle
import time

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/forms.body"]

TOKEN_PATH = "credentials/token.json"
SECRET_PATH = "credentials/client_secret.json"

FORM_IDS = {
    "Block 1 – V1": "14NTeClu7EADGDIl5gehfQLP20ApDi4KbQmfYVEiqooQ",
    "Block 1 – V2": "1e_2mnrr-MwQmghwyX_HHxUsBqNt13bwPxWQAwAzHCfE",
}

API_SLEEP = 1.0  # seconds between API calls

PILOT_SECTION_TITLE = "Pilot Feedback"


# ---------------------------------------------------------------------------
# Authentication (same pattern as 4_deploy_google_forms.py)
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
# Request builders (mirrors helpers in 4_deploy_google_forms.py)
# ---------------------------------------------------------------------------

def _page_break_req(title, description, idx):
    return {"createItem": {
        "item": {"title": title, "description": description, "pageBreakItem": {}},
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


def _scale_req(title, low, high, low_label, high_label, required, idx, description=None):
    item = {
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
    }
    if description:
        item["description"] = description
    return {"createItem": {"item": item, "location": {"index": idx}}}


def _paragraph_req(title, required, idx):
    return {"createItem": {
        "item": {
            "title": title,
            "questionItem": {"question": {
                "required": required,
                "textQuestion": {"paragraph": True},
            }},
        },
        "location": {"index": idx},
    }}


# ---------------------------------------------------------------------------
# Build pilot feedback section (6 items: 1 page break + 5 questions)
# ---------------------------------------------------------------------------

def build_pilot_feedback_requests(start_idx):
    """
    Return a list of 6 batchUpdate createItem requests for the Pilot Feedback
    section, beginning at start_idx.
    """
    reqs = []
    idx = start_idx

    # Section header / page break
    reqs.append(_page_break_req(
        title=PILOT_SECTION_TITLE,
        description=(
            "These five questions take under two minutes and will help improve the survey "
            "before full deployment. Your responses are greatly appreciated."
        ),
        idx=idx,
    ))
    idx += 1

    # Q1 – Completion time [RADIO, Required]
    reqs.append(_radio_req(
        title="How long did it take you to complete the survey?",
        options=[
            "Less than 15 minutes",
            "15\u201320 minutes",
            "20\u201325 minutes",
            "More than 25 minutes",
        ],
        required=True,
        idx=idx,
    ))
    idx += 1

    # Q2 – Scenario clarity [LINEAR_SCALE 1–5, Required]
    reqs.append(_scale_req(
        title=(
            "How clear and understandable were the scenario descriptions, "
            "including the news events and portfolio context?"
        ),
        low=1,
        high=5,
        low_label="Very unclear",
        high_label="Very clear",
        required=True,
        idx=idx,
    ))
    idx += 1

    # Q3 – Dashboard interpretability [LINEAR_SCALE 1–5, Not required]
    reqs.append(_scale_req(
        title=(
            "For scenarios that included the decision-support dashboard, how easy was it "
            "to interpret the information presented?"
        ),
        description=(
            "If no dashboard was displayed in your scenarios, please skip this question."
        ),
        low=1,
        high=5,
        low_label="Very difficult",
        high_label="Very easy",
        required=False,
        idx=idx,
    ))
    idx += 1

    # Q4 – Scenario realism [LINEAR_SCALE 1–5, Required]
    reqs.append(_scale_req(
        title=(
            "How realistic did the investment scenarios feel relative to your "
            "professional experience?"
        ),
        low=1,
        high=5,
        low_label="Not realistic",
        high_label="Very realistic",
        required=True,
        idx=idx,
    ))
    idx += 1

    # Q5 – Open-ended observations [PARAGRAPH, Not required]
    reqs.append(_paragraph_req(
        title=(
            "Please share any observations about aspects of the survey that were confusing, "
            "unrealistic, or could be improved. Any technical issues encountered may also be "
            "noted here."
        ),
        required=False,
        idx=idx,
    ))

    return reqs  # length == 6


# ---------------------------------------------------------------------------
# Verify: fetch form and confirm the section was appended correctly
# ---------------------------------------------------------------------------

def verify_form(forms_service, form_id, expected_item_count):
    """
    Fetch the form and check:
      1. Total item count matches expected_item_count.
      2. A page-break item titled 'Pilot Feedback' exists at the expected position.
    Returns True if both checks pass.
    """
    try:
        form = forms_service.forms().get(formId=form_id).execute()
    except HttpError as exc:
        print(f"  [ERROR] Verify fetch failed: {exc}")
        return False

    items = form.get("items", [])
    actual_count = len(items)
    count_ok = actual_count == expected_item_count

    # The page break should be at index expected_item_count - 6
    pilot_idx = expected_item_count - 6
    pilot_item = items[pilot_idx] if pilot_idx < len(items) else None
    section_ok = (
        pilot_item is not None
        and pilot_item.get("title") == PILOT_SECTION_TITLE
        and "pageBreakItem" in pilot_item
    )

    status = "OK" if (count_ok and section_ok) else "MISMATCH"
    print(
        f"  Verify [{status}]: "
        f"{actual_count} items (expected {expected_item_count}), "
        f"'{PILOT_SECTION_TITLE}' page break at index {pilot_idx}: "
        f"{'found' if section_ok else 'NOT FOUND'}"
    )
    return count_ok and section_ok


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Append Pilot Feedback section to Block 1 – V1 and V2 forms.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python 5_append_pilot_feedback.py           # live update\n"
            "  python 5_append_pilot_feedback.py --dry-run # validate without API calls"
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Print the append plan without making any API calls.",
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
    print("Shock Score Survey – Append Pilot Feedback (Block 1 only)")
    print(f"  Mode  : {'DRY-RUN (no API calls)' if dry_run else 'LIVE'}")
    print(f"  Forms : Block 1 – V1, Block 1 – V2")
    print(f"  Items : 6 (page break + 5 questions) appended per form")
    print("=" * 70)

    if not dry_run:
        print("\nAuthenticating with Google APIs...")
        creds = get_credentials()
        forms_service = build("forms", "v1", credentials=creds)
        print("  Authentication successful.")
    else:
        forms_service = None

    all_ok = True

    for block_id, form_id in FORM_IDS.items():
        print(f"\n--- {block_id}  (form_id: {form_id}) ---")

        if dry_run:
            print(f"  [DRY-RUN] Would append 6 items after the last existing item:")
            print(f"    i+0  Page break  : '{PILOT_SECTION_TITLE}'")
            print(f"    i+1  Radio       : Q1 – completion time (required)")
            print(f"    i+2  Scale 1-5   : Q2 – scenario clarity (required)")
            print(f"    i+3  Scale 1-5   : Q3 – dashboard interpretability (not required)")
            print(f"    i+4  Scale 1-5   : Q4 – scenario realism (required)")
            print(f"    i+5  Paragraph   : Q5 – open feedback (not required)")
            continue

        # Fetch current form to determine append position
        try:
            form = forms_service.forms().get(formId=form_id).execute()
        except HttpError as exc:
            print(f"  [ERROR] Could not fetch form: {exc}")
            all_ok = False
            continue

        current_items = form.get("items", [])
        current_count = len(current_items)
        print(f"  Current item count: {current_count}")

        # Idempotency guard: skip if section already present
        already_present = any(
            it.get("title") == PILOT_SECTION_TITLE for it in current_items
        )
        if already_present:
            print(f"  [SKIP] '{PILOT_SECTION_TITLE}' section already exists – no changes made.")
            continue

        # Build append requests
        reqs = build_pilot_feedback_requests(start_idx=current_count)
        expected_total = current_count + len(reqs)

        # Execute batchUpdate
        print(
            f"  Appending {len(reqs)} items "
            f"(indices {current_count}\u2013{expected_total - 1})...",
            end="", flush=True,
        )
        try:
            forms_service.forms().batchUpdate(
                formId=form_id, body={"requests": reqs}
            ).execute()
            print("  ok")
        except HttpError as exc:
            print(f"\n  [ERROR] batchUpdate failed: {exc}")
            all_ok = False
            continue

        time.sleep(API_SLEEP)

        # Verify
        verify_ok = verify_form(forms_service, form_id, expected_total)
        if not verify_ok:
            all_ok = False

    print("\n" + "=" * 70)
    if dry_run:
        print("DRY-RUN complete. No changes made.")
    elif all_ok:
        print("Both Block 1 forms updated and verified successfully.")
    else:
        print("WARNING: One or more forms may have issues – review output above.")
    print("=" * 70)


if __name__ == "__main__":
    main()
