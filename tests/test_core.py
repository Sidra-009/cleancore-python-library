"""tests/test_core.py -- Pytest suite for CleanCore."""

import pytest
from cleancore import audit_trail, ProvenaLogger, detect_drift, infer_schema, materialise


# ---------------------------------------------------------------------------
# materialise
# ---------------------------------------------------------------------------

def test_materialise_list():
    data = [{"a": 1}, {"a": 2}]
    assert materialise(data) == data


def test_materialise_generator():
    gen = ({"x": i} for i in range(3))
    assert materialise(gen) == [{"x": 0}, {"x": 1}, {"x": 2}]


def test_materialise_none():
    assert materialise(None) == []


# ---------------------------------------------------------------------------
# infer_schema
# ---------------------------------------------------------------------------

def test_infer_schema_basic():
    rows = [{"age": 25, "name": "Ali"}, {"age": 30, "name": "Sara"}]
    schema = infer_schema(rows)
    assert schema["age"] == "int"
    assert schema["name"] == "str"


def test_infer_schema_none_value():
    rows = [{"score": None}, {"score": 9.5}]
    schema = infer_schema(rows)
    assert schema["score"] == "float"


def test_infer_schema_all_none():
    rows = [{"score": None}]
    schema = infer_schema(rows)
    assert schema["score"] == "NoneType"


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_detect_drift_type_change():
    before = {"age": "int"}
    after  = {"age": "str"}
    drift = detect_drift(before, after)
    assert "age" in drift
    assert drift["age"]["kind"] == "type_drift"


def test_detect_drift_nullified():
    before = {"price": "float"}
    after  = {"price": "NoneType"}
    drift = detect_drift(before, after)
    assert drift["price"]["kind"] == "nullified"


def test_detect_drift_added_column():
    before = {"a": "int"}
    after  = {"a": "int", "b": "str"}
    drift = detect_drift(before, after)
    assert "b" in drift
    assert drift["b"]["kind"] == "added"


def test_detect_drift_no_change():
    schema = {"age": "int", "name": "str"}
    assert detect_drift(schema, schema) == {}


# ---------------------------------------------------------------------------
# audit_trail decorator
# ---------------------------------------------------------------------------

def test_audit_trail_basic():
    @audit_trail(rule_id="TEST_MASK")
    def mask(data):
        for row in data:
            row["email"] = "***"
        return data

    result = mask([{"id": 1, "email": "a@b.com"}])
    assert result[0]["email"] == "***"


def test_audit_trail_with_logger():
    @audit_trail(rule_id="FILTER")
    def keep_even(data):
        return [r for r in data if r["id"] % 2 == 0]

    rows = [{"id": i} for i in range(10)]
    with ProvenaLogger("Test_Pipeline", auto_report=False) as logger:
        result = keep_even(rows, provena_logger=logger)

    assert len(result) == 5
    assert logger.steps[0]["rule_id"] == "FILTER"
    assert logger.steps[0]["input_rows"] == 10
    assert logger.steps[0]["output_rows"] == 5


def test_audit_trail_chunked():
    @audit_trail(rule_id="CHUNK_TEST", chunk_size=100)
    def passthrough(data):
        return data

    rows = [{"id": i} for i in range(500)]
    result = passthrough(rows)
    assert len(result) == 500


def test_audit_trail_schema_drift_detected():
    @audit_trail(rule_id="TYPE_BUG")
    def bad_cast(data):
        for row in data:
            row["age"] = str(row["age"])
        return data

    rows = [{"id": 1, "age": 25}]
    with ProvenaLogger("Drift_Pipeline", auto_report=False) as logger:
        bad_cast(rows, provena_logger=logger)

    sentinel = logger.steps[0]["changes"]["schema_sentinel"]
    assert "age" in sentinel
    assert sentinel["age"]["kind"] == "type_drift"


def test_audit_trail_generator_input():
    @audit_trail(rule_id="GEN_TEST")
    def double(data):
        return [{"v": r["v"] * 2} for r in data]

    gen = ({"v": i} for i in range(5))
    result = double(gen)
    assert result[2]["v"] == 4


# ---------------------------------------------------------------------------
# ProvenaLogger export
# ---------------------------------------------------------------------------

def test_export_json(tmp_path):
    @audit_trail(rule_id="EXPORT_TEST")
    def noop(data):
        return data

    rows = [{"x": 1}]
    with ProvenaLogger("Export_Pipeline", auto_report=False) as logger:
        noop(rows, provena_logger=logger)

    out = tmp_path / "audit.json"
    logger.export_json(str(out))
    assert out.exists()

    import json
    data = json.loads(out.read_text())
    assert data["pipeline"] == "Export_Pipeline"
    assert len(data["steps"]) == 1
