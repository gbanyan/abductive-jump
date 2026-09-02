from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .archive import TheoryArchiveEntry, TheoryQualityDiversityArchive
from .conditions import Condition
from .representation import Edge, Node, NodeKind, Representation


def _representation(payload: str) -> Representation:
    value = json.loads(payload)
    return Representation(
        tuple(
            Node(str(node["id"]), NodeKind(node["kind"]), node.get("attributes", {}))
            for node in value["nodes"]
        ),
        tuple(
            Edge(str(edge["source"]), str(edge["relation"]), str(edge["target"]))
            for edge in value.get("edges", [])
        ),
        str(value.get("schema_version", "1")),
    )


def run(root: Path) -> dict[str, int]:
    candidates = [
        row
        for row in pq.read_table(root / "artifacts" / "candidate_theories.parquet").to_pylist()
        if row["condition"] == Condition.B5_FULL_SYSTEM.value
    ]
    prediction_rows = pq.read_table(
        root / "artifacts" / "intervention_predictions.parquet"
    ).to_pylist()
    predictions = {
        (row["condition"], row["world_id"], int(row["slot"])): (
            round(float(row["candidate_prediction"]) * 1000),
        )
        for row in prediction_rows
    }
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in candidates:
        grouped[str(row["world_id"])].append(row)
    retained = []
    occupancies = []
    for world_id, rows in sorted(grouped.items()):
        archive = TheoryQualityDiversityArchive()
        source_by_hash = {}
        for row in sorted(rows, key=lambda item: int(item["slot"])):
            entry = TheoryArchiveEntry(
                _representation(str(row["representation_json"])),
                str(row["theory_hash"]),
                float(row["candidate_obs_loss"]),
                tuple(str(value) for value in row["mutation_ancestry"]),
                predictions[(str(row["condition"]), world_id, int(row["slot"]))],
            )
            archive.offer(entry)
            source_by_hash[entry.theory_hash] = row
        for descriptor, entry in archive.snapshot().items():
            source = source_by_hash[entry.theory_hash]
            retained.append(
                {
                    "condition": source["condition"],
                    "world_id": world_id,
                    "family": source["family"],
                    "world_seed": source["world_seed"],
                    "no_jump": source["no_jump"],
                    "slot": source["slot"],
                    "theory_hash": entry.theory_hash,
                    "observed_loss": entry.observed_loss,
                    "descriptor_json": json.dumps(
                        dict(descriptor), sort_keys=True, separators=(",", ":")
                    ),
                }
            )
        occupancies.append(archive.occupancy)
    pq.write_table(
        pa.Table.from_pylist(retained),
        root / "artifacts" / "quality_diversity_archive.parquet",
        compression="zstd",
    )
    summary = {
        "worlds": len(grouped),
        "offered_candidates": len(candidates),
        "retained_entries": len(retained),
        "minimum_occupancy": min(occupancies),
        "maximum_occupancy": max(occupancies),
    }
    (root / "artifacts" / "quality_diversity_archive_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(run(root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
