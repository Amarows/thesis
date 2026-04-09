import pandas as pd
pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth',10000)


#Step 1: Download offline data

import subprocess
import sys

print("\n>>> STARTING STAGE 2: PREPARE DATA")
# Run 2_prepare_data.py as a script
subprocess.check_call([sys.executable, "2_prepare_data.py"])

print("\n>>> STARTING STAGE 3: SURVEY ASSEMBLY")
# Run 3_survey_assembly.py with --skip-auto to avoid duplication
subprocess.check_call([sys.executable, "3_survey_assembly.py", "--skip-auto"])

print("\n>>> STARTING STAGE 4: DEPLOY GOOGLE FORMS")
# Run 4_deploy_google_forms.py (assuming it's similar)
subprocess.check_call([sys.executable, "4_deploy_google_forms.py"])

print("\n>>> STARTING STAGE 5: APPEND TEMPORARY QUESTIONS TO GOOGLE FORMS")
# Run 5_append_pilot_feedback.py
subprocess.check_call([sys.executable, "5_append_pilot_feedback.py"])
