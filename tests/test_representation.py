import pytest

from abductive_jump.representation import Edge, LanguageSpec, Node, NodeKind, Representation


def test_canonical_hash_ignores_input_order_and_normalizes_negative_zero():
    a = Representation(
        (Node("b", NodeKind.OBSERVABLE, {"v": -0.0}), Node("a", NodeKind.OBSERVABLE)),
        (Edge("a", "rel", "b"),),
    )
    b = Representation(tuple(reversed(a.nodes)), a.edges)
    assert a.structural_hash == b.structural_hash
    assert '"v":0.0' in a.canonical_json()


def test_validator_rejects_dangling_and_duplicate_nodes():
    rep = Representation((Node("x", NodeKind.OBSERVABLE), Node("x", NodeKind.ENTITY)), (Edge("x", "r", "missing"),))
    assert "duplicate node id" in rep.validate()
    assert any("dangling" in error for error in rep.validate())
    with pytest.raises(ValueError):
        rep.canonical_json()


def test_language_membership_detects_structural_not_parameter_escape():
    r0 = Representation((Node("x", NodeKind.OBSERVABLE), Node("eq", NodeKind.EQUATION, {"family": "linear", "coefficient": 1})))
    changed_value = r0.replace_node("eq", attributes={"family": "linear", "coefficient": 99})
    latent = Representation(r0.nodes + (Node("z", NodeKind.LATENT_VARIABLE),))
    language = LanguageSpec(
        frozenset({NodeKind.OBSERVABLE, NodeKind.EQUATION}),
        {NodeKind.OBSERVABLE: 1, NodeKind.EQUATION: 1},
        frozenset(),
        allowed_equation_families=frozenset({"linear"}),
    )
    assert language.contains(changed_value)
    assert not language.contains(latent)
    assert "kind:LatentVariable" in language.membership_failures(latent)

