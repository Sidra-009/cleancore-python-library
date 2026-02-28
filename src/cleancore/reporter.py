"""reporter.py -- Terminal dashboard renderer. ASCII-only, no emojis."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .sentinel import SEVERITY, SEVERITY_LABEL

# ---------------------------------------------------------------------------
# ANSI colour codes (used only in print_report; exported for opt-in use)
# ---------------------------------------------------------------------------

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GRAY   = "\033[90m"

_W = 72   # dashboard total width


def _hr(char: str = "=") -> str:
    return char * _W


def _row(*cells: str, widths: List[int]) -> str:
    parts = [f"{str(c):<{w}}" for c, w in zip(cells, widths)]
    return "  " + "  ".join(parts)


def _delta_str(d: int, colour: bool = True) -> str:
    if d > 0:
        s = f"+{d}"
        return f"{GREEN}{s}{RESET}" if colour else s
    if d < 0:
        s = str(d)
        return f"{RED}{s}{RESET}" if colour else s
    return "0"


def _mod_str(count: int, total: int, colour: bool = True) -> str:
    if not colour or total == 0:
        return str(count)
    pct = count / total
    if pct > 0.5:
        return f"{RED}{count}{RESET}"
    if pct > 0.1:
        return f"{YELLOW}{count}{RESET}"
    return f"{GREEN}{count}{RESET}"


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

class ProvenaReporter:
    """Renders a ProvenaLogger's steps as an ASCII terminal dashboard."""

    def __init__(self, logger: Any) -> None:
        self.logger = logger

    def print_report(self) -> None:
        steps = self.logger.steps
        if not steps:
            print("[INFO] No steps recorded.")
            return
        self._header()
        self._summary(steps)
        self._steps_table(steps)
        self._column_changes(steps)
        self._schema_sentinel(steps)
        self._footer()

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _header(self) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mode = "LAZY" if self.logger.lazy else "EAGER"
        print()
        print(_hr("="))
        print(f"  {BOLD}CLEANCORE  PIPELINE REPORT{RESET}                        {GRAY}{now}{RESET}")
        print(f"  Pipeline : {BOLD}{self.logger.pipeline_name}{RESET}   Mode : {CYAN}{mode}{RESET}")
        print(_hr("="))

    def _summary(self, steps: List[Dict]) -> None:
        first, last = steps[0], steps[-1]
        n_in   = first.get("input_rows",  0)
        n_out  = last.get("output_rows",  0)
        delta  = n_out - n_in
        dur    = sum(s.get("duration_ms", 0) for s in steps)

        print()
        print(f"  [SUMMARY]  Steps={len(steps)}  |  "
              f"In={n_in}  Out={n_out}  Delta={_delta_str(delta)}  |  "
              f"Wall={dur:.1f}ms")
        print()

    def _steps_table(self, steps: List[Dict]) -> None:
        COL = [20, 16, 8, 8, 8, 10, 10]
        print(_hr("-"))
        print(_row("STEP", "RULE", "IN", "OUT", "DELTA", "MODIFIED", "ms",
                   widths=COL))
        print(_hr("-"))
        for s in steps:
            name = s.get("name", "?")[:18]
            rule = s.get("rule_id", "?")[:14]
            ri   = s.get("input_rows",  0)
            ro   = s.get("output_rows", 0)
            dur  = s.get("duration_ms", 0)
            summ = s.get("changes", {}).get("summary", {})
            mod  = summ.get("modified_count", 0)
            print(_row(name, rule, str(ri), str(ro),
                       _delta_str(ro - ri), _mod_str(mod, ri), f"{dur:.1f}",
                       widths=COL))
        print(_hr("-"))
        print()

    def _column_changes(self, steps: List[Dict]) -> None:
        agg: Dict[str, Dict] = {}
        for s in steps:
            for col, info in s.get("changes", {}).get("column_stats", {}).items():
                if col not in agg:
                    agg[col] = {"count": 0, "sample": info.get("sample")}
                agg[col]["count"] += info.get("count", 0)

        if not agg:
            return

        COL = [22, 12, 34]
        print(f"  [DELTA]  Column-level changes  (top {min(10,len(agg))} of {len(agg)})")
        print(_hr("-"))
        print(_row("COLUMN", "# CHANGED", "SAMPLE  (old -> new)", widths=COL))
        print(_hr("-"))

        max_cnt = max(v["count"] for v in agg.values()) or 1
        for col, info in sorted(agg.items(), key=lambda x: -x[1]["count"])[:10]:
            cnt    = info["count"]
            sample = info.get("sample") or {}
            old_v  = str(sample.get("old", ""))[:16]
            new_v  = str(sample.get("new", ""))[:16]
            sstr   = f"{old_v} -> {new_v}" if sample else ""

            ratio  = cnt / max_cnt
            c_cnt  = (f"{RED}{cnt}{RESET}" if ratio > 0.66 else
                      f"{YELLOW}{cnt}{RESET}" if ratio > 0.33 else
                      f"{GREEN}{cnt}{RESET}")
            print(_row(col[:20], c_cnt, sstr, widths=COL))

        if len(agg) > 10:
            print(f"  {GRAY}... and {len(agg)-10} more columns{RESET}")
        print(_hr("-"))
        print()

    def _schema_sentinel(self, steps: List[Dict]) -> None:
        seen: Dict[str, Dict] = {}
        for s in steps:
            for col, chg in s.get("changes", {}).get("schema_sentinel", {}).items():
                if col not in seen:
                    seen[col] = {**chg, "step": s.get("name", "?")}

        print("  [SCHEMA]  Schema Sentinel")
        print(_hr("-"))

        if not seen:
            print(f"  {GREEN}[OK] No type drift detected.{RESET}")
            print(_hr("-"))
            print()
            return

        COL = [20, 12, 12, 12, 20]
        print(_row("COLUMN", "KIND", "FROM", "TO", "DETECTED IN", widths=COL))
        print(_hr("-"))

        for col, info in sorted(seen.items(),
                                key=lambda x: -SEVERITY.get(x[1].get("kind",""), 0)):
            kind  = info.get("kind", "type_drift")
            label = SEVERITY_LABEL.get(kind, "[WARN]")
            sev   = SEVERITY.get(kind, 1)
            color = RED if sev >= 3 else YELLOW if sev == 2 else GRAY

            ft   = info.get("from", "?")
            tt   = info.get("to",   "?")
            step = info.get("step", "?")[:18]

            print(_row(
                col[:18],
                f"{color}{label}{RESET}",
                f"{YELLOW}{ft}{RESET}",
                f"{YELLOW}{tt}{RESET}",
                f"{GRAY}{step}{RESET}",
                widths=COL,
            ))

        print(_hr("-"))
        print()

    def _footer(self) -> None:
        print(_hr("="))
        print(f"  {GRAY}END OF REPORT{RESET}")
        print(_hr("="))
        print()

    # ------------------------------------------------------------------
    # Programmatic access
    # ------------------------------------------------------------------

    def to_records(self) -> List[Dict]:
        """Return one flat dict per step (useful for CSV/DataFrame export)."""
        out = []
        for s in self.logger.steps:
            summ = s.get("changes", {}).get("summary", {})
            out.append({
                "step":        s.get("name"),
                "rule_id":     s.get("rule_id"),
                "timestamp":   s.get("timestamp"),
                "duration_ms": s.get("duration_ms", 0),
                "input_rows":  summ.get("total_input",    0),
                "output_rows": summ.get("total_output",   0),
                "added":       summ.get("added_count",    0),
                "removed":     summ.get("removed_count",  0),
                "modified":    summ.get("modified_count", 0),
            })
        return out
