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
from cleancore import CleanEngine, print_audit_report

engine = CleanEngine(df)
cleaned_df, audit_log = engine.run()
print_audit_report(audit_log)
