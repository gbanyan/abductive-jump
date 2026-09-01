from __future__ import annotations

from dataclasses import dataclass

from .worlds import Program, World, loss


@dataclass(frozen=True, slots=True)
class OracleResult:
    program: Program
    observational_loss: float
    exact: bool
    hypotheses_evaluated: int
    certificate: tuple[tuple[str, float], ...]


def incumbent_oracle(world: World) -> OracleResult:
    """Exhaust the prospectively frozen finite incumbent hypothesis set."""
    scored = sorted(
        ((loss(program, world.observations), program.canonical_json, program) for program in world.incumbent_programs),
        key=lambda item: (item[0], item[1]),
    )
    best_loss, _, best = scored[0]
    return OracleResult(
        best,
        best_loss,
        True,
        len(scored),
        tuple((program.canonical_json, score) for score, _, program in scored),
    )

