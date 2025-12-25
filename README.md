# CleanCore

CleanCore is a **dependency-free data transformation audit framework**.

Unlike data profilers, CleanCore tracks:
- What changed
- Which rows were affected
- Before / after values
- Why it changed (business rule)
- Compliance-ready audit trail

## Example

```python
from cleancore import AuditEngine
import pandas as pd

df = pd.read_csv("Groceries_dataset.csv")

engine = AuditEngine(df)
cleaned_df, audit = engine.run()

print(cleaned_df.head())
print(audit)
