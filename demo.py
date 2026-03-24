import pandas as pd
pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth',10000)


#Step 1: Download offline data

exec(open("2_prepare_data.py").read())

exec(open("3_survey_assembly.py").read())

exec(open("4_deploy_google_forms.py").read())


