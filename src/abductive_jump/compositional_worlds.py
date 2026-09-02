from __future__ import annotations

import hashlib
import random
from collections.abc import Mapping
from typing import Any

from .representation import Edge, LanguageSpec, Node, NodeKind, Representation
from .worlds import Candidate, Case, Program, World, predict

HELD_OUT_FAMILY = "triadic_relation_reification"


def _frozen(values: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(values.items()))


def _case(
    case_id: str,
    inputs: Mapping[str, Any],
    intervention: Mapping[str, Any],
    program: Program,
) -> Case:
    return Case(case_id, _frozen(inputs), _frozen(intervention), predict(program, inputs, intervention))


def generate_heldout_world(seed: int, *, no_jump: bool = False) -> World:
    """Generate the sealed-family interface without exposing confirmatory outcomes.

    The structural family is a genuinely triadic relation reified from otherwise direct
    input-to-equation edges. AJ5 contained binary property-to-relation worlds, but never a
    higher-arity relation or this product mechanism. No primitive names the family or adds a
    complete triadic relation in one step.
    """

    rng = random.Random((seed << 9) ^ 0xC0A5)
    labels = iter(rng.sample(("dax", "wug", "kiv", "mep", "lor", "taz", "bim", "suv"), 8))

    def node(role: str, kind: NodeKind, **attributes: Any) -> Node:
        return Node(next(labels), kind, {"role": role, **attributes})

    x = node("input", NodeKind.OBSERVABLE)
    z = node("second_input", NodeKind.OBSERVABLE)
    w = node("third_input", NodeKind.OBSERVABLE)
    y = node("outcome", NodeKind.OBSERVABLE)
    equation = node("incumbent_rule", NodeKind.EQUATION, family="cubic")
    incumbent = Representation(
        (x, z, w, y, equation),
        (
            Edge(x.id, "input_to", equation.id),
            Edge(z.id, "input_to", equation.id),
            Edge(w.id, "input_to", equation.id),
            Edge(equation.id, "predicts", y.id),
        ),
    )
    relation = node("triadic_mechanism", NodeKind.RELATION, arity=3)
    ground = Representation(
        incumbent.nodes + (relation,),
        (
            Edge(x.id, "argument_0", relation.id),
            Edge(z.id, "argument_1", relation.id),
            Edge(w.id, "argument_2", relation.id),
            Edge(relation.id, "result_of", equation.id),
            Edge(equation.id, "predicts", y.id),
        ),
    )
    allowed_kinds = frozenset(node.kind for node in incumbent.nodes)
    language = LanguageSpec(
        allowed_kinds,
        {kind: sum(node.kind is kind for node in incumbent.nodes) for kind in allowed_kinds},
        frozenset(edge.relation for edge in incumbent.edges),
        allowed_equation_families=frozenset({"cubic"}),
    )

    k = float(rng.randint(1, 9))
    truth_program = Program("cubic_x", (("k", k),)) if no_jump else Program("triadic_relation", (("k", k),))
    truth_representation = incumbent if no_jump else ground
    incumbents = tuple(Program("cubic_x", (("k", value),)) for value in (k - 1, k, k + 1))
    values = [float(value) for value in rng.sample(range(1, 8), 3)]
    observation_specs = [({"x": value, "z": value, "w": value}, {}) for value in values]
    validation_specs = [({"x": values[-1], "z": values[-1], "w": values[-1]}, {})]
    intervention_specs = [
        ({"x": values[0], "z": values[0], "w": values[0]}, {"z": values[0] + 1}),
        ({"x": values[1], "z": values[1], "w": values[1]}, {"w": values[1] + 2}),
        ({"x": values[2], "z": values[2], "w": values[2]}, {}),
    ]
    falsification_specs = [
        ({"x": values[0], "z": values[0], "w": values[0]}, {"z": values[0] - 1}),
        ({"x": values[1], "z": values[1], "w": values[1]}, {"w": values[1] - 1}),
    ]
    observations = tuple(_case(f"obs-{index}", inputs, action, truth_program) for index, (inputs, action) in enumerate(observation_specs))
    validation = tuple(_case(f"val-{index}", inputs, action, truth_program) for index, (inputs, action) in enumerate(validation_specs))
    interventions = tuple(_case(f"test-{index}", inputs, action, truth_program) for index, (inputs, action) in enumerate(intervention_specs))
    falsification = tuple(_case(f"fals-{index}", inputs, action, truth_program) for index, (inputs, action) in enumerate(falsification_specs))
    identity = f"{HELD_OUT_FAMILY}:{seed}:{int(no_jump)}"
    world_id = "h-" + hashlib.sha256(identity.encode()).hexdigest()[:20]
    variable_names = (("x", x.id), ("z", z.id), ("w", w.id))
    return World(
        world_id,
        HELD_OUT_FAMILY,
        seed,
        seed ^ 0xA5A5A5A5,
        no_jump,
        incumbent,
        Candidate(truth_representation, truth_program),
        language,
        incumbents,
        observations,
        validation,
        interventions,
        falsification,
        (
            ("input", x.id),
            ("second_input", z.id),
            ("third_input", w.id),
            ("outcome", y.id),
            ("incumbent_rule", equation.id),
            ("triadic_mechanism", relation.id),
        ),
        variable_names,
    )
