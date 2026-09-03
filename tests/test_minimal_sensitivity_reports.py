from abductive_jump.minimal_sensitivity_reports import normalized_attrition, percent


def test_normalized_attrition_maps_historical_and_new_stage_names() -> None:
    rows = [
        {"condition": "old", "stage": "parse_valid", "rate": "1.0"},
        {"condition": "new", "stage": "json_parse_valid", "rate": "0.5"},
        {"condition": "old", "stage": "argument_type_valid", "rate": "0.25"},
        {"condition": "new", "stage": "argument_types_valid", "rate": "0.75"},
    ]
    result = normalized_attrition(rows)
    assert result["old"]["parse"] == 1.0
    assert result["new"]["parse"] == 0.5
    assert result["old"]["arguments/types"] == 0.25
    assert result["new"]["arguments/types"] == 0.75


def test_percent_formats_fraction_as_percentage() -> None:
    assert percent("0.125") == "12.5%"
