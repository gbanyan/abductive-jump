from abductive_jump.external_reasoning_calibration import _arrow_table, _prediction_table
from abductive_jump.proposals import external_representation_proposals
from abductive_jump.realization import fit_representation
from abductive_jump.worlds import generate_world


def test_external_prediction_table_is_public_and_has_no_outcomes():
    world = generate_world("coordinate_transform", 41)
    proposal = external_representation_proposals(world.public(), 41 ^ 0x5151)[5]
    fitted = fit_representation(world.public(), proposal.representation)
    table = _prediction_table(world, fitted.expression)
    assert {row["case_id"] for row in table} == {
        query["case_id"] for query in world.public().intervention_queries
    }
    assert all("outcome" not in row for row in table)
    assert max(row["absolute_separation"] for row in table) > 0


def test_sparse_result_columns_survive_arrow_conversion():
    table = _arrow_table([{"ok": True}, {"ok": False, "error": "bad"}])
    assert table.column_names == ["error", "ok"]
    assert table.to_pylist()[1]["error"] == "bad"
