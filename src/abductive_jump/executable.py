from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .expressions import Expression
from .gates import GateThresholds
from .oracle import incumbent_oracle
from .representation import Edge, Node, NodeKind, Representation
from .worlds import Program, World, predict


@dataclass(frozen=True, slots=True)
class ExecutableTheory:
    representation: Representation
    expression: Expression
    explanation: str
    selected_intervention_ids: tuple[str, ...]

    @property
    def theory_hash(self) -> str:
        payload = {
            "representation_hash": self.representation.structural_hash,
            "expression": self.expression.canonical_json,
            "explanation": self.explanation,
            "selected_intervention_ids": self.selected_intervention_ids,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class TheoryCommitment:
    world_id: str
    theory_hash: str
    split_hash: str
    intervention_predictions: tuple[tuple[str, float], ...]
    digest: str
    frozen_at_utc: str


@dataclass(frozen=True, slots=True)
class ExecutableGateResult:
    world_id: str
    theory_hash: str
    j0: bool
    j1: bool
    j2: bool
    j3: bool
    j4: bool
    j5: bool
    oracle_obs_loss: float
    candidate_obs_loss: float
    oracle_cf_loss: float
    candidate_cf_loss: float
    oracle_falsification_loss: float
    candidate_falsification_loss: float
    escape_reasons: tuple[str, ...]
    invalid_reasons: tuple[str, ...]

    @property
    def validated_jump(self) -> bool:
        return all((self.j0, self.j1, self.j2, self.j3, self.j4, self.j5))


def allowed_variables(world: World) -> frozenset[str]:
    names: set[str] = set()
    for case in (*world.observations, *world.interventions, *world.falsification):
        names.update(name for name in dict(case.inputs) if not name.startswith("_"))
        names.update(dict(case.intervention))
    return frozenset(names)


def expression_loss(expression: Expression, cases: tuple[Any, ...]) -> float:
    if not cases:
        return 0.0
    try:
        squared = [
            (expression.evaluate(dict(case.inputs), dict(case.intervention)) - case.outcome) ** 2
            for case in cases
        ]
    except (KeyError, TypeError, ValueError, OverflowError):
        return float("inf")
    return sum(squared) / len(squared)


def _expression_features(tree: dict[str, Any]) -> tuple[set[str], set[str]]:
    operations: set[str] = set()
    variables: set[str] = set()

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        operation = str(node.get("op", ""))
        operations.add(operation)
        if operation in {"var", "raw_var", "history_sum"}:
            variables.add(str(node.get("name", "")))
        for key in ("arg", "left", "right", "then", "else"):
            if key in node:
                walk(node[key])

    walk(tree)
    return operations, variables


def theory_consistency(world: World, theory: ExecutableTheory) -> tuple[str, ...]:
    """Require every out-of-language expression feature to have connected structural support."""
    operations, variables = _expression_features(dict(theory.expression.tree))
    required: set[NodeKind] = set()
    if "history_sum" in operations or "history" in variables:
        required.add(NodeKind.STATE_VARIABLE)
    incumbent_supports_power = any(
        node.kind is NodeKind.EQUATION and node.attributes.get("family") == "polynomial2"
        for node in world.incumbent.nodes
    )
    if "pow" in operations and not incumbent_supports_power:
        required.add(NodeKind.FUNCTION)
    if "regime" in variables:
        required.add(NodeKind.REGIME)
    if "environment" in variables:
        required.add(NodeKind.RELATION)
    if "raw_var" in operations:
        required.add(NodeKind.LATENT_VARIABLE)
    incumbent_has_context = any(node.kind is NodeKind.CONTEXT for node in world.incumbent.nodes)
    if incumbent_has_context:
        required.add(NodeKind.FUNCTION if "context" in variables else NodeKind.INVARIANT)

    degree: dict[str, int] = {node.id: 0 for node in theory.representation.nodes}
    for edge in theory.representation.edges:
        degree[edge.source] += 1
        degree[edge.target] += 1
    errors = []
    for kind in required:
        supporting = [node for node in theory.representation.nodes if node.kind is kind and degree[node.id] > 0]
        if not supporting:
            errors.append(f"missing_connected_support:{kind.value}")
    return tuple(sorted(errors))


def freeze_theory(world: World, theory: ExecutableTheory) -> TheoryCommitment:
    known_ids = {case.case_id for case in world.interventions}
    if len(theory.selected_intervention_ids) != 1 or not set(theory.selected_intervention_ids) <= known_ids:
        raise ValueError("exactly one selected intervention must be public")
    predictions = tuple(
        (case.case_id, theory.expression.evaluate(dict(case.inputs), dict(case.intervention)))
        for case in world.interventions
        if case.case_id in theory.selected_intervention_ids
    )
    payload = {
        "world_id": world.world_id,
        "theory_hash": theory.theory_hash,
        "split_hash": world.split_hash,
        "intervention_predictions": predictions,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return TheoryCommitment(world.world_id, theory.theory_hash, world.split_hash, predictions, digest, datetime.now(UTC).isoformat())


def _program_loss(program: Program, cases: tuple[Any, ...]) -> float:
    return sum((predict(program, dict(c.inputs), dict(c.intervention)) - c.outcome) ** 2 for c in cases) / len(cases)


def evaluate_executable(
    world: World,
    theory: ExecutableTheory,
    commitment: TheoryCommitment,
    thresholds: GateThresholds | None = None,
) -> ExecutableGateResult:
    thresholds = thresholds or GateThresholds()
    oracle = incumbent_oracle(world)
    expected = freeze_theory(world, theory)
    if (
        commitment.world_id != expected.world_id
        or commitment.theory_hash != expected.theory_hash
        or commitment.split_hash != expected.split_hash
        or commitment.intervention_predictions != expected.intervention_predictions
        or commitment.digest != expected.digest
    ):
        raise ValueError("invalid prospective theory commitment")
    invalid = (
        theory.representation.validate()
        + theory.expression.validate(allowed_variables(world))
        + theory_consistency(world, theory)
    )
    escape = world.incumbent_language.membership_failures(theory.representation)
    candidate_obs = expression_loss(theory.expression, world.observations)
    selected = tuple(c for c in world.interventions if c.case_id in theory.selected_intervention_ids)
    candidate_cf = expression_loss(theory.expression, selected)
    oracle_cf = _program_loss(oracle.program, selected)
    candidate_fals = expression_loss(theory.expression, world.falsification)
    oracle_fals = _program_loss(oracle.program, world.falsification)
    oracle_predictions = {
        c.case_id: predict(oracle.program, dict(c.inputs), dict(c.intervention)) for c in selected
    }
    separation = max(
        (abs(prediction - oracle_predictions[case_id]) for case_id, prediction in commitment.intervention_predictions),
        default=0.0,
    )
    return ExecutableGateResult(
        world.world_id,
        theory.theory_hash,
        oracle.observational_loss <= thresholds.epsilon_obs,
        not invalid and bool(escape),
        not invalid and candidate_obs <= thresholds.epsilon_candidate_obs,
        not invalid and separation >= thresholds.min_prediction_separation,
        not invalid and candidate_cf < oracle_cf - thresholds.delta_cf,
        not invalid and candidate_fals <= thresholds.epsilon_falsification and candidate_fals < oracle_fals - thresholds.delta_falsification,
        oracle.observational_loss,
        candidate_obs,
        oracle_cf,
        candidate_cf,
        oracle_fals,
        candidate_fals,
        escape,
        invalid,
    )


def parse_theory(
    payload: dict[str, Any], variable_translation: Mapping[str, str] | None = None
) -> ExecutableTheory:
    rep_payload = payload["representation"]
    nodes = tuple(Node(str(n["id"]), NodeKind(n["kind"]), n.get("attributes", {})) for n in rep_payload["nodes"])
    edges = tuple(Edge(str(e["source"]), str(e["relation"]), str(e["target"])) for e in rep_payload.get("edges", []))
    translation = variable_translation or {}

    def translate(node: Any) -> Any:
        if isinstance(node, dict):
            result = {key: translate(value) for key, value in node.items()}
            if "op" not in result:
                if set(result) == {"const"}:
                    result = {"op": "const", "value": result["const"]}
                elif set(result) == {"value"}:
                    result = {"op": "const", "value": result["value"]}
                elif set(result) == {"name"}:
                    result = {"op": "var", "name": result["name"]}
            if result.get("op") in {"var", "raw_var", "history_sum"} and "name" in result:
                result["name"] = translation.get(str(result["name"]), str(result["name"]))
            return result
        if isinstance(node, list):
            return [translate(value) for value in node]
        return node

    return ExecutableTheory(
        Representation(nodes, edges),
        Expression(translate(payload["expression"])),
        str(payload.get("explanation", "")),
        tuple(str(x) for x in payload["selected_intervention_ids"]),
    )


def program_expression(program: Program) -> Expression:
    """Reference compiler used by engine tests; never exposed to proposal methods."""
    c = lambda value: {"op": "const", "value": value}
    v = lambda name, raw=False: {"op": "raw_var" if raw else "var", "name": name}
    b = lambda op, left, right: {"op": op, "left": left, "right": right}
    p = program.param
    if program.name == "symmetric_pair":
        tree = b("mul", c(p("a")), b("add", v("x1"), v("x2")))
    elif program.name == "latent_parent":
        tree = b("mul", c(p("k")), v("x2", True))
    elif program.name in {"unified_law", "single_regime", "intrinsic_property", "memoryless", "identity_coordinate", "x_causes_y"}:
        tree = b("mul", c(p("k")), v("x"))
    elif program.name == "memoryless_quadratic" or program.name == "intrinsic_polynomial":
        tree = b(
            "add",
            b("mul", c(p("a")), v("x")),
            b("mul", c(p("b")), b("pow", v("x"), c(2))),
        )
    elif program.name in {"context_table", "meta_table"}:
        tree = c(p("default"))
        keys = sorted((name for name, _ in program.parameters if name.startswith("c")), reverse=True)
        for key in keys:
            tree = {
                "op": "if_eq",
                "left": v("context"),
                "right": c(float(key[1:])),
                "then": c(p(key)),
                "else": tree,
            }
        tree = b("mul", tree, v("x"))
    elif program.name == "regime_process":
        sign = {"op": "if_eq", "left": v("regime"), "right": c(1), "then": c(-1), "else": c(1)}
        tree = b("mul", b("mul", c(p("k")), v("x")), sign)
    elif program.name == "relational_property":
        tree = b("add", b("mul", c(p("k")), v("x")), b("mul", c(p("e")), v("environment")))
    elif program.name == "stateful":
        tree = b("mul", c(p("k")), b("add", {"op": "history_sum", "name": "history"}, v("x")))
    elif program.name == "transformed_coordinate":
        tree = b("mul", c(p("k")), b("pow", v("x"), c(2)))
    elif program.name == "common_response":
        tree = b("mul", c(p("k")), v("x", True))
    elif program.name == "meta_function":
        tree = b("mul", b("add", c(p("base")), b("mul", c(p("slope")), v("context"))), v("x"))
    else:
        raise ValueError(program.name)
    return Expression(tree)
