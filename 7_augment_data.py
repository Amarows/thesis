"""
7_augment_data_v2.py – Synthetic response augmentation from Persona file

Loads persona responses from survey/persona/persona_responses.csv and appends
them to results/analysis_panel.csv in the correct long-form format.
Overwrites analysis_panel.csv directly.
"""

import argparse
import sys
from pathlib import Path
import random

import numpy as np
import pandas as pd

from config import (
    PANEL_PATH,
    SEED, append_run_log, _sha256_file,
)

np.random.seed(SEED)
random.seed(SEED)

PERSONA_RESPONSES_PATH = Path("survey/persona/persona_responses.csv")

PILOT_FEEDBACK_COLS = [
    "completion_time",
    "pilot_clarity",
    "pilot_dashboard_ease",
    "pilot_realism",
    "open_feedback",
    "contact_optional",
]

CONTROL_COLS = [
    "manipulation_check",
    "usefulness_rating",
    "is_pilot_block",
    "completion_time",
    "pilot_clarity",
    "pilot_dashboard_ease",
    "pilot_realism",
    "open_feedback",
    "contact_optional",
]


def _exp_label(years: float) -> str:
    """Map years of experience to the label used in the real panel."""
    if years < 2: return "Less than 2"
    if years <= 5: return "2-5"
    if years <= 10: return "6-10"
    if years <= 15: return "11-15"
    if years <= 20: return "16-20"
    return "20+"


def load_panel(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def generate_persona_rows(
        real_df: pd.DataFrame,
        persona_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform persona_df (wide) to long-form rows matching real_df.
    Processes each persona for each form key exactly once.
    Resamples control answers from real_df for missing fields.
    """
    all_form_keys = sorted(real_df["form_key"].dropna().unique().tolist())

    # Pre-calculate distributions for resampling control columns from real respondents
    real_resp_level = real_df.drop_duplicates("respondent_id").copy()

    all_synthetic = []

    # Iterate through each persona
    for _, persona in persona_df.iterrows():
        persona_id = str(persona["persona_id"])

        # Each persona fills each form version once
        for form_key in all_form_keys:
            synth_id = f"persona_{persona_id}_{form_key}"

            # Get template rows for this form_key
            template_rows = real_df[real_df["form_key"] == form_key].copy()
            if template_rows.empty:
                continue

            # Take one representative real respondent's scenario rows as the template
            first_resp = template_rows["respondent_id"].iloc[0]
            template_rows = template_rows[template_rows["respondent_id"] == first_resp].copy()
            template_rows = template_rows.sort_values("scenario_position").reset_index(drop=True)

            # Build synthetic rows from template
            synth_rows = template_rows.copy()
            synth_rows["respondent_id"] = synth_id

            # Map demographics
            synth_rows["years_experience"] = float(persona["years_experience"])
            synth_rows["years_experience_label"] = _exp_label(persona["years_experience"])
            synth_rows["aum_category"] = str(persona["aum_usd_bn"]) + "B"
            synth_rows["institution_type"] = str(persona["institution_type"])
            synth_rows["investment_mandate"] = str(persona["investment_mandate"])
            synth_rows["geographic_focus"] = str(persona["geographic_focus"])
            synth_rows["discretionary_authority"] = str(persona["discretionary_authority"])
            synth_rows["certifications"] = str(persona["primary_certifications"])

            # Resample control items from a random real respondent
            donor = real_resp_level.sample(1).iloc[0]
            for col in CONTROL_COLS:
                if col in synth_rows.columns:
                    val = donor[col]
                    if pd.isna(val):
                        non_null_vals = real_resp_level[col].dropna()
                        if not non_null_vals.empty:
                            val = np.random.choice(non_null_vals)
                    synth_rows[col] = val

            # Map NRS values
            nrs_values = []
            for _, row in synth_rows.iterrows():
                sc_id = row["scenario_id"].replace("_", "")
                show_sc = int(row["show_sc"])
                col_name = f"nrs{show_sc}_{sc_id}"
                nrs_val = persona[col_name]
                nrs_values.append(nrs_val)

            synth_rows["nrs"] = nrs_values
            synth_rows["nrs_invalid"] = False
            synth_rows["is_synthetic"] = 1
            synth_rows["timestamp"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            all_synthetic.append(synth_rows)

    if not all_synthetic:
        return pd.DataFrame()
    return pd.concat(all_synthetic, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(
        description="Augment survey panel with persona-based synthetic respondents."
    )
    # Target parameter removed as per instructions
    args = parser.parse_args()

    if not PANEL_PATH.exists():
        print(f"ERROR: Input file not found: {PANEL_PATH}", file=sys.stderr)
        sys.exit(1)

    if not PERSONA_RESPONSES_PATH.exists():
        print(f"ERROR: Persona file not found: {PERSONA_RESPONSES_PATH}", file=sys.stderr)
        sys.exit(1)

    real_df = load_panel(PANEL_PATH)
    persona_df = pd.read_csv(PERSONA_RESPONSES_PATH)

    original_columns = list(real_df.columns)
    n_real = real_df["respondent_id"].nunique()

    # Priority: persona-based augmentation.
    # We generate ALL persona rows (one per persona per form block).

    synthetic_df = generate_persona_rows(real_df, persona_df)
    n_synthetic_added = synthetic_df["respondent_id"].nunique()

    if not synthetic_df.empty:
        # Cast pilot feedback cols to object before concat to avoid pandas dtype warnings
        for col in PILOT_FEEDBACK_COLS:
            if col in real_df.columns:
                real_df[col] = real_df[col].astype(object)
            if col in synthetic_df.columns:
                synthetic_df[col] = synthetic_df[col].astype(object)

        augmented = pd.concat([real_df, synthetic_df], ignore_index=True)
        augmented = augmented[original_columns]
        augmented.to_csv(PANEL_PATH, index=False)

        n_total_respondents = augmented["respondent_id"].nunique()
        print(
            f"Augmentation Complete: {n_real} real + {n_synthetic_added} persona-based = {n_total_respondents} total.")
    else:
        augmented = real_df

    append_run_log(
        script="7_augment_data_v2.py",
        parameters={
            "seed": SEED,
            "source": str(PERSONA_RESPONSES_PATH)
        },
        inputs=[
            {"file": str(PANEL_PATH), "sha256": _sha256_file(PANEL_PATH)},
            {"file": str(PERSONA_RESPONSES_PATH), "sha256": _sha256_file(PERSONA_RESPONSES_PATH)},
        ],
        outputs=[
            {"file": str(PANEL_PATH), "rows": len(augmented),
             "sha256": _sha256_file(PANEL_PATH)},
        ],
        notes=f"Augmented with persona-based responses from {PERSONA_RESPONSES_PATH.name}."
    )


if __name__ == "__main__":
    main()
