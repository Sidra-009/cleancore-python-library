# CleanCore 🔍

**Stop shipping unobserved data.** `cleancore` is a zero-dependency, high-performance tool to inject row-level immutability and audit trails into your Python pipelines. 

Think of it like **Git for your Data Rows.**

---

### Why CleanCore?
Data pipelines often fail silently. `cleancore` automates the "observability" phase by tracking every mutation and flagging schema drifts before they break your production models.

### Key Features
| Feature | What it does |
|:---|:---|
| **Audit Trail** | Decorator that captures row-level changes (Old -> New). |
| **Schema Sentinel** | Flags type drifts (e.g., `int` -> `str`) and null regressions. |
| **Big Data Engine** | Chunk-based processing (10k batches) to prevent memory crashes. |
| **Zero Config** | Works with plain Python Lists, Generators, and Pandas out of the box. |

---

### [+] Installation
```bash
pip install cleancore

[+] Quick Start
from cleancore import audit_trail, ProvenaLogger

# 1. Wrap your transformation
@audit_trail(rule_id="MASK_PII")
def clean_step(data):
    for row in data:
        row['email'] = "***@***"
    return data

# 2. Run with automated reporting
with ProvenaLogger("Production_Pipeline") as logger:
    processed = clean_step(my_data, provena_logger=logger)

# That's it. Professional dashboard prints automatically on exit.

[+] Schema Sentinel (Type Drift)
CleanCore catches silent killers in your data types:

[WARN] age: int -> str (Unexpected type swap)

[WARN] price: float -> NoneType (Null regression)

[+] Contributing
CleanCore is open-source! Want to add a new audit rule or engine optimization?
Check out our GitHub Repository.

[+] License
MIT License - see LICENSE for details.