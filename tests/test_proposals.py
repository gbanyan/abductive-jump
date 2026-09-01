from abductive_jump.executable import evaluate_executable, freeze_theory, parse_theory
from abductive_jump.oracle import incumbent_oracle
from abductive_jump.proposals import external_representation_proposals
from abductive_jump.realization import fit_representation
from abductive_jump.worlds import FAMILIES, generate_world, predict


def test_external_portfolio_is_family_blind_and_matched_for_jump_control_pair():
    jump = generate_world("state_invention", 44)
    control = generate_world("state_invention", 44, no_jump=True)
    jump_proposals = external_representation_proposals(jump.public(), 123)
    control_proposals = external_representation_proposals(control.public(), 123)
    assert len(jump_proposals) == 9
    assert [p.representation.structural_hash for p in jump_proposals] == [
        p.representation.structural_hash for p in control_proposals
    ]
    assert all(len(p.ancestry) >= 2 for p in jump_proposals)
    assert all(not jump.incumbent_language.contains(p.representation) for p in jump_proposals)


def test_external_portfolio_does_not_receive_or_copy_ground_truth():
    world = generate_world("coordinate_transform", 88)
    proposals = external_representation_proposals(world.public(), 5)
    assert all(p.representation.structural_hash != world.truth.representation.structural_hash for p in proposals)
    assert all(record.parent_hash and record.child_hash for p in proposals for record in p.ancestry)


def test_family_blind_portfolio_contains_a_validated_candidate_for_every_family():
    for family in FAMILIES:
        world = generate_world(family, 1101)
        public = world.public()
        oracle = incumbent_oracle(world)
        successes = 0
        for proposal in external_representation_proposals(public, 99):
            try:
                fitted = fit_representation(public, proposal.representation)
                separations = [
                    abs(
                        fitted.expression.evaluate(query["inputs"], query["intervention"])
                        - predict(oracle.program, dict(case.inputs), dict(case.intervention))
                    )
                    for case, query in zip(world.interventions, public.intervention_queries)
                ]
                best = max(range(len(separations)), key=separations.__getitem__)
                theory = parse_theory(
                    {
                        "representation": proposal.representation.canonical_dict(),
                        "expression": fitted.expression.tree,
                        "selected_intervention_ids": [world.interventions[best].case_id],
                    },
                    {public_name: internal for internal, public_name in world.variable_names},
                )
                successes += evaluate_executable(
                    world, theory, freeze_theory(world, theory)
                ).validated_jump
            except (KeyError, TypeError, ValueError, OverflowError):
                continue
        assert successes >= 1, family
