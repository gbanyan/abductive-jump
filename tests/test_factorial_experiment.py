from abductive_jump.conditions import Condition, ProposalSource
from abductive_jump.factorial_experiment import SOURCE_CONDITIONS


def test_factorial_sources_share_reasoning_conditions_but_change_proposal_source():
    assert SOURCE_CONDITIONS[ProposalSource.P0_LLM] is Condition.B1_SAMPLE_MATCHED
    assert SOURCE_CONDITIONS[ProposalSource.P1_EXTERNAL] is Condition.B4_REPRESENTATION_MUTATION
    assert SOURCE_CONDITIONS[ProposalSource.P2_ORACLE] is Condition.B4_REPRESENTATION_MUTATION
