import json

from abductive_jump.conditions import Condition, ProposalSource, build_prompt
from abductive_jump.llm import extract_json_object
from abductive_jump.worlds import generate_world


def test_prompt_exposes_observations_but_not_prospective_outcomes_or_family_label():
    world = generate_world("latent_common_cause", 22)
    prompt = build_prompt(world.public(), Condition.B0_DIRECT_LLM, ProposalSource.P0_LLM)
    payload = json.loads(prompt.user.split("World: ", 1)[1])
    assert all("outcome" in case for case in payload["observations"])
    assert all("outcome" not in case for case in payload["prospective_intervention_queries_without_outcomes"])
    assert world.family not in prompt.user
    assert world.truth.candidate_hash not in prompt.user


def test_oracle_prompt_supplies_representation_but_not_equation_or_outcomes():
    world = generate_world("state_invention", 5)
    prompt = build_prompt(
        world.public(),
        Condition.B4_REPRESENTATION_MUTATION,
        ProposalSource.P2_ORACLE,
        world.truth.representation,
    )
    payload = json.loads(prompt.user.split("World: ", 1)[1])
    assert payload["supplied_candidate_representation"] == world.truth.representation.canonical_dict()
    assert world.truth.program.canonical_json not in prompt.user


def test_json_extractor_accepts_plain_and_fenced_model_output():
    assert extract_json_object('{"x":1}') == {"x": 1}
    assert extract_json_object('```json\n{"x":2}\n```') == {"x": 2}

