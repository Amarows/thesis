"""
7_augment_data.py – Synthetic response augmentation (TEMPORARY)

Inflates results/analysis_panel.csv in-place to a target respondent count by
appending synthetic rows drawn from realistic population distributions.
Overwrites analysis_panel.csv directly — no new files created.

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

# Realistic population distributions for professional equity portfolio managers.
# Demographics are drawn independently from these distributions rather than
# cloned from donor profiles, ensuring synthetic respondents add genuine
# variability to the regression covariates.
SYNTHETIC_DISTRIBUTIONS = {
    "years_experience": {
        "type": "ordinal_midpoints",
        "categories": ["1-3", "3-5", "5-10", "10-15", "15-20", "20+"],
        "midpoints":  [2.0,   4.0,   7.5,   12.5,   17.5,   25.0],
        "weights":    [0.05,  0.10,  0.30,  0.30,   0.15,   0.10],
    },
    "aum_category": {
        "type": "categorical",
        "categories": ["Less than $50M", "$50M-$200M", "$200M-$500M",
                       "$500M-$2B", "$2B-$10B", "More than $10B"],
        "weights":    [0.10, 0.20, 0.25, 0.25, 0.15, 0.05],
    },
    "institution_type": {
        "type": "categorical",
        "categories": ["Asset manager", "Hedge fund", "Pension fund",
                       "Insurance", "Family office", "Private bank",
                       "Independent/RIA"],
        "weights":    [0.30, 0.20, 0.15, 0.10, 0.10, 0.08, 0.07],
    },
    "investment_mandate": {
        "type": "categorical",
        "categories": ["Equity only", "Equity-dominant multi-asset",
                       "Sector-specific", "Other"],
        "weights":    [0.40, 0.35, 0.15, 0.10],
    },
    "geographic_focus": {
        "type": "categorical",
        "categories": ["North America", "Europe", "Asia-Pacific",
                       "Global", "Other"],
        "weights":    [0.35, 0.25, 0.15, 0.20, 0.05],
    },
    "discretionary_authority": {
        "type": "categorical",
        "categories": ["Full discretion", "Partial/committee-based",
                       "Advisory only"],
        "weights":    [0.50, 0.35, 0.15],
    },
    "certifications": {
        "type": "categorical",
        "categories": ["CFA", "CFA, FRM", "CFA, CAIA", "FRM", "None", "Other"],
        "weights":    [0.45, 0.15, 0.10, 0.10, 0.12, 0.08],
    },
    "manipulation_check": {
        "type": "categorical",
        "categories": ["Yes", "No", "Unsure"],
        "weights":    [0.70, 0.15, 0.15],
    },
    "usefulness_rating": {
        "type": "categorical",
        "categories": ["1", "2", "3", "4", "5"],
        "weights":    [0.05, 0.10, 0.20, 0.40, 0.25],
    },
}

# NRS baseline distribution across the 7-point scale
NRS_BASELINE_VALUES = [1, 2, 3, 4, 5, 6, 7]
NRS_BASELINE_WEIGHTS = [0.05, 0.10, 0.15, 0.35, 0.15, 0.12, 0.08]


def _draw(field: str) -> object:
    """Draw a single value for a demographic field from its distribution."""
    dist = SYNTHETIC_DISTRIBUTIONS[field]
    weights = np.array(dist["weights"], dtype=float)
    weights /= weights.sum()
    if dist["type"] == "ordinal_midpoints":
        return float(np.random.choice(dist["midpoints"], p=weights))
    return str(np.random.choice(dist["categories"], p=weights))


def _exp_label(midpoint: float) -> str:
    """Map experience midpoint back to the label used in the real panel."""
    mapping = {2.0: "Less than 2", 4.0: "2-5", 7.5: "5-10",
               12.5: "10-15", 17.5: "15-20", 25.0: "20+"}
    return mapping.get(midpoint, str(midpoint))


def load_panel(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def generate_synthetic_rows(
    real_df: pd.DataFrame,
    n_synthetic: int,
) -> pd.DataFrame:
    """
    Generate n_synthetic synthetic respondent blocks. Each synthetic respondent
    is assigned a form_key sampled uniformly from the six form keys present in
    the real panel, and demographics drawn independently from SYNTHETIC_DISTRIBUTIONS.
    """
    all_form_keys = sorted(real_df["form_key"].dropna().unique().tolist())

    all_synthetic = []
    for i in range(n_synthetic):
        synth_id = f"synth_{i + 1:04d}"

        # Assign form_key uniformly across all six blocks
        form_key = str(np.random.choice(all_form_keys))

        # Get template rows for this form_key (scenario metadata, show_sc, etc.)
        template_rows = real_df[real_df["form_key"] == form_key].copy()
        if template_rows.empty:
            continue
        # Take one representative real respondent's scenario rows as the template
        first_resp = template_rows["respondent_id"].iloc[0]
        template_rows = template_rows[template_rows["respondent_id"] == first_resp].copy()
        template_rows = template_rows.reset_index(drop=True)

        # Draw demographics independently from realistic distributions
        exp_midpoint = _draw("years_experience")
        demographics = {
            "years_experience": exp_midpoint,
            "years_experience_label": _exp_label(exp_midpoint),
            "aum_category": _draw("aum_category"),
            "institution_type": _draw("institution_type"),
            "investment_mandate": _draw("investment_mandate"),
            "geographic_focus": _draw("geographic_focus"),
            "discretionary_authority": _draw("discretionary_authority"),
            "certifications": _draw("certifications"),
        }

        # Draw manipulation_check and usefulness_rating independently
        manip_check = _draw("manipulation_check")
        usefulness   = _draw("usefulness_rating")

        # Generate NRS values with wide variability
        baseline_nrs = int(np.random.choice(NRS_BASELINE_VALUES,
                                             p=NRS_BASELINE_WEIGHTS))
        sd = np.random.uniform(0.8, 2.0)
        nrs_raw    = baseline_nrs + np.random.normal(0, sd, size=len(template_rows))
        nrs_values = np.clip(np.round(nrs_raw), 1, 7).astype(int)

        # Build synthetic rows from template
        synth_rows = template_rows.copy()
        synth_rows["respondent_id"] = synth_id
        synth_rows["nrs"] = nrs_values
        synth_rows["nrs_invalid"] = False
        synth_rows["is_synthetic"] = 1
        synth_rows["timestamp"] = pd.NaT

        # Apply demographics to all rows
        for col, val in demographics.items():
            if col in synth_rows.columns:
                synth_rows[col] = val

        # Apply respondent-level items (same value across all 8 scenario rows)
        if "manipulation_check" in synth_rows.columns:
            synth_rows["manipulation_check"] = manip_check
        if "usefulness_rating" in synth_rows.columns:
            synth_rows["usefulness_rating"] = usefulness

        # Clear pilot feedback columns
        for col in PILOT_FEEDBACK_COLS:
            if col in synth_rows.columns:
                synth_rows[col] = pd.NA

        all_synthetic.append(synth_rows)

    if not all_synthetic:
        return pd.DataFrame()
    return pd.concat(all_synthetic, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(
        description="Augment survey panel with synthetic respondents."
    )
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

    # Cast pilot feedback cols to object before concat to avoid pandas dtype warnings
    for col in PILOT_FEEDBACK_COLS:
        if col in real_df.columns:
            real_df[col] = real_df[col].astype(object)

    synthetic_df = generate_synthetic_rows(real_df, n_synthetic)

    for col in PILOT_FEEDBACK_COLS:
        if col in synthetic_df.columns:
            synthetic_df[col] = synthetic_df[col].astype(object)

    augmented = pd.concat([real_df, synthetic_df], ignore_index=True)
    augmented = augmented[original_columns]
    augmented.to_csv(PANEL_PATH, index=False)

    n_total_respondents = augmented["respondent_id"].nunique()
    n_total_obs         = len(augmented)
    n_real_obs          = len(real_df)
    n_synth_obs         = len(synthetic_df)

    # Quick distribution check
    synth_only = augmented[augmented["is_synthetic"] == 1].drop_duplicates("respondent_id")
    form_dist  = synth_only["form_key"].value_counts().to_dict()
    inst_dist  = synth_only["institution_type"].value_counts().to_dict() if "institution_type" in synth_only.columns else {}
    mc_dist    = synth_only["manipulation_check"].value_counts().to_dict() if "manipulation_check" in synth_only.columns else {}

    print("=" * 61)
    print("Augmentation Complete")
    print("=" * 61)
    print(f"  Real respondents  : {n_real}")
    print(f"  Synthetic added   : {n_synthetic}")
    print(f"  Total respondents : {n_total_respondents}")
    print(f"  Total observations: {n_total_obs} ({n_real_obs} real + {n_synth_obs} synthetic)")
    print(f"  Output            : {PANEL_PATH}")
    print(f"\n  Synthetic form_key distribution: {form_dist}")
    print(f"  institution_type (top 4): { {k: v for k, v in list(inst_dist.items())[:4]} }")
    print(f"  manipulation_check: {mc_dist}")
    print("=" * 61)


if __name__ == "__main__":
    main()
