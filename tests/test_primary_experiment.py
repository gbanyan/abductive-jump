from abductive_jump.primary_experiment import _attribute_variant, _thresholds, _world_seeds
from abductive_jump.proposals import select_external_proposals
from abductive_jump.worlds import generate_world


def test_attribute_variant_stays_inside_incumbent_language():
    world = generate_world("latent_common_cause", 1)
    variant = _attribute_variant(world.incumbent, 2)
    assert variant.structural_hash != world.incumbent.structural_hash
    assert world.incumbent_language.contains(variant)


def test_external_subset_is_seeded_family_blind_and_without_replacement():
    public = generate_world("state_invention", 1).public()
    first = select_external_proposals(public, 100, 3)
    again = select_external_proposals(public, 100, 3)
    different = select_external_proposals(public, 101, 3)
    assert [p.operators for p in first] == [p.operators for p in again]
    assert len({p.representation.structural_hash for p in first}) == 3
    assert [p.operators for p in first] != [p.operators for p in different]


def test_plain_external_search_can_repeat_but_archive_selection_cannot():
    public = generate_world("state_invention", 1).public()
    diverse = select_external_proposals(public, 100, 9, diverse=True)
    plain = select_external_proposals(public, 100, 9, diverse=False)
    assert len({p.representation.structural_hash for p in diverse}) == 9
    assert len({p.representation.structural_hash for p in plain}) < 9


def test_gate_thresholds_are_explicit_and_complete():
    thresholds = _thresholds(
        {
            "gate_thresholds": {
                "epsilon_obs": 1e-12,
                "epsilon_candidate_obs": 1e-12,
                "min_prediction_separation": 0.5,
                "delta_cf": 0.1,
                "epsilon_falsification": 1e-12,
                "delta_falsification": 0.1,
            }
        }
    )
    assert thresholds.min_prediction_separation == 0.5


def test_seed_range_is_half_open_and_nonempty():
    assert _world_seeds({"world_seed_range": {"start": 10, "stop_exclusive": 13}}) == (
        10,
        11,
        12,
    )
