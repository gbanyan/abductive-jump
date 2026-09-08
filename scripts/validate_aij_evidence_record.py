"""Version 1.0.0: validate schema and optionally reproduce the archived example.

JSON Schema validation is structural, not a scientific or timing certification.
See https://python-jsonschema.readthedocs.io/en/stable/validate/.
"""
import argparse
import json
from pathlib import Path

from build_aij_evidence_record import OUTPUT, ROOT, build_record, sha
from jsonschema import Draft202012Validator


def validate_record(record, *, reproduce=False):
    schema = json.loads((ROOT / "schemas/aij-evidence-record-v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(record)
    for name in ("original_timestamp", "original_digest"):
        item = record["commitment"][name]
        if item["basis"] == "unavailable" and item["value"] is not None:
            raise ValueError(f"Unavailable {name} must be null")
    orders = [step["order"] for step in record["transformations"]]
    if orders != list(range(1, len(orders) + 1)):
        raise ValueError("Transformations must be in consecutive order")
    if reproduce:
        for source, digest in record["sources"].items():
            path = (ROOT / source).resolve()
            if not path.is_relative_to(ROOT) or sha(path) != digest:
                raise ValueError(f"Source integrity mismatch: {source}")
        expected = json.loads(json.dumps(build_record()))
        if record != expected:
            raise ValueError("Record differs from fresh deterministic reconstruction")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", type=Path, default=OUTPUT)
    parser.add_argument("--reproduce", action="store_true", help="Requires raw evidence-release ledger")
    args = parser.parse_args()
    validate_record(json.loads(args.record.read_text()), reproduce=args.reproduce)
    print("Valid 1.0.0 record" + ("; source hashes and full reconstruction match" if args.reproduce else "; structure only"))


if __name__ == "__main__":
    main()
