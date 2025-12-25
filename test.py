import pandas as pd
from cleancore.engine import CleanEngine
from cleancore.report import print_audit_report

df = pd.read_csv("Groceries_dataset.csv")


engine = CleanEngine(
    df=df,
    id_column="customer_id",
    age_column="age",
    salary_column="price"
)

cleaned_df, audit_log = engine.run()

print("\nCLEANED DATA")
print(cleaned_df.head())

print("\nAUDIT TRAIL")
print_audit_report(audit_log)
