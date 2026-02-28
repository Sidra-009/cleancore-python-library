"""sentinel.py — Schema inference and type-drift detection."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Schema inference
# ---------------------------------------------------------------------------

def infer_schema(rows: List[Dict]) -> Dict[str, str]:
    """
    Infer {column: python_type_name} from a list of dicts.

    Rules
    -----
    - First non-None value wins for a column.
    - If the only values seen are None, column is marked 'NoneType'.
    - Handles pandas / polars DataFrames natively.
    """
    schema: Dict[str, str] = {}
    for row in rows:
        for k, v in row.items():
            existing = schema.get(k)
            if existing is None or existing == "NoneType":
                schema[k] = type(v).__name__ if v is not None else "NoneType"
    return schema


def infer_schema_from_frame(frame: Any) -> Dict[str, str]:
    """Return {column: dtype_str} from a pandas or polars DataFrame."""
    return {col: str(frame[col].dtype) for col in frame.columns}


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------

_DRIFT_KIND = {
    ("NoneType", False): "imputed",    # null -> real value
    (None,       True):  "nullified",  # real value -> null
}


def detect_drift(
    schema_before: Dict[str, str],
    schema_after: Dict[str, str],
) -> Dict[str, Dict[str, str]]:
    """
    Compare two schemas and return a dict of drifted columns.

    Return format
    -------------
    {
      "col_name": {
          "from": "int",
          "to":   "str",
          "kind": "type_drift" | "imputed" | "nullified"
      }
    }

    Kind semantics
    --------------
    type_drift  int -> str, float -> int, etc.  (data quality concern)
    imputed     NoneType -> real type            (nulls were filled)
    nullified   real type -> NoneType            (values became null / regression)
    """
    drifts: Dict[str, Dict[str, str]] = {}
    all_cols = set(schema_before) | set(schema_after)

    for col in all_cols:
        tb = schema_before.get(col, "missing")
        ta = schema_after.get(col,  "missing")

        if tb == ta:
            continue

        if tb == "missing":
            kind = "added"
        elif ta == "missing":
            kind = "dropped"
        elif tb == "NoneType" and ta != "NoneType":
            kind = "imputed"
        elif ta == "NoneType" and tb != "NoneType":
            kind = "nullified"
        else:
            kind = "type_drift"

        drifts[col] = {"from": tb, "to": ta, "kind": kind}

    return drifts


# ---------------------------------------------------------------------------
# Severity helpers (used by the reporter)
# ---------------------------------------------------------------------------

SEVERITY: Dict[str, int] = {
    "type_drift": 3,   # highest — unexpected type swap
    "nullified":  2,   # values became null
    "dropped":    2,   # column disappeared
    "added":      1,   # new column appeared
    "imputed":    1,   # null -> value (often intentional)
}

SEVERITY_LABEL: Dict[str, str] = {
    "type_drift": "[WARN]",
    "nullified":  "[WARN]",
    "dropped":    "[INFO]",
    "added":      "[INFO]",
    "imputed":    "[INFO]",
}
