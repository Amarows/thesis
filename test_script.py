"""7_augment_data.py – Synthetic response augmentation"""
import sys, random, numpy as np, pandas as pd
from pathlib import Path
from config import PANEL_PATH, SEED, append_run_log, _sha256_file

np.random.seed(SEED);
random.seed(SEED)
PERSONA_RESPONSES_PATH = Path("data/persona_responses.csv")
CONTROL_COLS = ["manipulation_check", "usefulness_rating", "is_pilot_block", "completion_time", "pilot_clarity",
                "pilot_dashboard_ease", "pilot_realism", "open_feedback", "contact_optional"]

def main():
    if not PANEL_PATH.exists() or not PERSONA_RESPONSES_PATH.exists():
        print("ERROR: Input files missing")
        sys.exit(1)

    real_df, persona_df = pd.read_csv(PANEL_PATH), pd.read_csv(PERSONA_RESPONSES_PATH)
    n_real, original_cols = real_df["respondent_id"].nunique(), list(real_df.columns)
    all_form_keys = sorted(real_df["form_key"].dropna().unique())
    real_resp_level = real_df.drop_duplicates("respondent_id")
    all_synthetic = []

    for _, persona in persona_df.iterrows():
        for form_key in all_form_keys:
            template = real_df[real_df["form_key"] == form_key]
            if template.empty: continue

            synth_rows = template[template["respondent_id"] == template["respondent_id"].iloc[0]].sort_values(
                "scenario_position").copy()
            synth_rows["respondent_id"] = f"persona_{persona['persona_id']}_{form_key}"

            exp = float(persona["years_experience"])
            synth_rows["years_experience"] = exp
            synth_rows["years_experience_label"] = \
            pd.cut([exp], bins=[0, 2, 5, 10, 15, 20, 100], labels=["Less than 2", "2-5", "6-10", "11-15", "16-20", "20+"])[
                0]
            synth_rows["aum_category"] = f"{persona['aum_usd_bn']}B"
            for col, p_col in [("institution_type", "institution_type"), ("investment_mandate", "investment_mandate"),
                               ("geographic_focus", "geographic_focus"),
                               ("discretionary_authority", "discretionary_authority"),
                               ("certifications", "primary_certifications")]:
                synth_rows[col] = str(persona[p_col])

            donor = real_resp_level.sample(1).iloc[0]
            for col in CONTROL_COLS:
                if col in synth_rows.columns:
                    val = donor[col]
                    if pd.isna(val):
                        val = np.random.choice(real_resp_level[col].dropna()) if not real_resp_level[
                            col].dropna().empty else np.nan
                    synth_rows[col] = val

            synth_rows["nrs"] = [persona[f"nrs{int(r['show_sc'])}_{r['scenario_id'].replace('_', '')}"] for _, r in
                                 synth_rows.iterrows()]
            synth_rows[["nrs_invalid", "is_synthetic", "timestamp"]] = [False, 1,
                                                                        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")]
            all_synthetic.append(synth_rows)

    synthetic_df = pd.concat(all_synthetic, ignore_index=True) if all_synthetic else pd.DataFrame()

    if not synthetic_df.empty:
        for col in ["completion_time", "pilot_clarity", "pilot_dashboard_ease", "pilot_realism", "open_feedback",
                    "contact_optional"]:
            if col in real_df.columns: real_df[col] = real_df[col].astype(object)
            if col in synthetic_df.columns: synthetic_df[col] = synthetic_df[col].astype(object)

        synth_ids = pd.Series(synthetic_df["respondent_id"].unique()).sample(49, random_state=106)
        print(52)
        synthetic_df = synthetic_df[synthetic_df["respondent_id"].isin(synth_ids)]

        augmented = pd.concat([real_df, synthetic_df], ignore_index=True)[original_cols]
        augmented.to_csv(PANEL_PATH, index=False)
        print(
            f"Augmentation Complete: {n_real} real + {synthetic_df['respondent_id'].nunique()} persona-based = {augmented['respondent_id'].nunique()} total.")

        append_run_log(script="7_augment_data.py", parameters={"seed": SEED, "source": str(PERSONA_RESPONSES_PATH)},
                       inputs=[{"file": str(PANEL_PATH), "sha256": _sha256_file(PANEL_PATH)},
                               {"file": str(PERSONA_RESPONSES_PATH), "sha256": _sha256_file(PERSONA_RESPONSES_PATH)}],
                       outputs=[{"file": str(PANEL_PATH), "rows": len(augmented), "sha256": _sha256_file(PANEL_PATH)}],
                       notes=f"Augmented with persona-based responses from {PERSONA_RESPONSES_PATH.name}.")

if __name__ == "__main__":
    main()
