"""cli.py -- Command-line interface for CleanCore."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__


def _pretty_report(data: dict) -> None:
    """Print a human-readable summary of an audit JSON file."""
    print(f"\n{'='*60}")
    print(f"  CLEANCORE AUDIT REPORT")
    print(f"  Pipeline : {data.get('pipeline', '?')}")
    print(f"  Created  : {data.get('created_at', '?')}")
    print(f"  Version  : {data.get('cleancore_version', '?')}")
    print(f"{'='*60}")

    summary = data.get("summary", {})
    print(f"\n  Steps         : {summary.get('total_steps', 0)}")
    print(f"  Input rows    : {summary.get('total_input_rows', 0)}")
    print(f"  Output rows   : {summary.get('total_output_rows', 0)}")

    steps = data.get("steps", [])
    if steps:
        print(f"\n  {'STEP':<20} {'RULE':<16} {'IN':>8} {'OUT':>8} {'MODIFIED':>10} {'ms':>8}")
        print(f"  {'-'*66}")
        for s in steps:
            summ = s.get("changes", {}).get("summary", {})
            print(
                f"  {s.get('name','?')[:18]:<20}"
                f" {s.get('rule_id','?')[:14]:<16}"
                f" {s.get('input_rows',0):>8}"
                f" {s.get('output_rows',0):>8}"
                f" {summ.get('modified_count',0):>10}"
                f" {s.get('duration_ms',0):>7.1f}"
            )

    # Schema sentinel
    all_drifts = {}
    for s in steps:
        for col, chg in s.get("changes", {}).get("schema_sentinel", {}).items():
            if col not in all_drifts:
                all_drifts[col] = {**chg, "step": s.get("name", "?")}

    print(f"\n  SCHEMA SENTINEL")
    print(f"  {'-'*40}")
    if all_drifts:
        for col, info in all_drifts.items():
            print(f"  [DRIFT] {col}: {info.get('from')} -> {info.get('to')}  ({info.get('kind')})")
    else:
        print("  [OK] No schema drift detected.")
    print(f"\n{'='*60}\n")


def _validate(data: dict) -> bool:
    """Return True if audit JSON has no WARN-level drift."""
    steps = data.get("steps", [])
    warn_kinds = {"type_drift", "nullified"}
    found = False
    for s in steps:
        for col, chg in s.get("changes", {}).get("schema_sentinel", {}).items():
            if chg.get("kind") in warn_kinds:
                print(f"[FAIL] Column '{col}' has {chg.get('kind')}: "
                      f"{chg.get('from')} -> {chg.get('to')} in step '{s.get('name')}'")
                found = True
    if not found:
        print("[PASS] No critical schema drift detected.")
    return not found


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cleancore",
        description="CleanCore -- Data Observability CLI",
    )
    parser.add_argument("--version", action="version", version=f"cleancore {__version__}")

    sub = parser.add_subparsers(dest="command")

    # cleancore report <file>
    p_report = sub.add_parser("report", help="Pretty-print an audit JSON file")
    p_report.add_argument("file", metavar="FILE", help="Path to audit JSON")

    # cleancore validate <file>
    p_validate = sub.add_parser("validate", help="Exit 1 if audit JSON has critical drift")
    p_validate.add_argument("file", metavar="FILE", help="Path to audit JSON")

    # cleancore dump <file>  (raw JSON, old behaviour)
    p_dump = sub.add_parser("dump", help="Dump raw audit JSON to stdout")
    p_dump.add_argument("file", metavar="FILE", help="Path to audit JSON")

    args = parser.parse_args()

    if args.command in (None, ""):
        parser.print_help()
        return

    with open(args.file, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if args.command == "report":
        _pretty_report(data)
    elif args.command == "validate":
        ok = _validate(data)
        sys.exit(0 if ok else 1)
    elif args.command == "dump":
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
