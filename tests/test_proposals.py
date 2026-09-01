from abductive_jump.proposals import external_representation_proposals
from abductive_jump.worlds import generate_world


def test_external_portfolio_is_family_blind_and_matched_for_jump_control_pair():
    jump = generate_world("state_invention", 44)
    control = generate_world("state_invention", 44, no_jump=True)
    jump_proposals = external_representation_proposals(jump.public(), 123)
    control_proposals = external_representation_proposals(control.public(), 123)
    assert len(jump_proposals) == 8
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

