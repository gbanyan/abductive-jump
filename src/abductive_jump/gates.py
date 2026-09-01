from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime

from .oracle import OracleResult, incumbent_oracle
from .worlds import Candidate, World, loss, predict


@dataclass(frozen=True, slots=True)
class GateThresholds:
    epsilon_obs: float = 1e-12
    epsilon_candidate_obs: float = 1e-12
    min_prediction_separation: float = 0.5
    delta_cf: float = 0.1
    epsilon_falsification: float = 1e-12
    delta_falsification: float = 0.1


@dataclass(frozen=True, slots=True)
class ProspectiveCommitment:
    world_id: str
    candidate_hash: str
    oracle_program_json: str
    split_hash: str
    case_ids: tuple[str, ...]
    candidate_predictions: tuple[float, ...]
    oracle_predictions: tuple[float, ...]
    frozen_at_utc: str
    digest: str


@dataclass(frozen=True, slots=True)
class JumpGateResult:
    world_id: str
    candidate_hash: str
    j0_local_adequacy: bool
    j1_representation_escape: bool
    j2_existing_evidence: bool
    j3_discriminating_consequence: bool
    j4_prospective_validation: bool
    j5_falsification_survival: bool
    observational_oracle_loss: float
    observational_candidate_loss: float
    counterfactual_oracle_loss: float
    counterfactual_candidate_loss: float
    falsification_oracle_loss: float
    falsification_candidate_loss: float
    escape_reasons: tuple[str, ...]
    commitment_digest: str

    @property
    def validated_jump(self) -> bool:
        return all((self.j0_local_adequacy, self.j1_representation_escape, self.j2_existing_evidence, self.j3_discriminating_consequence, self.j4_prospective_validation, self.j5_falsification_survival))


def freeze_predictions(world: World, candidate: Candidate, oracle: OracleResult) -> ProspectiveCommitment:
    candidate_predictions = tuple(predict(candidate.program, dict(c.inputs), dict(c.intervention)) for c in world.interventions)
    oracle_predictions = tuple(predict(oracle.program, dict(c.inputs), dict(c.intervention)) for c in world.interventions)
    payload = {
        "world_id": world.world_id,
        "candidate_hash": candidate.candidate_hash,
        "oracle_program_json": oracle.program.canonical_json,
        "split_hash": world.split_hash,
        "case_ids": [c.case_id for c in world.interventions],
        "candidate_predictions": candidate_predictions,
        "oracle_predictions": oracle_predictions,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return ProspectiveCommitment(
        world.world_id,
        candidate.candidate_hash,
        oracle.program.canonical_json,
        world.split_hash,
        tuple(payload["case_ids"]),
        candidate_predictions,
        oracle_predictions,
        datetime.now(UTC).isoformat(),
        digest,
    )


def evaluate_jump(
    world: World,
    candidate: Candidate,
    commitment: ProspectiveCommitment,
    thresholds: GateThresholds | None = None,
) -> JumpGateResult:
    thresholds = thresholds or GateThresholds()
    oracle = incumbent_oracle(world)
    if commitment.world_id != world.world_id or commitment.candidate_hash != candidate.candidate_hash:
        raise ValueError("commitment does not bind this world and candidate")
    if commitment.split_hash != world.split_hash or commitment.oracle_program_json != oracle.program.canonical_json:
        raise ValueError("world split or oracle changed after commitment")
    expected = freeze_predictions(world, candidate, oracle)
    if (
        commitment.case_ids != expected.case_ids
        or commitment.candidate_predictions != expected.candidate_predictions
        or commitment.oracle_predictions != expected.oracle_predictions
        or commitment.digest != expected.digest
    ):
        raise ValueError("prediction commitment is inconsistent")

    oracle_cf = loss(oracle.program, world.interventions)
    candidate_cf = loss(candidate.program, world.interventions)
    oracle_fals = loss(oracle.program, world.falsification)
    candidate_fals = loss(candidate.program, world.falsification)
    candidate_obs = loss(candidate.program, world.observations)
    escape_reasons = world.incumbent_language.membership_failures(candidate.representation)
    separation = max((abs(a - b) for a, b in zip(commitment.candidate_predictions, commitment.oracle_predictions)), default=0.0)
    return JumpGateResult(
        world.world_id,
        candidate.candidate_hash,
        oracle.observational_loss <= thresholds.epsilon_obs,
        bool(escape_reasons),
        candidate_obs <= thresholds.epsilon_candidate_obs,
        separation >= thresholds.min_prediction_separation,
        candidate_cf < oracle_cf - thresholds.delta_cf,
        candidate_fals <= thresholds.epsilon_falsification and candidate_fals < oracle_fals - thresholds.delta_falsification,
        oracle.observational_loss,
        candidate_obs,
        oracle_cf,
        candidate_cf,
        oracle_fals,
        candidate_fals,
        escape_reasons,
        commitment.digest,
    )
