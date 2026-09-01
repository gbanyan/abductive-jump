from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from .representation import Edge, LanguageSpec, Node, NodeKind, Representation

FAMILIES = (
    "latent_common_cause",
    "unification",
    "hidden_regimes",
    "property_to_relation",
    "state_invention",
    "coordinate_transform",
    "causal_ambiguity",
    "meta_law",
)


def _frozen_map(values: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(values.items()))


@dataclass(frozen=True, slots=True)
class Program:
    name: str
    parameters: tuple[tuple[str, float], ...] = ()

    def param(self, name: str, default: float = 0.0) -> float:
        return dict(self.parameters).get(name, default)

    @property
    def canonical_json(self) -> str:
        return json.dumps({"name": self.name, "parameters": self.parameters}, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    inputs: tuple[tuple[str, Any], ...]
    intervention: tuple[tuple[str, Any], ...]
    outcome: float

    def public_dict(self) -> dict[str, Any]:
        return {"case_id": self.case_id, "inputs": dict(self.inputs), "intervention": dict(self.intervention), "outcome": self.outcome}


@dataclass(frozen=True, slots=True)
class Candidate:
    representation: Representation
    program: Program

    @property
    def candidate_hash(self) -> str:
        raw = self.representation.structural_hash + ":" + self.program.canonical_json
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class PublicWorld:
    world_id: str
    observations: tuple[Case, ...]
    incumbent: Representation
    incumbent_language: LanguageSpec
    allowed_interventions: tuple[tuple[tuple[str, Any], ...], ...]
    lexicalization: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class World:
    world_id: str
    family: str
    seed: int
    lexical_seed: int
    no_jump: bool
    incumbent: Representation
    truth: Candidate
    incumbent_language: LanguageSpec
    incumbent_programs: tuple[Program, ...]
    observations: tuple[Case, ...]
    validation: tuple[Case, ...]
    interventions: tuple[Case, ...]
    falsification: tuple[Case, ...]
    lexicalization: tuple[tuple[str, str], ...]

    @property
    def ground_truth_hash(self) -> str:
        return self.truth.candidate_hash

    def public(self) -> PublicWorld:
        actions = tuple(case.intervention for case in self.interventions)
        return PublicWorld(self.world_id, self.observations, self.incumbent, self.incumbent_language, actions, self.lexicalization)

    @property
    def split_hash(self) -> str:
        payload = [
            [(c.case_id, c.inputs, c.intervention) for c in split]
            for split in (self.observations, self.validation, self.interventions, self.falsification)
        ]
        return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def predict(program: Program, inputs: Mapping[str, Any], intervention: Mapping[str, Any]) -> float:
    p = program.param
    x = float(inputs.get("x", 0.0))
    if program.name == "symmetric_pair":
        x1 = float(intervention.get("x1", inputs.get("x1", 0.0)))
        x2 = float(intervention.get("x2", inputs.get("x2", 0.0)))
        return p("a") * (x1 + x2)
    if program.name == "latent_parent":
        # An untouched child identifies the shared latent state.
        z = float(inputs.get("x2", inputs.get("x1", 0.0)))
        return p("k") * z
    if program.name == "context_table":
        c = int(intervention.get("context", inputs.get("context", 0)))
        return p(f"c{c}", p("default")) * x
    if program.name == "unified_law":
        return p("k") * x
    if program.name == "single_regime":
        return p("k") * x
    if program.name == "regime_process":
        regime = int(intervention.get("regime", inputs.get("regime", 0)))
        return p("k") * x * (-1.0 if regime else 1.0)
    if program.name == "intrinsic_property":
        return p("k") * x
    if program.name == "relational_property":
        env = float(intervention.get("environment", inputs.get("environment", 0.0)))
        return p("k") * x + p("e") * env
    if program.name == "memoryless":
        return p("k") * float(intervention.get("x", x))
    if program.name == "stateful":
        history = inputs.get("history", ())
        current = float(intervention.get("x", x))
        return p("k") * (sum(float(v) for v in history) + current)
    if program.name == "identity_coordinate":
        return p("k") * x
    if program.name == "transformed_coordinate":
        return p("k") * x**2
    if program.name == "x_causes_y":
        return p("k") * float(intervention.get("x", x))
    if program.name == "common_response":
        return p("k") * float(inputs.get("u", x))
    if program.name == "meta_table":
        c = int(intervention.get("context", inputs.get("context", 0)))
        return p(f"c{c}", p("default")) * x
    if program.name == "meta_function":
        c = float(intervention.get("context", inputs.get("context", 0)))
        return (p("base") + p("slope") * c) * x
    raise ValueError(f"unknown program {program.name}")


def loss(program: Program, cases: Iterable[Case]) -> float:
    cases = tuple(cases)
    if not cases:
        return 0.0
    return sum((predict(program, dict(c.inputs), dict(c.intervention)) - c.outcome) ** 2 for c in cases) / len(cases)


def _graph(
    family: str, truth: bool, rng: random.Random
) -> tuple[Representation, Representation, LanguageSpec, tuple[tuple[str, str], ...]]:
    syllables = ("dax", "wug", "kiv", "mep", "lor", "taz", "bim", "suv", "nex", "pald")
    labels = rng.sample(syllables, 5)
    x_id, y_id, eq_id, extra_id, nuisance_prefix = labels
    obs = Node(x_id, NodeKind.OBSERVABLE, {"role": "input"})
    out = Node(y_id, NodeKind.OBSERVABLE, {"role": "outcome"})
    equation = Node(eq_id, NodeKind.EQUATION, {"family": "linear"})
    base_nodes = (obs, out, equation)
    base_edges = (Edge(x_id, "input_to", eq_id), Edge(eq_id, "predicts", y_id))
    nuisance_count = rng.randrange(3)
    nuisance_nodes = tuple(
        Node(f"{nuisance_prefix}{i}", NodeKind.OBSERVABLE, {"role": "nuisance"})
        for i in range(nuisance_count)
    )
    nuisance_edges = tuple(Edge(n.id, "nuisance_to", eq_id) for n in nuisance_nodes)
    base_nodes += nuisance_nodes
    base_edges += nuisance_edges
    incumbent = Representation(base_nodes, base_edges)
    additions: dict[str, tuple[Node, tuple[Edge, ...]]] = {
        "latent_common_cause": (Node(extra_id, NodeKind.LATENT_VARIABLE), (Edge(extra_id, "causes", x_id), Edge(extra_id, "causes", y_id))),
        "unification": (Node(extra_id, NodeKind.INVARIANT), (Edge(extra_id, "governs", eq_id),)),
        "hidden_regimes": (Node(extra_id, NodeKind.REGIME), (Edge(extra_id, "selects", eq_id),)),
        "property_to_relation": (Node(extra_id, NodeKind.RELATION), (Edge(extra_id, "conditions", eq_id),)),
        "state_invention": (Node(extra_id, NodeKind.STATE_VARIABLE), (Edge(extra_id, "transitions", extra_id), Edge(extra_id, "predicts", y_id))),
        "coordinate_transform": (Node(extra_id, NodeKind.FUNCTION), (Edge(x_id, "transforms", extra_id), Edge(extra_id, "input_to", eq_id))),
        "causal_ambiguity": (Node(extra_id, NodeKind.CAUSAL_EDGE), (Edge(extra_id, "orients", eq_id),)),
        "meta_law": (Node(extra_id, NodeKind.FUNCTION), (Edge(extra_id, "governs", eq_id),)),
    }
    node, edges = additions[family]
    ground = Representation(base_nodes + (node,), base_edges + edges) if truth else incumbent
    allowed_kinds = frozenset({NodeKind.OBSERVABLE, NodeKind.EQUATION})
    language = LanguageSpec(
        allowed_kinds=allowed_kinds,
        max_kind_counts={NodeKind.OBSERVABLE: 2 + nuisance_count, NodeKind.EQUATION: 1},
        allowed_relations=frozenset({"input_to", "predicts", "nuisance_to"}),
        allowed_equation_families=frozenset({"linear"}),
    )
    lexicalization = tuple(sorted({"input": x_id, "outcome": y_id, "mechanism": eq_id, "candidate_concept": extra_id}.items()))
    return incumbent, ground, language, lexicalization


def _case(case_id: str, inputs: Mapping[str, Any], intervention: Mapping[str, Any], program: Program) -> Case:
    y = predict(program, inputs, intervention)
    return Case(case_id, _frozen_map(inputs), _frozen_map(intervention), y)


def _programs(family: str, k: float) -> tuple[Program, tuple[Program, ...]]:
    grid = (k - 1.0, k, k + 1.0)
    if family == "latent_common_cause":
        truth = Program("latent_parent", (("k", 2 * k),))
        inc = tuple(Program("symmetric_pair", (("a", a),)) for a in grid)
    elif family == "unification":
        truth = Program("unified_law", (("k", k),))
        inc = tuple(Program("context_table", (("c0", a), ("c1", b), ("default", 0.0))) for a in grid for b in grid)
    elif family == "hidden_regimes":
        truth = Program("regime_process", (("k", k),))
        inc = tuple(Program("single_regime", (("k", a),)) for a in grid)
    elif family == "property_to_relation":
        truth = Program("relational_property", (("e", k + 1), ("k", k)))
        inc = tuple(Program("intrinsic_property", (("k", a),)) for a in grid)
    elif family == "state_invention":
        truth = Program("stateful", (("k", k),))
        inc = tuple(Program("memoryless", (("k", a),)) for a in grid)
    elif family == "coordinate_transform":
        truth = Program("transformed_coordinate", (("k", k),))
        inc = tuple(Program("identity_coordinate", (("k", a),)) for a in grid)
    elif family == "causal_ambiguity":
        truth = Program("common_response", (("k", k),))
        inc = tuple(Program("x_causes_y", (("k", a),)) for a in grid)
    elif family == "meta_law":
        truth = Program("meta_function", (("base", k), ("slope", 1.0)))
        inc = tuple(Program("meta_table", (("c0", a), ("c1", b), ("default", b))) for a in grid for b in (k, k + 1, k + 2))
    else:
        raise ValueError(f"unknown family {family}")
    return truth, inc


def generate_world(family: str, seed: int, *, no_jump: bool = False) -> World:
    if family not in FAMILIES:
        raise ValueError(f"unknown family {family}")
    rng = random.Random((seed << 8) ^ FAMILIES.index(family))
    k = rng.randint(10, 500) / 10.0
    truth_program, incumbent_programs = _programs(family, k)
    incumbent, ground, language, lexicalization = _graph(family, not no_jump, rng)

    # For no-jump controls truth is a member of H(R0), selected independently of test data.
    if no_jump:
        truth_program = min(incumbent_programs, key=lambda p: abs(p.param("k", p.param("c0")) - k))

    candidate = Candidate(ground, truth_program)
    obs_specs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    test_specs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    fals_specs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    xs = [round(rng.uniform(0.5, 5.0), 6) for _ in range(3)]
    if family == "latent_common_cause":
        obs_specs = [({"x1": v, "x2": v}, {}) for v in xs]
        test_specs = [({"x1": v, "x2": v}, {"x1": v + 2}) for v in xs[:2]]
        fals_specs = [({"x1": v, "x2": v}, {"x1": v - 1}) for v in xs]
    elif family == "unification":
        obs_specs = [({"x": v, "context": c}, {}) for c in (0, 1) for v in xs[:2]]
        test_specs = [({"x": v, "context": 0}, {"context": 2}) for v in xs[:2]]
        fals_specs = [({"x": v, "context": 0}, {"context": c}) for c in (2, 3) for v in xs[:1]]
    elif family == "hidden_regimes":
        obs_specs = [({"x": v, "regime": 0}, {}) for v in xs]
        test_specs = [({"x": v, "regime": 0}, {"regime": 1}) for v in xs[:2]]
        fals_specs = [({"x": v, "regime": 0}, {"regime": 1}) for v in xs]
    elif family == "property_to_relation":
        obs_specs = [({"x": v, "environment": 0}, {}) for v in xs]
        test_specs = [({"x": v, "environment": 0}, {"environment": e}) for v, e in zip(xs[:2], (1, 2))]
        fals_specs = [({"x": v, "environment": 0}, {"environment": -1}) for v in xs]
    elif family == "state_invention":
        obs_specs = [({"x": v, "history": ()}, {}) for v in xs]
        test_specs = [({"x": v, "history": (1.0, 2.0)}, {}) for v in xs[:2]]
        fals_specs = [({"x": v, "history": (-1.0, 3.0)}, {}) for v in xs]
    elif family == "coordinate_transform":
        obs_specs = [({"x": v}, {}) for v in (0.0, 1.0)]
        test_specs = [({"x": v}, {}) for v in (2.0, 3.0)]
        fals_specs = [({"x": v}, {}) for v in (-2.0, 4.0)]
    elif family == "causal_ambiguity":
        obs_specs = [({"x": v, "u": v}, {}) for v in xs]
        test_specs = [({"x": v, "u": v}, {"x": v + 2}) for v in xs[:2]]
        fals_specs = [({"x": v, "u": v}, {"x": v - 1}) for v in xs]
    elif family == "meta_law":
        obs_specs = [({"x": v, "context": c}, {}) for c in (0, 1) for v in xs[:2]]
        test_specs = [({"x": v, "context": 0}, {"context": 2}) for v in xs[:2]]
        fals_specs = [({"x": v, "context": 0}, {"context": c}) for c in (3, 4) for v in xs[:1]]

    # Randomized irrelevant measurements prevent split identity and test nuisance robustness.
    def add_nuisance(specs: list[tuple[dict[str, Any], dict[str, Any]]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        return [({**inputs, "nuisance": round(rng.uniform(-5.0, 5.0), 6)}, action) for inputs, action in specs]

    validation_specs = add_nuisance([(dict(obs_specs[-1][0]), dict(obs_specs[-1][1]))])
    obs_specs = add_nuisance(obs_specs)
    test_specs = add_nuisance(test_specs)
    fals_specs = add_nuisance(fals_specs)

    # Outcomes always come from the actual truth program, including no-jump controls.
    observations = tuple(_case(f"obs-{i}", a, b, truth_program) for i, (a, b) in enumerate(obs_specs))
    validation = tuple(_case(f"val-{i}", a, b, truth_program) for i, (a, b) in enumerate(validation_specs))
    interventions = tuple(_case(f"test-{i}", a, b, truth_program) for i, (a, b) in enumerate(test_specs))
    falsification = tuple(_case(f"fals-{i}", a, b, truth_program) for i, (a, b) in enumerate(fals_specs))
    world_id = f"{family}-{'nojump' if no_jump else 'jump'}-{seed:06d}"
    return World(world_id, family, seed, seed ^ 0xA5A5A5A5, no_jump, incumbent, candidate, language, incumbent_programs, observations, validation, interventions, falsification, lexicalization)
