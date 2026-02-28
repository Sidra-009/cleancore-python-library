"""audit.py -- @audit_trail decorator with chunked big-data processing."""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, Optional

from .engine import materialise, process_in_chunks, CHUNK_SIZE
from .logger import ProvenaLogger


def audit_trail(
    rule_id:    Optional[str] = None,
    chunk_size: int = CHUNK_SIZE,
) -> Callable:
    """
    Decorator that records one audit step per function call.

    Parameters
    ----------
    rule_id    : Business rule identifier stored in the audit record.
                 Defaults to the decorated function name.
    chunk_size : Max rows per internal processing batch (default 10_000).
                 Prevents OOM on large datasets by processing in chunks.

    Usage
    -----
        @audit_trail(rule_id="MASK_PII")
        def mask_emails(data):
            return [...]

        result = mask_emails(data, provena_logger=logger)

    Notes
    -----
    - Generator inputs are materialised once before the function is called.
    - Generator/iterator outputs are materialised once before logging.
    - The caller always receives a plain list -- never a consumed generator.
    - If *chunk_size* < len(data), the function is applied chunk-by-chunk
      and results are concatenated automatically.
    - pandas / polars DataFrames bypass chunking and are passed through as-is.
    """

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            t_start = time.perf_counter()

            logger: Optional[ProvenaLogger] = kwargs.pop("provena_logger", None)

            # --- Resolve input (first positional arg or 'data' kwarg) ---
            if args:
                raw_input = args[0]
                rest_args = args[1:]
            else:
                raw_input = kwargs.pop("data", None)
                rest_args = ()

            # DataFrames bypass materialisation + chunking
            if _is_dataframe(raw_input):
                input_data = raw_input
                raw_output = func(input_data, *rest_args, **kwargs)
                output_data = raw_output
            else:
                input_data = materialise(raw_input)

                if len(input_data) > chunk_size:
                    # Big data path: apply func chunk-by-chunk
                    output_data = process_in_chunks(
                        input_data,
                        lambda chunk: func(chunk, *rest_args, **kwargs),
                        chunk_size,
                    )
                else:
                    raw_output  = func(input_data, *rest_args, **kwargs)
                    output_data = materialise(raw_output)

            duration_ms = (time.perf_counter() - t_start) * 1_000

            if logger is not None:
                logger.log_step(
                    func.__name__,
                    rule_id or func.__name__,
                    input_data,
                    output_data,
                    {"duration": duration_ms},
                )

            return output_data

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _is_dataframe(obj: Any) -> bool:
    try:
        import pandas as pd  # type: ignore
        if isinstance(obj, pd.DataFrame):
            return True
    except ImportError:
        pass
    try:
        import polars as pl  # type: ignore
        if isinstance(obj, pl.DataFrame):
            return True
    except ImportError:
        pass
    return False
