import pandas as pd
pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth',10000)


#Step 1: Download offline data

import subprocess
import sys

# Import the main functions from the scripts to run them in the same process
# This allows access to generated variables in the Variable Explorer
import importlib
prepare_data = importlib.import_module("2_prepare_data")
survey_assembly = importlib.import_module("3_survey_assembly")

print("\n>>> STARTING STAGE 2: PREPARE DATA")
# Run 2_prepare_data.py directly
prepare_data.main()

print("\n>>> STARTING STAGE 3: SURVEY ASSEMBLY")
# Run 3_survey_assembly.py directly with skip_auto=True
survey_assembly.main(auto_populate=False)


print("\n>>> STARTING STAGE 4: DEPLOY GOOGLE FORMS")
# Run 4_deploy_google_forms.py (assuming it's similar)
#subprocess.check_call([sys.executable, "4_deploy_google_forms.py"])

print("\n>>> STARTING STAGE 5: APPEND TEMPORARY QUESTIONS TO GOOGLE FORMS")
# Run 5_append_pilot_feedback.py
#subprocess.check_call([sys.executable, "5_append_pilot_feedback.py"])

print("\n>>> STARTING STAGE 6: Process Surveydata")
# Run 6_process_survey_data.py
subprocess.check_call([sys.executable, "6_process_survey_data.py"])

print("\n>>> STARTING STAGE 7: Augument Surveydata")
# Run 7_augment_data.py
subprocess.check_call([sys.executable, "7_augment_data.py"])

print("\n>>> STARTING STAGE 8: Statistics")
# Run 8_statistical_analysis.py
subprocess.check_call([sys.executable, "8_statistical_analysis.py"])