from __future__ import annotations

from abductive_jump.compositional_worlds import generate_heldout_world
from abductive_jump.realizer_audit import (
    ALIGNED,
    MASK_PREFIX,
    MOTIF_DISABLED,
    ROLE_BLIND,
    evaluate_counterfactual,
    fit_counterfactual,
    representation_from_json,
)


def test_representation_round_trip() -> None:
    world = generate_heldout_world(91001)
    restored = representation_from_json(world.truth.representation.canonical_json())
    assert restored.canonical_json() == world.truth.representation.canonical_json()


def test_aligned_heldout_truth_passes_and_disabled_realizer_does_not() -> None:
    world = generate_heldout_world(91002)
    representation = world.truth.representation
    aligned = evaluate_counterfactual(world, representation, ALIGNED)
    disabled = evaluate_counterfactual(world, representation, MOTIF_DISABLED)
    assert aligned["counterfactual_validated_jump"] is True
    assert disabled["escape_reasons"]
    assert disabled["realized_signature"] == "incumbent_fallback"
    assert disabled["counterfactual_validated_jump"] is False


def test_signature_mask_is_selective() -> None:
    world = generate_heldout_world(91003)
    representation = world.truth.representation
    masked = fit_counterfactual(world, representation, f"{MASK_PREFIX}relation_arity_3")
    unrelated = fit_counterfactual(world, representation, f"{MASK_PREFIX}multi_argument_function")
    assert masked.detected_signature == "relation_arity_3"
    assert masked.realized_signature == "incumbent_fallback"
    assert unrelated.realized_signature == "relation_arity_3"


def test_role_blind_fit_is_deterministic() -> None:
    world = generate_heldout_world(91004)
    representation = world.truth.representation
    first = fit_counterfactual(world, representation, ROLE_BLIND)
    second = fit_counterfactual(world, representation, ROLE_BLIND)
    assert first.expression.canonical_json == second.expression.canonical_json
    assert first.observational_loss == second.observational_loss
