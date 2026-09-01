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

    def public_dict(self, names: Mapping[str, str] | None = None) -> dict[str, Any]:
        names = names or {}
        return {
            "case_id": self.case_id,
            "inputs": {
                names.get(key, key): value
                for key, value in self.inputs
                if not key.startswith("_")
            },
            "intervention": {names.get(key, key): value for key, value in self.intervention},
            "outcome": self.outcome,
        }

    def query_dict(self, names: Mapping[str, str] | None = None) -> dict[str, Any]:
        names = names or {}
        return {
            "case_id": self.case_id,
            "inputs": {
                names.get(key, key): value
                for key, value in self.inputs
                if not key.startswith("_")
            },
            "intervention": {names.get(key, key): value for key, value in self.intervention},
        }


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
    observations: tuple[dict[str, Any], ...]
    incumbent: Representation
    incumbent_language: LanguageSpec
    intervention_queries: tuple[dict[str, Any], ...]
    known_nuisance_fields: tuple[str, ...]


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
    variable_names: tuple[tuple[str, str], ...]

    @property
    def ground_truth_hash(self) -> str:
        return self.truth.candidate_hash

    def public(self) -> PublicWorld:
        names = dict(self.variable_names)
        observations = tuple(case.public_dict(names) for case in self.observations)
        queries = tuple(case.query_dict(names) for case in self.interventions)
        nuisances = tuple(public for internal, public in self.variable_names if internal == "nuisance")
        return PublicWorld(
            self.world_id,
            observations,
            self.incumbent,
            self.incumbent_language,
            queries,
            nuisances,
        )

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
    if program.name == "intrinsic_polynomial":
        return p("a") * x + p("b") * x**2
    if program.name == "relational_property":
        env = float(intervention.get("environment", inputs.get("environment", 0.0)))
        return p("k") * x + p("e") * env
    if program.name == "memoryless":
        return p("k") * float(intervention.get("x", x))
    if program.name == "memoryless_quadratic":
        current = float(intervention.get("x", x))
        return p("a") * current + p("b") * current**2
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
        return p("k") * float(inputs.get("_u", x))
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
    labels = iter(rng.sample(syllables, len(syllables)))

    def new(role: str, kind: NodeKind, **attributes: Any) -> Node:
        return Node(next(labels), kind, {"role": role, **attributes})

    x = new("input", NodeKind.OBSERVABLE)
    y = new("outcome", NodeKind.OBSERVABLE)
    eq = new("incumbent_rule", NodeKind.EQUATION, family="linear")
    base_nodes: tuple[Node, ...] = (x, y, eq)
    base_edges: tuple[Edge, ...] = (Edge(x.id, "input_to", eq.id), Edge(eq.id, "predicts", y.id))
    ground_nodes = base_nodes
    ground_edges = base_edges
    concept: Node

    if family == "latent_common_cause":
        x2 = new("second_input", NodeKind.OBSERVABLE)
        base_nodes += (x2,)
        base_edges += (Edge(x2.id, "input_to", eq.id),)
        concept = new("shared_source", NodeKind.LATENT_VARIABLE)
        ground_nodes = base_nodes + (concept,)
        ground_edges = base_edges + (
            Edge(concept.id, "causes", x.id),
            Edge(concept.id, "causes", x2.id),
            Edge(concept.id, "causes", y.id),
        )
    elif family in {"unification", "meta_law"}:
        context0 = new("context_zero", NodeKind.CONTEXT)
        context1 = new("context_one", NodeKind.CONTEXT)
        eq2 = new("incumbent_rule_two", NodeKind.EQUATION, family="linear")
        base_nodes += (context0, context1, eq2)
        base_edges += (
            Edge(context0.id, "selects", eq.id),
            Edge(context1.id, "selects", eq2.id),
            Edge(x.id, "input_to", eq2.id),
            Edge(eq2.id, "predicts", y.id),
        )
        concept = new(
            "common_invariant" if family == "unification" else "context_function",
            NodeKind.INVARIANT if family == "unification" else NodeKind.FUNCTION,
            **({"form": "affine_context"} if family == "meta_law" else {}),
        )
        ground_nodes = base_nodes + (concept,)
        ground_edges = base_edges + (Edge(concept.id, "governs", eq.id), Edge(concept.id, "governs", eq2.id))
    elif family == "hidden_regimes":
        concept = new("regime", NodeKind.REGIME)
        alternate = new(
            "alternate_rule",
            NodeKind.EQUATION,
            family="linear",
            relation_to_incumbent="sign_flip",
        )
        ground_nodes = base_nodes + (concept, alternate)
        ground_edges = base_edges + (
            Edge(concept.id, "selects", eq.id),
            Edge(concept.id, "selects", alternate.id),
            Edge(alternate.id, "predicts", y.id),
        )
    elif family == "property_to_relation":
        eq = Node(eq.id, eq.kind, {**eq.attributes, "family": "polynomial2"})
        base_nodes = tuple(eq if node.id == eq.id else node for node in base_nodes)
        entity = new("entity", NodeKind.ENTITY)
        prop = new("intrinsic_property", NodeKind.PROPERTY)
        base_nodes += (entity, prop)
        base_edges += (Edge(entity.id, "has_property", prop.id), Edge(prop.id, "input_to", eq.id))
        environment = new("environment", NodeKind.ENTITY)
        concept = new("relational_property", NodeKind.RELATION, form="additive_linear")
        ground_nodes = tuple(n for n in base_nodes if n.id != prop.id) + (environment, concept)
        ground_edges = tuple(e for e in base_edges if e.source != prop.id and e.target != prop.id) + (
            Edge(entity.id, "participant", concept.id),
            Edge(environment.id, "participant", concept.id),
            Edge(concept.id, "input_to", eq.id),
        )
    elif family == "state_invention":
        eq = Node(eq.id, eq.kind, {**eq.attributes, "family": "polynomial2"})
        base_nodes = tuple(eq if node.id == eq.id else node for node in base_nodes)
        ground_nodes = base_nodes
        concept = new("state", NodeKind.STATE_VARIABLE)
        transition = new("state_update", NodeKind.TRANSITION)
        ground_nodes = base_nodes + (concept, transition)
        ground_edges = base_edges + (
            Edge(concept.id, "input_to", transition.id),
            Edge(x.id, "input_to", transition.id),
            Edge(transition.id, "updates", concept.id),
            Edge(concept.id, "predicts", y.id),
        )
    elif family == "coordinate_transform":
        concept = new("coordinate_map", NodeKind.FUNCTION, transform="square")
        ground_nodes = base_nodes + (concept,)
        ground_edges = base_edges + (Edge(x.id, "transforms", concept.id), Edge(concept.id, "input_to", eq.id))
    elif family == "causal_ambiguity":
        incumbent_cause = new("direct_cause", NodeKind.CAUSAL_EDGE)
        base_nodes += (incumbent_cause,)
        base_edges += (Edge(x.id, "source_of", incumbent_cause.id), Edge(incumbent_cause.id, "target_of", y.id))
        concept = new("shared_source", NodeKind.LATENT_VARIABLE)
        cause_x = new("cause_x", NodeKind.CAUSAL_EDGE)
        cause_y = new("cause_y", NodeKind.CAUSAL_EDGE)
        ground_nodes = tuple(n for n in base_nodes if n.id != incumbent_cause.id) + (concept, cause_x, cause_y)
        ground_edges = tuple(e for e in base_edges if e.source != incumbent_cause.id and e.target != incumbent_cause.id) + (
            Edge(concept.id, "source_of", cause_x.id),
            Edge(cause_x.id, "target_of", x.id),
            Edge(concept.id, "source_of", cause_y.id),
            Edge(cause_y.id, "target_of", y.id),
        )
    else:  # pragma: no cover - guarded by FAMILIES
        raise ValueError(family)

    nuisance_count = rng.randrange(3)
    nuisance_nodes = tuple(
        Node(f"n{rng.randrange(1_000_000):06d}_{i}", NodeKind.OBSERVABLE, {"role": "nuisance"})
        for i in range(nuisance_count)
    )
    nuisance_edges = tuple(Edge(n.id, "nuisance_to", eq.id) for n in nuisance_nodes)
    base_nodes += nuisance_nodes
    base_edges += nuisance_edges
    ground_nodes += nuisance_nodes
    ground_edges += nuisance_edges
    incumbent = Representation(base_nodes, base_edges)
    ground = Representation(ground_nodes, ground_edges) if truth else incumbent
    allowed_kinds = frozenset(node.kind for node in incumbent.nodes)
    counts = {kind: sum(node.kind is kind for node in incumbent.nodes) for kind in allowed_kinds}
    language = LanguageSpec(
        allowed_kinds=allowed_kinds,
        max_kind_counts=counts,
        allowed_relations=frozenset(edge.relation for edge in incumbent.edges),
        allowed_equation_families=frozenset(
            str(node.attributes.get("family"))
            for node in incumbent.nodes
            if node.kind is NodeKind.EQUATION
        ),
    )
    role_names: dict[str, str] = {}
    for node in ground_nodes:
        if "role" in node.attributes:
            role_names.setdefault(str(node.attributes["role"]), node.id)
    lexicalization = tuple(sorted(role_names.items()))
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
        inc = tuple(
            Program("intrinsic_polynomial", (("a", a), ("b", b)))
            for a in grid
            for b in (k, k + 1, k + 2)
        )
    elif family == "state_invention":
        truth = Program("stateful", (("k", k),))
        inc = tuple(
            Program("memoryless_quadratic", (("a", a), ("b", b)))
            for a in grid
            for b in grid
        )
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
    k = float(rng.randint(1, 9))
    truth_program, incumbent_programs = _programs(family, k)
    incumbent, ground, language, lexicalization = _graph(family, not no_jump, rng)

    # For no-jump controls truth is a member of H(R0), selected independently of test data.
    if no_jump:
        truth_program = min(incumbent_programs, key=lambda p: abs(p.param("k", p.param("c0")) - k))

    candidate = Candidate(ground, truth_program)
    obs_specs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    test_specs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    fals_specs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    xs = [float(value) for value in rng.sample(range(1, 10), 3)]
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
        obs_specs = [({"x": v, "environment": v**2}, {}) for v in xs]
        test_specs = [({"x": v, "environment": 0}, {"environment": e}) for v, e in zip(xs[:2], (1, 2))]
        fals_specs = [({"x": v, "environment": 0}, {"environment": -1}) for v in xs]
    elif family == "state_invention":
        obs_specs = [({"x": v, "history": (v**2,)}, {}) for v in xs]
        test_specs = [({"x": v, "history": (1.0, 2.0)}, {}) for v in xs[:2]]
        fals_specs = [({"x": v, "history": (-1.0, 3.0)}, {}) for v in xs]
    elif family == "coordinate_transform":
        obs_specs = [({"x": v}, {}) for v in (0.0, 1.0)]
        test_specs = [({"x": v}, {}) for v in (2.0, 3.0)]
        fals_specs = [({"x": v}, {}) for v in (-2.0, 4.0)]
    elif family == "causal_ambiguity":
        obs_specs = [({"x": v, "_u": v}, {}) for v in xs]
        test_specs = [({"x": v, "_u": v}, {"x": v + 2}) for v in xs[:2]]
        fals_specs = [({"x": v, "_u": v}, {"x": v - 1}) for v in xs]
    elif family == "meta_law":
        obs_specs = [({"x": v, "context": c}, {}) for c in (0, 1) for v in xs[:2]]
        test_specs = [({"x": v, "context": 0}, {"context": 2}) for v in xs[:2]]
        fals_specs = [({"x": v, "context": 0}, {"context": c}) for c in (3, 4) for v in xs[:1]]

    # Randomized irrelevant measurements prevent split identity and test nuisance robustness.
    def add_nuisance(specs: list[tuple[dict[str, Any], dict[str, Any]]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        return [({**inputs, "nuisance": round(rng.uniform(-5.0, 5.0), 6)}, action) for inputs, action in specs]

    validation_specs = add_nuisance([(dict(obs_specs[-1][0]), dict(obs_specs[-1][1]))])
    test_specs.append((dict(obs_specs[0][0]), dict(obs_specs[0][1])))
    obs_specs = add_nuisance(obs_specs)
    test_specs = add_nuisance(test_specs)
    fals_specs = add_nuisance(fals_specs)

    # Outcomes always come from the actual truth program, including no-jump controls.
    observations = tuple(_case(f"obs-{i}", a, b, truth_program) for i, (a, b) in enumerate(obs_specs))
    validation = tuple(_case(f"val-{i}", a, b, truth_program) for i, (a, b) in enumerate(validation_specs))
    interventions = tuple(_case(f"test-{i}", a, b, truth_program) for i, (a, b) in enumerate(test_specs))
    falsification = tuple(_case(f"fals-{i}", a, b, truth_program) for i, (a, b) in enumerate(fals_specs))
    identity = f"{family}:{seed}:{int(no_jump)}"
    world_id = "w-" + hashlib.sha256(identity.encode()).hexdigest()[:20]
    internal_names = sorted(
        {
            key
            for case in (*observations, *validation, *interventions, *falsification)
            for key, _ in (*case.inputs, *case.intervention)
            if not key.startswith("_")
        }
    )
    role_names = dict(lexicalization)
    role_for_internal = {
        "x": "input",
        "x1": "input",
        "x2": "second_input",
        "nuisance": "nuisance",
        "history": "state",
        "regime": "regime",
        "environment": "environment",
        "context": "context_zero",
    }
    variable_names = tuple(
        (
            name,
            role_names.get(role_for_internal.get(name, ""), f"q{rng.randrange(1_000_000):06d}"),
        )
        for name in internal_names
    )
    return World(
        world_id,
        family,
        seed,
        seed ^ 0xA5A5A5A5,
        no_jump,
        incumbent,
        candidate,
        language,
        incumbent_programs,
        observations,
        validation,
        interventions,
        falsification,
        lexicalization,
        variable_names,
    )
