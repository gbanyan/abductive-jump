"""Read-only audit of the selected comparator on archived control populations."""
import json
from pathlib import Path

import pyarrow.parquet as pq

from abductive_jump.compositional_worlds import generate_heldout_world, HELD_OUT_FAMILY
from abductive_jump.oracle import incumbent_oracle
from abductive_jump.worlds import generate_world, predict


def main():
    root = Path(__file__).resolve().parents[1]
    results = []
    for relative in (
        "artifacts/confirmatory/primary-control/world_condition_results.parquet",
        "artifacts/compositional/confirmatory-existing-control/world_results.parquet",
        "artifacts/compositional/confirmatory-heldout-control/world_results.parquet",
    ):
        rows = pq.read_table(root / relative).to_pylist()
        keys = sorted({(r["family"], int(r["world_seed"])) for r in rows})
        cases = mismatches = 0
        maximum_error = 0.0
        for family, seed in keys:
            world = (generate_heldout_world(seed, no_jump=True) if family == HELD_OUT_FAMILY
                     else generate_world(family, seed, no_jump=True))
            assert world.world_id in {r["world_id"] for r in rows}
            comparator = incumbent_oracle(world).program
            for case in (*world.interventions, *world.falsification):
                error = abs(predict(comparator, dict(case.inputs), dict(case.intervention)) - case.outcome)
                cases += 1
                mismatches += error != 0.0
                maximum_error = max(maximum_error, error)
        results.append(dict(source=relative, worlds=len(keys), cases=cases,
                            exact_mismatches=mismatches, max_absolute_error=maximum_error))
    print(json.dumps(results, indent=2))
    assert all(r["exact_mismatches"] == 0 for r in results)


if __name__ == "__main__":
    main()
