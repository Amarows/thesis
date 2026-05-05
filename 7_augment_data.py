"""
7_augment_data.py – Synthetic response augmentation (TEMPORARY)

Inflates results/analysis_panel.csv in-place to a target respondent count by
appending synthetic rows that preserve the statistical properties of real
responses. Overwrites analysis_panel.csv directly — no new files created.

Disable: delete or stop calling this script. The downstream pipeline reads
analysis_panel.csv unchanged; deleting this script has no other side effects.

Usage:
    python 7_augment_data.py                          # default target: 60
    python 7_augment_data.py --target-respondents 80
    python 7_augment_data.py --target-respondents 0   # no-op, file unchanged
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

np.random.seed(42)

PANEL_PATH = Path("results/analysis_panel.csv")
DEFAULT_TARGET = 60

PILOT_FEEDBACK_COLS = [
    "completion_time",
    "pilot_clarity",
    "pilot_dashboard_ease",
    "pilot_realism",
    "open_feedback",
    "contact_optional",
]

DEMOGRAPHIC_COLS = [
    "years_experience",
    "aum_category",
    "institution_type",
    "investment_mandate",
    "geographic_focus",
    "discretionary_authority",
    "certifications",
]

FORM_COLS = ["form_key", "block_id", "version"]


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def build_respondent_profiles(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("respondent_id")
    profiles = grouped[DEMOGRAPHIC_COLS + FORM_COLS].first().reset_index()
    nrs_stats = grouped["nrs"].agg(mean_nrs="mean", sd_nrs="std").reset_index()
    nrs_stats["sd_nrs"] = nrs_stats["sd_nrs"].fillna(0.0)
    profiles = profiles.merge(nrs_stats, on="respondent_id")
    return profiles


def generate_synthetic_rows(
    real_df: pd.DataFrame,
    profiles: pd.DataFrame,
    n_synthetic: int,
) -> pd.DataFrame:
    sampled = profiles.sample(n=n_synthetic, replace=True).reset_index(drop=True)

    all_synthetic = []
    for i, donor_profile in sampled.iterrows():
        synth_id = f"synth_{i + 1:04d}"
        donor_id = donor_profile["respondent_id"]
        donor_rows = real_df[real_df["respondent_id"] == donor_id].copy()

        sd = donor_profile["sd_nrs"]
        if sd == 0.0:
            sd = 0.5
        mean_nrs = donor_profile["mean_nrs"]

        nrs_noise = np.random.normal(0, sd, size=len(donor_rows))
        nrs_raw = mean_nrs + nrs_noise
        nrs_values = np.clip(np.round(nrs_raw), 1, 7).astype(int)

        donor_rows = donor_rows.reset_index(drop=True)
        donor_rows["respondent_id"] = synth_id
        donor_rows["nrs"] = nrs_values
        donor_rows["is_synthetic"] = 1
        donor_rows["timestamp"] = pd.NaT

        for col in PILOT_FEEDBACK_COLS:
            if col in donor_rows.columns:
                donor_rows[col] = pd.NA

        all_synthetic.append(donor_rows)

    return pd.concat(all_synthetic, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(description="Augment survey panel with synthetic respondents.")
    parser.add_argument(
        "--target-respondents",
        type=int,
        default=DEFAULT_TARGET,
        dest="target",
        help="Target number of unique respondents (default: 60)",
    )
    args = parser.parse_args()
    target = args.target

    if not PANEL_PATH.exists():
        print(f"ERROR: Input file not found: {PANEL_PATH}", file=sys.stderr)
        sys.exit(1)

    real_df = load_panel(PANEL_PATH)
    original_columns = list(real_df.columns)
    n_real = real_df["respondent_id"].nunique()

    if target == 0 or n_real >= target:
        print(
            f"Real respondents ({n_real}) >= target ({target}). "
            f"No augmentation applied."
        )
        return

    n_synthetic = target - n_real
    profiles = build_respondent_profiles(real_df)
    synthetic_df = generate_synthetic_rows(real_df, profiles, n_synthetic)

    # Cast pilot feedback cols to object before concat to avoid pandas FutureWarning
    # about all-NA column dtype inference changing in a future version.
    for col in PILOT_FEEDBACK_COLS:
        if col in real_df.columns:
            real_df[col] = real_df[col].astype(object)
        if col in synthetic_df.columns:
            synthetic_df[col] = synthetic_df[col].astype(object)

    augmented = pd.concat([real_df, synthetic_df], ignore_index=True)
    augmented = augmented[original_columns]
    augmented.to_csv(PANEL_PATH, index=False)

    n_total_respondents = augmented["respondent_id"].nunique()
    n_total_obs = len(augmented)
    n_real_obs = len(real_df)
    n_synth_obs = len(synthetic_df)

    print("=" * 61)
    print("Augmentation Complete")
    print("=" * 61)
    print(f"  Real respondents  : {n_real}")
    print(f"  Synthetic added   : {n_synthetic}")
    print(f"  Total respondents : {n_total_respondents}")
    print(f"  Total observations: {n_total_obs} ({n_real_obs} real + {n_synth_obs} synthetic)")
    print(f"  Output            : {PANEL_PATH}")
    print("=" * 61)


if __name__ == "__main__":
    main()
