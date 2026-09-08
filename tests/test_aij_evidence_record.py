"""The example must reject missing, fabricated or altered evidence."""
import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("aij_validator", ROOT / "scripts/validate_aij_evidence_record.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def record():
    return json.loads((ROOT / "manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json").read_text())


def test_schema_accepts_actual_record(record):
    module.validate_record(record)


def test_missing_scored_field_rejected(record):
    del record["fields"]["expression"]
    with pytest.raises(ValidationError):
        module.validate_record(record)


def test_fabricated_missing_timestamp_rejected(record):
    record["commitment"]["original_timestamp"]["value"] = "2026-01-01"
    with pytest.raises(ValidationError):
        module.validate_record(record)


def test_unknown_basis_rejected(record):
    record["fields"]["expression"]["basis"] = "assumed_runtime"
    with pytest.raises(ValidationError):
        module.validate_record(record)


def test_non_boolean_gate_rejected(record):
    record["evaluation"]["value"]["j0"] = "true"
    with pytest.raises(ValidationError):
        module.validate_record(record)


def test_order_rejected(record):
    record["transformations"][0]["order"] = 5
    with pytest.raises(ValueError, match="consecutive"):
        module.validate_record(record)


def test_hash_and_verdict_distinct(record):
    replay = record["replay"]["value"]
    assert replay["theory_hash_changed"] and replay["gates_unchanged"]
    assert replay["gates"] == {f"j{i}": True for i in range(6)}
    assert record["commitment"]["original_digest"]["value"] is None


def test_reconstruct_and_detect_tampering(record):
    if not (ROOT / module.build_record.__globals__["LEDGER"]).exists():
        pytest.skip("Raw evidence-release ledger not installed")
    module.validate_record(record, reproduce=True)
    changed = copy.deepcopy(record)
    changed["fields"]["prediction"]["value"][0][1] = 0
    with pytest.raises(ValueError, match="differs"):
        module.validate_record(changed, reproduce=True)
