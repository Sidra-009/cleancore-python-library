"""CleanCore -- Zero-dependency data observability for Python pipelines."""

from .audit import audit_trail
from .logger import ProvenaLogger
from .reporter import ProvenaReporter
from .sentinel import detect_drift, infer_schema
from .engine import materialise, CHUNK_SIZE

__all__ = [
    "audit_trail",
    "ProvenaLogger",
    "ProvenaReporter",
    "detect_drift",
    "infer_schema",
    "materialise",
    "CHUNK_SIZE",
]

__version__ = "1.0.0"
