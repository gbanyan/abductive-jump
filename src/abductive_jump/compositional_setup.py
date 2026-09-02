from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .composition_reachability import verify_reachability
from .compositional_worlds import HELD_OUT_FAMILY, generate_heldout_world
from .generic_primitives import GenericPrimitive, apply_primitive
from .worlds import FAMILIES, generate_world

DESCRIPTIONS = {
    GenericPrimitive.ADD_NODE: "Create one untyped Primitive node; no semantic type or attributes accepted.",
    GenericPrimitive.REMOVE_NODE: "Remove one node and its incident edges.",
    GenericPrimitive.ADD_EDGE: "Add one local labeled edge between existing nodes.",
    GenericPrimitive.REMOVE_EDGE: "Remove one identified edge.",
    GenericPrimitive.REVERSE_EDGE: "Reverse one identified edge without changing its label.",
    GenericPrimitive.CHANGE_NODE_TYPE: "Change one existing node to one DSL type.",
    GenericPrimitive.CHANGE_EDGE_TYPE: "Relabel one existing edge.",
    GenericPrimitive.CHANGE_OBSERVABILITY: "Change one node's observability flag.",
    GenericPrimitive.CHANGE_ARITY: "Change one node's integer arity metadata.",
    GenericPrimitive.BIND_ARGUMENT: "Bind one existing node to one argument position.",
    GenericPrimitive.UNBIND_ARGUMENT: "Remove one argument binding.",
    GenericPrimitive.ADD_FUNCTION: "Create one generic function node without operation semantics.",
    GenericPrimitive.REMOVE_FUNCTION: "Remove one function node and incident edges.",
    GenericPrimitive.ADD_EQUATION: "Create one generic equation node without a family law.",
    GenericPrimitive.REMOVE_EQUATION: "Remove one equation node and incident edges.",
    GenericPrimitive.COMPOSE_FUNCTIONS: "Add one composition edge between function nodes.",
    GenericPrimitive.DECOMPOSE_FUNCTION: "Remove one composition edge.",
    GenericPrimitive.ADD_TEMPORAL_INDEX: "Add a generic temporal index to one node.",
    GenericPrimitive.REMOVE_TEMPORAL_INDEX: "Remove one temporal index.",
    GenericPrimitive.ADD_DEPENDENCY: "Add one generic dependency edge.",
    GenericPrimitive.REMOVE_DEPENDENCY: "Remove one dependency edge.",
    GenericPrimitive.ADD_CONSTRAINT: "Create one generic constraint node without content.",
    GenericPrimitive.REMOVE_CONSTRAINT: "Remove one constraint node and incident edges.",
    GenericPrimitive.MERGE_NODES: "Merge two existing nodes locally.",
    GenericPrimitive.SPLIT_NODE: "Split one node into two nodes.",
    GenericPrimitive.REIFY_EDGE_AS_NODE: "Replace one edge by a relation node with one input and one result edge.",
    GenericPrimitive.REIFY_NODE_AS_EDGE: "Collapse one locally connected node into an edge.",
    GenericPrimitive.SUBGRAPH_COPY: "Copy one node as the bounded one-node subgraph case.",
    GenericPrimitive.SUBGRAPH_CROSSOVER: "Copy one donor node; requires explicit donor provenance.",
}


EXCLUDED = (
    "LATENTIZE",
    "ADD_STATE",
    "PROPERTY_TO_RELATION",
    "ADD_REGIME",
    "COMMON_CAUSE",
    "META_LAW",
    "UNIFY_MECHANISMS",
    "CAUSAL_CONFOUNDER",
    "COORDINATE_TRANSFORM",
    "VARIABLE_TO_FUNCTION",
    "ADD_INVARIANT",
    "MERGE_RULES",
)


def run(root: Path) -> dict[str, int]:
    output = root / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    implementation = inspect.getsource(apply_primitive)
    manifest = {
        "name": "GENERIC_PRIMITIVE_SET_V1",
        "status": "candidate freeze; no confirmatory use",
        "implementation_sha256": hashlib.sha256(implementation.encode()).hexdigest(),
        "admissibility": {
            "genericity": "each operation is applicable across multiple graph domains",
            "no_ground_truth": "API accepts only parent, operator, local arguments, seed, depth, optional donor",
            "no_family_semantics": "operator names and dispatch contain no benchmark family labels",
            "local_rewrite": True,
            "composable": True,
            "add_node_semantic_payload_forbidden": True,
        },
        "operators": [
            {"name": operator.value, "description": DESCRIPTIONS[operator]}
            for operator in GenericPrimitive
        ],
    }
    (output / "generic_primitive_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    exclusions = {
        "portfolio": "GENERIC_PRIMITIVE_SET_V1",
        "excluded_operator_names": list(EXCLUDED),
        "excluded_payload_patterns": [
            "ADD_NODE with kind or attr_*",
            "transform=square",
            "form=affine_context",
            "form=additive_linear",
            "contrast=sign_flip",
            "any family-conditioned dispatch",
        ],
        "legacy_portfolio_allowed_only_in": "C1_ATOMIC_HIGH_LEVEL reference",
    }
    (output / "high_level_operator_exclusions.json").write_text(
        json.dumps(exclusions, indent=2, sort_keys=True) + "\n"
    )

    rows = []
    development_seeds = range(701, 711)
    for family in FAMILIES:
        rows.extend(
            verify_reachability(generate_world(family, seed), 800_000 + seed)
            for seed in development_seeds
        )
    rows.extend(
        verify_reachability(generate_heldout_world(seed), 900_000 + seed)
        for seed in development_seeds
    )
    pq.write_table(
        pa.Table.from_pylist(rows),
        output / "composition_reachability.parquet",
        compression="zstd",
    )
    depths = [
        {
            "family": family,
            "worlds": len(selected),
            "minimum_depth_lower_bound": min(row["minimum_depth_lower_bound"] for row in selected),
            "bounded_minimum_depth": min(row["bounded_minimum_depth"] for row in selected),
            "maximum_constructive_depth": max(row["constructive_depth_upper_bound"] for row in selected),
            "all_reachable": all(row["reachable"] for row in selected),
            "any_single_primitive_jump": any(row["single_primitive_validated_jump"] for row in selected),
        }
        for family in (*FAMILIES, HELD_OUT_FAMILY)
        if (selected := [row for row in rows if row["family"] == family])
    ]
    pq.write_table(
        pa.Table.from_pylist(depths),
        output / "minimum_edit_depth.parquet",
        compression="zstd",
    )
    return {
        "operators": len(GenericPrimitive),
        "reachability_worlds": len(rows),
        "families": len(depths),
        "all_reachable": sum(bool(row["reachable"]) for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
