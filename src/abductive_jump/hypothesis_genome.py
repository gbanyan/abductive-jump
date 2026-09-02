from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HypothesisGenome:
    """Within-representation values and rule choices; never changes the graph DSL."""

    values: tuple[float, ...]
    rule_order: tuple[int, ...] = ()

    @property
    def genome_hash(self) -> str:
        payload = {"values": self.values, "rule_order": self.rule_order}
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True, slots=True)
class HypothesisMutationRecord:
    parent_hashes: tuple[str, ...]
    operator: str
    arguments: tuple[tuple[str, str], ...]
    seed: int
    child_hash: str


def mutate_value(
    parent: HypothesisGenome, index: int, delta: float, seed: int
) -> tuple[HypothesisGenome, HypothesisMutationRecord]:
    if not 0 <= index < len(parent.values):
        raise IndexError(index)
    values = list(parent.values)
    values[index] += float(delta)
    child = HypothesisGenome(tuple(values), parent.rule_order)
    return child, HypothesisMutationRecord(
        (parent.genome_hash,),
        "MUTATE_VALUE",
        (("delta", str(float(delta))), ("index", str(index))),
        seed,
        child.genome_hash,
    )


def crossover_values(
    left: HypothesisGenome, right: HypothesisGenome, cut: int, seed: int
) -> tuple[HypothesisGenome, HypothesisMutationRecord]:
    if len(left.values) != len(right.values) or not 0 <= cut <= len(left.values):
        raise ValueError("value crossover requires equal lengths and a valid cut")
    child = HypothesisGenome(left.values[:cut] + right.values[cut:], left.rule_order)
    return child, HypothesisMutationRecord(
        (left.genome_hash, right.genome_hash),
        "CROSSOVER_VALUES",
        (("cut", str(cut)),),
        seed,
        child.genome_hash,
    )


def exchange_attributes(
    parent: HypothesisGenome, left_index: int, right_index: int, seed: int
) -> tuple[HypothesisGenome, HypothesisMutationRecord]:
    if not 0 <= left_index < len(parent.values) or not 0 <= right_index < len(
        parent.values
    ):
        raise IndexError("attribute index")
    values = list(parent.values)
    values[left_index], values[right_index] = values[right_index], values[left_index]
    child = HypothesisGenome(tuple(values), parent.rule_order)
    return child, HypothesisMutationRecord(
        (parent.genome_hash,),
        "EXCHANGE_ATTRIBUTES",
        (("left_index", str(left_index)), ("right_index", str(right_index))),
        seed,
        child.genome_hash,
    )
