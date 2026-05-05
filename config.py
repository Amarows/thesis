# config.py – Single source of truth for all pipeline parameters.
# All scripts import from here. Do not define analytical constants locally.

from pathlib import Path
import subprocess
import hashlib
import json
from datetime import datetime, timezone

# ── Respondent eligibility ────────────────────────────────────────────────────
MIN_YEARS_EXPERIENCE = 2          # Minimum years of experience for inclusion

# ── Survey instrument ─────────────────────────────────────────────────────────
NRS_MIN          = 1
NRS_MAX          = 7
NRS_NEUTRAL      = 4              # Neutral point on 7-point scale
NRS_SCALE_POINTS = 7

# ── Portfolio simulation ──────────────────────────────────────────────────────
WEIGHT_STEP = 0.02                # Weight adjustment per NRS unit from neutral
RF_ANNUAL   = 0.05                # Risk-free rate annualised (3-month T-bill proxy)
AUM         = 100_000_000         # Dollar impact AUM assumption ($100M)

HORIZON_DAYS = {                  # Trading days per persistence bucket
    "Intraday":      1,
    "Several Days":  5,
    "Several Weeks": 20,
}

# ── Statistical analysis ──────────────────────────────────────────────────────
ALPHA = 0.05                      # Significance threshold (two-tailed)
SEED  = 42                        # Random seed for reproducibility

# ── Augmentation ─────────────────────────────────────────────────────────────
DEFAULT_TARGET_RESPONDENTS = 60
AUGMENT_NOISE_FLOOR_SD     = 0.8  # Minimum SD for NRS noise generation

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID   = "1ICjcSZdwuW-xKepA5VMDjO-gfBfAe544wuO-wsmG3fM"
CREDENTIALS_PATH = Path("credentials/client_secret.json")

# ── Paths (relative to repo root) ────────────────────────────────────────────
RESULTS_DIR           = Path("results")
SURVEY_DIR            = Path("survey")
DATA_DIR              = Path("data")
RAW_RESPONSES_DIR     = Path("survey/raw_responses")

PANEL_PATH            = RESULTS_DIR / "analysis_panel.csv"
COMMENTS_PATH         = RESULTS_DIR / "analysis_panel_comments.md"
EXCLUDED_PATH         = RESULTS_DIR / "excluded_respondents.csv"
THESIS_RESULTS_PATH   = RESULTS_DIR / "thesis_results.md"
FIGURES_DIR           = RESULTS_DIR / "figures"
TABLES_DIR            = RESULTS_DIR / "tables"
RUN_LOG_PATH          = RESULTS_DIR / "pipeline_run_log.jsonl"

SHOCK_SCORE_PATH      = SURVEY_DIR / "metadata" / "scenario_shock_score.csv"
METADATA_PATH         = SURVEY_DIR / "metadata" / "scenario_metadata.csv"
PRICE_REACTION_PATH   = SURVEY_DIR / "metadata" / "scenario_price_reaction.csv"
COUNTERBALANCING_PATH = SURVEY_DIR / "counterbalancing" / "counterbalancing_matrix.csv"

THESIS_PATH           = Path("thesis.md")
THESIS_FINAL_PATH     = Path("thesis_final.md")
REFERENCE_DOCX        = Path("documents/thesis.docx")
DOCX_OUTPUT           = Path("documents/thesis_final.docx")


# ── Pipeline run log ──────────────────────────────────────────────────────────

def _get_git_commit() -> str:
    """Return short git commit hash, or 'unknown' if git unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _sha256_file(path: Path) -> str:
    """Return SHA-256 hex digest of a file, or 'missing' if not found."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:16]   # first 16 chars sufficient for integrity check
    except FileNotFoundError:
        return "missing"


def append_run_log(
    script: str,
    parameters: dict,
    inputs: list[dict],
    outputs: list[dict],
    notes: str = "",
) -> None:
    """
    Append one JSON record to results/pipeline_run_log.jsonl.

    Parameters
    ----------
    script : str
        Name of the calling script, e.g. "6_process_survey_data.py".
    parameters : dict
        Key analytical parameters active during this run.
        Use config constants: {"min_years_experience": MIN_YEARS_EXPERIENCE, ...}
    inputs : list[dict]
        Each entry: {"file": str, "sha256": str}.
        Use _sha256_file(path) to populate sha256.
    outputs : list[dict]
        Each entry: {"file": str, "rows": int | None, "sha256": str}.
    notes : str
        Free-text run summary (e.g. respondent counts, H1/H2 verdicts).
    """
    RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "script":     script,
        "git_commit": _get_git_commit(),
        "parameters": parameters,
        "inputs":     inputs,
        "outputs":    outputs,
        "notes":      notes,
    }
    with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
