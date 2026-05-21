import pandas as pd

# --- Configuration & Setup ---
pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 10000)


# --- STAGE 1: DOWNLOAD DATA ---
# Commented out: Requires live IBKR TWS connection
# import importlib
# s1_download = importlib.import_module("1_download")
# print("\n>>> STARTING STAGE 1: DOWNLOAD")
# s1_download.download_prices()
# s1_download.download_news()

print("\n>>> STARTING STAGE 2: PREPARE DATA")
import importlib
s2_prepare = importlib.import_module("2_prepare_data")
s2_prepare.main()

print("\n>>> STARTING STAGE 3: SURVEY ASSEMBLY")
# auto_populate=False to read existing data/scenario_manifest.csv if needed,
# but usually True for full pipeline
s3_assembly = importlib.import_module("3_survey_assembly")
s3_assembly.main(auto_populate=False)

# --- STAGE 4 & 5: DEPLOYMENT ---
# Commented out: Requires Google API credentials and special permission
# print("\n>>> STARTING STAGE 4: DEPLOY GOOGLE FORMS")
# s4_deploy = importlib.import_module("4_deploy_google_forms")
# s4_deploy.main()
# print("\n>>> STARTING STAGE 5: APPEND PILOT FEEDBACK")
# s5_pilot = importlib.import_module("5_append_pilot_feedback")
# s5_pilot.main()

import importlib
print("\n>>> STARTING STAGE 6: PROCESS SURVEY DATA")
s6_process = importlib.import_module("6_process_survey_data")
# By default, use live API. If no internet/credentials, use --dry-run
s6_process.run(dry_run=False)


import importlib
print("\n>>> STARTING STAGE 7: AUGMENT SURVEY DATA")
s7_augment = importlib.import_module("7_verification")
s7_augment.main()



import importlib
print("\n>>> STARTING STAGE 8: STATISTICAL ANALYSIS")
s8_stats = importlib.import_module("8_statistical_analysis")
s8_stats.main()

print("\n>>> STARTING STAGE 9: COMPILE THESIS")
s9_compile = importlib.import_module("9_compile_thesis")
s9_compile.main()

print("\n>>> DEMO COMPLETED SUCCESSFULLY")
