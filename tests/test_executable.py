import dataclasses

import pytest

from abductive_jump.executable import (
    ExecutableTheory,
    evaluate_executable,
    freeze_theory,
    parse_theory,
    program_expression,
)
from abductive_jump.representation import Edge, Node, NodeKind, Representation
from abductive_jump.worlds import FAMILIES, generate_world


@pytest.mark.parametrize("family", FAMILIES)
def test_reference_compiled_theory_passes_objective_executable_gates(family):
    world = generate_world(family, 71)
    theory = ExecutableTheory(
        world.truth.representation,
        program_expression(world.truth.program),
        "reference compiler test",
        (world.interventions[0].case_id,),
    )
    commitment = freeze_theory(world, theory)
    result = evaluate_executable(world, theory, commitment)
    assert result.validated_jump
    assert result.candidate_obs_loss == 0
    assert result.candidate_cf_loss == 0


def test_expression_cannot_read_outcomes_or_hidden_family_fields():
    world = generate_world("meta_law", 9)
    expression = program_expression(world.truth.program)
    invalid = dataclasses.replace(expression, tree={"op": "var", "name": "outcome"})
    assert "forbidden_variable:outcome" in invalid.validate(frozenset({"x", "context"}))


def test_theory_parser_is_typed_and_commitment_detects_selection_change():
    world = generate_world("coordinate_transform", 4)
    payload = {
        "representation": world.truth.representation.canonical_dict(),
        "expression": program_expression(world.truth.program).tree,
        "explanation": "square-coordinate law",
        "selected_intervention_ids": [world.interventions[0].case_id],
    }
    theory = parse_theory(payload)
    commitment = freeze_theory(world, theory)
    changed = dataclasses.replace(theory, selected_intervention_ids=(world.interventions[1].case_id,))
    with pytest.raises(ValueError, match="invalid prospective"):
        evaluate_executable(world, changed, commitment)


def test_theory_parser_translates_only_public_expression_variables():
    world = generate_world("state_invention", 33)
    public_history = dict(world.variable_names)["history"]
    payload = {
        "representation": world.truth.representation.canonical_dict(),
        "expression": {"op": "history_sum", "name": public_history},
        "selected_intervention_ids": [world.interventions[0].case_id],
    }
    theory = parse_theory(
        payload,
        {public: internal for internal, public in world.variable_names},
    )
    assert theory.expression.tree["name"] == "history"


def test_theory_parser_normalizes_unambiguous_leaf_shorthand():
    world = generate_world("coordinate_transform", 3)
    payload = {
        "representation": world.truth.representation.canonical_dict(),
        "expression": {
            "op": "mul",
            "left": {"const": 2},
            "right": {"name": "opaque"},
        },
        "selected_intervention_ids": [world.interventions[0].case_id],
    }
    theory = parse_theory(payload, {"opaque": "x"})
    assert theory.expression.tree == {
        "op": "mul",
        "left": {"op": "const", "value": 2},
        "right": {"op": "var", "name": "x"},
    }


def test_irrelevant_structural_escape_cannot_license_unrelated_equation_change():
    world = generate_world("coordinate_transform", 12)
    latent = Node("irrelevant_latent", NodeKind.LATENT_VARIABLE)
    representation = Representation(
        world.incumbent.nodes + (latent,),
        world.incumbent.edges + (Edge(latent.id, "unrelated", world.incumbent.nodes[0].id),),
    )
    theory = ExecutableTheory(
        representation,
        program_expression(world.truth.program),
        "an irrelevant latent cannot support a coordinate power",
        (world.interventions[0].case_id,),
    )
    result = evaluate_executable(world, theory, freeze_theory(world, theory))
    assert "missing_connected_support:Function" in result.invalid_reasons
    assert not result.validated_jump
