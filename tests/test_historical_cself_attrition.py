from abductive_jump.historical_attrition import strict_json_object


def test_strict_json_object_accepts_complete_plain_or_fenced_object() -> None:
    assert strict_json_object('{"plans": []}') == {"plans": []}
    assert strict_json_object('```json\n{"plans": []}\n```') == {"plans": []}


def test_strict_json_object_rejects_truncated_outer_object_with_nested_object() -> None:
    assert strict_json_object('{"plans": [[{"operator": "ADD_NODE"}') is None
