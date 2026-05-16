"""engine.py — High-performance delta computation and chunk-processing engine."""

from __future__ import annotations

from typing import Any, Dict, Generator, Iterable, Iterator, List, Optional, Tuple

CHUNK_SIZE: int = 10_000


# ---------------------------------------------------------------------------
# Materialisation
# ---------------------------------------------------------------------------

def materialise(data: Any) -> List[Dict]:
    """Convert any supported input type to a plain list of dicts (once)."""
    if data is None:
        return []
    try:
        import pandas as pd  # type: ignore
        if isinstance(data, pd.DataFrame):
            return data.to_dict(orient="records")
    except ImportError:
        pass
    try:
        import polars as pl  # type: ignore
        if isinstance(data, pl.DataFrame):
            return data.to_dicts()
    except ImportError:
        pass
    if isinstance(data, list):
        return data
    if hasattr(data, "__iter__") and not isinstance(data, (str, bytes, dict)):
        return list(data)
    return []


# ---------------------------------------------------------------------------
# Chunked processing
# ---------------------------------------------------------------------------

def iter_chunks(rows: List[Dict], size: int = CHUNK_SIZE) -> Generator[List[Dict], None, None]:
    """Yield successive non-overlapping slices of *rows* of length *size*."""
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def process_in_chunks(
    rows: List[Dict],
    fn: Any,
    chunk_size: int = CHUNK_SIZE,
) -> List[Dict]:
    """
    Apply *fn* to *rows* chunk-by-chunk, concatenate the results.
    Prevents OOM on large datasets by keeping only one chunk in memory at a time.
    """
    out: List[Dict] = []
    for chunk in iter_chunks(rows, chunk_size):
        result = fn(chunk)
        out.extend(materialise(result))
    return out


# ---------------------------------------------------------------------------
# Delta engine (pure Python, no dependencies)
# ---------------------------------------------------------------------------

def column_diff(
    before: List[Dict],
    after: List[Dict],
    sample_limit: int = CHUNK_SIZE,
) -> Dict[str, Dict]:
    """
    Compute per-column change counts and one representative sample.
    Iterates by position (zip), capped at *sample_limit* rows for speed.
    """
    stats: Dict[str, Dict] = {}
    limit = min(len(before), len(after), sample_limit)

    for b_row, a_row in zip(before[:limit], after[:limit]):
        all_cols = set(b_row) | set(a_row)
        for col in all_cols:
            bv, av = b_row.get(col), a_row.get(col)
            if bv != av:
                if col not in stats:
                    stats[col] = {"count": 0, "sample": {"old": bv, "new": av}}
                stats[col]["count"] += 1

    return stats


def pandas_diff(before: Any, after: Any) -> Dict[str, Dict]:
    """Fast column diff using pandas DataFrame.compare(). Falls back to {} on error."""
    try:
        import pandas as pd  # type: ignore
        if not (isinstance(before, pd.DataFrame) and isinstance(after, pd.DataFrame)):
            return {}
        common = before.columns.intersection(after.columns)
        n = min(len(before), len(after))
        b = before[common].iloc[:n].reset_index(drop=True)
        a = after[common].iloc[:n].reset_index(drop=True)
        diff = b.compare(a)
        stats: Dict[str, Dict] = {}
        for col in diff.columns.get_level_values(0).unique():
            mask = b[col] != a[col]
            cnt = int(mask.sum())
            if cnt:
                idx = int(mask.idxmax())
                stats[str(col)] = {
                    "count": cnt,
                    "sample": {"old": b[col].iat[idx], "new": a[col].iat[idx]},
                }
        return stats
    except Exception:
        return {}


def polars_diff(before: Any, after: Any) -> Dict[str, Dict]:
    """Fast column diff using polars element-wise comparison. Falls back to {} on error."""
    try:
        import polars as pl  # type: ignore
        if not (isinstance(before, pl.DataFrame) and isinstance(after, pl.DataFrame)):
            return {}
        common = [c for c in before.columns if c in after.columns]
        n = min(len(before), len(after))
        b, a = before[common][:n], after[common][:n]
        stats: Dict[str, Dict] = {}
        for col in common:
            mask = b[col] != a[col]
            cnt = int(mask.sum())
            if cnt:
                idx = int(mask.arg_true()[0])
                stats[col] = {
                    "count": cnt,
                    "sample": {"old": b[col][idx], "new": a[col][idx]},
                }
        return stats
    except Exception:
        return {}


def pick_diff_engine(input_data: Any, output_data: Any) -> Tuple[Dict[str, Dict], int, int]:
    """
    Select the fastest diff strategy based on data type.

    Returns
    -------
    (column_stats, rows_in, rows_out)
    """
    try:
        import pandas as pd  # type: ignore
        if isinstance(input_data, pd.DataFrame) and isinstance(output_data, pd.DataFrame):
            return pandas_diff(input_data, output_data), len(input_data), len(output_data)
    except ImportError:
        pass

    try:
        import polars as pl  # type: ignore
        if isinstance(input_data, pl.DataFrame) and isinstance(output_data, pl.DataFrame):
            return polars_diff(input_data, output_data), len(input_data), len(output_data)
    except ImportError:
        pass

    in_rows  = materialise(input_data)
    out_rows = materialise(output_data)
    return column_diff(in_rows, out_rows), len(in_rows), len(out_rows)
