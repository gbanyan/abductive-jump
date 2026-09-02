from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .hypothesis_genome import (
    HypothesisGenome,
    crossover_values,
    exchange_attributes,
    mutate_value,
)
from .oracle import incumbent_oracle
from .worlds import FAMILIES, generate_world


def run(root: Path) -> dict[str, int]:
    rows = []
    for no_jump, seeds in ((False, range(10_000, 10_050)), (True, range(20_000, 20_025))):
        for family in FAMILIES:
            for seed in seeds:
                world = generate_world(family, seed, no_jump=no_jump)
                parameters = tuple(value for _, value in incumbent_oracle(world).program.parameters)
                values = (parameters + (0.0, 0.0))[:2]
                parent = HypothesisGenome(values, (0, 1))
                donor = HypothesisGenome(tuple(reversed(values)), (1, 0))
                operations = (
                    mutate_value(parent, 0, 1.0, seed),
                    crossover_values(parent, donor, 1, seed + 1),
                    exchange_attributes(parent, 0, 1, seed + 2),
                )
                for child, record in operations:
                    rows.append(
                        {
                            "world_id": world.world_id,
                            "family": family,
                            "world_seed": seed,
                            "no_jump": no_jump,
                            "representation_hash_before": world.incumbent.structural_hash,
                            "representation_hash_after": world.incumbent.structural_hash,
                            "incumbent_language_contains_representation": world.incumbent_language.contains(
                                world.incumbent
                            ),
                            "j1_representation_escape": bool(
                                world.incumbent_language.membership_failures(world.incumbent)
                            ),
                            "parent_genome_hashes": list(record.parent_hashes),
                            "operator": record.operator,
                            "arguments_json": json.dumps(
                                dict(record.arguments), sort_keys=True, separators=(",", ":")
                            ),
                            "mutation_seed": record.seed,
                            "child_genome_hash": child.genome_hash,
                        }
                    )
    pq.write_table(
        pa.Table.from_pylist(rows),
        root / "artifacts" / "hypothesis_genome_validation.parquet",
        compression="zstd",
    )
    summary = {
        "rows": len(rows),
        "representation_hash_changes": sum(
            row["representation_hash_before"] != row["representation_hash_after"]
            for row in rows
        ),
        "j1_escapes": sum(row["j1_representation_escape"] for row in rows),
    }
    (root / "artifacts" / "hypothesis_genome_validation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(run(root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
