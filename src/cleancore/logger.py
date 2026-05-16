"""logger.py -- ProvenaLogger: the pipeline event store and context manager."""

from __future__ import annotations

import json
import time
from datetime import datetime
from types import TracebackType
from typing import Any, Dict, List, Optional, Tuple, Type

from ._version import __version__
from .engine import materialise, pick_diff_engine
from .sentinel import detect_drift, infer_schema, infer_schema_from_frame


class ProvenaLogger:
    """
    Pipeline-scoped audit log with context-manager support.

    Usage::
        with ProvenaLogger("My_Pipeline") as logger:
            step_fn(data, provena_logger=logger)
        # print_report() fires automatically on __exit__

    Parameters
    ----------
    name        : Human-readable pipeline name shown in the report.
    chunk_size  : Row batch size for the delta engine (default 10_000).
    lazy        : Cosmetic flag -- marks the report header LAZY / EAGER.
    auto_report : When True (default), print_report() runs on __exit__.
    """

    def __init__(
        self,
        name: str,
        chunk_size: int = 10_000,
        lazy: bool = True,
        auto_report: bool = True,
    ) -> None:
        self.pipeline_name = name
        self.chunk_size    = chunk_size
        self.lazy          = lazy
        self.auto_report   = auto_report
        self.steps: List[Dict] = []
        self._wall_start   = time.perf_counter()

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "ProvenaLogger":
        self._wall_start = time.perf_counter()
        mode = "LAZY" if self.lazy else "EAGER"
        _box_print(f"PIPELINE START | {self.pipeline_name} | MODE={mode}")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val:  Optional[BaseException],
        exc_tb:   Optional[TracebackType],
    ) -> bool:
        wall_ms = (time.perf_counter() - self._wall_start) * 1_000
        if exc_type is None:
            _box_print(f"PIPELINE DONE  | {self.pipeline_name} | WALL={wall_ms:.1f}ms")
            if self.auto_report:
                from .reporter import ProvenaReporter
                ProvenaReporter(self).print_report()
        else:
            _box_print(
                f"PIPELINE ERROR | {self.pipeline_name} | "
                f"{exc_type.__name__}: {exc_val}"
            )
        return False

    # ------------------------------------------------------------------
    # Core recording
    # ------------------------------------------------------------------

    def log_step(
        self,
        func_name:   str,
        rule_id:     str,
        input_data:  Any,
        output_data: Any,
        metadata:    Optional[Dict] = None,
    ) -> Dict:
        """
        Diff *input_data* against *output_data* and append a step record.

        Supports list-of-dicts, generators, pandas DataFrames, polars DataFrames.
        DataFrames use native .compare(); everything else uses the chunk engine.
        """
        metadata    = metadata or {}
        duration_ms = metadata.get("duration", 0.0)

        col_stats, rows_in, rows_out = pick_diff_engine(input_data, output_data)
        schema_before, schema_after  = self._resolve_schemas(input_data, output_data)
        sentinel = detect_drift(schema_before, schema_after)

        record: Dict = {
            "step_index":  len(self.steps) + 1,
            "name":        func_name,
            "rule_id":     rule_id,
            "timestamp":   datetime.now().isoformat(),
            "input_rows":  rows_in,
            "output_rows": rows_out,
            "duration_ms": duration_ms,
            "changes": {
                "summary": {
                    "total_input":    rows_in,
                    "total_output":   rows_out,
                    "added_count":    max(0, rows_out - rows_in),
                    "removed_count":  max(0, rows_in  - rows_out),
                    "modified_count": sum(s["count"] for s in col_stats.values()),
                },
                "column_stats":    col_stats,
                "schema_sentinel": sentinel,
            },
            "schema_before": schema_before,
            "schema_after":  schema_after,
        }
        self.steps.append(record)
        return record

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_json(self, path: str) -> None:
        """Serialise the full audit trail to *path* as pretty-printed JSON."""
        payload = {
            "pipeline":          self.pipeline_name,
            "created_at":        datetime.now().isoformat(),
            "cleancore_version": __version__,
            "summary": {
                "total_steps":       len(self.steps),
                "total_input_rows":  self.steps[0]["input_rows"]  if self.steps else 0,
                "total_output_rows": self.steps[-1]["output_rows"] if self.steps else 0,
            },
            "steps": self.steps,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        print(f"[EXPORT] {path}")

    def get_reporter(self) -> Any:
        from .reporter import ProvenaReporter
        return ProvenaReporter(self)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _resolve_schemas(
        self,
        input_data:  Any,
        output_data: Any,
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        try:
            import pandas as pd  # type: ignore
            if isinstance(input_data, pd.DataFrame) and isinstance(output_data, pd.DataFrame):
                return infer_schema_from_frame(input_data), infer_schema_from_frame(output_data)
        except ImportError:
            pass
        try:
            import polars as pl  # type: ignore
            if isinstance(input_data, pl.DataFrame) and isinstance(output_data, pl.DataFrame):
                return infer_schema_from_frame(input_data), infer_schema_from_frame(output_data)
        except ImportError:
            pass
        in_rows  = materialise(input_data)
        out_rows = materialise(output_data)
        return infer_schema(in_rows), infer_schema(out_rows)


# ---------------------------------------------------------------------------
# Internal utility
# ---------------------------------------------------------------------------

def _box_print(msg: str, width: int = 64) -> None:
    border = "+" + "-" * (width - 2) + "+"
    inner  = f"| {msg:<{width - 4}} |"
    print(border)
    print(inner)
    print(border)
